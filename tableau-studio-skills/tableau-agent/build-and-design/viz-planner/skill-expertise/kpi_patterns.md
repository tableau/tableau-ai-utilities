# KPI & Metric Patterns

BAN (Big-Ass Number) display formats, comparison logic, sparkline inclusion rules, and KPI hierarchy design for Tableau dashboards.

***

## KPI Hierarchy

Every business dashboard has a metric hierarchy. Define it before placing anything on the layout.

| Tier | Role | Count | Display | Position |
|---|---|---|---|---|
| **Primary** | Metrics the audience checks FIRST. The reason they opened the dashboard. | 2-4 | BAN with comparison (large, bold, color-coded delta) | KPI zone, top of dashboard |
| **Secondary** | Supporting context that explains or qualifies primary KPIs | 2-4 | Smaller BAN or inline with charts | Below primary, or right-side panel |
| **Detail** | Breakdown values visible within charts | N/A | Chart labels, axis values, tooltips | Within viz zone |

**How to identify Primary KPIs:**
- What number does the audience quote in meetings?
- What number triggers action if it moves?
- What's the first question they ask on Monday morning?

**How to identify Secondary KPIs:**
- What explains WHY the primary moved?
- What context is needed to interpret the primary?
- What's the "next question" after seeing the primary?

***

## BAN Display Format

Each KPI tile follows this structure:

```
+------------------------+
| METRIC LABEL           |  <- 10-11px, uppercase or title case, #666666
| $1.24M                 |  <- 28-48px, bold, #333333 (the number)
| ^ 12.3% vs. LY        |  <- 11-12px, color-coded (green up / red down)
| Target: $1.30M         |  <- 10px, #999999 (optional benchmark)
+------------------------+
```

### Size by Tier

| Tier | Number Size | Label Size | Card Width |
|---|---|---|---|
| Primary KPI | 28-36px bold | 10-11px | Equal share of KPI zone (e.g., 25% each for 4 KPIs) |
| Secondary KPI | 20-24px bold | 10px | Smaller card or inline |
| Inline metric | 14-16px bold | 9-10px | Within chart area |

### Comparison Line Rules

The comparison line (delta) is what makes a KPI actionable. A number without context is just a number.

| What to Compare | Format | When |
|---|---|---|
| vs. Same Period Last Year | "^12.3% vs. LY" or "+$148K vs. LY" | Default for most business metrics |
| vs. Prior Period | "^3.1% vs. last month" | Sequential process, monthly reviews |
| vs. Target/Goal | "92% of target" or "-$80K vs. goal" | Target-driven KPIs |
| vs. Baseline | "+24% since launch" | Campaign or initiative tracking |

