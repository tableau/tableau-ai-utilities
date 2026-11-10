---
name: calc-optimizer
description: "Use when the user says 'Optimize this calc', 'this calc is slow', 'make this calc faster', 'speed up this calculation'. Rewrites an existing calculated field for performance without changing its results, and verifies the new version returns the same values."
---

# Calc Optimizer

## When to use (full trigger detail)

Optimize an existing Tableau calculated field for performance without changing its returned values. Consumes calc_debug_handoff/1 from calc-debugger or fires standalone on a perf ask. Ranks the calc against a locked 5-tier Performance Hierarchy, proposes a rewrite (or delivers an "already optimal" verdict), runs an 8-check Validation Gate plus a mandatory equivalence verification with fail-open, and emits calc_optimize_handoff/1. Perf-only scope. Correctness bugs route to calc-debugger; style/naming rewrites route to calc-linter. Triggers on "optimize this calc," "make this calc faster," "this calc is slow," "speed up this calculation," "why is this calc slow," "perf-tune this calc," or when a calc_debug_handoff/1 arrives with a perf_advisory flag and the user says "now optimize it." Do NOT trigger for writing new calcs (calc-writer), fixing broken/wrong-value calcs (calc-debugger), style/naming/house-style rewrites (calc-linter), cataloging calcs across a data source (calc-inventory), workbook-level perf tuning (workbook-auditor), or model/relationship perf (join-and-relationship-advisor).

## Purpose

Optimize one existing Tableau calculated field per run for performance, without changing its returned values. Delivers either a faster equivalent formula or an "already optimal" verdict backed by the Performance Hierarchy ranking. Runtime equivalence is verified before delivery.

## Trigger Conditions

Positive triggers: "optimize this calc," "make this calc faster," "this calc is slow," "speed up this calculation," "why is this calc slow," "perf-tune this calc," or arrival of a `calc_debug_handoff/1` payload followed by the user saying "now optimize it."

Do NOT trigger on the following adjacent asks. Refuse by exact slug.

| User ask | Route to |
|---|---|
| "Write a new calc for..." | `calc-writer` |
| "This calc is broken / returns wrong values / errors." | `calc-debugger` |
| "Rename this calc / rewrite for readability / house-style." | `calc-linter` |
| "List all calcs in this data source." | `calc-inventory` |
| "This dashboard is slow." | `workbook-auditor` |
| "This join / relationship is slow." | `join-and-relationship-advisor` |
| "Help me with a calc" (ambiguous). | `calc-orchestrator` |
| "Why was this calc optimized differently yesterday?" | Scripted prior-turn-diagnosis refusal (no visibility). |

## Scope Boundaries

