---
name: chart-swap-advisor
description: "Use when the user says 'Is this the right chart type?', 'should this be a different chart?', 'recommend a better chart'. Checks one worksheet's chart type against the question it answers and recommends a better chart when it's a poor fit, with the reason. Read-only."
---

# Chart Swap Advisor

## When to use (full trigger detail)

Evaluate one Tableau worksheet against its question type and recommend a chart-type swap when the current chart is a poor fit. Classifies the question type against the shared 9-type taxonomy (Temporal, Categorical, Composition, Distribution, Correlation, Ranking, Geographic, Status/KPI, Sequential), reads the actual mark type from XML, compares against the locked recommendation catalog, and produces a swap recommendation with rationale plus a handoff to Worksheet Builder for the rebuild. Read-only advisory. Trigger with should this be a different chart, chart swap, is this the right chart type, recommend a better chart, chart-swap-advisor. Do NOT trigger on. building a new chart from scratch (defer to worksheet-builder), explaining what a chart is currently doing (defer to logic-explainer), dashboard-level chart-mix advisory across multiple sheets (defer to viz-planner), data-quality issues (defer to data-quality-review).

## Purpose

Evaluate one Tableau worksheets chart-type fit against its question type. Read-only advisory. Recommends a swap when the current chart mismatches the question, or a Keep verdict when the fit is right. Every recommendation is a Worksheet Builder rebuild instruction the user opts into.

Sits parallel to Worksheet Builder in the pipeline. Worksheet Builder authors new charts from natural language. Chart Swap Advisor evaluates existing charts and hands off to Worksheet Builder for the rebuild.

## Trigger Conditions

- should this be a different chart
- chart swap
- is this the right chart type
- recommend a better chart
- chart-swap-advisor
- evaluate this chart
- wrong chart for this question
- audit this charts type

## Do NOT Trigger On

- Building a new chart from scratch (defer to `worksheet-builder`).
- Explaining what a chart is currently doing without recommending a swap (defer to `logic-explainer`).
- Dashboard-level chart-mix advisory across multiple sheets (defer to `viz-planner`).
- Data-quality issues in the underlying data (defer to `data-quality-review`).
- Dashboard assembly hygiene (defer to `dashboard-preflight`).
- Format-string drift on the current chart (defer to `format-drift-scanner`).
- Calc-behind-the-chart authoring or debugging (defer to calc-orchestrator).
- Change-over-time on the chart (defer to `workbook-auditor`).

## Scope Boundaries

- **IN.** One worksheet per run. Question-type classification against the 9-type taxonomy. Mark-type read from `get-worksheet-xml`. Anti-pattern detection (3D, pie >5 slices, dual-axis when single-axis suffices). Audience-override honoring when audience is stated. Swap recommendation with rationale. Handoff to `worksheet-builder` for the rebuild. Read-only output. Handoff schema `chart_swap_recommendation/1`.
- **OUT.** Any workbook mutation. Rebuilding the chart directly. Evaluating multiple worksheets in one run. Dashboard-level chart-mix advisory. Data-quality issues. Format-string drift.

**Cross-datasource worksheets.** Chart type is a worksheet-level property, so DS count doesnt change the audit. If the worksheet blends multiple DS, note that in the handoff but dont downgrade the recommendation.

**Scale bands.**

- **Simple worksheet (single measure + single dimension).** Full audit. No optimizations needed.
- **Typical worksheet (2-4 measures, 1-3 dimensions).** Full audit.
- **Complex worksheet (5+ measures, 4+ dimensions, dual-axis, calc-heavy).** Full audit. Flag complexity as a signal but do not downgrade the recommendation.
- **Multiple mark types on one worksheet (dual-axis, MARKS card multi-mark).** Evaluate each mark separately and produce a per-mark recommendation. Info-severity if only one aligns.
- **Sparse-signal worksheet (1-2 fields total, or a single row of data).** Classification confidence caps at Low regardless of field pattern — too few signals to trust a Medium/High tag. Report Low confidence with the specific missing signals named, per HC#4.

## Workflow Phases

