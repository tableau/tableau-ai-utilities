# Output Template (Locked)

Deterministic output shape. Every delivery renders these sections in this order. Never skip a section; render "None applicable" if a section has nothing to report.

## Template

```markdown
## Summary

- **Data source audited:** {datasource_name}
- **Extracts found:** {N}
- **Findings by severity:** Critical {N_c}, Warning {N_w}, Note {N_n}, Info {N_i}
- **Sample-size status:** {all_verified | mixed | all_unverified}
- **Precedence applied:** {yes_multiple_dimensions_fired | no_single_dimension}

## Findings by Dimension

### D1 Incremental Refresh Key

For each D1 finding:
- **{extract_name}** — {severity}
  - Evidence: {candidate_field_name}, {monotonic_min}, {monotonic_max}
  - Quantified impact: {refresh_time_reduction_percent}, {new_rows_per_interval}
  - Fix: Data → [datasource] → Extract → Edit → All rows / Incremental refresh → New rows identified by [field]
  - {optional_precedence_note: "Secondary to D3/D4"}

Render "None." if D1 has no findings.

### D2 Aggregation

Same format as D1.

### D3 Hidden-Field Pruning

Same format.

### D4 Filter-at-Extract

Same format.

## Handoff (if applicable)

- **Calc perf next?** Ask `calc-optimizer` to "optimize this calc" for each slow calc on {datasource_name}.
- **Dashboard perf next?** Trigger `worksheet-builder` with: "check dashboard render performance for {workbook_name}."
- **Full pre-ship hygiene?** Trigger `publish-readiness` with: "publish readiness check for {workbook_name}."
- **Not sure what's next?** No handoff. Skill's job ends at findings delivery.

## Handoff YAML (optional, schema_version extract_audit_handoff/1)

Only render if a downstream skill has requested a machine-parseable handoff.

```yaml
schema_version: extract_audit_handoff/1
datasource_name: {name}
extracts:
  - extract_name: {name}
    findings:
      - d_id: {D1 | D2 | D3 | D4}
        severity: {critical | warning | note | info}
        quantified_impact: {string_with_numbers}
        verified: {true | false}
    dimension_precedence_applied: {true | false}
summary_counts:
  critical: {N_c}
  warning: {N_w}
  note: {N_n}
  info: {N_i}
verified: {true | false}
notes: {optional_free_text}
```
```

## Filling Rules

- Every `{placeholder}` filled or replaced with "not applicable." No placeholders in delivered output.
- Every D-section header renders even with zero findings ("D1 Incremental Refresh Key" with "None." body).
- Sample-size status: `all_verified` (all findings ≥1000 rows), `mixed`, or `all_unverified`.
- Precedence Applied: `yes` if multiple D-dimensions fired on same extract and precedence broke ties; `no` otherwise.
- Handoff YAML renders only on downstream skill request.

## What NOT to Render

- Tool names (`get-summary-data`, `list-available-fields`). Stay user-facing.
- Internal reference-file names.
- Grader IDs, gate IDs, HC IDs.
- Hedged language ("should improve performance"). HC#3 banned. Quantify or drop.

## Refuse to Deliver on Validation Gate Failure

- **V1 fail (finding without D-ID):** Drop the finding.
- **V2 fail (severity off-rubric):** Recompute from rubric.
- **V3 fail (unquantified impact):** Drop the finding. HC#3 hard-bans hedging.

The Validation Gate is a hard block, not a soft warning.
