---
name: dashboard-caption-audit
description: "Use when the user says 'Check my titles', 'audit captions', 'are my dashboards labeled?', 'missing titles'. Finds missing or default titles and captions across dashboards, worksheets, text objects, and phone or tablet layouts, with fix steps. Read-only."
---


# Dashboard Caption Audit

## When to use (full trigger detail)

Audit a Tableau workbook for missing or default titles and captions across dashboards, worksheets, dashboard text objects, and phone/tablet device-layout variants. Runs a locked completeness catalog (dashboard-title-missing, dashboard-caption-missing, worksheet-title-missing, worksheet-caption-missing, text-object-empty, default-name, device-layout-inheritance-duplicate, placeholder-title-text) per dashboard, groups findings by severity, and produces a Desktop-fix report. Read-only. Title and caption completeness only, no tooltip content, no position sanity, no spellcheck (defers to desktop-spellcheck). Trigger with audit captions, check my titles, are my dashboards labeled, caption audit, missing titles, dashboard-caption-audit. Do NOT trigger on. text-copy correctness or spelling (defer to desktop-spellcheck), tooltip content quality (defer to viz-critique-pro-studio), localization or hard-coded strings (defer to i18n-scanner), format-string drift on numbers/dates/fonts (defer to format-drift-scanner), chart-type-only advisory (defer to chart-swap-advisor), pre-publish assembly hygiene (defer to dashboard-preflight), calc issues (defer to calc-orchestrator).

## Purpose

Scan a Tableau workbook for missing or default titles and captions across every dashboard, every worksheet on those dashboards, and every dashboard text object. Read-only. Every finding cites a locked completeness rule and produces a Desktop-fix instruction, never a mutation.

Positioned parallel to desktop-spellcheck and format-drift-scanner in the pipeline. Spellcheck owns text-copy correctness. Format-drift-scanner owns cross-worksheet format-string consistency. Dashboard-caption-audit owns title and caption completeness (are the labels there at all, and did the author actually set them).

**Scope note.** Covers caption and title completeness only. Tooltip content is a viz-critique-pro-studio concern, and position sanity needs pixel-level rendering, which the agent can't do.

## Trigger Conditions

- audit captions
- check my titles
- are my dashboards labeled
- caption audit
- missing titles
- dashboard-caption-audit
- title completeness
- check labels on my workbook

## Do NOT Trigger On

