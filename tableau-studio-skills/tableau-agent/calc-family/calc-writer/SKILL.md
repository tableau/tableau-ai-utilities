---
name: calc-writer
description: "Use when the user says 'I need a calc that...', 'write a calc for...', 'create a calc that flags...', 'make a calc that...' Writes one new Tableau calculated field from plain language, checks it against your data, and confirms it works. Not for fixing or translating existing calcs."
---

# Calc Writer

## When to use (full trigger detail)

Author a new Tableau calculated field from a natural-language ask. Single-calc-per-pass discipline by default, with an opt-in sequential multi-calc mode when the user is asked and agrees. Reads workbook via list-workbook-datasources and list-available-fields; writes via author-calc; verifies via get-summary-data. Every authored calc passes an 8-check Validation Gate (R-TYPE, R-AGG, R-LOD, R-TC, R-NULL, R-BOOL, R-PERF, R-NAME) before delivery. Signatures looked up from nested function library, never guessed. Triggers on "write this calc," "author a calc for," "I need a calc that," "create a calc for," "make a calc that." Do NOT trigger for debugging broken calcs (use calc-debugger), improving performance (use calc-optimizer), translating from SQL/Excel/DAX (use calc-translator), style/naming audits (use calc-linter), cataloging existing calcs (use calc-inventory), or ambiguous calc questions (use calc-orchestrator).

## Purpose

Author one new Tableau calculated field per run from a natural-language ask. Single-trigger discipline. Every calc passes an 8-check Validation Gate before delivery. Function signatures are looked up from the function library in `skill-expertise/`, never guessed. When another calc skill is chained, the handoff YAML (`calc_write_handoff/1`) passes the result along.

## Trigger Conditions

**Single-calc triggers (default mode):** "write this calc," "author a calc for," "I need a calc that," "create a calc for," "make a calc that," "build me a calc for," "give me a calc that."

