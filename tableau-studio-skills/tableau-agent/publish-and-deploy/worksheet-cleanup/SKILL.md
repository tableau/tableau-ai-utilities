---
name: worksheet-cleanup
description: "Use when the user says 'Clean up worksheets', 'remove orphan sheets', 'audit unused worksheets', 'prune this workbook'. Finds orphaned, empty, duplicate, or broken worksheets and removes them only with your consent per sheet, writing to a copy by default."
---

# Worksheet Cleanup

## When to use (full trigger detail)

Remove orphaned, empty, duplicate, or deleted-field-bound worksheets from a Tableau workbook against a locked 8-rule cleanup catalog, with mandatory read-only inventory pass first, per-worksheet consent per removal, action-config candidate-with-warning discipline for worksheets whose dashboard-action references cannot be verified (platform gap), and sibling-copy workbook write by default (never `--in-place` unless explicitly requested). Second mutating skill in the portfolio after calc-migrator. Read-only phase 1 always runs first; mutating phase 2 is opt-in per candidate. Trigger with clean up worksheets, remove orphan sheets, worksheet-cleanup, audit unused worksheets, prune this workbook. Do NOT trigger on. dashboard-level cleanup like zone removal or container flattening (out of scope), renaming worksheets (not supported), calc cleanup (route to calc-linter and calc-hygiene-scan), multi-workbook bulk cleanup (out of scope), or any request that would remove a worksheet referenced in a dashboard action config without a candidate-with-warning acknowledgment from the user.

## Purpose

Audit a Tableau workbook for orphaned, empty, duplicate, or dead-referenced worksheets against a locked 8-rule catalog. Emit a full read-only candidate inventory first. Then, on a per-worksheet basis with explicit user consent per removal, apply deletions to a sibling-copy workbook (never the original by default). Original workbook is byte-identical after the run unless the user explicitly requests `--in-place` mode.

## Trigger Conditions

- "clean up worksheets"
- "remove orphan sheets"
- "worksheet-cleanup"
- "audit unused worksheets"
- "prune this workbook"
- "which worksheets can I delete"
- "find orphan sheets"

## Do NOT Trigger On

