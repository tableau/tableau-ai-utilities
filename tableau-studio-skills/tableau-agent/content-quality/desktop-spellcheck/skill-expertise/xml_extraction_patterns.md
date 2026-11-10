# XML Extraction Patterns

Where each text category lives in a Tableau `.twb` or `.twbx` file. Use this when Tier 1 (MCP tools) fails and you fall back to disk parsing.

## File structure primer

- A `.twb` is raw XML.
- A `.twbx` is a ZIP archive. Inside it, the `.twb` lives at the root (name matches the file, extension `.twb`). Unzip first, then parse.

To unzip a `.twbx` from bash:
```
unzip -q workbook.twbx -d unpacked/
```

The `.twb` is at `unpacked/<workbook-name>.twb`.

## Text category → XML location

| Category | XPath-equivalent | Attribute or child |
|---|---|---|
| Worksheet title | `//worksheet[@name='X']/layout-options/title/formatted-text/run` | text() of `<run>` |
| Worksheet caption | `//worksheet[@name='X']/layout-options/caption/formatted-text/run` | text() of `<run>` |
| Dashboard title | `//dashboard[@name='X']/layout-options/title/formatted-text/run` | text() of `<run>` |
| Dashboard text object | `//dashboard[@name='X']//zone[@type='text']/formatted-text/run` | text() of `<run>` |
| Tooltip text | `//worksheet[@name='X']//tooltip/formatted-text/run` | text() of `<run>` |
| Annotation text | `//worksheet[@name='X']//annotation/formatted-text/run` | text() of `<run>` |
| Field alias | `//datasource//column[@caption]` | `@caption` attribute |
| Calc name | `//datasource//column[@calculation][@caption]` | `@caption` attribute |
| Parameter display name | `//datasource[@name='Parameters']//column[@caption]` | `@caption` attribute |
| Parameter value labels | `//datasource[@name='Parameters']//column//alias` | `@value` attribute |

## Formatted-text quirks

- Text runs are frequently split across multiple `<run>` elements when the user applied formatting mid-string. Concatenate all sibling `<run>` text content in document order to reconstruct the visible string.
- Trailing `<run/>` with no text content is common; ignore.
- `<run>` may contain HTML entities (`&amp;`, `&lt;`, `&#8217;`). Decode before running the dictionary check.
- Curly quotes are stored as their literal Unicode characters, not as entities. Preserve them for the typography drift check.

## Field aliases specifically

The `<column>` element inside a datasource has two relevant attributes:

- `name` — the internal Tableau name, wrapped in brackets (e.g., `[Customer Segment]`). NOT user-facing.
- `caption` — the user-facing rename. This is what to check.

Only `caption` is stakeholder-visible. Skip `name`.

## Dashboard-bound worksheet detection

Sheets that are placed on any dashboard are "dashboard-bound." These are the sheets where `get-worksheet-xml` documented as flaky. Detect them by:

```
//dashboard//zone[@name] → the @name values are the dashboard-bound sheets
```

When Tier 1 fails, you can predict this list up front and go straight to Tier 2 for those sheets.

## What NOT to extract

- `<column name="...">` — internal names, not user-visible
- `<column-instance>` `@caption` fields that duplicate a parent column's caption already checked — do not double-count
- Field/column **descriptions** (the `desc` child element on a `<column>`, shown in the Data pane hover, not a category in Step 1) — never scan or report on these, even though they contain natural-language text
- Anything inside `<style>` blocks — formatting metadata
- `<repository-location>` — server paths
- `<connection>` blocks — connection strings, credentials, paths
- Any element under `<preferences>` — user prefs, not workbook content

## Two-tier decision logic

```
For each worksheet W in inventory:
  If W is dashboard-bound:
    Try get-worksheet-xml(W)
    If fails:
      Add W to "needs disk fallback" list
    Else:
      Extract text via XML tool response
  Else (standalone):
    Use get-worksheet-xml(W). This path is reliable.

For each dashboard D in inventory:
  Try get-worksheet-xml(D)
  If fails:
    Add D to "needs disk fallback" list

If "needs disk fallback" list is non-empty:
  Ask user for .twb or .twbx file path (once).
  If provided: unzip if needed, parse XML directly for all entries in the list.
  If not provided: mark all entries as "Not Scanned" in the report.
```

## Encoding

Tableau writes UTF-8. When reading from disk, open with `encoding='utf-8'`. Some older workbooks use `utf-8-sig` (BOM). If UTF-8 fails, retry with `utf-8-sig` before giving up.
