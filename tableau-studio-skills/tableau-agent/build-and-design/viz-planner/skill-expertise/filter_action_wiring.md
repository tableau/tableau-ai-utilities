# Filter & Action Wiring

Complete reference for configuring dashboard filters, actions, and interaction behaviors during assembly.

***

## Filter Types

| Filter Type | Control Appearance | Use When |
|---|---|---|
| Single Value (dropdown) | Dropdown select, one value | User picks one option at a time (Region, Segment) |
| Single Value (list) | Radio buttons | 3-6 options, all visible at once |
| Single Value (slider) | Slider control | Numeric or date with continuous range |
| Multiple Values (dropdown) | Multi-select dropdown | Many options, space-constrained |
| Multiple Values (list) | Checkbox list | 5-10 options, all visible |
| Wildcard | Text search box | Free-text matching on a dimension |
| Relative Date | Presets (Last N days/weeks) | Date filtering without calendar picker |
| Range of Dates | Calendar picker with start/end | Specific date range selection |

**Default selections:**
- Relative date: default to "Last 12 months" unless spec says otherwise
- Categorical: default to "All" unless spec specifies a default member
- Numeric: default to full range

***

## Filter Placement Options

| Placement | Container | Sizing | Best For |
|---|---|---|---|
| Header row | Header Horizontal Container, right-aligned | Fixed height 40-50px | 1-3 compact filters (dropdowns) |
| Filter bar (below header) | Dedicated Horizontal Container | Fixed height 40-50px | 3-5 horizontal filters |
| Left sidebar | Dedicated Vertical Container, fixed width | Fixed width 200-250px | 4+ filters, enough room for lists |
| Right sidebar | Same as left, right edge | Fixed width 200-250px | Same as left, less common |
| Above chart | Inside the chart's parent container, above the sheet | Fixed height 40px | Chart-specific filter (scoped to one sheet) |

**Placement decision logic:**
- 1-2 filters: header row
- 3-4 filters: filter bar below header
- 5+ filters: sidebar
- Chart-specific filter: above the chart it controls

***

## Filter Scoping

### "Apply to All Sheets" (Dashboard-Wide)

- Filter affects every worksheet on the dashboard
- Use for: Date range, primary segment dimension, region (when all charts share the context)
- Implementation: set filter scope to "All Using This Data Source" or "All Using Related Data Sources"

### "Apply to Selected Worksheets" (Targeted)

- Filter affects only named worksheets
- Use for: Detail-level filters that shouldn't touch KPI values, chart-specific drill-downs
- Implementation: explicitly list target sheets in the filter's scope settings

### "Apply to Single Worksheet" (Isolated)

- Filter affects only the sheet it's placed on
- Use for: "Show top 10" on one chart without affecting others, local sort filters
- Rarely placed as a visible control; usually a fixed filter

**Critical scoping rule:** KPI sheets should almost NEVER be affected by detail-level filters. If a dashboard has "Top N Products" as a filter, it should target the product bar chart and product table, NOT the summary KPI tiles. KPIs show the big picture; filters narrow the detail views.

### Scoping Syntax (in the spec)

When the DASHBOARD REQUEST says:
- `Scope: All` = apply to all worksheets
- `Scope: Sales Trend, Region Bar` = apply only to those named sheets
- `Scope: All except KPI*` = apply to all sheets except those starting with "KPI"

***

## Filter Interactions

### Context Filters (High Priority)

- Evaluated before dimension/measure filters in Tableau's order of operations (level 3 of 7; only extract and datasource filters precede them)
- Use for dimension filters that should also limit LOD calculations
- Marked as "Add to Context" in the filter shelf
- Apply these ONLY when the spec explicitly calls for context filtering (performance or LOD reasons)

### Dependent Filters

- One filter's available values update based on another filter's selection
- Example: Region filter selected = "West" -> City filter shows only western cities
- Implementation: set "Only Relevant Values" on the dependent filter
- Order matters: the controlling filter must be placed/processed before the dependent one

### Reset Mechanism

**Rule:** If the dashboard has >2 user-facing filters, provide a reset mechanism.

