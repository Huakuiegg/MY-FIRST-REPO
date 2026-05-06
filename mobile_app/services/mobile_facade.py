from __future__ import annotations

from dataclasses import asdict, dataclass

from config import APP_TITLE, get_default_params
from src.core.formatter import format_groups, format_samples
from src.core.models import CoverageRule, RunRecord, SelectionParams, SelectionResult
from src.services.history_service import HistoryService
from src.services.selection_service import SelectionService
from src.storage.database import initialize_database


@dataclass(frozen=True)
class MobileRunSummary:
    run_id: int
    title: str
    subtitle: str


class MobileAppFacade:
    def __init__(self) -> None:
        initialize_database()
        self.selection_service = SelectionService()
        self.history_service = HistoryService(self.selection_service)
        self.app_title = APP_TITLE

    def get_default_form_data(self) -> dict[str, str]:
        defaults = get_default_params()
        return {
            "m": str(defaults["m"]),
            "n": str(defaults["n"]),
            "k": str(defaults["k"]),
            "j": str(defaults["j"]),
            "s": str(defaults["s"]),
            "sample_mode": "random",
            "manual_samples": "",
            "rule_mode": "auto",
            "rule_threshold": "1",
        }

    def run_selection(self, form_data: dict[str, str]) -> SelectionResult:
        params = SelectionParams(
            m=int(form_data["m"]),
            n=int(form_data["n"]),
            k=int(form_data["k"]),
            j=int(form_data["j"]),
            s=int(form_data["s"]),
        )
        return self.selection_service.run_selection(
            params=params,
            sample_mode=form_data.get("sample_mode", "random"),
            manual_text=form_data.get("manual_samples", ""),
            rule_name=form_data.get("rule_mode", "auto"),
            rule_threshold=int(form_data.get("rule_threshold", "1") or "1"),
        )

    def save_result(self, result: SelectionResult) -> int:
        return self.history_service.save_run(result)

    def list_run_summaries(self) -> list[MobileRunSummary]:
        runs = self.history_service.list_runs()
        return [self._to_run_summary(run) for run in runs]

    def get_run_details(self, run_id: int) -> dict[str, object]:
        details = self.history_service.get_run_details(run_id)
        run = details["run"]
        groups = details["groups"]
        return {
            "run": asdict(run),
            "groups": format_groups(groups),
        }

    def rerun_saved_record(self, run_id: int) -> SelectionResult:
        return self.history_service.rerun_saved_record(run_id)

    def delete_run(self, run_id: int) -> None:
        self.history_service.delete_run(run_id)

    def selection_result_to_view_model(self, result: SelectionResult) -> dict[str, str | int | float | list[str]]:
        return {
            "title": "Optimization Result",
            "params": self._format_params(result.params),
            "samples": format_samples(result.selected_samples),
            "sample_mode": result.sample_mode,
            "rule": self._format_rule(result.rule),
            "summary": self.selection_service.summarize_result(result),
            "coverage_summary": result.coverage_report.summary_text,
            "candidate_count": result.candidate_count(),
            "target_count": result.target_count,
            "result_count": result.result_count(),
            "runtime_seconds": round(result.runtime_seconds, 4),
            "groups": format_groups(result.optimized_groups),
        }

    def history_details_to_view_model(self, details: dict[str, object]) -> dict[str, object]:
        run_dict = details["run"]
        groups = details["groups"]
        params = run_dict["params"]
        return {
            "title": run_dict["run_label"],
            "summary": run_dict["coverage_summary"],
            "created_at": run_dict["created_at"],
            "params": (
                f"m={params['m']}, n={params['n']}, k={params['k']}, "
                f"j={params['j']}, s={params['s']}"
            ),
            "sample_mode": run_dict["sample_mode"],
            "samples": format_samples(run_dict["selected_samples"]),
            "rule": self._format_rule(CoverageRule(mode=run_dict["rule_mode"], threshold=run_dict["rule_threshold"])),
            "result_count": run_dict["result_count"],
            "runtime_seconds": round(float(run_dict.get("runtime_seconds", 0.0)), 4),
            "groups": groups,
        }

    def build_form_data_from_run(self, run: RunRecord) -> dict[str, str]:
        return {
            "m": str(run.params.m),
            "n": str(run.params.n),
            "k": str(run.params.k),
            "j": str(run.params.j),
            "s": str(run.params.s),
            "sample_mode": run.sample_mode,
            "manual_samples": format_samples(run.selected_samples),
            "rule_mode": run.rule_mode,
            "rule_threshold": str(run.rule_threshold),
        }

    def _to_run_summary(self, run: RunRecord) -> MobileRunSummary:
        subtitle = (
            f"{run.created_at} | results={run.result_count} | rule={run.rule_mode}"
        )
        return MobileRunSummary(
            run_id=int(run.id or 0),
            title=run.run_label,
            subtitle=subtitle,
        )

    def _format_params(self, params: SelectionParams) -> str:
        return f"m={params.m}, n={params.n}, k={params.k}, j={params.j}, s={params.s}"

    def _format_rule(self, rule: CoverageRule | None) -> str:
        if rule is None:
            return "auto"
        if rule.mode == "at_least_n":
            return f"at_least_n ({rule.threshold})"
        return rule.mode
