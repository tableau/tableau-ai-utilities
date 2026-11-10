# Handoff Schema — `calc_optimize_handoff/1` (Locked)

Every successful `calc-optimizer` invocation emits this schema, including "already optimal" verdicts. Downstream calc-family peers consume it. Schema is versioned; unknown versions refused by downstream.

## Full Schema

```yaml
schema_version: calc_optimize_handoff/1
datasource_name: {name}
original_calc_name: {name}
original_formula: {formula_text}
optimized_calc_name: {name}
optimized_formula: {formula_text}
optimization_tier_movement:
  from: {1 | 2 | 3 | 4 | 5}
  to: {1 | 2 | 3 | 4 | 5 | none}
  # "none" only when from == to (already optimal)
calc_type: {row_level | aggregate | lod_fixed | lod_include | lod_exclude | table_calc}
return_type: {number | string | date | datetime | boolean | spatial}
references:
  fields: [{field_name}, ...]
  parameters: [{param_name} (cited, not resolved), ...]
  sets: [{set_name} (cited, not resolved), ...]
  nested_calcs: [{calc_name}, ...]
trade_offs:
  readability: {short_string | "None surfaced"}
  maintainability: {short_string | "None surfaced"}
  grain_sensitivity: {short_string | "None surfaced"}
  downstream_impact: {short_string | "None surfaced"}
verified_equivalent: {true | false}
equivalence_sample_size: {N | "below_threshold" | "verification_skipped"}
integrity_gate_passed: {true | false}
perf_advisory:
  flags: [{PA-flag-id}, ...]
  severity: {none | note | warning}
  recommendation: {optional_free_text}
overwrites_original: {true | false}
already_optimal: {true | false}
notes: {optional_free_text}
```

## Field-by-Field

- **schema_version:** always exactly `calc_optimize_handoff/1`.
- **datasource_name:** the data source the optimized calc was authored on.
- **original_calc_name / original_formula:** captured from the workbook (or from consumed `calc_debug_handoff/1`).
- **optimized_calc_name:** default `[original name] Fast`; may equal `original_calc_name` if `overwrites_original: true`.
- **optimized_formula:** the rewrite. **Equals `original_formula` when `already_optimal: true`.**
- **optimization_tier_movement:** captures the tier drop. `{from: 4, to: 2}` for typical optimizations. `{from: 2, to: 2}` with `already_optimal: true` for "already optimal" verdicts. **Never invent tiers 0 or 6.**
- **calc_type, return_type, references:** same as calc-writer/debugger. Must match the original's type and return_type per R-TYPE-01/02.
- **trade_offs:** **Every subsection has a body.** "None surfaced" is valid; blank/missing is not. HC#11 enforced.
- **verified_equivalent:** `true` if R-EQUIV-01 passed. `false` if double failure and fail-open engaged.
- **equivalence_sample_size:** row count sampled during R-EQUIV-01, or `"verification_skipped"` on fail-open.
- **integrity_gate_passed:** `true` if all 8 V-gate checks + R-EQUIV-01 passed.
- **perf_advisory:** advisory-only. Same catalog as calc-writer/debugger plus tier-5-specific flags (PA-COUNTD-HIGH-CARDINALITY, PA-REGEXP-IN-AGGREGATE, PA-LOD-NESTED-DEPTH-2, etc.).
- **overwrites_original:** `true` only if user opted in per HC#12. Never silent overwrite.
- **already_optimal:** `true` when no rewrite would meaningfully improve tier. `optimized_formula` still equals `original_formula`.
- **notes:** optional. Common uses: R-LOD-03 filter-order acknowledgment; R-TC-01 partitioning intent; equivalence caveat; unused-calc deletion suggestion; fail-open verification warning.

## Downstream Consumer Expectations

- **`calc-linter`** consumes when user says "now lint it": reads `optimized_formula`, `calc_type`, `optimized_calc_name`; produces `calc_lint_handoff/1`.
- **`calc-inventory`** consumes when user says "include this in the catalog": reads all fields.
- **`calc-writer`** does NOT consume this schema (starts fresh from natural-language ask).
- **`calc-debugger`** does NOT consume this schema (starts from a broken calc, not an optimized one).
- **`workbook-auditor`** may consume `perf_advisory.flags` for dashboard-level rollup.

## "Already Optimal" Verdict Contract

When `already_optimal: true`:
- `optimized_formula == original_formula`.
- `optimization_tier_movement.to == optimization_tier_movement.from`.
- `verified_equivalent: true` (trivially, since formulas are identical).
- `trade_offs` still renders with all four subsections. Typically all "None surfaced."
- `notes` should explain why (e.g., "Calc is a bare aggregated ratio at tier 2; no meaningful rewrite would drop it to tier 1 while preserving equivalence.").

## Refuse to Guess

If any required field can't be populated, populate the appropriate sentinel value and note in `notes`. Never leave a required field blank. Never fabricate a tier movement.
