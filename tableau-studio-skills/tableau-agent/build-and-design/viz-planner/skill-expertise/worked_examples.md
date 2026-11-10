# Worked Examples

Complete end-to-end examples showing the Viz Planner workflow from intake through design spec output.

***

## Example 1: Executive Sales Dashboard

### Input

- **Datasource:** Superstore (Orders table: Order Date, Sales, Profit, Category, Sub-Category, Region, State, Segment, Ship Mode, Quantity, Discount)
- **Questions:** (1) Are we on track for our sales target? (2) How is sales trending vs. last year? (3) Which regions are underperforming? (4) What product categories drive revenue?
- **Audience:** VP of Sales, checks Monday morning, 30 seconds max

### Phase 1: Requirements Resolution

- Audience profile: **Executive** (5-30 sec, 0-2 filters, 4-6 charts max)
- Question prioritization:
  - Q1: "Are we on track?" -> P1 (decision-critical)
  - Q2: "How is sales trending?" -> P1 (decision-critical)
  - Q3: "Which regions underperform?" -> P2 (monitoring)
  - Q4: "What categories drive revenue?" -> P2 (monitoring)
- All 4 questions fit within executive budget (4-6 charts). No multi-page needed.

### Phase 2: Field Classification

| Field | Category | Design Role |
|---|---|---|
| Order Date | Time dimension | X-axis for trend, date filter |
| Sales | Primary measure | KPI BAN, Y-axis |
| Profit | Secondary measure | Secondary KPI |
| Region | Low-cardinality dim (4 values) | Bar chart rows, filter action source |
| Category | Low-cardinality dim (3 values) | Color encoding, treemap |
| Sub-Category | Medium-cardinality dim (~17) | Drill target, tooltip |
| State | Medium-cardinality (50) | Drill only (not on Page 1) |
| Segment | Low-cardinality dim (3) | Optional color or filter |

No schema gaps. All questions map to available fields.

### Phase 3: Chart Selection

| Question | Chart Type | Rationale |
|---|---|---|
| Q1: On track? | KPI tile (BAN) | Status/KPI question. Single metric + comparison. |
| Q2: Trending? | Line chart (this year solid, last year dashed) | Temporal, single measure, >8 periods. Dual series for comparison. |
| Q3: Regions underperforming? | Horizontal bar (sorted, colored by vs-target) | Categorical comparison, 4 categories. Sorted bar is clearest. |
| Q4: Category revenue? | Treemap | Composition, 3 categories with sub-categories nested. Treemap shows hierarchy. |

Anti-pattern check: All pass. Sorted bar (not alphabetical). No pie (treemap for composition). No dual axis. Line connects ordered time.

### Phase 4-8: Design Spec Output

