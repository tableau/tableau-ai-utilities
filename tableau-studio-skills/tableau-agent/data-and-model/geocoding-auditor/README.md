# Geocoding Auditor

Audits a Tableau workbook's geocoded fields for role-assignment mistakes, unmatched-location rates, and ambiguity that silently break maps. Read-only. Every fix is a Desktop UI right-click instruction.

**Example:** You point it at a workbook with a "City" field that's actually storing zip codes. G1 Role Mismatch fires (Warning). Also flags 22% of that field's values as Unknown (G2 Critical). Recommends role change to Zip Code and a data-quality follow-up.

## What it does

Runs six locked checks (G1-G6) covering role mismatches, unmatched and ambiguous rates, wrong-country resolution, missing hierarchy, and role-vs-datatype conflicts. Novel domain: no other skill in the portfolio covers spatial-role hygiene.

## When to use it

- "Geocoding audit."
- "Why won't my cities match?"
- "Unknown locations across my map."
- "Check geographic roles."
- "Why is my map wrong?"

## When NOT to use it

- Building a map (use `worksheet-builder`).
- Map interaction design (use `viz-planner`).
- Performance on high-mark maps (use `extract-optimizer` or `publish-readiness`).
- Recommending which cities/countries to include (business decision).

## The Six Checks

- **G1 Role Mismatch:** field's current geographic role doesn't match its actual values (city role on zip data, etc.).
- **G2 High Unmatched Rate:** >15% Critical, 5-15% Warning, <5% Info.
- **G3 High Ambiguous Rate:** shared names resolving to wrong country, same thresholds.
- **G4 Wrong Country Resolution:** "Springfield" resolving to the wrong country because no Country context is present.
- **G5 Missing Hierarchy:** Country present but no State/City for drill.
- **G6 Role-vs-Datatype Conflict:** geographic role assigned to a Number field or vice versa.

## What you get back

- Severity-ranked findings grouped Critical → Warning → Note → Info.
- Each finding: check ID, field, current role, recommended role, evidence, Desktop UI fix.
- Handoff line if the follow-up is map-building or performance tuning.

## Limitations

- Cannot see rendered map output. Findings inferred from field metadata plus sampling.
- Cannot fix a role assignment. Right-click Desktop UI only.
- Cannot detect visual map issues (clipping, layer order, background style).
- No custom-polygon or spatial-file validation.
- Sample size limited by `get-summary-data` default; unmatched/ambiguous rates are estimates on very large tables.
