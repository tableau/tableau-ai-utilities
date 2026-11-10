# Date Functions (Locked)

Row-level date and datetime functions. Signatures cite help.tableau.com. All available in Desktop 2020.1+ unless noted.

## Parts and Truncation

| Function | Signature | Return | Notes |
|---|---|---|---|
| DAY | `DAY(date)` | Integer | Day of month. |
| MONTH | `MONTH(date)` | Integer | Month number. |
| YEAR | `YEAR(date)` | Integer | Year. |
| WEEK | `WEEK(date)` | Integer | Week of year. |
| QUARTER | `QUARTER(date)` | Integer | Quarter (1-4). |
| DATEPART | `DATEPART('part', date, [start_of_week])` | Integer | Generic; 'part' is 'year', 'quarter', 'month', 'week', 'day', 'hour', etc. |
| DATENAME | `DATENAME('part', date, [start_of_week])` | String | String name of part. |
| DATETRUNC | `DATETRUNC('part', date, [start_of_week])` | Date | Truncates to the start of the part. |

## Arithmetic

| Function | Signature | Return | Notes |
|---|---|---|---|
| DATEADD | `DATEADD('part', N, date)` | Date | Add N units. Negative N to subtract. |
| DATEDIFF | `DATEDIFF('part', start, end, [start_of_week])` | Integer | Whole-number difference in units. |

## Construction

| Function | Signature | Return | Notes |
|---|---|---|---|
| MAKEDATE | `MAKEDATE(year, month, day)` | Date | 2020.1+. |
| MAKEDATETIME | `MAKEDATETIME(date, time)` | Datetime | 2020.1+. Combines a date and time. |
| MAKETIME | `MAKETIME(hour, minute, second)` | Time | 2020.1+. |

## Current Values

| Function | Signature | Return | Notes |
|---|---|---|---|
| NOW | `NOW()` | Datetime | Current datetime; refreshes per query. |
| TODAY | `TODAY()` | Date | Current date. |

## Parsing

| Function | Signature | Return | Notes |
|---|---|---|---|
| DATEPARSE | `DATEPARSE('format', string)` | Date | 8.2+. Format uses Java SimpleDateFormat patterns. |
| DATE | `DATE(expression)` | Date | Coerce expression to Date. |
| ISDATE | `ISDATE(string)` | Boolean | Returns TRUE if the string is a valid date. |

## Common Patterns

- Days between order and ship: `DATEDIFF('day', [Order Date], [Ship Date])`.
- Truncate to first of month: `DATETRUNC('month', [Date])`.
- Year-over-year comparison: filter by `YEAR([Date]) = YEAR(TODAY())` vs. `YEAR([Date]) = YEAR(TODAY()) - 1`.
- Age in years: `DATEDIFF('year', [Birth Date], TODAY())`.

## Common Anti-Patterns

- Using `DATEDIFF('day', a, b)` when you need business days; there's no built-in business-day function.
- DATEPARSE with a wrong format string; test on a real value first.
- Comparing datetime to date without truncation may miss same-day matches.
- Using `NOW()` inside a FIXED LOD; refresh timing may not match user intent.

## Version Notes

- MAKEDATE, MAKEDATETIME, MAKETIME require Desktop 2020.1+.
- DATEPARSE available 8.2+ (all supported versions).
