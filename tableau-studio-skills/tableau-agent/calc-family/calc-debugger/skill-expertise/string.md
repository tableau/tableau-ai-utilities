# String Functions (Locked)

Row-level string functions. Signatures cite help.tableau.com. All available in Desktop 2020.1+ unless noted.

## Position and Search

| Function | Signature | Return | Notes |
|---|---|---|---|
| CONTAINS | `CONTAINS(string, substring)` | Boolean | Case-sensitive. |
| STARTSWITH | `STARTSWITH(string, prefix)` | Boolean | Case-sensitive. |
| ENDSWITH | `ENDSWITH(string, suffix)` | Boolean | Case-sensitive. |
| FIND | `FIND(string, substring, [start])` | Integer | Returns position (1-based) or 0 if not found. |
| FINDNTH | `FINDNTH(string, substring, occurrence)` | Integer | Position of Nth occurrence. |

## Extract and Transform

| Function | Signature | Return | Notes |
|---|---|---|---|
| LEFT | `LEFT(string, N)` | String | First N characters. |
| RIGHT | `RIGHT(string, N)` | String | Last N characters. |
| MID | `MID(string, start, [length])` | String | Substring. |
| LEN | `LEN(string)` | Integer | Character length. |
| LOWER | `LOWER(string)` | String | Lowercase. |
| UPPER | `UPPER(string)` | String | Uppercase. |
| PROPER | `PROPER(string)` | String | Title case. |
| REPLACE | `REPLACE(string, substring, replacement)` | String | First occurrence only? Check docs; behavior is all-occurrences in most versions. |
| TRIM | `TRIM(string)` | String | Strip leading and trailing whitespace. |
| LTRIM | `LTRIM(string)` | String | Strip leading whitespace. |
| RTRIM | `RTRIM(string)` | String | Strip trailing whitespace. |
| SPACE | `SPACE(N)` | String | Returns N space characters. |
| CHAR | `CHAR(codepoint)` | String | Character for Unicode codepoint. |
| ASCII | `ASCII(string)` | Integer | ASCII code of first character. |

## Split

| Function | Signature | Return | Notes |
|---|---|---|---|
| SPLIT | `SPLIT(string, delimiter, token_number)` | String | Returns the Nth token, 1-indexed. Negative index counts from end. |

## Regex (2013.1+, all supported versions)

| Function | Signature | Return | Notes |
|---|---|---|---|
| REGEXP_MATCH | `REGEXP_MATCH(string, pattern)` | Boolean | Full pattern match. |
| REGEXP_EXTRACT | `REGEXP_EXTRACT(string, pattern)` | String | First capture group. |
| REGEXP_EXTRACT_NTH | `REGEXP_EXTRACT_NTH(string, pattern, N)` | String | Nth capture group. |
| REGEXP_REPLACE | `REGEXP_REPLACE(string, pattern, replacement)` | String | Global replace. |

## Aggregate-context Rewrites (see aggregate.md for full aggregate string functions)

`MAX(string)` and `MIN(string)` in aggregate contexts return lexicographic min/max, not string length.

## Common Anti-Patterns

- Bare `LEFT([Field], 3) = 'ABC'` when `STARTSWITH([Field], 'ABC')` reads more clearly.
- `CONTAINS(LOWER([Field]), 'abc')` when regex would perform better on large datasets (R-PERF-01).
- SPLIT with 0 or unbounded token numbers; token_number must be a specific integer.
- REGEXP_MATCH inside aggregations where a pre-aggregated equivalent exists (R-PERF-01).

## Version Notes

All string functions available Desktop 2020.1+. Regex functions available Desktop 2013.1+.
