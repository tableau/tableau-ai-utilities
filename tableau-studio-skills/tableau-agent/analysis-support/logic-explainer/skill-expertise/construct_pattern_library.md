# Construct Pattern Library

Reference lookup for Tableau construction patterns. Two sections:

- **Section A — Chart-Shape Idioms.** Three-layer hierarchy for recognizing what a view is *doing* visually. Identify Layer 0 first, always; Layers 1 and 2 modify or extend that backbone.
- **Section B — Construct Patterns.** Common LOD, table calc, filter, action, set, and dynamic zone visibility shapes and their typical "why." Consult after Section A to explain the mechanics behind the idiom.

Match idioms by **structural fingerprint** (mark type, shelf contents, function combinations), never by field name. Names vary too much across authors to fingerprint reliably. A calc named `Keep Companies` is a *narrative seed*, not a match key.

When a view matches nothing below, say so plainly and fall back to a literal shelf description. A low-confidence honest answer beats a confident wrong one.

When a real pattern is missing, add it here in the same format rather than solving it inline.

***

# Section A — Chart-Shape Idioms

## Layer 0 — Foundational chart types

### Bar / column chart
**Fingerprint:** One discrete dimension on one axis (rows or columns), one continuous measure on the other, mark type Bar.
**Reads as:** Ranks or compares a measure across discrete categories. Orientation just follows which shelf holds the dimension.
**Template:** "compares [measure] across each [category]" (+ ", sorted by [sort basis]" if a sort is applied)

### Single trend line
**Fingerprint:** One continuous date/period on one axis, one continuous measure on the other, mark type Line, no color-splitting dimension (or a single member only).
**Reads as:** How one measure moved over time. No cross-entity comparison.
**Template:** "shows how [measure] has changed over [timeframe]"

### Multi-line trend (raw, not normalized)
**Fingerprint:** Same as single trend, plus a color-legend dimension producing multiple lines, and *no* normalization formula (raw SUM/AVG, not divided by window min/max).
**Reads as:** Direct side-by-side trend comparison across entities at raw magnitude.
**Template:** "compares [measure] trends across [entities] directly, at actual scale"

### Scatter plot
**Fingerprint:** Two continuous measures, one per axis, mark type Circle/Shape, typically with a dimension on Detail or Color for point identity.
**Reads as:** Relationship between two measures at the individual [entity] level. Looks for correlation, clusters, outliers.
**Template:** "plots [measure A] against [measure B] for each [entity], to surface relationships or outliers"

### Cleveland dot plot
**Fingerprint:** Categorical dimension on rows, continuous measure via point/circle marks (not bars), sometimes two point series per row (before/after).
**Reads as:** Bar-chart intent decluttered for many categories, or emphasizing precise point values. Two series shows two values per category at once.
**Template:** "compares [measure] across [category] using point position rather than bar length" (+ ", showing [A] versus [B] per category" if two series)

### Area chart
**Fingerprint:** Mark type Area/Polygon, continuous date/period axis, measure, often with a color dimension producing stacking.
**Reads as:** Shows a total\'s trend over time and how each component contributes to it simultaneously.
**Template:** "shows how [measure] has changed over [timeframe], broken into [components]" (drop component clause if not stacked)

### Table / crosstab
**Fingerprint:** No shape/line/bar mark encoding. Dimensions on both rows and columns, measures rendered as Text, mark type Automatic/Text.
**Reads as:** Built for precise value lookup and cross-referencing exact numbers, not visual pattern recognition.
**Template:** "a lookup table of [measure] by [row dimension] and [column dimension], for exact values rather than visual comparison"

### Geographic map (single layer)
**Fingerprint:** A field with a Geographic role (or generated Latitude/Longitude), mark type Map/Automatic, measure encoded via color or size.
**Reads as:** Spatial distribution of a measure across a geography.
**Template:** "shows the spatial distribution of [measure] across [geography]"

***

## Layer 1 — Composite idioms (modify a Layer 0 base)

### Trellis / small multiples
**Fingerprint:** Two calculated fields on rows and columns built from index()/size() (e.g. `int((index()-1)/round(sqrt(size())))` and `(index()-1)%(round(sqrt(size())))`), arranging one entity per panel.
**Reads as:** The Layer 0 chart repeated once per entity in a grid, for side-by-side scanning instead of overlay.
**Template:** "...shown as a grid of one panel per [entity], for side-by-side comparison"

