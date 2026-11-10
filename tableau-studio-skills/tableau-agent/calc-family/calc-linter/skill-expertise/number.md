# Number Functions (Locked)

Row-level number functions. Signatures cite help.tableau.com. All available in Desktop 2020.1+ unless noted.

## Basic Arithmetic

| Function | Signature | Return | Notes |
|---|---|---|---|
| ABS | `ABS(number)` | Number | Absolute value. |
| CEILING | `CEILING(number)` | Integer | Round up to nearest integer. |
| FLOOR | `FLOOR(number)` | Integer | Round down. |
| ROUND | `ROUND(number, [decimals])` | Number | Optional decimals arg; default 0. |
| SIGN | `SIGN(number)` | Integer | Returns -1, 0, or 1. |
| SQUARE | `SQUARE(number)` | Number | Squares the input. |
| SQRT | `SQRT(number)` | Number | Square root. NULL if negative. |
| POWER | `POWER(number, power)` | Number | Base to the power. |
| EXP | `EXP(number)` | Number | e^x. |
| LN | `LN(number)` | Number | Natural log. NULL if ≤ 0. |
| LOG | `LOG(number, [base])` | Number | Log base 10 default; optional base arg. |

## Trig

| Function | Signature | Return |
|---|---|---|
| SIN | `SIN(number)` | Number |
| COS | `COS(number)` | Number |
| TAN | `TAN(number)` | Number |
| ASIN | `ASIN(number)` | Number |
| ACOS | `ACOS(number)` | Number |
| ATAN | `ATAN(number)` | Number |
| ATAN2 | `ATAN2(y, x)` | Number |
| DEGREES | `DEGREES(radians)` | Number |
| RADIANS | `RADIANS(degrees)` | Number |
| PI | `PI()` | Number | Returns π. |

## Divisibility

| Function | Signature | Return | Notes |
|---|---|---|---|
| DIV | `DIV(integer, integer)` | Integer | Integer division. |
| MAX | `MAX(a, b)` | Number | Max of two values (row-level; distinct from aggregate MAX). |
| MIN | `MIN(a, b)` | Number | Min of two values (row-level). |

## Advanced

| Function | Signature | Return | Notes |
|---|---|---|---|
| ZN | `ZN(expression)` | Number | Returns 0 if NULL, else the value. Critical for R-NULL-01. |
| MODEL_QUANTILE | `MODEL_QUANTILE(quantile, target, predictors)` | Number | 2020.3+. |
| MODEL_PERCENTILE | `MODEL_PERCENTILE(target, predictors)` | Number | 2020.3+. |

## Common Anti-Patterns

- `SUM([Sales]) / SUM([Rows])` where `[Rows]` is a raw field. Should be `SUM([Sales]) / SUM(1)` for a count, or better use `AVG([Sales])`.
- Bare arithmetic on nullable fields without ZN wrapping. Should be `ZN([Field A]) + ZN([Field B])` if NULLs should be treated as 0.
- `POWER(x, 0.5)` when `SQRT(x)` reads more clearly.

## Version Notes

All functions listed available Desktop 2020.1+ except MODEL_QUANTILE and MODEL_PERCENTILE (2020.3+).
