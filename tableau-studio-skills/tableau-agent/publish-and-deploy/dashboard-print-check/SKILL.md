---
name: dashboard-print-check
description: "Use when the user says 'Is this dashboard print-ready?', 'print check', 'audit this dashboard for print'. Checks a dashboard's print layout: fixed vs. range size, container overflow, black-and-white color safety, and text legibility, with fix steps. Read-only."
---

# Dashboard Print Check

## When to use (full trigger detail)

Audit a Tableau dashboard for print-layout hygiene against a locked 4-check catalog (fixed-size vs range-size sanity, container overflow at print DPI, color-safe check for black-and-white printing, text-object legibility at print DPI). Read-only. Every finding is a manual Desktop-fix instruction. Export-format compatibility (PDF, PowerPoint, image) is not supported. Container-overflow findings route to dashboard-preflight for deeper container-nesting analysis via handoff. Trigger with audit this dashboard for print, print check, print layout audit, is this dashboard print-ready, dashboard-print-check. Do NOT trigger on. export-format compatibility like PDF or PowerPoint conversion (not supported), interactive-element behavior in print like filter states or tooltip visibility (out of scope), multi-dashboard batch runs, non-print dashboard hygiene (defer to dashboard-preflight), or chart-type appropriateness for print (defer to chart-swap-advisor).

## Purpose

Audit one Tableau dashboard for print-layout hygiene against a locked 4-check catalog. Read-only. Every finding is a manual Desktop-fix instruction; the skill never mutates. Export-format compatibility (PDF, PowerPoint, image conversion) is out of scope. Further rescoped on 2026-09-16, twice: first dropping Orientation Fit and Margin Sanity (dashboard size is explicit fixed pixel width x height, not portrait/landscape; no document-style margin setting exists), then dropping Page-Break Placement and Header/Footer Presence after empirical testing across every staged fixture showed no dashboard ever carries print-config XML for either — both checks always resolved to the same unresolved sentinel with no way to fire or clear.

## Trigger Conditions

- "audit this dashboard for print"
- "print check"
- "print layout audit"
- "is this dashboard print-ready"
- "dashboard-print-check"
- "check the print layout"
- "print-config audit"

## Do NOT Trigger On

- Export-format compatibility (PDF, PowerPoint, image conversion, filter-state preservation on export) → not supported.
- Interactive-element behavior in print (filter state, tooltip visibility, action responsiveness) → out of scope.
- Multi-dashboard batch runs → out of scope; one dashboard per run.
- Non-print dashboard assembly hygiene (zone alignment, filter-action wiring, parameter linkage) → defer to `dashboard-preflight`.
- Chart-type appropriateness for print → defer to `chart-swap-advisor`.
- Container-nesting soundness beyond print-DPI overflow → defer to `dashboard-preflight` via routing handoff.
- Deep dashboard design review or scoring → defer to `viz-critique-pro-studio`.

## Scope Boundaries

- **IN.** One dashboard per run. Read-only. 4-check print catalog (see below). Sentinel discipline for empty-dashboard cases per HC#9. Handoff schema `dashboard_print_report/1`. Routing offered to `dashboard-preflight` for container-nesting deep-dive when container overflow fires.
- **OUT.** Any dashboard mutation. Export-format compatibility. Interactive-element behavior. Multi-dashboard runs. Deep container-nesting analysis beyond print-DPI overflow. Rendering the print preview (pixel-visibility platform gap).

**Rescope note.** Print-export compatibility is not supported because export rendering paths are not accessible via current agent tools; auditing export compatibility without rendering visibility would require fabricating around a gap, which HC#8 forbids.

## The 4-Check Print Catalog (Locked)

Every finding cites a check ID. Multi-check findings are tagged with all applicable IDs; severity tier set by highest match.

