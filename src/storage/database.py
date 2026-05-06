import sqlite3
from pathlib import Path

from config import get_db_path
from src.storage.schema import get_index_sql, get_schema_sql



def ensure_database_directory() -> None:
    db_path = Path(get_db_path())
    db_path.parent.mkdir(parents=True, exist_ok=True)



def get_connection() -> sqlite3.Connection:
    ensure_database_directory()
    connection = sqlite3.connect(get_db_path())
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection



def initialize_database() -> None:
    ensure_database_directory()
    with get_connection() as connection:
        cursor = connection.cursor()
        for sql in get_schema_sql():
            cursor.execute(sql)
        try:
            cursor.execute("ALTER TABLE runs ADD COLUMN runtime_seconds REAL NOT NULL DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        for sql in get_index_sql():
            cursor.execute(sql)
        connection.commit()



def execute(sql: str, params: tuple = ()) -> None:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(sql, params)
        connection.commit()



def execute_and_return_lastrowid(sql: str, params: tuple = ()) -> int:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(sql, params)
        connection.commit()
        return int(cursor.lastrowid)



def executemany(sql: str, params_list: list[tuple]) -> None:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.executemany(sql, params_list)
        connection.commit()



def fetch_all(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()



def fetch_one(sql: str, params: tuple = ()) -> sqlite3.Row | None:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(sql, params)
        return cursor.fetchone()