```
=====================================================
VIZ PLANNER - Dashboard Design Specification
=====================================================

PROJECT: "Are We On Track?" - Sales Performance YTD
AUDIENCE: VP of Sales (Executive)
TIME BUDGET: 30 seconds
DIMENSIONS: 1400 x 900 px
PAGES: Single page (drill via tooltip + action)

-----------------------------------------------------
1. BUSINESS QUESTIONS -> CHART MAPPING

  Q1: "Are we on track for our sales target?" [P1]
  -> Chart: KPI BAN | Fields: SUM(Sales) YTD vs. Target | Position: KPI zone

  Q2: "How is sales trending vs. last year?" [P1]
  -> Chart: Line (dual series) | Fields: Month(Order Date) x, SUM(Sales) y, Year color | Position: Primary viz

  Q3: "Which regions are underperforming?" [P2]
  -> Chart: Horizontal bar (sorted) | Fields: Region rows, SUM(Sales) cols, vs-target color | Position: Secondary top

  Q4: "What categories drive revenue?" [P2]
  -> Chart: Treemap | Fields: Category color, Sub-Category detail, SUM(Sales) size | Position: Secondary bottom

-----------------------------------------------------
2. KPI HIERARCHY

  Primary:
  - Total Sales YTD: $X.XM | vs. target | top-left
  - Total Profit YTD: $X.XK | vs. LY | top-center
  - Profit Margin: XX.X% | vs. LY | top-right

-----------------------------------------------------
3. LAYOUT WIREFRAME

  +----------------------------------------------------+
  | "Are We On Track?" - Sales YTD | Updated: Jun 2026 |
  +----------------------------------------------------+
  | [$2.4M ^8%]  [$340K ^3%]  [14.2% v0.5pp]          |
  +----------------------------+-----------------------+
  |                            | Region Performance    |
  | Monthly Sales Trend        | ==== West    $820K    |
  |   ---- 2026 (solid)       | ==== East    $690K    |
  |   .... 2025 (dashed)      | ===  Central $510K    |
  |                            | ==   South   $380K    |
  |                            +-----------------------+
  |                            | Category Treemap      |
  |                            | [Tech] [Furn] [Off]   |
  +----------------------------+-----------------------+
  | Source: Superstore | Refreshed daily               |
  +----------------------------------------------------+

  Grid: 60/40 split. Primary: 60% width. KPIs: equal thirds, 60px.

-----------------------------------------------------
4. WORKSHEET SHELF RECIPES

  Sheet 1: "Sales YTD KPI"
  MARK TYPE: Text (BAN)
  BUILD PATH: manual (kpi-highlight-box pattern)
  COLUMNS: (none)
  ROWS: (none)
  TEXT: SUM([Sales YTD]) | $#.#M
  COLOR: [KPI Status] | Semantic (green/red)
  CALCULATED FIELDS:
    [Sales YTD]: IF YEAR([Order Date])=YEAR(TODAY()) AND [Order Date]<=TODAY() THEN [Sales] END
    [KPI Status]: IF SUM([Sales YTD])>=[Target] THEN "On Track" ELSE "Off Track" END

  Sheet 2: "Monthly Sales Trend"
  MARK TYPE: Line
  BUILD PATH: bind-template
  COLUMNS: MONTH([Order Date]) | Continuous
  ROWS: SUM([Sales])
  COLOR: YEAR([Order Date]) | Categorical (2 values: solid/dashed)
  FORMATTING: Current year solid #4E79A7, prior year dashed #9C9C9C

  Sheet 3: "Region Performance"
  MARK TYPE: Bar
  BUILD PATH: bind-template
  COLUMNS: SUM([Sales])
  ROWS: [Region]
  SORT: SUM([Sales]) | Descending
  COLOR: [vs Target %] | Diverging (red-gray-green)
  LABEL: SUM([Sales]) | $#K
  CALCULATED FIELDS:
    [vs Target %]: (SUM([Sales]) - [Region Target]) / [Region Target]

  Sheet 4: "Category Revenue"
  MARK TYPE: Square (treemap)
  BUILD PATH: manual
  DETAIL: [Category], [Sub-Category]
  SIZE: SUM([Sales])
  COLOR: [Category] | Categorical (#4E79A7, #F28E2B, #59A14F)
  LABEL: [Sub-Category], SUM([Sales]) | $#K

-----------------------------------------------------
5. FILTER STRATEGY

  | Filter | Type | Placement | Default | Scope |
  |--------|------|-----------|---------|-------|
  | Year | Segmented (2025/2026) | Header right | 2026 | All |

  Actions:
  - Region bar -> Filter action -> Trend + Treemap

  Reset: "Reset" text link, top-right

  Total visible filters: 1 (within executive max of 2)

-----------------------------------------------------
6. COLOR SYSTEM

  Primary (current year trend): #4E79A7
  Prior year (dashed): #9C9C9C
  Above target: #59A14F
  Below target: #E15759
  Categories: [#4E79A7, #F28E2B, #59A14F]
  Background: #FFFFFF
  KPI card background: #F8F9FA
  Text: #333333 (titles), #666666 (labels)

-----------------------------------------------------
7. INTERACTION MODEL & TOOLTIPS

  Interactions:
  - Region bar -> Filter action -> Trend + Treemap
  - KPI cards: non-interactive
  - Trend: hover for monthly detail

  Tooltip (trend):
  - Month (bold)
  - Sales: $X,XXX
  - vs. LY: ^/v X.X%

  Tooltip (region bar):
  - Region (bold)
  - Sales: $X,XXX | Target: $X,XXX
  - Gap: +/- $X,XXX
  - "Click to filter dashboard"

-----------------------------------------------------
8. TYPOGRAPHY

  Title: Tableau Bold, 20px, #333333
  Subtitle: Tableau Book, 11px, #666666
  KPI values: Tableau Bold, 28px, #333333
  KPI labels: Tableau Book, 10px, #666666
  Chart headers: Tableau Medium, 13px, #333333
  Axis labels: Tableau Book, 10px, #666666

-----------------------------------------------------
9. IMPLEMENTATION NOTES

  Container: Tiled throughout. Outer vertical -> Header + KPI row +
    Body (horizontal: 60/40) + Footer.
  Sizing: Fixed, 1400x900.
  Parameters: [Target Sales]: Float, $2.6M default
  Performance: Superstore ~10K rows. Live connection fine.
  Device layouts: Not needed (desktop-only audience)

=====================================================
```

