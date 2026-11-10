# Table Calculation Patterns

Reference library of common table calculations and a debugging table for them.

### Common Table Calcs

```tableau
// Running total
RUNNING_SUM(SUM([Sales]))
// Addressing: the dimension you're accumulating across (usually date)

// Year-over-Year % change, year axis (one mark per year)
(ZN(SUM([Sales])) - LOOKUP(ZN(SUM([Sales])), -1)) / ABS(LOOKUP(ZN(SUM([Sales])), -1))
// Addressing: Year. -1 = the previous year. ZN() prevents NULL errors.

// Year-over-Year % change, month axis (one mark per month)
(ZN(SUM([Sales])) - LOOKUP(ZN(SUM([Sales])), -12)) / ABS(LOOKUP(ZN(SUM([Sales])), -12))
// Addressing: Month of Order Date. -12 = the same month last year.
// With Month addressing, -1 would be month-over-month, not year-over-year.

// Percent of Total
SUM([Sales]) / TOTAL(SUM([Sales]))
// TOTAL() sums across the entire partition

// Rank (Competition)
RANK(SUM([Sales]))

// Moving average (3-period)
WINDOW_AVG(SUM([Sales]), -2, 0)

// Difference from first value
SUM([Sales]) - LOOKUP(SUM([Sales]), FIRST())
// FIRST() returns the offset to the first row; LOOKUP retrieves that row's value

// Index / Row Number
INDEX()

// Year-to-Date running total that resets each year
// Use RUNNING_SUM with Compute Using = date field, Advanced → Restart every Year
RUNNING_SUM(SUM([Sales]))
```

### Table Calc Debugging

| Symptom | Likely Cause | Fix |
|---|---|---|
| All NULLs | Addressing dimension not in the view | Add dimension or change Compute Using |
| Wrong values | Addressing/partitioning inverted | Switch Compute Using setting |
| Doesn't restart | Partitioning dimension not set | Add to partitioning or use "Restart every" |
| Rank ties wrong | Wrong rank type | RANK() vs. RANK_DENSE() vs. RANK_MODIFIED() |
| LOOKUP NULL at edges | No prior/next value exists | Wrap in ZN() or IFNULL() |
