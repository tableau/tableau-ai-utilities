# Validation Gate (Locked, 8 Checks)

Every authored calc passes all 8 checks before delivery. Any failure blocks the write per HC#3.

## The 8 Rules

### R-TYPE-01 — Calc-type classification

**Check:** the authored calc's type matches the intent:
- Row-level: no aggregation wrapper, references only row-level fields or nested row-level calcs.
- Aggregate: exactly one aggregation wrapper at the outer level (SUM, AVG, COUNT, COUNTD, MIN, MAX, ATTR).
- LOD FIXED: `{FIXED [dim] : agg(...)}` with valid syntax.
- LOD INCLUDE: `{INCLUDE [dim] : agg(...)}` with valid syntax.
- LOD EXCLUDE: `{EXCLUDE [dim] : agg(...)}` with valid syntax.
- Table calc: outer function is one of WINDOW_*, RUNNING_*, PREVIOUS_VALUE, INDEX, RANK, LOOKUP.

**Fail action:** re-classify and re-author once. If second attempt fails, refuse.

### R-TYPE-02 — Return type matches ask

**Check:** if the user asked for a Boolean, the calc returns TRUE/FALSE/NULL. If they asked for a Number, no coercion to String. Return type inferred from formula's outermost operator.

**Fail action:** re-author with correct return type or refuse.

### R-AGG-01 — Aggregation wrapping

**Check:** in aggregate contexts, every row-level field is wrapped in an aggregation. No bare `[Sales]` inside `IF SUM([Sales]) > 100 THEN [Sales] END` (the last `[Sales]` needs `SUM([Sales])` or similar).

**Fail action:** re-author with correct wrapping.

### R-AGG-02 — MIN/MAX preferred over ATTR

**Check:** ATTR only used when the semantics genuinely require "same value across all rows in the group and NULL otherwise." Prefer MIN or MAX when a stable-scalar assumption holds. Reason: NOT ATTR(bool) and ISNULL(ATTR(dim)) failure modes.

**Fail action:** rewrite with MIN/MAX if semantics allow; else leave ATTR and note in handoff.

### R-LOD-01 — LOD syntax validity

**Check:** FIXED/INCLUDE/EXCLUDE syntax valid:
- Opening `{` present.
- Dimensions bracketed correctly: `[Region]`, `[Region], [Segment]`.
- Colon delimiter present between dimensions and aggregation.
- Closing `}` present.
- Aggregation inside is valid (SUM, AVG, COUNT, etc.).

**Fail action:** re-author.

### R-LOD-02 — LOD nesting depth

**Check:** LOD nesting depth ≤ 1 unless explicitly needed. Nested LODs (`{FIXED [A] : SUM({FIXED [B] : SUM([X])})}`) get flagged with rationale in the handoff.

**Fail action:** rewrite as flat LOD if possible; else document nesting rationale.

### R-LOD-03 — LOD filter order-of-operations

**Check:** if the calc will sit alongside dimension filters, the handoff notes acknowledge which stage of Tableau's order-of-operations the LOD executes at (FIXED before dimension filters, INCLUDE/EXCLUDE after). Not blocking; notes-required for correctness.

**Fail action:** add order-of-operations note to handoff `notes` field.

### R-TC-01 — Table-calc partitioning intent

**Check:** table calcs (WINDOW_*, RUNNING_*, PREVIOUS_VALUE, INDEX, RANK, LOOKUP) document their intended partitioning and addressing in the handoff. Default table-calc behavior depends on shelf placement, which downstream skills need to know.

**Fail action:** add partitioning/addressing note to handoff.

### R-TC-02 — Prefer FIXED LOD over table calc

**Check:** table calcs never used where a FIXED LOD would suffice. Rationale: LODs compute earlier in the query pipeline, generally faster.

**Fail action:** rewrite as FIXED LOD if semantics allow; else keep table calc and document why.

### R-NULL-01 — NULL handling explicit

**Check:** numeric aggregates on nullable fields have explicit NULL handling (ZN, IFNULL) or explicit acceptance of NULL propagation documented in the handoff.

**Fail action:** wrap with ZN/IFNULL or document acceptance in handoff.

### R-BOOL-01 — Boolean return semantics

**Check:** Boolean calcs return TRUE/FALSE/NULL, not 1/0/-1. Downstream logic tests should be `IF [BoolCalc] THEN ...` not `IF [BoolCalc] = 1 THEN ...`.

**Fail action:** rewrite to return proper Boolean.

### R-PERF-01 — Row-level string ops in aggregations

**Check:** no CONTAINS, REGEXP_MATCH, or other row-level string operations inside aggregations where a pre-aggregated equivalent exists.

**Fail action:** rewrite or flag as intentional in handoff.

### R-NAME-01 — Calc naming

**Check:** calc name ≤ 20 characters, follows house-style prefix conventions if applicable, no default names ("Calculation1", "Calculation2").

**Fail action:** rename per house-style, re-author with new name.

## Total Checks

**8 rules, 13 sub-checks total.** Every calc passes all applicable checks. Some checks may be N/A (e.g., R-TC-01 for a row-level calc); N/A does not count as failure but must be explicitly noted.

## Gate Execution Order

1. R-TYPE-01, R-TYPE-02 first (classification and return type).
2. R-AGG-01, R-AGG-02 next (aggregation correctness).
3. R-LOD-01, R-LOD-02, R-LOD-03 if LOD.
4. R-TC-01, R-TC-02 if table calc.
5. R-NULL-01, R-BOOL-01 for return-type semantics.
6. R-PERF-01 for performance.
7. R-NAME-01 last (naming).

## Refuse to Fabricate

If a check can't be evaluated (e.g., R-TC-01 requires the user to state partitioning intent but they didn't), refuse the write and ask the clarifier. Never guess.
