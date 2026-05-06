import random
import time
from itertools import combinations

from src.core.coverage import check_overall_rule, get_covered_target_indices
from src.core.models import CoverageRule, CoverageTarget


RANDOM_SEED = 360


def is_fast_set_cover_rule(rule: CoverageRule) -> bool:
    return rule.mode == "at_least_one" or (rule.mode == "at_least_n" and rule.threshold <= 1)


def get_union_covered(
    selected_groups: list[tuple[int, ...]],
    group_cover_map: dict[tuple[int, ...], set[int]],
) -> set[int]:
    covered: set[int] = set()
    for group in selected_groups:
        covered.update(group_cover_map.get(group, set()))
    return covered


def is_solution_valid(
    selected_groups: list[tuple[int, ...]],
    targets: list[CoverageTarget],
    group_cover_map: dict[tuple[int, ...], set[int]],
    rule: CoverageRule,
) -> bool:
    if is_fast_set_cover_rule(rule):
        return len(get_union_covered(selected_groups, group_cover_map)) == len(targets)
    return check_overall_rule(selected_groups, targets, group_cover_map, rule)



def build_bitmask_cover_map(
    candidate_groups: list[tuple[int, ...]],
    group_cover_map: dict[tuple[int, ...], set[int]],
) -> list[tuple[tuple[int, ...], int]]:
    bitmask_cover_map: list[tuple[tuple[int, ...], int]] = []
    for group in candidate_groups:
        mask = 0
        for target_index in group_cover_map.get(group, set()):
            mask |= 1 << target_index
        if mask:
            bitmask_cover_map.append((group, mask))
    bitmask_cover_map.sort(key=lambda item: (-item[1].bit_count(), item[0]))
    return bitmask_cover_map


def remove_dominated_groups(
    bitmask_cover_map: list[tuple[tuple[int, ...], int]],
) -> list[tuple[tuple[int, ...], int]]:
    """Remove groups whose coverage mask is a strict subset of another.
    Classic set-cover preprocessing; preserves optimality for minimum cover.
    Runs in O(n^2) but n<=200 is negligible and shrinks search space significantly.
    """
    if len(bitmask_cover_map) <= 1:
        return bitmask_cover_map[:]

    # Work with copy and sort by coverage size descending (larger first less likely dominated)
    sorted_map = sorted(
        bitmask_cover_map, key=lambda x: (-x[1].bit_count(), x[0])
    )
    kept: list[tuple[tuple[int, ...], int]] = []

    for group_item in sorted_map:
        group, mask = group_item
        is_dominated = False
        for kept_group, kept_mask in kept:
            if (mask & kept_mask) == mask and mask != kept_mask:
                is_dominated = True
                break
        if not is_dominated:
            kept.append((group, mask))

    # Re-sort to match original ordering preference
    kept.sort(key=lambda item: (-item[1].bit_count(), item[0]))
    return kept



def greedy_bitmask_set_cover(
    bitmask_cover_map: list[tuple[tuple[int, ...], int]],
    target_count: int,
    rng: random.Random | None = None,
    restricted_candidate_size: int = 1,
) -> list[tuple[int, ...]]:
    full_mask = (1 << target_count) - 1
    covered_mask = 0
    selected_groups: list[tuple[int, ...]] = []
    used_indices: set[int] = set()
    while covered_mask != full_mask:
        ranked: list[tuple[int, int]] = []
        for index, (_group, mask) in enumerate(bitmask_cover_map):
            if index in used_indices:
                continue
            gain = (mask & ~covered_mask).bit_count()
            if gain > 0:
                ranked.append((index, gain))
        if not ranked:
            break
        ranked.sort(key=lambda item: -item[1])
        rcl_size = max(1, min(restricted_candidate_size, len(ranked)))
        if rng is None or rcl_size == 1:
            best_index = ranked[0][0]
        else:
            best_index = rng.choice(ranked[:rcl_size])[0]
        group, mask = bitmask_cover_map[best_index]
        selected_groups.append(group)
        used_indices.add(best_index)
        covered_mask |= mask
    return selected_groups



