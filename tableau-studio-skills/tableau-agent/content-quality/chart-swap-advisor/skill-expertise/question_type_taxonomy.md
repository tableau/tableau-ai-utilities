# Question Type Taxonomy (Locked, 9 Types)

Every classification cites this taxonomy. Duplicates Worksheet Builder's `decision_framework.md` intentionally so both skills stay in sync. If the taxonomy changes in Worksheet Builder, update this file in the same commit.

## Classification Rules (Evaluated in Order)

Rules evaluated top-to-bottom; first match wins. Every classification carries a High / Medium / Low confidence tag per the signal-count rule below.

## The 9 Types

### 1. Temporal

**Signal words.** "trend," "over time," "by month," "by year," "seasonality," "growth rate," "time series."

**Field pattern.** Continuous date or datetime dimension on Columns AND one or more measures on Rows. Discrete date pill counts as Temporal only when the pill's continuous underlying field carries the same intent.

**Default chart.** Line.

**Alternatives.** Area (for stacked composition-over-time), Bar (for period-over-period comparison), Sparkline (for compact multi-metric).

**Anti-patterns.** Pie chart over time. 3D area. Radar for time series.

### 2. Categorical

**Signal words.** "compare," "across," "by category," "by segment," "by product," "by region."

**Field pattern.** Discrete dimension on Rows or Columns AND one measure on the other axis.

**Default chart.** Horizontal sorted bar.

**Alternatives.** Vertical bar (when the dimension label is short), Dot plot (for many categories), Lollipop (for a small number of high-emphasis categories).

**Anti-patterns.** Line chart across categorical dimension. Pie for >5 categories.

### 3. Composition

**Signal words.** "breakdown," "share," "proportion," "makes up," "percentage of total."

**Field pattern.** Single measure summed to 100% across a discrete dimension. Often paired with a Percent-of-Total calc or Quick Table Calc.

**Default chart.** Stacked bar. Treemap for high-cardinality dimensions.

**Alternatives.** 100% stacked bar (for share comparison across a secondary dimension), Donut with hole for KPI overlay (rare).

**Anti-patterns.** Pie with >5 slices. 3D anything.

### 4. Distribution

**Signal words.** "distribution," "spread," "histogram," "how many fall in," "range of values."

**Field pattern.** Single measure with binning intent. Often paired with a bins field or a percentile calc.

**Default chart.** Histogram.

**Alternatives.** Box plot (for outlier emphasis), Density plot (for continuous distributions).

**Anti-patterns.** Bar chart with categorical dimension mislabeled as distribution. Pie for spread.

### 5. Correlation

**Signal words.** "relationship," "vs.," "correlation," "how X affects Y," "scatterplot."

**Field pattern.** Two measures, one on Rows and one on Columns.

**Default chart.** Scatter.

**Alternatives.** Scatter with trend line (for regression emphasis), Connected scatter (for correlation over time).

**Anti-patterns.** Text table for correlation. Scatter with >10,000 marks and no aggregation.

### 6. Ranking

**Signal words.** "top," "bottom," "rank," "best," "worst," "biggest," "smallest," "leaders," "laggards."

**Field pattern.** Measure on Rows or Columns AND discrete dimension on the other AND a sort spec on the measure. Often paired with a Top N filter or a RANK calc.

**Default chart.** Sorted horizontal bar with Top N filter.

**Alternatives.** Bump chart (for rank-over-time), Dot plot (for compact ranking display).

**Anti-patterns.** Unsorted bar for ranking. Pie chart for top-N.

### 7. Geographic

**Signal words.** "by state," "by city," "by country," "map," "where," "by region," "by ZIP."

**Field pattern.** Dimension with a geographic role assigned (State, City, Country, ZIP, Latitude/Longitude generated pair).

**Default chart.** Filled map (choropleth).

**Alternatives.** Point map (for lat/long-based data), Density map (for high-cardinality point data), Symbol map with size encoding (for measure-scaled points).

**Anti-patterns.** Choropleth with count-based measure (misleading; density normalization required). Filled map at ZIP level with sparse data.

### 8. Status/KPI

**Signal words.** "KPI," "target," "actual vs.," "on track," "at risk," "goal," "threshold."

**Field pattern.** One measure, minimal dimensions, often paired with a target parameter or a status calc.

**Default chart.** KPI tile (BAN + delta) OR bullet chart.

**Alternatives.** Gauge (avoid; Tableau's gauge implementation is space-inefficient). Sparkline with target line overlay.

**Anti-patterns.** Multi-measure KPI (route to a dashboard, not a single worksheet). Gauge for anything.

### 9. Sequential

**Signal words.** "funnel," "pipeline," "stages," "flow," "conversion," "drop-off."

**Field pattern.** Ordered discrete dimension with a natural sequence (funnel steps, pipeline stages, conversion phases). Often paired with a Stage field and a sequence calc.

**Default chart.** Funnel (sorted bar with stage labels).

**Alternatives.** Sankey (for multi-source-to-target flow, but Tableau native support is limited). Stage-transition matrix (for conversion between named stages).

**Anti-patterns.** Pie for funnel. Line chart for sequential stages.

## Confidence Tagging (Three-Tier)

Applied to every classification. Matches Logic Explainer's convention.

- **High confidence.** Descriptive worksheet name AND matched field pattern AND matched signal words in worksheet caption or user prompt all agree.
- **Medium confidence.** One or two of the three signals present, one contradicts or is missing.
- **Low confidence.** None of the three signals cleanly present, or two contradict each other. Report as "closest match is X but the signal is weak; consider re-running with a stated question or audience."

## Ambiguity Resolution

**Two-type conflict.** If the field pattern matches two types (e.g., continuous date on Columns + discrete dimension on Rows), assign the type that matches the signal words. If signal words are absent or ambiguous, ask one clarifying question per HC#9.

**No-match case.** If no type matches with even Low confidence, refuse classification and route the user to `worksheet-builder` for a fresh chart design.

## Signal-Word Table (Quick Reference)

| Type | Primary Signal Words |
|---|---|
| Temporal | trend, over time, by month, by year, seasonality, growth rate, time series |
| Categorical | compare, across, by [dimension], segment, category |
| Composition | breakdown, share, proportion, makes up, percentage of |
| Distribution | distribution, spread, histogram, range, fall in |
| Correlation | relationship, vs., correlation, affects, scatterplot |
| Ranking | top, bottom, rank, best, worst, biggest, smallest, leaders, laggards |
| Geographic | by state, by city, by country, map, where, by region, by ZIP |
| Status/KPI | KPI, target, actual vs., on track, at risk, goal, threshold |
| Sequential | funnel, pipeline, stages, flow, conversion, drop-off |

## Refuse to Fabricate

Never assign a High confidence tag when only one signal is present. Never invent a signal word that isn't in the user's prompt or worksheet metadata. Never classify a chart into a type it doesn't match just to produce a recommendation; refuse and route to `worksheet-builder` per HC#4.
