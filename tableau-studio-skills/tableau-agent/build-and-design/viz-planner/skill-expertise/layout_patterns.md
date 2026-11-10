# Layout Patterns

Spatial arrangement frameworks, grid systems, container strategies, responsive breakpoints, and multi-page architecture for Tableau dashboards.

***

## Core Layout Template

Every dashboard follows this zone hierarchy:

```
+---------------------------------------------------+
| HEADER (50-80px fixed height)                     |
| Title + subtitle + date context + top filters     |
+---------------------------------------------------+
| KPI ZONE (60-80px fixed height)                   |
| 2-4 BAN cards, horizontal row, evenly distributed |
+---------------------------+-----------------------+
| PRIMARY VIZ ZONE (60%)    | SECONDARY ZONE (40%)  |
| Largest chart             | Supporting charts     |
| Answers P1 question       | Answer P2 questions   |
| 40-50% of total viz area  | Stacked vertically    |
+---------------------------+-----------------------+
| CONTEXT ZONE (30-40px)                            |
| Source, refresh info, footnotes, reset link       |
+---------------------------------------------------+
```

***

## Grid Systems

| Dashboard Width | Grid | Column Split Options |
|---|---|---|
| 1400px (default desktop) | 3-column or 12-unit | 60/40, 50/25/25, 33/33/33 |
| 1920px (widescreen) | 4-column or 12-unit | 50/50, 25/50/25, 25/25/25/25 |
| 1024px (tablet landscape) | 2-column | 50/50, 60/40 |
| 768px (tablet portrait) | 1-column stack | Full-width stacked |

**Grid rules:**
- All charts align to the same grid. No arbitrary widths.
- Primary chart gets 2 of 3 columns (or 7-8 of 12 units).
- Secondary charts share the remaining column, stacked vertically.
- KPI cards span full width, evenly distributed within a horizontal container.

***

## Recommended Dashboard Dimensions

| Target | Width x Height | Use When |
|---|---|---|
| Desktop (default) | 1400 x 900 px | Standard desktop/laptop viewing |
| Widescreen | 1920 x 1080 px | Dedicated monitor, TV display |
| Tablet landscape | 1024 x 768 px | iPad/tablet in landscape |
| Tablet portrait | 768 x 1024 px | iPad/tablet in portrait |
| Server embed | Match embed dimensions | Coordinated with web team |

**Default:** 1400 x 900 unless user specifies otherwise.

***

## Layout Patterns by Audience

### Executive Layout (4-6 elements, 30 seconds)

```
+---------------------------------------------------+
| "Are We On Track?" - [Topic] YTD | Updated: [date]|
+---------------------------------------------------+
| [$2.4M ^8%]  [$340K ^3%]  [14.2% v0.5pp]         |
+---------------------------+-----------------------+
|                           | Region Bars (sorted)  |
| Primary Trend Line        |                       |
| (YTD vs. LY)             +-----------------------+
|                           | Category Treemap      |
+---------------------------+-----------------------+
| Source: [x] | Refreshed [x] | Click region to filter |
+---------------------------------------------------+
```

- 1 filter max (year toggle or date range in header)
- 1 filter action (click bar to filter trend + treemap)
- No scrolling required

### Manager Layout (5-8 elements, 3 minutes)

```
+---------------------------------------------------+
| [Title] | Filters: [Date] [Region] [Segment]     |
+---------------------------------------------------+
| [KPI 1]  [KPI 2]  [KPI 3]  [KPI 4]              |
+---------------------------+-----------------------+
| Primary Trend             | Comparison Bars       |
| (multi-line by segment)   | (sorted, colored)     |
+---------------------------+-----------------------+
| Composition Breakdown     | Detail Table or       |
| (stacked bar or treemap)  | Scatter (if analyst)  |
+---------------------------+-----------------------+
```

- 2-4 filters in top bar
- Filter actions from charts
- Drill-through to detail page if >6 questions

### Analyst Layout (6-12 elements, 15 minutes)

```
+---------------------------------------------------+
| [Title] | [Date Range] [Dim1] [Dim2] [Dim3] [+]  |
+---------------------------------------------------+
| [KPI 1]  [KPI 2]  [KPI 3]  [KPI 4]              |
+-----------------+-----------------+---------------+
| Trend           | Comparison      | Distribution  |
| (lines/area)    | (bars/dots)     | (histogram)   |
+-----------------+-----------------+---------------+
| Scatter/Heatmap                   | Detail Table  |
| (correlation, multi-dim)          | (drill path)  |
+-----------------------------------+---------------+
```

- 4-8 filters (collapsible panel if >6)
- Parameter actions for dynamic measure swap
- Set actions for comparison groups
- Multi-page with navigation

### Operations Layout (3-5 elements, 30 seconds)