def prune_bitmask_solution(
    selected_groups: list[tuple[int, ...]],
    group_to_mask: dict[tuple[int, ...], int],
    target_count: int,
) -> list[tuple[int, ...]]:
    full_mask = (1 << target_count) - 1
    pruned = selected_groups[:]
    changed = True
    while changed:
        changed = False
        for group in pruned[:]:
            covered_mask = 0
            for item in pruned:
                if item != group:
                    covered_mask |= group_to_mask.get(item, 0)
            if covered_mask == full_mask:
                pruned.remove(group)
                changed = True
                break
    return pruned



def choose_fast_time_budget(candidate_count: int, target_count: int) -> float:
    """Adaptive time budget. Increased slightly to leverage exact solver,
    dominated-group preprocessing, and improved scoring for higher accuracy.
    """
    if candidate_count <= 300:
        return 1.0  # more time for exact + local improve on small cases
    if candidate_count <= 1500:
        return 4.0
    if candidate_count <= 6000:
        return 2.5
    return 3.5



def generate_bitmask_removal_sets(
    selected_groups: list[tuple[int, ...]],
    max_single_count: int = 24,
    max_pair_count: int = 80,
) -> list[list[tuple[int, ...]]]:
    removal_sets: list[list[tuple[int, ...]]] = []
    for group in selected_groups[:max_single_count]:
        removal_sets.append([group])

    pair_count = 0
    pair_source = selected_groups[: min(len(selected_groups), 20)]
    for i in range(len(pair_source)):
        for j in range(i + 1, len(pair_source)):
            removal_sets.append([pair_source[i], pair_source[j]])
            pair_count += 1
            if pair_count >= max_pair_count:
                return removal_sets
    return removal_sets



def repair_bitmask_solution(
    partial_groups: list[tuple[int, ...]],
    bitmask_cover_map: list[tuple[tuple[int, ...], int]],
    group_to_mask: dict[tuple[int, ...], int],
    target_count: int,
    rng: random.Random,
    restricted_candidate_size: int,
) -> list[tuple[int, ...]]:
    full_mask = (1 << target_count) - 1
    repaired = partial_groups[:]
    selected_set = set(repaired)
    covered_mask = 0
    for group in repaired:
        covered_mask |= group_to_mask.get(group, 0)

    while covered_mask != full_mask:
        ranked: list[tuple[int, int]] = []
        for index, (group, mask) in enumerate(bitmask_cover_map):
            if group in selected_set:
                continue
            gain = (mask & ~covered_mask).bit_count()
            if gain > 0:
                ranked.append((index, gain))
        if not ranked:
            break
        ranked.sort(key=lambda item: -item[1])
        rcl_size = max(1, min(restricted_candidate_size, len(ranked)))
        best_index = rng.choice(ranked[:rcl_size])[0] if rcl_size > 1 else ranked[0][0]
        group, mask = bitmask_cover_map[best_index]
        repaired.append(group)
        selected_set.add(group)
        covered_mask |= mask
    return repaired



def local_improve_bitmask_solution(
    selected_groups: list[tuple[int, ...]],
    bitmask_cover_map: list[tuple[tuple[int, ...], int]],
    group_to_mask: dict[tuple[int, ...], int],
    target_count: int,
    rng: random.Random,
    max_rounds: int = 3,
) -> list[tuple[int, ...]]:
    best = prune_bitmask_solution(selected_groups, group_to_mask, target_count)
    if len(best) <= 2:
        return best

    restricted_sizes = [2, 3, 4]
    for round_index in range(max_rounds):
        improved = False
        restricted_candidate_size = restricted_sizes[round_index % len(restricted_sizes)]
        for removal_set in generate_bitmask_removal_sets(best):
            partial = [group for group in best if group not in removal_set]
            repaired = repair_bitmask_solution(
                partial,
                bitmask_cover_map,
                group_to_mask,
                target_count,
                rng,
                restricted_candidate_size,
            )
            repaired = prune_bitmask_solution(repaired, group_to_mask, target_count)
            if len(repaired) < len(best):
                best = repaired
                improved = True
                break
        if not improved:
            break
    return best



