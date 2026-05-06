from dataclasses import dataclass, field
from typing import Any


@dataclass
class SelectionParams:
    m: int
    n: int
    k: int
    j: int
    s: int

    def to_dict(self) -> dict[str, int]:
        return {
            "m": self.m,
            "n": self.n,
            "k": self.k,
            "j": self.j,
            "s": self.s,
        }

    def validate_relations(self) -> None:
        if self.n > self.m:
            raise ValueError("n must be less than or equal to m.")
        if self.k > self.n:
            raise ValueError("k must be less than or equal to n.")
        if self.j > self.k:
            raise ValueError("j must be less than or equal to k.")
        if self.s > self.j:
            raise ValueError("s must be less than or equal to j.")


@dataclass
class SampleSelection:
    mode: str
    samples: list[int]

    def as_text(self) -> str:
        return ", ".join(str(sample) for sample in self.samples)


@dataclass(frozen=True)
class CoverageRule:
    mode: str = "at_least_one"
    threshold: int = 1

    def to_dict(self) -> dict[str, int | str]:
        return {
            "mode": self.mode,
            "threshold": self.threshold,
        }

    def to_display_text(self) -> str:
        if self.mode == "all":
            return "For each j-group, all s-subsets must be covered."
        if self.mode == "at_least_n":
            return f"For each j-group, at least {self.threshold} s-subsets must be covered."
        return "For each j-group, at least one s-subset must be covered."


@dataclass(frozen=True)
class CoverageTarget:
    j_group: tuple[int, ...]
    s_subset: tuple[int, ...]

    def key(self) -> tuple[tuple[int, ...], tuple[int, ...]]:
        return (self.j_group, self.s_subset)


@dataclass
class CoverageReport:
    total_targets: int
    covered_targets: int
    coverage_ratio: float
    is_satisfied: bool
    summary_text: str
    uncovered_targets: list[CoverageTarget] = field(default_factory=list)

    def uncovered_count(self) -> int:
        return len(self.uncovered_targets)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_targets": self.total_targets,
            "covered_targets": self.covered_targets,
            "coverage_ratio": self.coverage_ratio,
            "is_satisfied": self.is_satisfied,
            "summary_text": self.summary_text,
            "uncovered_targets": [target.key() for target in self.uncovered_targets],
        }

    def to_display_text(self) -> str:
        return self.summary_text


@dataclass
class SelectionResult:
    params: SelectionParams
    selected_samples: list[int]
    candidate_groups: list[tuple[int, ...]]
    optimized_groups: list[tuple[int, ...]]
    coverage_report: CoverageReport
    sample_mode: str
    target_count: int = 0
    rule: CoverageRule | None = None
    runtime_seconds: float = 0.0

    def result_count(self) -> int:
        return len(self.optimized_groups)

    def candidate_count(self) -> int:
        return len(self.candidate_groups)

    def to_dict(self) -> dict[str, Any]:
        return {
            "params": self.params.to_dict(),
            "selected_samples": self.selected_samples,
            "candidate_groups": self.candidate_groups,
            "optimized_groups": self.optimized_groups,
            "coverage_report": self.coverage_report.to_dict(),
            "sample_mode": self.sample_mode,
            "target_count": self.target_count,
            "rule": self.rule.to_dict() if self.rule else None,
            "runtime_seconds": self.runtime_seconds,
        }


@dataclass
class RunRecord:
    id: int | None
    run_label: str
    params: SelectionParams
    sample_mode: str
    selected_samples: list[int]
    result_count: int
    coverage_summary: str
    created_at: str
    rule_mode: str = "at_least_one"
    rule_threshold: int = 1
    runtime_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "run_label": self.run_label,
            "params": self.params.to_dict(),
            "sample_mode": self.sample_mode,
            "selected_samples": self.selected_samples,
            "result_count": self.result_count,
            "coverage_summary": self.coverage_summary,
            "created_at": self.created_at,
            "rule_mode": self.rule_mode,
            "rule_threshold": self.rule_threshold,
            "runtime_seconds": self.runtime_seconds,
        }
