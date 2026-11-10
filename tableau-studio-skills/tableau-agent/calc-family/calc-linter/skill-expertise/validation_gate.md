# Validation Gate (Locked, 8 Checks + R-EQUIV-01)

Every rewrite passes all 8 checks plus R-EQUIV-01 before delivery. Any V-gate failure blocks the rewrite per HC#8; R-EQUIV-01 double failure fails-open with a warning per HC#8.

Identical to calc-writer/debugger/optimizer for the 8 core rules; R-EQUIV-01 is shared with calc-optimizer.

## R-TYPE-01 — Calc-type classification

**Check:** the rewritten calc's type matches the original (row-level, aggregate, LOD FIXED/INCLUDE/EXCLUDE, or table calc).

**Fail action:** reject candidate. Fall back to report-only for that violation.

## R-TYPE-02 — Return type matches original

**Check:** the rewritten formula returns the same type (Number, String, Boolean, Date).

**Fail action:** reject candidate.

## R-AGG-01 — Aggregation wrapping

**Check:** every row-level field inside an aggregate context is wrapped in an aggregation.

**Fail action:** self-heal (re-wrap) or reject candidate.

## R-AGG-02 — MIN/MAX preferred over ATTR

**Check:** ATTR only used when semantics require "same value across all rows in group and NULL otherwise."

**Fail action:** if rewrite would preserve ATTR without both conditions holding, rewrite with MIN/MAX; else document ATTR rationale in handoff.

## R-LOD-01 — LOD syntax validity

**Check:** FIXED/INCLUDE/EXCLUDE syntax valid.

**Fail action:** reject candidate.

## R-LOD-02 — LOD nesting depth

**Check:** LOD nesting depth ≤ 1 unless explicitly needed. Linter never introduces nesting via a rewrite.

**Fail action:** reject candidate if rewrite would deepen nesting.

## R-LOD-03 — LOD filter order-of-operations

**Check:** if the rewrite will sit alongside dimension filters, the handoff notes acknowledge which stage of Tableau's order-of-operations the LOD executes at.

**Fail action:** add order-of-operations note to handoff `notes`.

## R-TC-01 — Table-calc partitioning intent

**Check:** if rewrite is still a table calc, partitioning/addressing documented in handoff notes.

**Fail action:** add partitioning/addressing note to handoff.

## R-TC-02 — Prefer FIXED LOD over table calc

**Check:** linter never converts table calcs to FIXED LODs (that's calc-optimizer's job). If a rewrite candidate does this, reject and route to calc-optimizer.

**Fail action:** reject candidate; note "table-calc-to-LOD rewrite is calc-optimizer's scope, not linter's" in report.

## R-NULL-01 — NULL handling explicit

**Check:** numeric aggregates on nullable fields have explicit NULL handling (ZN, IFNULL) or explicit acceptance of NULL propagation.

**Fail action:** wrap with ZN/IFNULL or document acceptance in handoff.

## R-BOOL-01 — Boolean return semantics

**Check:** Boolean calcs return TRUE/FALSE/NULL, not 1/0/-1.

**Fail action:** rewrite candidate to return proper Boolean.

## R-PERF-01 — Row-level string ops in aggregations

**Check:** no CONTAINS, REGEXP_MATCH, or other row-level string operations inside aggregations where a pre-aggregated equivalent exists.

**Fail action:** flag as info-severity note; route perf rewrites to calc-optimizer. Linter never optimizes.

## R-NAME-01 — Calc naming

**Check:** rewritten calc name follows `[original name] Clean` default. The original name part is ≤20 characters unless the original was longer; the ` Clean` suffix doesn't count.

**Fail action:** rename per house-style; re-author with new name.

## R-EQUIV-01 — Runtime equivalence check

**Check:** rewritten formula returns the same values as the original for every group. Verified via:

1. Author both `[original name]` and `[original name] Clean` on a scratch worksheet.
2. Sample aggregated values by every dimension the original touches.
3. Compare row-by-row. Pass if all values match within Tableau's numeric precision.

**High-cardinality sampling cap:** if the grouping dimension(s) would produce more than ~500 distinct groups, sample the top 200 by row count plus a random 100 from the remainder (total ≤300). Note the sampling method and `equivalence_sample_size` in the handoff.

**Zero-dimension FIXED LOD read gap (preserved from calc-optimizer):** if the rewrite shape is `{ FIXED : SUM(...) }` (no grouping field inside the braces) and `get-summary-data` returns the field silently missing from the result set even though the shelf placement is correct, log as environment/tooling limitation, deliver with an explicit note, and do not count against the double-failure fail-open threshold the same way as a genuine value mismatch.

**Fail action (single failure):** re-author with a different rewrite candidate for that violation; re-verify.

**Fail action (double failure):** per HC#8, fail-open. Mark `verified_equivalent: false, equivalence_sample_size: "verification_skipped"` for that specific rewrite. Deliver the report + unrewritten violation with an explicit warning: "Equivalence could not be verified for this rewrite. Report-only for this violation."

## Value-Semantics Traps (Linter-specific)

Linter must NEVER apply the following "cosmetic" rewrites without R-EQUIV-01:

- **IF-to-CASE conversion.** IF supports comparison operators (`>`, `<`, `<>`); CASE requires exact match. Never do this unless the IF is genuinely equality-only.
- **IF/ELSEIF branch reordering.** Short-circuit evaluation can change results if branches overlap. Never reorder without R-EQUIV-01.
- **AND/OR reordering in boolean expressions.** Short-circuit evaluation of side-effecting sub-expressions changes. Never reorder without R-EQUIV-01.
- **Removing "redundant" ZN or IFNULL wrappers.** They may be documented insurance against upstream data changes. Never strip without user confirmation, even if they appear no-op today.
- **Simplifying `IF X THEN TRUE ELSE FALSE END` to `X`.** Legal only if X is guaranteed non-NULL. NULL propagates differently in the two forms.

## Gate Execution Order

1. R-TYPE-01, R-TYPE-02 first (classification and return type).
2. R-AGG-01, R-AGG-02 next (aggregation correctness).
3. R-LOD-01, R-LOD-02, R-LOD-03 if LOD.
4. R-TC-01, R-TC-02 if table calc.
5. R-NULL-01, R-BOOL-01 for return-type semantics.
6. R-PERF-01 for performance (route out if triggered).
7. R-NAME-01 (naming).
8. R-EQUIV-01 last (runtime verification against original).

## Refuse to Fabricate

If a check can't be evaluated, refuse the rewrite for that violation and deliver report-only. Never guess. Never claim an equivalence pass without running the runtime check (except in fail-open with explicit label).