| # | Check | ID | Severity | Detection |
|---|---|---|---|---|
| 1 | Fixed-size vs range-size sanity for print, plus print-aspect-ratio layout risk | DPC-SIZE-02 | Warning | Two-part check on the dashboards `<size>` element. (1) Sizing mode: fires if the dashboard uses `range` or `automatic` size mode — print rendering is unstable across page sizes without fixed pixel dimensions. (2) Aspect-ratio layout risk: even when fixed, fires if width:height (or height:width) is 2:1 or more — a fixed-size dashboard thats extremely wide or extremely tall will need heavy scaling or cropping to fit a standard print page, regardless of orientation, since Tableau dashboards have no separate portrait/landscape declaration to reconcile against. Evidence cites which sub-check fired (sizing-mode, aspect-ratio, or both). |
| 2 | Container overflow at print DPI | DPC-OVERFLOW-04 | Warning | Zone boundaries at print DPI (typically 96 dpi to 300 dpi depending on print config) exceed page-safe margins. Routes to `dashboard-preflight` via `routing.dashboard_preflight: true` when this fires for deeper container-nesting analysis. |
| 3 | Color-safe check for black-and-white printing | DPC-COLORSAFE-05 | Info | Per-worksheet numbered checklist. (1) Enumerate worksheets on dashboard via `get-dashboard-xml`. (2) Read shelf composition for each via `get-worksheet-xml`. (3) Check if `Color` shelf has any pill placement. (4) Check if `Shape`, `Size`, and `Label` shelves are all empty (no redundant encoding). (5) If both conditions hold, worksheet fires for this dashboard. (6) Dashboard fires if any worksheet triggers steps 3-5. See `skill-expertise/check_catalog.md` for evidence pattern and worked example. |
| 4 | Text-object legibility at print DPI | DPC-TEXTLEGIBLE-08 | Warning | Dashboard text object or worksheet title font size falls below the print-legibility threshold (typically 8pt at 300 dpi). Prints too small to read. |

**Retired checks.** DPC-ORIENTATION-03 (Orientation Fit), DPC-MARGINS-07 (Margin Sanity), DPC-PAGEBREAK-01 (Page-Break Placement), and DPC-HEADFOOT-06 (Header/Footer Presence) are removed from the catalog. Margins, Page-Break, and Header/Footer depended on print-config XML that, across every staged fixture tested, was never present on any dashboard — all three always resolved to an unresolved sentinel with no way to ever fire or clear, making them dead weight rather than a real audit. Orientation Fits underlying concern (a dashboard shape that wont print well) is real but was checking a property — portrait/landscape declaration — that doesnt exist on a Tableau dashboard; that concern is folded into DPC-SIZE-02s aspect-ratio sub-check above instead of being a standalone check. Do not report findings under these IDs.

**Multi-check tagging.** A dashboard can fire multiple checks simultaneously (common: DPC-SIZE-02 + DPC-OVERFLOW-04 both fire when a range-sized dashboard also has content overflowing the print-safe area). Skill emits all triggered check IDs in `checks_triggered[]`; severity tier set by highest match. Deterministic sort key per HC#10: severity tier → check ID ascending.

## Workflow Phases

