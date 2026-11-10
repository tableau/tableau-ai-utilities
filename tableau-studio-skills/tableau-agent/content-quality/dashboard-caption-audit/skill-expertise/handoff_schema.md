# Handoff Schema for `caption_audit_report/1` (Locked)

Every successful `dashboard-caption-audit` invocation emits this schema. Downstream skills (`desktop-spellcheck`, `format-drift-scanner`, `viz-planner`, `dashboard-preflight`, `workbook-auditor`) may consume it. Schema is versioned; unknown versions refused by downstream per HC#8.

## Full Schema

```yaml
schema_version: caption_audit_report/1
workbook_name: {name}
dashboards_audited: {N}
audit_metadata:
  timestamp: {ISO-8601}
  total_dashboards_in_workbook: {N}
  worksheets_on_audited_dashboards: {N}
  text_objects_audited: {N}
findings:
  - rule_id: {DC-TITLE-01 | DC-CAPTION-02 | DC-WS-TITLE-03 | DC-WS-CAPTION-04 | DC-TEXT-EMPTY-05 | DC-DEFAULT-NAME-06 | DC-DEVICE-07 | DC-TITLE-08}
    rule_name: {short_string}
    severity: {Warning | Info}
    dashboard_name: {name}
    element_type: {dashboard | worksheet | text_object | device_layout_parent}
    element_name: {name_or_null}
    xml_evidence: {snippet_string}
    desktop_fix: {step_by_step_instruction}
    affected_variants: [{phone | tablet | empty}]
finding_counts:
  warnings: {N}
  info: {N}
unscanned_dashboards:
  - dashboard_name: {name}
    reason: {short_string, e.g. "get-dashboard-xml returned partial results"}
routing:
  desktop_spellcheck: {true | false}
  format_drift_scanner: {true | false}
  viz_planner: {true | false}
  dashboard_preflight: {true | false}
  rationale: {short_string}
delivery:
  tier_a_rendered: {true | false}
  tier_b_saved: {true | false}
  tier_b_file_path: {absolute_path_or_null}
  tier_b_format: {md | txt | null}
run_metadata:
  tool_failures: [{tool_name_or_empty}]
notes: {optional_free_text}
```

## Field-by-Field

- **schema_version.** Always exactly `caption_audit_report/1`.
- **workbook_name.** Name of the audited workbook.
- **dashboards_audited.** Count of dashboards actually walked (excludes UNSCANNED).
- **audit_metadata.** Operational context (timestamp, total counts).
- **findings.** Every finding rendered in the report. Empty list `[]` if fully labeled.
- **finding_counts.** Aggregate by severity for quick consumption.
- **unscanned_dashboards.** HC#9 flagged dashboards with reason. Empty `[]` when all dashboards walked cleanly.
- **routing.** Downstream skill routing flags. Booleans set based on finding types:
  - `desktop_spellcheck: true` only when this run's Recommended Actions include adding NEW caption/title text (i.e., at least one DC-CAPTION-02, DC-WS-CAPTION-04, DC-TITLE-01, or DC-WS-TITLE-03 finding exists). Set `false` when the workbook is fully labeled or when all findings are non-text issues (e.g., only DC-DEFAULT-NAME-06 or DC-TEXT-EMPTY-05). The flag signals "spellcheck the text the user is about to add," not "text already exists somewhere in the workbook."
  - `format_drift_scanner: true` if caption fonts might drift after new captions added.
  - `viz_planner: true` if 5+ Warnings suggest structural redesign.
  - `dashboard_preflight: true` always (preflight consumes caption findings for assembly hygiene enrichment).
- **delivery.** Records Tier A/Tier B state; whether the file was saved and where.
- **run_metadata.** Operational metadata; `tool_failures` lists any tool that failed mid-run.
- **notes.** Optional free-text for edge cases.

## Downstream Consumer Expectations

- **`desktop-spellcheck`.** Consumes when `routing.desktop_spellcheck: true`. After the user adds missing captions, spellcheck the new text.
- **`format-drift-scanner`.** Consumes when `routing.format_drift_scanner: true`. New captions may drift font family or size from workbook baseline.
- **`viz-planner`.** Consumes when `routing.viz_planner: true` (5+ Warnings). Uses findings as design-review input.
- **`dashboard-preflight`.** Always consumes. Caption findings enrich assembly hygiene at pre-publish time.
- **`workbook-auditor`.** Consumes finding deltas across runs (workbook improvement or regression tracking).

## Verdict Contracts

**"Fully labeled workbook" (no findings):**

- `findings: []`.
- `finding_counts.warnings: 0`, `finding_counts.info: 0`.
- `routing.dashboard_preflight: true` (always).
- All other routing flags: `false`.

**"Mixed findings workbook":**

- `findings` contains at least one entry.
- `finding_counts` reflects severity distribution.
- `routing` flags set per finding-count thresholds.

**"UNSCANNED partial audit":**

- `unscanned_dashboards` populated with at least one entry.
- `findings` reflects only dashboards that were successfully walked.
- Report includes UNSCANNED disclosure section.
- `notes` may include recovery guidance.

## Refuse to Guess

If any required field cannot be populated, refuse delivery per HC#8. Never fake a finding. Never assign a rule_id that doesn't match the 8-rule catalog. Never bypass HC#11 (default-name always Warning).