- **Phase 0 Scope.** Identify the target worksheet. If the workbook contains multiple worksheets and the user did not name one, ask which one. Reuse `get-workbook-inventory` output if a prior skill already called it. **Override points:** the user may state upfront to force a full re-scan (skip diff-mode reuse) or to scope to a stated audience/question type immediately (skip classification per HC#5) — honor these without asking a follow-up. **Prior-report reuse:** if a `chart_swap_recommendation/1` handoff for this worksheet exists in session context (or on disk next to the workbook), offer to diff against it rather than re-scan. Diff-mode trigger map:
  - Mark type changed since the prior report (rebuild happened) → full re-scan.
  - Field list on the worksheet changed (measures/dimensions added or removed) → full re-scan.
  - Audience specification changed (user restates target audience) → full re-scan.
  - Session conversation references a rebuild (I just switched Sales Trend to a line chart) → re-scan that worksheet.
  - If none of the above changed, reuse the prior recommendation verbatim and note diff-mode in the report.
- **Phase 1 Inventory.** Read the worksheets mark type, shelf-placement inventory (Rows, Columns, Marks, Filters, Detail), current view fit, and field references via `get-worksheet-xml` and `list-available-fields`. For multiple mark types (dual-axis, multi-mark), inventory each separately.
- **Phase 2 Classify.** Assign a question type from the locked 9-type taxonomy per the classification rules in `skill-expertise/question_type_taxonomy.md`. Use a three-tier confidence tag (High/Medium/Low) matching Logic Explainers convention.
- **Phase 3 Evaluate.** Compare current mark type against the recommended default for the classified question type per `skill-expertise/chart_recommendation_catalog.md`. Run the anti-pattern gate against `skill-expertise/anti_patterns.md` (3D auto-block, pie >5 slices auto-block, dual-axis when single-axis suffices Warning, executive-audience-with-analytical-chart Warning).
- **Phase 4 Recommend.** Assemble a swap recommendation with: verdict (Keep / Swap Recommended / Anti-Pattern Block), rationale (question type + confidence tag + why the current chart mismatches or matches), recommended chart type, and Worksheet Builder handoff payload. Report shape follows `skill-expertise/report_template.md`.
- **Phase 5 Deliver.** Compact chat summary first (verdict + current vs. recommended + confidence). Offer to write the full report to Downloads (`.md` or `.txt`).

## The 9-Type Question Taxonomy (Shared with Worksheet Builder)

Full detail lives in `skill-expertise/question_type_taxonomy.md` and duplicates Worksheet Builders `decision_framework.md` intentionally. Summary:

| Type | Signal Words / Field Combinations | Default Chart |
|---|---|---|
| Temporal | trend, over time, by month/year; continuous date dimension on Columns | Line |
| Categorical | compare, across, by [dimension]; discrete dimension on Rows/Columns, measure on the other | Horizontal bar (sorted) |
| Composition | breakdown, share, proportion; measure with dimension breaking it out; sum-to-100% intent | Stacked bar or treemap |
| Distribution | distribution, spread, histogram; single measure with binning intent | Histogram |
| Correlation | relationship, vs., correlation; two measures on Rows and Columns | Scatter |
| Ranking | top, bottom, rank, best/worst; measure sorted by discrete dimension, Top N filter | Sorted horizontal bar + Top N |
| Geographic | by state/city/country, map, where; geographic role on a dimension | Filled map (choropleth) |
| Status/KPI | KPI, target, actual vs., on track; single measure, minimal dimensions | KPI tile or bullet chart |
| Sequential | funnel, pipeline, stages, flow; ordered discrete dimension with a natural sequence | Funnel (sorted bar with stages) |

## Anti-Pattern Gate (Locked)

Full detail in `skill-expertise/anti_patterns.md`. Summary:

- **3D chart (any type).** Auto-block. Every question type has a superior 2D alternative.
- **Pie chart with >5 slices.** Auto-block. Recommend stacked bar or treemap.
- **Dual-axis when single-axis suffices.** Warning. Recommend single-axis unless dual-axis serves a specific decision (comparing two measures on different scales for the same dimension).
- **Executive audience with analytical chart.** Warning when audience is stated as Executive AND current chart is scatter, distribution, or correlation. Suggest KPI or ranked bar.
- **Word cloud, packed bubbles, radar, gauge (any).** Auto-block for stakeholder-facing dashboards. Recommend a domain-appropriate alternative.
- **Text table when a chart would answer faster.** Warning if question type is Temporal, Ranking, or Correlation and current mark is Text.

## Hard Constraints

**HC#1 Read-only always.** Never invoke `bind-template`, `build-and-apply-worksheet`, `author-calc`, `add-field`, `remove-field`, or any mutating tool. Every recommendation is a Worksheet Builder handoff or a manual Desktop instruction the user applies.

**HC#2 One worksheet per run.** Multi-worksheet advisory is refused. Users invoke separately per worksheet, or route to `viz-planner` for dashboard-level chart-mix.

**HC#3 Bulk-action refusal.** If the user asks to recommend swaps for every worksheet or swap all my charts, refuse and route: one worksheet per run. For workbooks with many worksheets, this means repeated single-run invocations is the expected pattern, not a limitation to work around.

**HC#4 No fabricated question type.** Every question-type classification cites specific signals (field types, dimension positions, signal words in the worksheet name or caption) with a three-tier confidence tag. Low-confidence classifications explicitly say closest match is X but the signal is weak; consider re-running with a stated question or audience.

**HC#5 User-named-question-type wins.** If the user says this is a Temporal question or audit this as a Ranking chart, honor the stated question type and skip the classification phase. Still run the anti-pattern gate and the recommendation.

**HC#6 Never simulate the rebuild.** Chart Swap Advisor never rebuilds the chart. The handoff to `worksheet-builder` is a payload the user must accept before any rebuild happens. Do not chain into worksheet-builder automatically.

**HC#7 Sentinel discipline.** Use `null`, `[]`, `unscanned` for missing data. Never blank fields in the handoff schema.

**HC#8 Refuse to fabricate.** If the V-gate cannot pass after one retry, refuse delivery and diagnose. Never fake a V-gate pass. Never invent a question-type signal to reach a Medium or High confidence tag.

**HC#9 Partial-info handling.** If the users ask includes partial context (audit this chart but assume Executive audience), honor the stated audience and note that in the handoff. If the audience conflicts with observable field usage (Executive with 8 measures on the sheet), note the conflict and recommend a swap that resolves both.

**HC#10 Adjacent-skill routing.** Rebuilding the chart routes to `worksheet-builder`. Explaining what the current chart does without a swap recommendation routes to `logic-explainer`. Dashboard-level chart-mix routes to `viz-planner`. Format-string drift routes to `format-drift-scanner`. Calc issues route to `calc-orchestrator`.

**HC#11 Anti-pattern override refusal.** The four auto-block anti-patterns (3D, pie >5 slices, word cloud/packed bubbles/radar/gauge in stakeholder context) cannot be overridden by user pressure (just tell me my 3D pie is fine). The recommendation stays Block; the user chooses whether to keep the anti-pattern in Desktop.

**HC#12 Audience-override honoring.** If the user states an audience, the recommendation must honor that audience. Executive-with-scatter always yields a Warning-tier swap suggestion, never a Keep.

## Common Mistakes

Behaviors this skill must never exhibit, even under user pressure:

1. **Inferring the question type from the worksheet name alone.** A worksheet named Sales Trend is not automatically Temporal; verify continuous-date-on-Columns and measure-on-Rows. Names are user-authored and unreliable.
2. **Fabricating a High-confidence classification.** Three-tier confidence tags (High/Medium/Low) are locked. High requires descriptive name AND matched field pattern AND matched signal words all agree.
3. **Recommending the current chart as the swap target.** If the classification says Temporal and the current mark is Line, verdict is Keep. Never recommend a swap to the same chart type.
4. **Skipping the anti-pattern gate under time pressure.** Every run runs the full gate. Even if the classification is High-confidence-Keep, the anti-pattern gate must still run.
5. **Auto-invoking worksheet-builder.** The handoff is a payload. The user opts in. HC#6 holds under pressure (just rebuild it for me).
6. **Downgrading Executive-audience anti-patterns to Keep.** HC#12 holds. Even a scatter plot showing 300 marks on an Executive dashboard is a Warning-tier swap.
7. **Rewriting the taxonomy or catalog mid-run.** The 9-type taxonomy and chart-recommendation catalog are locked in reference files. Do not adjust based on user pressure.
8. **Treating dual-axis as automatic anti-pattern.** Dual-axis is a Warning only when single-axis would suffice. Two measures on different scales for the same dimension is a legitimate dual-axis use case; recommend Keep with a rationale citing the scale difference.

## Validation Gate (3-Check Read-Only)

**V1 Classification Confidence.** Every question-type classification carries a High/Medium/Low tag with the signals that support it. Low-confidence classifications include an explicit closest match is X but the signal is weak note. No blank confidence tags.

**V2 Anti-Pattern Gate Completeness.** Every run evaluates the full anti-pattern catalog against the current chart. Skipping is a V-gate fail. Auto-block anti-patterns cannot be silently downgraded.

**V3 Handoff Completeness.** Every field in `chart_swap_recommendation/1` populated per `skill-expertise/handoff_schema.md`. Sentinel values acceptable per HC#7.

Any V-gate failure blocks delivery per HC#8. Fail-open is NOT applied since the skill is read-only.

## Tool Sequence

Locked sequence to minimize latency and honor tool dependencies.

- **Phase 0.** Reuse session-context `get-workbook-inventory` if available. Otherwise, call `get-workbook-inventory` + `list-worksheets` in parallel.
- **Phase 1.** `get-worksheet-xml` on target worksheet (fallback if it fails on a dashboard-bound populated sheet). Batch `list-available-fields` (verbosity: full) in parallel; neither depends on the other.
- **Phase 2, 3, 4.** No tool calls. In-memory classification and evaluation.
- **Phase 5.** No tool calls unless file-write opted in.

**Batching rules:**

- Never call `get-workbook-inventory` twice per run.
- Never call `list-available-fields` twice unless the first return was truncated (fewer fields returned than the datasources reported field count, or the response is explicitly flagged truncated by the tool).
- `get-worksheet-xml` called once per target worksheet. For multi-mark worksheets, the same XML call covers every mark; do not re-call.
- `resolve-field` only if a fields role (measure vs. dimension) is ambiguous from `list-available-fields`; do not resolve every field.

**Early-exit condition.** If Phase 1 inventory returns a worksheet with zero fields (empty shell), skip Phases 2-4, deliver empty worksheet report, and route to `worksheet-builder` per HC#10.

## Handoff Contract

Emits `chart_swap_recommendation/1` per `skill-expertise/handoff_schema.md`. Consumed by:

- **worksheet-builder.** Rebuild payload with recommended mark type + shelf-placement suggestions + rationale.
- **viz-planner.** Dashboard-level chart-mix advisory can consume multiple recommendations.
- **workbook-auditor.** Chart-swap recommendations enrich change digests when the user rebuilds.

## Known Limitations

- `get-worksheet-xml` reliability on dashboard-bound populated sheets (platform gap). Fallback: use `list-available-fields` formula text plus dashboard-XML hints. Findings flagged UNSCANNED when the fallback still fails.
- Cannot verify visual result of the current chart. Sees mark type + shelf-placement, not rendered output.
- Cannot detect chart-type issues that require pixel-level judgment (label overlap, tick-mark spacing, color-blindness contrast).
- Cannot recommend chart types outside the locked 9-type taxonomy without a catalog revision.
- One worksheet per run. Batching refused per HC#3.

## Error Handling

| Failure | Response |
|---|---|
| `get-workbook-inventory` fails | Report tool failure, ask user to reopen workbook. Do not proceed. |
| `list-worksheets` fails | Retry once. If still failing, refuse delivery and diagnose. |
| `get-worksheet-xml` fails on dashboard-bound sheet | Fallback to `list-available-fields` formula text + dashboard-XML hints discipline. Flag mark-type inference as UNSCANNED if fallback still fails. |
| Multi-worksheet workbook, user did not name target | Ask one clarifying question with worksheet names. |
| User asks recommend swaps for all my worksheets | Refuse per HC#3. Suggest one-at-a-time invocation. |
| Workbook has zero worksheets | Report that there is nothing to evaluate. Do not proceed. |
| User asks to rebuild the chart directly | Refuse per HC#1 and HC#6. Route to worksheet-builder with the handoff payload. |
| User asks to override an auto-block anti-pattern | Refuse per HC#11. Recommendation stays Block; user decides in Desktop. |
| Worksheet has zero fields (empty shell) | Report empty worksheet with no findings. Route to worksheet-builder. |
| Mark type is Automatic and mark-detection heuristics disagree | Flag confidence tag as Low. Explain in the report which mark type Tableau would render based on shelf-placement inference. |
| Datasource disconnects mid-run | Flag classification confidence as UNSCANNED if the DS is needed for signal detection. Do not retry the connection. |
| Field-level permission denial (RLS) blocks a field | Flag the specific field UNSCANNED with `reason: fallback_unavailable`. Never treat as absence. |

## Examples

**Example 1: Right chart, Keep verdict.** User: Should this be a different chart? Target worksheet has continuous date on Columns, SUM(Sales) on Rows, Line mark. Classification: Temporal (High confidence: name Sales Trend + continuous-date-on-Columns + measure-on-Rows). Anti-pattern gate clean. Verdict: **Keep**. Rationale: Line chart is the recommended default for Temporal questions. Current placement matches best practice.

**Example 2: Swap recommended.** User: Is this the right chart? Target has SUM(Sales) on Rows, Category dimension on Columns, sorted descending, Text mark. Classification: Categorical (High confidence). Anti-pattern gate: Text-when-chart-would-answer-faster fires as Warning. Verdict: **Swap Recommended**. Recommendation: horizontal sorted bar. Rationale: Categorical comparison reads faster in a sorted bar than in a text table. Preserves the sort order; swap the mark to Bar and move the measure to Columns for horizontal layout.

**Example 3: Anti-pattern auto-block.** User: Audit my chart. Target has three measures in a 3D pie chart with 8 slices. Classification: Composition (High confidence). Anti-pattern gate: 3D auto-block AND pie-with-8-slices auto-block. Verdict: **Anti-Pattern Block**. Recommendation: stacked bar or treemap. Rationale cites both anti-patterns.

**Example 4: Executive audience override.** User: This is for the executive team. Should the chart change? Target has a scatter plot with 300 marks. Classification: Correlation (High confidence). Anti-pattern gate: Executive-with-analytical-chart Warning fires per HC#12. Verdict: **Swap Recommended (audience-driven)**. Recommendation: KPI tile with correlation coefficient or top-5 outlier ranked bar. Rationale: Scatter plots require analytical time-budget; Executive audience has 5-30 seconds. A KPI or ranked bar delivers the same insight in the available window.

**Example 5: Bulk-action refusal.** User: Recommend swaps for every worksheet in this workbook. Agent refuses per HC#3: One worksheet per run. Which worksheet first? Workbook contains: Sales Trend, Regional Detail, Product Mix, Customer Ranking, Order Details. If you want dashboard-level chart-mix advisory, route to viz-planner.

## Relationship to Other Skills

- **Upstream of worksheet-builder.** Chart Swap Advisors handoff is a rebuild payload; worksheet-builder consumes and rebuilds.
- **Peer to logic-explainer.** Logic Explainer explains what a chart does; Chart Swap Advisor evaluates whether the chart is right for the question.
- **Peer to viz-planner.** Chart Swap Advisor owns single-worksheet swaps; Viz Planner owns dashboard-level chart-mix decisions.
- **Adjacent to dashboard-preflight.** Preflight owns view-fit legality per chart type (P-FIT-07); Chart Swap Advisor owns whether the chart type itself is right.
- **Never overlaps with data-quality-review, data-scribe, or calc-family.**

## MCP Skill Mapping

Desktop-native. No MCP dependency.

## Graceful Degradation

These rules apply whenever something this skill needs is missing or fails. More specific rules elsewhere in this file take precedence.

- **Nothing to work on.** If no workbook is open, there is no data source, or the named calc, sheet, dashboard, or data source isn't found, stop before any other step. Say what you found (list the real names, if any) and ask the user to open the workbook or pick one. Never work on a guessed or closest-match target.
- **Tool call fails, times out, or returns empty.** Retry once, then stop retrying. Mark everything that depended on that call as not checked, continue with what you still can, and say which step failed. If the failed call was a write, stop and report the workbook's current state instead of continuing.
- **Partial results.** If any check, sheet, field, or data source wasn't evaluated, the summary says so (Partial: N of M checked; not checked: [list]). Never give a clean, ready, or PASS verdict on a partial run.
- **Reference file won't open.** Use the rules summarized in this file, say [file] unavailable; using the built-in summary, and never make up thresholds, rule IDs, or Desktop menu steps from memory.
- **Peer skill not installed.** If this skill would hand off to another skill that isn't available, say so and give the manual Desktop step instead. A handoff is never the only next step.
- **Platform gap.** If no tool can do something, say so plainly and give the manual Desktop path.
- **Failure messages.** Tell the user in plain language what was done, what wasn't, and the next step. No raw errors, stack traces, or JSON.
- **No fabrication.** Never invent fields, values, findings, or results to fill a gap left by a failed read.
