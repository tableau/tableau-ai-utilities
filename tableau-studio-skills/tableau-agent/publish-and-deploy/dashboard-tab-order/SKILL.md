---
name: dashboard-tab-order
description: "Use when the user says 'Audit my dashboard tab order', 'check tab flow', 'is my navigation logical?' Checks the order of dashboard tabs against 8 navigation rules (entry point, drill-down grouping, orphan tabs, and more) and gives drag-to-fix steps. Read-only."
---

# Dashboard Tab Order

## When to use (full trigger detail)

Audit a Tableau workbooks dashboard tab order (left-to-right navigation) for logical flow against a locked 8-rule catalog (entry-point clarity, drill-down grouping, exception-flow placement, orphan tabs, name-consistency, tab-count sanity, hidden-tab presence, device-layout inheritance). Read-only. Every finding is a manual Desktop-fix instruction (drag the tab in the strip) plus a structured reorder signal. Entry-point is user-declared at Phase 0. Trigger with audit dashboard tab order, check tab flow, is my navigation logical, dashboard-tab-order, tab strip audit. Do NOT trigger on. renaming tabs, applying reorders directly, dashboard-internal navigation like buttons or jump actions (defer to interaction-validator), tab-count reduction via worksheet removal (defer to worksheet-cleanup), or scoring the overall dashboard design (defer to viz-critique-pro-studio).

## Purpose

Audit a Tableau workbooks dashboard tab order (left-to-right navigation in the tab strip) for logical flow against a locked 8-rule catalog. Read-only. Every finding is a manual Desktop-fix instruction (drag the tab to a specific position in the strip); the skill also emits a structured `reorder_action` signal for each positional fix.

## Trigger Conditions

- "audit dashboard tab order"
- "check tab flow"
- "is my navigation logical"
- "dashboard-tab-order"
- "tab strip audit"
- "check my tab order"
- "audit tab navigation"

## Do NOT Trigger On

- Renaming tabs (rename manually in Desktop).
- Applying tab reorders directly (mutation). This skill gives drag-to-fix steps and does not mutate.
- Dashboard-internal navigation (buttons, jump actions, sheet swaps within a dashboard) → defer to `interaction-validator`.
- Tab-count reduction via worksheet or dashboard removal → defer to `worksheet-cleanup`.
- Scoring overall dashboard design → defer to `viz-critique-pro-studio`.
- Print-layout audit → defer to `dashboard-print-check`.
- Caption or title audit within tabs → defer to `dashboard-caption-audit`.

## Scope Boundaries

- **IN.** One workbook per run. Read-only. 8-rule tab-order catalog. User declares entry-point at Phase 0. Manual Desktop-fix instructions per finding plus handoff schema `tab_order_report/1`. Wide-workbook scale handling per HC#15.
- **OUT.** Any tab or workbook mutation. Renaming tabs. Applying reorders. Dashboard-internal navigation (buttons, jump actions). Tab-count reduction via removal. Multi-workbook batch runs.

## The 8-Rule Tab-Order Catalog (Locked)

Every finding cites a rule ID. Multi-rule findings are tagged with all applicable IDs; severity tier set by highest match. Full detection criteria and worked examples in `skill-expertise/rule_catalog.md`.

| # | Rule | ID | Severity | Detection |
|---|---|---|---|---|
| 1 | Entry-point clarity | DT-ENTRY-01 | Warning | User-declared entry-point tab (Phase 0) is not the leftmost tab in the strip. Fires when workbook has 2+ dashboards. |
| 2 | Drill-down grouping | DT-DRILL-02 | Warning | Tabs the user identifies as drill-down destinations are not adjacent to their parent tabs. Fires when Phase 0 flow-metadata captures parent-child relationships. |
| 3 | Exception-flow placement | DT-EXCEPTION-03 | Info | Tabs the user identifies as exception or alert flows are not positioned after the primary navigation flow. Fires when Phase 0 flow-metadata captures exception designations. |
| 4 | Orphan tabs | DT-ORPHAN-04 | Warning | Dashboard tab exists in the strip but is not referenced in any Phase 0 flow declaration (entry-point, drill-down, exception). |
| 5 | Name-consistency | DT-NAMING-05 | Info | Tab names mix casing conventions (e.g., some Title Case, some lowercase) or mix separators (e.g., some spaces, some hyphens). |
| 6 | Tab-count sanity | DT-TABCOUNT-06 | Warning | Workbook has more than 10 dashboard tabs. Cognitive-load research finds tab strips beyond 10 items degrade navigation performance for stakeholders unfamiliar with the workbook. |
| 7 | Hidden-tab presence | DT-HIDDEN-07 | Info | Workbook contains hidden dashboards. Flagged for governance review; hidden dashboards can indicate draft state, deprecated content, or intentional consumer-hiding for internal use. Info-tier because hidden-tab presence is legitimate in some workflows. |
| 8 | Device-layout inheritance | DT-DEVICE-08 | Warning | Phone or tablet device-layout tab order differs from desktop tab order. Fires when device-layout XML declares an explicit order that doesnt match the desktop tab strip. Excludes auto-generated device layouts (`auto-generated=true`), which Tableau creates by default on every dashboard and dont reflect a deliberate authoring choice. |

