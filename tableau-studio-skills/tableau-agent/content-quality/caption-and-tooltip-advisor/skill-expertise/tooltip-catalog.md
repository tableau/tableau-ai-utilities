# Tooltip Catalog (T1-T6)

Locked rule set for caption-and-tooltip-advisor. Every Audit finding cites one of these.

## Severity legend

- **FAIL.** Ships broken. Fix before stakeholder sees it.
- **NEEDS ATTENTION.** Works but reads badly. Fix in next revision.
- **PASS.** Reads well.

## T1. Uninformative measure labels

**Severity.** NEEDS ATTENTION.

**Rule.** Axis labels, tooltip rows, or caption references of the form `SUM(X)`, `AVG(X)`, `COUNTD(X)`, `AGG(X)` left in the raw field format rather than rewritten to plain-language headers.

**Evidence signal.** `get-dashboard-xml` tooltip or caption text matches regex `(SUM|AVG|COUNTD?|MIN|MAX|MEDIAN|AGG)\\([^)]+\\)`.

**Rewrite pattern.**
- Executive: `SUM(Sales)` → `Total revenue`.
- Analyst: `SUM(Sales)` → `Sales total` (keep "sales" since the analyst audience knows the term).
- Operations: `SUM(Sales)` → `Sales this period`.
- External: `SUM(Sales)` → `Total sales for the window shown`.

**Desktop step.** Click the field in the viz → Format → Default → Fields → change the alias OR double-click the axis label and type the new label.

## T2. Raw field names in tooltips

**Severity.** NEEDS ATTENTION.

**Rule.** Tooltip templates contain `[FieldName]` placeholders that render verbatim without rewriting to a plain phrase.

**Evidence signal.** `get-dashboard-xml` tooltip template contains tokens matching `\\[.+?\\]` without surrounding plain-language context.

**Rewrite pattern.** Replace `[Order Date]` with "Ordered on," `[Region]` with "Region," `[Customer Name]` with "Customer." Leave the field reference inside Tableau's template syntax but add explanatory text around it: `Ordered on <Order Date>`.

**Desktop step.** Right-click the sheet → Tooltip → Edit Tooltip → rewrite the template inline.

## T3. Missing dashboard-level context caption

**Severity.** FAIL for external and C-suite audiences; NEEDS ATTENTION otherwise.

**Rule.** The dashboard has no caption text explaining what it answers. External and C-suite audiences cannot infer context from field names.

**Evidence signal.** `get-dashboard-xml` returns no caption zone, or the caption zone is empty, on the dashboard root.

**Rewrite pattern.** Compose a 1-2-sentence caption in audience voice: "This dashboard shows [measure] by [dimensions] for [time window]."

**Desktop step.** Dashboard menu → Show Title → Edit Title. Or add a Text zone to the top of the dashboard with the caption.

## T4. Missing worksheet caption on complex views

**Severity.** NEEDS ATTENTION.

**Rule.** A worksheet has 3 or more pills on Rows + Columns combined and no caption. Dense views need captions to orient the viewer.

**Evidence signal.** `get-dashboard-xml` per-sheet pill count on Rows + Columns at or above 3 AND caption-zone text is empty.

**Rewrite pattern.** 1 sentence naming what the chart shows structurally: "Revenue by region, broken out by product category, over the last 4 quarters."

**Desktop step.** Right-click the sheet → Caption → Show Caption. Then edit the caption text in the view.

## T5. Tooltip-field mismatch

**Severity.** NEEDS ATTENTION.

**Rule.** Tooltip references a field the viz does not visually encode (not on any shelf, not on marks card). Shows up as "ghost" data in the hover that does not appear in the chart.

**Evidence signal.** `get-dashboard-xml` tooltip-template fields vs. the sheet's shelf fields. Any tooltip field not on Rows/Columns/Color/Size/Label/Detail is flagged.

**Rewrite pattern.** Either (a) remove the ghost field from the tooltip, or (b) add it to the viz on Detail or Tooltip shelf so it is intentionally encoded.

**Desktop step.** Right-click the sheet → Tooltip → Edit Tooltip → delete the ghost field reference. Or drag the ghost field onto the Tooltip shelf on the Marks card to intentionally include it.

## T6. Placeholder text

**Severity.** FAIL.

**Rule.** Any of the following literal strings appear in dashboard, worksheet, or text-object text:
- "Insert title here"
- "Double-click to edit"
- "Click to add text"
- Default sheet names: `Sheet \\d+`, `Dashboard \\d+`, `Story \\d+`
- "TODO," "TBD," "FIXME," "placeholder"

**Evidence signal.** `get-dashboard-xml` title, caption, or text-zone text matches any of the above (case-insensitive).

**Rewrite pattern.** Replace with real content in audience voice. If the author truly intends an empty slot, hide the title zone instead of leaving placeholder text.

**Desktop step.** Click the title → Edit Title → type real text. Or right-click → Hide Title.

## Rule interactions

- T1 and T2 often fire together on the same tooltip. Rewrite in one pass.
- T3 and T4 are distinct: T3 is dashboard-level, T4 is worksheet-level. Both can fire on the same dashboard.
- T5 can mask T4: if a worksheet has pills only on Marks card (not Rows/Columns), T4 may pass trivially while T5 catches real issues.
- T6 overrides everything else: if placeholder text is present, that is the headline finding regardless of other T-rules.