```
+---------------------------------------------------+
| SYSTEM STATUS | Last check: [timestamp]           |
+---------------------------------------------------+
| [STATUS: OK]  [METRIC: 99.2%]  [ALERTS: 3]       |
+---------------------------------------------------+
| Alert List (exceptions only, sorted by severity)  |
+---------------------------------------------------+
| Trend (last 24h, with threshold lines)            |
+---------------------------------------------------+
```

- 1-2 filters max (time window, scope)
- Status-driven color (green/yellow/red, triple-encoded)
- Exception-focused: normal state = minimal info

***

## Container Strategy (Tableau Implementation)

| Design Element | Tableau Implementation |
|---|---|
| Full-width header | Horizontal container (tiled), fixed height 60-80px |
| KPI row | Horizontal container, "Distribute Contents Evenly" |
| 2-column layout | Horizontal container with two vertical containers (60/40 or 50/50) |
| Filter bar (top) | Horizontal container above viz area, fixed height 40-50px |
| Filter panel (left) | Vertical container, fixed width 200-250px |
| Padding/gutters | Inner padding: 8px all sides. Outer padding: 12px. |
| Stacked charts in one column | Vertical container, equal or weighted distribution |

**Container nesting order (outside-in):**
1. Outer vertical container (full dashboard)
2. Header horizontal container (fixed height)
3. KPI horizontal container (fixed height)
4. Body horizontal container (fills remaining)
5. Left vertical container (primary viz, 60%)
6. Right vertical container (secondary charts, 40%)
7. Footer horizontal container (fixed height)

**Sizing mode:**

| Scenario | Mode | Settings |
|---|---|---|
| Desktop-only | Fixed size | 1400 x 900 (or spec dimensions) |
| Multiple devices | Automatic or Range | Min 1024px width, max 1920px |
| Embed | Fixed, matching embed | Coordinate with web team |
| Responsive | Automatic + Device layouts | Each breakpoint designed separately |

***

## Responsive / Adaptive Design

When the dashboard serves multiple devices:

| Element | Desktop (1400px) | Tablet Landscape (1024px) | Tablet Portrait (768px) |
|---|---|---|---|
| Grid | 3-column | 2-column | 1-column stack |
| KPI BANs | Horizontal row (4 across) | Horizontal (4, smaller) | 2x2 grid or stack |
| Primary chart | 60% width, beside secondary | Full width, above secondary | Full width |
| Secondary charts | 40% width, right column | Full width, below primary | Full width, below |
| Filter panel | Top bar (horizontal) | Collapsed to dropdown | Hidden behind toggle |
| Context zone | Full-width footer | Icon + tooltip | Hidden or separate tab |
| Charts to DROP | None | Drop lowest-priority P2 | Drop all P2; keep P1 only |

**Responsive rules:**
- Never shrink charts below readable size. Hide lower-priority elements instead.
- Filters collapse before charts do.
- KPI BANs survive all breakpoints (compress, never disappear).
- Primary chart visible without scrolling at every breakpoint.
- Viz-in-tooltip disabled on phone layouts (too slow).

***

## Multi-Page Architecture

When recommending multiple pages/sheets:

| Page | Purpose | Navigation |
|---|---|---|
| Overview/Summary | Executive scan, KPIs, at-a-glance | Landing page, always accessible |
| Detail/Drill | Deep dive into specific area | Linked from overview charts |
| Diagnostic/Analysis | Root cause exploration | Linked from anomaly indicators |
| Appendix/Reference | Definitions, methodology, raw data | Footer link or tab |

**Page naming rules:**
- Descriptive, 2-4 words: "Sales Overview", "Sales by Region", "Sales Detail"
- Never "Sheet 1", "Page 2", "Main"
- Consistent pattern across pages

**Navigation between pages:**
- Navigation action from overview charts to detail
- Tab strip or button bar for direct access
- "Back to Overview" link on every sub-page
- URL actions for external system links

***

## Dashboard Title & Header Design

**Title strategy by audience:**

| Audience | Strategy | Example |
|---|---|---|
| Executive | Question-driven | "Are We On Track for Q3?" |
| Manager | Scope-descriptive | "Regional Sales, Rolling 12 Months" |
| Analyst | Metric-centric | "Customer Cohort Retention Analysis" |
| Operations | Action-oriented | "System Health, Action Required" |
| External | Storytelling | "2026 Impact Report" |

**Header contents:**
- Title (left-aligned, largest text)
- Subtitle (below title or right-aligned): scope, refresh info, data-through date
- Top filters (right side of header bar)
- Logo (far-left or far-right, if branded, never center)

**What NOT to put in headers:**
- Generic titles ("Dashboard", "Overview")
- More than 2 filters in the header row (move rest to filter bar below)
- Decorative images or large logos that consume chart space
