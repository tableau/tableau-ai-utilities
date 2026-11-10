# Filter & Interaction Strategy

Filter selection rules, interaction design patterns, tooltip specifications, and reset mechanisms for Tableau dashboards.

***

## Filter Selection by Dimension Type

| Dimension Type | Filter Type | Placement | Audience |
|---|---|---|---|
| Time (Date) | Relative date picker ("Last 12 months", "YTD") | Top-right of header | All |
| Low-cardinality (≤5 values) | Radio buttons / segmented control | Top header bar | All |
| Low-cardinality (6-12 values) | Dropdown (single or multi-select) | Top bar or left sidebar | Manager, Analyst |
| Medium-cardinality (13-50) | Searchable dropdown | Left sidebar | Analyst only |
| High-cardinality (>50) | Type-ahead search box | Left sidebar | Analyst only |
| Geographic hierarchy | Cascading dropdowns (Country -> State -> City) | Left sidebar | Manager, Analyst |
| Boolean/binary | Toggle switch or checkbox | Inline with header | All |

***

## Filter Count Enforcement (Strict)

| Audience | Max Visible Filters | Strategy When Questions Need More |
|---|---|---|
| Executive | 0-2 | Use dashboard filter actions (click chart to filter) instead of controls |
| Manager | 2-4 | Group related filters (Region + Segment in one container) |
| Analyst | 4-8 | Collapsible filter panel if >6 |
| Operations | 1-2 | Time window only, or single scope selector |
| External | 0-1 | None ideally. Let the viz tell the story. |

**If questions require more filtering than the audience permits:**
- Replace explicit filter controls with filter actions (clicking a chart element)
- Use parameters for dynamic measure/dimension swapping (reduces filter clutter)
- Hide lower-priority filters behind a "More Filters" expander
- Move detailed filtering to a dedicated filter page (Analyst only)

***

## Filter Placement Rules

