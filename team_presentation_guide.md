# Team Presentation Guide - Optimal Samples Selection System

This guide is for teammates preparing the PPT and presentation.

## 1. Project Summary

The project is an **Optimal Samples Selection System**. It is not only a random sampling tool. It solves a **combinatorial coverage optimization problem**.

Main idea:

```text
Input parameters and samples
→ generate candidate k-groups
→ build coverage targets using j, s and rule
→ select a small number of result groups
→ display and store results
```

## 2. Parameter Meaning

| Parameter | Meaning |
|---|---|
| m | Total number of available samples |
| n | Number of selected samples from m |
| k | Size of each final result group |
| j | Size of each checking group |
| s | Size of subset inside each j-group |
| rule | Minimum number of s-subsets to be covered |

Example:

```text
m=45, n=10, k=6, j=6, s=4, rule=1
```

Meaning: choose or input 10 samples from 45 samples, generate all 6-sample candidate groups, and make sure every 6-sample checking group contains at least one covered 4-sample subset.

## 3. System Architecture

The project uses a layered architecture:

```text
UI Layer
  InputPanel / ResultPanel / HistoryPanel
        ↓
Service Layer
  SampleService / SelectionService / HistoryService
        ↓
Core Algorithm Layer
  Generator / Coverage / Optimizer / Validator / Formatter
        ↓
Storage Layer
  SQLite Database / Repositories
```

### UI Layer

Responsible for parameter input, Random n, Input n, Execute, Store, Clear, result display and database display.

### Service Layer

Coordinates the workflow between UI, algorithm and database.

### Core Algorithm Layer

Generates combinations, builds coverage targets, checks coverage rules and runs optimization.

### Storage Layer

Uses SQLite to store parameters, selected samples, optimized groups, coverage summary and history records.

## 4. System Workflow

```text
Start
↓
Input m, n, k, j, s and rule
↓
Validate parameters
↓
Choose Random n or Input n
↓
Generate or read n samples
↓
Generate all candidate k-groups
↓
Build coverage targets
↓
Build coverage map
↓
Run optimizer
↓
Display full results
↓
Store / Display / Delete database records
↓
End
```

## 5. Algorithm Design

### 5.1 Candidate Group Generation

After obtaining n samples, the system generates all k-groups.

```text
Number of candidate groups = C(n, k)
```

Example:

```text
C(10, 6) = 210
```

### 5.2 Coverage Target Construction

The system generates j-groups from n samples.

```text
Number of j-groups = C(n, j)
```

If all s-subsets are expanded:

```text
Total expanded targets = C(n, j) × C(j, s)
```

### 5.3 Set Cover Modeling

The optimization is modeled as a set cover problem.

- Each candidate k-group covers some targets.
- The goal is to select a small number of k-groups.
- All required targets must be covered.

Basic optimizer:

```text
While there are uncovered targets:
    choose the group covering the most uncovered targets
    add it to result set
    update uncovered targets
Remove redundant groups
Return result groups
```

## 6. Algorithm Optimizations

### 6.1 Compact Target Representation

For the common rule:

```text
at least 1 S sample
```

The system does not expand all s-subsets. Instead, it uses:

```text
|K ∩ J| ≥ s
```

Where:

- K = candidate k-group
- J = checking j-group
- s = required subset size

If K and J share at least s samples, K covers at least one s-subset of J.

Example 9:

```text
n=12, k=6, j=6, s=4
Expanded targets = C(12,6) × C(6,4) = 924 × 15 = 13860
Compact targets = C(12,6) = 924
```

This greatly reduces computation.

### 6.2 Bitmask Coverage Encoding

The newest optimization is bitmask-based coverage encoding.

Instead of using Python sets repeatedly, each group's covered targets are encoded as an integer bitmask.

Example:

```text
Target index:  1 2 3 4 5 6 7 8
Covered:       1 0 1 1 0 0 1 0
Bitmask:       10110010
```

Operations:

| Operation | Purpose |
|---|---|
| OR | Merge covered targets |
| AND | Calculate intersection |
| NOT | Find uncovered targets |
| bit_count() | Count covered targets |

This reduces repeated set operations and improves running time.

### 6.3 Redundancy Pruning

After a feasible result is found, the system checks whether any selected group can be removed. If coverage is still satisfied after removing one group, that group is deleted.

## 7. Project Iterations

### Version 1: Basic Functional Version

Implemented:

- GUI
- Parameter input
- Random and manual sample input
- Candidate generation
- Basic greedy optimizer
- Result display
- SQLite storage

Problems:

- Some cases were slow.
- UI did not fully match the assignment.
- Rule input was unclear.

### Version 2: UI and Rule Alignment

Improvements:

- Rule changed to `at least [ ] S sample`.
- Parameter limitation hints added.
- Random n and Input n logic improved.
- Generate Samples now switches to Input n.
- Input count validation added.
- Database display improved.

