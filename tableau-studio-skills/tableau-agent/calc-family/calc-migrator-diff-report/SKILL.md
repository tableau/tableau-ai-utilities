---
name: calc-migrator-diff-report
description: "Use when the user says 'Diff my migration', 'review migration output', 'show migration changes', 'calc migration diff'. After a calc migration, compares each calc's source and target formulas, field remaps, and validation status, and flags what needs follow-up. Read-only."
---

# Calc Migrator Diff Report

## When to use (full trigger detail)

Produce a per-calc source-DS vs. target-DS formula diff report from a calc-migrator run. Consumes calc_migration_report/1 handoff and re-validates each calc against current workbook state via V5 formula-hash and workbook fingerprint per portfolio-wide HC#15. For every migrated calc. source formula, target formula, field remaps applied, sentinels emitted, validation status, downstream routing signals. Read-only. Two-tier delivery. compact Tier A chat summary with top 5 findings plus opt-in Tier B full per-calc detail file save as .md or .txt per HC#11. Trigger with calc migration diff, diff my migration, review migration output, calc-migrator-diff-report, show migration changes, per calc migration diff. Do NOT trigger on. running a migration itself (route to calc-migrator), general hygiene audit (route to calc-hygiene-scan), rewriting migrated calcs (route to calc-writer or calc-optimizer), diagnosing NULL returns post-migration (route to calc-debugger), or workbook-level summary handoff (route to workbook-summary-onepager).

## Purpose

Produce a per-calc source-DS vs. target-DS formula diff report from a `calc-migrator` run. Consumes `calc_migration_report/1` handoff and re-validates each calc against current workbook state per portfolio-wide HC#15 staleness detection. Read-only. Every finding cites source formula, target formula, field remaps applied during migration, sentinels emitted, validation status, and downstream routing signal (calc-migrator re-run for unresolved, calc-writer for sentinels, calc-debugger for validation failures).

## Trigger Conditions

- calc migration diff
- diff my migration
- review migration output
- calc-migrator-diff-report
- show migration changes
- per calc migration diff
- what did the migration change
- audit my migration

## Do NOT Trigger On

- Running a migration itself → route to `calc-migrator`.
- General calc hygiene audit → route to `calc-hygiene-scan`.
- Rewriting migrated calcs to be simpler or faster → route to `calc-writer` or `calc-optimizer`.
- Diagnosing NULL returns post-migration → route to `calc-debugger`.
- Workbook-level summary handoff for stakeholders → route to `workbook-summary-onepager`.
- Explaining a single migrated calc in plain language → route to `calc-explainer`.
- Documenting every calc in detail (full dictionary) → route to `calc-documenter`.

## Scope Boundaries

- **IN.** One migration run per invocation. Read-only. Per-calc source-DS vs. target-DS formula diff. Required `calc_migration_report/1` handoff consumption with V5 formula-hash per-calc + workbook-fingerprint staleness detection per HC#15. Field-remap surfacing per calc. Sentinel surfacing per calc (whatever calc-migrator emitted as `unable to determine` gets its own diff-report finding). Validation-status surfacing per calc. Bulk-migration handling per HC#16 (50+ calcs). Downstream routing signals per finding. Handoff schema `calc_migration_diff/1`. Two-tier delivery: compact Tier A chat + opt-in Tier B file save as `.md` or `.txt`.
- **OUT.** Any workbook mutation. Running the migration itself (route to calc-migrator). Rewriting migrated calcs (route to calc-writer / calc-optimizer). NULL-return diagnosis (route to calc-debugger). Multi-migration-run comparison (single-migration-run diff only). PDF or DOCX output (`.md` and `.txt` only). Diff against prior migration runs.

## The Per-Calc Diff Schema (Locked)

Every diff finding cites a `finding_type`. Multi-type findings tier by highest severity. Full detection criteria, evidence patterns, and worked examples in `skill-expertise/diff_catalog.md`.

