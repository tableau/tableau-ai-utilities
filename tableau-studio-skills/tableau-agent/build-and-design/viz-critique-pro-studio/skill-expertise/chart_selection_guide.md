# Domain 3: Chart Usage (Locked)

Evaluates whether each chart on the dashboard is the right chart type for its question. Shares the 9-type question taxonomy with `chart-swap-advisor`; this domain scores the aggregate dashboard-level fit rather than per-worksheet fit.

## 9-Type Question Taxonomy (Shared)

| Type | Signal Words / Field Combinations | Default Chart |
|---|---|---|
| Temporal | trend, over time, by month/year | Line |
| Categorical | compare, across, by [dimension] | Horizontal sorted bar |
| Composition | breakdown, share, proportion | Stacked bar or treemap |
| Distribution | distribution, spread, histogram | Histogram |
| Correlation | relationship, vs., correlation | Scatter |
| Ranking | top, bottom, rank, best/worst | Sorted horizontal bar + Top N |
| Geographic | by state/city/country, map, where | Filled map |
| Status/KPI | KPI, target, actual vs., on track | KPI tile or bullet chart |
| Sequential | funnel, pipeline, stages | Funnel |

Full taxonomy detail lives in `chart-swap-advisor` reference files. This domain uses the same rules.

## Score Anchors

| Score | Description |
|---|---|
| 10 | Every chart matches its inferred question. No anti-patterns. |
| 8-9 | 90%+ of charts match. One minor mismatch or Info-tier anti-pattern (e.g., unsorted ranking bar). |
| 6-7 | 70-89% match. One Warning-tier anti-pattern present. |
| 4-5 | 50-69% match. Multiple Warning-tier anti-patterns, or one Auto-Block. |
| 2-3 | Under 50% match. Auto-Block present (3D, pie greater than 5, word cloud in stakeholder context, radar, gauge). |
| 1 | Dashboard-wide chart-type failure (e.g., all-text tables for a decision dashboard, or all pie charts). |

## Anti-Patterns (Auto-Block on Sight)

Any of the following visible in the image caps Domain 3 at 4/10 and triggers a Warning-tier note. Multiple simultaneous auto-blocks compound to Weak (2-3):

- **3D chart of any type.** Every 3D chart has a superior 2D alternative.
- **Pie chart with 6+ slices.** Angle comparison degrades sharply beyond 5.
- **Word cloud on stakeholder-facing dashboards.** Font-size perception is far less accurate than length/position encoding.
- **Packed bubbles on stakeholder-facing dashboards.** Obscures exact comparison.
- **Radar chart.** Enclosed-area comparison is a poor visual task.
- **Gauge chart.** Space-inefficient; KPI tile or bullet chart serves the same purpose better.

**Genre exception (Data Art / Infographic only).** When Genre Detection (see `SKILL.md`) classifies the piece as Data Art / Infographic, the word-cloud and packed-bubble Auto-Blocks do not fire automatically if the chart is caption-paired (a nearby sentence or label states the intended read, e.g., "font size = total points"). Score the chart instead on whether the expressive choice serves the narrative: does it draw the eye to the right emphasis, does the caption resolve the ambiguity font-size/bubble-size otherwise creates. 3D, pie 6+, radar, and gauge stay Auto-Blocked regardless of genre — those degrade readability independent of narrative intent, so no genre gets a pass on them.

## Warning-Tier Anti-Patterns

Any of the following visible caps Domain 3 at 7/10:

- **Dual-axis when single-axis suffices.** Two measures in the same unit and scale.
- **Executive audience with analytical chart.** Scatter, histogram, or correlation on an Executive dashboard.
- **Text table when a chart would answer faster.** Temporal, Ranking, or Correlation question rendered as Text.
- **Choropleth with count-based measure.** Overstates larger regions without normalization.
- **Multi-measure KPI in a single worksheet.** Dilutes the answer.
- **Discrete date on Columns with Bar mark for Temporal question.** Reads categorical for temporal data.
- **Histogram when outlier-per-category emphasis is the real question.** Ranking or box-plot serves that intent better.

## Info-Tier Observations

Note in the rationale; do not cap the score:

- Chart complexity vs. audience time budget (defer to Domain 1 for the audience scoring).
- Sort order not specified for a Ranking chart (Tableau default may not match intent).

## Calibration Examples

