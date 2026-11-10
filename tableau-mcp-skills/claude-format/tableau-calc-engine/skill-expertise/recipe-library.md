# Recipe Library

Ready-made multi-step calculation recipes for common analytical requests.

### Prior Period Comparison (Flexible)

```tableau
// Parameter: [Comparison Type] — "Prior Year", "Prior Month", "Prior Quarter"

// Step 1: Current period flag (row-level boolean)
// Name: "In Curr Period"
[Order Date] >= [Period Start] AND [Order Date] <= [Period End]

// Step 2: Prior period flag (row-level boolean)
// Name: "In Prior Period"
IF [Comparison Type] = "Prior Year" THEN
    [Order Date] >= DATEADD('year', -1, [Period Start])
    AND [Order Date] <= DATEADD('year', -1, [Period End])
ELSEIF [Comparison Type] = "Prior Month" THEN
    [Order Date] >= DATEADD('month', -1, [Period Start])
    AND [Order Date] <= DATEADD('month', -1, [Period End])
ELSEIF [Comparison Type] = "Prior Quarter" THEN
    [Order Date] >= DATEADD('quarter', -1, [Period Start])
    AND [Order Date] <= DATEADD('quarter', -1, [Period End])
ELSE FALSE
END

// Step 3: Period values (aggregates)
// Name: "Curr Sales"
SUM(IF [In Curr Period] THEN [Sales] END)

// Name: "Prior Sales"
SUM(IF [In Prior Period] THEN [Sales] END)

// Step 4: % Change
// Name: "Period Chg %"
([Curr Sales] - [Prior Sales]) / ABS([Prior Sales])
```

### Last N Complete Periods

```tableau
// Filter to last N COMPLETE months (excludes partial current month)
// Parameter: [N Months] — Integer, default 12

// Step 1: End of last complete month
// Name: "_Last Full Mo"
DATEADD('day', -1, DATETRUNC('month', TODAY()))

// Step 2: Start of window
// Name: "_Window Start"
DATEADD('month', -[N Months], DATETRUNC('month', TODAY()))

// Step 3: Filter calc (place on Filters → TRUE)
// Name: "In Window"
[Order Date] >= [_Window Start] AND [Order Date] <= [_Last Full Mo]
```

### Relative Date Window Comparison (Last 30 vs. Prior 30)

```tableau
// Compare last N days to the N days before that
// Parameter: [Window Days] — Integer, default 30

// Step 1: Period assignment (row-level)
// Name: "Date Window"
IF DATEDIFF('day', [Order Date], TODAY()) >= 0
   AND DATEDIFF('day', [Order Date], TODAY()) < [Window Days]
THEN "Current"
ELSEIF DATEDIFF('day', [Order Date], TODAY()) >= [Window Days]
   AND DATEDIFF('day', [Order Date], TODAY()) < [Window Days] * 2
THEN "Prior"
END

// Step 2: Aggregates per window
// Name: "Window Sales"
SUM(IF [Date Window] = "Current" THEN [Sales] END)

// Name: "Prior Window"
SUM(IF [Date Window] = "Prior" THEN [Sales] END)

// Step 3: % Change
// Name: "Window Chg %"
([Window Sales] - [Prior Window]) / ABS([Prior Window])
```

### Cohort Analysis

```tableau
// Step 1: Cohort month
// Name: "Cohort Month"
{ FIXED [Customer ID] : MIN(DATETRUNC('month', [Order Date])) }

// Step 2: Periods since cohort
// Name: "Periods Since"
DATEDIFF('month', [Cohort Month], DATETRUNC('month', [Order Date]))

// Step 3: Cohort size
// Name: "Cohort Size"
{ FIXED [Cohort Month] : COUNTD([Customer ID]) }

// Step 4: Retention rate
// Name: "Retention %"
COUNTD([Customer ID]) / MIN([Cohort Size])
// MIN() wraps the FIXED value so both sides are aggregates (avoids a mixed-aggregation error)
// Use on heatmap: Cohort Month on rows, Periods Since on columns
```

### Percent of Total (Three Methods)

```tableau
// Method 1: Table calc — responds to all filters
SUM([Sales]) / TOTAL(SUM([Sales]))

// Method 2: FIXED grand total — ignores dimension filters
SUM([Sales]) / { FIXED : SUM([Sales]) }
// Warning: FIXED ignores dimension filters. Use context filter if needed.

// Method 3: EXCLUDE parent — responsive to all filters
SUM([Sales]) / { EXCLUDE [Sub-Category] : SUM([Sales]) }
// Shows each sub-cat as % of its parent category
```

### Dynamic TOP N with "Other"

