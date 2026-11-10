# Worksheet Builder

Turns a natural language request into a fully specified Tableau worksheet. Given a question like "show me sales by region over time," it fetches the datasource metadata, picks the right chart type, validates against 15 anti-patterns, and either produces a shelf recipe or builds the worksheet directly in Desktop.

**Example:** "Build a chart showing profit by category for 2024" returns a horizontal bar with Category on Rows (sorted by SUM(Profit) descending), a Year filter defaulted to 2024, a reference line for average profit, and a numbered click-by-click build path if you want it.

***

## What it does

Takes one question at a time and produces one worksheet, precisely. Not a dashboard, not a critique, not a survey of options. It parses your ask into a question type (temporal, ranking, composition, correlation, and six others), classifies your fields, picks the chart the decision framework says fits, runs the anti-pattern gate, and hands you either a shelf recipe or an actual built worksheet.

Opinionated by design. It picks the best chart and explains why in one sentence. If you disagree, say so and it rebuilds.

## When to use it

- "Build a chart showing [metric] by [dimension]"
- "What chart should I use for [question]"
- "Make me a scatter of profit vs. discount"
- "I need a KPI tile for Q3 sales vs. target"
- "Show me top 10 customers by revenue"

## When NOT to use it

- Not for dashboard layout or assembling multiple sheets (use viz-planner)
- Not for critiquing or scoring an existing viz (use a viz critique skill)
- Not for writing a standalone calculated field with no chart around it (use calc-writer)
- Not for data quality profiling, nulls, or field hygiene (use data-quality-review)
- Not for creating parameters (that's the built-in Studio authoring skill's job (`tableau-desktop-authoring`, not part of this repo); `author-parameter` is also documented as broken on Windows)

## How to trigger it

- "Build a chart"
- "Make a worksheet"
- "Show me [metric] by [dimension]"
- "What chart should I use for [question]"
- "Chart for [question]"
- "Worksheet builder"

## What you'll need

- Tableau Studio with a datasource actively connected
- The MCP tools Worksheet Builder uses: `list-available-fields`, `resolve-field`, `bind-template`, `refine-worksheet`, `add-field`, `remove-field`, `build-and-apply-worksheet`, `author-calc`, `get-worksheet-xml`, `get-summary-data`
- If your build needs a parameter, that parameter must already exist. Worksheet Builder will not create one; it names what's needed and defers.

## Example walkthrough

**Input:** "Show me profit by sub-category, colored by category, for 2024 orders in the West region."

**Output (Shelf Recipe mode):**

```
WORKSHEET: Profit by Sub-Category, West 2024
MARK TYPE: Bar
BUILD PATH: bind-template (magnitude-simple-bar)

COLUMNS: SUM([Profit])
ROWS:    [Sub-Category]
COLOR:   [Category] | Qualitative (5-category palette)
LABEL:   SUM([Profit]) | $#,##0
TOOLTIP: Sub-Category, Category, SUM(Profit) with $ format,
         % of total profit within Category

FILTERS:
  [Order Date] | Year | 2024
  [Region]     | Single value | West

SORT: [Sub-Category] by SUM([Profit]) descending
REFERENCE LINE: Average of SUM([Profit]) per pane, dashed gray

FORMATTING:
  Axis: $#,##0K abbreviated
  Row banding: off
  Grid lines: light gray, minor only

Anti-pattern check: passed. Sort is by value, color is purposeful,
category count = 3 (well under 7-category limit), status not encoded.
```

Followed by: "Want me to build this now, or adjust anything first?"

Click-by-Click mode returns the same result as a numbered 5-8 step sequence with every field name, shelf, and dropdown bolded so it's scannable at a glance.

## What you get back

