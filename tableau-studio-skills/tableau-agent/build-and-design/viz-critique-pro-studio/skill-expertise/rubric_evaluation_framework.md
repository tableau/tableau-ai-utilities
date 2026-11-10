# Rubric Evaluation Framework (Locked)

Every VizCritique Pro Desktop run scores against this framework. Derived from the VizCritique Pro v2.1 evaluation-framework rubric, calibrated for Desktop dashboards evaluated from an image with optional XML context.

## 7 Domains and Locked Weights

| # | Domain | Weight | Scoring Range |
|---|---|---|---|
| 1 | Audience Adaptation | 12% | 1-10 |
| 2 | Message Alignment | 12% | 1-10 |
| 3 | Chart Usage | 18% | 1-10 |
| 4 | Layout and Hierarchy | 18% | 1-10 |
| 5 | Color and Typography | 12% | 1-10 |
| 6 | Accessibility | 14% | 1-10 |
| 7 | Interactive-Design Signals | 14% | 1-10 |

**Weights sum to 100%.**

## Overall Score Calculation

```
overall_score = sum over domains of (domain_score × domain_weight × 10)
```

Example: All 7 domains scored 8/10:

```
overall = (8 × 0.12 × 10) + (8 × 0.12 × 10) + (8 × 0.18 × 10) + (8 × 0.18 × 10) + (8 × 0.12 × 10) + (8 × 0.14 × 10) + (8 × 0.14 × 10)
       = 9.6 + 9.6 + 14.4 + 14.4 + 9.6 + 11.2 + 11.2
       = 80.0
```

## Score Tiers (Overall 0-100)

Applied to the overall score after ethics-cap enforcement.

| Range | Tier | Meaning |
|---|---|---|
| 90-100 | Exemplary | Best-in-class execution. Publishable as a template. |
| 80-89 | Strong | Meets professional bar with room for sharpening. |
| 70-79 | Solid | Functional and defensible. Clear gaps but no defects. |
| 60-69 | Developing | Ships with reservations. Multiple gaps to address. |
| 50-59 | Needs work | Not ready for stakeholder review. Fix before ship. |
| 0-49 | Rework | Redesign recommended. Route to viz-planner. |

## Per-Domain Score Anchors

Each domain uses a 1-10 anchored scale. The anchors below apply to every domain; the specific signals vary per domain reference file.

| Score | Anchor |
|---|---|
| 10 | Exceptional. Best-in-class for this domain. Preserve. |
| 8-9 | Strong. Minor sharpening possible. |
| 6-7 | Solid. One or two clear gaps. |
| 4-5 | Developing. Multiple gaps limiting effectiveness. |
| 2-3 | Weak. Fundamental issues; recommend redesign of the domain. |
| 1 | Missing or actively counterproductive. |

**Half-point scores are permitted** (e.g., 7.5) when the evidence sits between two anchors.

## Domain Scoring Discipline

Every domain score cites specific image signals in its rationale. Do not score a domain based on general impression.

- **Signal citations must be visible in the image.** "Legend uses low-contrast gray" is a citation. "The dashboard feels cluttered" is not.
- **Confidence flag on ambiguous signals.** If a specific element is ambiguous in the image, flag confidence in the rationale (e.g., "Font size hard to read at this resolution; scoring 6.5 with medium confidence").
- **XML context sharpens but does not override.** If the workbook is open and XML contradicts the image (e.g., XML shows a bar mark; image looks like a line chart at low resolution), trust the XML for mark-type ground truth and note the resolution issue.

## Domain Reference Files

Every domain has a dedicated reference file with detailed anchors and signals:

- Domains 1 and 2 → `audience_and_context.md`
- Domain 3 → `chart_selection_guide.md`
- Domain 4 → `layout_and_hierarchy.md`
- Domains 5 and 6 → `color_typography_accessibility.md`
- Domain 7 → `interactive_elements.md`

## Ethics Gatekeeper (Runs First)

Before any domain scoring, run the ethics-and-privacy gatekeeper per `ethics_privacy_gatekeeper.md`. If a violation fires, the overall score is capped:

- Critical → 59/100 ceiling.
- Warning → 79/100 ceiling.
- Info → no cap; note in ethics section.

HC#11 non-override applies.

## Bonuses and Penalties (Rare)

The framework permits small bonuses and penalties on the overall score for cross-cutting observations:

- **+2 bonus** for a dashboard that solves an ambiguous audience or unclear message via elegant design (rare; usually reserved for scores already in Strong or Exemplary tiers).
- **-3 penalty** for internal-detail leakage to the end user (surfacing raw calc names, tool template IDs, or debug output on the rendered dashboard).
- **-5 penalty** for a dashboard that is technically clean but fundamentally misleading in a way the ethics gatekeeper did not flag (rare; usually a domain issue in Chart Usage or Layout).

Bonuses and penalties are recorded in the ethics section of the report and reflected in the final overall score. Apply after ethics cap; the cap is the ceiling regardless.

## Refuse to Fabricate

Every domain score cites image evidence. Ethics cap applies without override. Weights and anchors are locked. If a domain cannot be scored (long-form partial image per HC#12), record UNSCANNED with rationale rather than fabricating.
