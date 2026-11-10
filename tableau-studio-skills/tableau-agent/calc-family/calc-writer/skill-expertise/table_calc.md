# Table Calculations (Locked)

Table calcs execute after Tableau retrieves the query result set, operating on the visible data grid. R-TC-01 requires partitioning/addressing intent in handoff. R-TC-02 prefers FIXED LOD over table calc when semantics allow.

## Window Aggregations

| Function | Signature | Return | Notes |
|---|---|---|---|
| WINDOW_SUM | `WINDOW_SUM(expression, [start], [end])` | Number | Sum across window. |
| WINDOW_AVG | `WINDOW_AVG(expression, [start], [end])` | Number | |
| WINDOW_MEDIAN | `WINDOW_MEDIAN(expression, [start], [end])` | Number | |
| WINDOW_MIN | `WINDOW_MIN(expression, [start], [end])` | Number | |
| WINDOW_MAX | `WINDOW_MAX(expression, [start], [end])` | Number | |
| WINDOW_COUNT | `WINDOW_COUNT(expression, [start], [end])` | Integer | |
| WINDOW_STDEV | `WINDOW_STDEV(expression, [start], [end])` | Number | |
| WINDOW_VAR | `WINDOW_VAR(expression, [start], [end])` | Number | |
| WINDOW_PERCENTILE | `WINDOW_PERCENTILE(expression, percent, [start], [end])` | Number | |

**Window offset syntax:** start and end offsets are relative to current row. Negative = past, positive = future, zero = current.

- `WINDOW_SUM(SUM([Sales]), -89, 0)` sums the current row plus previous 89.
- `WINDOW_AVG(SUM([Sales]), FIRST(), LAST())` averages the entire partition.

## Running Aggregations

| Function | Signature | Return | Notes |
|---|---|---|---|
| RUNNING_SUM | `RUNNING_SUM(expression)` | Number | Cumulative from start of partition. |
| RUNNING_AVG | `RUNNING_AVG(expression)` | Number | |
| RUNNING_MIN | `RUNNING_MIN(expression)` | Number | |
| RUNNING_MAX | `RUNNING_MAX(expression)` | Number | |
| RUNNING_COUNT | `RUNNING_COUNT(expression)` | Integer | |

## Rank

| Function | Signature | Return | Notes |
|---|---|---|---|
| RANK | `RANK(expression, ['asc'|'desc'])` | Number | Ties get same rank, next rank skipped. |
| RANK_DENSE | `RANK_DENSE(expression, ['asc'|'desc'])` | Number | Ties get same rank, no gap. |
| RANK_MODIFIED | `RANK_MODIFIED(expression, ['asc'|'desc'])` | Number | Ties get same rank equal to lowest of tied ranks. |
| RANK_UNIQUE | `RANK_UNIQUE(expression, ['asc'|'desc'])` | Number | Ties broken by physical row order. |
| RANK_PERCENTILE | `RANK_PERCENTILE(expression, ['asc'|'desc'])` | Number | Percentile position. |

## Position

| Function | Signature | Return | Notes |
|---|---|---|---|
| FIRST | `FIRST()` | Integer | Offset to first row in partition (0 for first row). |
| LAST | `LAST()` | Integer | Offset to last row in partition. |
| INDEX | `INDEX()` | Integer | Row number within partition (1-based). |
| SIZE | `SIZE()` | Integer | Number of rows in partition. |
| LOOKUP | `LOOKUP(expression, offset)` | Any | Value at offset from current row. |
| PREVIOUS_VALUE | `PREVIOUS_VALUE(expression)` | Any | Value of the calc for the prior row. |
| TOTAL | `TOTAL(agg_expression)` | Number | Aggregates across the entire partition without windowing. |

## R-TC-01 Partitioning and Addressing

Table calcs need explicit partitioning intent because default behavior depends on shelf placement. Every table-calc authored via calc-writer must document in the handoff notes:

- **Partition:** which dimensions define the group ("compute using" or "partition by").
- **Addressing:** which dimension the window traverses ("along" or "advanced").

**Example note:** "WINDOW_AVG partitioned by Product Category, addressed along Order Date, offset -89 to 0."

## R-TC-02 Prefer FIXED LOD Over Table Calc

If a `{FIXED [dim] : agg}` would produce the same result as a table calc, use the LOD. Reason: LODs compute earlier in the query pipeline, generally faster and independent of view state.

**When to use table calc anyway:**
- Running totals (RUNNING_SUM has no LOD equivalent).
- LOOKUP / PREVIOUS_VALUE for row-relative reference.
- WINDOW aggregations with row-relative offsets (not fixable via LOD).
- Rank calculations.

## Common Patterns

- 90-day rolling average: `WINDOW_AVG(SUM([Sales]), -89, 0)`.
- Cumulative sum: `RUNNING_SUM(SUM([Sales]))`.
- Year-over-year change: `(SUM([Sales]) - LOOKUP(SUM([Sales]), -1)) / LOOKUP(SUM([Sales]), -1)`.
- Rank within category: `RANK(SUM([Sales]))` with partition by Category.
- Percent of total: `SUM([Sales]) / TOTAL(SUM([Sales]))`.

## Common Anti-Patterns

- Table calc for grand total when `TOTAL()` or FIXED LOD works.
- Missing partitioning intent in handoff (R-TC-01 violation).
- Table calc when LOD suffices (R-TC-02 violation).
- Nested table calcs > 2 levels deep (readability and perf concern).

## Version Notes

All table calc functions available Desktop 2020.1+.
