from datetime import datetime
from typing import Any


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def safe_int(value: Any, default: int | None = None) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def unique_preserve_order(values: list[int]) -> list[int]:
    seen: set[int] = set()
    result: list[int] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def chunk_list(items: list[Any], size: int) -> list[list[Any]]:
    if size <= 0:
        raise ValueError("size must be greater than 0.")
    return [items[index:index + size] for index in range(0, len(items), size)]


def flatten_list(nested: list[list[Any]]) -> list[Any]:
    flattened: list[Any] = []
    for group in nested:
        flattened.extend(group)
    return flattened


def ensure_sorted_unique_ints(values: list[int]) -> list[int]:
    return sorted(set(values))
