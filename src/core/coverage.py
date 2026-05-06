from itertools import combinations

from src.core.generator import generate_j_groups, generate_s_subsets
from src.core.models import CoverageReport, CoverageRule, CoverageTarget


def is_subset_covered_by_group(
    s_subset: tuple[int, ...],
    k_group: tuple[int, ...],
) -> bool:
    return set(s_subset).issubset(set(k_group))


def build_coverage_targets(samples: list[int], j: int, s: int) -> list[CoverageTarget]:
    targets: list[CoverageTarget] = []
    j_groups = generate_j_groups(samples, j)

    for j_group in j_groups:
        s_subsets = generate_s_subsets(j_group, s)
        for s_subset in s_subsets:
            targets.append(CoverageTarget(j_group=j_group, s_subset=s_subset))

    return targets


def build_compact_j_group_targets(samples: list[int], j: int) -> list[CoverageTarget]:
    return [CoverageTarget(j_group=j_group, s_subset=()) for j_group in generate_j_groups(samples, j)]


def is_compact_target(target: CoverageTarget) -> bool:
    return target.s_subset == ()


def index_targets(targets: list[CoverageTarget]) -> dict[CoverageTarget, int]:
    return {target: index for index, target in enumerate(targets)}


def build_group_cover_map(
    k_groups: list[tuple[int, ...]],
    targets: list[CoverageTarget],
) -> dict[tuple[int, ...], set[int]]:
    cover_map: dict[tuple[int, ...], set[int]] = {}

    for k_group in k_groups:
        covered_indices: set[int] = set()
        k_group_set = set(k_group)

        for index, target in enumerate(targets):
            if set(target.s_subset).issubset(k_group_set):
                covered_indices.add(index)

        cover_map[k_group] = covered_indices

    return cover_map


def build_compact_j_group_cover_map(
    k_groups: list[tuple[int, ...]],
    targets: list[CoverageTarget],
    s: int,
) -> dict[tuple[int, ...], set[int]]:
    if not targets:
        return {group: set() for group in k_groups}

    target_index_by_group = {target.j_group: index for index, target in enumerate(targets)}
    all_sample_values = sorted({value for target in targets for value in target.j_group})
    j_size = len(targets[0].j_group)
    extension_size = j_size - s
    cover_map: dict[tuple[int, ...], set[int]] = {}

    for k_group in k_groups:
        covered_indices: set[int] = set()
        seen_j_groups: set[tuple[int, ...]] = set()

        for s_subset in combinations(k_group, s):
            extension_pool = [value for value in all_sample_values if value not in s_subset]
            for extension in combinations(extension_pool, extension_size):
                j_group = tuple(sorted(s_subset + extension))
                if j_group in seen_j_groups:
                    continue
                seen_j_groups.add(j_group)
                target_index = target_index_by_group.get(j_group)
                if target_index is not None:
                    covered_indices.add(target_index)

        cover_map[k_group] = covered_indices

    return cover_map


def build_target_cover_map(
    k_groups: list[tuple[int, ...]],
    targets: list[CoverageTarget],
) -> dict[int, set[tuple[int, ...]]]:
    target_cover_map: dict[int, set[tuple[int, ...]]] = {index: set() for index in range(len(targets))}

    for k_group in k_groups:
        k_group_set = set(k_group)

        for index, target in enumerate(targets):
            if set(target.s_subset).issubset(k_group_set):
                target_cover_map[index].add(k_group)

    return target_cover_map


def get_covered_target_indices(
    selected_groups: list[tuple[int, ...]],
    group_cover_map: dict[tuple[int, ...], set[int]],
) -> set[int]:
    covered: set[int] = set()

    for group in selected_groups:
        covered.update(group_cover_map.get(group, set()))

    return covered


def group_targets_by_j(targets: list[CoverageTarget]) -> dict[tuple[int, ...], list[CoverageTarget]]:
    grouped: dict[tuple[int, ...], list[CoverageTarget]] = {}

    for target in targets:
        grouped.setdefault(target.j_group, []).append(target)

    return grouped


def count_covered_targets_for_j_group(
    selected_groups: list[tuple[int, ...]],
    j_group: tuple[int, ...],
    targets: list[CoverageTarget],
    group_cover_map: dict[tuple[int, ...], set[int]],
) -> int:
    covered_indices = get_covered_target_indices(selected_groups, group_cover_map)
    count = 0

    for index, target in enumerate(targets):
        if target.j_group == j_group and index in covered_indices:
            count += 1

    return count


def check_j_group_rule(
    selected_groups: list[tuple[int, ...]],
    j_group: tuple[int, ...],
    targets: list[CoverageTarget],
    group_cover_map: dict[tuple[int, ...], set[int]],
    rule: CoverageRule,
) -> bool:
    total_for_j = sum(1 for target in targets if target.j_group == j_group)
    covered_for_j = count_covered_targets_for_j_group(
        selected_groups=selected_groups,
        j_group=j_group,
        targets=targets,
        group_cover_map=group_cover_map,
    )

    if rule.mode == "at_least_one":
        return covered_for_j >= 1

    if rule.mode == "all":
        return covered_for_j == total_for_j

    if rule.mode == "at_least_n":
        return covered_for_j >= rule.threshold

    raise ValueError(f"Unsupported rule mode: {rule.mode}")


def check_overall_rule(
    selected_groups: list[tuple[int, ...]],
    targets: list[CoverageTarget],
    group_cover_map: dict[tuple[int, ...], set[int]],
    rule: CoverageRule,
) -> bool:
    grouped_targets = group_targets_by_j(targets)

    for j_group in grouped_targets:
        if not check_j_group_rule(
            selected_groups=selected_groups,
            j_group=j_group,
            targets=targets,
            group_cover_map=group_cover_map,
            rule=rule,
        ):
            return False

    return True


def calculate_coverage_report(
    selected_groups: list[tuple[int, ...]],
    targets: list[CoverageTarget],
    group_cover_map: dict[tuple[int, ...], set[int]],
    rule: CoverageRule,
) -> CoverageReport:
    covered_indices = get_covered_target_indices(selected_groups, group_cover_map)
    uncovered_targets = [target for index, target in enumerate(targets) if index not in covered_indices]

    total_targets = len(targets)
    covered_targets = len(covered_indices)
    coverage_ratio = 0.0 if total_targets == 0 else covered_targets / total_targets

    is_satisfied = check_overall_rule(
        selected_groups=selected_groups,
        targets=targets,
        group_cover_map=group_cover_map,
        rule=rule,
    )

    summary_text = f"Covered {covered_targets}/{total_targets} targets ({coverage_ratio:.2%}) | Rule satisfied: {is_satisfied}"

    return CoverageReport(
        total_targets=total_targets,
        covered_targets=covered_targets,
        coverage_ratio=coverage_ratio,
        is_satisfied=is_satisfied,
        summary_text=summary_text,
        uncovered_targets=uncovered_targets,
    )
