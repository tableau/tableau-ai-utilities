# Type Conversion Functions (Locked)

Explicit datatype coercion. Row-level.

## Numeric

| Function | Signature | Return | Notes |
|---|---|---|---|
| INT | `INT(expression)` | Integer | Truncates decimals (not rounds). |
| FLOAT | `FLOAT(expression)` | Number | Converts to floating point. |

## String

| Function | Signature | Return | Notes |
|---|---|---|---|
| STR | `STR(expression)` | String | Converts any expression to string. |

## Date

| Function | Signature | Return | Notes |
|---|---|---|---|
| DATE | `DATE(expression)` | Date | Coerces string, datetime, or number to Date. |
| DATETIME | `DATETIME(expression)` | Datetime | Coerces to Datetime. |

## Boolean

| Function | Signature | Return | Notes |
|---|---|---|---|
| BOOL | `BOOL(expression)` | Boolean | Coerces to Boolean. Note: string 'true'/'false' → Boolean; number 0 → FALSE, nonzero → TRUE. |

## Common Patterns

- Convert a stringified number for math: `FLOAT([Numeric String])`.
- Format a number as a display string: `STR([Sales])`.
- Coerce a date-looking string to Date: `DATE([Date String])`, but prefer DATEPARSE for non-standard formats.
- Ensure Boolean interpretation: `BOOL([Flag Field])`.

## Common Anti-Patterns

- INT vs ROUND: INT truncates, doesn't round. `INT(2.7) = 2`, not 3. Use ROUND for rounding.
- STR without format control: for currency/percent display, use tooltip formatting or a display-string calc instead.
- DATE on a datetime loses the time portion. Confirm intent before dropping precision.
- Bare `BOOL()` on an untrusted string; validate first with ISNULL or a value check.

## R-TYPE-02 Return Type Discipline

If the ask specifies a return type ("give me a Boolean"), the outer function of the calc must return that type. Type conversion at the outermost position is the escape hatch for calcs that need to change their natural type.

## Version Notes

All type conversion functions available Desktop 2020.1+.
