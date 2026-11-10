# Calculation Templates

Common Tableau calculated field patterns used when building worksheets. Use `author-calc` to create these when the chart spec requires them.

***

## Year-over-Year Change (%)

**Use when:** Temporal chart needs comparison to same period last year.

```
// Table calculation approach (requires date on axis)
(SUM([Measure]) - LOOKUP(SUM([Measure]), -1)) / ABS(LOOKUP(SUM([Measure]), -1))

// Compute using: [Date Part] (e.g., Month of Order Date)
// Format: Percentage, 1 decimal
```

**LOD approach (period-independent):**
```
// Current Year Total
{ FIXED : SUM(IF YEAR([Date]) = YEAR(TODAY()) THEN [Measure] END) }

// Prior Year Total
{ FIXED : SUM(IF YEAR([Date]) = YEAR(TODAY()) - 1 THEN [Measure] END) }

// YoY Change
([Current Year Total] - [Prior Year Total]) / ABS([Prior Year Total])
```

***

## Running Total

**Use when:** Area chart showing cumulative, or tracking progress toward target.

```
RUNNING_SUM(SUM([Measure]))

// Compute using: [Date dimension]
// Addressing/Partitioning: compute along time, partition by category (if applicable)
```

***

## Percent of Total

**Use when:** Composition chart showing proportional share.

```
SUM([Measure]) / TOTAL(SUM([Measure]))

// Compute using: [Dimension on which you want percent]
// Format: Percentage, 1 decimal
// Example: each category's share of all categories
```

**For 100% stacked bars:**
- Apply as a table calculation on the measure already on Columns
- Compute using the color dimension (the parts)

***

## TOP N Filter (Parameter-Driven)

**Use when:** Bar chart should show only top N categories with a user-controlled parameter.

**Step 1: Create parameter**
```
Name: [Top N]
Type: Integer
Current value: 10
Range: 1 to 50
```

**Step 2: Create calculated field**
```
INDEX() <= [Top N]

// Compute using: [Dimension being ranked]
// Sort by: [Measure] descending (must set before applying)
```

**Step 3: Add to Filters shelf, keep TRUE only**

***

## TOP N Per Group / Facet (e.g. "top 5 products per region")

**Use when:** the ask is "top N [dimension A] for/by each/per [dimension B]" — the ranking must restart within each member of a partition dimension (region, category, year), not run globally across the whole table. This is distinct from the single-dimension TOP N Filter above.

**Do NOT try `bind-template`'s auto-applied Top-N for this.** It only handles a single flat ranking; when a partition dimension is present (e.g. `facet_row`), the server-side Top-N splice fails outright with an error like "Top-N over calcs is out of scope for this refinement" rather than silently doing the wrong thing. That failure is the signal to build the ranking filter manually — don't retry the template call.

**Step 1: Build the base chart first** (bind-template or manual), with the partition dimension and the ranked dimension nested on rows — e.g. `Region / Product Name` — and the measure on columns. Apply and confirm it renders before adding the rank filter.

**Step 2: Author a RANK calc**
```
RANK(SUM([Measure]))

// datatype: integer (Tableau overrides real -> integer on RANK regardless)
// role: measure
```

**Step 3: Set Compute Using to the RANKED dimension, not the partition dimension.** This is the detail that makes per-group ranking work: addressing (`ordering-type="Field"`, `ordering-field=`) must point at the dimension being ranked (e.g. Product Name). Whatever OTHER dimension is on the shelf but not addressed (e.g. Region) automatically becomes the partition boundary — the rank restarts at 1 for each Region member. Getting this backwards (addressing Region instead) produces one continuous rank ignoring the group boundaries.

**Step 4: Filter to the rank range.** A quantitative range filter on the RANK calc's column-instance, `included-values="in-range"` with `<min>1</min><max>5</max>` for top 5, restricted via a `<slices>` entry for the same CI.

**Verify:** `get-summary-data` should return exactly N rows × (number of partition members) — e.g. top 5 across 4 regions = 20 rows — and each partition's values should independently taper off after N rows, not follow one global ranking. Don't trust a clean `apply-worksheet` message alone; a "silently dropped" warning on the apply response has been observed as a false negative (rows/cols reported dropped but present on readback) — always re-fetch and check the real data before either accepting or discarding the result.

***

## Moving Average

**Use when:** Line chart needs smoothing to show underlying trend through noise.

