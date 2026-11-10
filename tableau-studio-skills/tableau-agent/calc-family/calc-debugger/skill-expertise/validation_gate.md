# Validation Gate (Locked, 8 Checks)

Every fix passes all 8 checks before delivery. Any failure blocks the fix per HC#3.

Identical to calc-writer's validation gate — every calc-family peer runs the same 8-check gate to preserve portfolio-wide V-gate discipline.

## The 8 Rules

### R-TYPE-01 — Calc-type classification

**Check:** the fixed calc's type matches the intent:
- Row-level: no aggregation wrapper, references only row-level fields or nested row-level calcs.
- Aggregate: exactly one aggregation wrapper at the outer level (SUM, AVG, COUNT, COUNTD, MIN, MAX, ATTR).
- LOD FIXED / INCLUDE / EXCLUDE with valid syntax.
- Table calc: outer function is one of WINDOW_*, RUNNING_*, PREVIOUS_VALUE, INDEX, RANK, LOOKUP.

**Fail action:** re-classify and re-fix once. If second attempt fails, refuse.

### R-TYPE-02 — Return type matches intent

**Check:** if the original was Boolean, the fix returns Boolean. If it was Number, no coercion to String. Return type inferred from formula's outermost operator.

**Fail action:** re-author with correct return type or refuse.

### R-AGG-01 — Aggregation wrapping

**Check:** every row-level field inside an aggregate context is wrapped in an aggregation.

**Fail action:** re-author with correct wrapping (self-healing).

### R-AGG-02 — MIN/MAX preferred over ATTR

**Check:** ATTR only used when semantics genuinely require "same value across all rows in group and NULL otherwise." Prefer MIN or MAX when stable-scalar semantics hold.

**Fail action:** rewrite with MIN/MAX if semantics allow; else document ATTR rationale in handoff.

### R-LOD-01 — LOD syntax validity

**Check:** FIXED/INCLUDE/EXCLUDE syntax valid (opening `{`, bracketed dimensions, colon delimiter, closing `}`, valid aggregation inside).

**Fail action:** re-author.

### R-LOD-02 — LOD nesting depth

**Check:** LOD nesting depth ≤ 1 unless explicitly needed. Nested LODs flagged with rationale.

**Fail action:** rewrite as flat if possible; else document nesting rationale.

### R-LOD-03 — LOD filter order-of-operations

**Check:** if the fix will sit alongside dimension filters, the handoff notes acknowledge which stage of Tableau's order-of-operations the LOD executes at (FIXED before dimension filters, INCLUDE/EXCLUDE after).

**Fail action:** add order-of-operations note to handoff `notes`.

### R-TC-01 — Table-calc partitioning intent

**Check:** table calcs document partitioning and addressing in the handoff notes.

**Fail action:** add partitioning/addressing note to handoff.

### R-TC-02 — Prefer FIXED LOD over table calc

**Check:** table calcs never used where a FIXED LOD would suffice.

**Fail action:** rewrite as FIXED LOD if semantics allow; else document why table calc is preferred.

### R-NULL-01 — NULL handling explicit

**Check:** numeric aggregates on nullable fields have explicit NULL handling (ZN, IFNULL) or explicit acceptance of NULL propagation.

**Fail action:** wrap with ZN/IFNULL or document acceptance in handoff.

### R-BOOL-01 — Boolean return semantics

**Check:** Boolean calcs return TRUE/FALSE/NULL, not 1/0/-1.

**Fail action:** rewrite to return proper Boolean.

### R-PERF-01 — Row-level string ops in aggregations

**Check:** no CONTAINS, REGEXP_MATCH, or other row-level string operations inside aggregations where a pre-aggregated equivalent exists.

**Fail action:** rewrite or flag as intentional in handoff.

### R-NAME-01 — Calc naming

**Check:** fixed calc name ≤ 20 characters. Default: `[original name] Fixed` (may exceed 20 chars — allowed exception if original was long; otherwise abbreviate).

**Fail action:** rename per house-style; re-author with new name.

## Gate Execution Order

1. R-TYPE-01, R-TYPE-02 first (classification and return type).
2. R-AGG-01, R-AGG-02 next (aggregation correctness).
3. R-LOD-01, R-LOD-02, R-LOD-03 if LOD.
4. R-TC-01, R-TC-02 if table calc.
5. R-NULL-01, R-BOOL-01 for return-type semantics.
6. R-PERF-01 for performance.
7. R-NAME-01 last.

## Refuse to Fabricate

If a check can't be evaluated, refuse the fix and ask the clarifier. Never guess.
