# Chart Swap Advisor

**Evaluate one Tableau worksheet's chart type against the question it answers.** Read-only. Every recommendation is a Worksheet Builder rebuild payload the user opts into.

## When to Use

- You built a chart and want to know if it's the right chart type for the question.
- You inherited a workbook and want a sanity check on the visualization choices.
- You're prepping for a stakeholder review and want to catch anti-patterns before someone else does.

## When Not to Use

- **Building a new chart from scratch.** Use `worksheet-builder`.
- **Explaining what a chart currently does** without a swap recommendation. Use `logic-explainer`.
- **Dashboard-level chart-mix advisory across multiple sheets.** Use `viz-planner`.
- **Data-quality issues.** Use `data-quality-review`.
- **Format-string drift on the current chart.** Use `format-drift-scanner`.
- **Calc issues.** Use `calc-orchestrator`.

## The 9-Type Question Taxonomy

Every classification maps to one of these types, backed by locked recommendation defaults:

| Type | Default Chart | Signal Words |
|---|---|---|
| Temporal | Line | trend, over time, by month/year |
| Categorical | Sorted horizontal bar | compare, across, by [dimension] |
| Composition | Stacked bar or treemap | breakdown, share, proportion |
| Distribution | Histogram | distribution, spread, histogram |
| Correlation | Scatter | relationship, vs., correlation |
| Ranking | Sorted horizontal bar + Top N | top, bottom, rank, best/worst |
| Geographic | Filled map | by state/city/country, map, where |
| Status/KPI | KPI tile or bullet chart | KPI, target, actual vs., on track |
| Sequential | Funnel | funnel, pipeline, stages, flow |

## The Anti-Pattern Gate

Every run evaluates the current chart against a locked anti-pattern catalog. Auto-blocks cannot be overridden:

- **3D chart (any type).** Auto-block.
- **Pie chart with >5 slices.** Auto-block.
- **Word cloud, packed bubbles, radar, gauge (in stakeholder-facing dashboards).** Auto-block.
- **Dual-axis when single-axis suffices.** Warning.
- **Executive audience with analytical chart.** Warning.
- **Text table when a chart would answer faster.** Warning.

## What You Get

A compact chat summary with the verdict (Keep / Swap Recommended / Anti-Pattern Block), the question type and confidence, and the recommendation with rationale. Optional full report file to Downloads. Handoff to `worksheet-builder` for the rebuild.

## Example Trigger Phrases

- "Should this be a different chart?"
- "Is this the right chart type?"
- "Recommend a better chart."
- "Chart swap."
- "Evaluate this chart."

## Output Handoff

Emits `chart_swap_recommendation/1` per the locked schema. Consumed by `worksheet-builder` (rebuild payload), `viz-planner` (dashboard-level chart-mix), and `workbook-auditor` (change enrichment).

## Known Limitations

- One worksheet per run. Batching is refused.
- Cannot verify visual result. Sees mark type and shelf placement, not rendered output.
- Cannot detect chart-type issues that require pixel-level judgment (label overlap, contrast, spacing).
- `get-worksheet-xml` reliability on dashboard-bound populated sheets. Fallback to `list-available-fields` + dashboard-XML hints.

## Distribution

Ships with Tableau Studio. Also available on Skills Exchange for latest-version pulls between Studio releases.
