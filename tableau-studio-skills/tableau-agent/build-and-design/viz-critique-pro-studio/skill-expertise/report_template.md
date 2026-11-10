# Report Template (Locked, Chat + File)

Every `viz-critique-pro-studio` delivery follows this shape. Compact chat summary (Tier A), then optional longform review file with improvement plan (Tier B). Never deviate from the section order; never rename headers.

## Two-Tier Delivery

**Tier A: Compact chat summary.** Renders every run. Target: under 25 lines total. Includes mode, overall score, tier, ethics banner if capped, 7-domain scoreline, top 3 one-line recommendations, and file-save offer. Never includes per-domain rationale, full recommendation list, or improvement plan.

**Tier B: Longform review file with improvement plan.** Written to Downloads only when user opts in. Full per-domain rationale, ethics section, prioritized improvement plan, calibration-anchor cross-reference, and handoff payload.

## Tier A: Compact Chat Summary

```markdown
**VizCritique Pro: {dashboard_name}**
Mode: {Workbook Scan | Image Only (reduced accuracy on Domain 4 and 7)}
Overall: {N}/100 · Tier: {Showcase-Ready | Vizzy Good | On the Right Track | Work in Progress | Needs a Rework | Back to the Drawing Board}
{Ethics banner rendered here if capped, one line, e.g.: "Critical ethics violation: E-DECEPTIVE-SCALE. Score capped at 59/100."}
{Drift banner rendered here if V5 fired, one line, e.g.: "Score drift detected: Domain 3 shifted 2 points from prior run. User decides which run to trust."}

Domain scores: Aud {N} · Ctx {N} · Chart {N} · Layout {N} · Type {N} · A11y {N} · Interact {N}

Top 3 recommendations:
1. {one-line teaser, no rationale}
2. {one-line teaser, no rationale}
3. {one-line teaser, no rationale}

Save the full critique and improvement plan to Downloads? (.md default, .txt option, or skip)
```

**Compact summary rules:**

- Target under 25 lines total.
- Mode line always shown, second line after the header.
- Overall score and tier always shown, third line.
- Ethics banner only rendered when capped; if rendered, one line.
- 7-domain scoreline as a single line for scan-ability.
- Top 3 recommendations as one-line teasers only. No "because ..." rationale, no anchor cross-reference, no impact estimate.
- Save-file offer is the last line.

**Never in Tier A:**

- Per-domain rationale.
- Full recommendation list (4+).
- Improvement plan detail (Desktop-fix steps).
- Calibration anchor citations.
- Handoff schema payload.
- V-gate output.

**Ethics banner formatting (one line each):**

- Critical: `Critical ethics violation: {rule_id}. Score capped at 59/100.`
- Warning: `Warning ethics observation: {rule_id}. Score capped at 79/100.`
- Info: not rendered in Tier A; appears in Tier B ethics section only.

**Mode line variants:**

- Workbook Scan: `Mode: Workbook Scan`
- Image Only, workbook closed: `Mode: Image Only (reduced accuracy on Domain 4 and 7)`
- Image Only, user override with workbook open: `Mode: Image Only, override (reduced accuracy on Domain 4 and 7)`

## Tier B: Longform Review File with Improvement Plan

Path: `{Downloads}/{workbook_name_or_dashboard_name}_viz-critique.md` (or `.txt`). Fresh-filename discipline: increment `_v2`, `_v3` on collision. Path resolves OS-appropriately per SKILL.md HC#13.