1. **Date filter always top-right** (most universal, sets temporal context)
2. **Scope filters (Region, Department) in header bar** (set the data universe)
3. **Detail filters (Product, Customer) in sidebar or below header** (narrow within scope)
4. **Never place filters below the charts they control** (user won't find them)
5. **Group related filters visually** (container with label: "Geography" containing Region + State)

***

## Filter Implementation in Tableau

| Design Filter Type | Tableau Realization |
|---|---|
| Radio buttons / segmented control | Single-value list, display as radio buttons |
| Dropdown | Single or multi-value dropdown |
| Date range picker | Relative date filter (show "Relative to" option) |
| Type-ahead search | Wildcard match filter or parameter with Type-in |
| Cascading (Country -> State) | "Only Relevant Values" on dependent; Country as context filter |
| "Filter by clicking chart" | Dashboard filter action: source -> target(s), clearing = show all |
| Toggle | Parameter (boolean) controlling a calculated filter |

**Context filter warning:** If filters need cascading behavior (Region must be selected before City populates), note: "Set [parent filter] as Context Filter (right-click -> Add to Context) to ensure dependent filters show correct values."

***

## Interaction Design Patterns

### Filter Actions (Click to Filter)

| When to Use | Source | Target | Clearing Behavior |
|---|---|---|---|
| Executive dashboards (reduces filter controls) | Bar chart, map, KPI card | All other charts | Clear = show all values |
| Manager dashboards (drill context) | Category bar, region map | Detail charts (not KPIs) | Clear = show all |
| Multi-chart exploration | Any chart with clickable marks | Specified targets only | Clear = show all |

**Implementation:**
- Source sheet: any chart with discrete marks (bars, map regions, pie slices)
- Target sheets: specify which charts respond (not always "all")
- Run on: Select (not hover)
- Clearing: Always "Show All Values" (never leave filtered with no way back)

**Affordance:** Always indicate interactivity. Options:
- Instruction text: "Click a bar to filter" (subtle, below chart)
- Hover highlight change (darken, outline)
- Cursor change to pointer (if supported)

### Highlight Actions

| When to Use | Effect | Vs. Filter |
|---|---|---|
| Context should persist while exploring | Dims non-selected marks (opacity ~30%) | Filter removes; highlight dims |
| Comparing one segment against the whole | Selected segment full color, rest gray | Keeps total visible |
| Executive exploration without losing overview | Subtle emphasis, no data disappears | Safer for scanning |

### Navigation Actions

| When to Use | Source | Target | Back Path |
|---|---|---|---|
| Multi-page drill-down | KPI card, overview chart mark | Detail sheet (same workbook) | "Back to Overview" button on detail |
| Anomaly exploration | Exception indicator, alert row | Diagnostic page | Same |
| External system link | Specific data point | URL (ticket system, wiki, etc.) | Opens in new tab |

**Implementation:**
- Source: sheet with marks that represent navigable entities
- Target: another dashboard sheet in the workbook
- Pass filters: Yes (carry the context of what was clicked)
- Back navigation: always provide a return path

### Parameter Actions

| When to Use | What Changes | Example |
|---|---|---|
| Dynamic measure selection | Y-axis measure swaps | "Click to view: Sales | Profit | Quantity" |
| Dynamic dimension selection | Breakdown category swaps | "Group by: Region | Segment | Category" |
| Threshold adjustment | Reference line moves | Slider controls target value |
| TOP N control | Filter adjusts to show more/fewer | "Show top: 5 | 10 | 20" |

**Implementation:**
- Create parameter with allowed values
- Create calculated field referencing the parameter
- Place the calculated field on the relevant shelf
- Expose parameter control in header or sidebar

### Set Actions

| When to Use | Complexity Level | Audience |
|---|---|---|
| Multi-select comparison groups | High | Analyst only |
| "Selected vs. Rest" analysis | High | Analyst only |
| Proportional highlighting | Medium-High | Analyst, advanced Manager |

**Implementation:**
- Create a set on the dimension
- Dashboard set action: select marks -> add to set
- Calculated field: IF [Set] THEN "Selected" ELSE "Rest"
- Use the calc for color encoding or separate panels

***

## Tooltip Design Strategy

Tooltips are the dashboard's hidden detail layer. They provide P3/P4 information without consuming layout space.

### Tooltip Content Hierarchy (top to bottom)

```
+-----------------------------------+
| DIMENSION VALUE (bold)            |  <- What am I looking at?
| Primary measure: $X,XXX          |  <- The number I came for
| vs. Prior Period: ^/v X.X%       |  <- Context / comparison
| Secondary measure: X,XXX         |  <- Supporting detail
| [Viz-in-tooltip: sparkline]      |  <- Optional: trend context
| Click to drill -> [Detail Page]  |  <- Action cue (if applicable)
+-----------------------------------+
```

### Tooltip Rules by Audience

| Audience | Depth | Viz-in-Tooltip | Action Cues |
|---|---|---|---|
| Executive | 2-3 lines. Value + comparison only. | No (too slow) | "Click for details" only if nav action exists |
| Manager | 3-5 lines. Value + comparison + one breakdown. | Optional sparkline | "Click to filter" or "Click for detail" |
| Analyst | 5-8 lines. Full context, multiple measures, IDs. | Yes (sparklines, bars) | "Click to drill", "Right-click for options" |
| Operations | 2-3 lines. Status + threshold + action. | No | "Click to open ticket" (URL action) |
| External | 2-3 lines. Plain language explanation. | No | None |

### What NOT to Put in Tooltips

- Raw database field names (use display names: "Total Revenue" not "SUM(sales_amt)")
- More than 8 lines of text
- Critical information the user MUST see (tooltips are hover-only)
- Redundant info already visible on the chart (if the bar label says "$1.2M", don't repeat in tooltip)

### Viz-in-Tooltip Recommendations

| Viz Type | Best For | When to Use |
|---|---|---|
| Sparkline (last 12 periods) | "Is this going up or down?" context | Manager/Analyst; trend exists |
| Small bar chart (sub-breakdown) | "What makes up this number?" | Manager/Analyst; sub-categories exist |
| Mini KPI (number + arrow) | Quick metric check without a full chart | Any audience with hover capability |

**Only use viz-in-tooltip when:**
- Audience is Manager or Analyst
- Extra context reduces need for a separate chart
- Rendering speed is acceptable (<0.5s)
- NOT on tablet/phone layouts (disable there)

***

## Reset & Context Mechanisms

### Reset Button

| Condition | Implementation |
|---|---|
| >2 visible filters | "Reset Filters" text link, top-right corner |
| Filter actions exist | "Reset" or "Clear Selection" button near source chart |
| Parameter actions | "Reset to Default" link near parameter control |

**Reset behavior:** Returns ALL filters (explicit + action-based) to their default state. One click, full reset.

### Active Filter State Display

Always show what's currently filtered. Options:

| Method | Best For | Implementation |
|---|---|---|
| Breadcrumb trail | Manager/Analyst with multiple filters | "Filtered: Region = West, Year = 2024" in subtitle area |
| Subtitle context | Executive (1-2 filters) | Dashboard subtitle updates: "Showing: West Region" |
| Filter indicator dots | Compact display | Small colored dot next to each active filter label |

### Date Context (Always Visible)

The temporal scope must be visible at all times:
- In subtitle: "Data through June 2026"
- In header: "Last 12 months | Updated daily"
- In KPI zone: comparison text makes time explicit ("vs. same period LY")

Never assume the user knows the time range. State it explicitly.

***

## Interaction Budget by Audience

| Audience | Filter Actions | Highlight Actions | Nav Actions | Parameter Actions | Set Actions |
|---|---|---|---|---|---|
| Executive | 0-1 | 0-1 | 0-1 (optional drill) | 0 | 0 |
| Manager | 1-2 | 0-1 | 1-2 (drill to detail) | 0-1 | 0 |
| Analyst | 2-4 | 1-2 | 2-3 (multi-page nav) | 1-3 | 0-2 |
| Operations | 0-1 | 0 | 1 (open ticket) | 0 | 0 |
| External | 0 | 0-1 | 0 | 0 | 0 |

**If the design exceeds the interaction budget:** Simplify. Remove the least essential interaction. Every interaction must justify its existence by the audience actually using it.
