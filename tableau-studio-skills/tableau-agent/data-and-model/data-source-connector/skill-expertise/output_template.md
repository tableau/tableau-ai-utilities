# Output Template (Locked)

Deterministic output shape. Every delivery renders these sections in this order. Never skip a section; render "None applicable" if a section has nothing to report.

## Template

```markdown
## Recommended Connector

- **Primary:** {primary_connector_name} ({driver_status})
- **Alternate:** {alternate_connector_name_or_"none applicable"}
- **Why this:** {one_line_rationale_from_catalog}

## Recommended Auth

- **Pattern:** {auth_pattern_name}
- **Why this:** {one_line_rationale_from_rubric}
- **Refresh compatibility:** {survives_scheduled_refresh | interactive_only}

## Prerequisites

- **Driver installs:** {driver_name_and_download_source | "none required, bundled with Desktop"}
- **Service account setup:** {steps | "not required for this auth pattern"}
- **Network:** {allow_list_targets_or_VPN_requirement | "no network config required"}

## Desktop UI Walkthrough

1. Data menu → New Data Source.
2. Search or scroll to {primary_connector_name}.
3. In the connection dialog: {dialog_fields_and_values}.
4. Auth section: {auth_specific_steps}.
5. Test the connection.
6. If test succeeds, click Connect. If it fails, see Error Handling.

## Handoff (if applicable)

- **Modeling next?** Trigger `join-and-relationship-advisor` with: "recommend relationships for {datasource_name}."
- **Data quality next?** Trigger `data-quality-review` with: "check data quality on {datasource_name}."
- **Not sure what's next?** No handoff. Skill's job ends at successful connection.

## Handoff YAML (optional, schema_version connection_handoff/1)

Only render if a downstream skill has requested a machine-parseable handoff.

```yaml
schema_version: connection_handoff/1
datasource_name: {name}
connector: {primary_connector_name}
auth_pattern: {auth_pattern_name}
hosting_mode: {self_hosted | cloud_hosted | on_prem_vpn}
extract_or_live: {extract | live | not_yet_configured}
verified: {true | false}
notes: {optional_free_text}
```
```

## Filling Rules

- Every `{placeholder}` must be filled or replaced with "not applicable" / "none required." Never leave a placeholder in the delivered output.
- Every section header must render, even if the section has no content. This is how the user knows the check ran.
- Prerequisites section always renders three sub-lines (Driver, Service account, Network), even if all three say "none required."
- Handoff section renders the two routing options plus the "no handoff" fallback. Never invent a fourth handoff.
- Handoff YAML renders only when a downstream skill has requested it. Not for every delivery.

## What NOT to Render

- Tool names (e.g., `bind-template`, `list-workbook-datasources`). This skill uses no tools; the output stays user-facing.
- Internal reference-file names or paths.
- Grader IDs, validation-gate IDs, or hard-constraint IDs.
- Any language that hedges the recommendation ("this might work," "you could try"). The catalog and rubric are locked; recommendations are definitive within their scope.

## Refuse to Deliver on Validation Gate Failure

If Phase 4.5 fails V1, V2, or V3, do NOT render this template. Instead:

- **V1 fail (connector not in catalog):** Render only the ODBC generic fallback plus a one-line explanation.
- **V2 fail (auth not in rubric):** Render the "no matching auth pattern" refusal from `auth_patterns.md`.
- **V3 fail (UI path uncertain):** Render "current Desktop menu paths uncertain; defer to Desktop's built-in help" and refuse the UI walkthrough.

The Validation Gate is a hard block, not a soft warning.
