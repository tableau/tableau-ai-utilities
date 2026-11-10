# Domains 1 and 2: Audience and Context Assessment (Locked)

Covers Domain 1 (Audience Adaptation) and Domain 2 (Message Alignment). Both use the shared audience taxonomy and message-clarity anchors below.

## Audience Taxonomy (Shared with Viz Planner)

| Audience | Time Budget | Filters | Charts | Interaction Style |
|---|---|---|---|---|
| Executive | 5-30 seconds | 0-2 | 4-6 | Minimal, hover tooltips only |
| Manager | 1-3 minutes | 2-4 | 5-8 | Moderate; filter actions, drill |
| Analyst | 3-15 minutes | 4-8 | 6-12 | Heavy; parameter actions, set actions, search |
| Operations | 5-30 seconds | 1-2 | 3-5 | Alert-driven; status color + threshold only |
| External / Public | 30-90 seconds | 0-1 | 3-5 | Minimal, pre-scoped, storytelling |

Audience is either stated by the user or inferred from dashboard signals (title language, chart count, filter count, complexity).

## Domain 1: Audience Adaptation

**What it measures.** How well the dashboard fits its stated or inferred audience per the taxonomy above.

**Signals evaluated (image + optional XML):**

- Chart count vs. audience chart budget.
- Filter count vs. audience filter budget.
- Complexity level (calc-heavy, dual-axis, small-multiples) vs. audience skill level.
- Reading-time estimate vs. audience time budget.
- Layout scan path (visual hierarchy) vs. audience decision-making style.

**Score anchors:**

| Score | Description |
|---|---|
| 10 | Dashboard fits the audience precisely. Chart count, filter count, and complexity all inside the audience's window. |
| 8-9 | Strong fit with one minor mismatch (e.g., one extra filter for Executive; one complex calc for Manager). |
| 6-7 | Solid fit; one clear mismatch that increases reading time by ~30%. |
| 4-5 | Developing; multiple mismatches. Audience will need effort the design does not support. |
| 2-3 | Weak; audience mismatch limits usability significantly. |
| 1 | Fundamental audience miss (e.g., Analyst-tier scatter plot on an Executive dashboard). |

**Common downgrades:**

- Executive dashboard with 8+ charts or a scatter/histogram/correlation view.
- Analyst dashboard with only KPI tiles and no drill capability.
- Operations dashboard without a clear status-color + threshold pattern.
- Multi-page navigation on an Executive dashboard.

**HC#9 partial-info handling.** If audience is stated, honor it. If stated audience contradicts observable design (Executive with 20 charts), flag the conflict in the Domain 1 rationale rather than lowering the score silently.

## Domain 2: Message Alignment

**What it measures.** How clearly the dashboard communicates its core message or decision-support intent.

**Signals evaluated:**

- Title clarity. Does the title name a decision, question, or metric?
- Subtitle or caption. Does it disclose the audience, time window, or filter context?
- Primary-metric hierarchy. Is the most important number the largest, first, or most-emphasized element?
- Supporting-chart alignment. Do secondary charts elaborate on the primary metric, or do they compete for attention?
- Empty-canvas discipline. Are unused zones minimized? Are decorative elements minimized?

**Score anchors:**

| Score | Description |
|---|---|
| 10 | Message reads in under 5 seconds; every element supports the primary decision or question. |
| 8-9 | Message reads in under 10 seconds; one or two elements are decorative or off-message. |
| 6-7 | Message reads with modest effort; 3-4 elements are off-message or ambiguous. |
| 4-5 | Message unclear on first pass; requires scanning to identify the primary metric. |
| 2-3 | Message competes with too many elements or is buried. |
| 1 | No discernible message; dashboard reads as a data dump. |

**Common downgrades:**

- Title is a field name ("Sales Dashboard") rather than a decision or question.
- 4+ competing primary metrics at similar visual weight.
- Decorative elements (logos, banners) larger than the primary KPI.
- Missing subtitle when audience or time-window matters.
- Empty zones with placeholder text or unused white space that suggests the dashboard is incomplete.

## Audience Inference Signals (When Not Stated)

If the user did not state the audience, infer from these signals in the image, in order of weight:

1. **Chart count.** 4-6 → Executive or External. 5-8 → Manager. 6-12 → Analyst. 3-5 → Operations or External.
2. **Filter count.** 0-1 → Executive or External. 2-4 → Manager. 4-8 → Analyst.
3. **Title language.** "Overview" or "Summary" → Executive. "Detail" or "Deep Dive" → Analyst. "Status" or "Monitor" → Operations.
4. **Interaction affordances visible.** Multiple filter controls + parameter dropdowns → Analyst. Minimal or none → Executive.
5. **Color palette.** Alert-heavy (orange, magenta) with shape encoding → Operations.

Confidence flag when inference is Low (contradicting signals). Ask the user for audience if truly ambiguous per HC#9.

## Calibration Examples

Real-world signal-to-score mappings for both domains. Use as anchors when the current image matches or approximates one of these shapes.

### Domain 1 Calibration

**Example 1.1 → Score 9.** Executive dashboard, image shows 4 KPI tiles on the top row, 2 supporting trend charts below, one filter for time period, no additional filters visible. Signal: chart count 6, filter count 1, complexity minimal. All three inside Executive time budget. Strong fit.

**Example 1.2 → Score 6.** Manager dashboard stated by user, image shows 9 charts including one scatter plot and one dense heatmap. Signal: chart count exceeds Manager budget by 1, and analytical-tier chart types dilute the 1-3 minute time window. One clear mismatch.

**Example 1.3 → Score 3.** Executive dashboard stated by user, image shows 14 charts including three scatter plots and a 30-row detail table. Signal: chart count 2.5x Executive budget, three analytical-tier charts require Analyst time budget, detail table is a Manager or Analyst artifact. Fundamental audience miss.

### Domain 2 Calibration

**Example 2.1 → Score 9.** Title reads "Q4 Revenue Growth: On Track for 8% YoY." Primary KPI (Revenue) is the largest element, centered top-left. Three supporting charts elaborate (regional breakdown, product-category breakdown, month-over-month trend). No decorative elements larger than a chart title. Signal: title names the decision, primary KPI anchors hierarchy, secondary charts elaborate. Message reads in under 5 seconds.

**Example 2.2 → Score 6.** Title reads "Sales Dashboard." Two primary KPIs (Sales and Profit) at similar visual weight. Company logo is 2x the size of the primary KPIs. Signal: title is a field name, two competing primary metrics, decorative element dominates. Message unclear on first pass.

**Example 2.3 → Score 2.** Title is "Overview." Four primary metrics tied at the same size. No subtitle. Empty zones scattered across the layout with placeholder text ("chart here"). Signal: no discernible primary metric; layout reads as incomplete dashboard.

## Ask-For-Audience Cadence

Skill asks for audience only when inference confidence is Low AND the domain-1 or domain-2 score would materially change based on audience. Example ask:

> "Who's the primary audience for this dashboard: Executive, Manager, Analyst, Operations, or External? I can score without it, but audience-fit accuracy improves with the answer."

Do not ask for audience on runs where confidence is High or Medium; the inference is good enough.

## Refuse to Fabricate

Never score Domain 1 or 2 on general impression. Cite specific image signals. Flag confidence when inference is Low. Do not invent an audience-mismatch to justify a lower score, and do not paper over a genuine mismatch to soften the critique.
