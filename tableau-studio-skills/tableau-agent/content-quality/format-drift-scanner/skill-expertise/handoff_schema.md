# Handoff Schema for `format_drift_report/1` (Locked)

Every successful `format-drift-scanner` invocation emits this schema, including "clean workbook" verdicts. Downstream skills (`publish-readiness`, `workbook-auditor`, `i18n-scanner`) may consume it. Schema is versioned; unknown versions refused by downstream per HC#8.

## Full Schema

```yaml
schema_version: format_drift_report/1
workbook_name: {name}
workbook_id: {luid_or_index}
placement_counts:
  measure_placements: {N}
  date_pills: {N}
  text_objects: {N}
data_sources:
  - name: {ds_name}
    id: {ds_luid}
findings_by_drift_type:
  currency: {N}
  decimal: {N}
  date: {N}
  separator: {N}
  font_family: {N}
  font_size: {N}
  negative_treatment: {N}
findings_count_by_severity:
  blocking: {N}
  warning: {N}
  info: {N}
findings:
  - rule_id: {F-CURRENCY-01 | F-DECIMAL-02 | F-DATE-03 | F-SEPARATOR-04 | F-FONT-FAMILY-05 | F-FONT-SIZE-06 | F-NEGATIVE-07}
    severity: {Blocking | Warning | Info}
    scope: {within_ds | cross_ds | workbook}
    data_source_name: {ds_name_or_null}
    element_category: {measure | date_pill | text_object}
    element_name: {field_name_or_element_category}
    differing_format_strings:
      - value: {format_string}
        placements: [{worksheet_or_dashboard_name}, ...]
    baseline_format_string: {format_string}
    finding_summary: {short_string}
    desktop_fix_instruction: {short_string}
    notes: {optional_free_text}
baselines_by_drift_type_per_ds:
  - drift_type: {currency | decimal | date | separator | negative_treatment}
    data_source_name: {ds_name}
    element_name: {field_name}
    baseline_format_string: {format_string}
  - drift_type: {font_family | font_size}
    scope: workbook
    element_category: {title | axis | tooltip | dashboard_text}
    baseline: {font_or_size_value}
unscanned_placements:
  - placement_id: {id}
    element_type: {measure_placement | date_pill | text_object}
    worksheet_name: {name_or_null}
    reason: {tool_failure | user_skip | fallback_unavailable}
    notes: {short_string}
run_metadata:
  timestamp: {ISO-8601}
  diff_mode: {true | false}
  prior_report_hash: {string_or_null}
  tool_failures: [{tool_name}, ...]
notes: {optional_free_text}
```

## Field-by-Field

- **schema_version.** Always exactly `format_drift_report/1`.
- **workbook_name / workbook_id.** Identifies the target workbook.
- **placement_counts.** Total count of measure placements, date pills, and text objects inventoried.
- **data_sources.** All data sources in the workbook. Used for scoping drift detection.
- **findings_by_drift_type.** Count of findings per drift type. Empty categories render as `0` (not omitted).
- **findings_count_by_severity.** Same counts grouped by severity.
- **findings.** Every drift finding with rule ID, severity, scope, differing format strings, and Desktop-fix instruction.
- **baselines_by_drift_type_per_ds.** First-seen format string per drift type per DS (or workbook-scoped for fonts). Records reproducibility signal per HC#11.
- **unscanned_placements.** Placements the run could not evaluate. Empty list `[]` if all placements were successfully scanned.
- **run_metadata.** Operational metadata. `diff_mode: true` when the report was reused verbatim from a prior report.
- **notes.** Optional free-text for edge cases.

## Downstream Consumer Expectations

- **`publish-readiness`.** Consumes `findings_count_by_severity` to inform pre-publish hygiene summary; skips its own format-hygiene section if a fresh report is in context.
- **`workbook-auditor`.** Consumes findings to enrich change digests when the user aligns formats between snapshots.
- **`i18n-scanner`.** Consumes currency and date findings as candidate locale-fragility signals.

## "Clean Workbook" Verdict Contract

When all `findings_by_drift_type` counters are `0`:

- `findings: []`.
- `unscanned_placements: []` (or non-empty with UNSCANNED explanations).
- `findings_count_by_severity: {blocking: 0, warning: 0, info: 0}`.
- `baselines_by_drift_type_per_ds` still populated (records the workbook's baseline format strings for future diff-mode runs).
- `notes` optionally explains scope: "All format strings within each drift category align. Workbook is format-drift clean across N measure placements and M data sources."

## "UNSCANNED" Handling

When placements cannot be evaluated (e.g., `get-worksheet-xml` fails):

- Every affected placement appears in `unscanned_placements` with a `reason` of `tool_failure`, `user_skip`, or `fallback_unavailable`.
- Findings still cite baseline drift where partial data is available.
- The `notes` field of each affected finding explicitly flags the partial coverage.

## Refuse to Guess

If any required field cannot be populated (e.g., baseline format string unresolvable, findings list contains a rule ID not in the catalog), refuse delivery per HC#8. Never fake fields to satisfy the schema.