***

## Example 2: Analyst Customer Cohort Dashboard (Multi-Page)

### Input

- **Datasource:** SaaS customer data (Signup Date, Last Active Date, Plan, MRR, Churn Date, Customer ID, Industry, Company Size, Region, Feature Usage Score, Support Tickets, NPS Score)
- **Questions:** (1) What's our retention rate by cohort? (2) Which segments churn fastest? (3) Is there a relationship between usage and churn? (4) What's the revenue impact of churn? (5) Which customers are at risk right now?
- **Audience:** Growth Analytics team, deep-dive weekly, 10-15 minutes

### Phase 1: Requirements Resolution

- Audience: **Analyst** (3-15 min, 4-8 filters, 6-12 charts, high complexity)
- Question prioritization:
  - Q1: Retention by cohort -> P1 (core metric)
  - Q2: Segments churn fastest -> P1 (actionable)
  - Q4: Revenue impact -> P2 (monitoring)
  - Q3: Usage vs. churn relationship -> P3 (diagnostic)
  - Q5: At-risk customers -> P2 (actionable, but detail-level)
- 5 questions, analyst budget allows it. Multi-page: Overview (P1+P2) + Diagnostic (P3+detail).

### Design Decision Highlights

- **Page 1 (Retention Overview):** Cohort retention heatmap (Q1), churn rate by segment bar (Q2), MRR impact line (Q4), at-risk customer count BAN
- **Page 2 (Churn Diagnostics):** Scatter plot usage vs. churn probability (Q3), at-risk customer table with action column (Q5)
- **Filters:** Date cohort range, Plan type, Industry, Company Size, Region (5 filters, collapsible panel)
- **Interactions:** Click cohort cell -> filter Page 1 charts. Click segment bar -> navigate to Page 2 filtered. Set action for "compare selected cohorts vs. rest."

***

## Example 3: Operations Real-Time Status Dashboard

### Input

- **Datasource:** System monitoring (Timestamp, Service Name, Response Time ms, Error Count, Uptime %, Alert Severity, Region, Request Volume)
- **Questions:** (1) Is everything healthy right now? (2) Are there active alerts? (3) What's the response time trend today?
- **Audience:** SRE on-call engineer, glances at it every few minutes

### Phase 1: Requirements Resolution

- Audience: **Operations** (5-30 sec, 1-2 filters, 3-5 charts, alert-driven)
- All questions are P1 (decision-critical for on-call):
  - Q1: Health status -> KPI with semantic color
  - Q2: Active alerts -> Alert list (exception table)
  - Q3: Response time -> Simple trend line (last 24h with threshold)

### Design Decision Highlights

