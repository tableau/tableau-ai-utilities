# Anti-Pattern Catalog (Locked)

Every Chart Swap Advisor run evaluates the current chart against every entry in this catalog. Auto-block severity cannot be overridden by user pressure per HC#11.

## Severity Tiers

- **Auto-Block.** Recommendation stays Block regardless of user pressure. Chart is unacceptable for stakeholder-facing dashboards. Rationale must cite this catalog entry.
- **Warning.** Chart is suboptimal; swap recommended. User can Keep in Desktop if they have context that overrides the general rule.
- **Info.** Chart is defensible but worth reviewing.

## Auto-Block Anti-Patterns

### AB-1: 3D Chart (Any Type)

**Detection signal.** Mark type or shelf-placement includes 3D encoding (Tableau's 3D chart types include 3D pie, 3D bar, 3D area). Rarely present in Tableau Studio natively; more common in ported Excel or PowerPoint imports.

**Why it's blocked.** 3D perspective distorts data reading. Every 3D chart has a superior 2D alternative. Confirmed portfolio-wide anti-pattern.

**Recommendation.** Swap to the 2D equivalent of the current type (3D pie → treemap or stacked bar; 3D bar → 2D bar; 3D area → 2D area or line).

### AB-2: Pie Chart with >5 Slices

**Detection signal.** Mark type is Pie AND the number of dimension values (slices) exceeds 5.

**Why it's blocked.** Pie charts become unreadable beyond 5 slices. Angle comparison degrades sharply. Stacked bar or treemap serves the same Composition question with better readability.

**Recommendation.** Swap to stacked bar (when slice order matters) or treemap (when hierarchy is available).

### AB-3: Word Cloud in Stakeholder-Facing Dashboard

**Detection signal.** Mark type is Text with text sizing driven by measure AND worksheet is placed on a dashboard.

**Why it's blocked.** Word clouds are ambiguous, hard to compare, and rarely answer a decision-oriented question. Fine for exploratory work; unacceptable for stakeholder decision surfaces.

**Recommendation.** Swap to sorted bar (Ranking) or treemap (Composition).

### AB-4: Packed Bubbles in Stakeholder-Facing Dashboard

**Detection signal.** Mark type is Circle with size encoding driven by measure AND worksheet is placed on a dashboard AND no positional axis carries meaning.

**Why it's blocked.** Packed bubbles obscure exact comparison and don't scale beyond a small number of items. Fine for aesthetic exploration; unacceptable for stakeholder decision surfaces.

**Recommendation.** Swap to sorted bar (Ranking) or treemap (Composition, when hierarchy exists).

### AB-5: Radar Chart

**Detection signal.** Radar-shaped chart authored via calc-heavy shelf placement (Tableau has no native radar mark; radar charts appear as multi-measure line charts with polar-axis calcs).

**Why it's blocked.** Radar charts require the reader to compare enclosed areas, which is a poor visual task. Every use case has a superior alternative (small-multiples bar for multi-metric comparison, sorted bar for ranking).

**Recommendation.** Swap to small-multiples bar (each metric its own bar chart) or a scoring KPI tile with delta.

### AB-6: Gauge Chart

**Detection signal.** Gauge-shaped chart authored via calc-heavy Automatic mark placement (Tableau has no native gauge mark).

**Why it's blocked.** Gauges are space-inefficient and hard to read at a glance. KPI tiles or bullet charts serve the same Status/KPI question far better.

**Recommendation.** Swap to KPI tile (BAN + delta) or bullet chart.

## Warning Anti-Patterns

### W-1: Dual-Axis When Single-Axis Suffices

**Detection signal.** Two measures on Rows or Columns with dual-axis synchronized AND the two measures share the same unit and scale.

**Why it's a warning.** Dual-axis is powerful when two measures have different units or scales (e.g., Sales in dollars + Profit Ratio in percent). When both measures are in the same unit and scale (e.g., Sales + Profit both in dollars), single-axis with a color-encoded measure name is clearer.

**Recommendation.** Swap to single-axis with the two measures color-encoded. Preserve dual-axis if the user cites a specific decision that requires two independent scales.

**Keep condition.** Two measures with different units or different orders of magnitude (>10x scale difference) → Keep dual-axis; recommendation is Info-tier only.

### W-2: Executive Audience with Analytical Chart

**Detection signal.** User states audience is Executive AND current chart is Scatter, Distribution, Correlation, or a text-heavy exploratory view.

**Why it's a warning.** Executive audience has a 5-30 second time budget per Viz Planner's audience taxonomy. Analytical charts require analytical time. A mismatch produces stakeholder frustration.

**Recommendation.** Swap to KPI tile with the single answer, or a sorted bar showing the top-5 outliers. Preserve the scatter as a downstream drill-in worksheet if the executive dashboard has a "see detail" link.

### W-3: Text Table When a Chart Would Answer Faster

**Detection signal.** Mark type is Text AND question type is Temporal, Ranking, or Correlation.

**Why it's a warning.** Text tables serve reference lookup and detailed number verification. Temporal/Ranking/Correlation questions read faster with visual encoding.

**Recommendation.** Swap to the question-type default chart (Line for Temporal, sorted bar for Ranking, scatter for Correlation). Preserve the text table as a companion detail view if the user cites a compliance or audit requirement.

### W-4: Categorical Chart with Discrete Date on Columns

**Detection signal.** Mark type is Bar AND Columns contains a discrete date pill.

**Why it's a warning.** Discrete date pills on bars produce categorical-looking output for temporal data. Line chart with continuous date reads faster. Bar chart with discrete date is defensible only when period-over-period comparison is the primary question.

**Recommendation.** Swap the discrete date pill to continuous, or swap the mark to Line. Preserve if user cites period-over-period comparison as the primary intent.

### W-5: Choropleth with Count-Based Measure

**Detection signal.** Filled map (choropleth) AND the measure is a raw count (Number of Records, COUNT(*), COUNTD(ID)).

**Why it's a warning.** Choropleths with count-based measures over-emphasize high-population regions and mislead about density or rate. Normalization is almost always required.

**Recommendation.** Swap to a rate-based measure (count / population, or count / area). Preserve the choropleth type; swap the underlying measure.

### W-6: Multi-Measure KPI in a Single Worksheet

**Detection signal.** Question type is Status/KPI AND worksheet has 3+ measures on the Marks card.

**Why it's a warning.** Status/KPI is a single-decision question. Multiple measures on one worksheet dilute the answer. Route to multiple KPI worksheets in a dashboard grid, one per measure.

**Recommendation.** Split into separate worksheets, one per KPI. Route the assembly to `viz-planner` for dashboard-level KPI grid design.

### W-7: Histogram Used When Outlier Emphasis Is the Real Question

**Detection signal.** Question type is Distribution AND user language or worksheet caption emphasizes outliers/extremes ("outlier," "spread by group," "compare distributions across categories") AND current mark is a plain bar-based histogram with no per-category breakdown.

**Why it's a warning.** A single histogram shows overall shape but not per-group outliers or spread comparisons. Box plot serves outlier-emphasis and per-category comparison better; density plot serves smooth continuous-distribution reading better.

**Recommendation.** Swap to box plot (outlier/per-category emphasis) or density plot (continuous, single-group distributions). Preserve histogram if the question is strictly "how many fall in this range" with no grouping or outlier intent.

## Info Anti-Patterns

### I-1: Chart Complexity vs. Audience Time Budget

**Detection signal.** Chart has 5+ measures OR 4+ dimensions AND no audience is stated.

**Why it's Info.** Complexity is a signal, not a fault. If the audience is Analyst-tier (per Viz Planner's audience taxonomy), complexity is fine. If Manager or Executive, complexity may need to be reduced.

