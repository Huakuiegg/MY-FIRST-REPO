from src.core.formatter import deserialize_groups, deserialize_int_list, serialize_groups, serialize_int_list
from src.core.models import RunRecord, SelectionParams
from src.storage.database import execute, execute_and_return_lastrowid, executemany, fetch_all, fetch_one



def insert_run(record: RunRecord) -> int:
    sql = """
    INSERT INTO runs (
        run_label, m, n, k, j, s, sample_mode, selected_samples,
        result_count, coverage_summary, created_at, rule_mode, rule_threshold, runtime_seconds
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        record.run_label,
        record.params.m,
        record.params.n,
        record.params.k,
        record.params.j,
        record.params.s,
        record.sample_mode,
        serialize_int_list(record.selected_samples),
        record.result_count,
        record.coverage_summary,
        record.created_at,
        record.rule_mode,
        record.rule_threshold,
        record.runtime_seconds,
    )
    return execute_and_return_lastrowid(sql, params)



def insert_result_groups(run_id: int, groups: list[tuple[int, ...]]) -> None:
    sql = """
    INSERT INTO result_groups (run_id, group_index, group_values)
    VALUES (?, ?, ?)
    """
    params_list = [(run_id, index, serialize_groups([group])) for index, group in enumerate(groups, start=1)]
    if params_list:
        executemany(sql, params_list)



def fetch_runs() -> list[RunRecord]:
    sql = """
    SELECT id, run_label, m, n, k, j, s, sample_mode, selected_samples,
           result_count, coverage_summary, created_at, rule_mode, rule_threshold, runtime_seconds
    FROM runs
    ORDER BY id DESC
    """
    rows = fetch_all(sql)
    records: list[RunRecord] = []
    for row in rows:
        records.append(
            RunRecord(
                id=row["id"],
                run_label=row["run_label"],
                params=SelectionParams(m=row["m"], n=row["n"], k=row["k"], j=row["j"], s=row["s"]),
                sample_mode=row["sample_mode"],
                selected_samples=deserialize_int_list(row["selected_samples"]),
                result_count=row["result_count"],
                coverage_summary=row["coverage_summary"],
                created_at=row["created_at"],
                rule_mode=row["rule_mode"] if "rule_mode" in row.keys() else "at_least_one",
                rule_threshold=row["rule_threshold"] if "rule_threshold" in row.keys() else 1,
                runtime_seconds=float(row["runtime_seconds"]) if "runtime_seconds" in row.keys() else 0.0,
            )
        )
    return records



def fetch_run_by_id(run_id: int) -> RunRecord | None:
    sql = """
    SELECT id, run_label, m, n, k, j, s, sample_mode, selected_samples,
           result_count, coverage_summary, created_at, rule_mode, rule_threshold, runtime_seconds
    FROM runs WHERE id = ?
    """
    row = fetch_one(sql, (run_id,))
    if row is None:
        return None
    return RunRecord(
        id=row["id"],
        run_label=row["run_label"],
        params=SelectionParams(m=row["m"], n=row["n"], k=row["k"], j=row["j"], s=row["s"]),
        sample_mode=row["sample_mode"],
        selected_samples=deserialize_int_list(row["selected_samples"]),
        result_count=row["result_count"],
        coverage_summary=row["coverage_summary"],
        created_at=row["created_at"],
        rule_mode=row["rule_mode"] if "rule_mode" in row.keys() else "at_least_one",
        rule_threshold=row["rule_threshold"] if "rule_threshold" in row.keys() else 1,
        runtime_seconds=float(row["runtime_seconds"]) if "runtime_seconds" in row.keys() else 0.0,
    )



def fetch_result_groups_by_run_id(run_id: int) -> list[tuple[int, ...]]:
    sql = "SELECT group_values FROM result_groups WHERE run_id = ? ORDER BY group_index ASC"
    rows = fetch_all(sql, (run_id,))
    groups: list[tuple[int, ...]] = []
    for row in rows:
        groups.extend(deserialize_groups(row["group_values"]))
    return groups



def delete_result_groups_by_run_id(run_id: int) -> None:
    execute("DELETE FROM result_groups WHERE run_id = ?", (run_id,))



def delete_run_by_id(run_id: int) -> None:
    execute("DELETE FROM runs WHERE id = ?", (run_id,))



def count_runs() -> int:
    row = fetch_one("SELECT COUNT(*) AS total FROM runs")
    return 0 if row is None else int(row["total"])
