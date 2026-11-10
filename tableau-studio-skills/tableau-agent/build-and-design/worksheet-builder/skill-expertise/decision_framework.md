# Chart Type Decision Framework

## Question Type → Chart Type Mapping

This is deterministic. Given a question type and field characteristics, follow the branching logic below to arrive at exactly one chart type.

***

## 1. Temporal Questions

**Signal:** "over time", "trend", "by month/week/year", "changed", "growing"

| Condition | Chart Type |
|---|---|
| Single measure, continuous time (>8 periods) | **Line chart** |
| Single measure, ≤8 discrete periods | **Column chart** (vertical bar) |
| Multiple measures (2-3), same scale | **Multi-line chart** |
| Multiple measures, very different scales | **Separate charts** (never dual axis by default) |
| 4+ measures over time | **Small multiples** (sparkline grid) |
| Cumulative/running total emphasis | **Area chart** |
| Micro-trend (space-constrained, shape > values) | **Sparkline** |

***

## 2. Categorical Comparison

**Signal:** "by [category]", "compare", "across", "between", "which is bigger"

| Condition | Chart Type |
|---|---|
| 3-20 categories, one measure | **Horizontal bar** (sorted high to low) |
| >20 categories | **Horizontal bar** (TOP 10 + filter for rest) |
| 2 measures across categories | **Grouped bar** (side-by-side) |
| With target/benchmark | **Bar + reference line** |
| Precise value emphasis over magnitude | **Dot plot** |
| Time periods as categories (Q1-Q4) | **Vertical column** (left-to-right time order) |

***

## 3. Composition

**Signal:** "breakdown", "parts of", "share", "proportion", "mix", "what makes up"

| Condition | Chart Type |
|---|---|
| Parts across categories | **Stacked bar** |
| Parts changing over time | **Stacked area** (caution: only baseline is accurate) |
| Hierarchical/nested categories | **Treemap** |
| Sequential buildup to total | **Waterfall** |
| Simple 2-3 parts, whole is the point | **Pie** (rare exception; prefer stacked bar) |
| Proportions more important than absolutes | **100% stacked bar** |
| Only one dimension available (no sub-breakdown field) | **Stacked bar with a single bar**: measure on the axis, the one dimension straight on Color, nothing on the other axis. Never a pie by default — see the Pie chart gate below before choosing pie. |

**Pie chart gate (ALL must be true):**
1. Exactly 2-5 segments (ideally 2-3)
2. Segments sum to a meaningful whole
3. Part-to-whole IS the primary message
4. Values labeled clearly
5. No 3D effects
6. Not comparing multiple pies

***

## 4. Distribution

**Signal:** "spread", "distribution", "range", "histogram", "variance", "outliers"

| Condition | Chart Type |
|---|---|
| Single variable frequency | **Histogram** |
| Compare distributions across categories | **Box plot** |
| Full distribution shape needed | **Violin plot** |
| Small dataset (<50 points) | **Dot plot** (strip) |

***

## 5. Correlation

**Signal:** "relationship", "correlation", "vs.", "impact of X on Y", "associated with"

| Condition | Chart Type |
|---|---|
| Two continuous variables | **Scatter plot** |
| + third variable (size) | **Bubble chart** (size variable must never be negative; a signed third variable goes on diverging Color) |
| + categorical grouping | **Scatter with color** (max 5-6 colors) |
| Many variable pairs | **Heatmap** (correlation matrix) |

***

## 6. Ranking

**Signal:** "top", "bottom", "best", "worst", "leaders", "laggards", "rank"

| Condition | Chart Type |
|---|---|
| Simple top/bottom N | **Sorted horizontal bar** |
| Rank change between two periods | **Slope chart** |
| Emphasis on endpoint values | **Lollipop chart** |

***

## 7. Sequential/Flow

**Signal:** "funnel", "flow", "stages", "conversion", "bridge", "waterfall", "timeline", "Gantt", "duration", "schedule"

| Condition | Chart Type |
|---|---|
| Step-by-step additions/subtractions | **Waterfall** |
| Flow between categories/stages | **Sankey** (extension required) |
| Conversion drop-off at stages | **Funnel** (sorted bar with stage labels) |
| Duration/elapsed time per entity (start + end dates) | **Gantt chart** |
| Project timeline or schedule visualization | **Gantt chart** |

***

## 8. Geographic

**Signal:** "by state", "by country", "where", "map", "location", "region" (geographic)

| Condition | Chart Type |
|---|---|
| Value by polygon region (state, country) | **Filled map** (choropleth) |
| Discrete locations + magnitude | **Point map** (bubble; size measure must never be negative) |
| Density/concentration | **Heat map** (geographic) |
| <5 regions total | **Bar chart** (more precise than map) |

***

## 9. Status/KPI

**Signal:** "current", "are we on track", "status", "KPI", "how are we doing", "metric"

| Condition | Chart Type |
|---|---|
| Single metric with context | **KPI tile** (BAN + comparison + sparkline) |
| Actual vs. target | **Bullet chart** |
| In naturally bounded range (0-100%) | **Gauge** (sparingly) |

***

## Audience Overrides

When audience is known, apply these modifications to chart selection:

### Executive (5-30 second time budget)
- **Suppress:** Scatter, box plot, histogram, heatmap, violin, complex stacked
- **Prefer:** KPI tiles, simple line (1-2 series), sorted bars (top 5), status indicators
- **Max charts per worksheet context:** Keep it scannable

### Analyst (3-15 minute time budget)
- **Suppress:** Over-simplified gauges, single-number-only views
- **Prefer:** Scatter, distributions, small multiples, heatmaps
- **Allow:** Higher complexity, more marks, deeper drill paths

### Operations (5-30 seconds, alert-driven)
- **Suppress:** Complex analytics, historical deep dives
- **Prefer:** Real-time KPIs, status dashboards (green/red), simple trends, gauges (if naturally bounded)

### External/Public (30-90 seconds)
- **Suppress:** Statistical charts, jargon-heavy labels, box plots
- **Prefer:** Simple bars, clean lines, heavy annotation, minimal chart types

### Manager (1-3 minutes)
- **Suppress:** High-density analytical charts
- **Prefer:** Trends with comparisons, category breakdowns, light filtering

***

## Ambiguity Resolution

When the question could map to two types:

| Ambiguity | Resolution |
|---|---|
| Temporal vs. Categorical ("sales by quarter") | If ≤8 periods and comparison is the point → Column. If >8 or trend shape matters → Line. |
| Ranking vs. Comparison ("sales by region") | If user says "top" or "best" → Ranking (sorted). If neutral → Comparison (still sort by value). |
| Composition vs. Comparison ("breakdown by category") | If "parts of whole" language → Composition (stacked). If "which is bigger" → Comparison (bar). |
| KPI vs. Temporal ("how are sales doing") | If "right now" / current state → KPI. If "lately" / over a period → Temporal. |

Always state your interpretation: "I'm reading this as a [type] question. If you meant [alternative], let me know."
