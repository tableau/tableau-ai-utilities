# Output Template (Locked)

Deterministic output shape. Every delivery renders these sections in this order. Never skip a section; render "None applicable" if a section has nothing to report.

## Template

```markdown
## Summary

- **Data source audited:** {datasource_name}
- **Geographic fields found:** {N}
- **Findings by severity:** Critical {N_c}, Warning {N_w}, Note {N_n}, Info {N_i}
- **Sample-size status:** {all_verified | mixed | all_unverified}

## Findings by Severity

### Critical ({N_c})

For each Critical finding:
- **{G_id}: {field_name}** — {current_role} → recommended {recommended_role}
  - Evidence: {percent_or_sample_values}
  - Sample size: {N_rows} ({verified | unverified})
  - Fix: {Desktop_UI_steps}
  - {optional_precedence_note: "Secondary to G{n} on same field"}

### Warning ({N_w})

Same format as Critical.

### Note ({N_n})

Same format.

### Info ({N_i})

Same format.

## Handoff (if applicable)

- **Build a map next?** Trigger `worksheet-builder` with: "build a map from {geographic_field_name}."
- **Performance tuning next?** Trigger `extract-optimizer` with: "optimize the extract for {datasource_name}."
- **Pre-ship hygiene next?** Trigger `publish-readiness` with: "publish readiness check for {workbook_name}."
- **Not sure what's next?** No handoff. Skill's job ends at findings delivery.

## Handoff YAML (optional, schema_version geo_audit_handoff/1)

Only render if a downstream skill has requested a machine-parseable handoff.

```yaml
schema_version: geo_audit_handoff/1
datasource_name: {name}
findings:
  - g_id: {G1 | G2 | ... | G6}
    field: {field_name}
    current_role: {role_name}
    recommended_role: {role_name}
    severity: {critical | warning | note | info}
    evidence: {string}
    sample_size: {N}
    verified: {true | false}
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

- Every `{placeholder}` must be filled or replaced with "not applicable" / "none." Never leave a placeholder.
- Every severity section header renders even with zero findings ("Critical (0)" with "None." body). Silence would be ambiguous.
- Sample-size status in Summary is `all_verified` (all findings ≥1000 rows), `mixed` (some verified, some not), or `all_unverified`.
- Handoff section renders three routing options plus the "no handoff" fallback.
- Handoff YAML renders only when downstream skill requested.

## What NOT to Render

- Tool names (`get-summary-data`, `list-available-fields`). Stay user-facing.
- Internal reference-file names (`geocoding_checks.md`, `severity_rubric.md`).
- Grader IDs, validation-gate IDs, or hard-constraint IDs.
- Hedged language ("might be misassigned," "could be ambiguous"). Findings cite G-ID with evidence; severity is locked.

## Refuse to Deliver on Validation Gate Failure

If Phase 4 fails V1, V2, or V3, do NOT render this template as-is:

- **V1 fail (finding without G-ID):** Drop the finding. Never render an unlabeled geographic finding.
- **V2 fail (severity off-rubric):** Recompute severity from rubric. If ambiguous, pick higher severity.
- **V3 fail (no sample size):** Flag the finding as "unverified" rather than dropping.

The Validation Gate is a hard block, not a soft warning.
