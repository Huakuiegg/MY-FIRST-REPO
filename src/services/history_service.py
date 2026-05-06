from src.core.formatter import build_run_label
from src.core.models import CoverageRule, RunRecord, SelectionResult
from src.services.selection_service import SelectionService
from src.storage.repositories import count_runs, delete_result_groups_by_run_id, delete_run_by_id, fetch_result_groups_by_run_id, fetch_run_by_id, fetch_runs, insert_result_groups, insert_run
from src.utils.helpers import now_text


class HistoryService:
    def __init__(self, selection_service: SelectionService) -> None:
        self.selection_service = selection_service

    def save_run(self, result: SelectionResult) -> int:
        run_index = self.get_next_run_index()
        run_label = build_run_label(result.params, run_index, result.result_count())
        rule = result.rule or CoverageRule(mode="at_least_one", threshold=1)
        record = RunRecord(
            id=None,
            run_label=run_label,
            params=result.params,
            sample_mode=result.sample_mode,
            selected_samples=result.selected_samples,
            result_count=result.result_count(),
            coverage_summary=result.coverage_report.summary_text,
            created_at=now_text(),
            rule_mode=rule.mode,
            rule_threshold=rule.threshold,
            runtime_seconds=result.runtime_seconds,
        )
        run_id = insert_run(record)
        insert_result_groups(run_id, result.optimized_groups)
        return run_id

    def list_runs(self) -> list[RunRecord]:
        return fetch_runs()

    def get_run_details(self, run_id: int) -> dict:
        run_record = fetch_run_by_id(run_id)
        if run_record is None:
            raise ValueError(f"Run with id {run_id} was not found.")
        return {"run": run_record, "groups": fetch_result_groups_by_run_id(run_id)}

    def delete_run(self, run_id: int) -> None:
        delete_result_groups_by_run_id(run_id)
        delete_run_by_id(run_id)

    def rerun_saved_record(self, run_id: int) -> SelectionResult:
        run_record = fetch_run_by_id(run_id)
        if run_record is None:
            raise ValueError(f"Run with id {run_id} was not found.")
        rule = CoverageRule(mode=run_record.rule_mode, threshold=run_record.rule_threshold)
        return self.selection_service.recalculate_from_samples(run_record.params, run_record.selected_samples, run_record.sample_mode, rule)

    def get_next_run_index(self) -> int:
        return count_runs() + 1
