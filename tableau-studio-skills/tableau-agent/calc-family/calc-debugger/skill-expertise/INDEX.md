# Function Library Index (Locked)

~150 Tableau Studio functions across 8 categories. HC#2 discipline: signatures looked up here, never guessed. Version-gated status called out inline.

## Categories

Each function group has its own file. INDEX lists which function belongs where.

| Category | File | Function Count |
|---|---|---|
| Number | `number.md` | ~25 |
| String | `string.md` | ~30 |
| Date | `date.md` | ~25 |
| Logical | `logical.md` | ~15 |
| Aggregate | `aggregate.md` | ~10 |
| LOD | `lod.md` | 3 (FIXED, INCLUDE, EXCLUDE) |
| Table Calc | `table_calc.md` | ~20 |
| Spatial | `spatial.md` | ~10 |
| Type Conversion | `type_conversion.md` | ~10 |

## Version-Gated Functions

:

| Function | Category | Minimum Desktop Version |
|---|---|---|
| MAKEPOINT | Spatial | 2019.2 |
| BUFFER | Spatial | 2024.1 |
| MAKELINE | Spatial | 2019.2 |
| DISTANCE | Spatial | 2019.2 |
| INTERSECTS | Spatial | 2019.2 |
| USEREMAIL | Logical | 2023.3 |
| MODEL_QUANTILE | Number | 2020.3 |
| MODEL_PERCENTILE | Number | 2020.3 |
| REGEXP_MATCH | String | 2013.1 (all supported) |
| REGEXP_EXTRACT | String | 2013.1 (all supported) |
| REGEXP_REPLACE | String | 2013.1 (all supported) |
| DATEPARSE | Date | 8.2 (all supported) |
| MAKEDATE | Date | 2020.1 |
| MAKEDATETIME | Date | 2020.1 |
| MAKETIME | Date | 2020.1 |

## Common Row-Level Functions (Number)

`ABS, CEILING, DIV, EXP, FLOOR, LN, LOG, MAX, MIN, PI, POWER, RADIANS, ROUND, SIGN, SIN, SQRT, SQUARE, TAN, ZN, IIF, IIFNULL`

## Common Aggregate Functions

`SUM, AVG, MEDIAN, COUNT, COUNTD, MIN, MAX, ATTR, PERCENTILE, STDEV, STDEVP, VAR, VARP, CORR, COVAR, COVARP`

## Common String Functions

`ASCII, CHAR, CONTAINS, ENDSWITH, FIND, FINDNTH, LEFT, LEN, LOWER, LTRIM, MAX, MID, MIN, PROPER, REPLACE, RIGHT, RTRIM, SPACE, SPLIT, STARTSWITH, TRIM, UPPER, REGEXP_MATCH, REGEXP_EXTRACT, REGEXP_REPLACE`

## Common Date Functions

`DATEADD, DATEDIFF, DATENAME, DATEPART, DATEPARSE, DATETRUNC, DAY, MONTH, NOW, TODAY, YEAR, WEEK, QUARTER, MAKEDATE, MAKEDATETIME, MAKETIME, ISDATE`

## Common Logical Functions

`IF ... THEN ... ELSEIF ... ELSE ... END, CASE ... WHEN ... THEN ... ELSE ... END, IFNULL, ISNULL, IIF, AND, OR, NOT, IN, USERNAME, USEREMAIL, ISUSERADMIN, ISFULLNAME`

## Common Table Calcs

`WINDOW_SUM, WINDOW_AVG, WINDOW_COUNT, WINDOW_MAX, WINDOW_MIN, WINDOW_MEDIAN, WINDOW_STDEV, WINDOW_VAR, RUNNING_SUM, RUNNING_AVG, RUNNING_COUNT, RUNNING_MAX, RUNNING_MIN, PREVIOUS_VALUE, INDEX, RANK, RANK_DENSE, RANK_MODIFIED, RANK_PERCENTILE, RANK_UNIQUE, FIRST, LAST, LOOKUP, SIZE, TOTAL`

## LOD Expressions

`{FIXED [dim1], [dim2] : agg([measure])}`
`{INCLUDE [dim1], [dim2] : agg([measure])}`
`{EXCLUDE [dim1], [dim2] : agg([measure])}`

## Common Spatial Functions

`MAKEPOINT, MAKELINE, DISTANCE, BUFFER, INTERSECTS, AREA, LENGTH, CENTROID, X, Y`

## Type Conversion

`INT, FLOAT, STR, DATE, DATETIME, BOOL`

## Refuse to Fabricate

If the user's ask requires a function not listed above, refuse the write per HC#2. Never invent a signature.

For the full signature, return type, and LOD/TC eligibility of each function, see the category-specific `.md` files in this folder. Every entry cites help.tableau.com as source of truth.
