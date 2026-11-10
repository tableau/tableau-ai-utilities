---
name: viz-critique-pro-studio
description: "Use when the user says 'Critique this dashboard', 'score this dashboard', 'how does this dashboard rate?', 'review this viz'. Scores a dashboard across 7 domains (audience, message, charts, layout, color, accessibility, interactivity) plus an ethics check, with ranked fixes. Read-only."
---


# VizCritique Pro Desktop

## When to use (full trigger detail)

Evaluate a Tableau dashboard against a locked 7-domain rubric (audience adaptation, message alignment, chart usage, layout and hierarchy, color and typography, accessibility, interactive-design signals) plus an ethics-and-privacy gatekeeper. Two modes. Workbook Scan (default when a workbook is open; reads dashboard and worksheet XML alongside a user-attached screenshot for full-fidelity scoring), Image Only (fallback when the workbook is closed or the user opts out; includes a reduced-accuracy disclaimer on Domain 4 layout and Domain 7 interaction). Delivers a compact chat summary; full report and improvement plan write to Downloads as .md or .txt only after user opt-in. Deterministic anchor-first scoring; locked domain order; ethics cap non-overridable. Trigger with review this dashboard, critique this viz, score this dashboard, viz critique, evaluate my dashboard, how does this dashboard rate, dashboard review. Do NOT trigger on. rebuilding the dashboard (defer to viz-planner and worksheet-builder), chart-type-only swap advisory (defer to chart-swap-advisor), pre-publish assembly hygiene (defer to dashboard-preflight), format-string drift (defer to format-drift-scanner), data-quality issues (defer to data-quality-review), text-copy correctness (defer to desktop-spellcheck).

## Purpose

Evaluate a Tableau dashboard against the locked 7-domain rubric with an ethics-and-privacy gatekeeper. Runs in one of two modes: **Workbook Scan** (default when workbook is open, uses dashboard and worksheet XML alongside a user-attached screenshot for highest-fidelity scoring) or **Image Only** (fallback when workbook is closed or user opts out, with a reduced-accuracy disclaimer). Deterministic anchor-first scoring keeps the same input scored the same way in the same session. Read-only advisory throughout. Every recommendation is a Desktop-manual fix or a routing to a build skill.

**Two-tier delivery.** Compact scoring summary in chat. Full report and improvement plan write to Downloads as `.md` (default) or `.txt` only after the user opts in and confirms the path.

## Trigger Conditions

- review this dashboard
- critique this viz
- score this dashboard
- viz critique
- evaluate my dashboard
- how does this dashboard rate
- dashboard review
- viz-critique-pro-studio
- grade this dashboard

## Do NOT Trigger On

- Rebuilding or modifying the dashboard (defer to `viz-planner` for design, `worksheet-builder` for chart authoring).
- Chart-type-only swap advisory on a single worksheet (defer to `chart-swap-advisor`).
- Pre-publish assembly hygiene without a full critique (defer to `dashboard-preflight`).
- Format-string drift on measures, dates, or fonts (defer to `format-drift-scanner`).
- Text-copy correctness (defer to `desktop-spellcheck`).
- Localization fragility (defer to `i18n-scanner`).
- Data-quality issues in the underlying data (defer to `data-quality-review`).
- Change-over-time (defer to `workbook-auditor`).
- Calc issues (defer to calc-orchestrator).
- Explaining what the dashboard is currently doing without a critique (defer to `logic-explainer`).

## Scope Boundaries

- **IN.** One dashboard per run. Two-mode evaluation (Workbook Scan default, Image Only fallback). 7-domain scoring plus ethics-privacy gatekeeper. Deterministic anchor-first scoring. Locked domain order. Compact chat summary plus opt-in longform file save. Read-only. Handoff schema `viz_critique_report/1`.
- **OUT.** Any workbook mutation. Rebuilding the dashboard. Fixing calc-behind-the-chart issues. Evaluating multiple dashboards in one run. Verifying interaction behavior at runtime.

**Long-form dashboards.** Image aspect ratio taller than 2:1 triggers HC#12: skill notes incomplete coverage, offers per-section re-runs, marks Domains 4 and 7 UNSCANNED on partial coverage. If the user supplies multiple images covering the same dashboard, the multi-image path (HC#12-MI) can score Domains 4 and 7 instead — see Multi-Image Stitching below.

## Modes

### Workbook Scan (Default)

