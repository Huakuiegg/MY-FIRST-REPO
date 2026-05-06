def get_schema_sql() -> list[str]:
    return [
        """
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_label TEXT NOT NULL,
            m INTEGER NOT NULL,
            n INTEGER NOT NULL,
            k INTEGER NOT NULL,
            j INTEGER NOT NULL,
            s INTEGER NOT NULL,
            sample_mode TEXT NOT NULL,
            selected_samples TEXT NOT NULL,
            result_count INTEGER NOT NULL,
            coverage_summary TEXT NOT NULL,
            created_at TEXT NOT NULL,
            rule_mode TEXT NOT NULL DEFAULT 'at_least_one',
            rule_threshold INTEGER NOT NULL DEFAULT 1,
            runtime_seconds REAL NOT NULL DEFAULT 0
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS result_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            group_index INTEGER NOT NULL,
            group_values TEXT NOT NULL,
            FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE
        )
        """,
    ]



def get_index_sql() -> list[str]:
    return [
        """
        CREATE INDEX IF NOT EXISTS idx_runs_created_at
        ON runs(created_at)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_result_groups_run_id
        ON result_groups(run_id)
        """,
    ]
