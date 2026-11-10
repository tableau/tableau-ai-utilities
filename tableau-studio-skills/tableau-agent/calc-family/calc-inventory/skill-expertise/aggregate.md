# Aggregate Functions (Locked)

Aggregations at query time. R-AGG-01 requires every row-level field inside an aggregate context to be wrapped. R-AGG-02 prefers MIN/MAX over ATTR.

## Basic Aggregates

| Function | Signature | Return | Notes |
|---|---|---|---|
| SUM | `SUM(expression)` | Number | Sums non-NULL values. |
| AVG | `AVG(expression)` | Number | Ignores NULL. |
| MEDIAN | `MEDIAN(expression)` | Number | Middle value. |
| COUNT | `COUNT(expression)` | Integer | Counts non-NULL values. |
| COUNTD | `COUNTD(expression)` | Integer | Distinct non-NULL count. |
| MIN | `MIN(expression)` | Any | Aggregate MIN. |
| MAX | `MAX(expression)` | Any | Aggregate MAX. |
| ATTR | `ATTR(expression)` | Any | Same value across group, else NULL. See R-AGG-02. |

## Statistical Aggregates

| Function | Signature | Return | Notes |
|---|---|---|---|
| STDEV | `STDEV(expression)` | Number | Sample standard deviation. |
| STDEVP | `STDEVP(expression)` | Number | Population standard deviation. |
| VAR | `VAR(expression)` | Number | Sample variance. |
| VARP | `VARP(expression)` | Number | Population variance. |
| PERCENTILE | `PERCENTILE(expression, decimal)` | Number | Nth percentile (0.0 to 1.0). |
| CORR | `CORR(x, y)` | Number | Pearson correlation. |
| COVAR | `COVAR(x, y)` | Number | Sample covariance. |
| COVARP | `COVARP(x, y)` | Number | Population covariance. |

## Booleans in Aggregate Context

Aggregating a Boolean: SUM converts TRUE to 1, FALSE to 0 (implicit numeric cast). Common pattern: `SUM(IF [Sales] > 500 THEN 1 ELSE 0 END)` counts orders above $500.

## R-AGG-01 Wrapping Discipline

Every row-level field inside an aggregate context needs an aggregation wrapper:

Wrong: `IF SUM([Sales]) > 100 THEN [Sales] END`
Right: `IF SUM([Sales]) > 100 THEN SUM([Sales]) END`

Wrong: `SUM([Sales]) / [Rows]` where [Rows] is row-level
Right: `SUM([Sales]) / SUM([Rows])`

## R-AGG-02 ATTR-vs-MIN/MAX Discipline

ATTR returns the value only if it's the same across all rows in the group; else NULL. This creates two documented failure modes:

- `NOT ATTR([BoolField])` fails when values are mixed (ATTR returns NULL, NOT NULL = NULL, not TRUE).
- `ISNULL(ATTR([DimField]))` is TRUE both when the field is genuinely NULL and when values are mixed.

Prefer MIN or MAX when a stable-scalar assumption holds. Both return a single value from the group regardless of uniformity, avoiding the NULL trap.

## Common Anti-Patterns

- Bare row-level fields in aggregate contexts (R-AGG-01 violation).
- ATTR-based Booleans (R-AGG-02 violation).
- SUM on a nullable field without ZN wrapping when zero is the intended fallback.
- COUNTD on a very high-cardinality field (perf concern, R-PERF-01).

## Version Notes

All aggregate functions available Desktop 2020.1+.
