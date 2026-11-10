---
name: join-and-relationship-advisor
description: "Use when the user says 'Join or relationship?', 'why is my measure doubling?', 'check cardinality', 'grain check'. Recommends a join or a relationship for two tables and checks grain and cardinality, flagging measures that would double. Advisory only."
---

# Join and Relationship Advisor

## When to use (full trigger detail)

Recommend join versus relationship, grain, and cardinality choices for a multi-table Tableau data source. Advisory-only. Reads workbook via list-workbook-datasources, list-available-fields, and get-summary-data. Diagnoses row-explosion and fanning risk against measures actually placed on shelves. Scoped to two-table pairs. Triggers on recommend relationships, join or relationship, why is my measure doubling, grain check, cardinality check, fanning problem. Do NOT trigger for connection setup (use data-source-connector), row-level data quality (use data-quality-review), LOD calc authoring (use calc-writer), model documentation (use data-model-documenter), or change tracking (use workbook-auditor).

## Purpose

Recommend join versus relationship, grain, and cardinality choices for a multi-table Tableau data source. Diagnose the three predictable failure modes: wrong join-vs-relationship choice, mismatched cardinality causing row explosion, and unresolved fanning that doubles measures. Advisory-only. Scoped to two-table pairs.

## Trigger Conditions

recommend relationships, join or relationship, should this be a join, why is my measure doubling, grain check, cardinality check, why is this row-exploding, fanning problem, help me model this data source.

Do NOT trigger on: connecting to a new data source (`data-source-connector`); data-quality issues at the row level (`data-quality-review`); writing an LOD calc to fix grain (`calc-writer`); documenting the resulting model (`data-model-documenter`); tracking model changes over time (`workbook-auditor`).

## Scope Boundaries

- IN: join-vs-relationship recommendation per table pair; cardinality diagnosis (one-to-one, one-to-many, many-to-many); referential integrity assumption; grain implications for measures; row-explosion prediction; fanning-risk diagnosis on shelf-placed measures.
- OUT: creating relationships (Desktop UI); joins beyond two-table pairs; LOD calc authoring to fix grain (`calc-writer`); data-quality issues (`data-quality-review`); model documentation (`data-model-documenter`); change tracking (`workbook-auditor`).

### Edge-Case Boundaries

| Edge Case | Handling |
|---|---|
| Composite keys (multi-column) | Refuse. Report outside current decision tree; consult manual join-config docs. |
| Temporal-range joins (effective start/end) | Route to F5 pattern only; refuse general recommendation, LOD authoring goes to `calc-writer`. |
| Cross-DS blends (blending two existing data sources in a view) | Refuse the advisory. Not a same-DS relationship; route to manual blending docs. |
| Request to create a NEW data source that relates tables from two existing sources | Do not call this unsupported by Tableau. Tableau supports it in Desktop; the agent has no verified command for it. Say so plainly, then give Desktop steps (see Error Handling). `data-source-connector` does not create relationships, so do not route there as if it solves this. |
| Self-referencing FK loops (parent-child hierarchies) | Route to F6 pattern; recommend `{FIXED [Parent ID] : ...}` LOD via `calc-writer`. |
| Single-table data source | Refuse. Report no candidate table pairs; nothing to recommend. |
| Three-or-more-table data source | HC#2 refusal. Ask which two tables to focus on. |
| Single table named by user in a multi-table data source (e.g., grain check on Orders) | Ask which second table to check it against. Grain and cardinality are pairwise; a single table has no grain claim to make without a comparison side. Never guess the second table. |
| Cardinality unverified (sample size < 1000 rows) | Report the recommendation but flag cardinality as unverified: sample size below reliable threshold. |

## Hard Constraints

- HC#1: Advisory-only. Never creates or modifies a relationship or join. Every fix is a Desktop UI instruction.
- HC#2: Two-table cap. Data sources with three or more tables trigger a scripted refusal.
- HC#3: Cardinality inferred from `get-summary-data` sampling. Referential-integrity flags surfaced by connectors are ignored.
- HC#4: Locked decision-tree in `skill-expertise/join_vs_relationship.md`. No model interpretation at the decision point.
- HC#5: Fanning-risk fires only on measures placed on shelves. Not on every possible measure.
- HC#6: Fix routing to `calc-writer` for LOD authoring. Never authors LODs directly.
- HC#7: Validation Gate before delivery. Every recommendation must pass V1 (decision-tree row exists), V2 (fanning claims cite an F-pattern), V3 (sample size disclosed).
- HC#8: Disagreement branch is scoped. Offer at most one alternate recommendation. Never chain a second alternate; route to manual docs instead.
- HC#9: Post-fix verification loop fires only on explicit user return or handoff-YAML re-entry. Never proactively re-samples after initial delivery.