```tableau
// Step 1: Create a Set on [Product Name]
// Create > Set..., Top tab > By field > Top [Top N Parameter] by SUM([Sales])
// Name: "Top N Set"  (a parameter can drive N)

// Step 2: Grouping (row-level; a set can be used inside an IF)
// Name: "Top N Group"
IF [Top N Set] THEN [Product Name] ELSE "Other" END
// Put [Top N Group] on Rows and SUM([Sales]) on Columns.
// Every product outside the top N collapses into one "Other" mark.

// Step 3: Sort (keeps "Other" at the bottom)
// Name: "Top N Sort"
IF ATTR([Top N Group]) = "Other" THEN 0 ELSE SUM([Sales]) END
// ATTR() is required because [Top N Group] is a dimension inside an aggregate-level calc.
// Sort [Top N Group] descending by field [Top N Sort].
```

Why a set and not RANK: a table calc such as RANK runs after aggregation, so it can't define a dimension that groups the marks. A set is evaluated before the view is built. Note that the set ranks across the whole datasource unless you add it to Context or use a conditional set with a filter.

### Year-over-Year (Two Approaches)

```
Choose: continuous month axis or growth line -> Approach B (table calc).
Discrete year comparison independent of view layout -> Approach A (uses TODAY()).
Fiscal year (user said "fiscal") -> use the Fiscal YoY recipe below; ask the start month only if not given.
```

```tableau
// Approach A: Separate calcs (works with discrete date)
// Name: "CY Sales"
IF YEAR([Order Date]) = YEAR(TODAY()) THEN [Sales] END

// Name: "PY Sales"
IF YEAR([Order Date]) = YEAR(TODAY()) - 1 THEN [Sales] END

// Name: "YoY %"
(SUM([CY Sales]) - SUM([PY Sales])) / ABS(SUM([PY Sales]))
// Warning: during the current year this compares year-to-date against the full prior year.
// For a like-for-like (YTD) comparison, use this PY calc instead:
// Name: "PY Sales (YTD)"
IF YEAR([Order Date]) = YEAR(TODAY()) - 1 AND DATEADD('year', 1, [Order Date]) <= TODAY() THEN [Sales] END

// Approach B: LOOKUP table calc (works with continuous month axis)
(SUM([Sales]) - LOOKUP(SUM([Sales]), -12)) / ABS(LOOKUP(SUM([Sales]), -12))
// Addressing: Month of Order Date. -12 = 12 months back.
```

### Fiscal Year-over-Year

```tableau
// Parameter: [FY Start Month] — Integer, 1-12 (7 = fiscal year starts in July)
// The fiscal year is named for the calendar year in which it ends.

// Name: "Fiscal Year"
YEAR(DATEADD('month', (13 - [FY Start Month]) % 12, [Order Date]))

// Name: "Current FY"
YEAR(DATEADD('month', (13 - [FY Start Month]) % 12, TODAY()))

// Name: "FY Sales"
IF [Fiscal Year] = [Current FY] THEN [Sales] END

// Name: "PY FY Sales"
IF [Fiscal Year] = [Current FY] - 1 THEN [Sales] END

// Name: "Fiscal YoY %"
(SUM([FY Sales]) - SUM([PY FY Sales])) / ABS(SUM([PY FY Sales]))
// With FY Start Month = 1 this equals calendar year. Like Approach A, it compares the year to date
// with the full prior fiscal year; for a like-for-like version, restrict PY FY Sales to dates
// where DATEADD('year', 1, [Order Date]) <= TODAY().
```

### Moving Average (Configurable)

```tableau
// Parameter: [MA Window] — Integer, range 2-12, default 3
// Name: "₮Moving Avg"
IF INDEX() >= [MA Window]
THEN WINDOW_AVG(SUM([Sales]), -([MA Window] - 1), 0)
END
// INDEX() is the position in the partition, so the first (window - 1) periods return NULL
// (SIZE() is the partition's total length and would not null the leading periods)
```

### Conditional Formatting / KPI Status

```tableau
// Name: "KPI Status"
IF SUM([Sales]) >= [Target] THEN "Above Target"
ELSEIF SUM([Sales]) >= [Target] * 0.9 THEN "Near Target"
ELSE "Below Target"
END
// Map colors: Above = #59A14F, Near = #F28E2B, Below = #E15759
```

### Days Since Last Event

```tableau
// Name: "Days Inactive"
DATEDIFF('day', { FIXED [Customer ID] : MAX([Order Date]) }, TODAY())
```

### Order Sequence per Customer

```tableau
// Use INDEX() table calc — partition by Customer, address by Order Date
// Name: "₮Order Seq"
INDEX()
// Compute Using: [Order Date] (ascending), Partition: [Customer ID]
```

### Distinct Count with Conditions

```tableau
// Customers who ordered 3+ times
// Name: "Freq Buyers"
{ FIXED [Customer ID] : COUNTD([Order ID]) } >= 3
// Returns boolean per row. Use as filter or in aggregate:
// COUNTD(IF [Freq Buyers] THEN [Customer ID] END)
```

### 52-Week High/Low

```tableau
// Name: "₮52wk High"
WINDOW_MAX(SUM([Sales]), -51, 0)

// Name: "₮% from High"
1 - (SUM([Sales]) / WINDOW_MAX(SUM([Sales]), -51, 0))
```
