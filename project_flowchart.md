# Project Flowchart (Mermaid)

> Open this file in an editor that supports Mermaid (e.g. VS Code + Mermaid extension),
> or paste the diagram into https://mermaid.live to export as PNG/SVG/PDF.

```mermaid
flowchart TD
  A[Start (app.py)] --> B[initialize_database()\ncreate/update data/results.db]
  B --> C[Create Tk root (tk.Tk)]
  C --> D[Create services\nSelectionService + HistoryService]
  D --> E[MainWindow]
  E --> F{User action}

  F -->|Generate Samples| G[generate_random_samples]
  G --> H[Fill input and switch to Manual]

  F -->|Run Optimization| I[Read params m,n,k,j,s + mode/samples]
  I --> J[Validate params/samples\nvalidate_params + validate_sample_values]
  J --> K[Resolve rule\nauto/all/at_least_one/at_least_n]
  K --> L[Generate candidate k-groups\nC(n,k)]
  L --> M[Build targets\nj-groups + s-subsets\n(or compact j-targets)]
  M --> N[Build cover map\ngroup_cover_map]
  N --> O[Optimize\noptimize_groups\nmultistart greedy + prune/repair\n(fast rules use bitmask)]
  O --> P[Coverage report\ncalculate_coverage_report]
  P --> Q[Display in GUI\ngroups/coverage/runtime]

  F -->|Save| R[HistoryService.save_run]
  R --> S[(runs table)]
  R --> T[(result_groups table)]
  S --> U[Refresh history list]
  T --> U

  F -->|View/Reload/Delete| V[HistoryService query/rerun/delete]
  V --> Q
  V --> U
```

