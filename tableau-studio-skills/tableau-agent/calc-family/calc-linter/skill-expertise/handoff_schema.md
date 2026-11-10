# Handoff Schema — `calc_lint_handoff/1` (Locked)

Every successful `calc-linter` invocation emits this schema, including "clean" verdicts and report-only deliveries. Downstream calc-family peers consume it. Schema is versioned; unknown versions refused by downstream.

## Full Schema

```yaml
schema_version: calc_lint_handoff/1
datasource_name: {name}
original_calc_name: {name}
original_formula: {formula_text}
violations:
  - rule_id: {S-NAME-01 | S-NAME-02 | S-NAME-03 | S-STRUCT-01 | S-STRUCT-02 | S-STRUCT-03 | S-STRUCT-04 | S-COMMENT-01 | S-COMMENT-02 | S-FORMAT-01 | S-FORMAT-02 | S-FORMAT-03}
    severity: {error | warning | info}
    rationale: {short_string}
    snippet: {relevant_formula_or_name_text}
    rewrite_suggested: {formula_or_name_string | null}
    rewrite_applied: {true | false}
    rewrite_verified_equivalent: {true | false | not_applicable}
    notes: {optional_free_text}
rewritten: {true | false}
rewritten_calc_name: {name | null}
rewritten_formula: {formula_text | null}
calc_type: {row_level | aggregate | lod_fixed | lod_include | lod_exclude | table_calc}
return_type: {number | string | date | datetime | boolean | spatial}
references:
  fields: [{field_name}, ...]
  parameters: [{param_name} (cited, not resolved), ...]
  sets: [{set_name} (cited, not resolved), ...]
  nested_calcs: [{calc_name}, ...]
verified_equivalent: {true | false | not_applicable}
equivalence_sample_size: {N | "below_threshold" | "verification_skipped" | "not_applicable"}
integrity_gate_passed: {true | false | not_applicable}
overwrites_original: {true | false}
clean_verdict: {true | false}
notes: {optional_free_text}
```

## Field-by-Field

- **schema_version:** always exactly `calc_lint_handoff/1`.
- **datasource_name:** the data source the calc lives on.
- **original_calc_name / original_formula:** captured from the workbook (or from a consumed upstream handoff).
- **violations:** list of rule violations found. Empty list `[]` means clean verdict. Each violation has all required sub-fields non-blank (except `rewrite_suggested` which is `null` when not rewritable).
- **rewritten:** `true` only if user opted in AND at least one rewrite was authored + verified. `false` for report-only deliveries and clean verdicts.
- **rewritten_calc_name:** default `[original name] Clean`; may equal `original_calc_name` if `overwrites_original: true`. `null` if `rewritten: false`.
- **rewritten_formula:** the rewrite that consolidates all applied violations. `null` if `rewritten: false`.
- **calc_type, return_type, references:** same as calc-writer/debugger/optimizer.
- **verified_equivalent:** `true` if R-EQUIV-01 passed on the rewrite. `false` if double failure and fail-open engaged. `not_applicable` if `rewritten: false`.
- **equivalence_sample_size:** row count sampled during R-EQUIV-01, or `"verification_skipped"` on fail-open, or `"not_applicable"` if `rewritten: false`.
- **integrity_gate_passed:** `true` if all 8 V-gate checks + R-EQUIV-01 passed. `not_applicable` if `rewritten: false`.
- **overwrites_original:** `true` only if user opted in per HC#12. Never silent overwrite.
- **clean_verdict:** `true` when `violations` is empty. Rewrite fields must all be `null`/`false`/`not_applicable`.
- **notes:** optional. Common uses: R-LOD-03 filter-order acknowledgment; R-TC-01 partitioning intent; equivalence caveat; value-semantics-risk callouts; fail-open verification warning.

## Downstream Consumer Expectations

- **`calc-inventory`** consumes when user says "add this to the catalog": reads all fields, especially the `violations` list for style-scorecard rollup across the data source.
- **`workbook-auditor`** may consume `violations` for dashboard-level style rollup.
- **`calc-writer`, `calc-debugger`, `calc-optimizer`** do NOT consume this schema (each starts from its own inputs).

## "Clean Verdict" Contract

When `clean_verdict: true`:
- `violations: []`.
- `rewritten: false`, `rewritten_calc_name: null`, `rewritten_formula: null`.
- `verified_equivalent: not_applicable`, `equivalence_sample_size: not_applicable`, `integrity_gate_passed: not_applicable`.
- `notes` should explain scope of check (e.g., "12 style rules run against `[Calc Name]`; no violations found.").

## Report-Only Contract

When `rewritten: false` but `violations` is non-empty:
- Every violation renders with `rewrite_applied: false`.
- `rewrite_suggested` may still be populated (advisory only).
- `rewrite_verified_equivalent: not_applicable` on every violation.
- `verified_equivalent: not_applicable` at the top level.

## Rewrite-Delivered Contract

When `rewritten: true`:
- At least one violation has `rewrite_applied: true`.
- Every applied rewrite has `rewrite_verified_equivalent: true` (or `false` with explicit fail-open note in `notes`).
- Top-level `verified_equivalent: true` (or `false` with fail-open explanation).
- `rewritten_formula` is the fully-consolidated form after all applied rewrites.

## Refuse to Guess

If any required field can't be populated, populate the appropriate sentinel (`null`, `false`, `not_applicable`) and note in `notes`. Never leave a required field blank. Never mark a violation `rewrite_applied: true` without a corresponding R-EQUIV-01 pass or a documented fail-open.
