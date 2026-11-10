# Complexity Rubric (C1-C6)

Locked 6-factor rubric for inheritance-triage Complexity-score mode. Each worksheet scores 1-10 as the sum of C-factor contributions.

## Scoring summary

| Factor | Max points | Weight |
|---|---|---|
| C1 Mark count | 3 | Density proxy |
| C2 Calc nesting depth | 2 | Dependency complexity |
| C3 Table-calc presence | 1 | Order-of-ops surprise |
| C4 LOD presence | 2 | Granularity-override complexity |
| C5 Filter count | 2 | Interaction surface |
| C6 Cross-DS references | 2 | Multi-source joining |
| **Total** | **12** | Clamped to 1-10 |

Sheets scoring 11-12 clamp to 10. In practice very few sheets hit above 10.

## C1. Mark count

**Scoring.**
- 0 points: under 100 marks.
- 1 point: 100-500 marks.
- 2 points: 500-5000 marks.
- 3 points: 5000+ marks.

**Evidence source.** `get-summary-data` on the worksheet. If not called, author-reported ("about how many marks are on this sheet"). If neither available, default to 1 point and note "unverified mark count."

**Why it matters.** Dense sheets are harder to read and often harder to maintain. The score flags density as a complexity factor, not a quality judgment (HC-8).

## C2. Calc nesting depth of fields used

**Scoring.**
- 0 points: all fields on the sheet are raw data-source fields (no calcs).
- 1 point: at least one calc on the sheet, no nesting (calcs reference only raw fields).
- 2 points: at least one calc on the sheet references another calc (one or more levels of nesting).

**Evidence source.** Parse calc text via `list-available-fields` for each field placed on the sheet (shelves + Marks card). Check whether any referenced calc body contains another calc's name.

**Why it matters.** Nested calcs are the most common source of "I don't know what this calc does" fatigue when inheriting a workbook.

## C3. Table-calc presence

**Scoring.**
- 0 points: no table calcs on the sheet.
- 1 point: at least one table calc on the sheet (quick table calcs count: Running Total, Difference From, Percent Difference, etc.).

**Evidence source.** `get-worksheet-xml` on the worksheet itself. Table-calc pills are marked with a delta glyph in the per-worksheet XML. Note: `get-dashboard-xml` returns zone layout only and does not carry shelf-level pill annotations; use `get-worksheet-xml` for this check.

**Why it matters.** Table calcs operate on viz state, not underlying data. Order-of-operations surprises are common when inheriting a sheet with table calcs.

## C4. LOD presence

**Scoring.**
- 0 points: no LODs on the sheet.
- 1 point: at least one INCLUDE or EXCLUDE LOD on the sheet.
- 2 points: at least one FIXED LOD on the sheet.

**Evidence source.** Parse calc text of each field placed on the sheet. Look for `{FIXED`, `{INCLUDE`, `{EXCLUDE`.

**Why it matters.** LODs override the viz's natural granularity. FIXED is the most powerful and the most confusing to inherit. INCLUDE and EXCLUDE are easier to reason about.

## C5. Filter count

**Scoring.**
- 0 points: under 3 filters on the sheet.
- 1 point: 3-5 filters.
- 2 points: 6+ filters.

**Evidence source.** `get-worksheet-xml` filters-shelf field count on the worksheet. Include quick filters, context filters, and dimension/measure filters. Note: `get-dashboard-xml` returns zone layout only and does not carry filter-shelf data; use `get-worksheet-xml` for this count.

**Why it matters.** More filters means more interaction surface for the next user to reason about. Also indicates the sheet is doing heavy work.

## C6. Cross-DS references

**Scoring.**
- 0 points: all fields on the sheet reference the same data source.
- 2 points: at least one field on the sheet references a data source different from the primary one.

**Evidence source.** `list-available-fields` returns the data source for each field. Compare against the sheet's primary data source.

**Why it matters.** Cross-DS calcs cannot be computed in the database and must run locally. They are a frequent source of performance issues and inheritance surprises.

## Tier boundaries

- **Simple (1-3).** Low interaction surface, raw fields, few filters, no cross-DS. Easy to understand on first read.
- **Moderate (4-6).** Some calcs, maybe one LOD or table calc, moderate filter count. Can be understood in 5-10 minutes.
- **Complex (7-10).** Nested calcs, multiple LODs or table calcs, many filters, possibly cross-DS. Needs a dedicated reading pass.

## HC-8 reminder

A score of 10 does not mean the sheet is bad. Complex sheets are often necessary: a cohort-retention sheet with FIXED LODs, 6 filters, and 20,000 marks will score 10 and still be the right design for its question. The score only tells the inheriting author "this one will take longer to read than the simple sheets."

The output must never say "this sheet is wrong" or "simplify this sheet." It names the complexity for prioritization only.

## Edge cases

- **Hidden sheets.** Score them, flag that they are hidden, and sort to the bottom of the ranked list.
- **Sheets used only in dashboard actions.** Score normally. The inheriting author may need to understand them to understand the dashboard.
- **Empty sheets.** Skip (score N/A). Route to worksheet-cleanup for the actual cleanup.
- **Sheets referencing deleted fields.** Score what can be scored. Flag the broken reference in the output.

## Tie-breaking

If multiple sheets score the same, sort secondarily by:
1. Named-field-count on the sheet (descending; more fields = more things to understand).
2. Alphabetical by sheet name.