**Multi-calc trigger (opt-in mode via HC#1 clarifier):** "write these calcs," "write me N calcs," "author several calcs," or any ask that names more than one calc in a single invocation. The skill still fires on the trigger, but HC#1s clarifier fires first ("one at a time or sequential this run?") before authoring begins.

**Adjacent-skill triggers that must NOT fire calc-writer:**

| Trigger phrase | Correct target skill |
|---|---|
| "debug this calc," "why is this calc returning NULL," "fix this broken calc" | `calc-debugger` |
| "optimize this calc," "why is this calc slow," "make this calc faster" | `calc-optimizer` |
| "translate this SQL to Tableau," "port this DAX to Tableau," "convert Excel formula" | `calc-translator` |
| "style-check my calcs," "lint my calcs," "check calc naming conventions" | `calc-linter` |
| "list all my calcs," "inventory these calcs," "catalog my calcs" | `calc-inventory` |
| "help with a calc" (ambiguous, no intent named) | `calc-orchestrator` |
| "build a dashboard," "create a viz for this calc" | `worksheet-builder` or `viz-planner` |
| "create a parameter for this calc" | Out of scope (author-parameter unreliable); route to Desktop UI. |
| "make this field a set" | Out of scope; route to Desktop UI. |
| "create a hierarchy from these calcs" | Out of scope; route to Desktop UI. |

## Scope Boundaries

- **IN:** author one new calc per run from a natural-language ask, or — when the user explicitly opts in via the HC#1 clarifier — a sequential multi-calc run authoring each named calc through the full pipeline one at a time; classify calc type (row-level, aggregate, LOD FIXED/INCLUDE/EXCLUDE, table calc); look up function signatures from `skill-expertise/` (function library files); run 8-check Validation Gate; verify output via `get-summary-data` on a scratch worksheet when the Verification Policy requires it; emit `calc_write_handoff/1` YAML only per HC#7.
- **OUT:** authoring multiple calcs without first asking the HC#1 clarifier; debugging existing calcs (`calc-debugger`); performance optimization (`calc-optimizer`); source-dialect translation (`calc-translator`); style audits (`calc-linter`); catalog exports (`calc-inventory`); parameter creation; set creation; hierarchy creation; whole-workbook migration; dashboard or worksheet building.

### Edge-Case Boundaries

| Edge Case | Handling |
|---|---|
| User asks for a calc that references a parameter | Author the calc, cite the parameter reference in the handoff as `[param_name] (parameter — cite but do not resolve)`. Do NOT attempt to create the parameter; refuse parameter creation. |
| User asks for a calc that references a set | Same as parameter: cite the set reference, refuse to create the set. |
| User asks for a calc that requires a nested calc dependency (`[Other Calc]`) that doesnt exist | Refuse the write; ask user to confirm whether to author the missing calc first (separate invocation) or use the raw fields inline. |
| User asks for a calc referencing a field that doesnt exist | Refuse: "field `[Missing Field]` doesnt exist in the target data source. Confirm the field name or point to the correct data source." Never fabricate the field. |
| User asks for a fresh parameter to be created for the calc | Refuse (author-parameter unreliable). Ask user to create the parameter manually in Desktop, then re-invoke. |
| Ambiguous calc type (could be row-level or aggregate) | Ask exactly one clarifier: "Should this aggregate across rows (SUM/AVG) or compute per row?" Never assume. |
| Sample size below 1,000 rows for verification | Report verification result but flag as "unverified: sample size below reliable threshold (1,000 rows)." Severity does not downgrade. |
| Data source has parameter-referencing calcs already (Data Scribe corruption risk) | Skip `build-and-apply-worksheet` verification; use existing scratch worksheet if one exists. Never mutate a workbook with parameter-referencing calcs via shelf-mutating tools. |
| Fresh-parameter resolution failure (author-calc cant resolve a param by bare name) | Retry once after asking user to refresh the Data pane in Desktop. If still failing, refuse with manual calc-creation instructions (platform gap). |
| Very wide data source (>100 fields) | Batch `list-available-fields` in groups of ~10 with inline progress notes. Reuse Phase 1 inventory across chained invocations in the same session rather than re-batching per call. |
| Multi-table data source (relationships or cross-join scenarios) | Confirm which logical table the calc will reference before authoring. If the calc spans two related tables, verify cardinality context in the handoff notes (calcs grain matters at query time). |
| Very narrow data source (<10 fields) | Skip the batching guidance in Phase 1; single `list-available-fields` call sufficient. |
| Tiny extract (<sample_size rows) | Sample size threshold labeling applies; report verified findings but flag confidence with "unverified: sample size below reliable threshold (1,000 rows)." |
| Ambiguous field name shared across multiple data sources | When asking which source, name each candidate source alongside the fields role/type in that source (e.g., "measure" vs. "dimension") so the user isnt just repeating the field name back — clarify with data-source names, not field names, since the field name alone doesnt disambiguate. |

## Hard Constraints

- **HC#1:** Default mode authors exactly one calc per run. If the ask names multiple calcs in one invocation, ask exactly one clarifier before starting: "I can author these one at a time (default, re-invoke per calc) or walk through all N sequentially in this run as separate single-calc passes — which would you prefer?" Never assume multi-calc mode; the user must opt in per invocation. In multi-calc mode, each calc still runs the full pipeline (Phases 0-4.6) independently and in sequence — no batching or shortcutting of field verification or the V-gate; Phase 4 verification follows the Verification Policy for each calc. A failure on one calc in the sequence does not block the others; report per-calc results.
- **HC#2:** Function signatures are looked up from `skill-expertise/INDEX.md`, never guessed. If the function isnt in the library, refuse the write; do not invent a signature.
- **HC#3:** Every authored calc passes the full 8-check Validation Gate (`skill-expertise/validation_gate.md`) before delivery. Failing any gate blocks the write.
- **HC#4:** One clarifying question maximum. If the ask is ambiguous, ask exactly one clarifier. Never chain a second.
- **HC#5:** Never fabricate field references. If a named field doesnt exist in the target data source, refuse.
- **HC#6:** Never create parameters, sets, or hierarchies. Refuse and route to Desktop UI manual creation.
- **HC#7:** Emit `calc_write_handoff/1` YAML only when the user chains to another installed calc skill or asks for it. Never include it in the normal user-facing reply.
- **HC#8:** Refuse out-of-scope questions by exact slug (six calc-family peers + `worksheet-builder`/`viz-planner` for dashboard work).
- **HC#9:** Perf advisory is advisory-only. Never rewrite the calc for performance. Detect patterns per the perf-advisory catalog, surface the recommendation in the reply with a verbatim `calc-optimizer` trigger phrase (and in `perf_advisory` when a handoff is emitted). Optimization is `calc-optimizer`s job.
- **HC#10:** Never claim quantified perf impact (specific latency, row count, or memory reduction). Perf advisory is pattern-detection only. Quantified impact comes from `calc-optimizer`, which profiles against actual data.

## Tools Used

- `list-workbook-datasources` — Phase 0 (identify target DS).
- `list-available-fields` (verbosity: full) — Phase 1 (verify field references, check for parameter-corruption risk).
- `author-calc` — Phase 3 (write the calc).
- `add-worksheet`, `delete-sheet` — Phase 4 (create/clean scratch worksheet for verification).
- `add-field` — Phase 4 (place calc on scratch worksheet Detail).
- `get-summary-data` — Phase 4 (verify calc output).
- `resolve-field` — Phase 1 fallback (disambiguate field names).

One workbook mutation per run (the authored calc, plus a scratch worksheet only when the Verification Policy calls for Phase 4). Any scratch worksheet is cleaned in Phase 5.

## Function Library (Locked Reference)

`skill-expertise/INDEX.md` catalogs ~150 Tableau Studio functions across eight categories: string, date, number, logical, aggregate, LOD, table calc, spatial. Every function has a signature, return type, LOD/TC eligibility, and version-gated status (e.g., MAKEPOINT 2019.2+, BUFFER 2024.1+, USEREMAIL 2023.3+).

Never invent a signature.

### Domain-Accuracy Assertions (Locked)

Locked Tableau behaviors (LOD order of operations, ATTR failure modes, INT vs. ROUND, Boolean aggregation, COUNT/COUNTD NULLs, DATEPARSE patterns, table-calc partitioning, spatial and USEREMAIL version gates, REGEXP escaping) live in `skill-expertise/domain_accuracy.md`. Read it before authoring any LOD, table-calc, ATTR, Boolean-aggregate, date-parsing, spatial, or REGEXP calc. Any calc that violates an assertion is caught by the Validation Gate or a perf-advisory flag, never delivered.

## Validation Gate (Locked, 8 Checks)

Every authored calc passes all applicable checks in `skill-expertise/validation_gate.md` before delivery, in this order: R-TYPE-01/02, R-AGG-01/02, R-LOD-01/02/03 (LOD only), R-TC-01/02 (table calc only), R-NULL-01, R-BOOL-01, R-PERF-01, R-NAME-01. Any failure blocks the write. If R-TYPE-01 fails, re-classify before re-authoring; other failures may need a clarifier or refusal.

## Sample-Size Reliability Threshold

`get-summary-data` verification is reliable when the scratch worksheet returns at least **1,000 rows**. Below that threshold:

- Report the verification result normally.
- Flag as **"unverified: sample size below reliable threshold (1,000 rows)."**
- Severity does not downgrade; the confidence label changes.

## Scale Tiers, Multi-Calc Mode, and Source Types

Field-count tiers (narrow to 200+ fields), row-count confidence tiers, multi-calc sequential mode, and data source type branching (extract, live, blend, federated, multi-table) are in `skill-expertise/scale_and_modes.md`. Read it for 100+ field or 1M+ row sources, multi-calc runs, or any blended, federated, or multi-table source.

## Verification Policy (When to Run Phase 4)

Run the scratch-sheet check (Phase 4) only when it is worth the extra calls:

- **Verify:** LOD (FIXED/INCLUDE/EXCLUDE), table calc, any ATTR or mixed row-level/aggregate logic, DATEPARSE or date math, type conversion, REGEXP, a nested-calc dependency, or when the user asks to check it.
- **Skip:** simple row-level calcs (arithmetic, comparisons, IF/CASE on existing fields, string concatenation) once `author-calc` succeeds and the Validation Gate passes.
- **Can't verify:** a FIXED LOD with no dimensions does not return through `get-summary-data` (platform gap). Report it as not checked in a view.
- **Never** verify on a data source with parameter-referencing calcs (shelf-mutation corruption risk); report it as not checked in a view.

Always state which happened in the reply: "Checked on N rows" or "Not checked in a view yet. Say 'check it' to verify on your data." Never imply a check that did not run.

## Workflow Phases

1. **Phase 0 Intake.** Confirm target data source via `list-workbook-datasources`. If multi-source, ask which. Parse the users natural-language ask into an intent: measure, dimension, calc-type hint, expected return type. If the ask names more than one calc, apply HC#1s clarifier before proceeding.
2. **Phase 1 Field Verification.** Call `list-available-fields` (verbosity: full). Verify every field the ask references exists. If any missing, refuse per HC#5. Check for parameter-referencing calcs already in the data source (parameter-corruption avoidance).
   - **Wide-workbook batching:** on data sources with >100 fields, batch `list-available-fields` calls in groups of ~10 with inline progress notes. Skip on <100-field sources.
   - **Inventory reuse:** if the same session already ran Phase 1 on this data source (e.g., a prior calc-writer invocation, or a chained handoff from calc-optimizer / calc-linter), reuse the cached inventory rather than re-calling. Detect this by checking whether the previous handoffs `datasource_name` matches the current target.
3. **Phase 2 Function Lookup.** For every function the calc requires, look up the signature in `skill-expertise/INDEX.md`. If missing, refuse per HC#2. If found, note the version-gated status if any.
4. **Phase 3 Author.** Call `author-calc` with the composed formula. On success, capture the returned calc name and formula text. On failure, apply error-handling table.
5. **Phase 4 Verification (conditional, per the Verification Policy).** Skip this phase for simple row-level calcs and report "not checked in a view yet." Otherwise, create a scratch worksheet (if none exists). Reference the calc on the shelf using the correct derivation prefix, determined by whether the calcs own formula already contains an aggregation:
   - **Formula has no aggregation** (plain row-level calc, e.g. `DATEDIFF(...)`, `[Sales] > 500`): Tableau applies default aggregation on shelf placement. Use `none:` for a dimension-role calc, `sum:` for a measure-role calc.
   - **Formula already contains its own aggregation** (`SUM(...)`, `AVG(...)`, an LOD `{FIXED/INCLUDE/EXCLUDE ...}`, or a table calc): the calc is fully aggregated already and has no separate per-row instance to re-aggregate. Use its native `usr:` ref — never wrap it in an additional `sum:`, which Tableau will reject as "no field named" the moment you try.
   - Either way, place the calc alone on Detail with nothing else on the shelves for verification, then call `get-summary-data`. Apply sample-size threshold labeling. If scratch worksheet creation fails, retry once; if it fails a second time, mark `verified: false`, `sample_size: "verification_skipped"`, and note the failure in the handoff rather than blocking delivery of an otherwise-passing calc.
   - **Table-calc addressing dimension:** when verifying a table calc that depends on row order (WINDOW_*, RUNNING_*, PREVIOUS_VALUE, INDEX, RANK, LOOKUP), place a continuous date pill (e.g., `[tdy:Order Date:qk]` or the appropriate continuous truncation) on Rows for the addressing dimension — never the raw discrete date field, which fails preflight as `date-field-bound-as-string`.
6. **Phase 4.4 Perf-Advisory Scan.** Pattern-match the authored calc against the perf-advisory catalog in `skill-expertise/handoff_schema.md` (PA-COUNTD-HIGH-CARDINALITY, PA-REGEXP-IN-AGGREGATE, PA-CONTAINS-IN-AGGREGATE, PA-LOD-NESTED, PA-TABLE-CALC-WHERE-LOD-WOULD-WORK, PA-CROSS-DS-BLEND, PA-DATEDIFF-IN-FILTER, PA-NESTED-IF-DEEP, PA-STRING-ARITHMETIC). This is advisory-only. Never rewrite the calc for perf; thats `calc-optimizer`s job. If severity is `note` or `warning`, tell the user in one line with the verbatim `calc-optimizer` trigger phrase. When a handoff is emitted (HC#7), also populate `perf_advisory.flags`, `perf_advisory.severity`, and `perf_advisory.recommendation`.
7. **Phase 4.5 Validation Gate.** Run all 8 checks against the authored calc. Any failure blocks delivery. If R-TYPE-01 fails, re-classify and re-author. Other failures may require clarifier or refusal.
8. **Phase 4.6 Disagreement Branch (conditional).** If user disputes the delivered calc:
   - Offer one alternate formulation (typically the next-most-natural calc type: row-level → aggregate, aggregate → LOD FIXED, or vice versa).
   - If rejected, route to Tableaus calc reference docs. Never chain a second alternate.
9. **Phase 5 Cleanup + Reply.** Delete any scratch worksheet (or leave it with the users approval). Reply with: the calc name and formula, what it does in one line, the verification status ("Checked on N rows" or "Not checked in a view yet"), and any perf note. Emit `calc_write_handoff/1` only per HC#7.

## Handoff Contract

The `calc_write_handoff/1` YAML schema is in `skill-expertise/handoff_schema.md`. Emit it only per HC#7: when the user chains to another calc skill that is installed in this session ("now optimize it", "now lint it", "add it to the inventory") or explicitly asks for it. It is not part of the normal reply. Downstream skills refuse unknown schema versions.

## Error Handling

| Situation | Response |
|---|---|
| Multi-source workbook | Ask which source. If the ask also names multiple calcs, combine with the HC#1 clarifier (one-at-a-time vs. sequential multi-calc mode) rather than asking twice. |
| Field doesnt exist in the target DS | Refuse per HC#5. Ask user to confirm field name or point to correct DS. |
| Function isnt in the library | Refuse per HC#2. Never invent a signature. |
| Ambiguous calc type | Ask one clarifier per HC#4. Never chain a second. |
| Parameter reference in the ask, parameter doesnt exist | Refuse parameter creation per HC#6. Ask user to create manually in Desktop, then re-invoke. |
| Fresh-parameter resolution fails (author-calc cant resolve param by bare name) | Retry once after Data pane refresh. If still failing, refuse with manual calc-creation instructions. |
| `author-calc` returns "syntax error" | Diagnose via V-gate rules; if fixable, re-author with corrected formula; else refuse and hand off to `calc-debugger`. |
| `author-calc` returns success but `get-summary-data` verification shows wrong output | Re-run V-gate; if V-gate says calc is valid but semantics dont match ask, offer one alternate formulation per Phase 4.6. |
| Data source has parameter-referencing calcs (corruption risk) | Skip `build-and-apply-worksheet`; use existing scratch worksheet. Never shelf-mutate. |
| Validation Gate R-TYPE-01 fails | Re-classify calc type; re-author once. If second attempt fails, refuse. |
| Validation Gate any other rule fails | Report the specific rule ID and evidence; block delivery. |
| User asks for multiple calcs in one invocation | Ask the HC#1 clarifier (one-at-a-time vs. sequential multi-calc mode this run). Proceed per the users choice; never assume. |
| Field or parameter reference resolves at Phase 1 but fails to resolve at `author-calc` time (stale/renamed mid-session) | Retry once. If still failing, refuse with "field/parameter `[X]` no longer resolves; confirm it wasnt renamed or removed, or refresh the Data pane and re-invoke." Do not silently substitute a similarly-named field. |
| User asks for debugging/optimization/translation/lint/inventory | Route to exact slug per HC#8. |
| `author-calc` hangs/times out twice in a row (no dialog blocking, session confirmed reachable) | Stop retrying after the second timeout. Check whether the calc was actually created server-side despite the timeout (search the field inventory for the intended caption) before assuming failure. If genuinely not created, hand the user exact manual creation steps (caption, formula, datatype, role) for Desktops Create Calculated Field dialog, and explicitly ask them to confirm once done so verification can proceed — never let the handoff trail off without that ask. Confirmed not connection-type-dependent: the same hang recurred identically on both a live connection and its extracted version of the same data source, and survived a full Desktop restart — treat this as a standing environment reliability gap, not a live-connection-latency or stale-session issue. |

## Common Mistakes to Avoid

- Inventing a function signature that isnt in `INDEX.md`. HC#2 hard-bans.
- Authoring a calc without running the full 8-check V-gate. HC#3 hard-bans.
- Fabricating field references. HC#5 hard-bans.
- Attempting to create a parameter. HC#6 hard-bans; route to Desktop UI.
- Chaining clarifying questions past the first. HC#4 caps at one.
- Emitting the handoff YAML when no calc skill asked for it, or showing it in the normal reply. HC#7 limits it to chained runs.
- Building a scratch sheet for a simple row-level calc. The Verification Policy skips it.
- Implying a calc was checked when Phase 4 did not run. Always state the verification status.
- Hedging on calc type ("this might be an LOD"). Classify or refuse.
- Delivering a calc that references a non-existent nested calc. Refuse per Edge-Case Boundary.
- Treating an `author-calc` "success" response as proof only the intended calc changed. If the returned calc name, formula, or datasource doesnt match what was requested, stop and verify before delivering — `author-calc` can silently touch the wrong calc on a workbook with caption collisions or stale field references; never assume success implies isolation.
- Assuming multi-calc mode by default. HC#1 requires the clarifier every time multiple calcs are requested in one invocation.

## Known Limitations

- Default mode is one calc per invocation; sequential multi-calc mode requires explicit user opt-in per HC#1 and still runs each calc through the full pipeline (no shortcuts). True batch authoring (parallel writes, shared V-gate pass) remains out of scope.
- Parameter creation is out of scope (platform gap).
- Set and hierarchy creation are out of scope.
- Function library reflects Tableau Desktop 2026.x GA.
- Fresh-parameter resolution has a documented one-retry pattern (platform gap).
- Sample-size threshold labeling requires ≥1,000 rows for verified; smaller samples flag as unverified.
- Simple row-level calcs are not checked in a view by default (Verification Policy); users can ask for a check.
- Version-gated functions (MAKEPOINT 2019.2+, BUFFER 2024.1+, USEREMAIL 2023.3+) noted inline; older Desktop versions may not support them.

## MCP Skill Mapping

`tableau-calc-engine` (Cloud) is the analog. Calc Writer is the Desktop-agent-native single-trigger authoring peer.

## Relationship to Other Skills

- **Peer to `calc-debugger`, `calc-optimizer`, `calc-translator`, `calc-linter`, `calc-inventory`.** Single-trigger discipline enforced by explicit Do NOT trigger clauses.
- **Orchestrator:** `calc-orchestrator` routes ambiguous asks to Calc Writer when intent is clearly "author new."
- **Downstream handoff (only when chained, per HC#7):** `calc_write_handoff/1` YAML consumable by `calc-optimizer` ("now optimize it"), `calc-linter` ("now lint it"), `calc-inventory` ("now include this in the catalog").
- **Upstream:** `viz-planner` and `worksheet-builder` may invoke Calc Writer during dashboard design when a calc is needed.
- **Sibling to non-calc skills:** never authors a field alias (thats a Desktop UI action); never modifies the data model (`join-and-relationship-advisor`); never documents field meaning (`data-scribe`).

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
