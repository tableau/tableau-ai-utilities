# Logical Functions (Locked)

Row-level logical operators, conditionals, and user-context predicates. Signatures cite help.tableau.com.

## Conditionals

| Function | Signature | Return | Notes |
|---|---|---|---|
| IF ... THEN ... [ELSEIF] ... ELSE ... END | `IF condition THEN result [ELSEIF ...] ELSE fallback END` | Any | Standard branching. |
| CASE ... WHEN ... THEN ... [ELSE] ... END | `CASE expression WHEN value THEN result [ELSE fallback] END` | Any | Equality-only pattern; prefer IF for range checks. |
| IIF | `IIF(condition, true_value, false_value, [null_value])` | Any | Short-form. Optional 4th arg for NULL branch. |
| IFNULL | `IFNULL(expression, fallback)` | Any | Fallback if expression is NULL. |
| ISNULL | `ISNULL(expression)` | Boolean | Returns TRUE if NULL. |
| ZN | `ZN(expression)` | Number | Zero if NULL; also in number.md. |

## Booleans

| Function | Signature | Return |
|---|---|---|
| AND | `condition1 AND condition2` | Boolean |
| OR | `condition1 OR condition2` | Boolean |
| NOT | `NOT condition` | Boolean |
| IN | `expression IN (value1, value2, ...)` | Boolean |

## User Context (2023.3+ where noted)

| Function | Signature | Return | Notes |
|---|---|---|---|
| USERNAME | `USERNAME()` | String | Current username. |
| USEREMAIL | `USEREMAIL()` | String | 2023.3+. Current user's email. |
| USERDOMAIN | `USERDOMAIN()` | String | Domain portion of username. |
| ISUSERADMIN | `ISUSERADMIN()` | Boolean | TRUE if user is site admin. |
| ISFULLNAME | `ISFULLNAME(string)` | Boolean | TRUE if current user matches. |
| ISUSERNAME | `ISUSERNAME(string)` | Boolean | TRUE if current user matches. |
| ISMEMBEROF | `ISMEMBEROF(group_name)` | Boolean | TRUE if user is in group. |

## Common Patterns

- Boolean flag: `[Sales] > 500` returns Boolean directly, no IF needed.
- NULL-safe default: `IFNULL([Field], 0)`.
- Range bucketing: `IF [Sales] < 100 THEN 'Low' ELSEIF [Sales] < 500 THEN 'Med' ELSE 'High' END`.
- Row-level security proxy: `IF [Region] = USERDOMAIN() OR ISUSERADMIN() THEN [Sales] END`.

## R-BOOL-01 Discipline

Boolean calcs return TRUE/FALSE/NULL. Never 1/0/-1. Downstream logic tests as:
- Correct: `IF [BoolCalc] THEN ... END`
- Wrong: `IF [BoolCalc] = 1 THEN ... END`

## Common Anti-Patterns

- `IF [Field] = TRUE THEN 'Y' ELSE 'N' END` when Boolean directly works.
- IIF nested >2 levels; use IF for readability.
- `ISNULL([Field]) = TRUE` when `ISNULL([Field])` alone works.
- CASE for range comparisons; use IF/ELSEIF instead.

## Version Notes

- USEREMAIL requires Desktop 2023.3+.
- Everything else available Desktop 2020.1+.