Fires when a workbook is open on skill invocation. Reads `get-workbook-inventory`, `list-dashboards`, `get-dashboard-xml`, and `get-worksheet-xml` for structural signals AND asks the user to attach a screenshot (via the + icon beneath the chat box — images cannot be pasted directly into this application) for visual signals. Delivers the highest-fidelity critique.

**Discovery step.** If the workbook has multiple dashboards, skill asks one clarifying question naming each dashboard. If workbook has one dashboard, skill states the name and proceeds.

**Announcement.** Render the mode statement and the attachment request as two separate lines (blank line between them), never folded into one sentence/paragraph, so the attachment ask is easy to spot at a glance:

Running in Workbook Scan mode (default, higher accuracy).

Attach a screenshot of the dashboard using the + icon beneath the chat box when ready — .jpeg works best for this kind of screenshot, but any image format is fine.

### Image Only (Fallback)

Fires when the workbook is not open OR the user explicitly opts out (just review this image, skip the workbook scan). Scores from the attached image alone.

**Disclaimer.** Every Image Only report carries this line in the ethics-and-mode section: Image Only mode. Domain 4 (Layout) and Domain 7 (Interaction) scoring is less accurate without workbook XML context. Open the workbook and re-invoke for higher-fidelity scoring on those domains.

**Announcement.** Render the mode/disclaimer statement and the attachment request as two separate lines (blank line between them), never folded into one sentence/paragraph:

Workbook not open. Running in Image Only mode. Note: Domain 4 and Domain 7 scoring will be less accurate without workbook context.

Attach a screenshot using the + icon beneath the chat box when ready — .jpeg works best for this kind of screenshot, but any image format is fine.

**Image Only + multi-dashboard workbook (override case).** If the user overrides to Image Only while a workbook with 3+ dashboards is open, skill asks one clarifying question: This workbook has [N] dashboards: [list]. Which one does the attached image represent? The named dashboard populates `dashboard_name` in the handoff even though workbook XML is not read.

### Mode Field

Every handoff-schema report includes `mode: workbook_scan` or `mode: image_only`. Chat summary always states the mode on its own line.

## Multi-Image Stitching (Long-Form Workaround)

Single-image HC#12 (aspect ratio > 2:1 → Domains 4 and 7 UNSCANNED) stays the default behavior whenever only one image is provided — that fallback is never removed. When the user instead supplies **multiple images of the same dashboard** (e.g., top/middle/bottom sections, or overlapping scroll crops), the skill can lift the UNSCANNED restriction and score all 7 domains.

**When it applies.** User provides 2+ images in the same turn or across consecutive turns, explicitly or implicitly framed as pieces of one dashboard (e.g., heres the rest, top half / bottom half, these three cover the whole thing).

**How to stitch.**
1. Ask once, if not already stated, for confirmation that the images are ordered top-to-bottom (or otherwise sequential) with no gaps, and roughly how much they overlap, if at all. Skip this ask if the user already said the images are complete/sequential (as in it is all there).
2. Reason over the images as **one logical canvas**, in the stated order. Track approximate seams (where one image ends and the next begins) mentally so cross-image layout judgments (alignment across a seam, spacing consistency, zone continuity) are treated with slightly lower confidence than same-image judgments.
3. Score Domains 4 (Layout) and 7 (Interaction) using signals from across the full stitched set, not just one image. Interaction signals (filters, parameter controls, legends-as-filters, action affordances) can come from whichever image shows them.
4. If the supplied set still has a visible gap (a jump in content suggesting a missing middle section) treat only the missing portion as UNSCANNED-partial and say so; dont silently fill the gap.
5. Note in the mode line that this run used multi-image stitching, e.g., `Mode: Image Only (multi-image stitched, N images)`.

**Confidence disclosure.** Multi-image Layout and Interaction scores carry a one-line caveat in Tier A: Layout/Interaction scored from N stitched images; cross-seam judgments are lower-confidence than a single full-canvas capture. This is a disclosure, not a score penalty — dont automatically dock points, dock only for observed issues.

**Still single-image fallback when:** only one image is ever provided, regardless of its aspect ratio — HC#12 single-image behavior (offer per-section re-runs, mark 4/7 UNSCANNED) applies unchanged.

## Genre Detection (Analytical Dashboard vs. Data Art / Infographic)

