# Calc Migrator Diff Report

Produce a per-calc source-DS vs. target-DS formula diff report from a calc-migrator run. Re-validates each calc against current workbook state via V5 formula-hash and workbook fingerprint.

**Example:** "Diff my calc migration."

***

## What it does

Consumes calc-migrator's `calc_migration_report/1` handoff and re-validates every migrated calc against current workbook state. For each calc it surfaces source formula, target formula, field remaps applied, sentinels emitted, validation status, and a downstream routing signal (calc-writer for sentinels, calc-debugger for validation failures, calc-migrator for staleness or unmigrated calcs). Read-only.

## When to use it

- "I just ran calc-migrator and want a before/after report."
- "I want to review what changed in each migrated calc without opening every one in Desktop."
- "I want to know which calcs went stale after I edited them post-migration."

## When NOT to use it

- Not for running the migration itself (route to calc-migrator).
- Not for general calc hygiene audit (route to calc-hygiene-scan).
- Not for rewriting migrated calcs to be simpler or faster (route to calc-writer or calc-optimizer).
- Not for diagnosing NULL returns post-migration (route to calc-debugger).
- Not for workbook-level summary handoff (route to workbook-summary-onepager).
- Not for explaining a single migrated calc (route to calc-explainer).
- Not for documenting every calc (route to calc-documenter).

## How to trigger it

- "calc migration diff"
- "diff my migration"
- "review migration output"
- "calc-migrator-diff-report"
- "show migration changes"
- "per calc migration diff"
- "what did the migration change"
- "audit my migration"

## What you'll need

- Tableau Desktop 2024.3 or later with the MCP agent connected.
- The workbook open.
- A fresh `calc_migration_report/1` handoff in session context. Run calc-migrator first if you have not already; the skill refuses without a handoff.

## Example walkthrough

**Input:** Diff the migration from Sample - Superstore to Orders (Migrated).

**Output:**

```
Calc Migration Diff Report: Sample - Superstore -> Orders (Migrated)
Calcs migrated: 6 (plus 1 intentionally unmigrated)
Findings: 4 Warning, 3 Info
Handoff verified: yes. Run stale: no. Diff mode: fresh_scan.

Warning-tier:
  1. [DiffStale] DIFF-STALE-05: per-calc formula-hash mismatch.
     Migrated as SUM([Profit]) * 1.05; current target is SUM([Profit]) * 1.10.
     Routing: calc-migrator (re-run).
  2. [DiffSentinel] DIFF-SENTINEL-03: Custom Region unresolved on target.
     Routing: calc-writer.
  3. [DiffValidation] DIFF-VALIDATION-04: Price Weight parameter not in
     target-DS scope. Routing: calc-debugger.
  4. [DiffUnmigrated] DIFF-UNMIGRATED-06: excluded from migration scope.
     Routing: calc-migrator (re-run with wider scope).

Info-tier:
  5. [DiffClean] DIFF-CLEAN-01: clean, both fields remapped, verified.
  6. [DiffRemap] DIFF-REMAP-02: 2 remaps applied (Sales, Discount).
  7. [DiffIdentical] DIFF-IDENTICAL-07: byte-identical, no remaps.

Routing offered: calc-migrator (2), calc-writer (1), calc-debugger (1).
Save full report to file? (.md or .txt)
```

## What you get back

- Tier A: compact chat summary with top-5 Warning findings and routing counts.
- Tier B (opt-in): full per-calc report saved as `.md` or `.txt`.
- A `calc_migration_diff/1` handoff for downstream consumers (workbook-auditor).
- Dual-mechanism staleness detection: per-calc formula-hash mismatch AND run-level workbook-fingerprint mismatch each fire independently.

## Limitations

- Single-migration-run scope.
- Supports `.md` and `.txt` only.
- DIFF-VALIDATION-04 inherits calc-migrator's `validation_status` field granularity. If calc-migrator emits only `passed` / `failed` without per-check breakdown, this skill inherits that granularity.
- DIFF-UNMIGRATED-06 relies on complete source-DS calc enumeration via `list-available-fields`. If that tool returns incomplete calc lists (rare), findings may miss calcs.
- Bulk-migration (50+ calcs) offered as file-first output. If you opt into live re-validation on a large batch, the skill re-warns about session-timeout risk first.

## Troubleshooting

- **"Handoff missing. Please run calc-migrator first."** Expected refusal per Phase 0. Run calc-migrator against your target migration first, then re-invoke this skill.
- **"DIFF-STALE-05 fired on a calc I didn't touch."** Something in the workbook state changed since the migration ran. Check the fingerprint mismatch details; a workbook-level change (unrelated edit, save) cascades to run-level staleness.
- **"Skill saved as applied but the diff shows validation failure."** Expected. DIFF-VALIDATION-04 fires on `passed_with_warnings` too. Route to calc-debugger to review.

## Support

File issues in the Tableau Studio Agent Skills repo.
