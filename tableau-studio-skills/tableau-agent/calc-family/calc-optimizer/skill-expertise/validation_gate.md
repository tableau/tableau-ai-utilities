# Validation Gate (Locked, 8 Checks + R-EQUIV-01)

Every optimized calc passes all 8 checks plus the optimizer-specific R-EQUIV-01 equivalence check before delivery. Any failure blocks the rewrite per HC#8; R-EQUIV-01 double failure fails-open with a warning per HC#8.

Identical to calc-writer/debugger for the 8 core rules; the equivalence check is unique to calc-optimizer.

## R-TYPE-01 — Calc-type classification

**Check:** the optimized calc's type matches the original:
- Row-level ↔ row-level.
- Aggregate ↔ aggregate.
- LOD FIXED/INCLUDE/EXCLUDE ↔ same LOD family (may switch between FIXED and INCLUDE only if equivalence verification passes).
- Table calc ↔ table calc OR FIXED LOD replacement if R-TC-02 promotes.

**Fail action:** reject candidate. Try next tier down.

## R-TYPE-02 — Return type matches original

**Check:** the optimized formula returns the same type (Number, String, Boolean, Date). Boolean stays Boolean; Number stays Number.

**Fail action:** reject candidate.

## R-AGG-01 — Aggregation wrapping

**Check:** every row-level field inside an aggregate context is wrapped in an aggregation.

**Fail action:** self-heal (re-wrap) or reject candidate.

## R-AGG-02 — MIN/MAX preferred over ATTR

**Check:** ATTR only used when semantics require "same value across all rows in group and NULL otherwise." Optimizer prefers MIN/MAX rewrites for stable-scalar semantics.

**Fail action:** rewrite with MIN/MAX if semantics allow; else document ATTR rationale in handoff.

## R-LOD-01 — LOD syntax validity

**Check:** FIXED/INCLUDE/EXCLUDE syntax valid.

**Fail action:** reject candidate.

## R-LOD-02 — LOD nesting depth

**Check:** LOD nesting depth ≤ 1 unless explicitly needed. Optimizer target: flatten nested LODs wherever semantics allow.

**Fail action:** flatten if possible; else document nesting rationale in handoff and rank as tier 4 or 5.

## R-LOD-03 — LOD filter order-of-operations

**Check:** if the optimized calc will sit alongside dimension filters, the handoff notes acknowledge which stage of Tableau's order-of-operations the LOD executes at (FIXED before dimension filters, INCLUDE/EXCLUDE after).

**Fail action:** add order-of-operations note to handoff `notes`.

## R-TC-01 — Table-calc partitioning intent

**Check:** if optimized calc is still a table calc, partitioning/addressing documented in handoff notes.

**Fail action:** add partitioning/addressing note to handoff.

## R-TC-02 — Prefer FIXED LOD over table calc

**Check:** table calcs never kept where a FIXED LOD would achieve the same semantics.

**Fail action:** rewrite as FIXED LOD; else document why table calc must be preserved.

## R-NULL-01 — NULL handling explicit

**Check:** numeric aggregates on nullable fields have explicit NULL handling (ZN, IFNULL) or explicit acceptance of NULL propagation.

**Fail action:** wrap with ZN/IFNULL or document acceptance in handoff.

## R-BOOL-01 — Boolean return semantics

**Check:** Boolean calcs return TRUE/FALSE/NULL, not 1/0/-1.

**Fail action:** rewrite candidate to return proper Boolean.

## R-PERF-01 — Row-level string ops in aggregations

**Check:** no CONTAINS, REGEXP_MATCH, or other row-level string operations inside aggregations where a pre-aggregated equivalent exists.

**Fail action:** rewrite to remove nested string ops. If unavoidable (semantics require it), rank as tier 4/5 and note in handoff.

## R-NAME-01 — Calc naming

**Check:** optimized calc name follows `[original name] Fast` default. ≤20 characters unless original was longer (allowed exception).

**Fail action:** rename per house-style; re-author.

## R-EQUIV-01 — Runtime equivalence check (Optimizer-specific)

**Check:** optimized formula returns the same values as the original for every group the original produces. Verified via:

1. Author both `[original name]` and `[original name] Fast` on a scratch worksheet.
2. Sample aggregated values by every dimension the original touches (e.g., if original references `[Region]`, group by Region).
3. Compare row-by-row. Pass if all values match within Tableau's numeric precision. Fail if any group produces different values.

**High-cardinality sampling cap:** if the grouping dimension(s) would produce more than ~500 distinct groups, sample the top 200 by row count plus a random 100 from the remainder (total ≤300) rather than pulling every group. Note the sampling method and `equivalence_sample_size` in the handoff so the user knows the check was sampled, not exhaustive. This keeps Phase 6 itself fast on the same high-cardinality data the optimizer is often called in to help with.

**Zero-dimension FIXED LOD read gap (confirmed in testing):** a rewrite of the exact shape `{ FIXED : SUM([field]) }` — no grouping field inside the braces, used for a grand-total-style rewrite of a partitionless table calc like `WINDOW_SUM(SUM([field]))` — can be correctly placed on a worksheet shelf (confirmed via the worksheet's own XML) but fails to return any value through the data-read tooling used for R-EQUIV-01, even when queried by its exact field name. This blocks equivalence verification for this specific rewrite shape, independent of whether the rewrite is actually correct. If this pattern is generated as a candidate and the equivalence read comes back with the field silently missing from the result set (not merely a null value), do not treat this as a R-EQUIV-01 failure of the *formula* — log it as an environment/tooling limitation, deliver with an explicit note that equivalence could not be technically verified for this reason, and do not count it against the double-failure fail-open threshold in the same way as a genuine value mismatch.

**Fail action (single failure):** re-author with a lower-tier candidate; re-verify.

**Fail action (double failure):** per HC#8, fail-open. Mark `verified_equivalent: false, equivalence_sample_size: "verification_skipped"`. Deliver with explicit warning: "Equivalence could not be verified in this session. User is responsible for validating values match before adopting the optimized formula."

## Gate Execution Order

1. R-TYPE-01, R-TYPE-02 first (classification and return type).
2. R-AGG-01, R-AGG-02 next (aggregation correctness).
3. R-LOD-01, R-LOD-02, R-LOD-03 if LOD.
4. R-TC-01, R-TC-02 if table calc.
5. R-NULL-01, R-BOOL-01 for return-type semantics.
6. R-PERF-01 for performance.
7. R-NAME-01 (naming).
8. R-EQUIV-01 last (runtime verification against original).

## Refuse to Fabricate

If a check can't be evaluated, refuse the optimization and ask the clarifier. Never guess. Never claim an equivalence pass without running the runtime check (except in fail-open with explicit label).
