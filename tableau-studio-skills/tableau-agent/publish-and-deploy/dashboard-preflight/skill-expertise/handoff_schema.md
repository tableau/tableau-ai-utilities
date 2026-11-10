# Handoff Schema for `dashboard_preflight_report/1` (Locked)

Every successful `dashboard-preflight` invocation emits this schema, including "clean dashboard" verdicts. Downstream skills (publish-readiness, workbook-auditor) may consume it. Schema is versioned; unknown versions refused by downstream.

## Full Schema

```yaml
schema_version: dashboard_preflight_report/1
workbook_name: {name}
workbook_id: {luid}
dashboard_name: {name}
dashboard_id: {luid_or_index}
zone_count: {N}
findings_count_by_severity:
  blocking: {N}
  warning: {N}
  info: {N}
findings:
  - rule_id: {P-ZONE-01 | P-SHEET-02 | ... | P-CONTAINER-08 | "unscanned"}
    severity: {Blocking | Warning | Info}
    zone_reference: {zone_name_or_id}  # OR omit if dashboard_scope: true
    dashboard_scope: {true | false}  # true for dashboard-level findings
    finding_summary: {short_string}
    desktop_fix_instruction: {short_string}
    notes: {optional_free_text}  # required when rule_id is "unscanned"
unscanned_checks:
  - rule_id: {P-ZONE-01 | ...}
    reason: {tool_failure | user_skip | fallback_unavailable}
    notes: {short_string}
run_metadata:
  timestamp: {ISO-8601}
  tool_failures: [{tool_name}, ...]
  fallback_paths_used: [{path_name}, ...]
handoff_ready: {true | false}
handoff_block_reason: {short_string}  # required when handoff_ready: false
notes: {optional_free_text}
```

## Field-by-Field

- **schema_version:** always `dashboard_preflight_report/1`.
- **workbook_name / workbook_id:** identifies the source workbook.
- **dashboard_name / dashboard_id:** identifies the target dashboard. Multi-dashboard workbooks require the user to name a target before this handoff can be built (HC#2).
- **zone_count:** count of zones in the dashboard from Phase 1 inventory.
- **findings_count_by_severity:** cardinality of findings by severity tier. Aggregate for the report banner.
- **findings:** list of finding entries. Empty list `[]` for clean dashboards.
- **findings[].rule_id:** one of the 8 catalog rule IDs OR `"unscanned"`.
- **findings[].severity:** `Blocking`, `Warning`, or `Info` per the catalog severity table.
- **findings[].zone_reference:** zone name or index. Omit when `dashboard_scope: true`.
- **findings[].dashboard_scope:** `true` for dashboard-level findings (canvas, dashboard-title, dashboard-level filter actions).
- **findings[].finding_summary:** one-line description of the finding.
- **findings[].desktop_fix_instruction:** concrete Desktop UI steps. Never blank.
- **findings[].notes:** optional; required when `rule_id: "unscanned"` with the reason for the skip.
- **unscanned_checks:** list of catalog rule IDs that could not be evaluated, with reason and notes. Distinct from findings; a check that was evaluated cleanly (no finding) does NOT appear here.
- **run_metadata.timestamp:** ISO-8601 timestamp of report delivery.
- **run_metadata.tool_failures:** list of Desktop tools that returned errors during the run.
- **run_metadata.fallback_paths_used:** list of documented fallback paths triggered (e.g., `get-worksheet-xml-fallback-to-list-available-fields`).
- **handoff_ready:** `true` if the report is complete and downstream skills can consume it. `false` if there are unrecoverable gaps.
- **handoff_block_reason:** required when `handoff_ready: false`. Concise reason string.
- **notes:** optional free-text for reporter comments.

## Downstream Consumer Expectations

- **publish-readiness.** Reads `findings_count_by_severity` and `findings[]` to skip its own dashboard-hygiene checks. Uses `handoff_ready` to decide whether to trust the preflight report.
- **workbook-auditor.** Reads `findings` and appends to change digests when the diff includes a dashboard whose preflight status changed.

## "Clean Dashboard" Verdict Contract

When `findings: []`:

- `findings_count_by_severity: { blocking: 0, warning: 0, info: 0 }`.
- `unscanned_checks: []` (or populated with any user-skipped checks per HC#5).
- `handoff_ready: true`.
- `notes` should confirm: "Dashboard `{name}` passed all 8 preflight checks with zero findings."

## Bulk-Action Refusal Contract

If the ask was a bulk-preflight (e.g., "preflight all my dashboards"), dashboard-preflight does NOT emit this schema. Instead, refuse per HC#3 with routing guidance to run one dashboard at a time. The refusal is not a delivery.

## Refuse to Guess

If any required field can't be populated (e.g., `dashboard_id` unresolvable, tool failures prevent Phase 1 inventory), refuse delivery per HC#8. Never fake fields to satisfy the schema. Never claim `handoff_ready: true` if any check is unresolved without being recorded in `unscanned_checks`.