def optimize_fast_rule_with_bitmasks(
    candidate_groups: list[tuple[int, ...]],
    targets: list[CoverageTarget],
    group_cover_map: dict[tuple[int, ...], set[int]],
    use_exact_first: bool = True,
) -> list[tuple[int, ...]]:
    bitmask_cover_map = build_bitmask_cover_map(candidate_groups, group_cover_map)
    if not bitmask_cover_map:
        return []

    # Preprocessing: remove dominated groups (improves accuracy and speed of exact + greedy)
    bitmask_cover_map = remove_dominated_groups(bitmask_cover_map)

    target_count = len(targets)
    group_to_mask = {group: mask for group, mask in bitmask_cover_map}

    # Exact-integration: try exact solver first for small fast-rule instances (provably optimal)
    if use_exact_first:
        exact_result = exact_small_set_cover(
            candidate_groups, targets, group_cover_map, max_depth=7, bitmask_cover_map=bitmask_cover_map
        )
        if exact_result:
            return prune_bitmask_solution(exact_result, group_to_mask, target_count)

    rng = random.Random(RANDOM_SEED)
    deadline = time.perf_counter() + choose_fast_time_budget(len(candidate_groups), target_count)

    best_result = prune_bitmask_solution(
        greedy_bitmask_set_cover(bitmask_cover_map, target_count),
        group_to_mask,
        target_count,
    )

    trial_index = 0
    while time.perf_counter() < deadline:
        restricted_candidate_size = 1 + (trial_index % 8)
        current = greedy_bitmask_set_cover(
            bitmask_cover_map,
            target_count,
            rng=rng,
            restricted_candidate_size=restricted_candidate_size,
        )
        current = prune_bitmask_solution(current, group_to_mask, target_count)
        current = local_improve_bitmask_solution(current, bitmask_cover_map, group_to_mask, target_count, rng)
        if len(current) < len(best_result):
            best_result = current
        trial_index += 1

    return best_result


def exact_small_set_cover(
    candidate_groups: list[tuple[int, ...]],
    targets: list[CoverageTarget],
    group_cover_map: dict[tuple[int, ...], set[int]],
    max_depth: int = 7,
    bitmask_cover_map: list[tuple[tuple[int, ...], int]] | None = None,
) -> list[tuple[int, ...]]:
    """Improved exact solver for small instances. Uses bitmasks when provided for speed.
    Returns the first (smallest cardinality) feasible cover found.
    """
    target_count = len(targets)
    if len(candidate_groups) > 200 or target_count > 300:
        return []

    if bitmask_cover_map is not None and target_count <= 64:  # bitmask limit
        return _exact_bitmask_set_cover(bitmask_cover_map, target_count, max_depth)

    # Fallback to original set-based for general case
    all_targets = set(range(target_count))
    ranked_groups = sorted(
        candidate_groups,
        key=lambda group: (-len(group_cover_map.get(group, set())), group),
    )

    for depth in range(1, max_depth + 1):
        for group_combo in combinations(ranked_groups, depth):
            covered: set[int] = set()
            for group in group_combo:
                covered.update(group_cover_map.get(group, set()))
                if len(covered) == len(all_targets):
                    return list(group_combo)
    return []


