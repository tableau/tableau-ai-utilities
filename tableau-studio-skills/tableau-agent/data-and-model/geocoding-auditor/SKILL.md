---
name: geocoding-auditor
description: "Use when the user says 'Why is my map wrong?', 'unknown locations', 'why won't my cities match?', 'geo role check'. Audits geographic fields for wrong roles, unmatched or ambiguous locations, and missing hierarchies that break maps, with fix steps. Read-only."
---

# Geocoding Auditor

## When to use (full trigger detail)

Audit a Tableau workbooks geocoded fields for role-assignment mistakes, unmatched-location rates, and ambiguity that silently break maps. Read-only. Runs six locked checks (G1 Role Mismatch, G2 High Unmatched Rate, G3 High Ambiguous Rate, G4 Wrong Country Resolution, G5 Missing Hierarchy, G6 Role-vs-Datatype Conflict) with locked severity thresholds. Every fix is a Desktop UI instruction. Triggers on geocoding audit, geo audit, unknown locations, why wont my cities match, geo role check, why is my map wrong, unmatched addresses, ambiguous locations. Do NOT trigger for building a map (use worksheet-builder), map design (use viz-planner), performance tuning (use extract-optimizer), pre-publish hygiene (use publish-readiness), or Server/Cloud mapping-service configuration (out of scope).

## Purpose

Audit a Tableau workbooks geocoded fields for role-assignment mistakes, unmatched-location rates, and ambiguity that will silently break maps. Novel domain in the portfolio. Read-only. Every finding is a Desktop UI instruction because role assignment is a right-click menu action, not a tool call.

## Trigger Conditions

geocoding audit, geo audit, audit my map fields, unknown locations, why wont my cities match, geo role check, check geographic roles, why is my map wrong, unmatched addresses, ambiguous locations.

Do NOT trigger on: building a map (`worksheet-builder`); designing a maps interactions or layout (`viz-planner`); performance issues on a map with millions of marks (`extract-optimizer` for extract-level, `publish-readiness` for pre-ship); recommending which cities or countries to include (business decision); Server/Cloud mapping-service configuration (out of scope).

## Scope Boundaries

- IN: geographic-role assignment audit per field; unmatched and ambiguous rate reporting via `get-summary-data` sampling; wrong-country resolution detection (shared city names across countries); missing-hierarchy detection; role-vs-datatype conflict; severity-tiered findings (Critical/Warning/Note/Info).
- OUT: building a map (`worksheet-builder`); designing map interactions (`viz-planner`); performance tuning (`extract-optimizer`); which cities/countries to include (business decision); fixing role assignments programmatically (Desktop UI only); recommending a mapping service (Mapbox, custom polygons — Tableau server-side config).

### Edge-Case Boundaries

| Edge Case | Handling |
|---|---|
| Custom polygon (spatial file) | Refuse. |
| Spatial-file connector (SHP, KML, GeoJSON) | Refuse for role audit; the files spatial fields are typed by the connector, not by user assignment. |
| Latitude/Longitude as measures on a map | G6 fires if datatype conflict; otherwise out of scope (map placement is `worksheet-builder`). |
| RTL city names (Arabic, Hebrew) | Handled by G2/G3 as unmatched or ambiguous. Note the RTL caveat when >5% of a field is RTL. |
| CJK city names (Chinese, Japanese, Korean) | Same as RTL; handled via G2/G3 unmatched rate. |
| Multi-language mixed fields | Higher unmatched rate expected. G2 fires at same thresholds. |
| Zero geographic fields | Refuse: no geographic fields; nothing to audit. |
| Sample size below 1,000 rows | Report findings but flag rates as unverified: sample size below reliable threshold. |

## Hard Constraints

