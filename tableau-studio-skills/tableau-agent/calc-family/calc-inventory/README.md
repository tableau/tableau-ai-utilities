# Calc Inventory

Catalogs every calculated field in one Tableau data source per run. Delivers a scannable markdown table plus a machine-readable `calc_inventory_handoff/1` YAML. Read-only. Batched pagination for data sources with 20+ calcs. Records name, type, formula, reference graph, style/perf/complexity flags, and usage metadata per calc.

**Example:** You have a Sample - Superstore workbook with 12 calculated fields. The skill enumerates all 12 via `list-available-fields`, resolves each calc's AGG-flag and derivation prefix, builds the reference graph (which calcs depend on which), applies flag heuristics from calc-linter's style catalog and calc-optimizer's performance hierarchy, fetches shelf placements and dashboard references, and hands you back a markdown table plus a `calc_inventory_handoff/1` YAML. The report surfaces 2 unused calcs as cleanup candidates and 1 cycle in the reference graph.

## What it does

Fires standalone on a data-source-wide inventory ask, or consumes any upstream calc-family handoff (`calc_write_handoff/1` / `calc_debug_handoff/1` / `calc_optimize_handoff/1` / `calc_lint_handoff/1`) for single-calc catalog inclusion. Enumerates via `list-available-fields`, resolves derivation prefixes via `resolve-field`, fetches usage metadata via `get-workbook-inventory`, applies flag heuristics from calc-linter's and calc-optimizer's locked catalogs (read-only reference), computes complexity, reconciles batched pagination results, runs a 3-check read-only V-gate, and emits the handoff.

## When to use it

Fires on "list all calcs in this data source," "inventory the calcs," "catalog my calculated fields," "show me every calc in this workbook," "what calcs exist here," or when an upstream calc-family handoff arrives and the user says "add it to the inventory."

Do NOT invoke for writing new calcs (`calc-writer`), fixing broken/wrong-value calcs (`calc-debugger`), performance rewrites (`calc-optimizer`), style rewrites (`calc-linter`), data-model documentation (`data-model-documenter`), or workbook-level cataloging beyond calcs (`workbook-auditor`).

## What makes this skill distinctive

- **Locked per-calc catalog schema.** Every entry has the same fields populated (or sentinel values per HC#8). Never blank, never fabricated, never invented. Deterministic across runs.
- **Batched pagination for scale.** Data sources with 20+ calcs batch in groups of ~20 with inline progress notes. 100+ calc data sources also batch `list-available-fields` calls in ~10-field groups. Reconciliation V-gate check catches duplicates and omissions.
- **Read-only compute-only.** Zero mutating tool calls. No `author-calc`, no calc renames, no deletions. Compute-only. Downstream consumers write if desired.
- **Bulk-action refusal is a hard constraint.** "Bulk-fix all style violations" → refuses; routes to `calc-linter` one calc at a time. Same for perf (routes to `calc-optimizer`) and correctness (routes to `calc-debugger`). Never absorbs bulk actions.
- **Flag heuristics are read-only references.** Uses calc-linter's `style_catalog.md` and calc-optimizer's `performance_hierarchy.md` as the rule authority. Never redefines or extends those catalogs mid-run; cites rule IDs (S-*, PA-*) directly.
- **Cycle detection is first-class.** Nested-calc cycles (A → B → A) surface in a dedicated `cycle_report` field, not silently included in reference graphs. Never attempts to break cycles.
- **Runtime-resolved derivation prefixes.** Uses each calc's actual AGG-flag via `list-available-fields`/`resolve-field`. Never string-matches the formula. Preserves the runtime-lookup discipline confirmed across the calc-family portfolio.

## Handoff contract

Emits `calc_inventory_handoff/1` unprompted after every delivery, including empty-inventory verdicts. Required non-blank fields: `total_count`, `calcs` (list; may be empty), `unused_calcs` (list; may be empty), `cycle_report` (list; may be empty), `batching_method`, `usage_metadata_available`.

Downstream consumers: `workbook-auditor` (full inventory rollup), `calc-linter` / `calc-optimizer` (single-calc entries for follow-up runs), `data-model-documenter` (calc-count rollup for its dependency-graph section).

## Hard constraints in force

- HC#1: single-data-source-per-run default; multi-source workbooks require clarifier.
- HC#2: read-only; zero mutating tool calls.
- HC#3: locked catalog schema is the per-calc entry authority.
- HC#5: no calc fabrication; every entry corresponds to a real calc.
- HC#7: every delivery emits handoff YAML unprompted.
- HC#8: 3-check read-only V-gate; no fail-open (read-only skill has no mutation risk to defer against).
- HC#10: cataloging-only scope; bulk-fix asks route by exact slug.
- HC#11: flag heuristics are read-only references; never extend or redefine mid-run.
- HC#12: batched pagination is default for 20+ calcs; inline progress notes required.

Full spec in `SKILL.md`. Catalog schema in `skill-expertise/catalog_schema.md`. Validation Gate in `skill-expertise/validation_gate.md`. Handoff schema in `skill-expertise/handoff_schema.md`. Function library in `skill-expertise/` (`INDEX.md` plus one file per function category).