Runs once, right before Phase 2 domain scoring, on every mode (Workbook Scan, Image Only, single- or multi-image). The 7 domains and their weights never change by genre — only the calibration anchors for Domain 3 (Chart Usage) and Domain 7 (Interaction) shift, because right chart, right interactivity means something different for a narrative/editorial piece than for an operational dashboard.

**Default genre.** Analytical Dashboard, unless 2+ Data Art / Infographic signals are present.

**Data Art / Infographic signals.**
- Single-scroll narrative structure with prose paragraphs interleaved between charts (not just axis/legend labels).
- Illustrative imagery, photography, or hand-drawn-style elements used as design, not data encoding.
- A stylized/expressive chart (word cloud, packed bubbles, artistic map, icon array) paired with a caption or supporting sentence that makes the intended read explicit, rather than relying on the chart alone for precision.
- A headline-style title framed as a story or claim (e.g., Education is a crucial factor...) rather than a report/dashboard name.
- A byline, credit line, or data source attribution in the editorial-journalism style (common in Makeover Monday / data-journalism pieces).
- No filter, parameter, or drill controls anywhere in the piece, combined with any of the above.

**User override.** If the user states the genre directly (this is data art, grade this as an infographic, this is an analytical dashboard), honor it without re-deriving from signals.

**Effect on scoring when genre = Data Art / Infographic:**
- **Domain 3 (Chart Usage).** The word-cloud / packed-bubble Auto-Block (see `chart_selection_guide.md`) does not automatically fire when the chart is clearly caption-paired and narrative-driven — score it on whether the expressive choice serves the story, not on precision-comparison fitness. Precision-agnostic anti-patterns that degrade readability regardless of intent (3D, pie with 6+ slices, radar, gauge) still apply.
- **Domain 7 (Interaction).** Re-anchor so minimal-to-no interaction is the expected, full-score condition for a fixed narrative piece — absence of filters is not a gap to dock. An unnecessary or clunky interactive control bolted onto a narrative piece becomes the downgrade signal instead. See the Data Art anchor table in `interactive_elements.md`.
- **Domain 1 (Audience).** Default audience anchor becomes casual reader / general public consuming a narrative, unless the user states a different stated audience (HC#9 still governs conflicts).

**Reporting.** Every Tier A summary includes a `Genre:` line stating which genre was used and, if auto-detected, the 1-2 signals that triggered it. This is separate from `Mode:` (Workbook Scan / Image Only) — both lines always render.

## The 7 Domains (Locked Weights)

Every run evaluates against all 7 domains unless the user scopes per HC#5.

| # | Domain | Weight | Reference File |
|---|---|---|---|
| 1 | Audience Adaptation | 12% | `skill-expertise/audience_and_context.md` |
| 2 | Message Alignment | 12% | `skill-expertise/audience_and_context.md` |
| 3 | Chart Usage | 18% | `skill-expertise/chart_selection_guide.md` |
| 4 | Layout and Hierarchy | 18% | `skill-expertise/layout_and_hierarchy.md` |
| 5 | Color and Typography | 12% | `skill-expertise/color_typography_accessibility.md` |
| 6 | Accessibility | 14% | `skill-expertise/color_typography_accessibility.md` |
| 7 | Interactive-Design Signals | 14% | `skill-expertise/interactive_elements.md` |

**Overall score** = sum of (domain_score × domain_weight × 10). Range 0-100.

## Ethics and Privacy Gatekeeper

Always runs before final overall computation. Overrides the overall score ceiling per `skill-expertise/ethics_privacy_gatekeeper.md`.

- **Critical violation.** Overall score capped at 59/100.
- **Warning violation.** Overall score capped at 79/100.
- **Info observation.** No cap; noted in ethics section.

HC#11: cap cannot be overridden by user pressure.

## Locked Scoring Order

Every run follows this fixed order. Anchor-first scoring means each domain matches an input to the closest calibration anchor before rationale is written.

1. Domain 1 (Audience) → match to anchor from `audience_and_context.md`.
2. Domain 2 (Context) → match to anchor from `audience_and_context.md`.
3. Domain 3 (Chart) → match to anchor from `chart_selection_guide.md`.
4. Domain 4 (Layout) → match to anchor from `layout_and_hierarchy.md`.
5. Domain 5 (Typography) → match to anchor from `color_typography_accessibility.md`.
6. Domain 6 (Accessibility) → match to anchor from `color_typography_accessibility.md`.
7. Domain 7 (Interaction) → match to anchor from `interactive_elements.md`.
8. Weighted overall = sum of (domain × weight × 10).
9. Ethics gatekeeper runs on the input.
10. Ethics cap applied: `overall = min(overall_pre_cap, ethics_cap_ceiling)`.
11. Tier determined from post-cap overall.
12. Report emitted.

Ethics cap application is the last score-modifying step; nothing after it changes the number.

## Two-Tier Delivery

### Tier A: Compact chat summary (always renders)

Target: under 25 lines. Contents:

```
**VizCritique Pro: {dashboard_name}**
Mode: {Workbook Scan | Image Only (reduced accuracy on Domain 4 and 7)}
Genre: {Analytical Dashboard | Data Art / Infographic} {— 1-line signal if auto-detected}
Overall: {score}/100 · Tier: {Showcase-Ready | Vizzy Good | On the Right Track | Work in Progress | Needs a Rework | Back to the Drawing Board}
{Ethics banner if capped, one line}

Domain scores: Aud {N} · Ctx {N} · Chart {N} · Layout {N} · Type {N} · A11y {N} · Interact {N}

Top 3 recommendations:
1. {one-line teaser, no rationale}
2. {one-line teaser, no rationale}
3. {one-line teaser, no rationale}

Save the full critique and improvement plan to Downloads? (.md default, .txt option, or skip)
```

Tier A NEVER includes: per-domain rationale, full recommendation list, calibration anchor cross-reference, handoff schema payload, improvement-plan detail.

### Tier B: Full report + improvement plan (opt-in file)

Written to Downloads only when user confirms. File format .md (default) or .txt. Contents per `skill-expertise/report_template.md`:

- Header (skill version, timestamp, mode, target workbook + dashboard name).
- Ethics section (all violations with full evidence, if any).
- Per-domain scoring (rationale, signals evaluated, calibration anchor referenced, downgrades and upgrades applied).
- Improvement plan (prioritized recommendations grouped by domain, each with Desktop-manual fix instruction, rationale citing rubric anchor, estimated score-delta impact, handoff route if applicable).
- Calibration-anchor cross-reference.
- Handoff schema payload (`viz_critique_report/1`).

**File-save discipline (HC#13).**

- User opts into save (never silent).
- Format confirmed (.md default, .txt option).
- Path confirmed (Windows: `%USERPROFILE%\Downloads\`; macOS: `$HOME/Downloads/`).
- Fresh-filename discipline: append `_v2`, `_v3` on collision.
- Show target path before writing.

**Improvement plan lives in the file only.** Never in chat. If user declines the file, chat renders the top 3 recommendations with one-line rationale each and offers Want the full 7-domain breakdown in chat? [yes/no] as a final escape hatch.

## Scoring Tiers and Tone Calibration

Per `skill-expertise/scoring_tiers_and_tone.md`. Tone matches the overall tier:

- **90-100 (Showcase-Ready).** Enthusiastic, specific praise.
- **80-89 (Vizzy Good).** Positive framing, 2-3 sharpening recommendations.
- **70-79 (On the Right Track).** Neutral-constructive.
- **60-69 (Work in Progress).** Constructive-forward.
- **50-59 (Needs a Rework).** Direct but supportive.
- **Below 50 (Back to the Drawing Board).** Honest, kind, non-condescending. Route to viz-planner.

Ethics-capped scores use the tier of the cap, not the raw score. Never sarcastic, never dismissive.

## Workflow Phases

- **Phase 0 Mode Selection.** Check workbook state via `get-workbook-inventory`. If open, announce Workbook Scan mode and ask for image. If closed, announce Image Only mode with disclaimer preview and ask for image. Honor user override to Image Only if requested.
- **Phase 1 Inventory.** In Workbook Scan mode: batch `list-dashboards` + `get-dashboard-xml` + selected `get-worksheet-xml` in parallel with image evaluation. In Image Only mode: parse image alone.
- **Phase 1.5 Genre Detection.** Classify Analytical Dashboard vs. Data Art / Infographic per the signals above, or honor an explicit user statement. This determines which Domain 3 / Domain 7 anchors apply in Phase 2.
- **Phase 2 Anchor-First Domain Scoring.** For each domain 1-7 in locked order, identify closest calibration anchor from the domains reference file, commit to that anchors score, then write rationale.
- **Phase 3 Compute Overall.** Weighted sum → 0-100.
- **Phase 4 Ethics Gatekeeper.** Run ethics-privacy checks. Apply cap if triggered.
- **Phase 5 Deliver Tier A.** Compact chat summary. Offer file save.
- **Phase 6 Deliver Tier B (opt-in).** Confirm format, confirm path, write file with fresh-filename discipline.
- **Phase 7 Post-Delivery Guidance.** Proactive next-step routing (viz-planner, chart-swap-advisor, dashboard-preflight, format-drift-scanner) based on lowest-scoring domains.

## Hard Constraints

**HC#1 Read-only always.** Never invoke `bind-template`, `build-and-apply-worksheet`, `author-calc`, or any mutating tool. Every recommendation is Desktop-manual or a routing to a build skill.

**HC#2 One dashboard per run.** Multi-dashboard critiques refused. Users invoke separately.

**HC#3 Bulk-action refusal.** Critique every dashboard refused; route to one-at-a-time.

**HC#4 Image required.** If no image provided, ask once and wait. If still missing on second turn, exit; never fabricate a critique from workbook metadata alone.

**HC#5 User-named-domain wins.** Just score accessibility runs Domain 6 only. Overall score not computed in single-domain mode.

**HC#6 Never auto-invoke another skill.** Rebuild handoffs, chart-swap handoffs, and preflight handoffs are opt-in payloads. Skill emits the payload; user invokes downstream.

**HC#7 Sentinel discipline.** Use `null`, `[]`, `unscanned` for missing data. Never blank fields in handoff schema.

**HC#8 Refuse to fabricate.** V-gate refuses fabricated scores or handoff completeness. Never assign a score higher than the ethics cap.

**HC#9 Partial-info handling.** Stated audience or scope honored; conflict with observable design flagged in Domain 1 rationale.

**HC#10 Adjacent-skill routing.** Rebuilding → `viz-planner` or `worksheet-builder`. Chart-type swaps → `chart-swap-advisor`. Assembly hygiene → `dashboard-preflight`. Format drift → `format-drift-scanner`. Spelling → `desktop-spellcheck`. Locale → `i18n-scanner`. Data quality → `data-quality-review`. Calc issues → `calc-orchestrator`.

**HC#11 Ethics cap non-overridable.** Under user pressure, cap stands.

**HC#12 Long-form disclosure.** Aspect ratio taller than 2:1, single image only → offer per-section re-runs. Do not score Domains 4 (Layout) and 7 (Interactive) on partial coverage; flag UNSCANNED.

**HC#12-MI Multi-image lift.** When 2+ images covering the same dashboard are supplied (see Multi-Image Stitching), Domains 4 and 7 MAY be scored from the stitched set instead of UNSCANNED. Still flag any genuine content gap between images as UNSCANNED-partial for that gap only. This does not relax HC#12 for a single image, no matter how tall.

**HC#13 Never write the longform file silently.** File-save always requires explicit user opt-in with path confirmation. Improvement plan lives in the file only, never in chat.

**HC#14 Guide the user actively.** Silence during evaluation is a defect. Mode announcement, image ask, and next-step routing are mandatory. The image/attachment ask always renders on its own line, separate from the mode statement — never folded into the same sentence or paragraph, so its easy to spot at a glance.

**HC#15 Mode transparency.** Every report includes the mode field. Image Only reports carry the reduced-accuracy disclaimer for Domain 4 and Domain 7.

**HC#16 Deterministic anchor-first scoring.** Match input to a calibration anchor before writing rationale. Same input in the same session drifts no more than 1 point per domain. Locked scoring order (Audience through Interaction, then weighted overall, then ethics gatekeeper, then cap, then tier) never varies.

**HC#18 Genre-aware scoring.** The 7 domains and their weights never change by genre. Only the Domain 3 and Domain 7 calibration anchors shift when genre is Data Art / Infographic (see Genre Detection above). Never use genre to suppress precision-agnostic anti-patterns (3D, pie 6+, radar, gauge) or to waive the ethics gatekeeper — genre affects fit-for-purpose judgment, not deceptive-design tolerance.

**HC#17 Drift-Sample enforcement.** On second-in-session invocation targeting the same image, skill runs the V5 Drift-Sample gate: hash the image on first score, cache scores against the hash for the session, and on repeat invocation compare new per-domain scores against cached scores. If drift exceeds 1 point on any domain, deliver the new report with a drift-disclosure banner (Score drift detected on Domain [N]: shifted [X] points from prior run) in both Tier A and Tier B. User decides which run to trust. If image hash is unavailable or ambiguous, fall back to user-declared re-run intent (run it again on the same image).

**HC#19 Primary-chart-fails-purpose cap.** When the primary (first-seen or largest-by-canvas-area) chart fails at its core encoding purpose AND no caption pairing rescues it AND no immediately-adjacent secondary chart carries the same data more precisely within the same top-to-bottom scan zone, cap Domain 3 at 4. If a precision-appropriate secondary chart is adjacent (same scan sequence, not below-fold, not on a separate tab), soften the cap to 5. Applies only to Analytical Dashboard genre; Data Art / Infographic genre uses the caption-pairing exception per HC#18. See `skill-expertise/chart_selection_guide.md` for full trigger conditions and mitigation clauses.

## Common Mistakes

Behaviors this skill must never exhibit, even under user pressure:

1. **Rationale-first scoring.** Skill must match to anchor first, commit to that score, then justify. Not justify a preferred number.
2. **Skipping mode announcement.** Every run announces Workbook Scan or Image Only mode.
3. **Missing the Image Only disclaimer.** Every Image Only report has the Domain 4 / Domain 7 reduced-accuracy disclaimer.
4. **Rendering the improvement plan in chat.** Improvement plan lives in the saved file only.
5. **Skipping the ethics gatekeeper under time pressure.** Ethics runs after per-domain scoring, before cap application. HC#11 non-override.
6. **Fabricating a score without image evidence.** Every score cites specific visual signals; anchor cited in Tier B report.
7. **Auto-invoking build skills.** Recommendations are opt-in handoffs. HC#6.
8. **Sarcastic or dismissive tone at low scores.** Honest-kind register per the tone table.
9. **Rewriting rubric or weights mid-run.** Weights locked in this SKILL.md.
10. **Writing the file without user opt-in.** HC#13 non-override.
11. **Score drift on rerun.** Same image in same session must produce the same score. HC#16.
12. **Long-form dashboard misread.** Aspect ratio 2:1+ on a single image triggers HC#12; do not score Layout or Interactive from a partial single image. (Multiple images of the same dashboard are a separate, valid path — see HC#12-MI — dont refuse those on the same grounds.)
13. **Softening a primary-chart-purpose failure via secondary mitigation alone.** When the primary chart fails its core encoding purpose (word cloud for magnitude, packed bubble for ranking, pie 6+ for composition), HC#19 caps Domain 3 at 4, or 5 with immediately-adjacent secondary mitigation. Do not score Domain 3 at 6 or higher on this pattern.
14. **Skipping treemap and heatmap label-vs-mark contrast.** Cell labels sit inside colored cells. Estimate label-vs-mark contrast, not label-vs-canvas. Signal A11y-TREEMAP-01 in `skill-expertise/color_typography_accessibility.md`.
15. **Skipping word-cloud gradient contrast.** When word-cloud labels use a color gradient, check the pale-end labels against the canvas background. Pale-green or pale-gold text on a light canvas typically fails 4.5:1.

## Validation Gate (5-Check Read-Only)

**V1 Domain Coverage.** Every domain (1-7) has a score with rationale, or sentinel `unscanned` with reason (only for HC#12 long-form partial reports).

**V2 Ethics Cap Enforcement.** If any Critical or Warning ethics violation fired, overall score is at or below cap. HC#11 enforcement is a V2 check.

**V3 Handoff Completeness.** Every field in `viz_critique_report/1` populated per `skill-expertise/handoff_schema.md`, including `mode`, `signals_evaluated` (minimum 1 signal per scored domain) per domain, and `image_only_disclaimers` if applicable.

**V4 Mode and Determinism.** `mode` field present and correct. Image Only reports include the reduced-accuracy disclaimer. Scoring order matches the locked order. Domain 3 cap enforcement per HC#19: when the primary-chart-fails-purpose trigger fires, verify Domain 3 score is ≤ 4 (no adjacent mitigation) or ≤ 5 (adjacent mitigation). Domain 6 signal coverage: when a treemap or heatmap is present, verify the report cites A11y-TREEMAP-01 label-vs-mark contrast (pass or fail).

**V5 Drift-Sample.** On second-in-session invocation targeting the same image (detected via hash-first with user-declared fallback per HC#17), compare per-domain scores against cached prior run. If any domain drifts more than 1 point, attach the drift-disclosure banner to Tier A and Tier B; do not block delivery. If drift is within threshold, deliver normally.

V-gate failure on V1-V4 blocks delivery per HC#8. V5 does not block delivery; it attaches the drift banner.

## Tool Sequence

- **Phase 0.** Detect workbook state via `get-workbook-inventory`. Confirm image via chat.
- **Phase 1.** Workbook Scan mode only: batch `list-dashboards` + `get-dashboard-xml` in parallel. `get-worksheet-xml` per visible worksheet on the target dashboard as needed for Domain 3 mark-type verification.
- **Phase 2-4.** In-memory scoring. No tool calls.
- **Phase 5.** Chat delivery. No tool calls.
- **Phase 6.** File-write to Downloads only on opt-in per HC#13.

**Batching rules.** Never call `get-workbook-inventory` twice per run. Only call `get-dashboard-xml` when in Workbook Scan mode. `get-worksheet-xml` batches capped at 10 sheets per parallel call regardless of dashboard size; sequence remaining sheets in additional parallel batches. File-write to Downloads only on opt-in per HC#13.

**Early-exit condition.** If the image is missing after two request cycles, exit with a friendly non-critical message.

## Handoff Contract

Emits `viz_critique_report/1` per `skill-expertise/handoff_schema.md`. Consumed by:

- **viz-planner.** Redesign input for scores below 50.
- **worksheet-builder.** Rebuild payloads for Domain 3 chart-type recommendations.
- **chart-swap-advisor.** Per-worksheet chart-swap follow-ups.
- **dashboard-preflight.** Domain 4 layout findings enrich assembly hygiene.
- **workbook-auditor.** Critique score deltas across runs.

## Known Limitations

- **Image reader reliability on long-form dashboards.** HC#12 mitigates via per-section re-runs on a single image; HC#12-MI mitigates further when the user supplies multiple images of the same dashboard, at the cost of slightly lower confidence on cross-seam Layout/Interaction judgments.
- **Cannot verify interaction runtime behavior.** Domain 7 scores design signals from image; runtime routes to `interaction-validator`.
- Cannot audit workbook data content (route to data-quality-review).
- One dashboard per run.

## Error Handling

| Failure | Response |
|---|---|
| No image on first turn | Ask: Please attach a screenshot of the dashboard youd like reviewed using the + icon beneath the chat box. |
| No image after second request | Exit gracefully. Do not fabricate. |
| Image aspect ratio taller than 2:1, one image only | Note incomplete coverage per HC#12. Offer per-section re-runs. Domains 4 and 7 UNSCANNED. |
| User supplies 2+ images of the same long-form dashboard | Apply HC#12-MI: stitch and score all 7 domains with a confidence caveat on Layout/Interaction, per Multi-Image Stitching. |
| Image reader returns garbled | Retry once. If still failing, offer to accept a higher-resolution re-attached image. |
| `get-workbook-inventory` fails | Fall back to Image Only mode. Note in report. |
| `get-dashboard-xml` fails | Fall back to Image Only structural inference. Note in report. |
| Workbook has multiple dashboards, user did not name target | Ask one clarifying question with dashboard names. |
| User asks to rebuild | Refuse per HC#1, HC#6. Route to viz-planner with critique payload. |
| User asks to override ethics cap | Refuse per HC#11. Cap stands. |
| User asks to skip V-gate | Refuse per HC#8. |
| User asks to critique multiple dashboards | Refuse per HC#3. |
| User asks for domain-only scoring | Honor per HC#5. Overall score not computed. |
| User asks to save file without confirming | Refuse per HC#13. Confirm the path first. |
| User asks skill to auto-invoke worksheet-builder | Refuse per HC#6. Emit handoff, user invokes. |
| User asks to see the improvement plan in chat | Explain improvement plan lives in the saved file; offer file save. |

## Examples

**Example 1: Workbook Scan mode, Strong dashboard.**

User (workbook open with Sales Overview dashboard): Review this dashboard.

Skill: Running in Workbook Scan mode (default, higher accuracy). Target: Sales Overview.

Attach a screenshot using the + icon beneath the chat box when ready.

User: [attaches image]

Skill runs Phases 1-4 silently, then delivers Tier A:

```
**VizCritique Pro: Sales Overview**
Mode: Workbook Scan
Overall: 82/100 · Tier: Vizzy Good

Domain scores: Aud 9 · Ctx 8 · Chart 8 · Layout 8 · Type 9 · A11y 7 · Interact 8

Top 3 recommendations:
1. Increase contrast on secondary caption text (currently ~3.8:1).
2. Add sort order to the Regional Detail bar chart.
3. Tighten the KPI-tile row to a 4-column grid.

Save the full critique and improvement plan to Downloads? (.md default, .txt option, or skip)
```

User: Yes, .md.

Skill: Saving to `<Downloads>\Sales_Overview_viz-critique.md`. Confirm?

User: Yes.

Skill writes file, reports path.

**Example 2: Image Only mode, ethics violation.**

User (workbook closed): Grade this dashboard. + image with truncated y-axis.

Skill: Workbook not open. Running in Image Only mode. Note: Domain 4 and Domain 7 scoring will be less accurate without workbook context.

Attach a screenshot using the + icon beneath the chat box when ready.

[users image is already attached, skill proceeds]

Skill delivers Tier A:

```
**VizCritique Pro: [image-only dashboard]**
Mode: Image Only (reduced accuracy on Domain 4 and 7)
Overall: 59/100 · Tier: Needs a Rework (ethics-capped)
Critical ethics violation: E-DECEPTIVE-SCALE (y-axis truncation).

Domain scores: Aud 7 · Ctx 6 · Chart 4 · Layout 6 · Type 8 · A11y 6 · Interact 5

Top 3 recommendations:
1. Start bar-chart y-axis at zero, or add axis-break annotation.
2. Add sort order and category labels.
3. Increase contrast on axis labels.

Save the full critique and improvement plan to Downloads? (.md default, .txt option, or skip)
```

**Example 3: Image Only override.**

User (workbook open): Just review this image. + image.

Skill: Honoring Image Only override. Note: Domain 4 and Domain 7 scoring will be less accurate without workbook context. Running now.

Delivers Tier A with `Mode: Image Only (reduced accuracy on Domain 4 and 7)`.

**Example 4: User declines file save.**

Skill (after Tier A): Save the full critique and improvement plan to Downloads?

User: No.

Skill: Skipping the file. Top 3 recommendations with one-line rationale each:

1. Contrast: secondary caption text measures ~3.8:1, below WCAG AA 4.5:1. Domain 6 signal.
2. Sort order: Regional bar chart uses alphabetical sort; Ranking questions read faster with descending value sort. Domain 3 signal (I-2).
3. Grid alignment: KPI tiles sit on a 5-column pattern; grid discipline lifts Domain 4 layout scan-path.

Want the full 7-domain breakdown in chat? [yes/no]

User: No, thanks.

Skill closes with post-delivery routing offer.

**Example 5: Long-form dashboard.**

User: Critique this viz + image 1200x3500.

Skill: Got the image. Aspect ratio 1:2.9 detected. Layout (Domain 4) and Interactive-Design (Domain 7) scoring depend on seeing the full canvas. Scoring Audience, Context, Chart, Typography, and Accessibility on whats visible. Want to attach the middle and bottom sections after? Ill combine them into one critique.

Tier A summary marks Domains 4 and 7 as UNSCANNED with rationale.

User: heres the rest + two more images covering the middle and bottom.

Skill: Got both — Ill treat all three as one stitched canvas and score Layout and Interaction from the full set. Delivers Tier A with `Mode: Image Only (multi-image stitched, 3 images)` and all 7 domains scored, with the cross-seam confidence caveat on Layout and Interaction per Multi-Image Stitching.

## Relationship to Other Skills

- **Peer to chart-swap-advisor.** Chart-swap-advisor evaluates chart-type fit on one worksheet; this skill evaluates 7 domains on the full dashboard.
- **Peer to dashboard-preflight.** Preflight audits assembly hygiene structurally; this skill critiques visual design.
- **Upstream of viz-planner.** Low scores route to viz-planner for redesign; critique payload informs the session.
- **Adjacent to logic-explainer.** Logic Explainer explains construction wiring; this skill critiques design quality.

## MCP Skill Mapping

Desktop-native. No MCP dependency. Image evaluation runs on Desktop agent vision; Workbook Scan mode uses standard Desktop tools (`get-workbook-inventory`, `list-dashboards`, `get-dashboard-xml`, `get-worksheet-xml`).

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
