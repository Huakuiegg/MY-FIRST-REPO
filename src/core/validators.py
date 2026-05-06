from typing import Any

from src.core.generator import parse_manual_samples
from src.core.models import SelectionParams


def validate_positive_integer(value: object, field_name: str) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a positive integer.") from exc

    if number <= 0:
        raise ValueError(f"{field_name} must be a positive integer.")

    return number



def validate_mode(mode: str) -> str:
    normalized = (mode or "").strip().lower()
    if normalized not in {"random", "manual"}:
        raise ValueError("Mode must be either 'random' or 'manual'.")
    return normalized



def validate_params(params: SelectionParams) -> SelectionParams:
    m = validate_positive_integer(params.m, "m")
    n = validate_positive_integer(params.n, "n")
    k = validate_positive_integer(params.k, "k")
    j = validate_positive_integer(params.j, "j")
    s = validate_positive_integer(params.s, "s")

    validated = SelectionParams(m=m, n=n, k=k, j=j, s=s)
    validated.validate_relations()

    if not (45 <= m <= 54):
        raise ValueError("m must be between 45 and 54.")
    if not (7 <= n <= 25):
        raise ValueError("n must be between 7 and 25.")
    if not (4 <= k <= 7):
        raise ValueError("k must be between 4 and 7.")
    if not (3 <= s <= 7):
        raise ValueError("s must be between 3 and 7.")

    return validated



def validate_sample_values(samples: list[int], m: int, n: int) -> list[int]:
    if len(samples) != n:
        raise ValueError(f"Exactly {n} sample values are required.")
    if len(set(samples)) != len(samples):
        raise ValueError("Sample values must not contain duplicates.")

    normalized: list[int] = []
    for value in samples:
        if not isinstance(value, int):
            raise ValueError("All sample values must be integers.")
        if value < 1 or value > m:
            raise ValueError(f"Sample values must be between 1 and {m}.")
        normalized.append(value)

    return sorted(normalized)



def normalize_manual_input(text: str) -> str:
    parsed = parse_manual_samples(text)
    return " ".join(str(value) for value in parsed)



def parse_and_validate_manual_samples(text: str, m: int, n: int) -> list[int]:
    samples = parse_manual_samples(text)
    return validate_sample_values(samples=samples, m=m, n=n)
