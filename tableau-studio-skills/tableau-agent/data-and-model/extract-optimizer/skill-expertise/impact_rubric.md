# Impact Quantification Rubric (Locked)

Every recommendation cites a specific quantified impact. Hedging is banned by HC#3.

## Estimation Methods

### D1 Incremental Refresh

- Sample the candidate key: MIN, MAX, and the "recent-N-days" count via `get-summary-data`.
- Estimate `new-rows-per-refresh-interval` from the recent-day sample.
- Impact: refresh-time reduction ≈ `1 - (new-rows / total-rows)`.
- Reporting: "Estimated refresh-time reduction ~72%: 8.3M new rows per day out of 300M total."

### D2 Aggregation

- Identify the intersection dimensions used on every sheet.
- Sample `COUNTD` across those dimensions to estimate post-aggregation row count.
- Impact: row-reduction ≈ `(post-aggregation-count / pre-aggregation-count)`.
- Reporting: "Estimated row reduction ~89%: 300M rows → ~33M rows after aggregating on {Product Category, Region, Order Date}."

### D3 Hidden-Field Pruning

- Count total fields vs. unused fields.
- Impact: file-size reduction ≈ `(unused / total)` percentage.
- Reporting: "Estimated file-size reduction ~38%: 47 of 124 fields never placed on any sheet."
- Caveat: not exact because some fields (strings, high-cardinality dimensions) are wider than others. Reporting includes the caveat.

### D4 Filter-at-Extract

- Sample `get-summary-data` count with and without the candidate filter.
- Impact: row-reduction ≈ `(1 - filtered-count / total-count)`.
- Reporting: "Estimated row reduction ~62%: 187M rows drop to 71M after applying [Order Date] >= 2024-01-01 at extract time."

## What Counts as Quantified

- Any percentage (row reduction, file-size reduction, refresh-time reduction).
- Any absolute count (fields pruned, rows removed).
- Any ratio comparing before and after.

## What Does NOT Count

- "Should improve performance."
- "Likely faster."
- "Could be significant."
- "Depends on your data."

## Sample-Size Caveats

- Estimates for D4 (filter-at-extract) depend on the sampled data. If the sample is representative, the estimate is close. On extract-configured sources with existing filters, the sample already reflects those filters.
- Report the caveat if the sample size is smaller than a reasonable threshold (< 10,000 rows for large tables).

## Refuse to Ship Without Numbers

If a finding cannot be quantified (e.g., because the tool surface fails or the sample returns zero rows), drop the finding rather than shipping it with hedged language.
