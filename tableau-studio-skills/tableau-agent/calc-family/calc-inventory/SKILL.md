---
name: calc-inventory
description: "Use when the user says 'List all calcs in this data source', 'inventory my calcs', 'what calcs exist here?', 'catalog my calculated fields'. Catalogs every calculated field in one data source: type, formula, references, flags, and where it's used. Read-only."
---

# Calc Inventory

## When to use (full trigger detail)

Catalog every calculated field in one Tableau data source per run into a scannable markdown table plus a machine-readable calc_inventory_handoff/1 YAML. Read-only. Records per-calc name, type, formula, reference graph (fields, parameters, sets, nested calcs), style/perf/complexity flags, and usage metadata (shelf placements, dashboard refs). Batched pagination for data sources with 20+ calcs. Consumes any upstream calc_write_handoff/1, calc_debug_handoff/1, calc_optimize_handoff/1, or calc_lint_handoff/1 for single-calc catalog inclusion, or fires standalone on a data-source-wide inventory ask. Routes bulk-fix asks to the appropriate peer (calc-linter for style, calc-optimizer for perf, calc-debugger for correctness) one at a time. Triggers on list all calcs in this data source, inventory the calcs, catalog my calculated fields, show me every calc in this workbook, what calcs exist here, or when a calc-family handoff arrives and the user says add it to the inventory. Do NOT trigger for writing new calcs (calc-writer), fixing broken/wrong-value calcs (calc-debugger), performance rewrites (calc-optimizer), style rewrites (calc-linter), workbook-level cataloging beyond calcs (workbook-auditor), or data-model documentation (data-model-documenter).

## Purpose

Catalog every calculated field in one Tableau data source per run. Delivers a scannable markdown table plus a machine-readable `calc_inventory_handoff/1` YAML. Read-only. Records name, type, formula, reference graph, style/perf/complexity flags, and usage metadata per calc. Batched pagination for 20+ calcs.

## Trigger Conditions

Positive triggers: list all calcs in this data source, inventory the calcs, catalog my calculated fields, show me every calc in this workbook, what calcs exist here, or arrival of any upstream calc-family handoff (`calc_write_handoff/1` / `calc_debug_handoff/1` / `calc_optimize_handoff/1` / `calc_lint_handoff/1`) followed by add it to the inventory.

Do NOT trigger on the following adjacent asks. Refuse by exact slug.

| User ask | Route to |
|---|---|
| Write a new calc for... | `calc-writer` |
| This calc is broken / returns wrong values / errors. | `calc-debugger` |
| This calc is slow / optimize this calc. | `calc-optimizer` |
| Lint this calc / check style / rewrite for readability. | `calc-linter` |
| Audit calc quality or hygiene (naming drift, unused calcs, deep nesting, hard-coded values). | `calc-hygiene-scan` |
| Document this data model / tables / relationships. | `data-model-documenter` |
| Audit the whole workbook (dashboards, worksheets, calcs). | `workbook-auditor` |
| Help me with a calc (ambiguous). | `calc-orchestrator` |
| Why was this inventoried differently yesterday? | Scripted prior-turn-diagnosis refusal (no visibility). |
| Bulk-fix / bulk-rewrite / bulk-lint all flagged calcs. | Route to appropriate peer per HC#10; never absorb as a bulk action. |

## Scope Boundaries