```
WINDOW_AVG(SUM([Measure]), -[Window Size] + 1, 0)

// -2, 0 = 3-period moving average (current + 2 prior)
// -5, 0 = 6-period moving average
// Compute using: [Date dimension]
```

**With parameter for user control:**
```
Name: [MA Window]
Type: Integer
Current value: 3
Range: 2 to 12

Calc: WINDOW_AVG(SUM([Measure]), -[MA Window] + 1, 0)
```

***

## Period-over-Period Comparison (Flexible)

**Use when:** KPI tile or bar chart needs "vs. prior period" regardless of granularity.

```
// Prior period value (table calc)
LOOKUP(SUM([Measure]), -1)

// Change (absolute)
SUM([Measure]) - LOOKUP(SUM([Measure]), -1)

// Change (percent)
(SUM([Measure]) - LOOKUP(SUM([Measure]), -1)) / ABS(LOOKUP(SUM([Measure]), -1))

// Compute using: [Date dimension at chosen granularity]
```

***

## Status Classification

**Use when:** KPI tile, bullet chart, or any view needs green/yellow/red status encoding.

**Against a fixed target:**
```
IF SUM([Measure]) >= [Target Parameter]
  THEN "On Track"
ELSEIF SUM([Measure]) >= [Target Parameter] * 0.9
  THEN "Caution"
ELSE "Alert"
END
```

**Against prior period (growth-based):**
```
IF [YoY Change %] >= 0.05 THEN "Strong"
ELSEIF [YoY Change %] >= 0 THEN "Stable"
ELSEIF [YoY Change %] >= -0.05 THEN "Caution"
ELSE "Alert"
END
```

**Inverted sentiment (lower is better, e.g., costs, churn):**
```
IF SUM([Measure]) <= [Target Parameter]
  THEN "On Track"
ELSEIF SUM([Measure]) <= [Target Parameter] * 1.1
  THEN "Caution"
ELSE "Alert"
END
```

***

## Variance from Target

**Use when:** Bullet chart or diverging bar showing gap to goal.

```
// Absolute variance
SUM([Measure]) - [Target]

// Percent variance
(SUM([Measure]) - [Target]) / ABS([Target])

// Format: +0.0%; -0.0% (show sign always)
```

***

## Index/Normalize to Baseline

**Use when:** Multi-line chart with different-scale measures needs a common axis (alternative to dual axes).

```
// Index to first value (= 100 at baseline)
SUM([Measure]) / LOOKUP(SUM([Measure]), FIRST()) * 100

// Compute using: [Date dimension]
// Both measures start at 100, showing relative change
```

***

## Rank

**Use when:** Ranking chart needs explicit rank numbers in labels.

```
RANK(SUM([Measure]))

// Compute using: [Dimension being ranked]
// Tie-breaking: Competition (1, 2, 2, 4) or Dense (1, 2, 2, 3) — usually Competition
```

***

## Days Since / Recency

**Use when:** KPI or status chart showing freshness or elapsed time.

```
DATEDIFF('day', MAX([Date Field]), TODAY())

// Useful for: "last updated X days ago", freshness indicators
// Status version:
IF DATEDIFF('day', MAX([Date Field]), TODAY()) <= 1 THEN "Current"
ELSEIF DATEDIFF('day', MAX([Date Field]), TODAY()) <= 7 THEN "Recent"
ELSE "Stale"
END
```

***

## Conditional Formatting (for Labels/Text)

**Use when:** Data labels need to show positive/negative with symbols.

```
// Arrow prefix
IF [Change %] > 0 THEN "▲ " + STR(ROUND([Change %] * 100, 1)) + "%"
ELSEIF [Change %] < 0 THEN "▼ " + STR(ROUND(ABS([Change %]) * 100, 1)) + "%"
ELSE "— 0.0%"
END
```

***

## Bin Creation (for Histograms)

**Use when:** Distribution chart needs binned data.

```
// In Tableau: Right-click [Measure] → Create → Bins
// Or calculated:
INT([Measure] / [Bin Size]) * [Bin Size]

// With parameter for dynamic bin size:
Name: [Bin Size]
Type: Float
Current value: 10
Range: 1 to 100
```

***

## Usage Notes

- Always verify field names exist via `resolve-field` before writing any calc
- Use `author-calc` to create the field, then place it on shelves
- Table calculations require specifying "Compute using" — always note this in the shelf recipe
- LOD expressions are evaluated before filters (except context filters) — note when this matters
- Format strings: use Tableau format codes ($#,##0 for currency; 0.0% for percent; #,##0 for integers)
