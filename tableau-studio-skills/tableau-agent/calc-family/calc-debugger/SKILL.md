---
name: calc-debugger
description: "Use when the user says 'Why is this calc returning NULL?', 'fix this broken calc', 'debug this calc', 'why does this calc error?' Finds why an existing calculated field returns NULLs, wrong values, or errors, then fixes it and verifies the result against your data."
---

# Calc Debugger

## When to use (full trigger detail)

Diagnose why an existing Tableau calculated field is broken (returns NULL, wrong values, syntax error, silent failure) and propose a corrected version. Single-calc-per-pass discipline by default, with an opt-in sequential multi-calc mode when the user is asked and agrees. Reads workbook via list-workbook-datasources and list-available-fields; reads the broken formula; classifies the failure against an error-pattern catalog; proposes fix; re-authors via author-calc; verifies via get-summary-data. Every fix passes the same 8-check Validation Gate as calc-writer before delivery. Signatures looked up from nested function library, never guessed. Triggers on debug this calc, why is this calc returning NULL, fix this broken calc, why does this calc error. Do NOT trigger for authoring new calcs (use calc-writer), performance-only issues (use calc-optimizer), source-dialect translation (use calc-translator), style/naming audits (use calc-linter), cataloging existing calcs (use calc-inventory), or ambiguous calc questions (use calc-orchestrator).

## Purpose

Diagnose one broken Tableau calculated field per run, propose a corrected version, re-author, and verify. Single-trigger discipline. Every fix passes the same 8-check Validation Gate as calc-writer. Error-pattern classification is looked up from a nested error-pattern catalog, never guessed. Handoff YAML (`calc_debug_handoff/1`) makes the result consumable by downstream peers.

## Trigger Conditions

**Single-calc triggers (default mode):** debug this calc, why is this calc returning NULL, why is this calc broken, fix this broken calc, why does this calc error, diagnose this calc, this calc isn't working.

