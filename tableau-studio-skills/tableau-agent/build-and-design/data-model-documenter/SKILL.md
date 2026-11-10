---
name: data-model-documenter
description: "Use when the user says 'Document this data model', 'export the tables and relationships', 'share this data model'. Exports a data source's model (tables, relationships, join conditions, calc dependencies) to a shareable markdown file. Read-only plus one file."
---

# Data Model Documenter

## When to use (full trigger detail)

Export a Tableau data sources logical model (tables, relationships, join conditions, calc-to-field dependencies) to a shareable markdown file. Read-only plus one file write per run. Uses list-workbook-datasources, list-available-fields, get-workbook-inventory, and one get-summary-data sample per table for row-count estimation. Writes to a fresh filename (increments _v2, _v3 on collision) to match CSV BOM overwrite discipline. Triggers on document this data model, export data model, share this data model, document the data source structure, export the tables and relationships, make a data model doc, data model export. Do NOT trigger for field-meaning documentation (use data-scribe), change tracking over time (use workbook-auditor), model recommendations (use join-and-relationship-advisor), connection setup (use data-source-connector), or data-content audit (use data-quality-review).

## Purpose

Export a Tableau data sources logical model (tables, relationships, join conditions, calc-to-field dependencies) to a shareable markdown file. The model lives inside the workbook and cannot easily be shared with anyone who doesnt open Tableau. Read-only plus one file write per run.

## Trigger Conditions

document this data model, export data model, share this data model, document the data source structure, export the tables and relationships, make a data model doc, data model export.

Do NOT trigger on: documenting what individual fields mean (`data-scribe`); tracking what changed in the model over time (`workbook-auditor`); recommending changes to the model (`join-and-relationship-advisor`); connecting a new data source (`data-source-connector`); auditing the model for issues (`data-quality-review` or `join-and-relationship-advisor`).

## Scope Boundaries

- IN: exporting the logical model of one data source per run: table inventory with row-count estimates, relationship map with cardinality and join conditions, calc-dependency graph, field-list per table with datatypes. Output as a single markdown file. One-to-one export (current state), no diff.
- OUT: field-meaning documentation (`data-scribe`); change-over-time diffing (`workbook-auditor`); model recommendations (`join-and-relationship-advisor`); connection setup (`data-source-connector`); data-content audit (`data-quality-review`); publishing the doc anywhere (Desktop-only file write); more than one data source per run; parameter reference resolution (parameters labeled Not Extractable, no reference tracing).

### Edge-Case Boundaries

| Edge Case | Handling |
|---|---|
| Multi-source workbook | Ask which source. Refuse HC#5 if user says all. One DS per run. |
| Federated multi-source data source | Refuse. |
| Blended data sources | Refuse. Blending is query-time, not model-time. Not applicable to Documenter scope. |
| Partial `list-available-fields` failure | Proceed with returned fields. Flag failed tables as not extractable this run: tool failure. |
| Calc-formula parse failure (syntax broken) | List the calc with formula text but empty References list. Note unable to parse. |
| Target path unwritable (permissions, disk full) | Refuse: report the specific write failure. Ask user to specify alternate path. |
| Sets, hierarchies, parameters | Labeled Not Extractable. Do NOT attempt reference resolution. |
| Sample size below 1,000 rows per table | Report row count as estimate; flag as unverified: sample size below reliable threshold. |
| Very wide workbook (>100 fields, >20 tables) | Batch `list-available-fields` in groups of ~10 with inline progress notes. |
| Data source with >10 relationship pairs | Batch cardinality sampling (`get-summary-data` per pair) in groups of ~5 with inline progress notes. |
| Logical table has zero shelf placements anywhere in the workbook | Row count and cardinality for that table are not extractable: no worksheet exposes this table for sampling. Do not place a field to force sampling. |

## Hard Constraints

