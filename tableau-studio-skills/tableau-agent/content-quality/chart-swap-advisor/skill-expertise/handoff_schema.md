# Handoff Schema for `chart_swap_recommendation/1` (Locked)

Every successful `chart-swap-advisor` invocation emits this schema, including Keep verdicts. Downstream skills (`worksheet-builder`, `viz-planner`, `workbook-auditor`) may consume it. Schema is versioned; unknown versions refused by downstream per HC#8.

## Full Schema

```yaml
schema_version: chart_swap_recommendation/1
workbook_name: {name}
worksheet_name: {name}
worksheet_id: {luid_or_index}
current_chart:
  mark_type: {mark_type_string}
  shelf_placement_summary: {short_string}
  view_fit: {Standard | Fit Width | Fit Height | Entire View}
  field_count: {N}
  measure_count: {N}
  dimension_count: {N}
classification:
  question_type: {Temporal | Categorical | Composition | Distribution | Correlation | Ranking | Geographic | Status_KPI | Sequential | refused_no_match}
  confidence: {High | Medium | Low | unscanned}
  supporting_signals:
    - {signal_string}
  classification_notes: {optional_free_text}  # required when confidence is Low
anti_patterns_matched:
  - anti_pattern_id: {AB-1 | AB-2 | ... | W-1 | ... | W-7 | I-1 | I-2}
    severity: {Auto-Block | Warning | Info}
    rationale: {short_string}
verdict: {Keep | Swap Recommended | Anti-Pattern Block}
recommendation:
  recommended_chart_type: {chart_type_string_or_null}
  rationale: {short_string}
  rebuild_handoff_payload:
    recommended_mark_type: {mark_type_string}
    recommended_shelf_placements:
      rows: [{field_name}, ...]
      columns: [{field_name}, ...]
      marks: [{field_name}, ...]
      filters: [{field_name}, ...]
      detail: [{field_name}, ...]
    preserve_fields: [{field_name}, ...]
    fields_to_drop: [{field_name}, ...]
    rebuild_instructions_summary: {short_string}
audience:
  stated: {true | false}
  audience_type: {Executive | Manager | Analyst | Operations | External | null}
run_metadata:
  timestamp: {ISO-8601}
  diff_mode: {true | false}
  prior_report_hash: {string_or_null}
  tool_failures: [{tool_name}, ...]
notes: {optional_free_text}
```

## Field-by-Field

- **schema_version.** Always exactly `chart_swap_recommendation/1`.
- **workbook_name / worksheet_name / worksheet_id.** Identifies the target worksheet.
- **current_chart.** Snapshot of what was audited. `mark_type` from `get-worksheet-xml` mark declaration; `shelf_placement_summary` is a short human-readable summary; `view_fit` from the same XML; counts from `list-available-fields`.
- **classification.** Question-type assignment plus confidence tag plus supporting signals. `classification_notes` required when confidence is Low.
- **anti_patterns_matched.** Every anti-pattern that fired. Empty list `[]` when none fired.
- **verdict.** Exactly one of `Keep`, `Swap Recommended`, `Anti-Pattern Block`.
- **recommendation.** Only populated when verdict is Swap Recommended or Anti-Pattern Block. `rebuild_handoff_payload` is `null` when verdict is Keep.
- **audience.** `stated: true` when the user explicitly named an audience. `audience_type` is `null` when `stated: false`.
- **run_metadata.** Operational metadata. `diff_mode: true` when the recommendation was reused verbatim from a prior report. `prior_report_hash` populated in diff mode; `null` otherwise. `tool_failures` lists any tools that failed during the run (usually empty).
- **notes.** Optional free-text for edge cases.

## Downstream Consumer Expectations

- **`worksheet-builder`.** Consumes `recommendation.rebuild_handoff_payload` when verdict is Swap Recommended or Anti-Pattern Block. Presents its own build plan to the user for approval before invoking `bind-template` or `build-and-apply-worksheet`.
- **`viz-planner`.** Consumes multiple recommendations to inform dashboard-level chart-mix decisions.
- **`workbook-auditor`.** Consumes recommendations to enrich change digests when the user rebuilds.

## "Keep" Verdict Contract

When `verdict: Keep`:

- `recommendation.recommended_chart_type` matches `current_chart.mark_type`. This is the only case where they should match.
- `recommendation.rebuild_handoff_payload` is `null`.
- `recommendation.rationale` explains why the current chart is a right fit (question type match, no anti-patterns, no audience mismatch).
- `anti_patterns_matched` is `[]`.

**Low-confidence non-endorsement variant of Keep.** When `classification.confidence` is `Low` and the anti-pattern gate is clean, `verdict` is still `Keep`, but `recommendation.recommended_chart_type` is `null` (never the current mark type) and `recommendation.rationale` explicitly states this is a low-confidence non-endorsement, not a best-fit match — per the locked default in `chart_recommendation_catalog.md`.

## "Anti-Pattern Block" Verdict Contract

When `verdict: Anti-Pattern Block`:

- `anti_patterns_matched` contains at least one Auto-Block entry (AB-1 through AB-6).
- `recommendation.recommended_chart_type` names the anti-pattern's escape route (never the current type).
- `recommendation.rationale` cites the specific anti-pattern IDs.
- HC#11 enforcement: this verdict cannot be overridden by user pressure.

## "Swap Recommended" Verdict Contract

When `verdict: Swap Recommended`:

- At least one of: (a) anti_patterns_matched contains a Warning-tier entry, or (b) classification recommends a different chart type than current.
- `recommendation.recommended_chart_type` names the target chart type from the recommendation catalog.
- `recommendation.rationale` cites the question-type match and any anti-patterns.

## Refuse to Guess

If any required field cannot be populated (e.g., `mark_type` unreadable, `classification.question_type` unassignable), refuse delivery per HC#8. Never fake fields to satisfy the schema. Never assign a High confidence tag when supporting signals don't support it.