**Example 3.1 → Score 10.** Dashboard has 6 charts. Line chart for a temporal trend, sorted horizontal bar for a categorical comparison, filled map for geographic distribution, KPI tile with delta for status, scatter for a correlation on a downstream drill worksheet, funnel for a pipeline. Every chart matches its inferred question. No anti-patterns fire.

**Example 3.2 → Score 7.** Dashboard has 5 charts. One horizontal bar for ranking has no visible sort. One line chart with two same-unit measures on dual-axis. Signal: I-2 sort-order Info-tier fires; W-1 same-unit dual-axis Warning fires. One clear Warning-tier anti-pattern.

**Example 3.3 → Score 4.** Dashboard has 4 charts. One is a pie with 7 slices for a Composition question. One is a text table for a Temporal question. Signal: AB-2 Auto-Block fires (pie greater than 5); W-3 Warning fires (text on Temporal). Multiple Warning-tier plus one Auto-Block caps score at 4.

**Example 3.4 → Score 2.** Dashboard has 3 charts, all 3D pies with 6+ slices. Signal: AB-1 Auto-Block fires on every chart; AB-2 Auto-Block fires on every chart. Dashboard-wide failure.

## Aggregate Scoring Discipline

Domain 3 is a dashboard-level score, not a per-worksheet score. Aggregate the individual chart evaluations:

- Count total charts visible in the image.
- For each, classify against the 9-type taxonomy and evaluate anti-patterns.
- Weight the aggregate score by chart prominence: primary KPI tile mismatch weighs more than a secondary supporting chart mismatch.

Cite specific chart references in the rationale (e.g., "Chart 3 (Regional Sales) uses a stacked bar for Composition, correct; Chart 4 (Rep Ranking) uses an unsorted bar, downgrade to 7").

**Wide dashboards (10+ charts).** Evaluate every chart individually; do not sample. Group findings by chart-type family in the rationale (e.g., "6 bar charts: 5 correctly sorted, 1 unsorted ranking bar") rather than listing all 10+ individually, to keep the rationale readable while still citing every anti-pattern found.

## Primary-Chart-Fails-Purpose Rule (Score Cap)

**Rule.** When the primary (first-seen or largest-by-canvas-area) chart fails at its core encoding purpose AND no caption pairing rescues it AND no immediately-adjacent secondary chart carries the same data more precisely, cap Domain 3 at 4 regardless of the rest of the dashboard's chart choices. Secondary mitigation clauses (e.g., "treemap present as more precise view") reduce but do not eliminate the penalty; the primary chart is what the user sees first and reads first.

**Trigger conditions (all must be true).**

- Primary chart is a word cloud, packed bubble chart, or radar/spider chart used for magnitude comparison, OR any Auto-Block chart (3D, pie 6+, gauge) used as the first-seen chart.
- No caption pairing states the intended read (e.g., no sentence "font size = total points" adjacent to the chart).
- No immediately-adjacent secondary chart carries the same data in a precision-appropriate encoding within the same visual scan zone (top row / above-fold area).

**When secondary mitigation applies (soften cap from 4 to 5).** If a precision-appropriate secondary chart (bar, treemap, sorted table) exists in the same dashboard AND is placed within the same top-to-bottom scan sequence (not tucked below the fold, not on a separate tab), Domain 3 caps at 5 rather than 4. The reader can pivot to the accurate chart with minimal effort.

**When Data Art / Infographic genre exception applies.** Skip this rule entirely. Data Art evaluates on expressive intent per the Genre exception clause above.

**Rationale.** A primary chart that fails its purpose is not a "missed opportunity" — it is a real problem. The reader forms a first impression on the wrong signal and may never scroll to the precision chart. Prior scoring softened this to 5 or 6 via mitigation, which was too generous. Score directly for what the reader sees first.

**Example.** Dashboard leads with a word cloud sized by "Total Points" for artist ranking. No caption. Treemap present in the row below with the same data. Analytical Dashboard genre. Primary-chart-fails-purpose fires; secondary mitigation applies (treemap adjacent below); Domain 3 capped at 5. If the treemap were on a separate tab or below the fold, cap would be 4.

## Handoff Payload for Specific Fixes

If Domain 3 fires Warning-tier or Auto-Block anti-patterns on specific charts, the report handoff payload includes:

- Per-chart routing to `chart-swap-advisor` with the identified anti-pattern IDs.
- User opts in per HC#6.

## Refuse to Fabricate

Cite specific chart references in the rationale. Never invent an anti-pattern to lower the score. Never suppress an Auto-Block to raise the score.
