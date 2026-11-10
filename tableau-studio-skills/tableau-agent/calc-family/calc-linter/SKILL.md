---
name: calc-linter
description: "Use when the user says 'Lint this calc', 'check this calc's style', 'rewrite for readability', 'does this follow our house style?' Checks one calculated field against house style (naming, comments, indentation, clarity) and rewrites it only if you opt in, with an equivalence check."
---

# Calc Linter

## When to use (full trigger detail)

Lint one existing Tableau calculated field per run against a locked house-style catalog (naming, comments, indentation, structural clarity), report violations with severity + rationale, and optionally rewrite on explicit user opt-in. Style-only scope. Consumes calc_write_handoff/1 or calc_debug_handoff/1 or calc_optimize_handoff/1 from upstream peers, or fires standalone on a lint ask. Runs an 8-check Validation Gate plus a mandatory R-EQUIV-01 equivalence check on any rewrite. Emits calc_lint_handoff/1. Correctness bugs route to calc-debugger; perf rewrites route to calc-optimizer; new calc authoring routes to calc-writer. Triggers on lint this calc, check this calcs style, rewrite for readability, does this calc follow our house style, check my calc naming, style-check this calc, or when a calc_write_handoff/1 / calc_debug_handoff/1 / calc_optimize_handoff/1 arrives and the user says now lint it. Do NOT trigger for writing new calcs (calc-writer), fixing broken/wrong-value calcs (calc-debugger), performance rewrites (calc-optimizer), cataloging calcs across a data source (calc-inventory), workbook-level style tuning (workbook-auditor), or model/relationship style (join-and-relationship-advisor).

## Purpose

Lint one existing Tableau calculated field per run against a locked house-style catalog. Report violations with severity plus rationale, or (on explicit user opt-in) rewrite the calc to fix them. Style-only scope. Value-preserving.

## Trigger Conditions

Positive triggers: lint this calc, check this calcs style, rewrite for readability, does this calc follow our house style, check my calc naming, style-check this calc, or arrival of a `calc_write_handoff/1` / `calc_debug_handoff/1` / `calc_optimize_handoff/1` payload followed by the user saying now lint it.

Do NOT trigger on the following adjacent asks. Refuse by exact slug.

| User ask | Route to |
|---|---|
| Write a new calc for... | `calc-writer` |
| This calc is broken / returns wrong values / errors. | `calc-debugger` |
| This calc is slow / optimize this calc. | `calc-optimizer` |
| List all calcs in this data source. | `calc-inventory` |
| This dashboards style is inconsistent. | `workbook-auditor` |
| This join / relationship naming is inconsistent. | `join-and-relationship-advisor` |
| Help me with a calc (ambiguous). | `calc-orchestrator` |
| Why was this calc linted differently yesterday? | Scripted prior-turn-diagnosis refusal (no visibility). |

## Scope Boundaries

