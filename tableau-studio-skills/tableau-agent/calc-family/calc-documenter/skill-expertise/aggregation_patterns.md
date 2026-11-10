# Aggregation Pattern Classification (Locked)

Every calc gets classified into one of six aggregation-context types. Classification is pattern-based on the formula text, cited in the doc entry.

## The Six Types

| Type | Pattern trigger | Example |
|---|---|---|
| **row-level** | Formula contains no aggregate function and no LOD keyword | `[Sales] * 0.1` |
| **aggregate** | Formula contains SUM/AVG/COUNT/COUNTD/MIN/MAX/MEDIAN/STDEV/VAR/ATTR at top level | `SUM([Sales]) - SUM([Cost])` |
| **LOD-fixed** | Formula contains `{FIXED [dim]:` at top level (or nested inside an aggregate) | `{FIXED [Region]: SUM([Sales])}` |
| **LOD-include** | Formula contains `{INCLUDE [dim]:` at top level | `{INCLUDE [Order Date]: SUM([Sales])}` |
| **LOD-exclude** | Formula contains `{EXCLUDE [dim]:` at top level | `{EXCLUDE [Region]: SUM([Sales])}` |
| **table-calc** | Formula contains WINDOW_SUM / RUNNING_SUM / TOTAL / RANK / INDEX / FIRST / LAST / SIZE / LOOKUP / SCRIPT_* | `WINDOW_SUM(SUM([Sales]))` |

## Classification Precedence

When multiple patterns could apply, the following precedence order determines the classification:

1. **LOD-fixed** (if formula contains `{FIXED ...:` regardless of what wraps it).
2. **LOD-include** (if formula contains `{INCLUDE ...:` at any nesting).
3. **LOD-exclude** (if formula contains `{EXCLUDE ...:` at any nesting).
4. **table-calc** (if formula contains any of the WINDOW_*/RUNNING_*/RANK/INDEX/FIRST/LAST/SIZE/LOOKUP/SCRIPT_* keywords).
5. **aggregate** (if formula contains SUM/AVG/COUNT/COUNTD/MIN/MAX/MEDIAN/STDEV/VAR/ATTR at top level, not inside an LOD).
6. **row-level** (fallback when no aggregate or LOD keyword fires).

**Rationale.** LOD keywords carry the strongest semantic signal about aggregation grain and are treated as authoritative. Table calcs come next because they change the computation model even if wrapped around an aggregate. Aggregate is the mid-tier default. Row-level is the fallback.

## Pattern Detection Rules

**Case sensitivity.** Tableau function names are case-insensitive in formulas but conventionally uppercase. Pattern match is case-insensitive.

**Whitespace normalization.** Strip leading/trailing whitespace and collapse internal runs to single spaces before pattern matching.

**Comment stripping.** Tableau supports `//` line comments in calc formulas. Strip these before classification to avoid false positives inside commented-out logic.

**Nested aggregate detection.** A calc like `SUM([Sales]) / {FIXED [Region]: SUM([Sales])}` classifies as LOD-fixed (precedence 1) even though it contains SUM.

**Nested table-calc detection.** A calc like `WINDOW_SUM(SUM([Sales]))` classifies as table-calc (precedence 4) because the WINDOW_SUM wrapper is the outermost operation.

## Cited Pattern in the Entry

Every doc entry cites the specific pattern that fired the classification. Examples:

- `Aggregation pattern cited: "SUM at top level, no LOD or table-calc keyword"` → aggregate
- `Aggregation pattern cited: "{FIXED [Region]: ...} at nesting level 0"` → LOD-fixed
- `Aggregation pattern cited: "WINDOW_SUM wrapping inner SUM"` → table-calc
- `Aggregation pattern cited: "No aggregate or LOD keyword; row-level default"` → row-level

## Common Ambiguities

**Attribute in a non-aggregating context.** `ATTR([Region])` at top level classifies as aggregate. `IF ATTR([Region]) = "EMEA"` also aggregate.

**Row-level with aggregate-looking function names.** `ROUND([Sales], 2)` is row-level (ROUND doesn't aggregate). Do not misclassify.

**Table calcs inside LODs.** Tableau doesn't allow this; if the formula contains both `{FIXED` and `WINDOW_SUM`, the workbook would fail to compile. Skill flags this as `AGG-CONFLICT-01` and refuses to classify (renders as `"conflict: LOD + table-calc invalid"`).

**Parameter references in row-level calcs.** `[Parameters].[Threshold]` is a row-level reference. Does not trigger any aggregation type.

**IIF and CASE with aggregate branches.** `IIF(SUM([Sales]) > 1000, "high", "low")` classifies as aggregate because the branch contains SUM at top level of an aggregate expression.

## Refuse to Fabricate

Every classification cites the specific pattern that fired. Never invent a classification. If no pattern fires (unusual, since row-level is the fallback), render as `"unclassified: no pattern matched"` per HC#7 sentinel discipline.