- **Phase 0 Scope.** Confirm workbook is open via `get-workbook-inventory`. Confirm target dashboard name. If not stated, ask which dashboard. Ensure only one dashboard per run per HC#2.
- **Phase 1 Dashboard-XML Extraction.** Read the dashboards XML via `get-dashboard-xml` (size mode, zone bounds, title/text font sizes). No print-config XML is read — none of the surviving checks depend on it (see Retired checks note in the catalog).
- **Phase 2 Check Evaluation (numbered checklist).**
  1. For each of the 4 checks in the catalog, apply the detection criteria.
  2. If a checks signal source (dashboard XML or worksheet XML) is unreadable for this dashboard, emit `"unresolved"` sentinel for that check per HC#5.
  3. If detection succeeds and the check fires, populate `checks_triggered[]` with the check ID and evidence citation.
  4. If detection succeeds and the check clears, mark `checks_cleared[]` with the check ID (used for handoff completeness).
  5. For DPC-COLORSAFE-05, batch the per-worksheet `get-worksheet-xml` reads across all worksheets on the dashboard rather than issuing them one at a time; this matters most on wide dashboards with many zones (see HC#15).
- **Phase 3 Severity Tiering.** For multi-check findings, tier by highest severity. Sort output by tier → check ID per HC#10.
- **Phase 4 Routing Signal.** If DPC-OVERFLOW-04 fires, populate `routing_offered.dashboard_preflight: true` in the handoff. Skill emits the routing offer to the user; never auto-invokes `dashboard-preflight`.
- **Phase 5 Validate.** Run the 4-check V-gate: check coverage, sentinel discipline, ordering determinism, handoff completeness.
- **Phase 6 Deliver.** Two-tier: compact Tier A chat summary with counts and top 3 Warning-tier findings; opt-in Tier B file save requires user path confirmation per HC#12.

## Hard Constraints

**HC#1 Read-only always.** Never mutates the dashboard. Never modifies print config. Every finding is a manual Desktop-fix instruction.

**HC#2 One dashboard per run.** Multi-dashboard runs refused; run once per dashboard.

**HC#3 4-check catalog locked.** No check omitted, no fabricated check added. Detection follows the criteria in the catalog above.

**HC#4 Every finding is a manual Desktop-fix instruction.** User applies fixes; skill never mutates.

**HC#5 Sentinel discipline for unreadable signal.** When a checks dashboard-XML or worksheet-XML signal source is unreadable for this dashboard, emit `"unresolved"` per-rule rather than guessing. Never fabricate assumptions about default print behavior. (Retired 2026-09-16: the former `"print-config-unset"` reason no longer applies — after dropping the print-config-dependent checks, no surviving check reads print-config XML at all.)

**HC#6 Diff-mode transparency** (portfolio-wide HC#13). Repeat invocations against unchanged dashboard state emit `diff_mode: reused_verbatim` in Tier A output. Fresh-scan / reused-verbatim / targeted-rescan enum.

**HC#7 Ordering determinism** (portfolio-wide HC#14). Same input produces byte-identical top-3 and full check list across runs.

**HC#8 Refuse to fabricate.** No inferred print-config values. No guessed rendering behavior at print DPI (pixel-visibility gap). No invented findings.

**HC#9 Sentinel discipline for empty-dashboard.** If a dashboard has zero zones or is a blank canvas, exit cleanly with "no print-relevant content found" per HC#5.

**HC#10 Never silent file write.** Tier B full report save requires user path confirmation.

**HC#11 Container overflow routes to dashboard-preflight.** Skill does not perform deep container-nesting analysis inline. When DPC-OVERFLOW-04 fires, emit `routing.dashboard_preflight: true` and let the user opt in to the deeper analysis. Preserves scope separation between print-specific concerns (this skill) and dashboard assembly hygiene (dashboard-preflight).

**HC#12 Pixel-visibility gap acknowledged.** DPC-OVERFLOW-04 and DPC-TEXTLEGIBLE-08 rely on XML-derived signals (zone boundaries, font size declarations), not rendered print preview. Findings tier as Info rather than Warning when XML doesnt cover the visual concern completely. User is told the finding is XML-signal-based, not pixel-verified.

**HC#13 Handoff staleness detection** (portfolio-wide HC#15). If skill consumes upstream handoffs (from `dashboard-preflight` for prior container analysis), verify hash against current dashboard state; mismatch forces local re-derivation.

**HC#14 Handoff-or-local labeled.** Every check emits `signal_source: "dashboard_xml" | "worksheet_xml" | "unresolved"` in the handoff so downstream consumers know the evidence origin.

**HC#15 Wide-dashboard scale handling.** For dashboards with 100 or more zones or 50 or more text objects, skill emits a wide-dashboard-notice in Tier A output ("this dashboard has N zones and M text objects; Tier A will truncate findings to top 5 per severity tier") and adjusts rendering: Tier A shows top 5 Warning-tier findings + top 5 Info-tier findings + a totals line. Full findings list still lands in the Tier B file save. Per-check evaluation still runs on every zone and text object; only the presentation layer truncates. Zone threshold raised from 10 to 50 to 100 on 2026-09-16: Tableaus dashboard XML nests layout/legend/filter/title zones heavily, so raw zone counts (as reported by `get-dashboard-xml`) run high even on small, simple dashboards — a 64-zone, 4-worksheet, single-container dashboard still isnt "wide" in any user-facing sense, so the threshold moved again to 100.

**HC#16 Reference-file grounding.** DPC-TEXTLEGIBLE-08 threshold (8pt) is documented with empirical defense in `skill-expertise/check_catalog.md`. DPC-COLORSAFE-05 detection uses the 6-step numbered checklist in the catalog reference. Skill cites the reference file when a user challenges a threshold; never argues from taste.

## Validation Gate (4-Check)

- **V1 Check Coverage.** All 4 checks evaluated. Every check has either a `checks_triggered` or `checks_cleared` entry (or a sentinel for unresolved cases).
- **V2 Sentinel Discipline.** Any check whose signal source is unreadable emits `"unresolved"` sentinel per HC#5. No fabricated defaults.
- **V3 Ordering Determinism.** Check list sort key deterministic per HC#7.
- **V4 Handoff Completeness.** `dashboard_print_report/1` schema fully populated. `routing.dashboard_preflight` set correctly when DPC-OVERFLOW-04 fires.

## Two-Tier Delivery

**Tier A (chat).** Compact summary: dashboard name, total checks evaluated, findings by severity tier, top 3 Warning-tier findings with Desktop-fix instructions, sentinel-per-rule count if any checks signal was unresolved.

Template:

```
**Dashboard Print Check: {dashboard_name}**
Checks evaluated: {N_evaluated} of 4 ({N_unresolved} unresolved)
Findings: {N_warning} Warning, {N_info} Info, {N_sentinel} sentinel (unresolved)
Diff mode: {fresh_scan | reused_verbatim | targeted_rescan}

Top 3 Warning-tier findings:
1. {check_id}: {evidence}. Desktop fix: {manual_fix_instruction}.
2. ...
3. ...

Routing offered: {dashboard-preflight for container overflow if DPC-OVERFLOW-04 fires}
Save full print report to file?
```

**Tier B (opt-in file save).** Full report `.md` written to user-confirmed path per HC#10. Includes per-check detail, evidence citation from XML, Desktop-fix instructions, handoff YAML block.

## Handoff Schema

Emits `dashboard_print_report/1`:

```yaml
dashboard_print_report:
  version: 1
  run_timestamp: <ISO 8601>
  workbook:
    name: <string>
    hash: <sha256>
  dashboard:
    name: <string>
    fingerprint: <sha256>
  diff_mode: <"fresh_scan" | "reused_verbatim" | "targeted_rescan">
  checks_triggered:
    - id: <check_id>
      severity: <"Warning" | "Info">
      evidence: <string>
      signal_source: <"dashboard_xml" | "worksheet_xml" | "unresolved">
      desktop_fix: <string>
  checks_cleared: [<check_id>]
  sentinels:
    - id: <check_id>
      reason: <"no-print-relevant-content" | "unresolved-other">
  totals:
    warning_count: <int>
    info_count: <int>
    sentinel_count: <int>
  routing_offered:
    dashboard_preflight: <boolean>
    viz_critique_pro_desktop: <boolean>
    chart_swap_advisor: <boolean>
  v_gate:
    v1_check_coverage: <pass|fail>
    v2_sentinel_discipline: <pass|fail>
    v3_ordering_determinism: <pass|fail>
    v4_handoff_completeness: <pass|fail>
```

Downstream consumers:

- **dashboard-preflight** (routing target when DPC-OVERFLOW-04 fires).
- **publish-readiness** (post-print-check readiness sweep before governance publish).
- **workbook-auditor** (tracks print-config deltas across runs).

## Common Mistakes (Anti-Patterns)

- **Fabricating a checks signal.** When a checks dashboard-XML or worksheet-XML signal is unreadable, emit `"unresolved"` sentinel per HC#5. Never assume default print settings or dashboard properties.
- **Rendering the print preview.** Pixel-visibility platform gap blocks this. DPC-OVERFLOW-04 and DPC-TEXTLEGIBLE-08 are XML-signal-based, not pixel-verified. Tier findings as Info where XML doesnt cover the visual concern completely.
- **Auto-invoking dashboard-preflight.** When DPC-OVERFLOW-04 fires, offer the routing; dont call `dashboard-preflight` on the users behalf. User opts in.
- **Silently mutating print config.** HC#1 makes this skill read-only always. Every fix is a manual Desktop instruction.
- **Deep container-nesting analysis inline.** HC#11 routes to `dashboard-preflight` for that.
- **Silent file write on Tier B save.** HC#10 requires user path confirmation.

## Adjacent-Skill Routing

- **Routing target (opt-in per finding):** `dashboard-preflight` for container-overflow deep-dive when DPC-OVERFLOW-04 fires.
- **Downstream opt-in:** publish-readiness (post-print-check sweep), workbook-auditor (print-config delta tracking).
- **Refusal routes:** export-format compatibility → not supported; multi-dashboard runs → not supported; non-print assembly hygiene → `dashboard-preflight`; chart-type appropriateness → `chart-swap-advisor`; deep design review → `viz-critique-pro-studio`.

## Known Limitations

- **Pixel-visibility gap**. DPC-OVERFLOW-04 and DPC-TEXTLEGIBLE-08 detect via XML signals (zone boundaries, font size declarations), not by rendering the print preview. Findings tier as Info where XML doesnt cover the visual concern completely.
- **Dashboard or worksheet XML unreadable on some dashboards** (variant of the `get-dashboard-xml` reliability gap). Sentinel `"unresolved"` per rule per HC#5.
- **Export-format compatibility not supported.** Export rendering paths are not accessible to agent tools.
- **Interactive-element behavior in print not audited.** Filter states, tooltip visibility, action responsiveness all out of scope.
- **DPC-COLORSAFE-05 detection is best-effort.** Detects color-as-sole-encoding via worksheet XML mark shelves. Does not account for accessibility-safe palettes (e.g., ColorBrewer safe schemes) that print acceptably in grayscale despite using color encoding.
- **Orientation and margin checks retired (2026-09-16).** DPC-ORIENTATION-03 and DPC-MARGINS-07 were removed from the catalog because Tableau dashboards have no portrait/landscape or document-margin property to audit against.

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
