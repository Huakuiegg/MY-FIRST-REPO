# Optimal Samples Selection System

A course project for combinatorial sample selection and coverage optimization.

## Project Overview

This system selects and optimizes groups of samples based on user-defined parameters:

- `m`: total number of available samples
- `n`: number of selected samples from `m`
- `k`: size of each result group
- `j`: size of intermediate comparison groups
- `s`: size of target subsets inside each `j`-group

The project models the task as a combinatorial coverage optimization problem and provides:

- random or manual sample input
- multiple coverage rule modes
- heuristic optimization for reducing result group count
- result display in a desktop GUI
- SQLite-based history storage and management

## Features

- Tkinter desktop interface
- SQLite result database
- Support for these rule modes:
  - `auto`
  - `all`
  - `at_least_one`
  - `at_least_n`
- Baseline and improved optimization logic implemented in the core modules
- Save, reload, view, and delete historical runs

## Project Structure

```text
project/
├─ app.py
├─ config.py
├─ course_report.txt
├─ data/
│  └─ results.db
├─ src/
│  ├─ core/
│  ├─ services/
│  ├─ storage/
│  ├─ ui/
│  └─ utils/
├─ group project.docx
└─ Group Project(26).pdf
```

## Main Modules

### `src/core/`
Contains the main algorithmic logic:
- data models
- parameter validation
- sample/group generation
- coverage calculation
- optimization strategy

### `src/services/`
Coordinates the main workflows:
- sample handling
- optimization execution
- history management

### `src/storage/`
Handles database logic:
- SQLite initialization
- table schema
- repositories for saving and loading runs

### `src/ui/`
Tkinter graphical user interface:
- input panel
- result panel
- history panel
- main window

## How to Run

Make sure Python is installed.

### Desktop version

Run the application with:

```bash
py app.py
```

If your environment supports `python` directly, you can also use:

```bash
python app.py
```

### Mobile Kivy version

There are two ways to run the mobile UI locally.

#### Option 1: run from project root

Install dependencies:

```bash
pip install -r requirements.txt
```

Then start the app:

```bash
python -m mobile_app.main
```

#### Option 2: run from `mobile_app/` directory

If your current directory is `mobile_app/`, install Kivy directly:

```bash
pip install kivy
```

Then start the app with:

```bash
python main.py
```

### Build APK with Buildozer

Recommended environment: Linux or WSL.

Example steps:

```bash
cd mobile_app
buildozer android debug
```

After the build succeeds, the generated APK will be placed in the `bin/` directory under `mobile_app/`.

### Build APK with GitHub Actions

If your local machine cannot use WSL or Linux packaging tools, you can build the APK with GitHub Actions.

This project includes the workflow file:

```text
.github/workflows/android-apk.yml
```

#### How to use

1. Create a new GitHub repository.
2. Upload this whole project to the repository.
3. Push to the `main` branch, or open the repository `Actions` tab and manually run `Build Android APK`.
4. Wait for the workflow to finish.
5. Open the workflow run.
6. Download the `android-apk` artifact.
7. Transfer the APK file to your Android phone and install it.

#### Notes

- The workflow runs on GitHub's Ubuntu runner.
- It builds a debug APK using `buildozer android debug`.
- The generated APK is uploaded as a workflow artifact.
- On first build, dependency download may take a long time.

## How to Use

1. Open the program.
2. Enter values for `m`, `n`, `k`, `j`, and `s`.
3. Choose input mode:
   - `Random`
   - `Manual`
4. Choose rule mode:
   - `auto`
   - `all`
   - `at_least_one`
   - `at_least_n`
5. If needed, enter a threshold for `at_least_n`.
6. Generate samples or type the samples manually.
7. Click `Run Optimization`.
8. Review the optimized result groups.
9. Save the run if needed.
10. Use the history panel to view, reload, or delete previous runs.

## Rule Interpretation

- `all`:
  every `j`-group must have all relevant `s`-subsets covered
- `at_least_one`:
  every `j`-group must have at least one covered `s`-subset
- `at_least_n`:
  every `j`-group must have at least `N` covered `s`-subsets
- `auto`:
  - if `j == s`, use `all`
  - otherwise, use `at_least_one`

## Optimization Strategy

The current implementation includes an improved optimizer combining exact and heuristic methods for higher accuracy (see `optimizer.py` and `selection_service.py`):

- exact set-cover solver (bitmask-accelerated, up to depth 7) for small fast-rule instances
- dominated group preprocessing (`remove_dominated_groups`)
- multi-start greedy with restricted candidate lists (RCL)
- enhanced scoring with rare-target frequency bonus in `score_group_with_j_diversity` + `compute_target_frequencies`
- local repair search, adaptive trial counts/time budgets, redundancy pruning

Now provides guaranteed optimal results on small instances via exact solver. Updated `_validate_89.py` includes accuracy assertions.

## Example Improvement Results

| Case | Before | After | Notes |
|---|----:|---:|-------|
| `n=8, k=6, j=4, s=4` | 8 | 7 | Exact solver (provably optimal) |
| `n=8, k=6, j=6, s=5, threshold=4` | 12 | 10 | Enhanced scoring + preprocessing |
| n=10/12 examples | - | 3/6 | Matches references |

## Database

Results are stored in:

```text
data/results.db
```

Stored information includes:
- parameters
- selected samples
- result groups
- coverage summary
- rule mode and threshold
- created time

## Report File

The generated course report is stored in:

```text
course_report.txt
```

## Notes

- The system uses integers such as `1, 2, 3, ...` to represent samples.
- It is designed to align with the assignment document examples and support flexible coverage rules.
- With the integrated exact solver (`exact_small_set_cover` with bitmask support), preprocessing, and rarity-aware scoring, the system now guarantees optimal results for small fast-rule instances while improving heuristic quality for others. Validation in `_validate_89.py` confirms <=7 groups for the n=8 all case.

## Future Improvements

Possible future work includes:
- supporting export to CSV or PDF
- improving the user interface
- adding more automated tests and benchmarks
- ILP/SAT solvers for medium instances
- parallel metaheuristics (GRASP, tabu search)