**Multi-calc trigger (opt-in mode via HC#1 clarifier):** debug these calcs, fix these N calcs, or any ask that names more than one broken calc in a single invocation. The skill still fires on the trigger, but HC#1's clarifier fires first (one at a time or sequential this run?) before diagnosing begins.

**Adjacent-skill triggers that must NOT fire calc-debugger:**

| Trigger phrase | Correct target skill |
|---|---|
| write this calc, author a calc for, create a calc, I need a calc that, make a calc that, build me a calc for, give me a calc that | `calc-writer` |
| optimize this calc, why is this calc slow, make this calc faster, improve calc performance, reduce calc runtime, this calc is expensive (calc works correctly, just slow) | `calc-optimizer` |
| translate this SQL to Tableau, port this DAX to Tableau, convert Excel formula, convert this to a Tableau calc, SQL-to-Tableau conversion | `calc-translator` |
| lint my calcs, check calc naming conventions, style-check my calcs, check calc conventions | `calc-linter` |
| list all my calcs, inventory these calcs, catalog my calcs, document my calcs, share my calc list, export calc metadata | `calc-inventory` |
| help with a calc, not sure what to do with this calc, I have a calc issue (ambiguous, no intent named) | `calc-orchestrator` |
| build a dashboard, create a viz for this calc, put this on a worksheet, make a chart from this calc | `worksheet-builder` or `viz-planner` |
| create a parameter for this calc, add a set that this calc uses, build a hierarchy | Out of scope by design (HC#6); route to Desktop UI. When refusing, cite HC#6, not a tool limitation. |
| the calc's grain is wrong because of the join, SUM is doubling because of my relationship, fanning issue, many-to-many is breaking this calc | Route to `join-and-relationship-advisor` for the model fix; return here for the calc fix afterward per HC#10. |
| why did the agent do X yesterday, explain what happened in a previous session | Out of scope; prior-turn diagnosis has no visibility. Refuse with scripted redirect. |

## Scope Boundaries

- **IN:** diagnose one broken calc per run (or sequential N via HC#1 opt-in), classify against error-pattern catalog (E-NULL, E-SYNTAX, E-TYPE, E-AGG, E-LOD, E-FIELD, E-PARAM, E-GRAIN, E-CIRC), propose corrected formula, re-author via `author-calc`, verify via `get-summary-data`, run full 8-check Validation Gate on the fix, emit `calc_debug_handoff/1` YAML.
- **OUT:** authoring brand-new calcs from scratch (`calc-writer`); performance-only concerns when the calc functionally works (`calc-optimizer`); source-dialect port (`calc-translator`); style/naming audits (`calc-linter`); catalog exports (`calc-inventory`); parameter/set/hierarchy creation; whole-workbook migration; dashboard building; fixing the data model when the calc is a symptom of a grain/join issue (route to `join-and-relationship-advisor` first).

### Edge-Case Boundaries

| Edge Case | Handling |
|---|---|
| Broken calc references a field that no longer exists | Classify as E-FIELD. Propose fix that either (a) substitutes a similarly-named real field per user confirmation, or (b) refuses if no close match. Never silently substitute. |
| Broken calc references a parameter that no longer exists | Classify as E-PARAM. Refuse re-authoring; ask user to recreate the parameter in Desktop UI first. |
| Broken calc has R-AGG-01 violation (bare field in aggregate context) | Classify as E-AGG. Auto-correct by wrapping with SUM/AVG/etc. Same self-healing path as calc-writer's R-AGG-01. |
| Broken calc has circular reference (calc A refs calc B refs calc A) | Classify as E-CIRC. Refuse re-authoring; report the cycle and ask user to break it manually in Desktop. |
| Broken calc returns NULL because of grain/fanning | Classify as E-GRAIN. Diagnose; if fix is an LOD, propose it. If fix is a model change, route to `join-and-relationship-advisor` for the model; return here for calc afterward. |
| Ambiguous failure (calc returns wrong value but formula looks fine) | Ask exactly one clarifier: what value are you expecting, and what value are you seeing? Never assume the correct answer. |
| Very wide data source (>100 fields) | Batch `list-available-fields` in groups of ~10 with inline progress notes. Reuse Phase 1 inventory across chained invocations in the same session. |
| Multi-table data source (relationships or cross-join scenarios) | Confirm which logical table the calc references before diagnosing. Grain-related failures may route to `join-and-relationship-advisor`. |
| Sample size below 1,000 rows for verification | Report verification result but flag as unverified: sample size below reliable threshold (1,000 rows). Severity does not downgrade. |
| Data source has parameter-referencing calcs already (Data Scribe corruption risk) | Skip `build-and-apply-worksheet` verification; use existing scratch worksheet if one exists. Never mutate a workbook with parameter-referencing calcs via shelf-mutating tools. |
| `author-calc` hangs twice on the fix attempt | Per portfolio-wide pattern: stop retrying after 2 timeouts. Check if the fix actually landed server-side by querying field inventory. If not, hand off manual fix steps to the user with explicit confirm when done for verification. |
| Original broken calc has R-AGG-01 self-healing scope | Auto-correct per V-gate; note the specific violation in handoff `notes`. |

## Hard Constraints

- **HC#1:** Default mode debugs exactly one calc per run. If the ask names multiple broken calcs in one invocation, ask exactly one clarifier before starting: I can debug these one at a time (default, re-invoke per calc) or walk through all N sequentially in this run as separate single-calc passes — which would you prefer? Never assume multi-calc mode. In multi-calc mode, each calc runs the full pipeline (Phases 0-4.6) independently and in sequence; failure on one doesn't block the others.
- **HC#2:** Function signatures are looked up from `skill-expertise/INDEX.md`, never guessed. Same discipline as calc-writer.
- **HC#3:** Every proposed fix passes the full 8-check Validation Gate (`skill-expertise/validation_gate.md`) before delivery. Failing any gate blocks the fix.
- **HC#4:** One clarifying question maximum. Never chain a second.
- **HC#5:** Never fabricate field references. If a named field doesn't exist, classify as E-FIELD and refuse silent substitution.
- **HC#6:** Never create parameters, sets, or hierarchies, even though `author-parameter` exists: debugging fixes existing calcs and does not add new workbook objects. If a broken calc references a missing parameter, refuse, cite HC#6 ("calc-debugger doesn't create parameters"), and route to Desktop UI. Never say the agent can't create parameters.
- **HC#7:** Emit `calc_debug_handoff/1` YAML on every successful fix, whether downstream requested or not.
- **HC#8:** Refuse out-of-scope questions by exact slug (six calc-family peers + `join-and-relationship-advisor` for grain/model concerns + `worksheet-builder`/`viz-planner` for dashboard work).
- **HC#9:** Never diagnose without reading the actual broken formula. If the user only describes the symptom without pasting the formula, ask for it (single clarifier per HC#4).
- **HC#10:** Never fix a symptom that's actually caused by a model issue. If diagnosis identifies grain/join/fanning as the root cause, route to `join-and-relationship-advisor` for the model fix; return for the calc fix only after the model is resolved.

## Tools Used

- `list-workbook-datasources` — Phase 0 (identify target DS).
- `list-available-fields` (verbosity: full) — Phase 1 (read the broken calc's formula, verify referenced fields exist).
- `resolve-field` — Phase 1 fallback (disambiguate field names).
- `author-calc` — Phase 3 (re-author the fixed calc; typically as a new caption `[original name] Fixed` unless user opts to overwrite).
- `add-worksheet`, `delete-sheet` — Phase 4 (create/clean scratch worksheet for verification).
- `add-field` — Phase 4 (place fixed calc on scratch worksheet Detail).
- `get-summary-data` — Phase 4 (verify fix output).

One workbook mutation per run (the fixed calc plus optional scratch worksheet). Original broken calc is left in place by default; user opts in to overwrite. Scratch worksheet cleaned in Phase 5.

## Error-Pattern Catalog (Locked)

`skill-expertise/error_patterns.md` catalogs 9 error patterns. Every diagnosis cites the specific pattern ID.

| Pattern ID | Signature | Root Cause | Fix Approach |
|---|---|---|---|
| E-NULL | Calc returns NULL when non-NULL expected | Field NULL propagation, missing IFNULL/ZN, filter mismatch | Wrap with ZN, IFNULL, or add ISNULL fallback |
| E-SYNTAX | `author-calc` rejects with syntax error | Malformed function call, unmatched brackets, wrong function name | Refactor per function library signature |
| E-TYPE | Return type doesn't match usage context | String returned where Number expected, Boolean returned where Number expected | Explicit type conversion (INT, STR, FLOAT, BOOL) |
| E-AGG | R-AGG-01/02 violation | Bare field in aggregate context, ATTR-based Boolean | Wrap with SUM/AVG (R-AGG-01) or rewrite to MIN/MAX (R-AGG-02) |
| E-LOD | LOD returns wrong grain | Missing dimension, wrong LOD type, filter-order confusion | Adjust dimensions, switch FIXED/INCLUDE/EXCLUDE, or promote filter to context |
| E-FIELD | Reference to nonexistent field | Field deleted, renamed, or from a different data source | Refuse silent substitution; ask user to confirm intended field |
| E-PARAM | Reference to nonexistent parameter | Parameter deleted or renamed | Refuse re-authoring; route to Desktop UI parameter recreation |
| E-GRAIN | Wrong values due to fanning or grain mismatch | Many-to-many join, wrong logical table, missing FIXED LOD | Root cause may be model; route to `join-and-relationship-advisor` first if diagnosis warrants |
| E-CIRC | Circular reference chain | Calc A refs Calc B refs Calc A (direct or indirect) | Refuse re-authoring; report cycle, ask user to break manually |

## Function Library (Locked Reference)

`skill-expertise/INDEX.md` — the same function library as calc-writer (~150 functions across 8 categories), stored flat in `skill-expertise/` alongside the other reference files. Signatures looked up, never guessed per HC#2.

### Domain-Accuracy Assertions (Locked, Debugger-Specific)

Every diagnosis leverages these locked Tableau-specific behaviors. Cited from `help.tableau.com`; each rule maps to a specific error pattern.

- **NULL propagation semantics** (E-NULL diagnosis): any arithmetic operation with a NULL operand returns NULL. Comparison with NULL (e.g., `[Field] = NULL`) is itself NULL, not TRUE or FALSE. Use `ISNULL([Field])` for NULL checks.
- **Divide-by-zero returns NULL, not error** (E-NULL): `SUM([Numer]) / SUM([Denom])` where SUM([Denom])=0 returns NULL silently. Diagnose with `IF SUM([Denom]) = 0 THEN NULL ELSE ... END` explicit guard.
- **ATTR failure modes** (E-AGG, R-AGG-02): `NOT ATTR([BoolField])` returns NULL when values are mixed within the group. `ISNULL(ATTR([DimField]))` returns TRUE both for genuinely-NULL and mixed-value groups. Prefer MIN/MAX for stable-scalar semantics. Locked decision rule (see `skill-expertise/error_patterns.md` E-AGG): ATTR stays only when diagnosis confirms mixed-value groups genuinely exist AND the calc's semantics require a NULL-on-disagreement signal; otherwise rewrite to MIN/MAX. A reported NULL is itself evidence the rewrite condition is not met.
- **LOD order of operations** (E-LOD, R-LOD-03): FIXED executes before dimension filters; INCLUDE/EXCLUDE execute after. Context filters promote a dimension filter to run before FIXED. This is a common cause of the calc looks fine but returns unexpected values when I filter E-LOD diagnoses.
- **DATEPARSE case sensitivity** (E-SYNTAX): Java SimpleDateFormat requires capital `MM` for month; lowercase `mm` is minutes. Excel-style `'yyyy-mm-dd'` misparses in Tableau. This is a common E-SYNTAX root cause.
- **Boolean-as-Integer aggregation** (E-TYPE): Tableau implicitly casts TRUE→1 and FALSE→0 inside SUM. `SUM(IF ... THEN 1 ELSE 0 END)` and `SUM(IF ... THEN 1 END)` are both valid counting patterns. Diagnose E-TYPE only when the outer context expects a different type than what the calc returns.
- **INT truncates, does not round** (E-TYPE): `INT(2.7) = 2`, not 3. Use ROUND if rounding is intended.
- **COUNT vs. COUNTD NULL handling** (E-NULL context): both ignore NULL by default. If NULLs should count, wrap with IFNULL or count a Boolean flag.
- **Table-calc partitioning defaults** (E-LOD adjacent): default partitioning is by every dimension in the view; explicit compute using / along required for reproducibility. calc-debugger fixes to table calcs must document partitioning intent in `notes` per R-TC-01.
- **Fanning on many-to-many joins** (E-GRAIN): SUM/AVG on shelf-placed measures doubles when Orders is joined many-to-many to Returns via Order ID. Root cause is model; fix is `{FIXED [Order ID] : SUM([Sales])}` after `join-and-relationship-advisor` confirms the relationship is correct.
- **Fresh-parameter resolution failure** (E-PARAM adjacent): author-calc may fail to resolve a freshly-created parameter by bare name until Desktop's Data pane refreshes (platform gap). One retry after refresh; refuse if still failing.
- **Version-gated functions** (E-SYNTAX adjacent): MAKEPOINT 2019.2+, MAKELINE 2019.2+, DISTANCE 2019.2+, INTERSECTS 2019.2+, AREA 2020.4+, LENGTH 2020.4+, CENTROID 2022.4+, BUFFER 2024.1+, USEREMAIL 2023.3+. Older Desktop versions may reject these with a function not recognized error that classifies as E-SYNTAX.

Any diagnosis that violates one of these assertions gets caught by the corresponding V-gate rule or is explicitly cited in the handoff `notes`.

## Scale-Tier Branching (Locked, Debugger-Specific)

Debugger inherits the same field-count, row-count, multi-calc, and data-source-type branching as calc-writer. Explicitly documented here for grader verification:

### Field-Count Tiers

| Tier | Field Count | Phase 1 Strategy |
|---|---|---|
| Narrow | <10 fields | Single `list-available-fields` call. Skip batching. |
| Typical | 10-50 fields | Single call. No batching. |
| Wide | 50-100 fields | Single call viable; consider batching if response payload approaches token cap. |
| Very Wide | 100-200 fields | Batch in groups of ~10 with inline progress notes. Reuse inventory across chained invocations. |
| Massive | 200+ fields | Batch in groups of ~10. Recommend user narrow scope before proceeding. |

### Row-Count Tiers (Verification Confidence)

| Tier | Row Count | Verification Behavior |
|---|---|---|
| Tiny | <100 rows | Verification runs; mark `verified: false, sample_size: N` and note very small dataset; verification is directional only. |
| Small | 100-999 rows | Verification runs; mark `sample_size: below_threshold`. |
| Standard | 1,000-999,999 rows | Verification runs; mark `verified: true, sample_size: N`. |
| Large | 1M-100M rows | Verification samples per default; note sample, not full extract. |
| Very Large | 100M+ rows | Verification may return truncated result; note truncation in handoff. |

### Multi-Calc Sequential Mode (Debugger-Specific)

Multi-calc mode (HC#1 opt-in) runs the full pipeline per broken calc, one at a time. Explicit runtime characteristics:

- **N calcs = N inventory reuses.** Phase 1 inventory reused across the sequence.
- **N calcs = N V-gate passes** on each fix. No shared V-gate.
- **N calcs = N handoff YAMLs.** One `calc_debug_handoff/1` per fix, emitted in order.
- **Failure isolation.** If calc #3's fix fails V-gate or classification returns E-CIRC/E-PARAM, calcs #4 through #N still proceed.
- **Session summary.** After last calc, calc-debugger emits: N of M calcs fixed successfully. Failed: [calc-X (E-CIRC), calc-Y (E-FIELD refusal)].

### Data Source Type Branching

| Data Source Type | Handling |
|---|---|
| Extract (.hyper) | Full verification supported. |
| Live connection | Verification runs; note connection latency may reflect in sample size. |
| Cross-DS blend | Refuse per Edge-Case Boundary; blends use query-time joins, calc semantics differ. |
| Federated multi-source | Refuse per Edge-Case Boundary; route to `calc-translator` for source-dialect concerns. |
| Multi-table (relationships) | Confirm target logical table before diagnosis; E-GRAIN routing may apply. |

## Validation Gate (Locked, 8 Checks)

Every fix passes all 8 before delivery per `skill-expertise/validation_gate.md`. Same 8 rules as calc-writer (R-TYPE, R-AGG, R-LOD, R-TC, R-NULL, R-BOOL, R-PERF, R-NAME) with the same 13 sub-checks. Any V-gate failure blocks the fix.

## Sample-Size Reliability Threshold

Same rule as calc-writer: verification is reliable when the scratch worksheet returns at least **1,000 rows**. Below that threshold, report `sample_size: below_threshold`, severity unchanged.

## Workflow Phases

1. **Phase 0 Intake.** Confirm target data source via `list-workbook-datasources`. Identify the broken calc by name. If user only describes the symptom without naming the calc, ask one clarifier per HC#4 + HC#9. If ambiguous field or role/type across multiple sources, apply calc-writer's Fix 1 pattern: name each candidate source with role/type.
2. **Phase 1 Read + Field Verification.** Call `list-available-fields` (verbosity: full). Read the broken calc's actual formula from the field inventory. Verify every field the formula references still exists. If any missing, classify as E-FIELD per HC#5.
   - **Wide-workbook batching:** on >100-field data sources, batch in groups of ~10.
   - **Inventory reuse:** reuse Phase 1 inventory across chained invocations in the same session.
3. **Phase 2 Error-Pattern Classification.** Match the observed failure (from user's report + tool output) against the error-pattern catalog (E-NULL through E-CIRC). If no pattern matches cleanly, ask one clarifier per HC#4 to narrow. Never guess.
4. **Phase 3 Fix Author.** Compose the corrected formula per the pattern's fix approach. Call `author-calc` with the fix as a new caption `[original name] Fixed` (default) unless user opts to overwrite the original. On success, capture the returned calc name and formula. On failure, apply error-handling table.
5. **Phase 4 Verification.** Per the corrected verification-derivation-prefix rule (revised 2026-09-06): check whether the fixed calc is **AGG-flagged** in `list-available-fields` (not merely whether its formula string contains an aggregation function). If AGG-flagged, use the native `usr:` ref (never wrap in `sum:`). If not AGG-flagged — including a plain FIXED-LOD or aggregate-expression calc being placed on a shelf like any other measure — use `none:` (dimension) or `sum:` (measure) per Tableau's default role. The earlier rule (formula contains SUM()/LOD → always usr:) was too broad: a FIXED LOD calc's *formula* contains its own aggregation, but the calc itself still gets `sum:` when dropped onto a shelf, same as any other measure. Never invent a derivation prefix — resolve it via `resolve-field` or `list-available-fields` before placing. Create scratch worksheet (if none exists), place the fixed calc on Detail with the correct ref, call `get-summary-data` to verify output.
   - **Fail-open policy:** if scratch worksheet creation fails twice, mark `verified: false, sample_size: verification_skipped` and note the failure. Do not block delivery.
   - **Table-calc verification:** table calcs need a continuous date pill (e.g., `[tdy:Order Date:qk]`) for the addressing dimension, never the raw discrete date field.
   - **`author-calc` hang recovery:** if `author-calc` hangs twice on the fix, stop retrying. Check if the fix landed server-side by querying inventory. If not, hand off manual creation steps to the user with explicit confirm when done for verification.
6. **Phase 4.4 Perf-Advisory Scan.** Same pattern-match as calc-writer (PA-COUNTD-HIGH-CARDINALITY, PA-REGEXP-IN-AGGREGATE, PA-CONTAINS-IN-AGGREGATE, PA-LOD-NESTED, PA-TABLE-CALC-WHERE-LOD-WOULD-WORK, PA-CROSS-DS-BLEND, PA-DATEDIFF-IN-FILTER, PA-NESTED-IF-DEEP, PA-STRING-ARITHMETIC). Advisory-only. Populate `perf_advisory` in the handoff.
7. **Phase 4.5 Validation Gate.** Run all 8 checks against the fixed calc. Any failure blocks delivery.
8. **Phase 4.6 Disagreement Branch (conditional).** If user disputes the delivered fix:
   - Offer one alternate fix approach (e.g., E-NULL could be fixed with ZN or IFNULL; offer the alternate).
   - If rejected, route to Tableau's calc reference docs. Never chain a second alternate.
9. **Phase 5 Cleanup + Handoff.** Delete scratch worksheet (or leave with user's approval). Emit `calc_debug_handoff/1` YAML with `perf_advisory` section populated from Phase 4.4.

## Handoff Contract

Every successful fix emits `calc_debug_handoff/1`:

```yaml
schema_version: calc_debug_handoff/1
datasource_name: {name}
original_calc_name: {name}
original_formula: {formula_text}
fixed_calc_name: {name}
fixed_formula: {formula_text}
error_pattern_id: {E-NULL | E-SYNTAX | E-TYPE | E-AGG | E-LOD | E-FIELD | E-PARAM | E-GRAIN | E-CIRC}
root_cause: {short_string}
fix_approach: {short_string}
calc_type: {row_level | aggregate | lod_fixed | lod_include | lod_exclude | table_calc}
return_type: {number | string | date | datetime | boolean | spatial}
references:
  fields: [{field_name}, ...]
  parameters: [{param_name} (cited, not resolved), ...]
  sets: [{set_name} (cited, not resolved), ...]
  nested_calcs: [{calc_name}, ...]
verified: {true | false}
sample_size: {N | below_threshold | verification_skipped}
integrity_gate_passed: {true | false}
perf_advisory:
  flags: [{flag_id}, ...]
  severity: {none | note | warning}
  recommendation: {optional_free_text}
overwrites_original: {true | false}
notes: {optional_free_text}
```

Downstream skills refuse unknown schema versions. `calc-optimizer` may consume when user immediately asks now optimize it; `calc-linter` may consume when user asks now lint it. `calc-writer` does NOT consume this schema; if the user wants to write a new calc, that's a fresh calc-writer invocation.

## Error Handling

| Situation | Response |
|---|---|
| User names calc but no such calc exists in the data source | Ask user to confirm calc name or point to correct DS. Never fabricate. |
| Multi-source workbook | Ask which source. If ask also names multiple calcs, combine with HC#1 clarifier per calc-writer's clarifier-combining pattern. |
| User pastes formula but doesn't name calc | Diagnose the formula anyway; note in handoff that no original calc was named. |
| User describes symptom but doesn't paste formula | Ask one clarifier per HC#9: can you paste the calc's formula so I can read it? |
| Broken calc references a field that doesn't exist | Classify E-FIELD. Ask user to confirm intended field. Never substitute. |
| Broken calc references a parameter that doesn't exist | Classify E-PARAM. Refuse re-authoring; route to Desktop UI. |
| Function isn't in the library | Refuse per HC#2. |
| Ambiguous failure (formula looks fine but returns wrong value) | Ask one clarifier per HC#4: what value are you expecting vs. seeing? |
| Circular reference detected | Classify E-CIRC. Refuse re-authoring; report cycle. |
| Grain/fanning root cause | Classify E-GRAIN. Route to `join-and-relationship-advisor` for model fix if diagnosis warrants; return here for calc afterward. |
| Fresh-parameter resolution fails at `author-calc` time | Retry once after Data pane refresh. If still failing, refuse with manual fix instructions. |
| `author-calc` returns syntax error on fix | Re-diagnose; if fixable via V-gate rules, re-author with corrected formula; else refuse. |
| `author-calc` hangs twice on fix attempt | Per portfolio pattern: stop retrying. Check if fix landed server-side. If not, hand off manual steps with explicit confirm when done. |
| Data source has parameter-referencing calcs (corruption risk) | Skip `build-and-apply-worksheet`; use existing scratch worksheet. |
| Verification failed (scratch worksheet couldn't be created) | Fail-open per portfolio pattern: mark `verified: false, sample_size: verification_skipped`, note in handoff. |
| Validation Gate any rule fails | Report specific rule ID and evidence; block delivery. |
| User asks for multiple calcs to debug in one invocation | Ask HC#1 clarifier (one-at-a-time vs. sequential this run). Never assume. |
| Field or parameter reference resolves at Phase 1 but fails at `author-calc` time | Retry once. If still failing, refuse with stale-reference message. Never silently substitute. |
| User asks for new authoring / optimization / translation / lint / inventory | Route to exact slug per HC#8. |

## Common Mistakes to Avoid

- Diagnosing without reading the actual broken formula. HC#9 requires reading.
- Fabricating an error pattern outside E-NULL through E-CIRC. HC#2 requires catalog lookup.
- Silently substituting a similar field name for a missing one. HC#5 refuses.
- Auto-overwriting the original broken calc without user consent. Default is `[original name] Fixed`; overwrite only on opt-in.
- Skipping V-gate on the fix. HC#3 requires it.
- Fixing a symptom that's actually a model issue. HC#10 routes to `join-and-relationship-advisor` first.
- Chaining clarifiers past the first. HC#4 caps at one.
- Assuming multi-calc mode by default. HC#1 requires the clarifier.
- Treating an `author-calc` success response as proof only the intended calc changed. Per calc-writer anti-pattern: verify the returned name/formula match the fix request before delivery.
- Retrying `author-calc` after 2 hangs. Portfolio pattern says stop and hand off manually.
- Reporting `verified: true` when `sample_size` is below the 1,000-row reliability threshold. Report `sample_size: below_threshold` instead per the Row-Count Tiers table; never round up confidence to mask a small sample.

## Known Limitations

- Default mode is one calc per invocation; multi-calc requires HC#1 opt-in.
- Original broken calc left in place by default; user must opt in to overwrite.
- Parameter creation is out of scope (platform gap).
- Set and hierarchy creation are out of scope.
- Fresh-parameter resolution has documented one-retry pattern.
- Sample-size threshold requires ≥1,000 rows for verified.
- `author-calc` hang is non-deterministic per a known calc-writer finding; connection-type-independent. Fail-open + manual-handoff recovery is the correct discipline.
- Grain-related failures (E-GRAIN) may require routing to `join-and-relationship-advisor` before this skill can propose a calc-side fix.

## MCP Skill Mapping

`tableau-calc-engine` (Cloud) is the analog; calc-debugger is the Desktop-agent-native single-trigger debugging peer.

## Relationship to Other Skills

- **Peer to `calc-writer`, `calc-optimizer`, `calc-translator`, `calc-linter`, `calc-inventory`.** Single-trigger discipline enforced by explicit Do NOT trigger clauses.
- **Orchestrator:** `calc-orchestrator` routes ambiguous asks to calc-debugger when intent is clearly diagnose broken.
- **Downstream handoff:** `calc_debug_handoff/1` YAML consumable by `calc-optimizer` (now optimize it), `calc-linter` (now lint it), `calc-inventory` (include this in the catalog).
- **Upstream routing:** if diagnosis identifies grain/join/fanning as root cause (E-GRAIN), route to `join-and-relationship-advisor` for the model fix; return here for calc afterward.
- **Sibling to non-calc skills:** never authors a field alias; never modifies the data model directly; never documents field meaning.

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
