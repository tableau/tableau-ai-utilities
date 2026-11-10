# Handoff Schema — `calc_debug_handoff/1` (Locked)

Every successful `calc-debugger` invocation emits this schema. Downstream calc-family peers consume it. Schema is versioned; unknown versions refused by downstream.

## Full Schema

```yaml
schema_version: calc_debug_handoff/1
datasource_name: {name}
original_calc_name: {name}
original_formula: {formula_text}
fixed_calc_name: {name}
fixed_formula: {formula_text}
error_pattern_id: {E-NULL | E-SYNTAX | E-TYPE | E-AGG | E-LOD | E-FIELD | E-PARAM | E-GRAIN | E-CIRC}
root_cause: {short_string}
fix_approach: {short_string}
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
overwrites_original: {true | false}
notes: {optional_free_text}
```

## Field-by-Field

- **schema_version:** always exactly `calc_debug_handoff/1`.
- **datasource_name:** the data source the fixed calc was authored on.
- **original_calc_name / original_formula:** the broken calc's name and formula, captured from the workbook.
- **fixed_calc_name:** default `[original name] Fixed`; may equal `original_calc_name` if `overwrites_original: true`.
- **fixed_formula:** the corrected formula authored via `author-calc`.
- **error_pattern_id:** one of nine locked values from the error-pattern catalog. Never blank.
- **root_cause:** short string describing what went wrong (e.g., "NULL propagation from ZN-less denominator").
- **fix_approach:** short string describing the fix strategy (e.g., "wrapped denominator with ZN, added divide-by-zero guard").
- **calc_type, return_type, references:** same as calc-writer.
- **verified, sample_size, integrity_gate_passed:** same as calc-writer.
- **perf_advisory:** written at fix time, advisory-only. Same catalog as calc-writer: PA-COUNTD-HIGH-CARDINALITY, PA-REGEXP-IN-AGGREGATE, PA-CONTAINS-IN-AGGREGATE, PA-LOD-NESTED, PA-TABLE-CALC-WHERE-LOD-WOULD-WORK, PA-CROSS-DS-BLEND, PA-DATEDIFF-IN-FILTER, PA-NESTED-IF-DEEP, PA-STRING-ARITHMETIC. Never blocks delivery.
- **overwrites_original:** `true` if user opted in to overwrite the original broken calc; `false` if fix was authored as `[original name] Fixed`.
- **notes:** optional free-text. Common uses: R-LOD-03 filter-order acknowledgment; R-TC-01 partitioning intent; verification caveat; user-directed customization.

## Downstream Consumer Expectations

- **`calc-optimizer`** consumes when user says "now optimize it": reads `fixed_formula`, `calc_type`, `return_type`, `references`; produces `calc_optimize_handoff/1`.
- **`calc-linter`** consumes when user says "now lint it": reads `fixed_formula`, `calc_type`, `fixed_calc_name`; produces `calc_lint_handoff/1`.
- **`calc-inventory`** consumes when user says "include this in the catalog": reads all fields.
- **`calc-writer`** does NOT consume this schema (calc-writer starts fresh from the natural-language ask, not from a fix output).
- **`join-and-relationship-advisor`** does NOT consume this schema directly; if E-GRAIN routes to it, the routing carries only the root_cause + original context, not the full handoff.

## Refuse to Guess

If any required field can't be populated, populate the appropriate sentinel value and note in `notes`. Never leave a required field blank.