- Text-copy correctness or spelling (defer to `desktop-spellcheck`).
- Tooltip content quality (defer to `viz-critique-pro-studio`).
- Localization fragility or hard-coded strings (defer to `i18n-scanner`).
- Format-string drift on numbers, dates, or fonts (defer to `format-drift-scanner`).
- Chart-type advisory (defer to `chart-swap-advisor`).
- Pre-publish assembly hygiene (defer to `dashboard-preflight`).
- Calc issues (defer to `calc-orchestrator`).
- Applying caption changes (all fixes are Desktop-manual per HC#1).
- Whole-workbook pre-publish hygiene (defer to `publish-readiness`).
- Change-over-time (defer to `workbook-auditor`).

## Scope Boundaries

- **IN.** One workbook per run. Every dashboard, worksheet on those dashboards, and dashboard text object audited for title + caption completeness. Default-name detection (`Dashboard 1`, `Sheet 1`, and locale variants). Locked severity tiers per completeness catalog. Read-only. Per-dashboard TL;DR banner in chat, full findings in opt-in Downloads file. Handoff schema `caption_audit_report/1`.
- **OUT.** Any workbook mutation. Applying caption or title changes. Tooltip content evaluation. Spellcheck of caption text. Format-drift on caption fonts. Position sanity or overlap detection.

**Text objects on the dashboard canvas.** In scope for completeness (empty text object with no content fires `text-object-empty`). Text object content quality is out of scope (defers to viz-critique-pro-studio for design and desktop-spellcheck for spelling).

**Cross-dashboard workbooks.** Each dashboard audited independently. Default naming on one dashboard does not affect scoring of another. TL;DR renders one line per dashboard.

## The 8-Rule Completeness Catalog

Full detail lives in `skill-expertise/completeness_catalog.md`. Summary:

| Rule ID | Trigger | Severity |
|---|---|---|
| DC-TITLE-01 Dashboard-Title-Missing | Dashboard has no title text OR title is hidden AND caption also missing | Warning |
| DC-CAPTION-02 Dashboard-Caption-Missing | Dashboard has no caption text | Info |
| DC-WS-TITLE-03 Worksheet-Title-Missing | Worksheet on a dashboard has no title text OR title is hidden | Warning |
| DC-WS-CAPTION-04 Worksheet-Caption-Missing | Worksheet on a dashboard has no caption text | Info |
| DC-TEXT-EMPTY-05 Text-Object-Empty | Dashboard text object has no content | Warning |
| DC-DEFAULT-NAME-06 Default-Name | Dashboard or worksheet name matches auto-generated pattern (`Dashboard \d+`, `Sheet \d+`, and locale variants) | Warning |
| DC-DEVICE-07 Device-Layout-Inheritance-Duplicate | Desktop parent has missing title or caption AND phone/tablet variant inherits (no device-specific override) | Warning |
| DC-TITLE-08 Placeholder-Title-Text | Dashboard or worksheet title text is Tableaus unedited literal boilerplate (e.g. `<Sheet Name>`, `<Dashboard Name>`) | Warning |

**Warning severity** for missing titles, empty text objects, default names, and device-layout inheritance defects because these reach the end user on Desktop or on phone/tablet. **Info severity** for missing captions because captions are optional in most published workbooks and their absence is a design choice more often than a defect.

Default names are Warning-tier because they signal the author never set an intentional label; the audience sees `Dashboard 1` and reads it as unfinished work.

Device-layout inheritance duplicates are reported **once on the Desktop parent**, with affected variants (phone, tablet) listed in the same finding record. One Desktop-fix path resolves all inherited variants.

## Workflow Phases

- **Phase 0 Scope.** Confirm workbook is open via `get-workbook-inventory`. If not open, ask user to open it. Enumerate every dashboard via `list-dashboards`; enumerate every worksheet on each dashboard via `get-dashboard-xml`. Ask which dashboard(s) to audit only if the workbook has 10+ dashboards (default: all).
- **Phase 1 Inventory.** For each dashboard: read `get-dashboard-xml` for title/caption XML and text-object elements. For each worksheet on the dashboard: read `get-worksheet-xml` for title/caption XML. Batch by dashboard per HC#5 (10 sheets per parallel `get-worksheet-xml` call, sequence remaining).
- **Phase 2 Detect Completeness.** Apply the 8-rule catalog to every dashboard, worksheet, and text object. Every failing element gets its own finding record (do not collapse multiple worksheet-level failures under one rule into a single finding) — a dashboard with 3 worksheets missing titles reports 3 DC-WS-TITLE-03 findings, one per worksheet, matching the per-element counts shown in the Tier A/B templates. Do not fabricate findings; every rule fire cites specific XML evidence.
- **Phase 3 Assemble Report.** Group findings by dashboard (primary) then by severity (Warning → Info). Every finding includes a Desktop-fix instruction. Report shape follows `skill-expertise/report_template.md`.
- **Phase 4 Deliver Tier A.** Compact chat summary: one-line TL;DR per dashboard, then top 3 recommendations across the workbook, then file-save offer. If the workbook has more than 8 dashboards, render TL;DR lines for the first 8 in enumeration order and collapse the remainder into a single `+ {N} more (see full report)` line; Tier B always renders every dashboard regardless of this collapse. Top-3 selection is locked (HC#14): sort all findings by severity (Warning before Info), then by dashboard enumeration order (as returned by `list-dashboards`), then by rule ID ascending (`DC-TITLE-01` before `DC-DEFAULT-NAME-06`, etc.); take the first 3. Ties never depend on judgment.
- **Phase 5 Deliver Tier B (opt-in).** Full findings written to Downloads as `.md` (default) or `.txt` only after user confirms path.

## Hard Constraints

**HC#1 Read-only always.** Never invoke `bind-template`, `build-and-apply-worksheet`, `author-calc`, or any mutating tool. Every recommendation is Desktop-manual.

**HC#2 One workbook per run.** Multi-workbook audits refused. Users invoke separately.

**HC#3 Bulk-action refusal.** Fix all missing captions refused; skill is read-only per HC#1.

**HC#4 Locked catalog.** Every finding cites one of the 8 rule IDs. No fabricated rules. No severity reassignment mid-run.

**HC#5 Batching cap.** `get-worksheet-xml` batches capped at 10 sheets per parallel call regardless of workbook size; sequence remaining sheets in additional batches.

**HC#6 Never auto-invoke another skill.** Adjacent-skill routing (desktop-spellcheck for spelling, viz-critique-pro-studio for tooltip content) is an opt-in handoff. Skill emits the payload; user invokes downstream.

**HC#7 Sentinel discipline.** Use `null`, `[]`, `not_present` for missing XML fields. Never blank fields in handoff schema.

**HC#8 Refuse to fabricate.** V-gate refuses fabricated findings or missing rule citations.

**HC#9 Partial-info handling.** If `get-dashboard-xml` returns partial results (per a known reliability gap), flag UNSCANNED for that dashboard with reason; do not proceed with incomplete evidence.

**HC#10 Adjacent-skill routing.** Text-copy quality → `desktop-spellcheck`. Tooltip content → `viz-critique-pro-studio`. Localization → `i18n-scanner`. Format drift on caption fonts → `format-drift-scanner`.

**HC#11 Default-name treatment locked.** Auto-generated names (`Dashboard \d+`, `Sheet \d+`, and locale variants) fire DC-DEFAULT-NAME-06 as Warning. Never Info. Never demoted under user pressure.

**HC#12 Never write the longform file silently.** File-save requires explicit user opt-in with path confirmation. Improvement plan lives in the file only; chat renders TL;DR + top 3 only.

**HC#13 Guide the user actively.** Silence during evaluation is a defect. Announce per-dashboard progress on 5+ dashboard runs.

**HC#14 Top-3 selection locked.** Sort by severity (Warning → Info), then dashboard enumeration order (as returned by `list-dashboards`), then rule ID ascending. Never pick top 3 by subjective importance.

**HC#15 Per-dashboard TL;DR ordering locked.** Per-dashboard TL;DR lines render in `list-dashboards` enumeration order. Never sorted by finding count, severity mix, or judgment. Fully-labeled dashboards render inline in their enumeration slot as `{Dashboard}: fully labeled`.

## Two-Tier Delivery

### Tier A: Compact chat summary (always renders)

Target under 25 lines. One-line TL;DR per dashboard, then workbook-wide top 3, then save-file offer.

```
**Caption Audit: {workbook_name}**
Dashboards audited: {N} · Total findings: {N Warnings, N Info}

Per-dashboard TL;DR:
- {Dashboard A}: {n} missing captions, {n} missing titles
- {Dashboard B}: {n} missing captions, {n} missing titles

Top 3 recommendations:
1. {one-line teaser, no rationale}
2. {one-line teaser, no rationale}
3. {one-line teaser, no rationale}

Save the full findings and Desktop-fix instructions to Downloads? (.md default, .txt option, or skip)
```

### Tier B: Full findings file (opt-in file)

Written to Downloads only when user confirms. File format .md (default) or .txt. Contents per `skill-expertise/report_template.md`:

- Header (skill version, timestamp, workbook name).
- Per-dashboard sections with every finding, rule ID cited, XML evidence quoted, and Desktop-fix instruction.
- Handoff schema payload (`caption_audit_report/1`).

File-save discipline: user opts in, format confirmed, path confirmed (Windows: `%USERPROFILE%\Downloads\`; macOS: `$HOME/Downloads/`), fresh-filename discipline on collision.

## Validation Gate (4-Check Read-Only)

**V1 Rule Coverage.** Every rule ID (DC-TITLE-01 through DC-TITLE-08) evaluated on every applicable element. Empty findings list is a legitimate outcome (workbook fully labeled).

**V2 Evidence Citation.** Every finding cites specific XML evidence from `get-dashboard-xml` or `get-worksheet-xml`. No fabricated findings.

**V3 Handoff Completeness.** Every field in `caption_audit_report/1` populated per `skill-expertise/handoff_schema.md`.

**V4 Ordering Determinism.** Top-3 recommendations rendered in the HC#14 sort order (severity → dashboard enum order → rule ID ascending). Per-dashboard TL;DR rendered in HC#15 order (`list-dashboards` enumeration). Default-name findings never demoted below Warning per HC#11. Verify the on-wire report matches these ordering rules before delivery.

V-gate failure blocks delivery per HC#8.

## Tool Sequence

- **Phase 0.** `get-workbook-inventory` (never twice per run). `list-dashboards` for enumeration.
- **Phase 1.** `get-dashboard-xml` per dashboard (batched). `get-worksheet-xml` per worksheet on each dashboard (batched, 10 per parallel call).
- **Phase 2-3.** In-memory rule evaluation and report assembly. No tool calls.
- **Phase 4.** Chat delivery. No tool calls.
- **Phase 5.** File-write to Downloads only on opt-in per HC#12.

## Handoff Contract

Emits `caption_audit_report/1` per `skill-expertise/handoff_schema.md`. Consumed by:

- **dashboard-preflight.** Caption findings enrich assembly hygiene.
- **desktop-spellcheck.** After captions are added, spellcheck the new text.
- **viz-critique-pro-studio.** Domain 4 layout scoring cross-references caption presence.
- **workbook-auditor.** Caption findings deltas across runs.

## Known Limitations

- **`get-worksheet-xml` dashboard-bound-sheet reliability gap**. Some worksheets on dashboards return partial XML. HC#9 flags UNSCANNED rather than fabricating.
- **Locale variants.** Default-name regex covers English (`Dashboard \d+`, `Sheet \d+`), French (`Tableau de bord \d+`, `Feuille \d+`), Spanish (`Panel \d+`, `Hoja \d+`), and German (`Dashboard \d+`, `Blatt \d+`). Other locales require regex extension.
- Cannot evaluate caption content quality (spelling, tone, clarity) — routes to desktop-spellcheck and viz-critique-pro-studio.
- Cannot detect intentionally-hidden titles (right-click > Hide Title). XML shows `<title style=hidden>` regardless of intent; skill treats hidden title as missing per DC-TITLE-01 rule.

## Error Handling

| Failure | Response |
|---|---|
| Workbook not open | Ask: Please open the workbook youd like audited. |
| `get-workbook-inventory` fails | Retry once. If still failing, exit gracefully. |
| `get-dashboard-xml` returns partial | Flag UNSCANNED for that dashboard per HC#9. |
| `get-worksheet-xml` returns garbled | Retry once per sheet. If still failing, mark that sheet UNSCANNED. |
| Workbook has 0 dashboards | Exit with No dashboards found; nothing to audit. |
| Workbook has 10+ dashboards | Ask user to scope; default to all. |
| User asks to fix captions | Refuse per HC#1. Route to Desktop-manual instructions in the report. |
| User asks to spellcheck captions | Refuse per HC#10. Route to `desktop-spellcheck` with handoff payload. |
| User asks to audit multiple workbooks | Refuse per HC#2. Ask which workbook. |
| User asks to skip V-gate | Refuse per HC#8. |
| User asks to save file without path confirmation | Refuse per HC#12. Confirm path first. |
| User asks to demote default-name to Info | Refuse per HC#11. Warning stands. |

## Examples

**Example 1: Clean workbook.**

User: audit captions

Skill runs Phases 0-3 silently, then delivers Tier A:

```
**Caption Audit: Sales Overview**
Dashboards audited: 3 · Total findings: 0 Warnings, 0 Info

Per-dashboard TL;DR:
- Sales Overview: 0 missing captions, 0 missing titles
- Regional Detail: 0 missing captions, 0 missing titles
- Product Mix: 0 missing captions, 0 missing titles

No findings. Workbook is fully labeled.

Save the empty report to Downloads for the record? (.md default, .txt option, or skip)
```

**Example 2: Mixed findings.**

User: check my titles

Skill delivers Tier A:

```
**Caption Audit: Q3 Executive Review**
Dashboards audited: 4 · Total findings: 6 Warnings, 3 Info

Per-dashboard TL;DR:
- Q3 Summary: 1 missing title (worksheet Regional Rollup), 1 empty text object
- Product Detail: 2 missing captions, 1 default name (Dashboard 2)
- Customer Segments: 0 missing captions, 0 missing titles
- Financial Rollup: 3 missing captions, 1 missing title

Top 3 recommendations:
1. Rename Dashboard 2 to a descriptive title (right-click > Rename Dashboard).
2. Add title to worksheet Regional Rollup (right-click > Show Title).
3. Fill or delete empty text object on Q3 Summary.

Save the full findings and Desktop-fix instructions to Downloads? (.md default, .txt option, or skip)
```

**Example 3: Refuse fix request.**

User: just fix all the missing captions for me

Skill: This skill is read-only per HC#1; I cant apply caption changes directly. Every recommendation in the report is a Desktop-manual fix path (right-click > Rename, right-click > Show Title, etc.). Want the full report saved to Downloads so you can work through the list?

## Relationship to Other Skills

- **Peer to desktop-spellcheck.** Spellcheck audits text-copy correctness once captions exist; this skill audits whether captions exist at all.
- **Peer to format-drift-scanner.** Format-drift audits font family, font size, and format-string consistency on captions that exist; this skill checks completeness first.
- **Upstream of viz-planner.** Missing-caption Warning findings route to viz-planner for redesign at Rework tier.
- **Adjacent to dashboard-preflight.** Preflight audits assembly hygiene structurally; this skill audits caption completeness. Both are Phase 5 layer.

## MCP Skill Mapping

Desktop-native. No MCP dependency. Uses standard Desktop tools (`get-workbook-inventory`, `list-dashboards`, `get-dashboard-xml`, `get-worksheet-xml`).

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