- **Two output modes:** Shelf Recipe (Mode A, concise, field placements + mark type + calcs) or Click-by-Click (Mode B, step-by-step UI instructions). Worksheet Builder asks which you prefer on first use and remembers your choice.
- **Chart chosen deterministically.** Question type + field conditions map to one chart via the decision framework, not a menu of options.
- **Anti-pattern gate** on every build. Critical anti-patterns get replaced automatically. High severity gets a warning with an offered alternative. Medium gets a note.
- **Audience overrides** when the ask mentions a role. Executive suppresses scatter and box plots. Analyst suppresses gauges. And so on.
- **Complete color and accessibility handling.** WCAG AA contrast, max 7 categorical colors, status encoded with shape + color + text (never color alone).
- **Post-build verification.** After every build, mark type, axes, and one data point get checked. If the ask named a comparison ("vs. last year"), the comparison encoding is verified as its own field, not silently dropped.
- **Question-answered check.** Beyond "here's your chart," Worksheet Builder states in plain language whether the chart actually answers the question, names what to look at, and offers 1-2 concrete ways to strengthen the chart for that specific question type.

## Limitations

- **One worksheet per request.** Multiple questions get multiple sequential builds, not one combined chart.
- **Does not create parameters.** If the build needs a user-adjustable parameter, Worksheet Builder names it, describes its values, and defers to the built-in Studio authoring skill (`tableau-desktop-authoring`) for creation, or gives the manual steps in Tableau if it is not available. `author-parameter` is documented as broken on Windows.
- **Does not create Sets that need Set semantics.** For simple IN/OUT splits, Worksheet Builder prefers a calculated field (fully verifiable). For genuine Set semantics (Set actions, Show/Hide), it hands you manual Desktop instructions rather than calling `author-set`, which produces placeholder objects the tools can't see back into. Top-N sets are documented as broken (red invalid-field indicator natively in Desktop) and Worksheet Builder builds a RANK-based table calc instead.
- **Filter shelf and context filters require manual steps.** No `add-field` target reaches the Filters shelf and no command promotes a filter to context. Worksheet Builder gives the exact drag-and-right-click instructions rather than pretending it applied them.
- **Dual-axis with two different measures needs one manual click.** The tools can produce the marker but not the merge; Worksheet Builder explains the gap and gives the one-click step.
- **Number formatting with up/down arrows via custom format string is a known weak spot.** Worksheet Builder uses a discovery-then-replicate workflow (diff Desktop's own XML output after a manual edit) rather than guessing attribute names.
- **Hard cap after two identical failed attempts.** If the same build fails twice with identical output, Worksheet Builder stops retrying and hands you manual Desktop instructions rather than burning turns.

## Troubleshooting

- **"I can't find a field called '[name]'."** Field names are case-sensitive and may include qualifiers ("Sales Amount [USD]"). Worksheet Builder suggests the closest match from `list-available-fields`. Accept, correct, or ask it to create a calculated field.
- **"Every build is failing with the same long preflight error list."** Could be workbook corruption OR a static/cached error list from a validator bug (confirmed 2026-08-05 on Superstore). Worksheet Builder runs a cross-datasource test before concluding corruption. If the error is identical byte-for-byte across unrelated datasources, it's a tool bug and manual Desktop editing is the workaround.
- **"The tool says a field was silently dropped, but it looks fine."** This warning is a documented false negative. Worksheet Builder verifies real state with `get-worksheet-xml` or `get-summary-data` before rebuilding. If the readback confirms the field is missing, only then is it actually broken.
- **"The scatter/pie collapsed my thousand orders into five dots."** `bind-template`'s auto-classify treated your color dimension as an aggregation key. Rebuild with a row-level identifier (e.g. Order ID) on Detail so marks don't collapse. Worksheet Builder verifies mark counts on scatter/correlation and "colored by X" builds now.
- **"The template rejected my COUNTD."** Confirmed platform gap on fast-path templates (kpi-text, magnitude-simple-bar). Worksheet Builder authors a helper calc that's literally the number `1`, then uses SUM of that helper — same result, no kind-mismatch.
- **"Refinement (top-N, sort) errors out on my calculated measure."** The refinement tool's splice only handles native-field sort/top-N XML. For calc-backed measures, Worksheet Builder hands you the manual Desktop steps (right-click axis pill → Sort, or drag dimension to Filters → Top tab).
- **"An `apply-worksheet` call hung."** Desktop is blocked on a dialog. Dismiss the dialog before retrying. Worksheet Builder does not retry against a still-blocked dialog; it will ask you to confirm the dialog is closed first.

## Support

File issues in the same channel you use for other Tableau Studio skill feedback. Include the exact request text, the datasource, the chart type Worksheet Builder chose, and what went wrong.