Options:
- "Reset" button (URL action to the dashboard's base URL)
- "Clear All" button linking to the dashboard without parameters
- Text instruction: "Ctrl+click to deselect" (less discoverable, avoid as sole method)

***

## Dashboard Actions

### Filter Action

**Purpose:** Clicking a mark in one sheet filters data in other sheets.

**Configuration:**

| Setting | Value | Notes |
|---|---|---|
| Source Sheet | The chart the user clicks | One source per action |
| Run On | Select (default) | Hover for preview, Menu for right-click |
| Target Sheets | Named sheets that respond | Can be "All" or specific list |
| Clearing Selection | Show All Values | ALWAYS. Prevents "stuck" state |
| Source Fields | Specific field(s) or "All Fields" | Use specific for cross-datasource or precision |
| Target Fields | Auto-match or manually map | Map manually when field names differ between sources |

**Common pattern:** Click a bar in a category chart -> filters a detail table and a trend line to that category.

### Highlight Action

**Purpose:** Clicking a mark dims non-matching marks in other sheets (without removing data).

**Configuration:**

| Setting | Value | Notes |
|---|---|---|
| Source Sheet | The chart the user clicks | Same as filter action |
| Run On | Hover (common) or Select | Hover for quick exploration |
| Target Sheets | Named sheets or "All" | Typically broader than filter actions |
| Clearing Selection | Show All Values | Restores full opacity |

**When to use Highlight vs. Filter:**
- Highlight: user wants to explore/compare without losing context (the other marks stay visible but muted)
- Filter: user wants to drill down (non-matching marks disappear entirely)

### Navigation Action

**Purpose:** Clicking a mark navigates to another dashboard page.

**Configuration:**

| Setting | Value | Notes |
|---|---|---|
| Source Sheet | The chart with clickable marks | Often a summary table or overview chart |
| Run On | Select or Menu | Select for primary flow, Menu for alternative paths |
| Target Dashboard | Another dashboard sheet in the workbook | Must be a dashboard, not a worksheet |
| Pass Filters | Yes (carry the selected context) | Critical: passes the clicked dimension values as filter context to the target page |

**Common pattern:** Click a region in an overview map -> navigates to the region detail dashboard, pre-filtered to that region.

**"Back" navigation:** On detail pages, add a navigation action (or text link) pointing back to the overview page. Without this, users get stranded.

### URL Action

**Purpose:** Clicking a mark opens an external URL.

**Configuration:**

| Setting | Value | Notes |
|---|---|---|
| Source Sheet | Chart containing linkable marks | Often a table with IDs or names |
| Run On | Menu (common) or Select | Menu avoids accidental navigation |
| URL Template | `https://example.com/detail/<Field Name>` | Field tokens in angle brackets |

**URL token syntax:** `<Field Name>` inserts the value of that field for the clicked mark. Use URL-safe field values.

### Parameter Action (Change Parameter)

**Purpose:** Clicking a mark sets a parameter value.

**Configuration:**

| Setting | Value | Notes |
|---|---|---|
| Source Sheet | Chart the user clicks | Value comes from the clicked mark |
| Target Parameter | Named parameter | Must already exist in the workbook |
| Source Field | Field whose value populates the parameter | Match data type to parameter type |
| Clearing Selection | Keep current value | Parameters persist, don't "reset" on clear |

### Set Action (Add/Remove from Set)

**Purpose:** Clicking marks adds or removes dimension members from a set.

**Configuration:**

| Setting | Value | Notes |
|---|---|---|
| Source Sheet | Chart the user interacts with | Works best with discrete dimensions |
| Target Set | Named set in the workbook | Must already exist |
| Running Action | Assign values to set | Or "Add values" / "Remove values" |
| Clearing Selection | Keep set values OR Remove all values | Depends on UX intent |

***

## Action Wiring Best Practices

### Source-Target Pairing Rules

1. **A sheet must be ON the dashboard to be a source or target.** If it's in the workbook but not placed on this dashboard, actions can't reach it.

2. **One action per interaction intent.** Don't wire both a filter action AND a highlight action from the same source on "Select." Pick one. (Hover for highlight + Select for filter is fine.)

3. **Filter actions need clearing.** ALWAYS set clearing to "Show All Values." This is the single most common mistake in dashboard assembly. Without it, users click once and can never get back to the unfiltered state without refreshing.

4. **Cross-datasource filter actions require field mapping.** If source and target use different datasources, you must manually map which source field corresponds to which target field. Never guess or invent field names for the mapping. Verify both the source field and target field exist (via `get-workbook-inventory` or field inspection) before wiring the action. A wrong mapping silently produces no results rather than erroring.

5. **Navigation actions should pass filters.** When navigating to a detail page, pass the relevant dimension filters so the detail page is pre-scoped. Otherwise the user navigates to an unfiltered detail page and wonders why.

### Action Naming Convention

Name actions descriptively so they're identifiable in the Actions dialog:
- "[Source] filters [Targets] on [Field]" — e.g., "Region Bar filters Trend + Table on Region"
- "[Source] highlights [Targets]" — e.g., "Category Chart highlights All on Category"
- "[Source] navigates to [Destination]" — e.g., "Summary Table navigates to Detail Page"

***

## Interaction Patterns by Dashboard Type

### Executive Dashboard

| Interaction | Implementation |
|---|---|
| Date context changes all charts | Date filter scoped to "All Sheets" |
| Click KPI drills to detail | Navigation action from KPI to detail page |
| Compare segments | Highlight action on segment bar -> all other charts |

### Manager Dashboard

| Interaction | Implementation |
|---|---|
| Filter cascade (Region -> City -> Store) | Dependent filters with "Only Relevant Values" |
| Click bar to filter detail | Filter action from bar chart -> table + trend |
| Reset all selections | Reset button (URL action to base dashboard URL) |

### Analyst Dashboard

| Interaction | Implementation |
|---|---|
| Sidebar filters narrow all views | 5+ filters scoped to all sheets |
| Select marks to add to set | Set action for cohort building |
| Parameter controls chart behavior | Parameter action from control sheet |
| Export/detail link | URL action to detail system |

### Operations Dashboard

| Interaction | Implementation |
|---|---|
| Alert list filters trend to that alert | Filter action from alert table -> trend chart |
| Click trend point shows details | Filter action from trend -> detail table |
| Minimal other interaction | Operations dashboards favor clarity over interactivity |

***

## Filter Order of Operations (Tableau)

When multiple filters are present, Tableau evaluates them in this order:

1. Extract Filters (on data connection)
2. Data Source Filters (on data source)
3. Context Filters (marked "Add to Context")
4. Top N / Conditional Filters (on filter shelf)
5. Dimension Filters (on filter shelf)
6. Measure Filters (on filter shelf, after aggregation)
7. Table Calculation Filters (after table calc evaluation)

**Why this matters for assembly:** If a dashboard filter is meant to affect an LOD calculation, it must be set as a Context Filter (level 3). Regular dimension filters (level 5) are evaluated AFTER LOD calcs. The DASHBOARD REQUEST should specify this if needed; if it doesn't, default to regular dimension filter placement.
