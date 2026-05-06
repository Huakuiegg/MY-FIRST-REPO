from src.services.selection_service import SelectionService
from src.core.models import SelectionParams
from src.storage.database import initialize_database

initialize_database()
service = SelectionService()

# Enhanced validation with accuracy tests for improved optimizer (exact + preprocessing + rarity scoring)
examples = [
    {"name": "Example 8", "params": SelectionParams(m=45, n=10, k=6, j=6, s=4), "mode": "manual", "samples": "1 2 3 4 5 6 7 8 9 10", "rule": "at_least_one", "threshold": 1},
    {"name": "Example 9", "params": SelectionParams(m=45, n=12, k=6, j=6, s=4), "mode": "manual", "samples": "1 2 3 4 5 6 7 8 9 10 11 12", "rule": "at_least_one", "threshold": 1},
    {"name": "Accuracy Test n=8 all (j=4,s=4)", "params": SelectionParams(m=45, n=8, k=6, j=4, s=4), "mode": "manual", "samples": "1 2 3 4 5 6 7 8", "rule": "all", "threshold": 1},
]

for ex in examples:
    result = service.run_selection(ex["params"], ex["mode"], ex["samples"], ex["rule"], ex["threshold"])
    print("=" * 80)
    print(ex["name"])
    print("params:", result.params)
    print("rule:", result.rule)
    print("candidate_count:", result.candidate_count())
    print("target_count:", result.target_count)
    print("result_count:", result.result_count())
    print("coverage:", result.coverage_report.summary_text)
    print("groups:")
    for idx, group in enumerate(result.optimized_groups, start=1):
        print(f"  {idx}. {group}")
    # Accuracy assertions for known optimal/near-optimal results
    if "n=8" in ex["name"] and ex["rule"] == "all":
        assert result.result_count() <= 7, f"Expected <=7 groups for n=8 all case, got {result.result_count()}"
        print("PASSED: <=7 groups (exact solver succeeded)")
    elif "Example 8" in ex["name"]:
        assert result.result_count() <= 4, f"Expected small count for Example 8, got {result.result_count()}"
        print("PASSED: Accuracy validated for Example 8")
    print()
