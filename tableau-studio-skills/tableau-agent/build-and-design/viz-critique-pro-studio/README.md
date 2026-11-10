# VizCritique Pro Desktop

**Score a Tableau dashboard against a locked 7-domain rubric plus ethics gatekeeper.** Read-only. Two-tier delivery: short chat summary + opt-in longform file to Downloads.

## When to Use

- You just built a dashboard and want a professional-grade critique before stakeholder review.
- You inherited a dashboard and want to know if it's ready to ship.
- You're prepping for a design-review meeting and want a scored critique to bring in.

## When Not to Use

- **Rebuilding the dashboard.** Use `viz-planner` for redesign, `worksheet-builder` for chart authoring.
- **Chart-type-only advisory on one worksheet.** Use `chart-swap-advisor`.
- **Pre-publish assembly hygiene without a full critique.** Use `dashboard-preflight`.
- **Format-string drift.** Use `format-drift-scanner`.
- **Text-copy correctness.** Use `desktop-spellcheck`.
- **Localization fragility.** Use `i18n-scanner`.
- **Data-quality issues.** Use `data-quality-review`.
- **Interaction runtime behavior.** Use `interaction-validator`.

## How It Works

**Image required.** Paste a screenshot of the dashboard. Skill asks if missing. If your dashboard scrolls beyond one screen (aspect ratio 2:1+), paste the top half and the skill will offer per-section re-runs.

**Workbook open (optional).** If your workbook is open, the skill pulls dashboard structure via `get-dashboard-xml` to sharpen chart-type and layout scoring. If closed, the skill runs image-only.

**Ethics first.** Every run starts with an ethics-and-privacy gatekeeper. Critical violations cap the score at 59/100. Warning violations cap at 79/100. Info observations don't cap.

**7 domains, locked weights.**

| Domain | Weight |
|---|---|
| 1. Audience Adaptation | 12% |
| 2. Message Alignment | 12% |
| 3. Chart Usage | 18% |
| 4. Layout and Hierarchy | 18% |
| 5. Color and Typography | 12% |
| 6. Accessibility | 14% |
| 7. Interactive-Design Signals | 14% |

**Two-tier delivery.**

- **Tier A (chat):** Overall score, tier, top 2 strengths, top 3 recommendations, per-domain scores, next-step routing. Under 15 lines.
- **Tier B (optional file):** Full longform review to your Downloads folder as `.md` or `.txt`. Executive summary, ethics section, per-domain rationale with signals, rebuild handoff payload.

## Tier Table

| Score | Tier | What It Means |
|---|---|---|
| 90-100 | Exemplary | Best-in-class. Publishable as a template. |
| 80-89 | Strong | Meets professional bar. Minor sharpening. |
| 70-79 | Solid | Functional and defensible. Some gaps. |
| 60-69 | Developing | Ships with reservations. |
| 50-59 | Needs work | Not ready for stakeholder review. |
| 0-49 | Rework | Redesign recommended. Route to viz-planner. |

## Example Trigger Phrases

- "Review this dashboard"
- "Critique this viz"
- "Score this dashboard"
- "Grade this dashboard"
- "Evaluate my dashboard"
- "How does this dashboard rate"
- "Viz critique"

## What the Skill Does Not Score

- **Runtime behavior.** Design signals only; runtime routes to `interaction-validator`.
- **Data content quality.** Underlying data quality routes to `data-quality-review`.

## Output Handoff

Emits `viz_critique_report/1` per the locked schema. Consumed by `viz-planner` (redesign input at Rework tier), `worksheet-builder` and `chart-swap-advisor` (per-chart rebuild payloads), `dashboard-preflight` (layout findings), `format-drift-scanner` (color and typography drift), `interaction-validator` (runtime verification), and `workbook-auditor` (critique score deltas across runs).

## Known Limitations

- One dashboard per run. Batching is refused.
- Image reader reliability on long-form dashboards. Aspect ratios taller than 2:1 trigger per-section re-runs; Layout and Interactive-Design domains flag UNSCANNED on partial coverage.
- Cannot verify interaction runtime behavior.
- Cannot evaluate pixel-level palette compliance beyond accessibility scoring.
- Cannot audit workbook data content.

## Distribution

Ships with Tableau Studio. Also available on Skills Exchange for latest-version pulls between Studio releases.