### Shape-normalized trend comparison
**Fingerprint:** Measure computed as `SUM([value]) / (WINDOW_MIN(SUM([value])) + WINDOW_MAX(SUM([value])))` or similar division against the window\'s own min/max.
**Reads as:** Rescaled so viewers compare trajectory and shape, not absolute magnitude. Useful when entities differ by orders of magnitude.
**Template:** "...normalized so trajectory is comparable despite [entities] differing widely in scale"

### Sparkline endpoint labeling
**Fingerprint:** A label field gated by `WINDOW_MIN(MIN([date]))=MIN([date])` OR `WINDOW_MAX(MAX([date]))=MAX([date]))` so only first/last points get a value label.
**Reads as:** Minimal sparkline convention. Uncluttered line, start/end values readable without a full axis.
**Template:** "only start and end values are labeled, so net change is readable without a full axis"

### Reference / anchor entity
**Fingerprint:** Categorical/color-legend calc with a hardcoded branch pinning one specific member to a fixed bucket, distinct from the logic governing every other member.
**Reads as:** One entity (often the author\'s own org, or a benchmark) is always shown regardless of filter/selection state. Fixed point the rest of the comparison is measured against.
**Template:** "[anchor entity] is always shown as the reference point, regardless of what else is selected"

### Selectable peer / comparison set
**Fingerprint:** A string parameter/calc using CONTAINS/REPLACE to toggle delimited membership (e.g. `|BAC||WFC||`), often with a selection-count cap.
**Reads as:** Interactive peer comparison. The viewer adds/removes entities up to some limit, rather than a fixed list.
**Template:** "the viewer can choose which [entities] to compare, up to [N] at a time"

### Growth / net-change badge
**Fingerprint:** FIXED LOD computing (value at max period − value at min period) / value at min period, formatted with directional glyphs, shown as text on a shape/annotation mark.
**Reads as:** Headline growth-rate number per entity, alongside (not replacing) the trend line.
**Template:** "headlined by total percent change over the period, with the trend line showing the shape behind it"

### Percent-of-total
**Fingerprint:** Measure divided by a TOTAL() or `{FIXED : SUM(...)}` grand-total expression, usually formatted as a percentage, often on a bar or stacked mark.
**Reads as:** Each category\'s share of a whole, not its absolute value.
**Template:** "shows each [category]\'s share of total [measure], not the absolute amount"

### Top-N with "Other" bucket
**Fingerprint:** A RANK()/INDEX() table calc gating which member names display, with an IF rank > N THEN \'Other\' collapsing the remainder.
**Reads as:** Focuses attention on the leading N entities while still accounting for the full total via a catch-all.
**Template:** "highlights the top [N] [entities] by [measure], with everything else rolled into an Other bucket"

### Reference line / band (statistical)
**Fingerprint:** A reference line, band, or distribution band defined on the axis (target, average, std-dev), independent of any specific member. This is a statistical marker, not the pinned-member anchor idiom above.
**Reads as:** Gives the viewer a threshold or benchmark to judge values against without needing a second full comparison series.
**Template:** "values are shown against a [target/average/band] reference so you can judge them without a separate comparison series"

### Parameter-driven measure swap
**Fingerprint:** A parameter feeding a CASE/IF that changes which underlying measure is displayed. Same chart shape, swappable subject.
**Reads as:** One chart shape built to answer several related questions. Viewer picks the measure via a control rather than the author building separate sheets.
**Template:** "the viewer can swap which measure this shows via a control, using the same chart shape for [list of swappable measures]"

### Tiered classification / status badge
**Fingerprint:** A CASE/IF chain sorting entities into named segments (not raw values) shown via color or shape, often 3-5 discrete tiers.
**Reads as:** Segments entities into named performance/status tiers rather than showing continuous values directly.
**Template:** "classifies each [entity] into a status tier ([tier names]) based on [measure/logic], rather than showing raw values"

### Heatmap / matrix
**Fingerprint:** Two dimensions (rows and columns) with a measure encoded purely via color/shading intensity, mark type Square/Automatic, no bar or line marks.
**Reads as:** Surfaces magnitude patterns across two dimensions at a glance. Meant to be scanned for hot/cold spots, not read for exact values.
**Template:** "shows [measure] intensity across [row dimension] by [column dimension], for spotting patterns rather than reading exact values"

### Waterfall / bridge
**Fingerprint:** A running-total calc (RUNNING_SUM) combined with a Gantt/bar mark type, positive/negative segments colored distinctly, connecting a start value to an end value through intermediate steps.
**Reads as:** Explains how a total moved from a starting point to an ending point through discrete contributing changes.
**Template:** "bridges from [starting value] to [ending value], showing each contributing change along the way"

### Dual-axis / bullet / variance (actual vs. target vs. budget)
**Fingerprint:** Two measures on the same axis via dual-axis or a bullet-graph construction (bar + reference line/tick for target), often with a variance calc (actual − target) driving color.
**Reads as:** Directly compares an actual result against a target or budget, with the gap itself often the point.
**Template:** "compares actual [measure] against [target/budget], with color highlighting whether it\'s ahead or behind"

### Geographic map, multiple layers
**Fingerprint:** More than one map layer (background/reference plus point plus polygon), via Tableau\'s map-layers feature or a dual-axis map construction.
**Reads as:** Combines spatial distribution of a primary measure with additional context layers (branch points over regional shading, etc.).
**Template:** "shows [primary measure/entity] positioned over [context layer], so location relative to [regional context] is visible"

***

## Layer 2 — KPI family (base + modifier)

### KPI base
**Fingerprint:** No dimension breakdown on rows/columns, a single aggregated measure on Text, minimal or no axis.
**Reads as:** A headline number meant to be scanned in under a second. Usually one tile in a larger dashboard.
**Template:** "a single headline number for [measure]"

Modifiers below extend the KPI base rather than replacing it. Combine the base template with the relevant modifier clause.

- **+ trend line** — small embedded line mark alongside the number. Adds: "..., backed by its recent trend so you see trajectory as well as the current value"
- **+ bar chart** — small embedded bar marks (period-over-period or category comparison) alongside the number. Adds: "..., with a quick bar comparison against [periods/categories]"
- **+ shape indicator** — a shape encoding tied to a sign/threshold calc (up/down arrow driven by `IF [delta] > 0`). Adds: "..., with a directional indicator showing whether it\'s up or down"
- **+ reference band/shading** — background shading or distribution bands driven by thresholds (traffic-light convention), condensing a bullet-graph-style read into one tile. Adds: "..., shaded to show whether the value falls in an acceptable range"

***

## Adding a new idiom

State which layer it belongs in (Layer 0 if nothing else could describe the chart without it, Layer 1 if it modifies a Layer 0 base, Layer 2 if it\'s a KPI variant), then use the same Fingerprint / Reads as / Template format. Favor fingerprints built from function combinations and shelf structure over field names.

***

# Section B — Construct Patterns

Match the construct\'s *shape* (syntax pattern) before applying a stock rationale. A `RANK()` used for a color threshold, not a leaderboard, still needs its own explanation. Adapt every stock rationale to the actual field names and view context on the sheet. Never paste a row from this table verbatim as the explanation.

## LOD Calculations

| Pattern | Shape | Typical Why |
|---|---|---|
| FIXED at coarser grain than the view | `{FIXED [Dim]: AGG(...)}` where `[Dim]` is coarser than what\'s on Rows/Cols | Computes a value independent of the view\'s filters/grain. Common for "grand total," "customer lifetime value," or a flag that shouldn\'t dilute when a date/detail filter is applied. |
| INCLUDE | `{INCLUDE [Dim]: AGG(...)}` | Temporarily adds granularity the view doesn\'t show, usually to compute a per-unit value (avg order value per customer) before re-aggregating up to the view\'s grain. |
| EXCLUDE | `{EXCLUDE [Dim]: AGG(...)}` | Removes a dimension present on the view to compute a coarser aggregate alongside detail rows. Common for "% of parent category" or comparing a row to its group total. |
| Nested FIXED (LOD referencing another LOD) | `{FIXED A: ...{FIXED B: ...}...}` | Multi-step aggregation, often building a cohort or segment flag before a second aggregation layer. Verify dependency order. Flag if it looks unnecessarily deep. |

## Table Calculations

| Pattern | Shape | Typical Why |
|---|---|---|
| Running total | `RUNNING_SUM(...)` | Cumulative trend view. Answers "how much so far," not "how much this period." |
| Rank | `RANK(...)` / `RANK_UNIQUE(...)` | Leaderboard/Top-N framing. Ordering matters more than the raw value. |
| Percent of total | `SUM(...)/TOTAL(SUM(...))` or `WINDOW_SUM` variant | Shows share within a partition (whole view, or a partition set by "Compute Using") rather than absolute magnitude. |
| Moving average | `WINDOW_AVG(...)` | Smooths period-to-period noise to reveal an underlying trend. |
| Difference / % difference from prior | `ZN(SUM(...)) - LOOKUP(ZN(SUM(...)), -1)` | Period-over-period comparison. Growth/decline framing. |

## Filters — by visibility

**Filter-visibility is a first-class classification.** For each filter on the view, decide whether it is Visible (viewer can see and change) or Hidden (viewer sees narrowed data with no on-canvas control). Section B\'s pattern column below classes the mechanism; the visibility call is separate and must be made per filter, per view.

**Visible** = quick filter card exposed, parameter control on the dashboard, dashboard filter action target, or a legend acting as a filter (legend-based range filter).

**Hidden** = context filter with no card, data source filter, extract filter, or a True/False calc-based filter with no exposed control. Hidden filters must be disclosed in the output; silence reads as "nothing is hidden," which is only true when confirmed.

| Pattern | Shape | Typical Why |
|---|---|---|
| Context filter | Filter shelf item marked as context (grey pill) | Either a performance optimization (pre-filters before other computations) or intentionally makes a downstream filter/Top-N dependent on it. |
| Parameter-driven quick filter | Calc referencing `[Parameters].[...]` used as a filter | Lets the end user dynamically change scope without editing the view. |
| Top-N filter | `RANK`-based filter or a Top-N set used as a filter | Focuses attention on highest/lowest performers rather than showing the full member list. |
| Filter on a calc, not a raw field | Filter references a calculated field | Usually encodes business logic into the filter itself ("Active Customers" flag) rather than a raw dimension value. |
| Hardcoded True/False gate | Calc resolving to True/False (e.g. `[Source] = [Source Parameter]`) placed on Filters shelf keeping only True | Scope-narrowing that isn\'t exposed to the viewer. Common on inherited dashboards. Always disclose. |
| Data source filter | Filter on the data source itself, not the sheet | Applies workbook-wide before any sheet-level filters. Highest-scope Hidden filter. Almost never visible to end users. |
| Extract filter | Filter baked into the extract at extract time | Only in extract-backed workbooks. Data not in the extract can\'t be recovered by the viewer at all. |

## Actions (dashboard-level)

| Pattern | Shape | Typical Why |
|---|---|---|
| Filter action | Source sheet -> target sheet(s), filters on select | Drill from a summary view into supporting detail. The classic "click a bar, see the detail table update." |
| Highlight action | Source -> target, highlight on hover/select | Draws visual attention to related marks without changing what data is shown. Used when losing context (via filtering) would hurt comparison. |
| Parameter action | Source sheet sets a parameter value on select/hover | Drives a dynamic swap elsewhere (axis measure switch, viz-in-tooltip content, dynamic zone visibility). The sheet is acting as a control, not just a display. |
| URL action | Source sheet -> external URL, often with field values interpolated | External drill-through (to a source system record) beyond what Tableau itself can show. |

## Sets

| Pattern | Shape | Typical Why |
|---|---|---|
| Condition-based dynamic set | Set defined by a calculated condition (e.g. `SUM([Sales]) > 10000`) | Membership recalculates as data changes. Used for a rolling cohort ("customers active in trailing 90 days") rather than a fixed list. |
| Top-N set | Set defined by Top/Bottom N on a measure | Same intent as a Top-N filter, but reusable as a set across multiple sheets/calcs. |
| Manually curated set | Set with an explicit fixed member list | Deliberate comparison group ("key accounts") that shouldn\'t drift automatically as data changes. |

## Dynamic Zone Visibility (dashboard-level)

| Pattern | Shape | Typical Why |
|---|---|---|
| Boolean parameter toggle | Zone visibility bound to a boolean parameter | View-switcher pattern. User toggles between two layouts/chart types without navigating away. |
| Set-membership toggle | Zone visibility bound to set membership | Shows/hides a zone based on whether the current selection/filter state falls into a defined set (alert banner that only appears when a threshold set is non-empty). |

***

## Using This Library

- Section A first (chart-shape idiom, backbone before modifiers), Section B second (mechanics behind the idiom).
- Match structural fingerprint, never field name. Author-chosen names are a *narrative seed*, not a match key.
- Adapt every stock rationale to actual fields/context. Never paste a row verbatim as an explanation.
- If a construct partially matches multiple patterns, say which parts came from where.
- This library does not replace confidence-tagging: pattern-matching raises confidence, it does not eliminate ambiguity. Every uncertain inference still gets a `[Confidence: Low]` or `[Confidence: Medium]` tag per SKILL.md Hard Constraint #3.
