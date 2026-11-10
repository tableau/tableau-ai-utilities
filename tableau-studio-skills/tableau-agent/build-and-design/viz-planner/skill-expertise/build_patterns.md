# Chart-Specific Build Patterns

Shelf recipes for the core chart types. Each pattern defines the exact mark type, field placements, key settings, and formatting. Use these as templates when constructing the worksheet specification.

***

## Line Chart (Temporal)

```
MARK TYPE: Line
COLUMNS: [Date field] | [Date part: MONTH/WEEK/etc.] | Continuous
ROWS: [Measure] | SUM (or appropriate agg)
COLOR: [Segment dimension] (if comparing series; max 6 lines)
PATH: [Date field] (ensures correct line ordering)
```

**Key settings:**
- Line weight: 2-3px
- Single line: primary color (#4E79A7)
- Multiple lines: categorical palette, max 6 series
- Show markers only at endpoints or on hover
- Y-axis: include zero if magnitude matters; exclude if trend shape matters more
- If series count >6: switch to small multiples or highlight-one-dim-rest-gray

**Formatting:**
- Grid lines: horizontal only, light gray (#E0E0E0)
- Axis format: abbreviated ($0K, $0M) for large numbers
- Legend: right side, sorted by final value descending

***

## Horizontal Bar (Comparison/Ranking)

```
MARK TYPE: Bar
COLUMNS: [Measure] | SUM
ROWS: [Dimension]
SORT: [Measure] | Descending (largest at top)
COLOR: Single color (#4E79A7) unless semantic meaning applies
LABEL: [Measure] | end of bar | format: $#,##0 or #,##0
```

**Key settings:**
- Bar size: 60-80% of row height
- If >15 categories: apply TOP N filter (show 10, user can expand)
- If including target: add reference line (dashed, #9C9C9C)
- Row height: enough for labels without truncation
- Single color unless color encodes a meaningful category or status

**Formatting:**
- Hide column header (value is in labels)
- Hide grid lines (bars provide their own reference)
- Row banding: off (clean look)

***

## Stacked Bar (Composition)

**Two dimensions available** (a primary grouping + a sub-breakdown, e.g. Region split by Category):

```
MARK TYPE: Bar
COLUMNS: [Measure] | SUM
ROWS: [Primary dimension]
COLOR: [Secondary dimension] (the parts making up the whole)
SORT: By total value, descending
```

**Single dimension available** (the ask is "breakdown of [measure] by [one dimension]" and there's no second grouping field — e.g. "sales breakdown by category"):

```
MARK TYPE: Bar
COLUMNS: [Measure] | SUM
ROWS: (empty — one single bar)
COLOR: [The one dimension] (segments the single bar into its members)
SORT: By segment value, descending (Tableau default color-sort is fine)
```

Do not invent or add a second dimension (e.g. a sub-category) just to satisfy a two-dimension stacked-bar template. If a `bind-template` call for a stacked-bar template errors or requires a slot you don't have a real second field for, drop to manual shelf authoring (measure on Columns, the one dimension straight onto the Color encoding, nothing on Rows) rather than substituting an unrequested field. If you must add a field the user didn't name, ask first — don't silently apply it.

**Key settings:**
- Max 5-7 color segments (aggregate remainder into "Other")
- Label: show % inside segments >10% of total width
- Baseline segment (leftmost) is most important for comparison
- For proportions over absolutes: use "Percent of Total" table calc on axis

**100% Stacked variant:**
- Same structure, but axis shows 0-100%
- Add table calc: Percent of Total, compute using [Secondary dimension] (or the single dimension, in the one-dimension case)

***

## Scatter Plot (Correlation)

```
MARK TYPE: Circle
COLUMNS: [Measure 1] | SUM (or AVG)
ROWS: [Measure 2] | SUM (or AVG)
DETAIL: [Entity dimension] (what each dot represents)
COLOR: [Categorical dimension] (optional, max 5-6 colors)
SIZE: [Third measure] (optional; creates bubble chart)
```

**Key settings:**
- Trend line: linear, show R-squared value
- Mark opacity: 50-70% if many overlapping points
- Axis labels: clear metric names (not "SUM(field1)")
- For 4-quadrant analysis: add reference lines at averages on both axes
- Mark size: small enough to see density, large enough to hover

**Answering "is there a relationship" specifically:** a scatter needs one point per detail-grain member (order, customer, transaction) to show a real relationship — aggregating to a handful of category totals collapses the pattern to a few dots and answers nothing (see Phase 5 question-answered check in `SKILL.md`). Add the trend line (no tool path — give the user the manual Analytics pane → Trend Line step) as the default strengthening move for this question type; offer an R²/correlation annotation as the next step up.

**Formatting:**
- Show both axes, labeled clearly
- Grid lines: both directions, subtle
- Zero lines: show if data crosses zero

***

## KPI Tile (Status)

```
MARK TYPE: Text (primary value)
TEXT: [Measure] | SUM | Format: large number
```

**Building a complete KPI tile (multi-sheet approach):**

Sheet 1 (Value):
- Mark: Text
- Text: SUM([Measure]), formatted large and bold
- Filter: current period

Sheet 2 (Comparison):
- Mark: Text
- Text: [Change %] calc, formatted with arrow (up/down) and color
- Color: by status (green = good, red = bad)

Sheet 3 (Sparkline):
- Mark: Line
- Columns: [Date] continuous
- Rows: [Measure] SUM
- Hide all axes, headers, gridlines
- Fixed axis range for consistent shape

**Calculated fields needed:**
- `[KPI Value]`: SUM([Measure]) filtered to current period
- `[Prior Period]`: SUM([Measure]) filtered to comparison period
- `[Change %]`: ([KPI Value] - [Prior Period]) / ABS([Prior Period])
- `[Status]`: IF [Change %] >= 0 THEN "On Track" ELSE "Alert" END

**Status encoding (non-negotiable):**
- Color + icon + text label (triple encoding)
- Never color alone

**Highlight-box variant (Square shape, background-matched):** for a plain single-number KPI tile (no status color needed), use a maximized Square mark colored to match the dashboard background instead of a bare Text mark — it gives the number a full-bleed highlight card with no visible shape outline. Requires manual XML edit (no `bind-template` template covers this); see `skill-expertise/kpi_highlight_box.md` for the exact worksheet XML pattern (mark-sizing, mark-color, cell text/vertical alignment). Do not combine with the triple-encoding status rule above — this variant is for value-only KPIs, not status tiles.

***

## Histogram (Distribution)

```
MARK TYPE: Bar
COLUMNS: [Measure] | BIN (create bin of appropriate size)
ROWS: COUNT or CNTD([Entity])
COLOR: None (single color) or [Category] for side-by-side distributions
```

**Key settings:**
- Bin size: start with (max - min) / 10; adjust for readability
- Y-axis: always count or frequency
- No gaps between bars (this distinguishes histogram from bar chart)
- Add reference line at median or average (labeled)
- X-axis: show bin boundaries

**Build path — do NOT default to `bind-template`'s `distribution-histogram` template.** That template's bin calc is hardcoded to `Profit` in this environment (a `DATASET_SPECIFIC_FORMULA` fast-path blocker) — it will error (`missing-required-slot 'measure' (Profit)`) for any other field, including the obvious case of literally binning `Profit` itself if the dataset differs. Go straight to manual build:

1. Check the real min/max of the measure first (put MIN/MAX on a throwaway detail/tooltip encoding and read with `get-summary-data`, or reason from `list-available-fields` if the range is obviously small/discrete). Don't guess a bin size blind.
2. If the measure is a small-range discrete integer (e.g. order quantity 1-14), bin width 1 is correct and the "bin" is just the value itself — author a dimension calc via `author-calc` with `role: dimension`, formula `FLOOR([Measure])` (or `FLOOR([Measure]/binwidth)*binwidth` for a real bin width), caption e.g. "[Measure] Bin".
3. Resolve the new calc's `column_ref` (it will be `[none:Calculation_XXXX:ok]` — an ordinal dimension instance), put it on Columns, and put `[cnt:Entity:qk]` (or `[cntd:Entity:qk]`) on Rows via `add-field` + `apply-worksheet`.
4. Verify with `get-summary-data` on the two fields before reporting done — one row per bin value, monotonic bin axis, plausible counts.

**Creating the bin:**
- Right-click measure → Create → Bins (UI path, if not doing it programmatically)
- Set size based on data range and meaningful groupings
- Name the bin clearly: "[Measure] (Binned)"

***

## Map (Geographic)

```
MARK TYPE: Map (filled) for choropleth, Circle for point map
DETAIL: [Geographic dimension] (auto-generates lat/long)
COLOR: [Measure] | Sequential palette (single hue, light to dark)
SIZE: (point maps only) [Measure]
LABEL: (optional) [Geographic dimension] for key regions only
```

**Key settings:**
- Sequential palette: blues (#c6dbef → #08519c) — accessible, intuitive
- Never use rainbow color scale
- If <5 regions in dataset: switch to bar chart (more precise reading)
- Include borders between regions
- Tooltip: region name + value + rank

**Formatting:**
- Hide map background layers if not needed (coastlines, terrain)
- Zoom to data extent
- Legend: show color scale with min/max values labeled

***

## Bullet Chart (vs. Target)

```
MARK TYPE: Bar (layered approach)
COLUMNS: [Actual measure] | SUM
ROWS: [Category dimension]
REFERENCE LINE: [Target value] | per cell | short marker line
```

**Build approach (simplified):**
1. Bar for actual value (narrow, dark primary color)
2. Reference line for target (short vertical tick, black or dark gray)
3. Optional: background shading for performance zones (light gray bands for bad/ok/good ranges)

**Alternative (single-mark approach):**
- Gantt bar from 0 to actual
- Reference line at target
- Color by: above/below target (green/red with icon)

**Key settings:**
- Bar width: narrow (30-40% of row)
- Reference line: prominent but not overwhelming
- Sort: by actual value or by gap-to-target (user preference)

***

## Heatmap / Highlight Table (Two Dimensions × One Measure)

**Clarify first — "heatmap" is ambiguous.** When the ask is "heatmap of [measure] by [dim A] and [dim B]," people commonly mean a **highlight table** (numeric value shown per cell, shaded by color intensity), not a color-only grid with no labels. Ask which one before building unless already specified: "Highlight table (numbers + color)" vs. "Pure heatmap (color only, no numbers)."

**No dedicated crosstab template exists.** `bind-template` misroutes this ask (e.g. to `trend-line-chart`), and the only heatmap-named template (`change-over-time-calendar-heatmap`) is a year×month calendar heatmap that drops any additional categorical dimension. Build manually:

```
MARK TYPE: Square
ROWS: [Dimension A] (discrete)
COLUMNS: [Dimension B] (discrete, e.g. Month — use a Month-Trunc/Month-part CI, not exact date)
COLOR: [Measure] | SUM
TEXT: [Measure] | SUM (highlight-table variant only — omit for a pure color-only heatmap)
```

**Build steps:** scaffold via any two-field template (e.g. `magnitude-simple-bar` with dimension A + measure), then hand-edit the worksheet XML — add dimension B's column def/column-instance, set `<mark class="Square">`, put each dimension on its own shelf (rows/cols), and encode the measure on `color` (+ `text` and `mark-labels-show`/`mark-labels-cull` format attrs for the highlight-table variant). Remove any stale title/axis-title text left over from the scaffold template. Verify cell count via `get-summary-data` — rows × cols members should equal the returned row count.

***

## Small Multiples (Faceted Trend, One Panel Per Category)

**Use when:** the ask explicitly wants separate panels per category (small multiples), not one shared axis with overlaid colored lines. Distinguish from a plain multi-series line chart (color-encoded, single panel) — small multiples create actual separate panes.

```
MARK TYPE: Line
COLUMNS: [Date field] | Month-Trunc, continuous   (small multiples across columns)
ROWS: [Facet dimension] * [Measure]                (small multiples down rows — nest with add-field)
```

- **Facet across columns** (side-by-side panels): keep the date field on Columns, and place `([Facet dimension] * [Date field])` on... actually the working shape is Rows = `[Measure]`, Cols = `([Facet] * [Date field])` — the two different fields on the same shelf, joined by `*`, create separate panes per facet member, in facet-then-date column order.
- **Facet down rows** (stacked vertically, one panel per category): swap the shelves — Cols = `[Date field]` only, Rows = `([Facet dimension] / [Measure])` (nesting a dimension then a measure on rows uses `/` — confirmed via `add-field`'s own generated XML, not `*`). Build the plain trend chart first, then use `add-field` to append the facet dimension to whichever shelf (rows or cols) should carry it — the tool generates the correct `*`/`/` operator; don't guess it by hand. Wrap the final expression in parentheses if hand-editing: `([DS].[none:Facet:nk] / [DS].[sum:Measure:qk])`.
- **Verify row/column orientation** via `get-summary-data` (facet member × time period count) before reporting done — an `add-field` or `bind-template` result claiming a field was "silently dropped" on this kind of shelf edit is not always accurate; confirm with real data either way.
- A `bind-template` call using an optional `color_series`/`facet_col` slot can land the facet dimension on BOTH the color encoding AND the axis shelf (via `*`), producing small multiples when the ask actually wanted one overlaid chart with colored lines — check the readback and strip the dimension from rows/cols (keep only the color encoding) if that's not what was asked for.

***

## Reference Lines (Average, Median, Target)

**Confirmed correct `<reference-line>` shape** (pane-level, sibling of `<mark>`) for a simple average line:

```xml
<reference-line axis-column="[DS].[sum:Measure:qk]" enable-instant-analytics="true"
  formula="average" id="refline0" label-type="automatic" probability="95"
  scope="per-table" value-column="[DS].[sum:Measure:qk]" z-order="1"></reference-line>
```

Key gotchas (each one silently failed on a first guess and only surfaced by diffing Desktop's own output):
- `formula="average"` — **not** `"avg"`.
- `value-column` references the **same CI** as `axis-column` — no separate avg-derivation column-instance is needed; Tableau computes the aggregation from `formula` alone.
- `label-type="automatic"` shows the computation name (e.g. "Average"); `label-type="value"` shows the computed number instead — both are valid, pick based on what's asked.
- `probability="95"` is present even for a plain average line (harmless to include).
- `scope="per-table"` for one global line; `scope="per-cell"` for an independent line per facet/panel (e.g. small multiples — one average per panel, not one line across all panels).
- Swap `formula` for `"median"`, `"sum"`, `"total"`, etc. for other simple reference lines, keeping `value-column` equal to `axis-column` in all cases.

**Dash/dot line style** — a separate, also-confirmed-the-hard-way gotcha:

```xml
<style-rule element="refline">
  <format attr="line-visibility" id="refline0" value="on"></format>
  <format attr="line-pattern-only" id="refline0" value="dashed"></format>
</style-rule>
```

`attr="line-pattern-only"` — **not** `"line-pattern"` (that attribute name round-trips as valid XML but silently does nothing). Both attributes key to the same reference line `id`. Values seen: `"dashed"`; verify `"dotted"`/`"solid"` against a live diff if requested and not confirmed here yet.

**Bottom-N filter (for a ranked bar/table showing the worst/lowest N, not the top N):** use `end="top"` with the nested order's `direction="ASC"` — **not** `end="bottom"`. There is no working `end="bottom"`; it silently behaves as if unfiltered (same rows as a Top-N sheet) rather than erroring. "Top of the ascending-sorted list" is how Tableau expresses bottom-N. Always verify a Top-N/Bottom-N filter against real `get-summary-data`, not just a clean apply message.

***

## Column Chart (Discrete Time Periods)

```
MARK TYPE: Bar
COLUMNS: [Date field] | Discrete (QUARTER, YEAR, etc.)
ROWS: [Measure] | SUM
COLOR: Single color or [Category] for grouped
SORT: Keep chronological (do not sort by value)
```

**Key settings:**
- Use when time periods ≤8 and comparison between specific periods is the point
- Gap between bars: 40-60% of bar width
- Label: show values on top of each bar
- If comparing to prior period: use paired color (solid = current, lighter = prior)

***

## General Formatting Rules (All Charts)

| Element | Default |
|---|---|
| Title | Descriptive, answers "what am I looking at?" — not "Sheet 1" |
| Subtitle | Time context, filter state, or data source info |
| Axis labels | Clear metric names, abbreviated if large (K, M, B) |
| Grid lines | Minimal (horizontal only for most; both for scatter) |
| Borders | None on marks; light on containers |
| Background | White (#FFFFFF) |
| Font | Tableau default or brand font; never decorative |
| Null handling | Hide or call out explicitly (never leave unexplained gaps) |

***

## Performance Considerations

| Scenario | Risk | Mitigation |
|---|---|---|
| >1M rows, live connection | Slow rendering, potential timeout | Suggest extract; or aggregate to higher grain (week instead of day, category instead of product) |
| >10K marks on a single chart | Visual overload + performance | Apply TOP N filter, aggregate, or switch to density/heatmap approach |
| Complex LOD in tooltip | Slow tooltip render | Move LOD to a pre-calculated field or remove from tooltip |
| Multiple independent filters | Each adds a query round-trip | Consolidate using parameters where possible |
| Map with high-cardinality points | Slow pan/zoom, overlapping marks | Aggregate to higher geo level (state instead of city); use clustering |

**Rule of thumb:** If the chart will produce more marks than the user can visually distinguish, aggregate. No one reads 50,000 dots on a scatter plot.
