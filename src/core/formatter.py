from src.core.models import SelectionParams


def format_group(group: tuple[int, ...]) -> str:
    return ", ".join(str(value) for value in group)


def format_groups(groups: list[tuple[int, ...]]) -> list[str]:
    return [format_group(group) for group in groups]


def format_samples(samples: list[int]) -> str:
    return ", ".join(str(sample) for sample in samples)


def build_run_label(params: SelectionParams, run_index: int, result_count: int) -> str:
    return (
        f"{params.m}-"
        f"{params.n}-"
        f"{params.k}-"
        f"{params.j}-"
        f"{params.s}-"
        f"{run_index}-"
        f"{result_count}"
    )


def serialize_int_list(values: list[int]) -> str:
    return ",".join(str(value) for value in values)


def deserialize_int_list(text: str) -> list[int]:
    cleaned = (text or "").strip()
    if not cleaned:
        return []
    return [int(part.strip()) for part in cleaned.split(",") if part.strip()]


def serialize_groups(groups: list[tuple[int, ...]]) -> str:
    serialized_chunks: list[str] = []
    for group in groups:
        serialized_chunks.append(",".join(str(value) for value in group))
    return ";".join(serialized_chunks)


def deserialize_groups(text: str) -> list[tuple[int, ...]]:
    cleaned = (text or "").strip()
    if not cleaned:
        return []

    groups: list[tuple[int, ...]] = []
    for chunk in cleaned.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        values = [int(part.strip()) for part in chunk.split(",") if part.strip()]
        groups.append(tuple(values))
    return groups


def format_run_summary(
    params: SelectionParams,
    sample_count: int,
    candidate_count: int,
    target_count: int,
    result_count: int,
    coverage_ratio: float,
) -> str:
    return (
        f"m={params.m}, n={params.n}, k={params.k}, j={params.j}, s={params.s} | "
        f"Samples={sample_count} | Candidates={candidate_count} | "
        f"Targets={target_count} | Results={result_count} | "
        f"Coverage={coverage_ratio:.2%}"
    )