**Recommendation.** Ask the user to state the audience, then rerun with HC#12 audience-honoring logic. If Analyst, mark as Keep with Info note. If Manager/Executive, upgrade to Warning.

### I-2: Sort Order Not Specified for Ranking

**Detection signal.** Question type is Ranking AND no explicit sort spec is set on the measure.

**Why it's Info.** Tableau may default-sort ascending in ways that don't match the question. Ranking questions almost always want descending by measure.

**Recommendation.** Add an explicit sort spec on the measure in the correct direction.

## Anti-Pattern Match Rules

- Multiple anti-patterns can fire on the same chart. All fire; verdict is the highest severity.
- Auto-Block trumps Warning trumps Info.
- If no anti-pattern fires and the classification recommends the current chart type, verdict is Keep.
- If no anti-pattern fires but the classification recommends a different chart type, verdict is Swap Recommended (Warning-tier by default; Info-tier if the current chart is a defensible alternative per the taxonomy's "Alternatives" section).
- If no anti-pattern fires and the classification is Low-confidence with no clean type match, verdict is Keep with `recommended_chart_type: null` and an explicit low-confidence non-endorsement rationale (see `chart_recommendation_catalog.md`'s locked default). This is not the same as a confident Keep and must never be rendered identically to one.

## Refuse to Fabricate

Never invent an anti-pattern to reach a Swap Recommended verdict. Every anti-pattern cited in a recommendation must map to a specific entry in this catalog. If a chart has a genuinely novel design problem not covered here, note it in the report as a Low-confidence Info-tier observation and flag for catalog revision, but do not invent an anti-pattern ID.
