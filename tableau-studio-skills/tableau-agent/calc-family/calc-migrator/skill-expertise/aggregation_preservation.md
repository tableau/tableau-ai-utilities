# Aggregation Preservation Reference
Locked reference file for calc-migrator's Phase 3 aggregation preservation check. Cited by HC#7. Six aggregation types with locked precedence rules and reclassification decision tree. Every migration classifies the source calc against this reference before proceeding.

## The 6 Aggregation Types

Aggregation classification uses the same precedence order calc-documenter's `aggregation_patterns.md` locks. Matched substrings determine type; matches evaluate in strict order top-to-bottom. First match wins.

| # | Type | Detection substring | Preservation rule on target |
|---|---|---|---|
| 1 | LOD-fixed | `{FIXED` (case-insensitive, whitespace-tolerant) | Every dimension named after `FIXED` and before `:` must exist on the target datasource by exact name. If any missing, refuse and route to calc-optimizer. |
| 2 | LOD-include | `{INCLUDE` at any nesting depth | Every dimension named after `INCLUDE` and before `:` must exist on the target. Same rule as LOD-fixed. |
| 3 | LOD-exclude | `{EXCLUDE` at any nesting depth | Every dimension named after `EXCLUDE` and before `:` must exist on the target. Same rule. |
| 4 | table-calc | `WINDOW_*` / `RUNNING_*` / `RANK*` / `INDEX` / `FIRST` / `LAST` / `SIZE` / `LOOKUP` / `SCRIPT_*` | No dimension check; table-calc addressing is sheet-level, not datasource-level. Aggregation type preserved as-is. |
| 5 | aggregate | `SUM` / `AVG` / `COUNT` / `COUNTD` / `MIN` / `MAX` / `MEDIAN` / `STDEV` / `VAR` / `ATTR` at top level (not nested inside an LOD) | No dimension check. Aggregation type preserved as-is. |
| 6 | row-level | Fallback when no aggregate or LOD keyword fires | No dimension check. Row-level preserved as-is. |

## Precedence Rules

**Rule 1: LOD wins over aggregate.** If a formula contains both an LOD and an aggregate wrapping it (e.g., `SUM({FIXED [Region]: SUM([Sales])})`), classify as LOD-fixed. The outer SUM does not upgrade the classification because the LOD is the structurally dominant expression. Verified empirically in calc-documenter's Nested LOD trap-catching test 2026-09-14.

**Rule 2: Innermost LOD determines dimension requirements.** If a formula nests multiple LODs (e.g., `{FIXED [Region]: SUM({INCLUDE [Segment]: [Sales]})}`), preservation checks apply to every LOD's dimensions. Any missing dimension across any LOD triggers refusal. `[Region]` AND `[Segment]` must both exist on target.

**Rule 3: table-calc + aggregate.** `WINDOW_SUM(SUM([Sales]))` classifies as table-calc (Rule 4). Table-calc always wins over aggregate wrapping.

**Rule 4: Case-insensitivity for keywords.** `{fixed`, `{FIXED`, `{Fixed` all match. Field names inside LODs remain case-sensitive per the `resolve-field` shared-tool concern documented.

## Reclassification Decision Tree

```
Enter: source calc formula
  |
  |-- Does formula contain "{FIXED"?
  |       yes -> LOD-fixed
  |               |-- Enumerate dimensions after FIXED, before :
  |               |-- For each dim, resolve-field on target
  |               |       |-- Any fail -> refuse, route to calc-optimizer
  |               |       |-- All pass -> proceed to Phase 4 consent
  |               no ->
  |
  |-- Does formula contain "{INCLUDE"?
  |       yes -> LOD-include (same dimension check)
  |       no ->
  |
  |-- Does formula contain "{EXCLUDE"?
  |       yes -> LOD-exclude (same dimension check)
  |       no ->
  |
  |-- Does formula contain table-calc keyword (WINDOW_*, RUNNING_*, RANK, INDEX, FIRST, LAST, SIZE, LOOKUP, SCRIPT_*)?
  |       yes -> table-calc
  |               |-- No dimension check; proceed to Phase 4 consent
  |       no ->
  |
  |-- Does formula contain top-level aggregate (SUM, AVG, COUNT, COUNTD, MIN, MAX, MEDIAN, STDEV, VAR, ATTR)?
  |       yes -> aggregate
  |               |-- No dimension check; proceed to Phase 4 consent
  |       no ->
  |
  |-- Fallback: row-level
          |-- No dimension check; proceed to Phase 4 consent
```