def _exact_bitmask_set_cover(
    bitmask_cover_map: list[tuple[tuple[int, ...], int]],
    target_count: int,
    max_depth: int = 7,
) -> list[tuple[int, ...]]:
    """Fast exact set cover using bitmasks and combinations on ranked list."""
    full_mask = (1 << target_count) - 1

    # Use the already ranked bitmask map (by coverage count)
    for depth in range(1, max_depth + 1):
        for combo_idx in combinations(range(len(bitmask_cover_map)), depth):
            covered_mask = 0
            selected: list[tuple[int, ...]] = []
            for idx in combo_idx:
                _, mask = bitmask_cover_map[idx]
                covered_mask |= mask
                selected.append(bitmask_cover_map[idx][0])
                if covered_mask == full_mask:
                    return selected
    return []

def score_group(
    group: tuple[int, ...],
    uncovered_targets: set[int],
    group_cover_map: dict[tuple[int, ...], set[int]],
) -> int:
    return len(group_cover_map.get(group, set()) & uncovered_targets)


def compute_target_frequencies(
    uncovered_targets: set[int],
    candidate_groups: list[tuple[int, ...]],
    group_cover_map: dict[tuple[int, ...], set[int]],
) -> dict[int, int]:
    """Compute how many remaining candidates cover each uncovered target.
    Used for rare-target bonus in scoring (prefer groups covering low-frequency targets).
    """
    freq: dict[int, int] = {t: 0 for t in uncovered_targets}
    for group in candidate_groups:
        covered = group_cover_map.get(group, set()) & uncovered_targets
        for t in covered:
            freq[t] = freq.get(t, 0) + 1
    return freq


def score_group_with_j_diversity(
    group: tuple[int, ...],
    uncovered_targets: set[int],
    group_cover_map: dict[tuple[int, ...], set[int]],
    targets: list[CoverageTarget],
    target_freq: dict[int, int] | None = None,
) -> tuple[int, int, float, int]:
    new_target_indices = group_cover_map.get(group, set()) & uncovered_targets
    j_groups = {targets[index].j_group for index in new_target_indices}
    new_count = len(new_target_indices)
    rarity_bonus = 0.0
    if target_freq and new_target_indices:
        rarity_bonus = sum(1.0 / max(1, target_freq.get(t, 1)) for t in new_target_indices)
    return (new_count, len(j_groups), rarity_bonus, -sum(group))


def rank_groups(
    candidate_groups: list[tuple[int, ...]],
    uncovered_targets: set[int],
    group_cover_map: dict[tuple[int, ...], set[int]],
    targets: list[CoverageTarget],
) -> list[tuple[int, ...]]:
    if not uncovered_targets or not candidate_groups:
        return []

    # Enhanced scoring: compute frequencies once per ranking for rare-target bonus
    target_freq = compute_target_frequencies(
        uncovered_targets, candidate_groups, group_cover_map
    )

    scored_groups: list[tuple[tuple[int, ...], tuple[int, int, float, int]]] = []
    for group in candidate_groups:
        score = score_group_with_j_diversity(
            group, uncovered_targets, group_cover_map, targets, target_freq
        )
        if score[0] > 0:
            scored_groups.append((group, score))

    # Sort: primary new covers, secondary j-diversity, tertiary rarity bonus, then tie-break
    scored_groups.sort(
        key=lambda item: (-item[1][0], -item[1][1], -item[1][2], item[0])
    )
    return [group for group, _score in scored_groups]


def select_best_group(
    candidate_groups: list[tuple[int, ...]],
    uncovered_targets: set[int],
    group_cover_map: dict[tuple[int, ...], set[int]],
    targets: list[CoverageTarget],
    rng: random.Random | None = None,
    restricted_candidate_size: int = 1,
) -> tuple[int, ...] | None:
    ranked = rank_groups(candidate_groups, uncovered_targets, group_cover_map, targets)
    if not ranked:
        return None
    rcl_size = max(1, min(restricted_candidate_size, len(ranked)))
    if rng is None or rcl_size == 1:
        return ranked[0]
    return rng.choice(ranked[:rcl_size])


