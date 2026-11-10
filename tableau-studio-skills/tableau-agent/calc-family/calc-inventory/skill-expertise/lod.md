# LOD Expressions (Locked)

Level of Detail expressions compute at a specific grain independent of the visualization. Three variants: FIXED, INCLUDE, EXCLUDE.

## Syntax

```
{FIXED [dim1], [dim2], ... : agg([measure])}
{INCLUDE [dim1], [dim2], ... : agg([measure])}
{EXCLUDE [dim1], [dim2], ... : agg([measure])}
```

- Braces required: `{` opening, `}` closing.
- Dimensions bracketed: `[Region]`, or multi-dimension `[Region], [Segment]`.
- Colon delimiter between dimensions and aggregation.
- Aggregation inside: SUM, AVG, COUNT, COUNTD, MIN, MAX, MEDIAN, PERCENTILE, STDEV, VAR, ATTR.

## FIXED

Computes at the specified grain regardless of any dimensions in the view. Ignores dimension filters (executes before them in Tableau's order of operations, per R-LOD-03).

**Example:** `{FIXED [Region] : SUM([Sales])}` returns total sales per region, even when Segment is on Rows.

**Use for:** grain-specific totals, deduplication (`{FIXED [Order ID] : SUM([Sales])}` to fix fanning), percent-of-total against a fixed grain.

## INCLUDE

Computes at the view's grain PLUS the specified dimensions. Executes after dimension filters.

**Example:** `{INCLUDE [Customer] : AVG([Sales])}` computes average sales per customer, aggregated up to whatever's in the view.

**Use for:** "average of averages" style computations where you want a finer grain than the view.

## EXCLUDE

Computes at the view's grain MINUS the specified dimensions. Executes after dimension filters.

**Example:** `{EXCLUDE [Segment] : SUM([Sales])}` in a view with Segment on Rows returns total sales collapsed across Segment.

**Use for:** percent-of-total calculations, cross-dimension comparisons where you want to strip out one dimension.

## R-LOD-01 Syntax Validity

Every check must pass:
- Opening `{` present.
- Dimensions bracketed correctly.
- Colon delimiter present.
- Closing `}` present.
- Aggregation inside is a valid aggregate function.

## R-LOD-02 Nesting Depth

Nesting LOD > 1 level is allowed but must be flagged with rationale in the handoff.

**Example nested:** `{FIXED [Region] : SUM({FIXED [Segment] : SUM([Sales])})}` computes total-of-totals; rare but valid.

If nesting can be flattened, flatten. If not, document why.

## R-LOD-03 Filter Order of Operations

Tableau's order of operations:
1. Extract filters
2. Data source filters
3. Context filters
4. FIXED LODs
5. Dimension filters
6. INCLUDE / EXCLUDE LODs
7. Measure filters
8. Table calc filters

**Implication:** FIXED LODs are computed BEFORE dimension filters. If a user applies a filter on Region and the calc uses `{FIXED [Region] : SUM([Sales])}`, the LOD returns unfiltered totals per region, not the filtered subset.

To make a FIXED LOD respect a filter, promote the filter to a context filter.

## Common Patterns

- Fanning fix (many-to-many join): `{FIXED [Order ID] : SUM([Sales])}` deduplicates.
- Percent of total by category: `SUM([Sales]) / SUM({FIXED : SUM([Sales])})` (empty FIXED = grand total).
- First order date per customer: `{FIXED [Customer ID] : MIN([Order Date])}`.
- Cohort analysis: `{FIXED [Customer ID] : MIN(YEAR([Order Date]))}`.
- Difference from customer average: `SUM([Sales]) - {INCLUDE [Customer] : AVG([Sales])}`.

## Common Anti-Patterns

- FIXED where INCLUDE/EXCLUDE would suffice (filter-order confusion).
- Missing dimension list: `{FIXED : SUM([Sales])}` is legal (grand total) but easy to mistype.
- LOD nested inside a row-level context where a plain aggregation works.
- Applying LOD result in an aggregate context without wrapping (LOD returns pre-aggregated values but still needs an outer aggregation in visualization).

## Version Notes

LOD expressions available Desktop 9.0+ (all supported versions).
