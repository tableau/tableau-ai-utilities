---
name: calc-hygiene-scan
description: "Use when the user says 'Audit my calcs', 'calc hygiene scan', 'check calc quality', 'find calc issues'. Checks every calculated field against 8 hygiene rules (naming drift, unused calcs, deep nesting, hard-coded values, deprecated functions, LOD overuse) with manual fix steps. Read-only."
---

# Calc Hygiene Scan

## When to use (full trigger detail)

Audit calc-family hygiene across a Tableau workbook against a locked 8-rule catalog (naming convention drift, missing author captions, unused calcs, excessive nesting depth, hardcoded values that should be parameters, deprecated function usage, cross-DS calcs without rationale, over-reliance on LOD when a simpler pattern works). Read-only. Every finding is a manual Desktop-fix instruction. Opportunistically consumes calc-documenters calc_documentation/1 handoff with V5 formula-hash staleness detection per portfolio-wide HC#15; local-extract fallback when handoff is missing or stale. Autofix candidates route to calc-linter via handoff signal but this skill never mutates. Trigger with calc hygiene scan, audit my calcs, check calc quality, calc-hygiene-scan, review my calcs, calc quality audit, find calc issues. Do NOT trigger on. explaining a single calc in plain language (route to calc-explainer), documenting every calc in detail (route to calc-documenter), calc performance rewrites (route to calc-optimizer), applying naming or hygiene fixes (route to calc-linter), authoring new calcs (route to calc-writer), diagnosing NULL returns (route to calc-debugger), or migrating a calc between datasources (route to calc-migrator).

## Purpose

Audit every calculated field in a Tableau workbook against a locked 8-rule hygiene catalog. Read-only. Every finding is a manual Desktop-fix instruction; autofix candidates (naming drift, deprecated functions, hardcoded values) route to `calc-linter` via handoff signal but this skill never mutates. Opportunistically consumes `calc_documentation/1` handoff from `calc-documenter` with V5 formula-hash staleness detection; local-extract fallback when handoff is missing or stale.

## Trigger Conditions

- calc hygiene scan
- audit my calcs
- check calc quality
- calc-hygiene-scan
- review my calcs
- calc quality audit
- find calc issues
- audit calculated fields

## Do NOT Trigger On

- Explaining a single calc in plain language → route to `calc-explainer`.
- Documenting every calc in detail (full dictionary) → route to `calc-documenter`.
- Listing, inventorying, or cataloging calcs (what calcs exist, reference graph, usage) → route to `calc-inventory`.
- Calc performance rewrites → route to `calc-optimizer`.
- Applying naming or hygiene fixes → route to `calc-linter`.
- Authoring new calcs from scratch → route to `calc-writer`.
- Diagnosing NULL returns from a specific calc → route to `calc-debugger`.
- Migrating a calc between datasources → route to `calc-migrator`.
- Producing a summary onepager for stakeholders → route to `workbook-summary-onepager`.

## Scope Boundaries

- **IN.** One workbook per run. Read-only. 8-rule hygiene catalog. Opportunistic `calc_documentation/1` handoff consumption with V5 formula-hash staleness detection per portfolio-wide HC#15; local-extract fallback via `list-available-fields`, `resolve-field`, and formula pattern-matching. Autofix routing signal (`routing.calc_linter: true`) emitted for autofixable findings but never auto-invoked. Handoff schema `calc_hygiene_report/1`. Wide-workbook scale handling per HC#16.
- **OUT.** Any workbook mutation. Applying fixes (route to calc-linter). Explaining a single calc (route to calc-explainer). Bulk documentation (route to calc-documenter). Performance rewrites (route to calc-optimizer). Multi-workbook batch runs. Cross-workbook calc comparison.

## The 8-Rule Hygiene Catalog (Locked)

Every finding cites a rule ID. Multi-rule findings tier by highest severity. Full detection criteria, threshold defenses, and worked examples in `skill-expertise/rule_catalog.md`.