| # | Finding Type | ID | Severity | Signal source | Downstream routing |
|---|---|---|---|---|---|
| 1 | Clean migration (formula changed, all fields remapped, validated) | DIFF-CLEAN-01 | Info | handoff + re-validation | None (no action needed) |
| 2 | Field-remap applied | DIFF-REMAP-02 | Info | handoff `field_remaps[]` | None (informational) |
| 3 | Sentinel emitted by calc-migrator (unresolved field, unresolvable calc) | DIFF-SENTINEL-03 | Warning | handoff `sentinels[]` | calc-writer (manual authoring) |
| 4 | Validation failure post-migration (target formula fails syntax or type check) | DIFF-VALIDATION-04 | Warning | handoff `validation_status` + re-validation | calc-debugger (NULL / error diagnosis) |
| 5 | Staleness detected (source workbook state changed since migration ran) | DIFF-STALE-05 | Warning | V5 formula-hash mismatch per calc, workbook-fingerprint mismatch | calc-migrator (re-run) |
| 6 | Unmigrated calc (in source but not in migration report) | DIFF-UNMIGRATED-06 | Warning | source-DS calc list vs. handoff `migrated_calcs[]` | calc-migrator (re-run with wider scope) |
| 7 | Formula-identical migration (target formula byte-identical to source; no remap needed) | DIFF-IDENTICAL-07 | Info | handoff formula comparison | None (informational; may indicate no-op migration) |

**Multi-type tagging.** A calc can fire multiple finding types (e.g., DIFF-REMAP-02 + DIFF-VALIDATION-04 both fire when field remap applied but target formula still fails validation). Skill emits all triggered finding IDs in `findings_triggered[]`; severity tier set by highest match. Deterministic sort per HC#10: severity tier (Warning → Info) → finding ID ascending → calc name alphabetical.