## Tools Used

- `list-workbook-datasources` — Phase 0 (enumerate DS, table count).
- `list-available-fields` (verbosity: full) — Phase 1 (enumerate fields, detect candidate keys).
- `get-summary-data` — Phase 2 (sample uniqueness ratios for cardinality inference).

Zero mutating tool calls. Zero file writes.

## Key-Detection Rules (Locked)

Deterministic key-detection precedence. Never interpret; look up.

| Precedence | Rule | Example |
|---|---|---|
| 1 | Exact-name match across tables | Orders.OrderID = Returns.OrderID |
| 2 | Name suffix `_id` or `_key` matching another tables primary field | Orders.customer_id = Customers.id |
| 3 | Table-name prefix on the key field | OrderItems.OrderID (prefix Order) = Orders.OrderID |
| 4 | User-provided key mapping (from disambiguation clarifier) | User states join on invoice_number |
| 5 | Composite key (multi-column) | Refuse per Edge-Case Boundary; out of scope |

**When multiple keys match:** Rank by precedence (1 highest). If a tie remains, ask the user to name the intended key. Never guess.

**When no keys match:** Ask user to name the key explicitly. Never invent a key by inference.

## Sample-Size Reliability Threshold

Cardinality inference from `get-summary-data` sampling is only reliable when the sample includes at least **1,000 rows per side** of the candidate key. Below that threshold:

- Report the recommendation using the locked decision tree.
- Flag cardinality as **unverified: sample size below reliable threshold (1,000 rows).**
- Do NOT downgrade severity; the recommendation stands, but the confidence label changes.

Above the threshold, report cardinality as verified with the actual COUNTD/COUNT ratios cited.

## Workflow Phases

1. **Phase 0 Intake.** Confirm target data source via `list-workbook-datasources`. If the users prompt already names two specific tables from that data source, treat that as satisfying the Phase 5 pick two narrowing and proceed directly to Phase 1 on that pair — do not refuse. Otherwise, if three+ tables, execute N-table refusal (Phase 5). If single table, execute single-table refusal per Edge-Case Boundary.
2. **Phase 1 Inventory.** Batch-call `list-available-fields` (verbosity: full) for both tables in one pass. Detect candidate keys per Key-Detection Rules precedence table. Before recommending a new LOD fix later in the workflow, scan existing calcs for one whose formula already matches an F-patterns fix signature (e.g., contains `FIXED` plus the candidate key field). If a matching calc already exists, report it instead of proposing a duplicate, and route to `calc-writer` only if the existing calc needs to be verified or adjusted.
3. **Phase 2 Cardinality Inference.** Batch two `get-summary-data` calls (one per table side) to compute COUNTD/COUNT ratios. Classify each side as one or many. Cardinality is the product.
4. **Phase 2.5 Partial-Sampling Recovery.** If sampling fails partway (extract disconnect, tool timeout on one side, empty return on either side):
   - If one side sampled successfully, proceed with recommendation but flag cardinality as **unverified: partial sampling.**
   - If neither side sampled, refuse with sampling failed on both sides; refresh extract or reconnect data source and re-invoke.
   - Never guess cardinality without at least one successful sample.
5. **Phase 3 Recommendation.** Apply `skill-expertise/join_vs_relationship.md`. One-line why this and not the other per pair.
6. **Phase 4 Fanning-Risk Diagnosis.** For every shelf-placed measure, cross-reference against recommended cardinality. Report doubling risk with the specific F-pattern (F1-F6).
7. **Phase 4.5 Validation Gate.** Before delivery, confirm all three:
   - **V1 Decision-tree row exists.** The recommendation matches a row in `join_vs_relationship.md`. If not, fall back to relationship (safer default) and note the fallback.
   - **V2 Fanning claims cite F-pattern.** Every fanning-risk claim in Phase 4 output names an F-pattern from `fanning_patterns.md` (F1-F6) or outside current pattern catalog.
   - **V3 Sample size disclosed.** Every recommendation reports either verified cardinality (with COUNTD/COUNT ratios) or unverified cardinality (with sample-size caveat).
   Failing any gate blocks delivery. Do not deliver a hedged or partially-validated recommendation.