| # | Rule | ID | Severity | Signal source | Autofixable? |
|---|---|---|---|---|---|
| 1 | Naming convention drift | CH-NAMING-01 | Info | workbook XML | Yes (route to calc-linter) |
| 2 | Missing author captions | CH-CAPTION-02 | Info | workbook XML | No (author intent required) |
| 3 | Unused calcs (zero references) | CH-UNUSED-03 | Warning | reference graph (handoff) or local-extract usage scan | No (removal is destructive; route to calc-linter for delete workflow) |
| 4 | Excessive nesting depth | CH-NESTING-04 | Warning | formula parse | No (rewrite is out of scope for this skill; route to calc-optimizer) |
| 5 | Hardcoded values that should be parameters | CH-HARDCODED-05 | Warning | formula pattern-match against a locked hardcoded-value catalog | Yes (route to calc-linter) |
| 6 | Deprecated function usage | CH-DEPRECATED-06 | Warning | formula pattern-match against a locked deprecated-function list | Yes (route to calc-linter) |
| 7 | Cross-DS calcs without rationale | CH-CROSSDS-07 | Info | reference graph (handoff) with `cross_datasource_reference` flag | No (rationale is author intent; user acknowledges) |
| 8 | Over-reliance on LOD when a simpler pattern works | CH-LOD-OVERUSE-08 | Info | formula pattern-match against `skill-expertise/explanation_patterns.md` precedence rules | No (rewrite is out of scope for this skill; route to calc-optimizer) |

**Multi-rule tagging.** A calc can fire multiple rules simultaneously (common: CH-NAMING-01 + CH-CAPTION-02 both fire on a poorly-authored calc). Skill emits all triggered rule IDs in `rules_triggered[]`; severity tier set by highest match. Deterministic sort per HC#10: severity tier → rule ID ascending → calc name alphabetical.