**Fallback discipline (HC#5).** When diff detection depends on data thats unavailable per calc (handoff missing formula body, re-validation tool call fails), skill emits `unable to determine` sentinel per HC#5 for that specific finding type on that specific calc. Other finding types on the same calc still evaluate.

## Workflow Phases

- **Phase 0 Scope.** Confirm `calc_migration_report/1` handoff is available in session context. If missing, stop and tell the user to run `calc-migrator` first — do not proceed to Phase 1 on a missing handoff. Confirm workbook is open via `get-workbook-inventory`; if the call fails, returns no workbook, or the session is disconnected, stop and tell the user to confirm Tableau Studio is open with a workbook loaded. Ensure one migration run per invocation per HC#2.
- **Phase 1 Handoff Verification.** Verify `calc_migration_report/1` handoff completeness. Field mapping from calc-migrator's `calc_migration_report/1`: `source_datasource` = `source.datasource`; `target_datasource` = `target.datasource`; the single migrated calc is `migrated_calcs[0]` with `source_formula` = `source.formula`, `target_formula` = `target.formula`, `field_remaps[]` = `consent_log[]`, `sentinels[]` = `unresolved_references[]`, `validation_status` = `status` plus `v_gate`. Apply this mapping before checking completeness. Required fields: `source_datasource`, `target_datasource`, `migrated_calcs[]` with per-calc `source_formula`, `target_formula`, `field_remaps[]`, `sentinels[]`, `validation_status`. If any required field is missing on the handoff itself, treat the run as incomplete and emit `handoff_incomplete: true` in output metadata; skill can still render diff for the calcs that do have complete data, but flags the handoff as partial. Populate workbook-fingerprint from `get-workbook-inventory` for HC#15 comparison in Phase 2. **Single-fetch discipline:** `get-workbook-inventory` is called once in Phase 1; its result (workbook fingerprint and inventory snapshot) is cached and reused for both the Phase 1 completeness check and the Phase 2 staleness re-validation — never re-fetched mid-run.
- **Phase 2 Re-Validation (numbered checklist).**
  1. For each calc in `migrated_calcs[]`, verify V5 formula-hash on the target formula against current workbook state. `formula-hash` and `workbook fingerprint` are values computed by this skill (a hash of the formula text and a hash of overall workbook state), not native Tableau APIs or Tableau-exposed properties — they exist purely for this skills own staleness bookkeeping. If the target formulas formula-hash from the handoff does not match the current workbooks formula-hash for that calc name on the target datasource, mark the calc `stale: true` and fire DIFF-STALE-05.
  2. Verify workbook fingerprint from the handoff matches current workbook fingerprint per HC#15. If mismatch, mark the whole run `run_stale: true`; per-calc staleness still evaluated individually via step 1.
  3. Re-validate every calcs target formula against the target datasource. Batch `resolve-field` calls in groups of 20 per portfolio-wide HC batching cap (matches calc-migrators Phase 2 pattern). If a batch call fails outright (timeout, disconnect), retry that batch once; on a second failure, emit `unable to determine` sentinel for every calc dependent on that batchs resolution and continue with remaining batches — do not abort the whole diff.
  4. For each calc, apply the 7 finding types from `skill-expertise/diff_catalog.md`. Populate `findings_triggered[]` with the finding ID, evidence citation, and `signal_source`.
  5. Enumerate source-DS calc list via `list-available-fields` and compare to handoff `migrated_calcs[]`. Any source calc not in the handoff fires DIFF-UNMIGRATED-06.
  6. For findings with unresolvable signals, emit `unable to determine` sentinel per HC#5 rather than skipping.
- **Phase 3 Severity Tiering + Deterministic Sort.** Sort per HC#10: severity tier (Warning → Info) → finding ID ascending → calc name alphabetical. Warning-tier findings surface in Tier A top 5.
- **Phase 4 Validate.** Run the 5-check V-gate: finding coverage, per-calc signal-source attribution, ordering determinism, handoff completeness, downstream routing correctness. If any check fails, do not discard the run: re-run only the failing checks underlying data pull once (e.g., re-fetch signal-source labels for V2, re-sort for V3), then re-validate that check. If it fails a second time, deliver Tier A with the specific V-check named as unresolved and the affected calcs/findings listed, rather than blocking delivery entirely or silently passing.
- **Phase 5 Deliver.** Two-tier: compact Tier A chat summary with counts and top 5 Warning-tier findings (staleness, validation failures, sentinels, unmigrated calcs); opt-in Tier B file save requires user path confirmation per HC#11.

## Hard Constraints

**HC#1 Read-only always.** Never mutates the workbook. Never invokes calc-migrator to re-run. Every finding is a diagnostic; downstream routing signals emitted but skill never chains invocation.

**HC#2 One migration run per invocation.** Multi-migration-run comparison refused.

**HC#3 7-finding-type catalog locked.** No finding type omitted, no fabricated finding type added. Detection follows the criteria in `skill-expertise/diff_catalog.md`.

**HC#4 Refuse to fabricate.** No inferred field remaps, no guessed migration rationale, no invented validation results. Sentinels: `null`, `unable to determine`, empty-state prose.

**HC#5 Sentinel discipline per finding per calc.** When a findings detection fails on a specific calc (handoff missing formula body, re-validation tool call fails for that calc), emit `unable to determine` sentinel for that finding on that calc. Other findings on the same calc still evaluate; other calcs still get all 7 finding types.

**HC#6 Handoff data quoted verbatim.** Source formula, target formula, field remaps, and sentinels from calc-migrators handoff are quoted byte-identical. Skill supplements around handoff data; never rewrites or paraphrases the migration output.

**HC#7 Sentinel discipline for zero-calc migration.** If handoff `migrated_calcs[]` is empty, exit cleanly with no calcs migrated in this run; diff report not applicable. Zero-calc source datasource also exits cleanly.

**HC#8 Diff-mode transparency** (portfolio-wide HC#13). Repeat invocations against unchanged handoff state emit `diff_mode: reused_verbatim` in Tier A. Fresh-scan / reused-verbatim / targeted-rescan enum. Note: `diff_mode` here refers to the diff-reports own idempotency, not to the migration diff content itself — the report is always presenting migration-diff content, but `diff_mode` tracks whether this specific report invocation is a fresh render or a re-render of unchanged inputs.

**HC#9 Ordering determinism** (portfolio-wide HC#14). Sort key locked: severity tier → finding ID → calc name alphabetical. Same input produces byte-identical top-5 and full findings list across runs.

**HC#10 Handoff-or-revalidation labeled per finding.** Every finding records `signal_source: handoff | revalidation | handoff+revalidation | unresolved` so downstream consumers know evidence origin. `handoff` = pure handoff data (e.g., field remap surfacing); `revalidation` = current-state re-check (e.g., staleness detection); `handoff+revalidation` = combines both (e.g., validation failure confirmed against current state).

**HC#11 Never silent file write.** Tier B save requires user path confirmation AND format choice (`.md` or `.txt`). No default writes to Downloads.

**HC#12 Downstream routing signals, never routing invocation.** For each Warning-tier finding, emit routing signals: DIFF-SENTINEL-03 → `routing.calc_writer: true`, DIFF-VALIDATION-04 → `routing.calc_debugger: true`, DIFF-STALE-05 and DIFF-UNMIGRATED-06 → `routing.calc_migrator: true`. Skill never invokes downstream skills directly per HC#1; user opts in.

**HC#13 Handoff staleness detection required** (portfolio-wide HC#15). V5 formula-hash check per calc when consuming calc-migration handoff. Per-calc mismatch fires DIFF-STALE-05 for that specific calc; other calcs with fresh hash-match still render normally. Workbook-fingerprint check per HC#15 fires run-level staleness.

**HC#14 Reference-file grounding.** All 7 finding types cite detection criteria and worked examples in `skill-expertise/diff_catalog.md`. Threshold defenses (V5 formula-hash discipline, validation-status semantics from calc-migrator, source-vs-target formula comparison rules) all documented with cross-references to calc-migrators contract.

**HC#15 Wide-workbook / bulk-migration scale handling.** For migration runs with 50+ calcs, skill emits a bulk-migration-notice in Tier A (this migration touched N calcs; Tier A truncates to top 5 per severity tier, full findings list in Tier B). Per-calc evaluation still runs on every calc; only presentation truncates. Warning-tier findings always surface fully in Tier A even beyond 5 if all are Warning; only Info-tier truncates. Per-calc evaluation cost scales linearly with calc count — there is no upper bound on migration size beyond the resolve-field groups-of-20 batching cap in Phase 2 step 3; a 200-calc migration runs the same per-calc logic as a 5-calc one, just in more batches.

**HC#16 Handoff completeness check.** Required fields on `calc_migration_report/1`: `source_datasource`, `target_datasource`, `migrated_calcs[]` (each with `source_formula`, `target_formula`, `field_remaps[]`, `sentinels[]`, `validation_status`). If handoff is missing any required field on the run-level, refuse with a route to re-run calc-migrator. If handoff is present but a specific calcs fields are incomplete, emit sentinels for those calcs per HC#5 and continue rendering the others. `resolve-field` case-sensitivity concern (a known platform gap, shared with calc-family): re-validation uses exact-case matches per HC#5 fallback.

## Validation Gate (5-Check)

- **V1 Finding Coverage.** All 7 finding types evaluated against every migrated calc plus any unmigrated source calcs.
- **V2 Signal-Source Attribution.** Every finding has `signal_source` populated per HC#10.
- **V3 Ordering Determinism.** Findings sort key deterministic per HC#9.
- **V4 Handoff Completeness.** `handoff_verified`, `handoff_incomplete`, `run_stale`, and per-calc `stale` flags all populated. Workbook-fingerprint match verified.
- **V5 Downstream Routing Correctness.** Every Warning-tier finding has the correct `routing.*` flag set per HC#12 (SENTINEL-03 → calc_writer, VALIDATION-04 → calc_debugger, STALE-05 / UNMIGRATED-06 → calc_migrator).

## Two-Tier Delivery

**Tier A (chat).** Compact summary: source datasource, target datasource, calcs migrated, findings by severity tier, top 5 Warning-tier findings with per-calc detail and downstream routing signals where applicable.

Template:

```
**Calc Migration Diff Report: {source_ds} → {target_ds}**
Calcs migrated: {N}
Findings: {N_warning} Warning, {N_info} Info, {N_sentinel} sentinel
Handoff verified: {yes/no}, run stale: {yes/no}
Diff mode: {fresh_scan | reused_verbatim | targeted_rescan}

Top 5 Warning-tier findings:
1. [{calc_name}] {finding_id}: {evidence}. Source: `{source_formula}`. Target: `{target_formula}`. Routing: {calc_migrator | calc_writer | calc_debugger}.
2. ...

Routing offered: calc-migrator (for stale / unmigrated), calc-writer (for sentinels), calc-debugger (for validation failures).
Save full diff report to file? (.md or .txt)
```

**Tier B (opt-in file save).** Full report `.md` (default) or `.txt` written to user-confirmed path per HC#11. Unbounded length. Per-calc detail: source formula, target formula, field-remap list, sentinels emitted, validation status, staleness status, downstream routing flags. Handoff YAML block appended.

## Handoff Schema

Emits `calc_migration_diff/1`. Downstream: `calc-migrator` (re-run for STALE-05 / UNMIGRATED-06), `calc-writer` (manual authoring for SENTINEL-03), `calc-debugger` (NULL / error diagnosis for VALIDATION-04), `workbook-auditor` (migration-diff delta tracking).

Fields include: source_datasource, target_datasource, run_timestamp (from calc-migrator handoff), diff_mode, handoff_verified, handoff_incomplete, run_stale, workbook_fingerprint_current, workbook_fingerprint_migration, calcs[] with per-calc findings_triggered / signal_source / stale / routing, totals (warning_count, info_count, sentinel_count, unmigrated_count), routing_offered (calc_migrator, calc_writer, calc_debugger, workbook_auditor), v_gate results.

## Common Mistakes (Anti-Patterns)

- **Auto-invoking calc-migrator to re-run.** HC#1 read-only + HC#12 routing-only. Skill emits `routing.calc_migrator: true` on STALE-05 / UNMIGRATED-06; user opts in.
- **Silent stale-handoff rendering.** HC#13 requires per-calc V5 formula-hash check plus run-level workbook-fingerprint check. Stale-per-calc fires DIFF-STALE-05; stale-per-run marks the whole run.
- **Rewriting handoff data.** HC#6 quotes source/target formulas verbatim. Skill supplements around them; never paraphrases.
- **Fabricating field remaps.** HC#4. DIFF-REMAP-02 evidence comes from handoff `field_remaps[]`; no inferred remaps.
- **Missing DIFF-UNMIGRATED-06 coverage.** HC#3 + V1 require enumerating source-DS calc list and comparing to handoff `migrated_calcs[]`. Source calcs absent from handoff fire this finding.
- **Silent file write on Tier B save.** HC#11 requires path confirmation AND format choice (`.md` or `.txt`).
- **Skipping a finding on a specific calc.** HC#5 requires all 7 finding types evaluated per calc (where applicable), with sentinel for unresolvable signals.
- **Confusing diff-mode enum with diff content.** HC#8 clarifies: `diff_mode` tracks this skills own idempotency across re-invocations; the migration-diff content itself is always the same 7-finding-type report.

## Adjacent-Skill Routing

- **Upstream required:** `calc-migrator` (produces `calc_migration_report/1` handoff).
- **Downstream opt-in per finding:**
  - DIFF-SENTINEL-03 → `calc-writer` (manual authoring for calcs calc-migrator couldnt resolve).
  - DIFF-VALIDATION-04 → `calc-debugger` (NULL / error diagnosis for target formula that fails validation).
  - DIFF-STALE-05 → `calc-migrator` (re-run because workbook state changed since migration).
  - DIFF-UNMIGRATED-06 → `calc-migrator` (re-run with wider scope to catch missed source calcs).
- **Downstream general:** `workbook-auditor` for migration-diff delta across runs.
- **Refusal routes:** running migration → `calc-migrator`; hygiene audit → `calc-hygiene-scan`; rewriting migrated calcs → `calc-writer` / `calc-optimizer`; NULL diagnosis → `calc-debugger`; workbook-level summary → `workbook-summary-onepager`; single-calc explanation → `calc-explainer`; full documentation → `calc-documenter`.

## Known Limitations

- Supports `.md` and `.txt` only.
- **DIFF-VALIDATION-04 depends on calc-migrators `validation_status` field being populated.** If calc-migrator emitted the field but with a coarse-grained value (e.g., `passed` / `failed` without per-check breakdown), diff-report inherits that granularity and cannot decompose further.
- **DIFF-UNMIGRATED-06 relies on complete source-DS calc enumeration via `list-available-fields`.** If that tool returns incomplete calc lists on a specific datasource, DIFF-UNMIGRATED-06 may miss calcs that should have fired it. HC#5 sentinel discipline applies.
- **`resolve-field` case-sensitivity concern**. Re-validation uses handoff data preferentially; local-extract fallback exact-case matches per rule.
- **Bulk-migration Tier A cap at top 5 per severity may hide Info-tier detail.** By design: Warning-tier always surfaces fully; Info-tier truncates. Full Info detail in Tier B.

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