def greedy_optimize(
    candidate_groups: list[tuple[int, ...]],
    targets: list[CoverageTarget],
    group_cover_map: dict[tuple[int, ...], set[int]],
    rule: CoverageRule,
    rng: random.Random | None = None,
    restricted_candidate_size: int = 1,
) -> list[tuple[int, ...]]:
    if is_fast_set_cover_rule(rule):
        return greedy_set_cover(candidate_groups, targets, group_cover_map, rng, restricted_candidate_size)

    selected_groups: list[tuple[int, ...]] = []
    all_target_indices = set(range(len(targets)))
    while not check_overall_rule(selected_groups, targets, group_cover_map, rule):
        covered_indices = get_covered_target_indices(selected_groups, group_cover_map)
        uncovered_targets = all_target_indices - covered_indices
        remaining_groups = [group for group in candidate_groups if group not in selected_groups]
        best_group = select_best_group(remaining_groups, uncovered_targets, group_cover_map, targets, rng, restricted_candidate_size)
        if best_group is None:
            break
        selected_groups.append(best_group)
    return selected_groups


def greedy_set_cover(
    candidate_groups: list[tuple[int, ...]],
    targets: list[CoverageTarget],
    group_cover_map: dict[tuple[int, ...], set[int]],
    rng: random.Random | None = None,
    restricted_candidate_size: int = 1,
) -> list[tuple[int, ...]]:
    selected_groups: list[tuple[int, ...]] = []
    selected_set: set[tuple[int, ...]] = set()
    uncovered_targets = set(range(len(targets)))

    while uncovered_targets:
        remaining_groups = [group for group in candidate_groups if group not in selected_set]
        best_group = select_best_group(remaining_groups, uncovered_targets, group_cover_map, targets, rng, restricted_candidate_size)
        if best_group is None:
            break
        selected_groups.append(best_group)
        selected_set.add(best_group)
        uncovered_targets -= group_cover_map.get(best_group, set())
    return selected_groups


def prune_redundant_groups(
    selected_groups: list[tuple[int, ...]],
    targets: list[CoverageTarget],
    group_cover_map: dict[tuple[int, ...], set[int]],
    rule: CoverageRule,
) -> list[tuple[int, ...]]:
    pruned_groups = selected_groups[:]
    changed = True
    while changed:
        changed = False
        for group in pruned_groups[:]:
            trial_groups = [item for item in pruned_groups if item != group]
            if is_solution_valid(trial_groups, targets, group_cover_map, rule):
                pruned_groups = trial_groups
                changed = True
                break
    return pruned_groups


def repair_solution(
    partial_groups: list[tuple[int, ...]],
    candidate_groups: list[tuple[int, ...]],
    targets: list[CoverageTarget],
    group_cover_map: dict[tuple[int, ...], set[int]],
    rule: CoverageRule,
    rng: random.Random,
    restricted_candidate_size: int,
) -> list[tuple[int, ...]]:
    repaired = partial_groups[:]
    selected_set = set(repaired)
    all_target_indices = set(range(len(targets)))

    while not is_solution_valid(repaired, targets, group_cover_map, rule):
        covered_indices = get_union_covered(repaired, group_cover_map)
        uncovered_targets = all_target_indices - covered_indices
        remaining_groups = [group for group in candidate_groups if group not in selected_set]
        best_group = select_best_group(remaining_groups, uncovered_targets, group_cover_map, targets, rng, restricted_candidate_size)
        if best_group is None:
            break
        repaired.append(best_group)
        selected_set.add(best_group)
    return repaired


def generate_removal_sets(selected_groups: list[tuple[int, ...]], max_pair_count: int = 8) -> list[list[tuple[int, ...]]]:
    removal_sets: list[list[tuple[int, ...]]] = [[group] for group in selected_groups]
    pair_count = 0
    for i in range(len(selected_groups)):
        for j in range(i + 1, len(selected_groups)):
            removal_sets.append([selected_groups[i], selected_groups[j]])
            pair_count += 1
            if pair_count >= max_pair_count:
                return removal_sets
    return removal_sets


