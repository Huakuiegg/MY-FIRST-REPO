import random
import re
from itertools import combinations


def normalize_group(values: list[int] | tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted(dict.fromkeys(values)))


def generate_random_samples(m: int, n: int) -> list[int]:
    return sorted(random.sample(range(1, m + 1), n))


def parse_manual_samples(text: str) -> list[int]:
    if not text or not text.strip():
        return []

    raw_parts = re.split(r"[\s,]+", text.strip())
    values: list[int] = []
    for part in raw_parts:
        if part:
            values.append(int(part))
    return values


def generate_combinations(items: list[int], size: int) -> list[tuple[int, ...]]:
    normalized_items = sorted(items)
    return [tuple(group) for group in combinations(normalized_items, size)]


def generate_k_groups(samples: list[int], k: int) -> list[tuple[int, ...]]:
    return generate_combinations(samples, k)


def generate_j_groups(samples: list[int], j: int) -> list[tuple[int, ...]]:
    return generate_combinations(samples, j)


def generate_s_subsets(group: tuple[int, ...], s: int) -> list[tuple[int, ...]]:
    return [tuple(subset) for subset in combinations(group, s)]


def build_candidate_group_map(samples: list[int], k: int) -> dict[int, tuple[int, ...]]:
    groups = generate_k_groups(samples, k)
    return {index + 1: group for index, group in enumerate(groups)}


def build_j_to_s_targets(
    samples: list[int],
    j: int,
    s: int,
) -> dict[tuple[int, ...], list[tuple[int, ...]]]:
    result: dict[tuple[int, ...], list[tuple[int, ...]]] = {}
    j_groups = generate_j_groups(samples, j)
    for j_group in j_groups:
        result[j_group] = generate_s_subsets(j_group, s)
    return result


def count_candidate_groups(samples: list[int], k: int) -> int:
    return len(generate_k_groups(samples, k))
