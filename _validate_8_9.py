from src.services.selection_service import SelectionService
from src.core.models import SelectionParams
from src.storage.database import initialize_database

initialize_database()
service = SelectionService()

examples = [
    {"name": "Example 8", "params": SelectionParams(m=45, n=10, k=6, j=6, s=4), "samples": "1 2 3 4 5 6 7 8 9 10", "rule": "at_least_one", "threshold": 1},
    {"name": "Example 9", "params": SelectionParams(m=45, n=12, k=6, j=6, s=4), "samples": "1 2 3 4 5 6 7 8 9 10 11 12", "rule": "at_least_one", "threshold": 1},
]

for ex in examples:
    print("=" * 80)
    print(ex["name"])
    result = service.run_selection(ex["params"], "manual", ex["samples"], ex["rule"], ex["threshold"])
    print("target_count:", result.target_count)
    print("result_count:", result.result_count())
    print("coverage:", result.coverage_report.summary_text)
    print("groups:")
    for idx, group in enumerate(result.optimized_groups, start=1):
        print(f"  {idx}. {group}")