```markdown
# VizCritique Pro: {dashboard_name}

**Report generated:** {ISO-8601 timestamp}
**Mode:** {Workbook Scan | Image Only | Image Only, override}
**Workbook:** {workbook_name_or_null}
**Dashboard:** {dashboard_name}
**Image aspect ratio:** {width_x_height} · **Sections covered:** {full | partial}
**Overall Score:** {N}/100
**Tier:** {Showcase-Ready | Vizzy Good | On the Right Track | Work in Progress | Needs a Rework | Back to the Drawing Board}

{If Image Only mode, render this line immediately after the header block:}
**Mode disclaimer:** Image Only mode. Domain 4 (Layout) and Domain 7 (Interaction) scoring is less accurate without workbook XML context. Open the workbook and re-invoke for higher-fidelity scoring on those domains.

## Ethics and Privacy

**Status:** {No violations | Warning observation | Critical violation}
**Cap applied:** {None | 79/100 | 59/100}
**Raw pre-cap score:** {N}/100

{If any violation fired:}
- **[{trigger_id}]** {rationale citing image evidence}
  - **Severity:** {Critical | Warning | Info}
  - **Fix recommendation:** {short_string}

### Drift Sample (V5)

**Detection method:** {hash_match | user_declared | not_applicable}
**Drift detected:** {Yes | No | Not applicable (first run this session)}

{If drift detected, render this table:}

| Domain | Prior Score | New Score | Delta |
|---|---|---|---|
| {N} {name} | {X} | {Y} | {Z} |

**Note.** V5 does not block delivery; the drift banner discloses variance. Recurring drift patterns on a domain trigger a decision-tree sharpening pass in that domain's reference file.

## Executive Summary

{One or two paragraph plain-language summary. Cites overall tier, primary strengths, primary must-address items. Tone matches the tier per `scoring_tiers_and_tone.md`.}

## Per-Domain Scoring

### Domain 1: Audience Adaptation ({N}/10)

**Calibration anchor matched:** {Example 1.1 | 1.2 | 1.3}
**Confidence:** {High | Medium | Low}
**Signals evaluated:**
- {signal_1}
- {signal_2}
- {signal_3}
**Rationale.** {2-3 sentences citing specific image signals and the matched anchor.}

### Domain 2: Message Alignment ({N}/10)

{Same shape as Domain 1.}

### Domain 3: Chart Usage ({N}/10)

{Same shape. Additionally list anti-patterns matched if any.}

**Anti-patterns matched.**
- {AB-1 | AB-2 | ...}: {rationale}

### Domain 4: Layout and Hierarchy ({N}/10 or UNSCANNED)

{Same shape. If UNSCANNED (long-form partial per HC#12), render:}

**Score:** UNSCANNED
**Reason:** {layout_requires_full_canvas}
**Recommendation:** {Paste the middle and bottom sections for full coverage.}

### Domain 5: Color and Typography ({N}/10)

{Same shape.}

### Domain 6: Accessibility ({N}/10)

{Same shape.}

### Domain 7: Interactive-Design Signals ({N}/10 or UNSCANNED)

{Same shape as Domain 4. UNSCANNED variant renders when applicable.}

## Improvement Plan

{Prioritized recommendations grouped by domain, ordered by impact (highest score-delta first). Each recommendation has What / Why / How / Impact / Handoff.}

### Domain {N}: {domain_name}

1. **{recommendation_title}.**
   - **What:** {short_string}
   - **Why:** {short_string tied to the domain's calibration anchor}
   - **How:** {Desktop-manual fix steps}
   - **Estimated impact:** {+N points on Domain {X}; overall {before} → {after}}
   - **Handoff:** {none | chart-swap-advisor | format-drift-scanner | dashboard-preflight | viz-planner | worksheet-builder | interaction-validator}

{Repeat per domain until all recommendations are covered. No cap in Tier B.}

## Calibration Anchor Cross-Reference

{Table mapping each domain's score to the closest anchor in the reference files.}

| Domain | Score | Anchor Matched |
|---|---|---|
| 1 Audience | {N} | {Example 1.1 / 1.2 / 1.3} |
| 2 Context | {N} | {Example 2.1 / 2.2 / 2.3} |
| 3 Chart | {N} | {Example 3.1 / 3.2 / 3.3 / 3.4} |
| 4 Layout | {N or UNSCANNED} | {Example 4.1 / 4.2 / 4.3} |
| 5 Typography | {N} | {Example 5.1 / 5.2 / 5.3} |
| 6 Accessibility | {N} | {Example 6.1 / 6.2 / 6.3} |
| 7 Interaction | {N or UNSCANNED} | {Example 7.1 / 7.2 / 7.3} |

## Handoff Payload

```yaml
schema: viz_critique_report/1
mode: {workbook_scan | image_only}
dashboard_name: "{name}"
workbook_name: "{name_or_null}"
overall_score: {N}
tier: "{tier}"
ethics:
  status: "{No violations | Warning | Critical}"
  cap_applied: {None | 79 | 59}
  raw_pre_cap: {N}
  violations: [{list}]