**Comparison formatting:**
- Up/positive: green (#59A14F) with up arrow (^) or triangle
- Down/negative: red (#E15759) with down arrow (v) or triangle
- Flat/neutral: gray (#9C9C9C) with dash (-)
- **Reverse for cost metrics:** Lower is better, so down = green, up = red

***

## Comparison Period Selection Logic

Choose the default comparison based on business context:

| Context | Default Comparison | Why |
|---|---|---|
| Ongoing operations (sales, revenue) | vs. same period last year (YoY) | Normalizes seasonality |
| Campaign / product launch | vs. pre-launch baseline | Shows lift |
| Target-driven (quotas, OKRs) | vs. target / goal | Shows gap to close |
| Sequential process (pipeline) | vs. prior period (MoM, WoW) | Shows momentum |
| Seasonal business | vs. same period last year | Always YoY to control for season |
| Growth startups | vs. prior period (MoM) | Growth rate is the metric |
| Real-time operations | vs. same time yesterday or trailing average | Anomaly detection |

**Multiple comparisons:** If both YoY and vs. Target are relevant, show the more actionable one as the primary comparison line, and put the other in the tooltip.

***

## Sparkline Inclusion Rules

Sparklines add trend context to KPI tiles. They answer "is this going up or down?" without requiring a full chart.

### When to Include Sparkline in KPI Card

| Include | Don't Include |
|---|---|
| Metric has meaningful time trend | Metric is a snapshot (count of active users right now) |
| Audience is Manager or Analyst | Audience is Executive (scan-only; sparkline adds noise) |
| Time periods available (>6 periods) | Fewer than 6 data points (not enough for a shape) |
| Trend direction matters for interpretation | Only the current value matters |

### Sparkline Specifications

```
Size: 80-120px wide x 20-30px tall
Color: Primary blue (#4E79A7), single line, no fill
Periods: Last 12 (months/weeks/days depending on grain)
Markers: None, OR single endpoint marker (current value)
Axis: Hidden (sparklines show shape, not precise values)
Grid: None
Labels: None (the BAN above provides the number)
```

### Sparkline Position in KPI Card

```
+------------------------+
| METRIC LABEL           |
| $1.24M                 |
| ^ 12.3% vs. LY        |
| [__________/^^]        |  <- Sparkline at bottom of card
+------------------------+
```

OR (compact variant):

```
+----------------------------------+
| METRIC LABEL  [__/^^]            |  <- Sparkline right-aligned
| $1.24M        ^ 12.3% vs. LY    |
+----------------------------------+
```

***

## KPI Card Styling

### Background

| Style | When | Hex |
|---|---|---|
| Light gray card | Default. Subtle container differentiation. | #F8F9FA |
| White card (no background) | When dashboard background is already gray | #FFFFFF |
| Status-colored card | Operations dashboards with health status | Green/Yellow/Red at 10% opacity |

### Borders and Spacing

- Card border: none (use background contrast) or 1px #E0E0E0
- Inner padding: 12px all sides
- Between cards: 8-12px gap
- Cards in a row: always same height (visual consistency)

***

## Number Formatting Rules

| Metric Type | Format | Example |
|---|---|---|
| Revenue/Sales (large) | $#.#M or $#.#K | $2.4M, $847K |
| Revenue (small, <$1K) | $#,##0 | $892 |
| Percentage | #.#% (one decimal) | 14.2%, 3.1% |
| Count (large) | #.#K or #.#M | 24.5K, 1.2M |
| Count (small, <1000) | #,##0 | 847 |
| Ratio | #.## | 3.14, 0.87 |
| Change (absolute) | +$#.#M / -$#.#M | +$148K, -$23K |
| Change (relative) | +#.#% / -#.#% | +12.3%, -4.1% |

**Formatting rules:**
- Always abbreviate large numbers (M, K). Never show $2,400,000 in a BAN.
- Always show sign (+/-) on change values. No sign = ambiguous.
- One decimal place for percentages. Two decimals only for very small percentages (<1%).
- Consistent precision across all KPI cards (don't mix $2.4M with $847,231).

***

## KPI Calculated Fields

Common calculations needed for KPI tiles:

### YTD Value
```
// [Sales YTD]
IF YEAR([Order Date]) = YEAR(TODAY()) 
   AND [Order Date] <= TODAY()
THEN [Sales] 
END
```

### YoY Change (%)
```
// [YoY Change]
(SUM([Sales This Year]) - SUM([Sales Last Year])) 
/ ABS(SUM([Sales Last Year]))
```

### vs. Target (%)
```
// [vs Target %]
(SUM([Sales]) - [Target Parameter]) / [Target Parameter]
```

### Status Classification
```
// [KPI Status]
IF SUM([Sales]) >= [Target Parameter] THEN "On Track"
ELSEIF SUM([Sales]) >= [Target Parameter] * 0.9 THEN "At Risk"
ELSE "Off Track"
END
```

### Period-over-Period (Table Calc)
```
// [PoP Change]
(ZN(SUM([Sales])) - LOOKUP(ZN(SUM([Sales])), -1)) 
/ ABS(LOOKUP(ZN(SUM([Sales])), -1))
```

***

## Multi-KPI Layout Options

### 3 Primary KPIs (Most Common)

```
+----------+----------+----------+
| Sales    | Profit   | Margin   |
| $2.4M   | $340K    | 14.2%    |
| ^8% YoY | ^3% YoY  | v0.5pp   |
+----------+----------+----------+
```
- Equal thirds, 60-80px height

### 4 Primary KPIs

```
+--------+--------+--------+--------+
| Rev    | Orders | AOV    | NPS    |
| $2.4M  | 24.5K  | $98    | 72     |
| ^8%    | ^12%   | v3%    | ^2pts  |
+--------+--------+--------+--------+
```
- Equal quarters, 60-80px height

### 2 Primary + 2 Secondary (Stacked)

```
+-------------------+-------------------+
| REVENUE           | CUSTOMERS         |
| $2.4M  ^8% YoY   | 24.5K  ^12% YoY  |
+-------------------+-------------------+
| Avg Order: $98    | Retention: 87%    |  <- Secondary, smaller
+-------------------+-------------------+
```

***

## KPI Interaction (When Applicable)

| Audience | KPI Interactivity |
|---|---|
| Executive | Non-interactive (display only) OR click to navigate to detail page |
| Manager | Click KPI to filter dashboard to that metric's detail |
| Analyst | Click KPI to navigate; hover for tooltip with breakdown |
| Operations | Click to open alert detail or ticket |

**KPI as filter action source:**
- Works when KPIs represent segments (e.g., Revenue by Region cards)
- Click "West: $820K" -> filters all charts to West
- Must have clear "selected" state (border, background change)
- Always provide "clear selection" / "show all" reset