8. **Phase 4.6 User-Disagreement Branch (conditional).** If the user disputes the recommendation after Phase 4.5 delivery:
   - Offer one alternate. For a relationship recommendation, offer the join alternate (Inner or Left per the decision-trees Prefer-Join criteria). For a join recommendation, offer the relationship alternate.
   - If the user rejects the alternate, refuse further alternatives and route to Tableaus official data-modeling documentation. Never chain a second alternate.
9. **Phase 5 N-Table Refusal (conditional).** If three+ tables, do not run the full workflow. Instead offer a lightweight triage: rank all table pairs by (a) row count on the many side (from `list-available-fields`/basic metadata, not a full sample) and (b) whether both tables in the pair have a measure currently placed on a shelf. Report the top two riskiest pairs by that ranking and ask the user to pick one (or confirm the top pair) to run the full Phase 0-4.6 workflow against. This is a ranking heuristic only — it does not substitute for the full two-table analysis, and it never samples cardinality itself. If the user does not want to narrow down, refuse: the skill handles two-table pairs only. Pick the two tables most causing the problem and re-invoke.
10. **Phase 6 Handoff.** LOD fix → `calc-writer`. Model export → `data-model-documenter`. Change tracking → `workbook-auditor`. Emit `join_handoff/1` YAML if a downstream skill has requested a machine-parseable handoff.
11. **Phase 7 Post-Fix Verification Loop (conditional).** If the user returns after `calc-writer` shipped the LOD fix and asks did the fix work (or the returning skill invocation carries `calc_handoff/1` YAML with `verified: true`):
    - Re-sample the affected measure via `get-summary-data`.
    - Compare pre-fix cardinality-inflated value against post-fix value.
    - **If the value dropped to the expected grain:** Report fanning resolved. F-pattern {Fn} fix verified. Measure now aggregates at correct grain.
    - **If the value is unchanged, NULL, or errors:** Report fanning NOT resolved. LOD applied but grain issue persists or the LOD returns wrong results, NULLs, or errors. Route to `calc-debugger` with pattern slug `{Fn}` and note the failed verification.
    - **If the value is correct but the LOD is overused or too heavy:** Route to `calc-optimizer` (its rewrites verify the new calc returns the same results as the old one).
    - **If sampling fails:** Report verification sampling failed; unable to confirm fix. Ask user to open the affected sheet in Desktop and eyeball the value.

    This closes the model → LOD → verify loop. Its the only phase that fires after the initial recommendation delivery, and only on explicit user return or handoff-YAML re-entry.

## Output Template

Every delivery follows `skill-expertise/output_template.md` (locked). Sections in fixed order: Recommendation, Cardinality, Fanning-Risk Diagnosis, Fix Path, Handoff. Validation Gate failures block template rendering; see the template file for fallback handling per V1/V2/V3.

## Downstream Handoff Contract

Downstream skills (`calc-writer`, `data-model-documenter`, `workbook-auditor`) may request a machine-parseable handoff. When requested, emit a fenced YAML block with `schema_version: join_handoff/1` and these keys:

- `table_pair` — array of two table names.
- `cardinality` — one of one_to_one, one_to_many, many_to_one, many_to_many.
- `recommendation` — one of relationship, join_inner, join_left.
- `key_pair` — array of two column names in table_pair order.
- `fanning_pattern_id` — one of F1, F2, F3, F4, F5, F6, or none.
- `suggested_lod_pattern_name` — the `calc-writer` pattern slug (e.g., `F1-fixed-lod-dedupe`) or none.
- `sample_size` — integer, rows sampled per side (or partial if one side failed).
- `verified` — true if sample size ≥ 1000, false otherwise.
- `notes` — optional free text.

Downstream skills should refuse unknown schema versions (`join_handoff/2` and up) rather than guessing at forward-compatibility.

## Handoff Availability (Graceful Degradation)

This skill may ship without the skills it hands off to (`calc-writer`, `calc-debugger`, `calc-optimizer`, `data-source-connector`, `data-model-documenter`, `workbook-auditor`, `data-quality-review`). Never make a handoff the only path to a result:

- Before naming a skill in the Fix Path or Handoff section, check that it is available. If it is, route as written.
- If it is not available, do not name it and do not say a skill is missing. Give the next step inline in plain language: for an LOD fix, describe the calculation (for example, a FIXED LOD at the key's grain) and the Desktop steps to add it; for a wrong-result or heavy LOD, describe what to check or simplify; for documentation or change tracking, say it is outside this check and stop.
- Still render every section of the output template. Replace the skill-specific trigger line with the inline step.
- Emit the `join_handoff/1` YAML only when a downstream skill has actually requested it.

## Error Handling

| Situation | Response |
|---|---|
| Three or more tables | N-table refusal (Phase 5). Ask which two tables to focus on. |
| Single-table data source | Refuse: no candidate table pairs; nothing to recommend. |
| No candidate keys detected by name pattern | Ask user to name the intended key pair explicitly. Never invent a key. |
| Sampling returns zero rows | Report data source appears empty or extract disconnected; refresh and re-invoke. |
| Sampling partial (one side failed) | Phase 2.5 recovery. Proceed with recommendation but flag cardinality as unverified: partial sampling. |
| Extract-filter skewing sample | If extract has filters and sampled cardinality diverges from expected schema pattern, note extract filters may skew cardinality; verify against unfiltered source if possible. |
| Key collision (both sides look like id) | Ask user to name the intended key. Never guess when Precedence 1 produces multiple matches. |
| Composite-key detection | Refuse per Edge-Case Boundary. Route to manual join-config docs. |
| User asks to just fix it | Refuse: Desktop UI action, not tool-accessible. Here are the steps. |
| User asks to create a new data source relating table A to table B (same or different sources) | Capability gap in the agent, not a Tableau limitation. State that plainly. Give exact Desktop steps (**Data > New Data Source**, add each table, relate on the named key) with table and field names in bold. Offer to read the workbook back once the user is done. Report the turn as Blocked, not Done. |
| Named table or data source is not in `list-workbook-datasources` | Do not conclude it is unreachable. Ask where it lives (file path, published data source name, or another workbook) before anything else. |
| A handoff target skill is not available | Degrade gracefully per Handoff Availability: give the next step inline, do not name the missing skill, still render every template section. |
| About to describe a gap | Say "I couldn't find a command for that", never "Tableau can't do that". One empty search does not prove a feature is absent. |
| User asks for the LOD calc | Route to `calc-writer` by exact slug with the verbatim trigger phrase and F-pattern name. |
| Validation Gate fails V1 (no decision-tree row) | Fall back to relationship (safer default). Note the fallback explicitly. |
| Validation Gate fails V2 (fanning claim without F-pattern) | Drop the fanning claim from output. Never render an unlabeled fanning warning. |
| Validation Gate fails V3 (no sample size) | Do NOT deliver. Report the sampling failure and ask user to refresh extract or re-invoke. |
| Post-fix verification: LOD applied, fanning resolved | Report fanning resolved. F-pattern {Fn} fix verified. Close the loop. |
| Post-fix verification: LOD applied, fanning persists, or LOD returns wrong results, NULLs, or errors | Report LOD applied but grain issue persists. Route to `calc-debugger` with pattern slug `{Fn}` and note the failed verification. |
| Post-fix verification: LOD correct but overused or too heavy | Route to `calc-optimizer`. |
| Post-fix verification: sampling fails | Report verification sampling failed; unable to confirm fix. Ask user to open the affected sheet in Desktop and eyeball the value. |

## Common Mistakes to Avoid

- Trusting connector referential-integrity flags. Sample the data.
- Firing fanning diagnosis on every measure in the data source. Only on shelf-placed measures.
- Extending to three-plus tables. Refuse and route.
- Authoring the LOD. Refuse and route to `calc-writer`.
- Skipping the Validation Gate. Every recommendation must pass V1, V2, V3 before delivery.
- Guessing cardinality when sampling fails. Flag unverified rather than fabricating.
- Chaining alternates past the first. HC#8 caps at one.

## Known Limitations

- **Sample-size floor at 1,000 rows.** Below threshold, cardinality is reported as unverified.
- **Composite keys out of scope.** Refused per Edge-Case Boundary.
- **Cross-DS blends out of scope.** Refused per Edge-Case Boundary.
- **Cardinality inference depends on sampling.** Extract filters may skew results.

## MCP Skill Mapping

No direct MCP equivalent. Desktop-agent-native model-advisory skill.

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