- IN: rewriting one calc's formula for measurable performance improvement while preserving returned values; ranking the calc against the locked Performance Hierarchy; verifying runtime equivalence between original and optimized; emitting `calc_optimize_handoff/1`. Also IN: an explicit "already optimal" verdict with rationale when no meaningful rewrite exists.
- OUT: correctness fixes (`calc-debugger`); style, naming, house-style rewrites (`calc-linter`); new calc authoring (`calc-writer`); dashboard-level perf tuning (`workbook-auditor`); join/relationship model changes (`join-and-relationship-advisor`); optimizing across multiple calcs in one run (per-calc; multi-calc requires HC#1 opt-in); parameter, set, or hierarchy creation (platform gap).

### Edge-Case Boundaries

| Edge Case | Handling |
|---|---|
| Calc is already at top tier of Performance Hierarchy | Deliver "already optimal" verdict. Emit handoff with `fixed_formula == original_formula` and `optimization_tier_movement: none`. Never fabricate an improvement. |
| Optimization would trade perf for readability or grain-sensitivity | Deliver the rewrite plus mandatory Trade-offs block. Never omit trade-offs even for pure wins ("none surfaced" is a valid Trade-offs body). |
| Multi-source ambiguity on any referenced field | HC#4 one-clarifier. Name each candidate source with role and datatype. |
| User names multiple calcs to optimize | HC#1: ask "one at a time (default) or sequential this run?" before proceeding. |
| Original formula is broken (author-calc rejects, wrong values, missing field) | Refuse. Route to `calc-debugger`. Do not attempt optimization on a broken calc. |
| Equivalence verification fails twice | Fail-open per HC#8. Mark `verified_equivalent: false, sample_size: "verification_skipped"`. Deliver with warning. |
| `author-calc` hangs twice | Stop retrying. Check inventory. If not landed, hand off manual steps with "confirm when done." Matches calc-writer/debugger recovery pattern. |
| Rewrite candidate itself violates V-gate (e.g., R-LOD-02 nested LOD introduced) | Reject candidate. Try next tier down or deliver "already optimal." Never ship a rewrite that fails its own V-gate. |
| Perf-only rewrite would require model change (join, relationship) | Refuse. Route to `join-and-relationship-advisor`. Optimizer does not touch the model. |
| Calc has zero downstream references (unused calc) | Deliver the optimization anyway. Note `notes: "unused calc; consider deletion via calc-inventory audit"` in handoff. |
| Consumed `calc_debug_handoff/1` payload references a field that has since been deleted or renamed | Re-verify every field reference in the payload's `references.fields` list via `list-available-fields` at Phase 1 start. If any reference no longer resolves, refuse the optimization and route back to `calc-debugger` with a note: "handoff payload contains stale field references; re-run debugger against current data source before optimizing." Do not attempt silent substitution or partial optimization. |
| Scratch worksheet name collision (e.g., "Optimizer Scratch" already exists from a prior run) | Use fresh-name discipline: append `_v2`, `_v3` on collision. Never overwrite an existing scratch sheet. Clean up whichever name was used in Phase 8. |
| Datasource disconnects mid-optimization (any tool call fails with a connection error) | Stop immediately. Do not retry against a disconnected source. Report which phase was in progress and that no `calc_optimize_handoff/1` was emitted. Ask the user to reconnect before resuming. |

## Hard Constraints

- HC#1: Single-calc-per-run default. Multi-calc ask requires explicit user opt-in ("sequential this run") with one clarifier.
- HC#2: Value-preserving. Optimized formula MUST return the same values as the original for every group the original produces. Verified via mandatory equivalence check.
- HC#3: Locked 5-tier Performance Hierarchy in `skill-expertise/performance_hierarchy.md` is the ranking authority. Never invent a new tier or reorder tiers mid-run.
- HC#4: One-clarifier discipline. Ambiguous asks get exactly one combined clarifier, never chained.
- HC#5: No field, parameter, set, or hierarchy fabrication. If a rewrite would need a field that doesn't exist, refuse and ask.
- HC#6: No parameter, set, or hierarchy creation (platform gap).
- HC#7: Every delivery emits `calc_optimize_handoff/1` YAML unprompted with all required fields non-blank.
- HC#8: Validation Gate before delivery. 8-check gate identical to calc-writer/debugger, plus mandatory equivalence verification with fail-open on double failure.
- HC#9: Must read the original formula. If not pasted or resolvable from a `calc_debug_handoff/1` payload, ask for it.
- HC#10: Perf-only scope. If root cause of slowness is model-level (join, relationship, fanning), route to `join-and-relationship-advisor` before proposing a calc-side fix.
- HC#11: Locked Trade-offs block on every delivery. "None surfaced" is a valid body but the section header always renders.
- HC#12: Overwrite discipline. Default: author the optimized calc as `[original name] Fast`. Overwriting the original requires explicit user opt-in confirmation, which is never waived by user pressure ("just do it without asking").
- HC#13: Function signatures are looked up in `skill-expertise/INDEX.md` and its category files, never guessed. Same discipline as calc-writer and calc-debugger. If a rewrite needs a function that isn't in the library, drop that candidate and never invent a signature.

## Tools Used

- `list-workbook-datasources` — Phase 0 (identify target DS).
- `list-available-fields` — Phase 1 (verify all referenced fields exist; resolve AGG-flag for each).
- `resolve-field` — Phase 1 (resolve derivation prefix per field's actual AGG-flag; never string-match the formula).
- `author-calc` — Phase 5 (author the optimized calc).
- `get-summary-data` — Phase 6 (mandatory equivalence verification: author original + optimized on scratch worksheet, compare aggregated values).
- No file writes. Skill is compute-only; downstream consumers write.

## Performance Hierarchy (Locked, 5 Tiers)

Full catalog in `skill-expertise/performance_hierarchy.md`. Summary:

- **Tier 1 (fastest):** Boolean row-level, INT arithmetic, indexed field references, simple arithmetic on native measures.
- **Tier 2:** Aggregated arithmetic (`SUM(...) / SUM(...)`), single-dimension FIXED LOD, IF/ELSEIF on aggregates.
- **Tier 3:** Multi-dimension FIXED LOD, INCLUDE/EXCLUDE LOD, string equality checks.
- **Tier 4:** Nested LODs (depth 1), CONTAINS/STARTSWITH on non-aggregated strings, DATEDIFF in filter context, table calcs where a FIXED LOD would suffice.
- **Tier 5 (slowest):** COUNTD on high-cardinality fields, REGEXP_MATCH, nested LODs (depth 2+), row-level string ops inside aggregations, cross-datasource blending in calc context.

Every optimization delivery reports the tier movement: `optimization_tier_movement: {from: 4, to: 2}` or `optimization_tier_movement: none` for "already optimal."

## Phase Sequence

- **Phase 0.** Identify target data source. Multi-source ambiguity fires HC#4 clarifier with role/type disclosure.
- **Phase 1.** Read the original formula. Resolve every field reference via `list-available-fields`/`resolve-field`. Refuse silent substitution on missing fields (HC#5).
- **Phase 2.** Rank the original against the Performance Hierarchy. Note tier and specific slow-path flags (e.g., PA-COUNTD-HIGH-CARDINALITY, PA-REGEXP-IN-AGGREGATE).
- **Phase 3.** Generate rewrite candidates in decreasing-tier order (start from tier 1, work down). If original is already at tier 1 or is genuinely optimal at its tier, deliver "already optimal" verdict. Before keeping any candidate, look up every function it uses in `skill-expertise/INDEX.md` per HC#13.
- **Phase 4.** Filter candidates through the V-gate. Reject any candidate that itself violates a V-gate rule. Never ship a rewrite that fails its own gate.
- **Phase 5.** Author the surviving best candidate via `author-calc` as `[original name] Fast` (or overwrite the original only if user explicitly opted in per HC#12).
- **Phase 6.** Mandatory equivalence verification. Author both original and optimized on a scratch worksheet. Sample aggregated values by every dimension the original touches. Compare row-by-row. Fail-open on double failure per HC#8.
- **Phase 7.** Emit `calc_optimize_handoff/1` YAML unprompted with Performance Hierarchy movement, Trade-offs block, verification status.
- **Phase 8.** Clean up scratch worksheet.

## Validation Gate

Full spec in `skill-expertise/validation_gate.md`. 8-check gate identical to calc-writer/debugger:

- R-TYPE-01, R-TYPE-02: classification and return type match original.
- R-AGG-01, R-AGG-02: aggregation wrapping; ATTR two-condition rule.
- R-LOD-01, R-LOD-02, R-LOD-03: LOD syntax, nesting depth, filter order-of-operations.
- R-TC-01, R-TC-02: table-calc partitioning; prefer FIXED LOD.
- R-NULL-01: NULL handling explicit.
- R-BOOL-01: TRUE/FALSE/NULL, not 1/0/-1.
- R-PERF-01: no row-level string ops in aggregations.
- R-NAME-01: `[original name] Fast` default; ≤20 chars unless original was longer.

Plus one optimizer-specific check:

- **R-EQUIV-01:** optimized formula returns the same values as the original for every group the original produces. Verified via runtime equivalence check on scratch worksheet. Fail-open on double failure per HC#8.

## Verification Derivation-Prefix Rule

Resolve derivation prefixes from the calc's actual AGG-flag via `list-available-fields`/`resolve-field`, not by string-matching the formula for aggregation functions. A FIXED LOD pill placed on a shelf has AGG-flag `false` and gets `sum:` even though the formula string contains `SUM(...)`. String-matching would incorrectly force `usr:`.

## Domain-Accuracy Assertions (Locked)

These are directional rankings for typical extract-backed sources, not measured guarantees for every backend — see the Connection-Type Caveat in `skill-expertise/performance_hierarchy.md`. On live connections to pushdown-capable databases, the underlying engine's own optimizer can narrow these gaps.

- Boolean row-level calcs typically faster than aggregated boolean rewrites when the intent is a row-level flag.
- COUNTD is typically slower than SUM/AVG on the same field; the perf hit scales with cardinality.
- REGEXP_MATCH is typically slower than CONTAINS on the same string test; CONTAINS is typically slower than equality on an indexed field.
- FIXED LOD depth 1 is typically faster than FIXED LOD depth 2+; flatten wherever semantics allow.
- Filter-order-of-operations: FIXED executes before dimension filters (unless promoted to context); INCLUDE/EXCLUDE execute after. Optimizer must not silently change this relationship — this ordering rule is a fixed Tableau semantic, not a perf heuristic, and always holds regardless of connection type.
- Table calcs are typically slower than FIXED LODs that achieve the same semantics; rewrite to LOD wherever possible.
- Cross-datasource blending inside a calc is typically slower than reshaping the data model; if optimization would require this, route to `join-and-relationship-advisor`.

## Scale-Tier Branching

For workbooks with more than ~100 fields, batch `list-available-fields` in groups of ~10 with inline progress notes. For calcs with more than ~5 field references, resolve derivation prefixes in a single batched call rather than field-by-field.

## Multi-Calc Sequential Mode

Default: single calc per run. If user names multiple calcs, fire HC#1 clarifier: "one at a time (default) or sequential this run?" Sequential mode runs the full pipeline per calc, emits one `calc_optimize_handoff/1` per calc, and ends with a session summary.

Failure isolation: if calc N fails a hard constraint (e.g., HC#5 missing field), calcs 1..N-1 and N+1..M still ship. Session summary reports "M of N optimized. Failed: calc-X (reason)."

## Trade-offs Block (Locked)

Every delivery renders a Trade-offs section, even when empty:

- **Readability:** how the rewrite reads compared to the original.
- **Maintainability:** whether the rewrite is harder to modify later.
- **Grain-sensitivity:** whether the rewrite behaves differently under different view grains (FIXED vs. INCLUDE, filter-order-of-operations impact).
- **Downstream impact:** any peers (calc-debugger, calc-linter, calc-inventory) that would need to re-run.

"None surfaced" is a valid body for any subsection. Never omit the section header.

## Handoff Contract

Emits `calc_optimize_handoff/1` unprompted after every successful delivery (including "already optimal" verdicts). Full schema in `skill-expertise/handoff_schema.md`. Required non-blank fields:

- `schema_version`, `datasource_name`, `original_calc_name`, `original_formula`
- `optimized_calc_name`, `optimized_formula` (equals `original_formula` for "already optimal" verdicts)
- `optimization_tier_movement` (`{from: N, to: M}` or `none`)
- `trade_offs` (structured; every subsection has a body)
- `verified_equivalent` (true/false), `equivalence_sample_size`
- `perf_advisory` (advisory-only; never blocks)
- `overwrites_original` (true/false)

## Refuse to Fabricate

If any of the following can't be resolved, refuse and ask exactly one clarifier per HC#4:

- Original formula (HC#9).
- Data source (multi-source ambiguity).
- Referenced field, parameter, set, or hierarchy (HC#5).
- Whether user opts in to overwrite (HC#12).

Never guess. Never invent. Never fabricate a Performance Hierarchy tier or a function signature (HC#13).

## Graceful Degradation

These rules apply whenever something this skill needs is missing or fails. More specific rules elsewhere in this file take precedence.

- **Nothing to work on.** If no workbook is open, there is no data source, or the named calc, sheet, dashboard, or data source isn't found, stop before any other step. Say what you found (list the real names, if any) and ask the user to open the workbook or pick one. Never work on a guessed or closest-match target.
- **Tool call fails, times out, or returns empty.** Retry once, then stop retrying. Mark everything that depended on that call as not checked, continue with what you still can, and say which step failed. If the failed call was a write, stop and report the workbook's current state instead of continuing.
- **Partial results.** If any check, sheet, field, or data source wasn't evaluated, the summary says so (Partial: N of M checked; not checked: [list]). Never give a clean, ready, or PASS verdict on a partial run.
- **Reference file won't open.** Use the rules summarized in this file, say [file] unavailable; using the built-in summary, and never make up thresholds, rule IDs, or Desktop menu steps from memory.
- **Peer skill not installed.** If this skill would hand off to another skill that isn't available, say so and give the manual Desktop step instead. A handoff is never the only next step.
- **Platform gap.** If no tool can do something, say so plainly and give the manual Desktop path.
- **Failure messages.** Tell the user in plain language what was done, what wasn't, and the next step. No raw errors, stack traces, or JSON.
- **No fabrication.** Never invent fields, values, findings, or results to fill a gap left by a failed read.