- HC#1: Read-only. Zero mutating tool calls. Role assignment is a right-click Desktop UI action.
- HC#2: Six checks locked (G1-G6). Never invent a check category.
- HC#3: Severity thresholds locked in `skill-expertise/severity_rubric.md`. No model interpretation.
- HC#4: Sampling batched per field. One `get-summary-data` sample used across all applicable checks.
- HC#5: Refuse out-of-scope questions by exact slug.
- HC#6: Validation Gate before delivery. Every recommendation must pass V1 (finding cites G-ID), V2 (severity matches rubric), V3 (sample size disclosed).
- HC#7: Disagreement branch is scoped. Offer at most one alternate role recommendation. Never chain a second alternate.
- HC#8: Detection precedence when multiple G-checks fire on same field: G1 (Role Mismatch) > G6 (Datatype Conflict) > G2 (Unmatched Rate) > G3 (Ambiguous Rate) > G4 (Wrong Country) > G5 (Missing Hierarchy). Higher precedence wins; lower still reports but flagged as secondary.

## Tools Used

- `list-workbook-datasources` — Phase 0 (enumerate DS).
- `list-available-fields` (verbosity: full) — Phase 1 (enumerate geographic fields, candidate role-mismatch surfaces).
- `get-summary-data` — Phase 2 (one sample per field, batched across all applicable checks).

Zero mutating tool calls. Zero file writes.

## Sample-Size Reliability Threshold

Unmatched/ambiguous rate estimates are reliable when the sample includes at least **1,000 rows**. Below that threshold:

- Report findings using the locked severity rubric.
- Flag the rate as **unverified: sample size below reliable threshold (1,000 rows).**
- Severity does not downgrade; the confidence label changes.

**User override.** If the user explicitly asks for a faster first pass with fewer rows (e.g., just give me a quick read, dont wait for the full sample), sample below the 1,000-row floor on request. Always label the resulting findings unverified: sample size below reliable threshold (user-requested fast pass) rather than the default unverified label, so its clear the shortcut was requested, not a sampling failure. Severity assignment and the rest of the workflow are unchanged.

For wide-workbook batching, if enumerating fields across 100+ fields, batch `list-available-fields` calls in groups of ~10 with inline progress notes.

## Workflow Phases

1. **Phase 0 Intake.** Confirm data source via `list-workbook-datasources`. If multi-source, ask which. Refuse per Edge-Case Boundary if zero geographic fields.
2. **Phase 1 Inventory Geographic Fields.** `list-available-fields` (verbosity: full). Enumerate fields with geographic roles + candidate role-mismatch surfaces (fields with geography-suggesting names or datatypes but no role assigned).
3. **Phase 2 Run Six Checks.** G1 Role Mismatch, G2 High Unmatched Rate, G3 High Ambiguous Rate, G4 Wrong Country Resolution, G5 Missing Hierarchy, G6 Role-vs-Datatype Conflict. Batch `get-summary-data` sampling once per field. Apply HC#8 precedence when multiple hits.
4. **Phase 3 Severity Ranking.** Apply `skill-expertise/severity_rubric.md`. Sort Critical → Warning → Note → Info. Within severity, sort alphabetically by field name for determinism.
5. **Phase 4 Validation Gate.** Before delivery, confirm all three:
   - **V1 G-ID citation.** Every finding cites a check ID from G1-G6. No unlabeled findings.
   - **V2 Severity match.** Every severity assignment matches `severity_rubric.md`. No off-rubric severity.
   - **V3 Sample size disclosed.** Every rate-based finding (G2, G3) reports either verified (≥1000 rows) or unverified (<1000 rows) sample size.
   Failing any gate blocks delivery. Drop the failing finding or report the gate failure honestly.
6. **Phase 4.5 Disagreement Branch (conditional).** If the user disputes a role recommendation after delivery:
   - Offer one alternate role from the same G-checks rationale (e.g., if G1 recommended Zip Code, alternate could be Postal Code for international).
   - If rejected, route to Tableaus Geographic Role documentation. Never a second alternate.
7. **Phase 5 Report Assembly.** Grouped by severity. Each finding: check ID (G1-G6), field name, current role, recommended role, evidence (percent unmatched, sample values), Desktop UI fix, precedence note if secondary.
8. **Phase 6 Handoff.** Map-build → `worksheet-builder`. Performance → `extract-optimizer`. Pre-ship hygiene → `publish-readiness`. Emit `geo_audit_handoff/1` YAML if downstream skill requested.

