# Worked Examples

Three complete end-to-end examples demonstrating how the skill handles ambiguity, anti-pattern negotiation, and complex multi-calc builds.

***

## Example 1: Ambiguous Request

**User says:** "Show me how products are doing"

### Phase 1: Intent Classification

This is ambiguous. "How products are doing" could mean:
- **Ranking** — Which products are best/worst? (signal: "how...doing" implies performance judgment)
- **Temporal** — How are product sales trending over time?
- **Comparison** — How do products compare to each other?

**Resolution:** No explicit time reference, no "top/bottom" language. The most natural reading of "how are they doing" is performance status. But without a clear signal, ask:

> "I'm reading this as a ranking question (which products perform best/worst). If you meant 'how are products trending over time' or 'how do they compare on a specific metric', let me know."

**User clarifies:** "Yeah, which ones are selling the most"

**Reclassified:** Ranking (signal: "most")

### Phase 2: Datasource Metadata

`list-available-fields` returns:
- Product Name (STRING, 85 distinct values — high cardinality)
- Product Category (STRING, 4 values — low cardinality)
- Product Sub-Category (STRING, 17 values — medium cardinality)
- Sales (REAL, SUM)
- Order Date (DATE)
- Region (STRING, 4 values)

`resolve-field`: "products" → Product Sub-Category (17 values, reasonable for a ranked bar). Product Name is too high-cardinality for axis.

### Phase 3: Chart Decision

Ranking + 17 categories → **Sorted horizontal bar (TOP 10)**

Anti-pattern check:
- 3D? No. Pie? No. Dual axis? No. Non-zero start? No. Alphabetical sort? Will sort by value. All clear.

### Phase 4: Shelf Recipe

```
WORKSHEET: Top Product Sub-Categories by Sales
MARK TYPE: Bar
BUILD PATH: bind-template

COLUMNS: Sales | SUM
ROWS: Sub-Category
COLOR: Single color | #4E79A7
LABEL: Sales | SUM | Format: $#,##0
SORT: Sales | Descending | Sort by: SUM(Sales)
FILTERS: Sub-Category | TOP 10 by SUM(Sales)
TOOLTIP:
  - Sub-Category (bold)
  - Sales: $#,##0
  - Rank: [RANK calc]

CALCULATED FIELDS:
  - [Rank]: RANK(SUM([Sales])) — compute using Sub-Category

FORMATTING:
  - Hide column axis (values shown in labels)
  - Row height: comfortable for reading (no truncation)
  - Grid lines: off
```

### Phase 5: Execute

1. `author-calc` → create [Rank]
2. `bind-template` → horizontal bar, sorted
3. `refine-worksheet` → TOP 10 filter, label formatting

**Post-build verification:** Confirmed 10 bars showing, sorted descending, labels visible.

***

## Example 2: Anti-Pattern Override Negotiation

**User says:** "Make a pie chart showing sales by sub-category"

### Phase 1: Intent Classification

- Question type: Composition (signal: pie chart request implies part-to-whole)
- Primary measure: Sales
- Primary dimension: Sub-Category

### Phase 2: Datasource Metadata

`resolve-field`: Sub-Category has 17 distinct values.

### Phase 3: Chart Decision + Anti-Pattern Gate

User requests pie chart. Sub-Category has 17 values.

**Anti-pattern #2 triggered (CRITICAL): Pie chart with >5 slices.**

Response:

> "Pie charts fail beyond 5 slices (humans can't compare 17 angles accurately). I'll build a sorted horizontal bar instead, which shows the same ranking clearly. If you specifically need part-to-whole, I can do a treemap. Want me to override with the pie anyway?"

**User says:** "Actually a treemap would be great"

**Revised chart type:** Treemap (Composition + hierarchical)

### Phase 4: Shelf Recipe

```
WORKSHEET: Sales Composition by Sub-Category
MARK TYPE: Square (Treemap)
BUILD PATH: bind-template

SIZE: Sales | SUM
COLOR: Sales | SUM | Sequential palette (Blues: #c6dbef → #08519c)
LABEL: Sub-Category + Sales | SUM | Format: $#,##0
DETAIL: Sub-Category

TOOLTIP:
  - Sub-Category (bold)
  - Sales: $#,##0
  - % of Total: [Percent of Total calc] | Format: 0.0%

CALCULATED FIELDS:
  - [% of Total]: SUM([Sales]) / TOTAL(SUM([Sales])) — compute using Sub-Category

FORMATTING:
  - Border: white, 1px (separates tiles clearly)
  - Label: show for tiles >5% of total; hide for smaller tiles
```

### Phase 5: Execute

1. `author-calc` → create [% of Total]
2. `bind-template` → treemap
3. `refine-worksheet` → color palette, label threshold

**Post-build verification:** 17 tiles visible, sized by sales, darkest color = highest sales. Labels visible on major tiles.

***

## Example 3: Multi-Calc KPI Build

**User says:** "Build me a KPI tile for revenue that shows YoY change and whether we're on track vs. target. My target is $2.5M."

### Phase 1: Intent Classification