- IN: cataloging every calc in one data source per run with locked schema (name, type, formula, reference graph, style/perf/complexity flags, usage metadata); rendering scannable markdown table plus `calc_inventory_handoff/1` YAML; batched pagination for 20+ calcs; consuming any upstream calc-family handoff for single-calc catalog inclusion. Also IN: an explicit empty inventory verdict when the data source has zero calcs.
- OUT: authoring, rewriting, or deleting any calc (`calc-writer` / `calc-linter` / `calc-optimizer` / `calc-debugger`); cataloging across multiple data sources in one run (one DS per run; multi-DS requires HC#1 opt-in); tables/relationships (`data-model-documenter`); dashboard-level or workbook-level cataloging (`workbook-auditor`); parameters, sets, or hierarchies (cited as references, never resolved deeper); calc routing (calc-orchestrator); bulk mutations of any kind.

### Edge-Case Boundaries

| Edge Case | Handling |
|---|---|
| Data source has zero calcs | Deliver empty inventory verdict. Emit handoff with `calcs: []`, `total_count: 0`. Never fabricate calc entries. |
| Data source has 20+ calcs | Batched pagination in groups of ~20 with inline progress notes. Full inventory delivered at end. |
| Data source has 100+ calcs | Additional batching for `list-available-fields` in groups of ~10 as default practice. Note batching method in handoff. |
| Multi-source workbook | HC#1 clarifier: which data source? One DS per run. |
| Consumed upstream handoff payload has stale field references | Re-verify at Phase 1 start via `list-available-fields`. If stale, still catalog the calc but flag `stale_references: [field_names]` in that entrys metadata. Do not refuse the inventory over one stale entry. |
| Calc references a parameter, set, or hierarchy | Cite by name in `references.parameters` / `references.sets` / `references.hierarchies`. Never resolve deeper (thats out of scope). |
| Calc references another calc (nested reference) | List in `references.nested_calcs`. Build the reference graph across the whole inventory. |
| Calc has zero shelf placements or dashboard references anywhere in the workbook | Record `usage: { shelf_placements: 0, dashboards: [], flag: unused }`. Surface as a cleanup candidate in the summary. |
| User asks for bulk fix all flagged style violations | Refuse per HC#10. Route to `calc-linter` one calc at a time. Never absorb. |
| User asks for bulk optimize all tier-5 calcs | Refuse per HC#10. Route to `calc-optimizer` one calc at a time. Never absorb. |
| User asks for delete all unused calcs | Refuse; explain that calc-inventory is read-only and no calc-delete tool exists on this platform. Deletion is a manual Desktop step. |
| Datasource disconnects mid-inventory | Stop immediately. Report which batch was in progress and how many calcs were successfully cataloged so far. Do not emit `calc_inventory_handoff/1`. Ask user to reconnect. |
| Very wide data source (>100 fields, unrelated to calc count) | Batch `list-available-fields` in ~10-field groups with inline progress notes; locked threshold is field count > 30. Same discipline as calc-linter. |
| Multi-source workbook, user explicitly opts into cataloging all data sources in one run | HC#1 sequential-mode opt-in: after the clarifier, if the user confirms all of them, run Phase 0-7 sequentially per data source (one inventory + one handoff per DS, never merged into a single cross-DS entry list). Announce which DS is being processed before each pass. Default without explicit opt-in remains one DS per run. |
| Style/perf/complexity flag heuristics come from `skill-expertise/style_catalog.md` and `skill-expertise/performance_hierarchy.md` | Read-only reference; never redefine or extend those catalogs mid-run. Cite rule IDs (S-*, PA-*) directly. |
| Usage-metadata tool unavailable (`get-workbook-inventory` returns error) | Proceed without usage data. Flag each calcs `usage` block as `unavailable_this_run: true` and note in handoff `notes`. Do not fabricate placements. |

## Hard Constraints

- HC#1: Single-data-source-per-run default. Multi-source workbooks require explicit clarifier before proceeding. User may opt into sequential all-data-source mode after the clarifier (yes, all of them) — runs one full inventory pass per DS, never merged, never skipping the clarifier itself.
- HC#2: Read-only. Zero mutating tool calls on the workbook or any calc. No `author-calc`, no calc renames, no deletions. Compute-only.
- HC#3: Locked schema in `skill-expertise/catalog_schema.md` is the per-calc entry authority. Never invent an attribute or reshape entries mid-run.
- HC#4: One-clarifier discipline. Ambiguous asks get exactly one combined clarifier, never chained.
- HC#5: No calc fabrication. Every entry in the inventory MUST correspond to a real calc resolvable via `list-available-fields`. Never invent calcs to fill perceived gaps.
- HC#6: No parameter/set/hierarchy deep resolution. Cite by name only. Thats `calc-writer`s or the users job to resolve.
- HC#7: Every delivery emits `calc_inventory_handoff/1` YAML unprompted with all required fields non-blank. Even the empty inventory verdict.
- HC#8: Read-only V-gate before delivery. Verify (a) every catalog entry has all required fields populated, (b) batched pagination results reconciled into a single deduplicated inventory, (c) reference-graph is internally consistent (nested-calc references resolve to actual calcs in the inventory or are flagged as `external_reference: true`).
- HC#9: Must read live data source state. If `list-available-fields` unavailable, refuse the inventory and route to user for a reconnect. Never inventory from stale cache.
- HC#10: Cataloging-only scope. Bulk-fix asks route by exact slug (calc-linter, calc-optimizer, calc-debugger) one calc at a time. Never absorb bulk actions.
- HC#11: Flag heuristics are read-only references from calc-linter and calc-optimizer catalogs. Never extend or redefine those catalogs mid-run; cite rule IDs directly.
- HC#12: Batched pagination is default for 20+ calcs. Inline progress notes required. Reconciled single delivery at end.

## Tools Used

- `list-workbook-datasources` — Phase 0 (identify target DS; multi-source ambiguity fires HC#1 clarifier).
- `list-available-fields` — Phase 1 (enumerate every calc; verbosity full to capture formula, type, AGG-flag, references). Locked threshold: batch calls in ~10-field groups with inline progress notes whenever the data sources field count exceeds 30. Below 30, single call.
- `resolve-field` — Phase 2 (resolve derivation prefix per calcs actual AGG-flag; never string-match the formula).
- `get-workbook-inventory` — Phase 3 (dashboard references only; it returns worksheet↔datasource associations, not per-field shelf placement).
- `search-workbook-fields` — Phase 3 (shelf placements: returns explicit Rows/Columns/Marks placement per field across worksheets). Optional. If either tool is unavailable, note `usage.unavailable_this_run: true` for the affected sub-field and proceed.
- No file writes. Skill is compute-only; downstream consumers write if desired.

## Catalog Schema (Locked, Per-Calc Entry)

Full schema in `skill-expertise/catalog_schema.md`. Summary of required fields per calc:

- **Identity:** `calc_name`, `calc_type` (row_level / aggregate / lod_fixed / lod_include / lod_exclude / table_calc), `formula`, `return_type`.
- **Reference graph:** `references.fields`, `references.parameters` (cited), `references.sets` (cited), `references.hierarchies` (cited), `references.nested_calcs`.
- **Style/perf/complexity flags:** `style_violations` (list of S-* rule IDs from calc-linters catalog, with severity), `perf_advisory_flags` (list of PA-* flags from calc-optimizers catalog), `complexity` (`line_count`, `branch_depth`, `nested_lod_depth`).
- **Usage:** `usage.shelf_placements` (count, from `search-workbook-fields`), `usage.dashboards` (list of dashboard names, from `get-workbook-inventory`), `usage.flag` (`unused` / `low_usage` / `in_use`).

Every catalog entry has all required fields populated. Missing values sentinel to `null`, `[]`, or `unavailable_this_run` per HC#8. Never blank.

## Phase Sequence

- **Phase 0.** Identify target data source. Multi-source ambiguity fires HC#1 clarifier.
- **Phase 1.** Enumerate every calc via `list-available-fields` (verbosity: full). Batch in ~10-field groups with inline progress notes. Record name, formula, type, AGG-flag, and raw reference list per calc.
- **Phase 2.** Resolve derivation prefix per calc via `resolve-field`. Classify `calc_type` and `return_type`. Build the reference graph across the whole inventory (nested-calc references, parameters, sets, hierarchies).
- **Phase 3.** Fetch dashboard references via `get-workbook-inventory` and shelf-placement counts via `search-workbook-fields`. Derive `usage.flag` from both. If either tool is unavailable, mark `usage.unavailable_this_run: true` and proceed.
- **Phase 4.** Apply flag heuristics: run each calc through `skill-expertise/style_catalog.md` and `skill-expertise/performance_hierarchy.md` (read-only reference; never extend). Record `style_violations` and `perf_advisory_flags` per calc.
- **Phase 5.** Compute `complexity` per calc (line count, branch depth, nested LOD depth) from the formula text.
- **Phase 6.** Reconcile batched results into a single deduplicated inventory. Run the 3-check V-gate (all fields populated, batches reconciled, reference-graph consistent).
- **Phase 7.** Render markdown table (scannable). Emit `calc_inventory_handoff/1` YAML unprompted.
- **Phase 8.** No cleanup needed (read-only; no scratch state).

## Validation Gate (Read-Only, 3 Checks)

Full spec in `skill-expertise/validation_gate.md`. Every inventory passes:

- **V1 (Entry completeness):** every catalog entry has all required schema fields populated (or sentinel values per HC#8). No blanks. No fabricated fields.
- **V2 (Batch reconciliation):** batched pagination results reconciled into a single inventory with zero duplicates and zero omissions. Verified by cross-checking total count against `list-available-fields`s reported count.
- **V3 (Reference-graph consistency):** every nested-calc reference in the inventory resolves to another entry in the inventory OR is flagged as `external_reference: true` with rationale. No dangling references. No cycles undetected (report cycles as `notes` on the affected calcs).

Any V-gate failure blocks delivery per HC#8. Fail-open is NOT applied here — since the skill is read-only, a V-gate failure means the inventory itself is incomplete or inconsistent, not a mutation risk. Refuse delivery and diagnose.

## Verification Derivation-Prefix Rule

Resolve derivation prefixes from each calcs actual AGG-flag via `list-available-fields`/`resolve-field`, not by string-matching the formula. Preserves the runtime-lookup discipline confirmed across the calc-family portfolio.

## Domain-Accuracy Assertions (Locked)

- Calc dependency graphs can have cycles (Calc A → Calc B → Calc A). Detect and report; do not attempt to break.
- A calcs `isAggregated` flag is authoritative for AGG classification; the formulas leading token is not. A `{FIXED ...}` LOD is AGG-flagged true even though the formula starts with `{`.
- A calc with zero downstream calc references AND zero shelf placements is unused — but not necessarily deletable; users may reference it via parameters or from other data sources.
- Parameters, sets, and hierarchies are cited by name, not resolved. calc-inventory does not follow references into those object types.
- Batched pagination MUST preserve calc identity across batches. Deduplicate on `calc_name` within a single data source (calc names are unique within a data source per Tableaus own model).

## Scale-Tier Branching

| Calc count | Handling |
|---|---|
| 0 | Empty inventory verdict, handoff with `total_count: 0`. |
| 1-19 | Single-pass enumeration. No batching. |
| 20-99 | Batched pagination in groups of ~20 with inline progress notes. |
| 100+ | Batched pagination + secondary batching of `list-available-fields` calls in ~10-field groups. Inline progress notes on both levels. Handoff `notes` documents both batching methods. |

## Bulk-Action Refusal Discipline (Locked)

calc-inventory catalogs; it does not act. Every bulk-action ask routes to the appropriate peer one calc at a time:

- Bulk-fix all style violations → calc-linter, one calc at a time (with HC#1 sequential-mode opt-in on the linter side).
- Bulk-optimize all tier-5 perf calcs → calc-optimizer, one calc at a time.
- Bulk-debug all NULL-returning calcs → calc-debugger, one calc at a time.
- Delete all unused calcs → refuse. No calc-delete tool exists on this platform; deletion is a manual Desktop step. Note in handoff.
- Rewrite every long-named calc → calc-linter with HC#12 overwrite-discipline gating per calc; never a single bulk pass.

## Report Structure (Locked)

Every inventory delivery renders this exact structure, even for empty inventory verdicts:

- **Summary:** N calcs cataloged, X unused, Y with style violations, Z with perf-advisory flags. Or Empty inventory — no calcs in this data source.
- **Markdown table:** one row per calc. Columns: `Name`, `Type`, `Formula (truncated)`, `References`, `Flags`, `Usage`. Wide tables paginate with clear break points.
- **Unused-calc list** (if any): explicit list of calcs with `usage.flag: unused`. Cleanup candidates.
- **Cycle report** (if any): any nested-calc cycles detected. Not automatically resolved (calc-inventory does not act).
- **`calc_inventory_handoff/1` YAML** with full structured data for downstream consumption.

## Handoff Contract

Emits `calc_inventory_handoff/1` unprompted after every delivery, including empty inventory verdicts. Full schema in `skill-expertise/handoff_schema.md`. Required non-blank fields:

- `schema_version`, `datasource_name`, `total_count`, `calcs` (list of catalog entries; may be empty for empty-inventory verdicts)
- `unused_calcs` (list of calc names; may be empty)
- `cycle_report` (list of detected cycles; may be empty)
- `batching_method` (`single_pass` / `paginated_20` / `paginated_20_plus_field_batching`)
- `usage_metadata_available` (true/false; based on `get-workbook-inventory` availability this run)

## Refuse to Fabricate

Never invent a calc entry. Never invent a rule ID outside calc-linters or calc-optimizers locked catalogs. Never estimate usage without live `get-workbook-inventory` data. Never act on calcs (no author, no edit, no delete). Never mark a calc as unused without confirming zero shelf placements AND zero downstream calc references.

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