**Fallback discipline (HC#5).** When rule detection depends on data thats unavailable (calc-documenter handoff missing, formula unreadable via `list-available-fields`), skill emits `unable to determine` sentinel per HC#5 for that specific rule on that specific calc.

## Workflow Phases

- **Phase 0 Scope.** Confirm workbook is open via `get-workbook-inventory`. If the call fails, returns no workbook, or the session is disconnected, stop and tell the user to confirm Tableau Studio is open with a workbook loaded — do not proceed to Phase 1 on an empty or failed inventory read. Ensure one workbook per run per HC#2. Enumerate calcs across all datasources via `list-available-fields`. If zero calcs exist, exit cleanly per HC#7 with no calculated fields defined; hygiene scan not applicable.
- **Phase 1 Handoff Discovery.** Check session context for `calc_documentation/1` handoff. If present, verify V5 formula-hash match per calc against current workbook state per HC#13. Populate `handoff_consumed` (true/false), `stale_handoff` (true/false), and per-calc `signal_source` flags. Stale handoff forces local-extract fallback per HC#13; skill does not render against stale data.
- **Phase 2 Rule Evaluation (numbered checklist).**
  1. For each calc in the workbook, apply each of the 8 rules from `skill-expertise/rule_catalog.md`.
  2. Formula text for parse-depth (CH-NESTING-04) and pattern-match rules (CH-HARDCODED-05, CH-DEPRECATED-06, CH-LOD-OVERUSE-08) comes from `list-available-fields`s formula field when populated for a calc; if a given calcs entry has no formula text, treat that calc as formula-unreadable for those rules and emit the HC#5 sentinel for them specifically rather than assuming the tool always returns formula bodies.
  3. Batch `resolve-field` calls in groups of 20 per portfolio-wide HC batching cap (matches calc-migrators Phase 2 pattern). If a batch call fails outright (timeout, disconnect), retry that batch once; on a second failure, emit `unable to determine` sentinel for every calc/rule pair depending on that batchs resolution and continue with the remaining batches — do not abort the whole scan.
  4. For each rule fired, populate `rules_triggered[]` with the rule ID, calc name, evidence citation, and `signal_source`.
  5. For autofixable rules (CH-NAMING-01, CH-HARDCODED-05, CH-DEPRECATED-06), set `autofixable: true` and populate `routing.calc_linter: true` at the finding level.
  6. For rules with unresolvable signals, emit `unable to determine` sentinel per HC#5 rather than skipping.
- **Phase 3 Severity Tiering + Deterministic Sort.** Sort per HC#10: severity tier (Warning → Info) → rule ID ascending → calc name alphabetical.
- **Phase 4 Validate.** Run the 5-check V-gate: rule coverage, per-calc signal-source attribution, ordering determinism, handoff completeness, autofix routing correctness. If any check fails, do not discard the run: re-run only the failing checks underlying data pull once (e.g., re-fetch signal-source labels for V2, re-sort for V3), then re-validate that check. If it fails a second time, deliver Tier A with the specific V-check named as unresolved and the affected calcs/rules listed, rather than blocking delivery entirely or silently passing.
- **Phase 5 Deliver.** Two-tier: compact Tier A chat summary with counts and top 5 Warning-tier findings; opt-in Tier B file save requires user path confirmation per HC#12.

## Hard Constraints

**HC#1 Read-only always.** Never mutates the workbook. Every finding is a manual Desktop-fix instruction plus (for autofixable rules) a routing signal to calc-linter.

**HC#2 One workbook per run.** Multi-workbook runs refused.

**HC#3 8-rule catalog locked.** No rule omitted, no fabricated rule added. Detection follows the criteria in `skill-expertise/rule_catalog.md`.

**HC#4 Refuse to fabricate.** No inferred naming conventions, no guessed author intent, no invented deprecation timelines. Sentinels: `null`, `unable to determine`, empty-state prose.

**HC#5 Sentinel discipline per rule per calc.** When a rules detection fails on a specific calc (formula unreadable, handoff stale for that specific calc), emit `unable to determine` sentinel for that rule on that calc. Other rules on the same calc still evaluate; other calcs still get all 8 rules.

**HC#6 Author caption preserved verbatim.** If a calc has an author caption or in-formula `//` annotation, CH-CAPTION-02 correctly clears (not fires). Skill supplements around author intent per portfolio-wide discipline.

**HC#7 Sentinel discipline for zero-calc workbook.** If workbook has 0 calcs, exit cleanly with no calculated fields defined message. Zero-datasource workbooks also exit cleanly.

**HC#8 Diff-mode transparency** (portfolio-wide HC#13). Repeat invocations against unchanged workbook + handoff state emit `diff_mode: reused_verbatim` in Tier A. Fresh-scan / reused-verbatim / targeted-rescan enum.

**HC#9 Ordering determinism** (portfolio-wide HC#14). Sort key locked: severity tier → rule ID → calc name alphabetical. Same input produces byte-identical top-5 and full findings list across runs.

**HC#10 Handoff-or-local labeled per calc per rule.** Every rule evaluation records `signal_source: handoff | local_extract | unresolved` per calc so downstream consumers know evidence origin.

**HC#11 Never silent file write.** Tier B save requires user path confirmation.

**HC#12 Autofix routing, never autofix invocation.** For autofixable rules (CH-NAMING-01, CH-HARDCODED-05, CH-DEPRECATED-06), emit `routing.calc_linter: true` on the finding. Skill never invokes calc-linter directly per HC#1; user opts in.

**HC#13 Handoff staleness detection required** (portfolio-wide HC#15). V5 formula-hash check per calc when consuming calc-documenter handoff. Per-calc mismatch forces local-extract fallback for that specific calc; other calcs with fresh hash-match still use handoff data.

**HC#14 Reference-file grounding.** All 8 rules cite detection criteria and worked examples in `skill-expertise/rule_catalog.md`. Threshold defenses (CH-NESTING-04 depth threshold, CH-HARDCODED-05 hardcoded-value catalog, CH-DEPRECATED-06 deprecated-function list, CH-LOD-OVERUSE-08 pattern precedence) all documented with empirical grounding.

**HC#15 Wide-workbook scale handling.** For workbooks with 50+ calcs, skill emits a wide-workbook-notice in Tier A (this workbook has N calcs; Tier A truncates to top 5 per severity tier, full findings list in Tier B). Per-calc evaluation still runs on every calc; only presentation truncates.

**HC#16 Case-insensitive resolve-field concern acknowledged.** `resolve-field` is case-sensitive (a known platform gap). CH-NAMING-01 detection uses handoff data preferentially when available; local-extract fallback exact-case matches per rule and does not attempt case-insensitive fuzzy matching.

## Validation Gate (5-Check)

- **V1 Rule Coverage.** All 8 rules evaluated against every calc in the workbook.
- **V2 Signal-Source Attribution.** Every rule evaluation per calc has `signal_source` populated.
- **V3 Ordering Determinism.** Findings sort key deterministic per HC#9.
- **V4 Handoff Completeness.** `handoff_consumed`, `stale_handoff`, and per-calc `signal_source` all populated.
- **V5 Autofix Routing Correctness.** Every autofixable finding (CH-NAMING-01, CH-HARDCODED-05, CH-DEPRECATED-06) has `autofixable: true` and `routing.calc_linter: true` set.

## Two-Tier Delivery

**Tier A (chat).** Compact summary: workbook name, calc count, findings by severity tier, top 5 Warning-tier findings with Desktop-fix instructions and autofix-routing flags where applicable.

Template:

```
**Calc Hygiene Scan: {workbook_name}**
Calcs evaluated: {N}
Findings: {N_warning} Warning, {N_info} Info, {N_sentinel} sentinel
Autofixable findings routing to calc-linter: {N}
Handoff consumed: {yes/no}, stale: {yes/no}
Diff mode: {fresh_scan | reused_verbatim | targeted_rescan}

Top 5 Warning-tier findings:
1. [{calc_name}] {rule_id}: {evidence}. Desktop fix: {manual_fix_instruction}. Autofixable: {yes/no}.
2. ...
3. ...

Routing offered: calc-linter (for autofixable findings), calc-optimizer (for CH-NESTING-04 and CH-LOD-OVERUSE-08).
Save full hygiene report to file?
```

**Tier B (opt-in file save).** Full report `.md` written to user-confirmed path per HC#11. Includes per-calc detail, per-rule evidence citation, Desktop-fix instructions, autofix-routing flags, and handoff YAML block.

## Handoff Schema

Emits `calc_hygiene_report/1`. Downstream: `calc-linter` (autofix for CH-NAMING-01, CH-HARDCODED-05, CH-DEPRECATED-06), `calc-optimizer` (rewrite for CH-NESTING-04, CH-LOD-OVERUSE-08), `workbook-auditor` (hygiene delta tracking).

Fields include: workbook (name, fingerprint), diff_mode, handoff_consumed, stale_handoff, calcs[] with per-calc rules_triggered / rules_cleared / sentinels / signal_source, totals (warning_count, info_count, sentinel_count, autofixable_count), routing_offered (calc_linter, calc_optimizer, workbook_auditor), v_gate results.

## Common Mistakes (Anti-Patterns)

- **Auto-invoking calc-linter.** HC#1 read-only + HC#12 routing-only. Skill emits `routing.calc_linter: true`; user opts in.
- **Silent stale-handoff rendering.** HC#13 requires per-calc V5 formula-hash check. Stale-per-calc forces local-extract fallback for that calc.
- **Rewriting author caption.** HC#6 preserves author intent. Skill supplements around it; never paraphrases.
- **Fabricating deprecation timelines.** HC#4. CH-DEPRECATED-06 uses the locked deprecated-function list in `skill-expertise/rule_catalog.md`; no inferred deprecation.
- **CH-NAMING-01 fuzzy-match on case-insensitive `resolve-field`.** HC#16 blocks. Exact-case per rule; no fuzzy matching to work around the shared-tool gap.
- **Silent file write on Tier B save.** HC#11 requires path confirmation.
- **Skipping a rule on a specific calc.** HC#5 requires all 8 rules evaluated per calc, with sentinel for unresolvable signals.

## Adjacent-Skill Routing

- **Upstream opportunistic:** `calc-documenter` (produces `calc_documentation/1` handoff).
- **Downstream opt-in per rule:**
  - CH-NAMING-01, CH-HARDCODED-05, CH-DEPRECATED-06 → `calc-linter` (autofix).
  - CH-NESTING-04, CH-LOD-OVERUSE-08 → `calc-optimizer` (rewrite).
  - CH-UNUSED-03 → `calc-linter` for delete workflow (destructive).
- **Downstream general:** `workbook-auditor` for hygiene delta across runs, `publish-readiness` for pre-publish hygiene sweep.
- **Refusal routes:** single-calc explanation → `calc-explainer`; performance rewrite → `calc-optimizer`; NULL diagnosis → `calc-debugger`; migration → `calc-migrator`; authoring → `calc-writer`.

## Known Limitations

- **Autofix out of scope.** Every autofixable finding emits routing signal; actual application is calc-linters job.
- **CH-LOD-OVERUSE-08 detection is heuristic.** Uses `skill-expertise/explanation_patterns.md` precedence rules; flags LOD-when-simpler-would-work but user acknowledges per finding.
- **CH-NESTING-04 threshold is heuristic.** Documented in `skill-expertise/rule_catalog.md` with defense.
- **CH-DEPRECATED-06 list is snapshot.** Deprecated-function list documented in reference file.
- **`resolve-field` case-sensitivity concern**. CH-NAMING-01 exact-case matches; no fuzzy fallback.
- **Cross-datasource references** in CH-CROSSDS-07 rely on handoff `cross_datasource_reference` flag when available; local-extract fallback flags cross-DS references but cannot verify rationale (author intent required).

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
