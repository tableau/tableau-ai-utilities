# Catalog Schema (Locked, Per-Calc Entry)

Schema authority for calc-inventory. Every catalog entry has these fields populated (or sentinel values per HC#8). Never invent an attribute. Never omit a required field.

## Full Per-Calc Entry Schema

```yaml
calc_name: {string}
calc_type: {row_level | aggregate | lod_fixed | lod_include | lod_exclude | table_calc}
formula: {formula_text}
return_type: {number | string | date | datetime | boolean | spatial | unknown}
is_aggregated_flag: {true | false}
derivation_prefix: {none | sum | usr}
references:
  fields: [{field_name}, ...]
  parameters: [{param_name} (cited, not resolved), ...]
  sets: [{set_name} (cited, not resolved), ...]
  hierarchies: [{hierarchy_name} (cited, not resolved), ...]
  nested_calcs: [{calc_name}, ...]
  external_references: [{ref_name}, ...]  # references not resolvable in this DS
style_violations:
  - rule_id: {S-NAME-01 | S-NAME-02 | ... | S-FORMAT-03}
    severity: {error | warning | info}
    rationale: {short_string}
perf_advisory_flags:
  - flag_id: {PA-COUNTD-HIGH-CARDINALITY | PA-REGEXP-IN-AGGREGATE | ... | PA-STRING-ARITHMETIC}
    rationale: {short_string}
complexity:
  line_count: {N}
  branch_depth: {N}  # deepest IF/ELSEIF nesting
  nested_lod_depth: {N}  # 0 for non-LOD, 1 for flat, 2+ for nested
usage:
  shelf_placements: {N | "unavailable_this_run"}
  dashboards: [{dashboard_name}, ...]  # or "unavailable_this_run"
  flag: {unused | low_usage | in_use | unavailable_this_run}
notes: {optional_free_text}
```

## Field-by-Field

- **calc_name:** the calc's user-visible name in the data source. Unique within a DS per Tableau's own model.
- **calc_type:** the calc's structural type. `row_level` for bare arithmetic/string/date operations without aggregation wrappers. `aggregate` for SUM/AVG/etc. wrappers. `lod_*` for FIXED/INCLUDE/EXCLUDE. `table_calc` for WINDOW_*/RUNNING_*/RANK/INDEX/LOOKUP/PREVIOUS_VALUE.
- **formula:** the full formula text as stored by Tableau. Never truncated in the YAML (markdown table may truncate for display).
- **return_type:** inferred from the formula's outermost operator. `unknown` if not derivable (rare; usually broken calcs).
- **is_aggregated_flag:** Tableau's own `isAggregated` flag from `list-available-fields`. Authoritative for AGG classification.
- **derivation_prefix:** resolved via `resolve-field`. `usr` for AGG-flagged calcs, `sum` for measure-role non-AGG calcs, `none` for dimension-role calcs. Never string-match the formula.
- **references.fields:** every native field the formula references, in order of first appearance. No deduplication (a field cited twice is listed twice).
- **references.parameters / sets / hierarchies:** cited by name only. HC#6 forbids deeper resolution.
- **references.nested_calcs:** other calcs this calc references. Must resolve to another entry in the inventory OR appear in `external_references`.
- **references.external_references:** references not resolvable in this DS. Rare; usually indicates a broken calc, a cross-DS reference, or a stale reference from a consumed upstream handoff.
- **style_violations:** run from calc-linter's `style_catalog.md` (read-only reference; never redefine). One entry per rule that fired.
- **perf_advisory_flags:** run from calc-optimizer's `performance_hierarchy.md` (read-only reference; never redefine). One entry per flag that fired.
- **complexity.line_count:** count of newline characters + 1 in the formula.
- **complexity.branch_depth:** deepest IF/ELSEIF nesting depth. 0 for calcs with no IF branches. Counts nested IF-inside-IF, not sibling ELSEIFs (a 7-branch ELSEIF chain has branch_depth 1).
- **complexity.nested_lod_depth:** 0 for non-LOD calcs, 1 for a flat LOD, 2+ for nested LODs. Cited in `perf_advisory_flags` as PA-LOD-NESTED-DEPTH-2 when >=2.
- **usage.shelf_placements:** count of worksheets where this calc appears on any shelf or mark encoding (Rows, Columns, Marks, Filters, Detail, etc.). From `search-workbook-fields`. Sentinel `"unavailable_this_run"` if that tool call failed.
- **usage.dashboards:** list of dashboard names that reference this calc (directly or transitively through worksheets). Empty list if unused. From `get-workbook-inventory`. Sentinel `"unavailable_this_run"` if that tool call failed.
- **usage.flag:** derived from shelf_placements and dashboards. `unused` if both are zero/empty. `low_usage` if placed on 1-2 worksheets and 0-1 dashboards. `in_use` otherwise. `unavailable_this_run` if either source tool failed for this entry.
- **notes:** optional. Common uses: cycle detection (`"cycle: A → B → A"`), external-reference rationale, style/perf-advisory caveats.

## "Empty Entry" is Not Valid

Every field above MUST be populated per HC#8. Sentinel values (`null`, `[]`, `"unavailable_this_run"`) are acceptable substitutes; blank is not. A single-blank field blocks V-gate V1.

## Derivation-Prefix Resolution (Locked)

`resolve-field` returns `isAggregated: true` for:
- Bare `SUM(...)`, `AVG(...)`, `COUNT(...)`, `COUNTD(...)`, `MIN(...)`, `MAX(...)`, `ATTR(...)` wrappers.
- Any `{FIXED ...}`, `{INCLUDE ...}`, `{EXCLUDE ...}` LOD (regardless of what's inside the braces).
- Any `WINDOW_*`, `RUNNING_*`, `RANK`, `INDEX`, `LOOKUP`, `PREVIOUS_VALUE` table calc.

`isAggregated: false` for:
- Bare row-level field references and arithmetic.
- Row-level string/date functions on native fields.
- Type-coercion functions (`INT`, `STR`, `FLOAT`, `DATE`) applied to row-level fields.

`derivation_prefix` is `usr` when `isAggregated: true`, else `sum` for measure-role calcs, else `none` for dimension-role calcs. Confirmed across calc-writer/debugger/optimizer/linter behavioral runs 2026-09-04 through 2026-09-06.

## Reference-Graph Rules (Locked)

- Every entry in `references.nested_calcs` MUST resolve to another entry in the inventory OR appear in `references.external_references`.
- Every entry in `references.external_references` MUST have a `notes` block explaining why (e.g., "references a calc from a different DS", "references a deleted calc").
- Cycles (A → B → A) are reported in the top-level `cycle_report`, not silently included in `nested_calcs`. Detection is depth-first traversal from every root calc; termination on revisiting an already-marked node.
- Reference-graph consistency verified by V-gate V3 before delivery.

## Batched-Pagination Reconciliation (Locked)

For 20+ calcs:

- Each batch produces a partial inventory of ~20 calcs.
- After all batches complete, reconcile into a single inventory:
  - Deduplicate on `calc_name` (calc names are unique within a DS per Tableau's own model).
  - Rebuild the reference graph across the full inventory (nested-calc references may span batches).
  - Verify total count matches `list-available-fields`'s reported count.
- V-gate V2 catches reconciliation errors before delivery.

## Refuse to Fabricate

If any required field cannot be populated, use the appropriate sentinel value and note in `notes`. Never leave a field blank. Never invent a calc entry. Never mark a calc "unused" without confirming zero shelf placements AND zero downstream calc references.