### Version 3: Algorithm Optimization

Improvements:

- Compact target representation.
- Set-cover based optimizer.
- Bitmask coverage encoding.
- Redundancy pruning.
- Runtime timer.
- Background thread to reduce UI freezing.

## 8. Features Developed

1. Tkinter GUI.
2. Parameter input with constraints.
3. Random n and Input n.
4. Input count validation.
5. Rule input: `at least [ ] S sample`.
6. Candidate group generation.
7. Coverage target construction.
8. Set-cover based optimizer.
9. Bitmask acceleration.
10. Runtime display.
11. Full result output.
12. SQLite database storage.
13. Store / Display / Delete history records.

## 9. Results Panel Output

The Results panel now displays full details, not only candidate groups and coverage targets.

It includes:

- Run parameters
- Selected samples
- Candidate groups count
- Coverage targets count
- Result groups count
- Rule description
- Coverage summary
- Every optimized result group

Example:

```text
Run Parameters
  45-10-6-6-4-1-3

Selected Samples
  1, 2, 3, 4, 5, 6, 7, 8, 9, 10

Statistics
  Candidate groups: 210
  Coverage targets: 210
  Result groups: 3
  Rule: For each j-group, at least one s-subset must be covered.

Coverage Summary
  Covered 210/210 targets (100.00%) | Rule satisfied: True

Optimized Result Groups
  Result 1: 1, 2, 3, 4, 5, 6
  Result 2: 1, 2, 3, 4, 7, 8
  Result 3: 5, 6, 7, 8, 9, 10
```

## 10. Sample Run Results

| Case | Parameters | Rule | Candidate Groups | Coverage Targets | Result Groups | Runtime |
|---|---|---|---:|---:|---:|---:|
| Example 8 | 45-10-6-6-4 | at least 1 | 210 | 210 | 3 | about 0.02s |
| Example 9 | 45-12-6-6-4 | at least 1 | 924 | 924 | 6 | about 0.37s |
| Additional Case | 45-10-6-5-4 | at least 1 | 210 | 252 | 7 | about 0.02s |

## 11. Limitations

Be honest in the presentation:

1. The system does not guarantee global optimality for every input.
2. Very large parameters may still cause long computation.
3. Compact target optimization mainly applies to `at least 1 S sample`.
4. More exact algorithms can be added in the future.
5. Print is currently a preview-style function.

Better wording:

```text
The system finds optimized feasible results, but does not guarantee global optimum for all possible inputs.
```

## 12. Suggested PPT Structure

1. Title
2. Background and Problem
3. Project Objective
4. System Architecture
5. Parameter Explanation
6. Algorithm Workflow
7. Optimization 1: Compact Target Representation
8. Optimization 2: Bitmask Coverage Encoding
9. Project Iterations V1-V3
10. Features and UI
11. Sample Run Results
12. Limitations and Future Work
13. Conclusion

## 13. 7-8 Minute Presentation Script

### 1. Project Goal

This project is an Optimal Samples Selection System. It solves a combinatorial coverage optimization problem. From many candidate groups, the system selects a smaller number of groups that satisfy the required coverage rule.

### 2. Architecture

The system has four layers: UI layer, service layer, core algorithm layer and storage layer. This separates user interaction, workflow control, algorithm logic and database storage.

### 3. Algorithm

The algorithm models the problem as a set cover problem. Each candidate k-group covers some coverage targets. The optimizer selects groups that cover the most uncovered targets until all targets are covered.

### 4. Compact Target Optimization

For at least-one S-sample rules, the system uses |K ∩ J| ≥ s instead of expanding all s-subsets. In Example 9, this reduces targets from 13860 to 924.

### 5. Bitmask Optimization

Each group's coverage targets are encoded as a bitmask. Coverage operations use OR, AND, NOT and bit_count(). This improves efficiency compared with repeated set operations.

### 6. Iterations

Version 1 completed the basic workflow. Version 2 improved UI and rule alignment. Version 3 optimized the algorithm using compact targets, bitmask encoding, pruning, runtime display and background execution.

### 7. Results

Example 8 produced 3 result groups in about 0.02 seconds. Example 9 produced 6 result groups in about 0.37 seconds. The system can efficiently produce coverage-satisfied results for medium-sized examples.

### 8. Limitations

The system uses heuristic optimization, so it does not guarantee global optimality for all inputs. Future work can include branch-and-bound exact solving, parallel computation and export functions.

## 14. Key Sentences

```text
The project models sample selection as a combinatorial coverage optimization problem.
```

```text
The optimizer is based on the set cover idea.
```

```text
For at least-one S-sample rules, the condition |K ∩ J| ≥ s is used to reduce target expansion.
```

```text
Coverage targets are encoded as bitmasks to accelerate coverage operations.
```

```text
The system produces optimized feasible results, but does not guarantee global optimality for all possible inputs.
```
