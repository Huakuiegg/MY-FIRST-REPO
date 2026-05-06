from math import comb
import time

from src.core.coverage import (
    build_compact_j_group_cover_map,
    build_compact_j_group_targets,
    build_coverage_targets,
    build_group_cover_map,
    calculate_coverage_report,
)
from src.core.generator import generate_k_groups
from src.core.models import CoverageRule, CoverageTarget, SelectionParams, SelectionResult
from src.core.optimizer import optimize_groups
from src.core.validators import validate_params, validate_sample_values
from src.services.sample_service import SampleService


class SelectionService:
    def __init__(
        self,
        sample_service: SampleService | None = None,
        default_rule: CoverageRule | None = None,
    ) -> None:
        self.sample_service = sample_service or SampleService()
        self.default_rule = default_rule or CoverageRule(mode="at_least_one", threshold=1)

    def prepare_candidates(self, samples: list[int], k: int) -> list[tuple[int, ...]]:
        return generate_k_groups(samples, k)

    def should_use_compact_targets(self, rule: CoverageRule, params: SelectionParams) -> bool:
        if params.j == params.s:
            return True
        return rule.mode == "at_least_one" or (rule.mode == "at_least_n" and rule.threshold <= 1)

    def prepare_targets(
        self,
        samples: list[int],
        j: int,
        s: int,
        rule: CoverageRule,
        params: SelectionParams,
    ) -> list[CoverageTarget]:
        if self.should_use_compact_targets(rule, params):
            return build_compact_j_group_targets(samples, j)
        return build_coverage_targets(samples, j, s)

    def build_cover_map(
        self,
        candidate_groups: list[tuple[int, ...]],
        targets: list[CoverageTarget],
        params: SelectionParams,
        rule: CoverageRule,
    ) -> dict[tuple[int, ...], set[int]]:
        if self.should_use_compact_targets(rule, params):
            return build_compact_j_group_cover_map(candidate_groups, targets, params.s)
        return build_group_cover_map(candidate_groups, targets)

    def build_rule_from_params(self, params: SelectionParams) -> CoverageRule:
        if params.j == params.s:
            return CoverageRule(mode="all", threshold=1)
        return CoverageRule(mode="at_least_one", threshold=1)

    def normalize_rule_for_execution(self, params: SelectionParams, rule: CoverageRule) -> CoverageRule:
        if params.j == params.s and rule.mode == "all":
            return CoverageRule(mode="at_least_one", threshold=1)
        return rule

    def get_rule_by_name(self, rule_name: str, threshold: int = 1) -> CoverageRule:
        normalized = (rule_name or "").strip().lower()
        if normalized in {"auto", ""}:
            raise ValueError("Auto rule should be resolved from parameters.")
        if normalized == "all":
            return CoverageRule(mode="all", threshold=1)
        if normalized == "at_least_n":
            normalized_threshold = max(1, threshold)
            if normalized_threshold == 1:
                return CoverageRule(mode="at_least_one", threshold=1)
            return CoverageRule(mode="at_least_n", threshold=normalized_threshold)
        return CoverageRule(mode="at_least_one", threshold=1)

    def estimate_problem_size(self, params: SelectionParams) -> dict[str, int]:
        validated_params = validate_params(params)
        return {
            "candidate_group_count": comb(validated_params.n, validated_params.k),
            "j_group_count": comb(validated_params.n, validated_params.j),
            "expanded_target_count": comb(validated_params.n, validated_params.j) * comb(validated_params.j, validated_params.s),
            "compact_target_count": comb(validated_params.n, validated_params.j),
        }

    def execute_selection_pipeline(
        self,
        params: SelectionParams,
        samples: list[int],
        sample_mode: str,
        rule: CoverageRule | None = None,
    ) -> SelectionResult:
        start_time = time.perf_counter()
        validated_samples = validate_sample_values(samples, params.m, params.n)
        active_rule = self.normalize_rule_for_execution(params, rule or self.build_rule_from_params(params))
        candidate_groups = self.prepare_candidates(validated_samples, params.k)
        targets = self.prepare_targets(validated_samples, params.j, params.s, active_rule, params)
        group_cover_map = self.build_cover_map(candidate_groups, targets, params, active_rule)
        optimized_groups = optimize_groups(
            candidate_groups=candidate_groups,
            targets=targets,
            group_cover_map=group_cover_map,
            rule=active_rule,
            use_pruning=True,
            trials=self.choose_trial_count(params, active_rule),
            use_exact_first=True,
        )
        coverage_report = calculate_coverage_report(optimized_groups, targets, group_cover_map, active_rule)
        return SelectionResult(
            params=params,
            selected_samples=validated_samples,
            candidate_groups=candidate_groups,
            optimized_groups=optimized_groups,
            coverage_report=coverage_report,
            sample_mode=sample_mode,
            target_count=len(targets),
            rule=active_rule,
            runtime_seconds=time.perf_counter() - start_time,
        )

    def choose_trial_count(self, params: SelectionParams, rule: CoverageRule) -> int:
        """Adaptive trial count. Increased for better accuracy with exact solver,
        preprocessing, and enhanced scoring. Small instances get more exploration.
        """
        candidate_count = comb(params.n, params.k)
        if params.j == params.s or (params.n <= 8):  # exact likely to succeed
            return 5
        if rule.mode == "at_least_one" or (rule.mode == "at_least_n" and rule.threshold <= 1):
            if params.n <= 10:
                return 15
            if params.n <= 12:
                return 6
            return 3
        if rule.mode == "at_least_n":
            if params.n <= 10:
                return 25
            return 6
        if candidate_count <= 100:
            return 25
        return 5

    def run_selection(
        self,
        params: SelectionParams,
        sample_mode: str,
        manual_text: str = "",
        rule_name: str | None = None,
        rule_threshold: int = 1,
    ) -> SelectionResult:
        validated_params = validate_params(params)
        sample_selection = self.sample_service.get_samples(validated_params, sample_mode, manual_text)
        if rule_name and rule_name.lower() != "auto":
            explicit_rule = self.get_rule_by_name(rule_name, rule_threshold)
        else:
            explicit_rule = self.build_rule_from_params(validated_params)
        return self.execute_selection_pipeline(validated_params, sample_selection.samples, sample_selection.mode, explicit_rule)

    def recalculate_from_samples(
        self,
        params: SelectionParams,
        samples: list[int],
        sample_mode: str,
        rule: CoverageRule | None = None,
    ) -> SelectionResult:
        validated_params = validate_params(params)
        validated_samples = validate_sample_values(samples, validated_params.m, validated_params.n)
        return self.execute_selection_pipeline(validated_params, validated_samples, sample_mode, rule)

    def summarize_result(self, result: SelectionResult) -> str:
        rule_text = result.rule.to_display_text() if result.rule else "No rule"
        return (
            f"Samples: {len(result.selected_samples)} | Candidates: {result.candidate_count()} | "
            f"Targets: {result.target_count} | Selected Groups: {result.result_count()} | "
            f"Coverage: {result.coverage_report.coverage_ratio:.2%} | Rule: {rule_text}"
        )