- Dashboard-level cleanup (zone removal, container flattening, tab removal) → out of scope.
- Renaming worksheets → not supported.
- Calc-family cleanup (unused calcs, hardcoded values) → route to `calc-linter` or `calc-hygiene-scan`.
- Multi-workbook bulk cleanup → out of scope.
- Removing worksheets referenced in a dashboard action config without the user acknowledging the candidate-with-warning tier (HC#3 refuses to silently remove unverifiable candidates).
- Auditing dashboard tab order → route to `dashboard-tab-order`.
- Print-layout audit → route to `dashboard-print-check`.
- Removing a worksheet that would break a published dashboard on Server → skill flags but does not enforce; server-side verification is out of scope.

## Scope Boundaries

- **IN.** One workbook per run. Two-phase workflow: Phase 1 read-only inventory pass (always runs first, emits full candidate list with per-candidate rationale), Phase 2 mutating removal (opt-in per candidate, sibling-copy write). 8-rule cleanup catalog. Action-config candidate-with-warning tier per HC#3. `--in-place` mode available on explicit user request but not default. Handoff schema `worksheet_cleanup_report/1`.
- **OUT.** Multi-workbook batch runs. Dashboard-level cleanup (zones, containers, tabs). Worksheet renaming. Calc-family cleanup. Server-side impact verification. Any silent removal without per-worksheet consent. Any removal of a worksheet flagged as action-config-referenced without the user explicitly acknowledging the warning tier.

**Sibling-copy default.** Skill creates `{original_name}_cleaned.twb(x)` in the same directory as the source. Applies deletions on the copy. Original workbook unchanged unless `--in-place` explicitly requested. Refuses writes under `training-data/` per shared portfolio discipline.

**Multi-datasource scope.** Rule detection runs per-worksheet against that worksheets own active datasource(s), not the workbooks full datasource list. WC-DEAD-FIELD-05 checks `resolve-field` against every datasource a worksheet actually references; a field that resolves on a different datasource than the one the worksheet uses still fires WC-DEAD-FIELD-05 for that worksheet, tagged `cross_datasource_reference`. Workbooks with multiple datasources do not require special-casing beyond this — each worksheets rule evaluation is scoped to its own reference set.

**Action-config gap handling.** Dashboard action configs are inconsistently readable via `get-dashboard-xml`. Skills default posture: any worksheet whose action-config reference cannot be verified (action XML unreadable or partially readable) is tagged candidate-with-warning. User must explicitly acknowledge the warning before removal proceeds. No silent removal of unverifiable candidates ever.

## The 8-Rule Cleanup Catalog (Locked)

Every candidate maps to exactly one primary rule. Multi-rule candidates are tagged with all applicable rules but tier by the highest-severity match.

| # | Rule | ID | Severity | Detection |
|---|---|---|---|---|
| 1 | Orphaned scratch sheet (not on any dashboard, hidden or unhidden) | WC-ORPHAN-01 | Warning | `get-workbook-inventory` shows worksheet with zero dashboard placements. |
| 2 | Hidden worksheet with no dashboard use | WC-HIDDEN-02 | Warning | Worksheet has `hidden: true` in XML AND zero dashboard placements. Stronger signal than WC-ORPHAN-01. |
| 3 | Empty shelves (no fields on Rows / Columns / Text / Detail) | WC-EMPTY-03 | Warning | `get-worksheet-xml` shows all shelves empty. Excludes sheets with parameter-only placements. |
| 4 | Duplicate near-identical worksheet | WC-DUPE-04 | Info | Two or more worksheets with identical shelf configurations AND identical field references. Skill flags all copies; user chooses which to keep. |
| 5 | Worksheet bound to deleted fields | WC-DEAD-FIELD-05 | Warning | Worksheet has shelf placements referencing fields that `resolve-field` fails to locate on the active datasource. |
| 6 | Default name + no shelf content | WC-DEFAULT-NAME-06 | Warning | Name matches default patterns ("Sheet 1", "Feuille 1", "Hoja 1", "Blatt 1") AND WC-EMPTY-03 fires. Combined signal reduces false positives on legitimate placeholder sheets. |
| 7 | Worksheets with formula-only fields (calc placeholders never used) | WC-FORMULA-ONLY-07 | Info | Every field on the worksheet is a calculated field, AND the worksheet is not on any dashboard, AND all calcs are also unused elsewhere. Weak signal; requires all three conditions. |
| 8 | Worksheets referenced only by a sheet-swap parameter (dynamic zone visibility target) | WC-DZV-ONLY-08 | Info | Worksheet appears in a dashboard via dynamic zone visibility parameter binding AND has no direct dashboard placement AND parameter-binding traversal succeeded. If parameter traversal fails or returns partial results (parameter-readability gap), skill emits `"unable to determine"` sentinel for this rule per HC#5 rather than firing. Prevents false-positive removal of legitimately-placed worksheets when platform tools are unreliable. See `skill-expertise/rule_catalog.md` for detection detail. |

**Precedence and multi-rule tagging.** A worksheet can fire multiple rules (e.g., WC-HIDDEN-02 and WC-EMPTY-03 both true). Skill lists all triggered rules per candidate; the highest-severity rule sets the tier. WC-DZV-ONLY-08 and WC-FORMULA-ONLY-07 are the only Info-tier rules; the rest are Warning.

## Workflow Phases

- **Phase 0 Scope.** Confirm workbook is open via `get-workbook-inventory`. Confirm target workbook path. Confirm write destination (sibling-copy default; explicit `--in-place` opt-in required for direct-write).
- **Phase 1 Read-Only Inventory (always).** Enumerate every worksheet via `list-worksheets`. If `get-workbook-inventory` fails, times out, or returns empty for a workbook known to have worksheets, stop immediately and report the failure rather than emitting a partial or fabricated candidate list. For each worksheet, run the 8-rule detection catalog in a single pass: one `get-workbook-inventory` read plus one `get-worksheet-xml` read per worksheet supplies the evidence for all 8 rules — never issue separate reads per rule. Build the candidate list with per-candidate rule tags, action-config verifiability tag, and severity tier. Emit the full candidate list before any removal action.
- **Phase 2 Per-Candidate Consent (opt-in).** For each candidate, present:
  - Worksheet name
  - Rule(s) triggered
  - Severity tier
  - Action-config verifiability (verified | unable to verify)
  - Dashboard placements (if any, per WC-DZV-ONLY-08 detection)
  - Recommended action (remove | keep | investigate)
  
  Wait for users explicit yes / no / skip per candidate. No batch consent. If action-config verifiability is "unable to verify," user must acknowledge the candidate-with-warning tier before consent counts.
- **Phase 3 Sibling-Copy Preparation.** Before any removal, create `{original_name}_cleaned.twb(x)` in the same directory via `workbook-export-as` targeting the sibling path (falls back to `save-workbook` with a new path if `workbook-export-as` is unavailable). Verify the copy succeeded (file exists, non-zero size) before proceeding. **`save-workbook` with a `filePath` behaves like Save As in this environment — it switches the live Desktop sessions active document identity to the new file, it does not save a copy while leaving the original active.** Immediately after this call, re-check `get-workbook-inventory`s reported title/location; if it now points at the sibling rather than the original, the active document has been hijacked. Skill must not proceed to Phase 4 until the original is confirmed as the active document again (reopen the original path if needed). Treat this as a hard gate, not a warning: applying Phase 4 removals while the sibling is the active document risks corrupting the "original untouched" guarantee entirely, not just the mtime check.
- **Phase 4 Removal Application.** For each user-approved candidate, apply the removal on the sibling copy. Skill uses `worksheet-delete` tool (or platform equivalent, given known gaps in delete tools); if no delete tool is available or the call fails once, never fall back to XML manipulation (crash risk). Mark status `pending_manual_delete` and tell the user: In the copy, right-click the [sheet] tab > Delete, then tell me and Ill re-read the inventory to confirm.
- **Phase 5 Validate.** Run the 5-check V-gate: rule coverage, per-candidate consent complete, sibling-copy discipline held (source untouched), action-config warnings acknowledged, deletion applied cleanly.
- **Phase 6 Deliver.** Two-tier: compact chat summary with counts and top-3 removals + opt-in file save of full report to Downloads.

## Hard Constraints

**HC#1 Read-only Phase 1 always.** Phase 1 inventory runs before any removal. User sees the full candidate list before consent flow starts. No skipping straight to removal.

**HC#2 Sibling-copy default.** Original workbook untouched by default. `{original_name}_cleaned.twb(x)` sibling copy is the default write target. `--in-place` only on explicit user request with acknowledgment ("yes, apply to the original workbook"). Refuse writes under `training-data/`.

**HC#3 Action-config candidate-with-warning.** If dashboard action configs for a candidate cannot be verified, tag candidate-with-warning. User must acknowledge the warning tier explicitly ("I understand the action-config status is unverified") before consent counts. Never silently remove an unverifiable candidate.

**HC#4 Per-worksheet consent required.** Every removal requires explicit user yes/no/skip. No batch consent. User can respond "remove all Warning-tier" (batch confirmation) only after skill has presented each candidate individually and the user has explicitly requested batch mode; even then, skill iterates per-candidate consent for candidate-with-warning tier.

**HC#5 Refuse to fabricate.** Skill never invents dashboard placements, action-config references, or field-resolution status. Sentinels: `null`, `[]`, `"unresolved"`, `"unverified"`.

**HC#6 Never remove referenced worksheets silently.** Any worksheet with confirmed dashboard placement (positive signal from `get-dashboard-xml`) or confirmed action-config reference is refused for removal with a "remove from dashboard first" route. Only orphans, hidden-with-no-use, or user-acknowledged-warning candidates proceed to removal.

**HC#6 / HC#3 precedence (confirmed 2026-09-16 behavioral test).** These two constraints operate on different signals — HC#6 gates on dashboard *placement*, HC#3 gates on action-config *verifiability* — and a single worksheet can trigger both at once (placed on a dashboard AND the subset of that dashboards action config is unreadable). HC#6 takes precedence: a worksheet with **confirmed** dashboard placement is refused for removal outright, with the "remove from dashboard first" route, even if the user acknowledges the action-config warning under HC#3. HC#3s acknowledgment path only unblocks removal when placement itself is unconfirmed/ambiguous — it never overrides a confirmed placement. Skill must check placement confirmation status before offering the HC#3 acknowledgment prompt at all; if placement is confirmed, skip straight to the HC#6 refusal and do not present a warning-acknowledgment option for that candidate.

**HC#7 Sentinel discipline for empty-workbook.** Zero-worksheet workbooks exit cleanly with "no candidates found." One-worksheet workbooks refuse removal with "cannot remove the only worksheet" message.

**HC#8 Read-back verification.** After each removal on the sibling copy, skill re-reads the sibling copys inventory to confirm the worksheet is gone. Mismatch = mark that removal `failed`, alert user, proceed to next candidate.

**HC#9 Diff-mode transparency (portfolio-wide HC#13).** Repeat invocations against the same workbook state must state `diff_mode: fresh_scan | reused_verbatim | targeted_rescan` in Phase 1 output. Silent-diff-mode-skip pattern applies here per format-drift-scanners discovery.

**HC#10 Ordering determinism (portfolio-wide HC#14).** Candidate list sorted deterministically: severity tier first (Warning before Info), then by rule ID (WC-ORPHAN-01 first), then alphabetical by worksheet name. Same input produces byte-identical candidate list across runs.

**HC#11 Never touch the source workbook file (default mode).** V-gate verifies via workbook-fingerprint check, not file mtime: capture `targetFingerprint`/`workbook_hash` from `get-workbook-inventory` before the run, re-read it after Phase 4, and compare. Any hash change in default mode = V5 fail, skill flags a serious violation. File-mtime is not a reliable signal in this environment — the path Desktop reports via `get-workbook-inventory.location` does not reliably reflect the actual on-disk write target, so mtime comparisons against that path can silently pass or fail against the wrong file entirely.

**HC#12 Two-tier delivery. Never silent file write.** Tier B full report file save requires user path confirmation. No default writes to Downloads.

**HC#13 Locked 8-rule catalog.** No rule omitted, no fabricated rule added. Rule detection follows the criteria in the catalog above. Rule ID assignment is deterministic.

**HC#14 Handoff schema `worksheet_cleanup_report/1`.** Emitted with all fields populated. Empty-state prose ("no candidates found") for zero-candidate workbooks rather than blank fields.

**HC#15 Portfolio-wide HC#15 handoff staleness detection.** If skill consumes upstream handoffs (workbook-auditor, dashboard-caption-audit), verify hash against current workbook state; mismatch forces local re-derivation.

**HC#16 Wide-workbook scale handling.** For workbooks with 50 or more Phase 1 candidates, skill emits a wide-workbook-notice ("this workbook has N candidates; Tier A summary will truncate to top 10 per severity") and adjusts Tier A rendering: shows top 10 Warning-tier candidates + top 10 Info-tier candidates + a totals line. The full candidate list still lands in Tier B file save. Per-candidate consent flow still applies for every approved candidate; skill offers "review by rule ID" batch mode so the user can review all WC-ORPHAN-01 candidates together, then all WC-HIDDEN-02, etc. Per-candidate consent within each rule group still holds; batch mode does not batch consent, only presentation order.

## Validation Gate (5-Check)

- **V1 Rule Coverage.** All 8 rules evaluated against every worksheet in the workbook.
- **V2 Per-Candidate Consent Complete.** `consent_log[]` populated with explicit user response per candidate. No implicit assent.
- **V3 Sibling-Copy Discipline.** Default mode: source workbook fingerprint (`targetFingerprint`/hash) unchanged from pre-run, verified via `get-workbook-inventory`, not file mtime. `--in-place` mode: explicit user acknowledgment logged, fingerprint expected to change.
- **V4 Action-Config Warnings Acknowledged.** Every candidate with `action_config_verifiability: unverified` has a corresponding acknowledgment in `consent_log[]`.
- **V5 Ordering Determinism.** Candidate list sort key deterministic per HC#10.

## Two-Tier Delivery

**Tier A (chat).** Compact summary: workbook name, total worksheets, candidate count by severity tier, top 3 removals (deterministic sort per HC#10), verified vs. unverified action-config counts, sibling-copy path.

Template:

```
**Worksheet Cleanup: {workbook_name}**
Total worksheets: {N}
Candidates: {N_warning} Warning, {N_info} Info
Diff mode: {fresh_scan | reused_verbatim | targeted_rescan}

Top 3 Warning-tier removals:
1. {worksheet_name}: {rule_ids}. Action-config: {verifiability}. Recommended: remove.
2. ...
3. ...

Sibling copy will write to: {sibling_path}
Save full candidate report? (y/N)
```

**Tier B (opt-in file save).** Full report `.md` written to user-confirmed path. Includes per-candidate detail: rule triggered, evidence citation from XML, action-config verifiability tag, dashboard placements, Desktop-fix instructions if user declines removal, and handoff YAML block.

## Handoff Schema

Emits `worksheet_cleanup_report/1`:

```yaml
worksheet_cleanup_report:
  version: 1
  run_timestamp: <ISO 8601>
  workbook:
    name: <string>
    path: <string>
    total_worksheets: <int>
    workbook_hash: <sha256>
  diff_mode: <"fresh_scan" | "reused_verbatim" | "targeted_rescan">
  candidates:
    - worksheet_name: <string>
      rules_triggered: [<rule_id>]
      severity_tier: <"Warning" | "Info">
      action_config_verifiability: <"verified" | "unverified">
      dashboard_placements: [<dashboard_name>]
      recommended_action: <"remove" | "keep" | "investigate">
      consent: <"remove" | "keep" | "skip" | "pending">
      consent_timestamp: <ISO 8601>
      warning_acknowledged: <boolean|null>
      removal_status: <"applied" | "pending_manual_delete" | "refused" | "failed" | null>
  sibling_copy:
    path: <string>
    created: <boolean>
    mtime_verified: <boolean>
  in_place_mode: <boolean>
  in_place_acknowledgment: <string|null>
  totals:
    candidates_offered: <int>
    removals_applied: <int>
    removals_declined: <int>
    removals_failed: <int>
    warnings_acknowledged: <int>
  routing_offered:
    dashboard_preflight: <boolean>
    workbook_auditor: <boolean>
    publish_readiness: <boolean>
  v_gate:
    v1_rule_coverage: <pass|fail>
    v2_consent_complete: <pass|fail>
    v3_sibling_copy_discipline: <pass|fail>
    v4_warnings_acknowledged: <pass|fail>
    v5_ordering_determinism: <pass|fail>
```

Downstream consumers:

- **dashboard-preflight.** Identifies remaining orphans post-cleanup.
- **workbook-auditor.** Tracks worksheet-count deltas across runs.
- **publish-readiness.** Post-cleanup readiness sweep.
- **workbook-summary-onepager.** Reports on updated worksheet inventory.

## Adjacent-Skill Routing

- **Downstream opt-in:** dashboard-preflight (post-cleanup orphan sweep), workbook-auditor (delta tracking), publish-readiness (post-cleanup readiness), workbook-summary-onepager (updated worksheet inventory).
- **Refusal routes:** dashboard-level cleanup → out of scope; worksheet renaming → not supported; calc cleanup → calc-linter or calc-hygiene-scan; multi-workbook → not supported.

## Common Mistakes (Anti-Patterns)

- **Batching consent under one yes.** Even if the user says "remove all Warning-tier," skill still iterates per-candidate for candidate-with-warning tier. HC#4.
- **Silently removing action-config-referenced worksheets.** Action configs are inconsistently readable; skill must tag verifiability and require acknowledgment. HC#3.
- **Writing to the original workbook by default.** Sibling-copy is the default; `--in-place` is opt-in only. HC#2.
- **Skipping Phase 1 inventory.** Always emit the full candidate list before Phase 2 removal starts. HC#1.
- **Fabricating dashboard placements or action-config references.** Sentinel (`unresolved`, `unverified`) preferred over guess. HC#5.
- **Removing the only worksheet in a workbook.** Refuse per HC#7.

## Known Limitations

- **Delete-family tools inconsistent**. `worksheet-delete` tool availability varies by platform version; HC#8 read-back verification catches silent failures.
- **Action-config gap**. Dashboard action configs inconsistently readable. Skills candidate-with-warning tier is the workaround per HC#3.
- **`get-worksheet-xml` reliability gap on dashboard-bound sheets**. If a candidates XML cant be read, WC-EMPTY-03 and WC-FORMULA-ONLY-07 detection fall back to "unable to determine" sentinel per HC#5.
- **Server-side impact not verified.** If a published dashboard on Server references a worksheet, cleanup on the desktop workbook wont detect that. Out of scope.
- **DZV (dynamic zone visibility) detection is best-effort.** WC-DZV-ONLY-08 relies on parameter-binding traversal; if parameters are unreadable, rule falls back to "unable to determine" sentinel.
- **Duplicate detection is exact-match only.** WC-DUPE-04 requires identical shelf configurations AND field references. Near-duplicates with slight variance are not caught.
- **No undo capability.** Sibling-copy discipline is the recovery path; skill provides no revert mechanism beyond "delete the sibling copy and re-run."
- **`save-workbook` with a path acts as Save As, not save-a-copy** (confirmed 2026-09-16 behavioral test). Writing the sibling copy via `save-workbook filePath=...` switches the active Desktop document to that new file rather than leaving the original active. Phase 3 now hard-gates on re-confirming the original is active before Phase 4 proceeds. `workbook-export-as` (packaged-workbook format) does not have this problem and is preferred when available; `save-workbook` is the documented fallback only.

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