- HC#1: Read-only plus single write. Uses only read tools plus one `Write` call for the output file.
- HC#2: Fresh-filename discipline. If the target path exists, increment `_v2`, `_v3`.
- HC#3: Current-state export only. No diff, no snapshot, no history. Route to `workbook-auditor` for change tracking.
- HC#4: Locked output template in `skill-expertise/output_template.md`. Deterministic output.
- HC#5: One data source per run. Multi-source workbooks require repeated invocations.
- HC#6: Refuse out-of-scope questions by exact slug.
- HC#7: Validation Gate before delivery. Every export must pass V1 (template compliance), V2 (file write succeeded), V3 (row counts + Not Extractable section rendered).
- HC#8: Disagreement branch is scoped. If user disputes the output, offer one alternate (verbose vs. concise). Never chain a second alternate; route to Tableau documentation docs.
- HC#9: Parameters are out of scope for calc parsing. Detected calcs that reference parameters get the reference listed as `[parameter name] (parameter — out of scope)` rather than resolved.

## Tools Used

- `list-workbook-datasources` — Phase 0 (enumerate DS, identify target).
- `get-workbook-inventory` — Phase 1 (batched inventory).
- `list-available-fields` (verbosity: full) — Phase 1 (per-table field enumeration).
- `get-summary-data` — Phase 3 (one COUNT per table for row-count estimate; also one COUNTD/COUNT sample per candidate key pair for cardinality inference per relationship, per Cardinality Inference below).
- `Write` — Phase 5 (single file write to disk).

Zero mutating tool calls on the workbook. One file write per run.

## Sample-Size Reliability Threshold

Row-count estimates via `get-summary-data` are reliable when the sample includes at least **1,000 rows**. Below that threshold:

- Report the row count as an estimate.
- Flag as **unverified: sample size below reliable threshold (1,000 rows).**
- Do not suppress the finding.

## Cardinality Inference (Locked)

For every relationship pair reported in the Relationship Map, cardinality and referential integrity (RI) are empirically sampled, not guessed — this mirrors `join-and-relationship-advisor`s method:

- Compute `COUNTD(key) / COUNT(*)` via `get-summary-data` on each side of the candidate join key.
- Ratio close to 1.0 → that side is one. Ratio well below 1.0 → that side is many. Cardinality is the product (one-to-one, one-to-many, many-to-one, many-to-many).
- RI (referential integrity) is reported as Unknown unless the connector/model explicitly asserts it — this skill does not attempt to verify orphan keys; report Unknown rather than guessing Yes.
- Apply the same 1,000-row Sample-Size Reliability Threshold used for row counts. Below threshold, label the cardinality as unverified: sample size below reliable threshold (1,000 rows) rather than suppressing it.
- If no candidate key is detectable between two related tables (no name match, no user-resolvable key), report cardinality as not extractable: no candidate key identified rather than fabricating a value.
- This skill reports cardinality as a factual sample result only. It does not recommend a join-vs-relationship model choice — that recommendation, plus fanning-risk diagnosis, belongs to `join-and-relationship-advisor`; route there if the user asks should this be a join or relationship.
- **Batching for many relationship pairs.** For data sources with more than ~10 relationship pairs, batch cardinality sampling in groups of ~5 pairs with inline progress notes, mirroring the wide-workbook field-enumeration batching already used for `list-available-fields`. Never fire all pair samples in one unbatched burst on a wide multi-table model.

## Calc-Parsing Precedence (Locked)

Parse calc formula text outer to inner. Never re-order. Deterministic output.