## Worked Examples

**Example 1: aggregate preservation, no dimensions**

Source calc: `SUM([Sales])` on Orders
Target datasource: Returns
Classification: aggregate (Rule 4 doesn't fire; Rule 5 does)
Dimension check: not applicable
Preservation: proceeds to Phase 4 consent for `[Sales]` field only.

**Example 2: LOD-fixed with matching dimension**

Source calc: `{FIXED [Region]: SUM([Sales])}` on Orders
Target datasource: Returns (has `[Region]` and `[Sales]`)
Classification: LOD-fixed (Rule 1)
Dimension check: `[Region]` resolves on Returns → pass
Preservation: proceeds to Phase 4 consent for `[Region]` and `[Sales]`.

**Example 3: LOD-fixed with missing dimension (refusal)**

Source calc: `{FIXED [Container]: SUM([Sales])}` on Orders
Target datasource: Returns (no `[Container]` field)
Classification: LOD-fixed (Rule 1)
Dimension check: `[Container]` fails on Returns → refuse
Route: calc-optimizer with rationale ("Target datasource lacks [Container] dimension required by LOD-fixed. Semantic rewrite needed.")
`unresolved_references: ["Container"]` populated.

**Example 4: nested LOD in aggregate (Rule 1 wins)**

Source calc: `SUM([Sales]) / SUM({FIXED [Region]: SUM([Sales])})`
Target datasource: Returns
Classification: LOD-fixed (Rule 1 dominant despite outer SUM/SUM structure)
Dimension check: `[Region]` resolves on Returns → pass
Preservation: proceeds to Phase 4 consent for `[Region]` and `[Sales]`.

**Example 5: table-calc with aggregate wrapping (Rule 3 applies)**

Source calc: `WINDOW_SUM(SUM([Sales]))`
Target datasource: Returns
Classification: table-calc (Rule 3)
Dimension check: not applicable
Preservation: proceeds to Phase 4 consent for `[Sales]` field only. Table-calc addressing is not migrated at the calc level; user handles at sheet level.

**Example 6: nested LODs (Rule 2 applies)**

Source calc: `{FIXED [Region]: SUM({INCLUDE [Segment]: [Sales]})}`
Target datasource: Returns (has `[Region]`, missing `[Segment]`)
Classification: LOD-fixed (outermost LOD dominates)
Dimension check: `[Region]` passes, `[Segment]` fails on Returns → refuse
Route: calc-optimizer
`unresolved_references: ["Segment"]` populated.

**Example 7: row-level with parameter reference**

Source calc: `[Sales] * [Multiplier Parameter]`
Target datasource: Returns
Classification: row-level (Rule 6 fallback)
Dimension check: not applicable
Preservation: proceeds to Phase 4 consent for `[Sales]` and `[Multiplier Parameter]`. Parameter must exist on the target workbook by exact name (parameters are workbook-scope, not datasource-scope). If missing, refuse per HC#4.

## Refusal Templates

**Missing LOD dimension:**

> Cannot migrate `{source_calc}` from `{source_ds}` to `{target_ds}`. Source is LOD-fixed on `[{missing_dim}]`, which does not exist on `{target_ds}`. Route to calc-optimizer for semantic rewrite, or add `[{missing_dim}]` to `{target_ds}` and re-run.

**Missing aggregate field:**

> Cannot migrate `{source_calc}` from `{source_ds}` to `{target_ds}`. Field `[{missing_field}]` does not exist on `{target_ds}`. Route to manual authoring, or add `[{missing_field}]` to `{target_ds}` and re-run.

**Missing parameter:**

> Cannot migrate `{source_calc}` from `{source_ds}` to `{target_ds}`. Parameter `[{missing_param}]` does not exist in this workbook. Parameters are workbook-scope; create the parameter first and re-run.

## Failure Modes This Reference Prevents

- **Silent aggregation swap** (e.g., LOD-fixed → aggregate because outer SUM was seen first). Precedence Rule 1 blocks.
- **Silent dimension loss** (e.g., LOD-fixed migrated without checking target dimensions). Decision tree enforces resolve-field per dimension.
- **Nested LOD misclassification** (e.g., inner LOD ignored). Precedence Rule 2 requires all LOD dimensions verified.
- **Table-calc field-check overhead** (e.g., dimension check runs on table-calc). Rule 3 explicitly skips dimension check for table-calc.
- **Case-sensitivity confusion on LOD keywords** (e.g., `{fixed` treated differently from `{FIXED`). Rule 4 locks case-insensitive keyword matching.