- IN: linting one calc per run against a locked house-style catalog; reporting violations with severity plus rationale; rewriting on explicit user opt-in with mandatory runtime equivalence verification; emitting `calc_lint_handoff/1`. Also IN: an explicit clean verdict when no violations surface.
- OUT: correctness fixes (`calc-debugger`); performance rewrites (`calc-optimizer`); new calc authoring (`calc-writer`); dashboard-level style tuning (`workbook-auditor`); join/relationship naming (`join-and-relationship-advisor`); linting across multiple calcs in one run (per-calc; multi-calc requires HC#1 opt-in); parameter, set, or hierarchy creation (platform gap); style-config file loading (skill uses only its locked catalog; user-supplied style files are out of scope).

### Edge-Case Boundaries

| Edge Case | Handling |
|---|---|
| Calc passes all style rules cleanly | Deliver clean verdict. Emit handoff with `violations: []` and `rewritten: false`. Never fabricate a violation. |
| User asks for lint but declines rewrite opt-in | Deliver report-only. `rewritten: false`. Never rewrite without explicit opt-in. |
| Rewrite would change returned values | Reject candidate. Try next rule down or refuse the rewrite for that specific violation. Report the violation without the rewrite. Never ship a value-changing style fix. |
| Multi-source ambiguity on any referenced field | HC#4 one-clarifier. Name each candidate source with role and datatype. |
| User names multiple calcs to lint | HC#1: ask one at a time (default) or sequential this run? before proceeding. |
| Original formula is broken (author-calc rejects, wrong values, missing field) | Refuse. Route to `calc-debugger`. Do not lint a broken calc. |
| Equivalence verification fails twice on a rewrite | Fail-open per HC#8. Mark `verified_equivalent: false, equivalence_sample_size: verification_skipped` for that rewrite. Deliver report + unrewritten violation with warning. |
| `author-calc` hangs twice | Stop retrying. Check inventory. If not landed, hand off manual steps with confirm when done. Matches calc-writer/debugger/optimizer recovery pattern. |
| Style violation is subjective (e.g., naming convention conflict between old-Superstore style and new-house style) | Report as `severity: info`. Never as error or warning. User decides. |
| Consumed upstream handoff payload references a field that has since been deleted or renamed | Re-verify every field reference in the payloads `references.fields` list via `list-available-fields` at Phase 1 start. If any reference no longer resolves, refuse the lint and route back to the upstream peer with a note: handoff payload contains stale field references; re-run upstream before linting. |
| Scratch worksheet name collision (e.g., Linter Scratch already exists) | Use fresh-name discipline: append `_v2`, `_v3` on collision. Never overwrite an existing scratch sheet. Clean up whichever name was used in Phase 8. |
| Datasource disconnects mid-lint | Stop immediately. Report which phase was in progress. Do not emit `calc_lint_handoff/1`. Ask user to reconnect before resuming. |
| Rewrite would violate value semantics via IF-to-CASE reordering, NULL propagation change, or short-circuit swap | Reject candidate at V-gate. Never ship a cosmetic rewrite that silently changes NULL/order semantics. Document in report as flagged but not rewritten: value-semantics risk. |
| S-NAME-* rewrite would rename a calc that other calcs in the same data source depend on | Tableau stores calc-to-calc references by internal ID (`[Calculation_...]`), so a caption rename does not break formulas inside the workbook. It can still confuse readers and break anything outside the workbook that cites the name (published-datasource consumers, external docs). Before authoring the rename, get the target calc's internal name from `list-available-fields` and search every formula for that internal name AND the caption. If any dependents exist, refuse the rename by default and report `notes: rename held: [N] calcs depend on this calc ([calc names]). Renaming won't break them in this workbook, but check published-datasource consumers and docs that cite the old name.` User can override with an explicit second opt-in. Never silent. |

## Hard Constraints

- HC#1: Single-calc-per-run default. Multi-calc ask requires explicit user opt-in (sequential this run) with one clarifier.
- HC#2: Value-preserving. Any rewrite MUST return the same values as the original for every group. Verified via mandatory R-EQUIV-01 equivalence check.
- HC#3: Locked house-style catalog in `skill-expertise/style_catalog.md` is the rule authority. 12 rules with severity tiers (error/warning/info). Never invent a new rule or reorder severity mid-run.
- HC#4: One-clarifier discipline. Ambiguous asks get exactly one combined clarifier, never chained.
- HC#5: No field, parameter, set, or hierarchy fabrication.
- HC#6: No parameter, set, or hierarchy creation (platform gap).
- HC#7: Every delivery emits `calc_lint_handoff/1` YAML unprompted with all required fields non-blank.
- HC#8: Validation Gate before delivery of any rewrite. 8-check gate identical to calc-writer/debugger/optimizer, plus mandatory R-EQUIV-01 equivalence verification with fail-open on double failure.
- HC#9: Must read the original formula. If not pasted or resolvable from an upstream handoff payload, ask for it.
- HC#10: Style-only scope. If root cause of the ask is correctness (calc-debugger) or performance (calc-optimizer), route by exact slug. Never absorb.
- HC#11: Report-mode default; rewrite requires explicit user opt-in. Lint this calc alone triggers report-only. Rewrite it to match or fix the style is the opt-in phrase. Never silently rewrite.
- HC#12: Rewrite discipline. Default: author the rewritten calc as `[original name] Clean`. Overwriting the original requires explicit user opt-in confirmation, which is never waived by user pressure (just do it without asking).
- HC#13: Function signatures are looked up in `skill-expertise/INDEX.md` and its category files, never guessed. Same discipline as calc-writer, calc-debugger, and calc-optimizer. If a rewrite needs a function that isn't in the library, drop that candidate and never invent a signature.

## Tools Used

- `list-workbook-datasources` — Phase 0 (identify target DS).
- `list-available-fields` — Phase 1 (verify all referenced fields exist; resolve AGG-flag for each). Default practice, not just the >100-field edge case: batch calls in groups of ~10 with inline progress notes whenever the workbooks field count makes a single call unwieldy.
- `resolve-field` — Phase 1 (resolve derivation prefix per fields actual AGG-flag; never string-match the formula).
- `author-calc` — Phase 5 (author the rewritten calc, only on user opt-in).
- `get-summary-data` — Phase 6 (mandatory R-EQUIV-01 verification: author original + rewrite on scratch worksheet, compare aggregated values). On a live (non-extract) datasource connection, this call is slower than on an extract; apply the high-cardinality sampling cap (top 200 + random 100) proactively rather than waiting for the >500-group threshold to be reached, to bound wait time.
- No file writes. Skill is compute-only; downstream consumers write.

## House-Style Catalog (Locked, 12 Rules)

Full catalog in `skill-expertise/style_catalog.md`. Summary:

**Naming (severity: error)**
- **S-NAME-01:** Calc name is ≤20 characters unless it inherits a longer parent name. A skill-added suffix (` Clean`, ` Fast`, ` Fixed`) doesn't count toward the 20.
- **S-NAME-02:** Calc name uses Title Case, no leading/trailing whitespace, no double spaces.
- **S-NAME-03:** Calc name is not a Tableau reserved word or a bare function name (e.g., SUM, COUNT).

**Structure (severity: warning)**
- **S-STRUCT-01:** IF/ELSEIF chains ≤4 branches; deeper chains flagged.
- **S-STRUCT-02:** Nested LODs deeper than depth 1 documented in a leading comment or flagged.
- **S-STRUCT-03:** Table calcs document partitioning/addressing in a leading comment or flagged.
- **S-STRUCT-04:** No unnecessary parentheses around single-token operands.

**Comments (severity: info)**
- **S-COMMENT-01:** Calcs longer than 5 lines have a leading comment explaining purpose.
- **S-COMMENT-02:** Non-obvious literal values (magic numbers, business thresholds) have inline explanatory comments.

**Formatting (severity: info)**
- **S-FORMAT-01:** Indentation uses spaces (2 or 4), consistent within one calc.
- **S-FORMAT-02:** No trailing whitespace on any line.
- **S-FORMAT-03:** One blank line max between logical sections.

Every violation is reported with its rule ID, severity, and one-line rationale. Rewrite suggestions render only when the violation is safely rewritable (see R-EQUIV-01 discipline below).

## Phase Sequence

- **Phase 0.** Identify target data source. Multi-source ambiguity fires HC#4 clarifier with role/type disclosure.
- **Phase 1.** Read the original formula. Resolve every field reference via `list-available-fields`/`resolve-field`. Refuse silent substitution on missing fields (HC#5). Re-verify any consumed handoff payloads references.
- **Phase 2.** Run the calc against the 12-rule catalog. Log every violation with severity + rationale.
- **Phase 3.** Assemble the lint report. Group violations by severity (error → warning → info). If zero violations, deliver clean verdict.
- **Phase 4.** If user opted in to rewrite (HC#11), generate rewrite candidates per violation. Filter through the V-gate. Reject any candidate that itself violates a V-gate rule or would change returned values. Before keeping any candidate, look up every function it uses in `skill-expertise/INDEX.md` per HC#13.
- **Phase 5.** Author the rewritten calc via `author-calc` as `[original name] Clean` (or overwrite the original only if user explicitly opted in per HC#12).
- **Phase 6.** Mandatory R-EQUIV-01 equivalence verification. Author both original and rewrite on a scratch worksheet. Sample aggregated values by every dimension the original touches. Compare row-by-row. Fail-open on double failure per HC#8.
- **Phase 7.** Emit `calc_lint_handoff/1` YAML unprompted with violations, rewrites (if any), and verification status.
- **Phase 8.** Clean up scratch worksheet.

## Validation Gate

Full spec in `skill-expertise/validation_gate.md`. 8-check gate identical to calc-writer/debugger/optimizer:

- R-TYPE-01, R-TYPE-02: classification and return type match original.
- R-AGG-01, R-AGG-02: aggregation wrapping; ATTR two-condition rule.
- R-LOD-01, R-LOD-02, R-LOD-03: LOD syntax, nesting depth, filter order-of-operations.
- R-TC-01, R-TC-02: table-calc partitioning; prefer FIXED LOD.
- R-NULL-01: NULL handling explicit.
- R-BOOL-01: TRUE/FALSE/NULL, not 1/0/-1.
- R-PERF-01: no row-level string ops in aggregations.
- R-NAME-01: `[original name] Clean` default; the original name part is ≤20 chars unless the original was longer. The ` Clean` suffix doesn't count.

Plus the optimizer-shared runtime check:

- **R-EQUIV-01:** any rewrite returns the same values as the original for every group. Verified via runtime equivalence check on scratch worksheet. Fail-open on double failure per HC#8. High-cardinality sampling cap (>500 groups → top 200 + random 100). Zero-dimension FIXED LOD read-gap recovery discipline preserved from calc-optimizer.

## Verification Derivation-Prefix Rule

Resolve derivation prefixes from the calcs actual AGG-flag via `list-available-fields`/`resolve-field`, not by string-matching the formula for aggregation functions. Preserves the runtime-lookup discipline confirmed in calc-writer/debugger/optimizer testing.

## Domain-Accuracy Assertions (Locked)

- IF/ELSEIF chain reordering can change short-circuit evaluation semantics. Never rewrite branch order without R-EQUIV-01 verification.
- IF-to-CASE conversion changes NULL propagation and equality semantics (CASE requires exact match; IF supports full comparison operators). Never do this rewrite unless the original formula is genuinely equality-only.
- Naming rewrites (S-NAME-*) never touch the formula body. Renaming is authoring a new calc with the new name, not editing.
- Comment additions never change formula semantics but can trigger `author-calc` reject if the comment syntax collides with formula syntax. Verify author-calc round-trip before delivery.
- Whitespace/indentation edits are semantically no-ops in Tableaus parser but must still pass R-EQUIV-01 as belt-and-braces.

## Scale-Tier Branching

For calcs with more than ~50 lines, batch the rule catalog into two passes: structural rules (S-STRUCT-*) first, then naming/formatting. For workbooks with more than ~100 fields (relevant when re-verifying handoff references), batch `list-available-fields` in groups of ~10 with inline progress notes.

## Multi-Calc Sequential Mode

Default: single calc per run. If user names multiple calcs, fire HC#1 clarifier: one at a time (default) or sequential this run? Sequential mode runs the full pipeline per calc, emits one `calc_lint_handoff/1` per calc, and ends with a session summary.

Failure isolation: if calc N fails a hard constraint (e.g., HC#5 missing field), calcs 1..N-1 and N+1..M still ship.

## Report Structure (Locked)

Every lint delivery renders this exact structure, even for clean verdicts:

- **Summary:** N violations found (X errors, Y warnings, Z info), or Clean — no violations.
- **Errors:** rule ID, rationale, snippet, rewrite suggestion (if safely rewritable). None surfaced is valid.
- **Warnings:** same shape.
- **Info:** same shape.
- **Rewrite delivered:** yes/no (only yes if user opted in AND R-EQUIV-01 passed).
- **Trade-offs (if rewrite delivered):** readability, maintainability, downstream impact. None surfaced is valid.

## Handoff Contract

Emits `calc_lint_handoff/1` unprompted after every delivery, including clean verdicts. Full schema in `skill-expertise/handoff_schema.md`. Required non-blank fields:

- `schema_version`, `datasource_name`, `original_calc_name`, `original_formula`
- `violations` (list; may be empty for clean verdicts)
- `rewritten` (true/false), `rewritten_calc_name` (only if `rewritten: true`), `rewritten_formula` (only if `rewritten: true`)
- `verified_equivalent` (true/false; N/A only if `rewritten: false`)
- `overwrites_original` (true/false)

## Refuse to Fabricate

Never invent a style rule outside the locked 12-rule catalog. Never fabricate a violation. Never silently rewrite. Never ship a rewrite that fails its own V-gate or R-EQUIV-01. Never invent a function signature (HC#13).

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
