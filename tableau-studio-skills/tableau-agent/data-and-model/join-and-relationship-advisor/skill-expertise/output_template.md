# Output Template (Locked)

Deterministic output shape. Every delivery renders these sections in this order. Never skip a section; render "None applicable" if a section has nothing to report.

## Template

````markdown
## Recommendation

- **Table pair:** {table_1} ↔ {table_2}
- **Model choice:** {relationship | join_inner | join_left}
- **Key:** {table_1}.{key_column} = {table_2}.{key_column}
- **Why this:** {one_line_rationale_from_decision_tree}

## Cardinality

- **Classification:** {one_to_one | one_to_many | many_to_one | many_to_many}
- **Evidence:** {table_1_side} = {ratio_1} ({one | many}); {table_2_side} = {ratio_2} ({one | many})
- **Sample size:** {N_rows} per side (verified) OR {N_rows} per side (unverified: below 1,000 threshold) OR partial sampling (only {side} completed).

## Fanning-Risk Diagnosis

For each shelf-placed measure:
- **{measure_name}** — {no_risk | risk_confirmed}. {If risk_confirmed: cites F-pattern (F1-F6) with specific "SUM([X]) will double because ..." format.}

Render "No measures placed on shelves; fanning diagnosis skipped." if nothing to check.

## Fix Path

- **For the model change:** {Desktop UI steps: Data → Data Source page → drag/relate/join dialog}.
- **For LOD fixes (if fanning present):** Route to `calc-writer` with pattern name `{Fn-pattern-slug}` and verbatim trigger phrase.
- **For manual override:** {none | user_disagreement_alternate: one alternate offered per HC#8}.

## Handoff (if applicable)

- **LOD fix next?** Trigger `calc-writer` with: "author {pattern_slug} on {datasource_name}."
- **Model export next?** Trigger `data-model-documenter` with: "document the data model for {datasource_name}."
- **Track model changes?** Trigger `workbook-auditor` with: "snapshot the data model for {datasource_name}."
- **Not sure what's next?** No handoff. Skill's job ends at recommendation delivery.

## Post-Fix Verification (Phase 7, conditional)

Rendered only when Phase 7 fires (user returns after LOD fix, or handoff-YAML re-entry).

- **Fix applied:** {F-pattern name and LOD slug}.
- **Pre-fix measure value:** {value_before}.
- **Post-fix measure value:** {value_after}.
- **Verification result:** {resolved | not_resolved | sampling_failed}.
- **Next step:** {none | route to calc-debugger (wrong, NULL, or error results) | route to calc-optimizer (overused or heavy LOD) | manual Desktop eyeball}.

If Phase 7 did not fire, this section does NOT render. Do not include an empty Post-Fix Verification section on initial delivery.

## Handoff YAML (optional, schema_version join_handoff/1)

Only render if a downstream skill has requested a machine-parseable handoff.

```yaml
schema_version: join_handoff/1
table_pair: [{table_1}, {table_2}]
cardinality: {one_to_one | one_to_many | many_to_one | many_to_many}
recommendation: {relationship | join_inner | join_left}
key_pair: [{key_1}, {key_2}]
fanning_pattern_id: {F1 | F2 | F3 | F4 | F5 | F6 | none}
suggested_lod_pattern_name: {slug | none}
sample_size: {N | partial}
verified: {true | false}
notes: {optional_free_text}
```
````

## Filling Rules

- Every `{placeholder}` must be filled or replaced with "not applicable" / "none." Never leave a placeholder in the delivered output.
- Every section header must render, even if the section has no content. This is how the user knows the check ran.
- Cardinality section always renders Sample size line, with the verified/unverified/partial label.
- Fanning-Risk section renders "No measures placed on shelves" when applicable, not silence.
- Fix Path section renders three sub-lines even when some are empty ("none applicable").
- Handoff YAML renders only when a downstream skill has requested it. Not for every delivery.

## What NOT to Render

- Tool names (`list-workbook-datasources`, `get-summary-data`). Stay user-facing.
- Internal reference-file names or paths (`join_vs_relationship.md`, `fanning_patterns.md`).
- Grader IDs, validation-gate IDs, or hard-constraint IDs.
- Hedged language ("might be many-to-many," "could cause fanning"). Cardinality is verified/unverified/partial; fanning is confirmed via F-pattern or absent.

## Refuse to Deliver on Validation Gate Failure

If Phase 4.5 fails V1, V2, or V3, do NOT render this template. Instead:

- **V1 fail (no decision-tree row):** Render only the relationship fallback with the "safer default" note.
- **V2 fail (fanning claim without F-pattern):** Drop the fanning claim; render the rest of the template normally.
- **V3 fail (no sample size):** Do NOT deliver. Report the sampling failure and ask user to refresh/re-invoke.

The Validation Gate is a hard block, not a soft warning.