**Multi-rule tagging.** A workbook can fire multiple rules simultaneously (common: DT-ENTRY-01 + DT-ORPHAN-04 both fire when the leftmost tab isnt the users declared entry-point and additional tabs arent in the flow-metadata). Skill emits all triggered rule IDs in `rules_triggered[]`; severity tier set by highest match. Deterministic sort key per HC#10: severity tier → rule ID ascending.

**Fallback discipline (HC#5).** When rule detection depends on data thats unavailable or unreliable (e.g., device-layout XML unreadable for DT-DEVICE-08), skill emits `"unable to determine"` sentinel per HC#5. Rule is not treated as either true or false; user sees the sentinel and decides.

## Workflow Phases

- **Phase 0 Scope + Flow Declaration.** Confirm workbook is open via `get-workbook-inventory`. If the call fails, returns no workbook, or the session is disconnected, stop and tell the user to confirm Tableau Studio is open with a workbook loaded — do not proceed to Phase 1 on an empty or failed inventory read. Enumerate dashboards. If workbook has fewer than 2 dashboards, exit cleanly with "tab order not applicable" per HC#7. Otherwise: **ask the user to declare the entry-point tab** and, optionally, drill-down groupings and exception flows. Capture in `flow_metadata`. If user declines to declare (or answers "any of them are fine"), skill proceeds with only the rules that dont require flow metadata (DT-NAMING-05, DT-TABCOUNT-06, DT-HIDDEN-07, DT-DEVICE-08) and emits `flow_metadata_declined: true` in the handoff. DT-ORPHAN-04 also requires flow metadata (per `skill-expertise/rule_catalog.md`, an orphan tab is only meaningful relative to a declared flow) and evaluates as `n/a: flow_metadata_declined` when declined.
- **Phase 1 Tab-Strip Inventory.** Read tab order and hidden-tab flags via `get-workbook-xml`. Read device-layout XML for phone/tablet variants via `get-dashboard-xml`. Discard any `<devicelayout auto-generated=true>` before DT-DEVICE-08 evaluation — Tableau creates these by default on every dashboard, so they are not evidence of a deliberate authoring choice. `get-dashboard-xml` is a confirmed-unreliable read on populated, dashboard-bound sheets (500/`operation-failed`); if it fails or returns partial device-layout data on a non-auto-generated layout, do not retry more than once — emit the DT-DEVICE-08 `"unable to determine"` sentinel per HC#5 rather than treating a failed read as "no device layout declared."
- **Phase 2 Rule Evaluation (numbered checklist).**
  1. For each of the 8 rules in the catalog, apply the detection criteria from `skill-expertise/rule_catalog.md`.
  2. If detection requires flow metadata and the user declined to declare, skip DT-ENTRY-01, DT-DRILL-02, DT-EXCEPTION-03, DT-ORPHAN-04 (mark as `n/a: flow_metadata_declined`).
  3. If detection depends on data thats unavailable (device-layout XML unreadable), emit `"unable to determine"` sentinel for that rule per HC#5.
  4. If detection succeeds and the rule fires, populate `rules_triggered[]` with the rule ID and evidence citation.
  5. If detection succeeds and the rule clears, mark `rules_cleared[]` with the rule ID.
- **Phase 3 Severity Tiering + Recommendations.** For multi-rule findings, tier by highest severity. For each finding, produce a manual Desktop-fix instruction ("drag {tab_name} from position {N} to position {M} in the tab strip") and a structured `reorder_action` signal.
- **Phase 4 Validate.** Run the 4-check V-gate: rule coverage, sentinel discipline, ordering determinism, handoff completeness.
- **Phase 5 Deliver.** Two-tier: compact Tier A chat summary with counts and top 3 Warning-tier findings; opt-in Tier B file save with full findings per HC#12.

## Hard Constraints

**HC#1 Read-only always.** Never mutates the workbook. Never reorders the tab strip. Every finding is a manual Desktop-fix instruction plus a handoff signal.

**HC#2 One workbook per run.** Multi-workbook runs refused; run once per workbook.

**HC#3 8-rule catalog locked.** No rule omitted, no fabricated rule added. Detection follows the criteria in `skill-expertise/rule_catalog.md`.

**HC#4 Every finding is a manual Desktop-fix instruction plus handoff signal.** User applies fixes manually via drag-and-drop in the tab strip.

**HC#5 Sentinel discipline.** Missing data uses `"unable to determine"`. Never fabricate assumptions about tab flow, entry-point, or drill-down relationships without user-declared metadata.

**HC#6 User declares entry-point at Phase 0.** Skill does not auto-detect entry-point via name-pattern matching or leftmost-tab assumption. Phase 0 asks the user. If declined, DT-ENTRY-01 / DT-DRILL-02 / DT-EXCEPTION-03 evaluate as `n/a: flow_metadata_declined`; the other 5 rules still evaluate cleanly.

**HC#7 Single-dashboard workbook sentinel.** If workbook has fewer than 2 dashboards, exit cleanly with "tab order not applicable" message. Zero-dashboard workbooks also exit cleanly.

**HC#8 Refuse to fabricate.** No inferred flow relationships. No guessed entry-points. No invented drill-down patterns.

**HC#9 Diff-mode transparency** (portfolio-wide HC#13). Repeat invocations against unchanged workbook state emit `diff_mode: reused_verbatim` in Tier A. Fresh-scan / reused-verbatim / targeted-rescan enum.

**HC#10 Ordering determinism** (portfolio-wide HC#14). Same input produces byte-identical top-3 and full rule list across runs. Same flow_metadata input produces same rules_triggered ordering.

**HC#11 Handoff-or-declined labeled.** Every rule emits `flow_metadata_source: "user_declared" | "declined" | "n/a"` so downstream consumers know whether flow-metadata was provided.

**HC#12 Never silent file write.** Tier B full report save requires user path confirmation.

**HC#13 Handoff staleness detection** (portfolio-wide HC#15). If skill consumes upstream handoffs (from workbook-auditor for delta tracking), verify hash against current workbook state; mismatch forces local re-derivation.

**HC#14 Reference-file grounding.** All 8 rules cite their detection criteria and worked examples in `skill-expertise/rule_catalog.md`. Skill cites the reference file when a user challenges a finding; never argues from taste.

**HC#15 Wide-workbook scale handling.** For workbooks with 10 or more dashboards or 5 or more device-layout variants, skill emits a wide-workbook-notice in Tier A ("this workbook has N dashboards and M device-layout variants; Tier A will truncate to top 5 per severity tier") and adjusts rendering: Tier A shows top 5 Warning-tier findings + top 5 Info-tier findings + a totals line. Full findings list still lands in the Tier B file save.

**HC#16 Structured reorder signal.** Every finding whose fix is a tab-strip repositioning (DT-ENTRY-01, DT-DRILL-02, DT-EXCEPTION-03, DT-DEVICE-08) emits a `reorder_action` in the handoff schema with source position, target position, and the tab name to reorder. Findings whose fix is not positional (DT-ORPHAN-04, DT-NAMING-05, DT-TABCOUNT-06, DT-HIDDEN-07 — rename, hide/unhide, group, or split fixes) emit `reorder_action: null` and rely on `desktop_fix` alone; this is expected, not a gap.

## Validation Gate (4-Check)

- **V1 Rule Coverage.** All 8 rules evaluated. Every rule has a `rules_triggered`, `rules_cleared`, or sentinel entry.
- **V2 Sentinel Discipline.** Any rule with missing metadata or unreadable data emits appropriate sentinel per HC#5 and HC#6.
- **V3 Ordering Determinism.** Rules_triggered sort key deterministic per HC#10.
- **V4 Handoff Completeness.** `tab_order_report/1` schema fully populated. Every finding includes `desktop_fix` (manual instruction); `reorder_action` is populated for positional findings (DT-ENTRY-01, DT-DRILL-02, DT-EXCEPTION-03, DT-DEVICE-08) and `null` for non-positional findings (DT-ORPHAN-04, DT-NAMING-05, DT-TABCOUNT-06, DT-HIDDEN-07) per HC#16.

## Two-Tier Delivery

**Tier A (chat).** Compact summary: workbook name, dashboard count, entry-point declaration status, findings by severity tier, top 3 Warning-tier findings with Desktop-fix instructions.

Template:

```
**Dashboard Tab Order Audit: {workbook_name}**
Dashboards: {N}
Entry-point declared: {yes/no}
Findings: {N_warning} Warning, {N_info} Info, {N_sentinel} sentinel
Diff mode: {fresh_scan | reused_verbatim | targeted_rescan}

Top 3 Warning-tier findings:
1. {rule_id}: {evidence}. Desktop fix: {manual_fix_instruction}.
2. ...
3. ...

Structured `reorder_action` signals included in the handoff.
Save full tab-order report to file?
```

**Tier B (opt-in file save).** Full report `.md` written to user-confirmed path per HC#12. Includes per-rule detail, evidence citation from XML, Desktop-fix instructions, handoff YAML block with reorder_action per finding.

## Handoff Schema

Emits `tab_order_report/1`:

```yaml
tab_order_report:
  version: 1
  run_timestamp: <ISO 8601>
  workbook:
    name: <string>
    hash: <sha256>
    dashboard_count: <int>
  diff_mode: <"fresh_scan" | "reused_verbatim" | "targeted_rescan">
  flow_metadata:
    entry_point: <tab_name | null>
    drill_down_groups: [{parent: <tab_name>, children: [<tab_name>]}]
    exception_flows: [<tab_name>]
    flow_metadata_source: <"user_declared" | "declined" | "n/a">
  current_tab_order: [<tab_name>]
  hidden_tabs: [<tab_name>]
  device_layouts:
    phone: [<tab_name>] | null
    tablet: [<tab_name>] | null
  rules_triggered:
    - id: <rule_id>
      severity: <"Warning" | "Info">
      evidence: <string>
      desktop_fix: <string>
      reorder_action: <null | {tab_name: <string>, source_position: <int>, target_position: <int>}>
  rules_cleared: [<rule_id>]
  sentinels:
    - id: <rule_id>
      reason: <"flow_metadata_declined" | "device_layout_unreadable" | "unresolved-other">
  totals:
    warning_count: <int>
    info_count: <int>
    sentinel_count: <int>
  routing_offered:
    workbook_tab_manager: <boolean>
    interaction_validator: <boolean>
    dashboard_caption_audit: <boolean>
  v_gate:
    v1_rule_coverage: <pass|fail>
    v2_sentinel_discipline: <pass|fail>
    v3_ordering_determinism: <pass|fail>
    v4_handoff_completeness: <pass|fail>
```

Downstream consumers:

- **dashboard-caption-audit** for cross-check on tab naming consistency.
- **publish-readiness** for pre-publish tab-order check.
- **workbook-auditor** for tab-order delta tracking across runs.

## Common Mistakes (Anti-Patterns)

- **Auto-detecting entry-point via name patterns.** HC#6 requires user declaration. Never assume "Overview" or "Home" or leftmost-tab is the entry-point without user input.
- **Fabricating drill-down relationships.** If the user declines to declare flow-metadata, DT-DRILL-02 and DT-EXCEPTION-03 evaluate as `n/a`. Never invent parent-child relationships.
- **Mutating the tab strip.** HC#1 makes this skill read-only always. Every fix is a manual Desktop instruction plus a handoff signal.
- **Extending scope to dashboard-internal navigation.** HC#3 locks the catalog to tab-strip-level rules. Buttons, jump actions, and sheet swaps route to `interaction-validator`.
- **Silent file write on Tier B save.** HC#12 requires user path confirmation.

## Adjacent-Skill Routing

- **Downstream opt-in:** `dashboard-caption-audit` for cross-check on tab naming consistency, `publish-readiness` for pre-publish tab-order sweep, `workbook-auditor` for delta tracking.
- **Refusal routes:** tab renaming → manual rename in Desktop; dashboard-internal navigation → `interaction-validator`; tab-count reduction via removal → `worksheet-cleanup`; overall design review → `viz-critique-pro-studio`.

## Known Limitations

- **Entry-point detection is user-declared, not auto-detected** per HC#6. If user declines to declare, three rules (DT-ENTRY-01, DT-DRILL-02, DT-EXCEPTION-03) evaluate as `n/a: flow_metadata_declined`.
- **Device-layout XML reliability gap** (variant of the `get-dashboard-xml` reliability gap). DT-DEVICE-08 falls back to `"unable to determine"` sentinel per HC#5 when device-layout XML cant be read.
- **Hidden-tab detection is XML-based.** DT-HIDDEN-07 detects declared hidden-tab flags in workbook XML. If a dashboard is hidden via a mechanism the XML doesnt expose, the rule may miss it.
- **DT-TABCOUNT-06 threshold is heuristic.** 10-tab threshold grounded in cognitive-load research (Millers 7±2, extended to 10 for pre-loaded visual navigation). Documented in `skill-expertise/rule_catalog.md` with defense.

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
