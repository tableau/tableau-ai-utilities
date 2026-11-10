# Calc Optimizer

Optimizes one existing Tableau calculated field per run for performance, without changing what it returns. Runs the calc against a locked 5-tier Performance Hierarchy, proposes a rewrite (or delivers an "already optimal" verdict), verifies the rewrite returns identical values on a scratch worksheet, and passes an 8-check Validation Gate plus a runtime equivalence check before delivery.

**Example:** You have `SUM(IF CONTAINS([Product Name], 'Chair') THEN [Sales] ELSE 0 END)` (tier 5: row-level string op inside an aggregation). The skill ranks it as tier 5, proposes `{FIXED IF CONTAINS([Product Name], 'Chair') THEN 'Chair' ELSE 'Other' END : SUM([Sales])}` as a tier-3 rewrite, verifies both formulas return the same values grouped by relevant dimensions, passes the V-gate, and hands you back the optimized calc plus a `calc_optimize_handoff/1` YAML with the tier movement, trade-offs, and equivalence confirmation.

## What it does

Consumes a `calc_debug_handoff/1` payload from calc-debugger, or fires standalone on a perf ask. Reads the original formula, ranks it against the Performance Hierarchy, generates rewrite candidates in decreasing-tier order, filters candidates through the V-gate, authors the best surviving candidate via `author-calc`, verifies runtime equivalence on a scratch worksheet, and emits `calc_optimize_handoff/1`. Renders a locked Trade-offs block on every delivery.

## When to use it

Fires on "optimize this calc," "make this calc faster," "this calc is slow," "speed up this calculation," "why is this calc slow," "perf-tune this calc," or when a `calc_debug_handoff/1` arrives with a `perf_advisory` flag and the user says "now optimize it."

Do NOT invoke for writing new calcs (`calc-writer`), fixing broken/wrong-value calcs (`calc-debugger`), style/naming/house-style rewrites (`calc-linter`), cataloging calcs across a data source (`calc-inventory`), dashboard-level perf (`workbook-auditor`), or model/relationship perf (`join-and-relationship-advisor`).

## What makes this skill distinctive

- **Perf-only scope.** Never touches correctness bugs or style. Correctness routes to calc-debugger by exact slug; style routes to calc-linter by exact slug.
- **Value-preserving hard constraint.** Optimized formula must return identical values to the original for every group. Verified via mandatory runtime equivalence check, not static analysis.
- **"Already optimal" is a real verdict.** When no meaningful rewrite exists, the skill delivers an explicit verdict with rationale rather than fabricating an improvement. Handoff emits with `optimized_formula == original_formula` and `already_optimal: true`.
- **Locked Trade-offs block on every delivery.** Readability, maintainability, grain-sensitivity, and downstream impact each render even for pure wins ("None surfaced" is a valid body). Report shape is deterministic.
- **Fail-open equivalence verification.** If the runtime equivalence check fails twice (tool blip, scratch sheet issue), the skill marks `verified_equivalent: false, equivalence_sample_size: "verification_skipped"` and delivers with an explicit warning. User keeps control; skill never claims a pass it didn't earn.
- **Runtime-resolved derivation prefixes.** Uses the calc's actual AGG-flag via `list-available-fields`/`resolve-field`. Never string-matches the formula for aggregation functions (matches the corrected rule from calc-debugger session 2026-09-06).

## Handoff contract

Emits `calc_optimize_handoff/1` unprompted after every delivery, including "already optimal" verdicts. Required non-blank fields: `optimization_tier_movement`, `trade_offs` (all four subsections), `verified_equivalent`, `perf_advisory`, `overwrites_original`, `already_optimal`.

Downstream consumers: calc-linter (style pass after optimization), calc-inventory (catalog inclusion), workbook-auditor (dashboard-level perf rollup).

## Hard constraints in force

- HC#1: single-calc-per-run default; multi-calc requires opt-in clarifier.
- HC#2: value-preserving; equivalence verified at runtime.
- HC#5: no field, parameter, set, or hierarchy fabrication.
- HC#8: 8-check V-gate plus R-EQUIV-01 equivalence check.
- HC#10: perf-only; model-level slowness routes to join-and-relationship-advisor.
- HC#11: Trade-offs block always renders.
- HC#12: overwrite discipline; default is new calc `[original name] Fast`, overwrite requires explicit opt-in that user pressure never waives.

Full spec in `SKILL.md`. Performance Hierarchy in `skill-expertise/performance_hierarchy.md`. Validation Gate in `skill-expertise/validation_gate.md`. Handoff schema in `skill-expertise/handoff_schema.md`. Function library in `skill-expertise/` (`INDEX.md` plus one file per function category).