- Question type: Status/KPI (signal: "KPI", "on track", "target")
- Primary measure: Revenue (need to resolve)
- Comparison: vs. target ($2.5M) AND vs. last year (YoY)

### Phase 2: Datasource Metadata

`list-available-fields` returns:
- Revenue (REAL, SUM) — confirmed
- Order Date (DATE)
- No existing YoY or status calc found

`resolve-field`: "revenue" → `Revenue`

### Phase 3: Chart Decision

Status/KPI + single metric with context → **KPI tile (BAN + comparison + status)**

Anti-pattern check: All clear (no chart-type anti-patterns for KPI tiles).

### Phase 4: Shelf Recipe (Multi-Sheet KPI)

This requires 3 calculated fields and a parameter:

```
PARAMETER:
  - [Revenue Target] | Float | Default: 2500000 | Display: $#,##0

CALCULATED FIELDS:
  - [Revenue YTD]:
    SUM(IF YEAR([Order Date]) = YEAR(TODAY()) THEN [Revenue] END)

  - [Revenue LY]:
    SUM(IF YEAR([Order Date]) = YEAR(TODAY()) - 1 THEN [Revenue] END)

  - [YoY Change %]:
    ([Revenue YTD] - [Revenue LY]) / ABS([Revenue LY])

  - [Status]:
    IF [Revenue YTD] >= [Revenue Target] THEN "On Track"
    ELSEIF [Revenue YTD] >= [Revenue Target] * 0.9 THEN "Caution"
    ELSE "Alert"
    END
```

**Sheet 1: Primary Value**
```
WORKSHEET: Revenue KPI — Value
MARK TYPE: Text
BUILD PATH: manual (KPI tile layout not available in bind-template)

TEXT: [Revenue YTD] | Format: $#.##M (abbreviated)
FILTERS: Order Date | Relative | Year to Date

FORMATTING:
  - Font size: 48px, bold
  - Color: #333333
  - Alignment: center
  - Hide all axes, headers, gridlines
```

**Sheet 2: YoY Comparison**
```
WORKSHEET: Revenue KPI — YoY
MARK TYPE: Text
BUILD PATH: manual

TEXT: Custom label calc →
  IF [YoY Change %] > 0 THEN "▲ " + STR(ROUND([YoY Change %] * 100, 1)) + "% vs. LY"
  ELSE "▼ " + STR(ROUND(ABS([YoY Change %]) * 100, 1)) + "% vs. LY"
  END

COLOR: [YoY Change %] | Diverging (Red < 0 < Green) with icon

FORMATTING:
  - Font size: 14px
  - Hide all axes, headers
```

**Sheet 3: Status Indicator**
```
WORKSHEET: Revenue KPI — Status
MARK TYPE: Shape (custom: checkmark / warning / X)
BUILD PATH: manual

SHAPE: [Status] → On Track = ✓, Caution = ⚠, Alert = ✗
COLOR: [Status] → On Track = #59A14F, Caution = #F28E2B, Alert = #E15759
LABEL: [Status] (text label alongside icon — triple encoding)

FORMATTING:
  - Font size: 12px
  - Hide all axes, headers
```

**Sheet 4: Sparkline (Optional)**
```
WORKSHEET: Revenue KPI — Sparkline
MARK TYPE: Line
BUILD PATH: bind-template

COLUMNS: Order Date | MONTH | Continuous
ROWS: Revenue | SUM
FILTERS: Order Date | Last 12 months

FORMATTING:
  - Line color: #4E79A7, 2px
  - Hide ALL axes, headers, gridlines, zero line
  - Fixed axis range (don't auto-scale)
  - Size: minimal (120px wide x 40px tall)
```

### Phase 5: Execute

1. `author-calc` → create parameter [Revenue Target], then [Revenue YTD], [Revenue LY], [YoY Change %], [Status]
2. Build Sheet 1 (manual — `build-and-apply-worksheet`)
3. Build Sheet 2 (manual)
4. Build Sheet 3 (manual)
5. Build Sheet 4 (`bind-template` — simple line)
6. `refine-worksheet` on each — formatting, hide elements

**Post-build verification:**
- Sheet 1: Large revenue number visible, formatted as $X.XM
- Sheet 2: Arrow + percentage visible, colored correctly (green if positive)
- Sheet 3: Status icon + color + text all present (triple-encoded)
- Sheet 4: Sparkline shows 12-month trend, no axis clutter

**Note to user:** "These 4 sheets are designed to be composed on a dashboard (use Dashboard Blueprint to lay them out). Each sheet is one component of the full KPI tile."

***

## Pattern Summary

| Scenario | Key Skill Behavior |
|---|---|
| Ambiguous request | Classify best-guess, state interpretation, offer alternative, reclassify if user redirects |
| Anti-pattern triggered | Block critical, warn high, note medium. Present alternative. Accept override on high/medium only. |
| Multi-calc complex build | Author calcs in dependency order (parameter → base calcs → derived calcs → status). Build sheets individually. Note dashboard composition for multi-sheet outputs. |
