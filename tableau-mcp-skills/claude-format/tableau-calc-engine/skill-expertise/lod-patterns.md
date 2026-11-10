# LOD Expression Patterns

Reference patterns for FIXED, INCLUDE, EXCLUDE, two-level aggregation and multi-condition LOD expressions.

### FIXED Patterns

```tableau
// Customer's first order date (cohort assignment)
{ FIXED [Customer ID] : MIN([Order Date]) }

// Total sales per region (independent of view filters)
{ FIXED [Region] : SUM([Sales]) }

// Customer lifetime value (ignores time filters)
{ FIXED [Customer ID] : SUM([Sales]) }

// Flag: Is this the customer's first order?
[Order Date] = { FIXED [Customer ID] : MIN([Order Date]) }

// FIXED with date truncation (common pattern)
{ FIXED DATETRUNC('month', [Order Date]) : SUM([Sales]) }
```

### INCLUDE Patterns

```tableau
// Average order value (need order grain in customer-level view)
{ INCLUDE [Order ID] : SUM([Sales]) }
// Then use as AVG([above calc]) to get true average order size

// Daily count in a monthly view
{ INCLUDE [Order Date] : COUNTD([Order ID]) }
```

### EXCLUDE Patterns

```tableau
// % of category total (view shows Sub-Category)
SUM([Sales]) / { EXCLUDE [Sub-Category] : SUM([Sales]) }

// Deviation of a state's total from the average state total in its region (view shows Region and State)
SUM([Sales]) - ({ EXCLUDE [State] : SUM([Sales]) } / { EXCLUDE [State] : COUNTD([State]) })
// The first LOD is the region total; dividing by the state count gives the average state total.
// (AVG([Sales]) would average individual order rows, not state totals.)
```

### Two-Level Aggregation and Multi-Condition LODs

```tableau
// Average of customer-level totals (two-level aggregation)
// Place this on viz shelf as AVG() — averages the per-customer values
{ FIXED [Customer ID] : SUM([Sales]) }

// Customers who bought in BOTH Category A and B
{ FIXED [Customer ID] : COUNTD(
    IF [Category] = "A" OR [Category] = "B"
    THEN [Category] END
) } = 2
```
