# Calc Migrator

Migrate one Tableau calculated field from a source datasource to a target datasource in the same open workbook, with per-field consent and read-back verification.

**Example:** "Migrate `Profit Ratio` from Sample - Superstore to Orders (Migrated)."

***

## What it does

Takes one calculated field, resolves every field reference against the target datasource, remaps them with your explicit approval per field, and writes a sibling copy on the target with a `_migrated` suffix. Every write is verified by re-reading the target calc so a manual paste with a typo never gets marked applied.

## When to use it

- "I duplicated a datasource and need to move my calcs to the new one."
- "I built a calc on dev and want to move it to prod without hand-editing every field."
- "I have a source and target that share field names and I need one calc ported cleanly."

## When NOT to use it

- Not for bulk-calc migration (not supported).
- Not for cross-workbook migration (out of scope).
- Not for rewriting calc semantics like aggregate-to-LOD (route to calc-optimizer).
- Not for authoring new calcs from scratch (route to calc-writer).
- Not for producing the before/after report (route to calc-migrator-diff-report after migration).

## How to trigger it

- "migrate this calc"
- "move calc to another datasource"
- "calc-migrator"
- "port this calc to another data source"

## What you'll need

- Tableau Desktop 2024.3 or later with the Tableau Desktop MCP agent connected.
- Source and target datasources both loaded in the same open workbook.
- Source and target sharing every field name the calc references (same-schema only).
- A fresh `calc_documentation/1` handoff from calc-documenter in session context. Run calc-documenter first if you have not already.

## Example walkthrough

**Input:** Migrate `Profit Ratio` from Sample - Superstore to Orders (Migrated).

**Output:**

```
Phase 2 field resolution:
  [Profit] → [Orders (Migrated)].[Profit]   approve? y
  [Sales]  → [Orders (Migrated)].[Sales]    approve? y

Phase 6 final go-ahead:
  Target calc: Profit Ratio_migrated
  Formula:     SUM([Profit]) / SUM([Sales])
  Proceed? y

Read-back verification: PASS. Target calc byte-identical to composed formula.
Status: applied.
```

Every field mapping asked for explicit approval; the composed formula was shown before writing; the post-write read-back confirmed the calc landed correctly.

## What you get back

- One migrated calc on the target datasource, named `{original}_migrated`.
- A `calc_migration_report/1` handoff in session context capturing source formula, target formula, field remaps, sentinels, validation status, and formula hash.
- A routing offer to calc-migrator-diff-report if you want a before/after audit.

## Limitations

- Same-schema only. If any required field has no target-DS counterpart, the migration is refused and routed to calc-writer for manual authoring.
- `author-calc` write path is unreliable in some sessions. If the write fails, the skill instructs you to paste the formula manually in Desktop, then verifies via read-back before marking applied.
- Fresh parameters created in Desktop just before the migration may not resolve on the first attempt (platform gap). Retry after a Data pane refresh.
- One calc per invocation. Bulk-calc migration is refused per HC#1.

## Troubleshooting

- **"No calc-documenter handoff in session."** Run calc-documenter on the source datasource first, then re-invoke calc-migrator.
- **"Field X has no counterpart on the target datasource."** The rule is same-schema only. Either add the field on the target or route to calc-writer for manual authoring.
- **"author-calc failed with a stale-session error."** The read path may still work. The skill will fall back to manual-paste instructions and verify the paste via read-back. Do not skip the verification.
- **"Migration marked applied but the calc looks wrong."** Should never happen with HC#17 read-back verification. If it does, file a bug against calc-migrator; the read-back check should have caught it.

## Support

File issues in the Tableau Studio Agent Skills repo.