def local_improve(
    selected_groups: list[tuple[int, ...]],
    candidate_groups: list[tuple[int, ...]],
    targets: list[CoverageTarget],
    group_cover_map: dict[tuple[int, ...], set[int]],
    rule: CoverageRule,
    rng: random.Random,
    restricted_candidate_size: int,
    max_iterations: int = 5,
) -> list[tuple[int, ...]]:
    best = prune_redundant_groups(selected_groups, targets, group_cover_map, rule)
    if len(candidate_groups) > 300:
        return best

    iteration = 0
    improved = True
    while improved and iteration < max_iterations:
        improved = False
        iteration += 1
        for removal_set in generate_removal_sets(best):
            partial = [group for group in best if group not in removal_set]
            repaired = repair_solution(partial, candidate_groups, targets, group_cover_map, rule, rng, restricted_candidate_size)
            repaired = prune_redundant_groups(repaired, targets, group_cover_map, rule)
            if is_solution_valid(repaired, targets, group_cover_map, rule) and len(repaired) < len(best):
                best = repaired
                improved = True
                break
    return best


def choose_restricted_candidate_size(candidate_count: int, trial_index: int) -> int:
    if candidate_count <= 50:
        return 2 + (trial_index % 3)
    if candidate_count <= 250:
        return 2 + (trial_index % 4)
    return 2


def multi_start_greedy(
    candidate_groups: list[tuple[int, ...]],
    targets: list[CoverageTarget],
    group_cover_map: dict[tuple[int, ...], set[int]],
    rule: CoverageRule,
    trials: int = 20,
    use_exact_first: bool = True,
) -> list[tuple[int, ...]]:
    rng = random.Random(RANDOM_SEED)
    best_result: list[tuple[int, ...]] = []

    if is_fast_set_cover_rule(rule):
        # use_exact_first is handled inside optimize_fast_rule_with_bitmasks
        return optimize_fast_rule_with_bitmasks(
            candidate_groups, targets, group_cover_map, use_exact_first
        )

    for trial_index in range(trials):
        restricted_candidate_size = choose_restricted_candidate_size(len(candidate_groups), trial_index)
        current_result = greedy_optimize(candidate_groups, targets, group_cover_map, rule, rng, restricted_candidate_size)
        current_result = prune_redundant_groups(current_result, targets, group_cover_map, rule)
        current_result = local_improve(current_result, candidate_groups, targets, group_cover_map, rule, rng, restricted_candidate_size)
        if is_solution_valid(current_result, targets, group_cover_map, rule) and (not best_result or len(current_result) < len(best_result)):
            best_result = current_result
    return best_result


def explain_group_scores(
    candidate_groups: list[tuple[int, ...]],
    uncovered_targets: set[int],
    group_cover_map: dict[tuple[int, ...], set[int]],
) -> list[tuple[tuple[int, ...], int]]:
    explanations = [(group, score_group(group, uncovered_targets, group_cover_map)) for group in candidate_groups]
    explanations.sort(key=lambda item: (-item[1], item[0]))
    return explanations


def optimize_groups(
    candidate_groups: list[tuple[int, ...]],
    targets: list[CoverageTarget],
    group_cover_map: dict[tuple[int, ...], set[int]],
    rule: CoverageRule,
    use_pruning: bool = True,
    trials: int = 20,
    use_exact_first: bool = True,
) -> list[tuple[int, ...]]:
    """use_exact_first enables the integrated exact solver for small fast-rule cases."""
    selected_groups = multi_start_greedy(
        candidate_groups, targets, group_cover_map, rule, trials, use_exact_first
    )
    if use_pruning and selected_groups:
        selected_groups = prune_redundant_groups(selected_groups, targets, group_cover_map, rule)
    return selected_groups