domains:
  - id: 1
    name: "Audience Adaptation"
    score: {N}
    anchor_matched: "{Example X}"
    signals_evaluated: [{list}]
  - {domain 2 through 7 same shape}
image_only_disclaimers:
  - "Domain 4 (Layout) reduced accuracy without workbook XML context"
  - "Domain 7 (Interaction) reduced accuracy without workbook XML context"
{image_only_disclaimers only when mode is image_only; empty [] otherwise}
routing:
  viz_planner: {true | false}
  worksheet_builder_per_chart: [{list_of_worksheets_or_empty}]
  chart_swap_advisor_per_chart: [{list_of_worksheets_or_empty}]
  dashboard_preflight: {true | false}
  format_drift_scanner: {true | false}
  interaction_validator: {true | false}
```

## Next Steps

{One or two-line concrete pointer based on lowest-scoring domain and applicable handoffs. Never generic inspiration.}

## Reference

- Evaluation framework: `rubric_evaluation_framework.md` in the skill directory.
- Scoring tiers and tone: `scoring_tiers_and_tone.md`.
- Ethics gatekeeper: `ethics_privacy_gatekeeper.md`.
- Handoff schema: `handoff_schema.md`.
```

## Section Rendering Rules (Longform, Tier B)

**Header block.** Always renders skill version, timestamp, mode, workbook + dashboard, aspect ratio, overall score, and tier. Image Only mode adds the disclaimer line immediately after.

**Ethics section.** Always rendered. When no violations fired, render:

```
## Ethics and Privacy

**Status:** No violations
**Cap applied:** None
**Raw pre-cap score:** {N}/100
```

Never omit the section; empty is a signal.

**Executive Summary.** 1-2 paragraphs. Plain-language. Tone matches the tier per `scoring_tiers_and_tone.md`.

**Per-Domain sections.** All 7 rendered, even when UNSCANNED. Anchor matched, signals evaluated, and rationale for each.

**Improvement Plan.** Grouped by domain, ordered by impact. No cap; every recommendation gets What / Why / How / Impact / Handoff.

**Calibration Anchor Cross-Reference.** Always rendered as a small table.

**Handoff Payload.** Always rendered as a YAML block at the bottom.

**Next Steps.** Concrete pointer per the tier. Never generic advice.

## Overflow Handling

- **Long-form dashboards (aspect ratio 2:1+).** Domains 4 and 7 render as UNSCANNED with reason and re-run recommendation.
- **Multiple ethics violations.** All rendered in the Ethics section, ordered by severity (Critical → Warning → Info).
- **Improvement plan length.** No inline cap; every recommendation renders. If length exceeds 30 recommendations, group secondary items in a `<details>` block at the end of the plan.

## File-Write Confirmation Flow

1. Tier A chat summary renders with the file-save offer line.
2. If the user opts in ("yes," "save it," "put it in Downloads," ".md," ".txt"):
   - Confirm format choice if not already stated (default `.md`).
   - Resolve the Downloads folder OS-agnostically. Windows: `%USERPROFILE%\Downloads\`. macOS: `$HOME/Downloads/`. Never hard-code a tilde path.
   - Confirm the exact save path before writing.
   - Write the file per Tier B shape.
   - Report the path back in chat.
3. If the user declines, no file is written. Handoff schema still emits to session context regardless. Chat then offers the top 3 recommendations with one-line rationale each and asks: "Want the full 7-domain breakdown in chat? [yes/no]".
4. If the user says yes to the in-chat breakdown, render the per-domain rationale (still without the improvement plan; improvement plan lives in the file only).

**Never write a file silently.** HC#13 non-override.

**Fresh-filename discipline.** If the target path already exists, append `_v2` (then `_v3`, etc.) before the extension.

**Naming convention.** The `_viz-critique` suffix is reserved to this skill; never reuse it for other skills' exports.

## Improvement Plan Discipline

The improvement plan lives in the saved file only. Never in the Tier A chat summary. If the user declines the file, chat renders top 3 recommendations with one-line rationale each, and offers the per-domain breakdown as a final escape hatch. The full improvement plan (Desktop-fix steps, impact estimates, handoff routing) is only ever written to the file.

## Refuse to Fabricate

Never render a domain score without citing signals and matched anchor. Never render an ethics banner without a specific triggered violation. Never suppress a triggered ethics violation to raise the score. Never invent a recommendation. Never render the improvement plan in chat.