| Order | Layer | Signature | Handling |
|---|---|---|---|
| 1 | Nested calcs | `[calc_name]` where calc_name is another calculated field | Resolve one level of nesting. Deeper nesting reports as `[calc_name] (nested)`. |
| 2 | LOD-referenced dimensions | Inside `{FIXED [...] : ...}`, `{INCLUDE [...] : ...}`, `{EXCLUDE [...] : ...}` | Track LOD-context dimensions separately from raw field refs. Report as `[dim_name] (LOD context)`. |
| 3 | Table-calc referenced fields | Inside `WINDOW_*`, `RUNNING_*`, `PREVIOUS_VALUE` | Report as `[field_name] (table calc)`. |
| 4 | Raw field references | Bare `[field_name]` at row level | Report as `[field_name]`. |
| 5 | Parameters (HC#9 out of scope) | `[parameter_name]` where field is a parameter | Report as `[parameter_name] (parameter — out of scope)`. Do NOT resolve or trace. |

**Nested calc depth:** Resolve one level. Deeper nesting is documented as (nested) without recursion. Prevents infinite loops and keeps output bounded.

## Workflow Phases

1. **Phase 0 Intake.** Confirm target data source via `list-workbook-datasources`. Confirm output path (default: `{datasource-name}_model.md` next to the workbook). If multi-source, ask which; refuse all.
2. **Phase 1 Inventory.** Batch-call `list-workbook-datasources`, `get-workbook-inventory`, `list-available-fields` (verbosity: full). Read tables, fields, relationships, calc formulas.
3. **Phase 2 Calc Dependency Graph.** Parse formula text per Calc-Parsing Precedence table. Build `{calc name} → [ordered references list]` map.
4. **Phase 3 Row-Count and Cardinality Estimation.** One `get-summary-data` COUNT per table for row counts. For every relationship pair, one COUNTD/COUNT sample per side per Cardinality Inference above. Cache both. Apply sample-size threshold labeling to each independently.
5. **Phase 4 Assembly.** Fill `skill-expertise/output_template.md`. Sections: metadata, table inventory, relationship map, calc-dependency graph, appendix, Not Extractable.
6. **Phase 4.5 Validation Gate.** Before write, confirm all three:
   - **V1 Template compliance.** Every locked section renders; no placeholder `{...}` remains; Not Extractable section renders even if empty.
   - **V2 File-write pre-check.** Target path is writable (permissions, disk space). If not, refuse per Error Handling.
   - **V3 Row-count + Not-Extractable coverage.** Row counts include verified/unverified labels; Not Extractable lists sets, hierarchies, parameters explicitly (with none surfaced if empty).
   Failing any gate blocks the write.
7. **Phase 4.6 Disagreement Branch (conditional).** If user disputes the output shape after delivery:
   - Offer one alternate rendering (typically verbose vs. concise, or with/without appendix).
   - If rejected, route to Tableau documentation. Never a second alternate.
8. **Phase 5 Write to Disk.** Write to target path. If collision, increment `_v2`, `_v3`. Report actual output path.
9. **Phase 6 Handoff.** Field-meaning → `data-scribe`. Change tracking → `workbook-auditor`. Model recommendation → `join-and-relationship-advisor`. Emit `model_doc_handoff/1` YAML if downstream skill requested.

## Output Template

Every delivery follows `skill-expertise/output_template.md` (locked). Sections in fixed order: metadata, table inventory, relationship map, calc-dependency graph, appendix, Not Extractable. Validation Gate failures block the write per template fallback handling.

## Downstream Handoff Contract

Downstream skills may request `model_doc_handoff/1`:

- `datasource_name` — the audited data source.
- `output_file_path` — actual path written (post-collision increment).
- `table_count` — integer.
- `relationship_count` — integer.
- `calc_count` — integer.
- `not_extractable` — object with `sets`, `hierarchies`, `parameters` arrays (each entry a name string; empty array if none surfaced).
- `row_counts_verified` — true if all row counts ≥ 1000 sample rows, false otherwise.
- `notes` — optional free text.

Downstream skills refuse unknown schema versions.

## Error Handling

| Situation | Response |
|---|---|
| Multi-source workbook | Ask which source. Refuse HC#5 if user says all. |
| Federated multi-source | Refuse per Edge-Case Boundary. |
| Blended sources | Refuse per Edge-Case Boundary. |
| Sampling returns zero rows | Note row-count unavailable; extract may be disconnected. Proceed with rest. Flag as unverified. |
| No candidate key detectable for a relationship pair | Report cardinality as not extractable: no candidate key identified. Never guess. |
| Cardinality sample below 1,000 rows per side | Report cardinality with unverified: sample size below reliable threshold (1,000 rows) label. Do not suppress. |
| Logical table not referenced by any worksheet shelf | Report row count and cardinality for that table/pair as not extractable: no worksheet exposes this table for sampling. Never place a field solely to enable sampling. |
| User asks for a join-vs-relationship recommendation | Route to `join-and-relationship-advisor` by exact slug. This skill reports sampled cardinality as fact, not a model recommendation. |
| Partial `list-available-fields` failure | Proceed with returned fields. Flag failed tables. |
| Calc-formula parse failure | List calc with formula; empty References; note unable to parse. |
| Calc references a field that no longer exists in the data source | This state typically arises from legacy/imported workbooks where a referenced field was later deleted — Desktops own calc authoring validates field references and blocks creating such a calc fresh. When encountered (existing workbook), apply the standard rule: list the calc with its formula text, empty References, note unable to parse: referenced field not found. |
| Target path exists | Increment filename. Report actual output path. |
| Target path unwritable | Refuse with specific error (permissions, disk full). Ask user for alternate path. |
| User asks for a diff | Refuse HC#3. Route to `workbook-auditor` by exact slug. |
| User asks for field meaning | Route to `data-scribe` by exact slug. |
| User asks for model recommendations | Route to `join-and-relationship-advisor` by exact slug. |
| User asks to document all sources | Refuse HC#5. Ask which one. |
| Validation Gate fails V1 (template incomplete) | Do NOT write. Report the specific missing section. |
| Validation Gate fails V2 (path unwritable) | Do NOT write. Refuse per unwritable path row above. |
| Validation Gate fails V3 (row counts or Not Extractable missing) | Complete the gap before writing. |

## Common Mistakes to Avoid

- Overwriting an existing output path. Increment; never overwrite.
- Documenting more than one source per run. Refuse and ask which.
- Producing a diff. Thats `workbook-auditor` territory.
- Documenting field meaning beyond datatype. Thats `data-scribe` territory.
- Attempting to resolve parameter references. HC#9 out of scope.
- Recursing deeper than one level on nested calcs. Bounded by Calc-Parsing Precedence.
- Skipping the Validation Gate. Every write must pass V1, V2, V3.
- Chaining alternates past the first. HC#8 caps at one.

## Known Limitations

- **Row-count estimates on live connections may not equal true source count.**
- **Cardinality is sampled (COUNTD/COUNT per key pair), not read from connector metadata.** RI (referential integrity) is reported as Unknown unless explicitly asserted by the connector; this skill never verifies orphan keys.
- **This skill reports cardinality as a fact, not a recommendation.** It does not advise join-vs-relationship model choice or diagnose fanning risk; route to `join-and-relationship-advisor` for that.
- **Cannot detect model changes over time** (`workbook-auditor`).
- **Cannot document field meaning beyond datatype and role** (`data-scribe`).
- **Sets, hierarchies, parameters labeled Not Extractable.** Not resolved.
- **Parameters in calcs listed as out-of-scope,** not traced.
- **Parameters created directly in Tableau Studios UI mid-session may not be visible to this skills tools** until the workbook is reloaded/refreshed at the tool layer. This is a known environment gap, not a scope decision — if a user-created parameter cant be found, say so plainly rather than reporting it as absent from the model.
- **Nested calcs resolved one level only.** Deeper nesting labeled (nested).
- **No publishing anywhere.** Desktop file write only.

## MCP Skill Mapping

No direct MCP equivalent. Desktop-agent-native model-export skill.

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