## Output Template

Every delivery follows `skill-expertise/output_template.md` (locked). Sections in fixed order: Summary, Findings by Severity, Handoff. Validation Gate failures block template rendering; see template for fallback handling.

## Downstream Handoff Contract

Downstream skills may request `geo_audit_handoff/1` YAML:

- `datasource_name` — the audited data source.
- `findings` — array; each entry has `g_id` (G1-G6), `field`, `current_role`, `recommended_role`, `severity`, `evidence` (string), `sample_size`, `verified` (boolean).
- `summary_counts` — object with `critical`, `warning`, `note`, `info` integer counts.
- `verified` — true if all findings sample sizes ≥ 1000, false otherwise.
- `notes` — optional free text.

Downstream skills refuse unknown schema versions.

**Status: speculative.** This schema is designed for downstream consumption but has not been verified against a live invocation of `worksheet-builder`, `extract-optimizer`, or `publish-readiness`. Do not claim a confirmed round-trip handoff to the user; state that the YAML is offered for a downstream skill to consume if it recognizes the schema.

## Error Handling

| Situation | Response |
|---|---|
| No geographic fields detected | Report cleanly: no geographic fields in this data source; nothing to audit. |
| Sampling returns zero rows | Report data source appears empty or extract disconnected; refresh and re-invoke. |
| Sampling partial (some fields returned, others failed) | Proceed with the fields that returned. Flag failed fields as sampling failed: not audited. |
| Extract-filter skewing sample | If extract has filters, note extract filters may skew rates; verify against unfiltered source if possible. |
| Custom-polygon or spatial-file connector encountered | Refuse per Edge-Case Boundary. Route to Tableau spatial-file docs. |
| RTL/CJK city names encountered | Handled via G2/G3. Note the language caveat when >5% of the field is non-Latin. |
| Wide workbook (100+ fields, some with roles) | Batch `list-available-fields` in groups of ~10 with inline progress notes. |
| User asks to fix roles automatically | Refuse: Desktop UI action, provide right-click steps. |
| User asks to build a map | Route to `worksheet-builder` by exact slug. |
| User asks for map performance tuning | Route to `extract-optimizer` by exact slug. |
| Symptom doesnt match G1-G6 | Say the symptom is outside the G1-G6 checks and point to Desktop's unknown-location indicator (Map > Edit Locations) to inspect it. |
| Validation Gate fails V1 (finding without G-ID) | Drop the finding. Never render an unlabeled geographic finding. |
| Validation Gate fails V2 (severity off-rubric) | Recompute severity from rubric. If ambiguous, pick the higher severity. |
| Validation Gate fails V3 (no sample size) | Flag the finding as unverified rather than dropping. |

## Common Mistakes to Avoid

- Inventing a G7 check when the symptom doesnt fit. Say it's outside G1-G6 and give the Map > Edit Locations path.
- Firing repeated `get-summary-data` calls per check. Batch once per field.
- Drifting into map design or performance. Refuse and route.
- Skipping the Validation Gate. Every finding must pass V1, V2, V3 before delivery.
- Rendering findings without G-IDs. HC#2 requires citation.
- Chaining alternates past the first. HC#7 caps at one.

## Known Limitations

- **Cannot see rendered map output.** Findings inferred from field metadata plus sampling. This directly limits G2 and G3: neither check can read Tableaus actual Unknown/Ambiguous geocoding-resolution status, since no tool exposes it. Both report an estimated rate from a format/script/ambiguous-name proxy (see `geocoding_checks.md`), labeled estimated unless the user supplies the maps own resolution count, in which case its labeled verified from map.
- **Cannot fix role assignments.** Right-click Desktop UI only.
- **No RTL/CJK-specific pattern beyond unmatched-rate detection.** Handled via G2/G3, not a dedicated check.
- **Sample size limited by `get-summary-data` default.** Very large tables produce rate estimates, not exact rates.

## MCP Skill Mapping

No direct MCP equivalent. Desktop-agent-native spatial audit skill.

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