- **Layout:** Stacked vertical (1-column). Status banner at top (blue/teal + orange/magenta + gray, triple-encoded). Alert list (sorted by severity). Trend line below.
- **KPIs:** Overall Status (On Track/Degraded/Down), Uptime % (last 24h), Active Alerts count, P95 Response Time
- **Filters:** Region selector only (1 filter). Everything else is "show all, highlight exceptions."
- **Color:** Default Status Palette (per `skill-expertise/color_accessibility.md`) — Blue/Teal = healthy, Orange/Magenta = degraded/down, Gray = neutral/unknown. Never red/yellow/green (this project's non-negotiable rule, including for operations status). Triple-encoded with icons (checkmark, warning, X) and text labels.
- **Interaction:** Click alert row -> open incident ticket (URL action). No complex filtering.
- **Title:** "System Health | Last check: [timestamp]" (action-oriented, real-time context)

***

## Pattern Recognition: When to Use Each Layout

| Signal from the User | Layout Pattern |
|---|---|
| "Executive summary" / "for my VP" / "30 seconds" | Executive layout, single page, 4-6 elements |
| "Weekly review" / "team meeting" / "for managers" | Manager layout, 1-2 pages, 5-8 elements |
| "Deep dive" / "analysis" / "explore" / "analysts" | Analyst layout, multi-page, 6-12 elements per page |
| "Real-time" / "monitoring" / "alerts" / "on-call" | Operations layout, vertical stack, status-driven |
| "External" / "client-facing" / "public" / "report" | Minimal layout, single page, storytelling structure |

***

## Assembly Instruction Examples (Phase 9 Step 3)

Ported from the retired Dashboard Assembler skill. These show what to hand the user once worksheets are built and verified — Viz Planner produces these instructions itself; it never executes them.

### Example A: Simple Tiling Instructions (4-6 sheets, no custom layout)

**Situation:** 4 worksheets built and verified (KPI Sales, KPI Profit, Monthly Trend, Region Bar), no spatial requirements beyond "put them on a dashboard," no filter scoping, no actions.

**Instructions to give:**
1. Call `get-workbook-inventory` (read-only) to confirm all 4 sheets exist.
2. Tell the user: "Click New Dashboard, then drag each of these sheets onto the canvas in this order: KPI Sales, KPI Profit, Monthly Trend, Region Bar. Then set the dashboard to Fixed size, 1400x900, via the Size dropdown in the Dashboard pane — this alone noticeably improves how the default tiled layout looks."
3. Report: "Here are the instructions for a 4-sheet dashboard — KPIs first, then the trend chart, then the region bar. Let me know once you've built it and I'll confirm it landed correctly with `get-workbook-inventory`/`list-dashboards`."

### Example B: Full Manual Assembly Instructions (7 sheets, KPI row, 60/40 split, filters, actions)

**Situation:** DASHBOARD ASSEMBLY SPEC calls for a 1400x900 fixed dashboard, 4 KPIs across the top, a primary trend chart at 60% width on the left, two secondary charts stacked at 40% width on the right, two filters scoped to all sheets, and two dashboard actions.

**Instructions to give (in this order):**
1. Confirm all 7 sheets exist via `get-workbook-inventory` (read-only).
2. Container structure: "Build outside-in using placeholders — drop the outer vertical container first, add Blank placeholders for Header/KPI/Body/Footer, then replace each placeholder with the real container." Give exact sizes: Header 70px fixed, KPI row 80px fixed (Distribute Contents Evenly across the 4 KPI tiles), Body fills remaining height and splits into a Left Vertical container (60% width) and Right Vertical container (40% width, itself split 50/50 top-to-bottom).
3. Worksheet placement: name which sheet goes in which container slot.
4. Filters: "Add each filter as a Single Value dropdown in the header. Right-click each → Apply to Worksheets → All Using This Data Source (since all 7 sheets share one source) — or Selected Worksheets, listing specific sheets, if sources differ."
5. Actions: "Dashboard menu → Actions → Add Action" with the exact source sheet, type, target sheet(s), and clearing = "Show All Values" for each action.
6. Sizing: "Set the dashboard to Fixed, 1400x900."
7. Report the complete instruction set, then ask the user to confirm once built — verify with `get-workbook-inventory`/`list-dashboards` afterward, but note that filter scope, action wiring, and clipping still need the user's visual confirmation.

### Example C: Missing Sheet During Assembly Instructions

**Situation:** The DASHBOARD ASSEMBLY SPEC names a sheet ("Segment Pie") that Worksheet Builder never actually confirmed as built — a dependency-order slip.

**What to do:** Do not write instructions referencing a sheet that doesn't exist. Report: "Sheet 'Segment Pie' doesn't exist in the workbook yet. Available sheets: [list]. Options: (1) proceed without it, (2) go back to Worksheet Builder to build it first, (3) substitute an existing sheet." Never silently drop it from the instructions without saying so.

### Example D: Two-Column Split with Fit Recommendations (no tool path for either)

**Situation:** 5 built sheets (KPI text, filled map, two stacked-area charts, one horizontal-ranked-bar chart), user wants "2 columns."

**Why this is instructions-only, not a tool call:** No Desktop command exists to place an existing sheet into a specific container/column, or to set a sheet's view Fit — this is expected under Viz Planner's advisory approach to assembly, not a workaround. See Platform Limitations: Dashboard Assembly in `SKILL.md`.

**Instructions to give:**
1. "Click New Dashboard, drag all 5 sheets onto the canvas, then set the dashboard to a fixed size, e.g. 1400x900."
2. Give a fit recommendation per chart type, with the exact menu path (right-click sheet → Fit → [option]): KPI text/map → Entire View; time-series (stacked area) → Fit Width; horizontal ranked bars → Fit Height; vertical bars → Fit Width.
3. Propose a concrete column grouping as an ASCII wireframe, plus the two-vertical-container instruction ("drag a Vertical container onto the canvas, then drop each sheet into the left or right slot as shown").
4. Ask the user to confirm once built.
