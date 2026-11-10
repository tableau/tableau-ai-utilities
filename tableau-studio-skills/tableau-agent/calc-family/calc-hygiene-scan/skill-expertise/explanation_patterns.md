# Explanation Patterns (Locked)

Every "why is this structured this way" explanation cites a named pattern from this catalog. No invented pattern names.

## The 12 Patterns

Each pattern captures a common technical rationale for a specific calc structure. When the target calc matches a pattern's signature, cite the pattern name in Dimension 2 of the explanation.

### 1. agg-first-then-divide

**Trigger.** Calc computes a ratio using `SUM([A]) / SUM([B])` (or COUNT variants). Not `AVG([A]/[B])`.
**Rationale.** Avoids the average-of-averages pitfall. Summing numerator and denominator separately preserves portfolio-level correctness. The AVG-of-ratios equivalent would distort weighted totals.
**Example call-out.** "SUM-of-ratios avoids the average-of-averages pitfall."

### 2. attr-for-partition-check

**Trigger.** Calc uses `ATTR([dim])` to test whether a dimension has a single value in the current partition.
**Rationale.** ATTR returns the value if all rows in the partition agree, or `*` if they disagree. Useful for filter cards and conditional formatting that depend on partition uniqueness.
**Example call-out.** "ATTR returns the shared value when the partition is homogeneous; otherwise it returns `*`."

### 3. lod-fixed-for-cross-context

**Trigger.** Calc uses `{FIXED [dim]: ...}` to preserve a computation grain independent of the shelf context.
**Rationale.** FIXED locks the aggregation grain to the named dimensions regardless of what else is on the sheet. Useful for percent-of-total-per-region calcs, cohort baselines, or any comparison that must survive shelf changes.
**Example call-out.** "FIXED locks the grain to {dim} regardless of shelf context."

### 4. lod-include-to-broaden

**Trigger.** Calc uses `{INCLUDE [dim]: ...}` to compute at a finer grain than the shelf, then aggregate up.
**Rationale.** INCLUDE forces a finer aggregation than the shelf currently shows, then rolls up. Useful for average-order-value-by-customer computed at the customer grain and averaged at the segment shelf.
**Example call-out.** "INCLUDE forces the computation at {dim}-grain, then rolls up to the shelf grain."

### 5. lod-exclude-to-collapse

**Trigger.** Calc uses `{EXCLUDE [dim]: ...}` to compute ignoring one shelf dimension.
**Rationale.** EXCLUDE removes named dimensions from the aggregation grain. Useful for showing per-cell contribution against a broader total.
**Example call-out.** "EXCLUDE removes {dim} from the aggregation grain."

### 6. table-calc-partition-context

**Trigger.** Calc uses WINDOW_SUM, RUNNING_SUM, RANK, INDEX, FIRST, LAST, SIZE, LOOKUP, or SCRIPT_* function.
**Rationale.** Table calcs compute across a partition defined on the worksheet, not in the calc XML. Behavior depends on the addressing configured on the shelf.
**Example call-out.** "Table calc behavior depends on the worksheet's partition and addressing, not the formula itself."

### 7. iif-for-branchless

**Trigger.** Calc uses `IIF([test], [true], [false])` instead of IF/THEN/ELSE.
**Rationale.** IIF evaluates both branches always. Faster than IF for simple two-branch logic; slower than IF when the false branch is expensive.
**Example call-out.** "IIF evaluates both branches; simpler than IF for two-branch logic but always computes the false branch."

### 8. case-for-lookup-table

**Trigger.** Calc uses `CASE [field] WHEN ... THEN ... END` structure for mapping.
**Rationale.** CASE-WHEN reads as a lookup table when there are 3+ discrete branches. More readable than nested IIFs.
**Example call-out.** "CASE-WHEN reads as a lookup table for {N}+ discrete branches."

### 9. isnull-for-null-guard

**Trigger.** Calc uses `ISNULL()` or `IFNULL()` to handle NULL propagation.
**Rationale.** NULL propagates through arithmetic in Tableau. Guarding with ISNULL prevents blank rows or unintended aggregation drops.
**Example call-out.** "ISNULL guards against NULL propagation through arithmetic."

### 10. string-boolean-in-two-branches

**Trigger.** Row-level IF/CASE with branches returning exactly two distinct string literals.
**Rationale.** Anti-pattern per Tableau performance guidance; should be a Boolean. Included here for explanation completeness only. Skill flags the pattern but does not recommend a rewrite (calc-optimizer's job).
**Example call-out.** "Two-string-literal branches; typical calc-linter flag as string-Boolean anti-pattern."

### 11. row-level-parameter-lever

**Trigger.** Calc uses `[Parameters].[X]` at row level (no aggregate wrapping).
**Rationale.** Row-level parameter reference is a very cheap lever. Adjusts calc behavior via user-facing parameter without duplicating the calc.
**Example call-out.** "Row-level parameter reference is a cheap runtime lever."

### 12. running-baseline

**Trigger.** Calc uses `RUNNING_SUM(SUM([X]))` or similar cumulative pattern.
**Rationale.** Running totals build a cumulative baseline over a partition. Table-calc semantics apply.
**Example call-out.** "Running total pattern; cumulative across partition."

## Pattern Precedence

If multiple patterns match, cite the outermost structural pattern first, then the inner detail. Example: `SUM([Profit]) / {FIXED [Region]: SUM([Sales])}` cites lod-fixed-for-cross-context (outer FIXED) then agg-first-then-divide (inner ratio).

## Refuse to Fabricate

If no pattern from this catalog matches the target calc's structure, Dimension 2 renders: "Non-canonical structure; no pattern from `explanation_patterns.md` matched. Formula reads as straightforward arithmetic with no distinctive Tableau idiom." Do not invent a pattern name.

## Extension Rule

Adding a new pattern requires:

1. A trigger condition (formula shape) precise enough for consistent classification.
2. A rationale grounded in Tableau-native mechanics (not personal opinion).
3. A one-sentence example call-out for use in Dimension 2 rendering.

Patterns are locked once released. Renaming or removing a pattern is a breaking change to `calc_explanation/1` handoff schema.
