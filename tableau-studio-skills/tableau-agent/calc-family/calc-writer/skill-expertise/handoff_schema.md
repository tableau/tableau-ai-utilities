# Handoff Schema — `calc_write_handoff/1` (Locked)

`calc-writer` emits this schema only when the user chains to another installed calc skill or asks for it (HC#7). Downstream calc-family peers consume it. Schema is versioned; unknown versions refused by downstream.

## Full Schema

```yaml
schema_version: calc_write_handoff/1
datasource_name: {name}
calc_name: {name}
formula: {formula_text}
calc_type: {row_level | aggregate | lod_fixed | lod_include | lod_exclude | table_calc}
return_type: {number | string | date | datetime | boolean | spatial}
references:
  fields: [{field_name}, ...]
  parameters: [{param_name} (cited, not resolved), ...]
  sets: [{set_name} (cited, not resolved), ...]
  nested_calcs: [{calc_name}, ...]
verified: {true | false}
sample_size: {N | "below_threshold" | "verification_skipped"}
integrity_gate_passed: {true | false}
perf_advisory:
  flags: [{flag_id}, ...]
  severity: {none | note | warning}
  recommendation: {optional_free_text}
notes: {optional_free_text}
```

## Field-by-Field

- **schema_version:** always exactly `calc_write_handoff/1`. Bump to `/2` if breaking changes.
- **datasource_name:** the data source the calc was authored on.
- **calc_name:** the name assigned to the calc (≤ 20 chars per R-NAME-01).
- **formula:** the full formula text as authored, exactly as `author-calc` returned it.
- **calc_type:** one of six values. Never blank, never inferred at consumption time.
- **return_type:** one of six values.
- **references.fields:** every raw field the formula references. Nested-calc dependencies go in `nested_calcs` instead.
- **references.parameters:** parameter references, cited only (never resolved by calc-writer per HC#6).
- **references.sets:** set references, cited only.
- **references.nested_calcs:** other calculated fields this calc depends on.
- **verified:** `true` if `get-summary-data` returned expected output on a scratch worksheet; `false` if verification failed or was skipped.
- **sample_size:** integer if verified, `"below_threshold"` if <1,000 rows, `"verification_skipped"` if scratch worksheet couldn't be created.
- **integrity_gate_passed:** `true` if all 8 Validation Gate checks passed; `false` blocks delivery (this field will not appear in delivered handoff — failed handoffs are not emitted).
- **perf_advisory:** written at write time, advisory-only. Never blocks delivery. Structured as:
  - `flags`: array of perf-flag IDs matching the perf-advisory catalog (see below).
  - `severity`: `none` (no perf-sensitive patterns detected), `note` (minor pattern worth flagging), or `warning` (calc uses a pattern that commonly benefits from optimizer tuning).
  - `recommendation`: optional free text. When severity is `note` or `warning`, includes the verbatim trigger phrase for calc-optimizer: "trigger `calc-optimizer` with 'optimize this calc'."
- **notes:** optional free-text. Common uses: R-LOD-03 filter-order-of-operations acknowledgment; R-TC-01 partitioning/addressing intent; R-AGG-02 ATTR rationale; sample-size caveat; user-directed customization.

## Perf-Advisory Catalog (Locked)

Written at write time. calc-writer never rewrites the calc for perf; it authors correctly and flags. Optimization is `calc-optimizer`'s job.

| Flag ID | Signature | Severity | Rationale |
|---|---|---|---|
| PA-COUNTD-HIGH-CARDINALITY | `COUNTD([high-cardinality field])` such as Customer ID, Order ID, transaction UUID | warning | COUNTD is expensive on high-cardinality fields; consider LOD-based dedupe or pre-aggregated helper measure. |
| PA-REGEXP-IN-AGGREGATE | `REGEXP_MATCH` / `REGEXP_EXTRACT` / `REGEXP_REPLACE` inside SUM/AVG/COUNT | warning | Row-level regex inside aggregate context runs regex on every row before aggregation. |
| PA-CONTAINS-IN-AGGREGATE | `CONTAINS()` or `STARTSWITH()` / `ENDSWITH()` inside SUM/AVG/COUNT | note | Similar to regex but lighter; still per-row. |
| PA-LOD-NESTED | LOD nested >1 level deep | note | Nested LODs compile to multiple query passes; often flattenable. |
| PA-TABLE-CALC-WHERE-LOD-WOULD-WORK | Table calc that could be a FIXED LOD | warning | LODs compute earlier in the query pipeline (per R-LOD-03 order of operations); generally faster. |
| PA-CROSS-DS-BLEND | Calc references fields from a blended data source | warning | Blending is query-time; performance depends on both sources returning results. |
| PA-DATEDIFF-IN-FILTER | DATEDIFF used in a filter or comparison that runs per-row | note | Consider a pre-computed extract calc if filter fires often. |
| PA-NESTED-IF-DEEP | IF/ELSEIF chain >5 branches | note | Consider CASE for equality-based branching or a lookup helper. |
| PA-STRING-ARITHMETIC | String concatenation or manipulation inside an aggregate | note | Row-level string ops multiply cost by row count. |

Any calc that hits one or more of these gets `severity: warning` if any warning-tier flag fires, else `severity: note`, else `severity: none`. The `recommendation` field is populated with:

```
recommendation: "This calc uses [flag_id]. If performance matters, trigger calc-optimizer with 'optimize this calc' after review."
```

The catalog is extensible.

## Refuse to Fabricate Perf Data

Perf advisory is pattern-detection, not measurement. calc-writer never claims a specific latency or row-count impact for the flag. Quantified impact comes from calc-optimizer, which profiles against actual data.

## Downstream Consumer Expectations

- **`calc-optimizer`** consumes when the user says "now optimize it": reads `formula`, `calc_type`, `return_type`, `references`, and produces its own `calc_optimize_handoff/1`.
- **`calc-linter`** consumes when the user says "now lint it": reads `formula`, `calc_type`, `calc_name`, and produces `calc_lint_handoff/1`.
- **`calc-inventory`** consumes when the user says "now include this in the catalog": reads all fields and appends to the calc catalog.
- **`calc-debugger`** does NOT consume this schema directly; if a user reports the calc-writer's output is broken, `calc-debugger` starts from the workbook state, not from this handoff.

## Refuse to Guess

If any required field can't be populated (e.g., verification was skipped because the data source has parameter-referencing calcs), populate the appropriate sentinel value (`"verification_skipped"`) and note in `notes`. Never leave a required field blank.
