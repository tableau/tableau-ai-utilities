# Domain 7: Interactive-Design Signals (Locked)

Evaluates the design signals for interactivity visible in the image (filter controls, tabs, drill affordances, parameter controls, tooltip presence). Does not evaluate runtime behavior; that routes to `interaction-validator`.

## Score Anchors

| Score | Description |
|---|---|
| 10 | Interaction affordances are visible, well-labeled, and match the audience's interaction budget. Filter placement supports the scan path. |
| 8-9 | Strong signals with 1-2 minor gaps (one unlabeled filter, one drill affordance ambiguous). |
| 6-7 | Solid with 3-4 interaction-design gaps or one significant miss. |
| 4-5 | Developing; interaction affordances present but poorly placed or unlabeled. |
| 2-3 | Weak; interaction hidden or missing where the audience needs it. |
| 1 | No interaction signals visible; static dashboard passed off as interactive. |

## Signals Evaluated

**Filter design.**

- Are filter controls visible and labeled?
- Do filter placements support the scan path (top strip, left rail) or fight it (scattered)?
- Do filter types match cardinality (dropdown for many values, checkbox for few, slider for continuous)?
- Are Apply / Reset controls visible when the filter set is complex?

**Tab and page navigation.**

- Are tabs labeled with the destination content (not "Sheet 1", "Sheet 2")?
- Is the current tab visually distinct from inactive tabs?
- Is tab order intentional (natural reading order or workflow order)?

**Drill affordances.**

- Are drill-in cues visible (chevrons, "+" icons, underlined labels)?
- Do interactive elements have hover states or visual affordances signaling clickability?

**Parameter controls.**

- Are parameters visible in a parameter zone or grouped with related filters?
- Do parameters have clear labels indicating what they control?

**Tooltip design signals.**

- Do charts show evidence of custom tooltips (visible in the image if hovered during screenshot capture)?
- Are tooltip labels descriptive rather than field names?

**Audience-interaction budget alignment.**

- Executive: 0-2 filters, hover tooltips only.
- Manager: 2-4 filters, filter actions.
- Analyst: 4-8 filters, parameter actions, set actions.
- Operations: 1-2 filters, alert-driven interaction only.
- External / Public: 0-1 filters, minimal interaction.

If the interaction budget on the dashboard exceeds the audience budget, the score drops.

## Common Downgrades

- Filter controls scattered across the canvas rather than clustered.
- Tab labels are field names or default sheet names ("Sheet 1").
- Missing filter labels or filter zone header.
- Interaction affordances present but not visually distinguishable from non-interactive elements.
- Interaction budget significantly exceeds audience budget (Executive dashboard with 8 filters).
- Missing Apply / Reset on a complex filter set.
- Drill affordances present without clear cues (readers do not know what is clickable).

## Calibration Examples

**Example 7.1 → Score 9.** Manager dashboard with 3 filter controls (period, region, category) clustered in a top strip with clear labels. Two tabs labeled "Overview" and "Detail" with the active tab visually distinct. Drill-in chevrons visible on the Regional breakdown chart. Filter budget matches Manager audience (2-4 filters). Strong signals.

**Example 7.2 → Score 6.** Executive dashboard with 6 filter controls (exceeds Executive 0-2 budget). Filters labeled but scattered: two on top strip, three on right rail, one at the bottom. Tabs labeled "Sheet 1" and "Sheet 2" (defaults, not descriptive). Signal: filter budget mismatch, filter placement fights scan path, tab labels are defaults. Solid but three interaction-design gaps.

**Example 7.3 → Score 3.** No filter controls visible on a stated-Analyst dashboard (should have 4-8). No drill affordances signaled. Static-looking table for a dashboard that user says supports parameter-driven navigation. Signal: interaction hidden or missing where the audience needs it.

## Data Art / Infographic Anchors (Genre Override)

When Genre Detection (see `SKILL.md`) classifies the piece as Data Art / Infographic, replace the Score Anchors table above with this one. A fixed narrative piece with zero interaction is not a lesser dashboard — it's a different genre with a different full-score condition.

| Score | Description |
|---|---|
| 10 | No interaction present, and none is needed — the piece is a complete, self-contained narrative. Any controls present (e.g., a source-toggle) are clearly labeled and unobtrusive. |
| 8-9 | No interaction, narrative reads cleanly standalone; one very minor affordance (e.g., an unlabeled hyperlink) is slightly ambiguous. |
| 6-7 | A control is present but adds friction without adding narrative value (e.g., a filter that doesn't change the story being told), or a control is unlabeled. |
| 4-5 | Interaction is bolted on in a way that fights the narrative flow (e.g., a filter mid-story that resets scroll position or breaks the reading order). |
| 2-3 | Interactive controls are present and clearly necessary for the reader to get the intended information, but are broken, hidden, or mislabeled. |
| 1 | The piece claims to be interactive/exploratory but shows no usable affordances at all. |

Do not penalize the absence of filters, tabs, or drill affordances under this anchor table — that absence is the expected condition for this genre. Only score down for interaction that is present-but-flawed, or for an interaction claim (stated by the user or implied by the piece) that isn't backed up visually.

## Long-Form Dashboards (HC#12)

If image aspect ratio is taller than 2:1, Domain 7 scoring depends on seeing the full canvas. Do not score Domain 7 on a partial image; flag UNSCANNED with `reason: interaction_affordances_require_full_canvas`. Offer per-section re-runs.

## XML Context Sharpening

When workbook is open and `get-dashboard-xml` / `get-worksheet-xml` are available:

- Cross-reference visible filter controls against declared filter actions.
- Detect parameter references in calc formulas (via `list-available-fields`).
- Detect dynamic-zone-visibility bindings.

Note that action-configuration XML is partially unreliable (`get-dashboard-xml` action-block gap). If action-config is unavailable, score from image signals only and note the limitation in the rationale.

`get-worksheet-xml` has also been observed failing with a 500 error on worksheets already placed on a dashboard. If it fails, fall back to image-only signals for that worksheet and note the limitation in the rationale rather than retrying indefinitely.

## Handoff Payload for Fixes

If Domain 7 scores below 7, the report handoff payload includes:

- Routing to `interaction-validator` for runtime behavior verification.
- Routing to `viz-planner` for interaction-design redesign at Rework-tier scores.
- User opts in per HC#6.

## Refuse to Fabricate

Cite specific interaction-affordance references in the rationale. Never invent an interaction gap. Do not score runtime behavior from the image; runtime routes to `interaction-validator`.
