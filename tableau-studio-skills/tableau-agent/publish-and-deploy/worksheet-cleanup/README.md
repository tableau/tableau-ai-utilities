# Worksheet Cleanup

Audit a Tableau workbook for stale worksheet scaffolding (hidden sheets, scratch calcs, dead-field placements, orphan filters) and remove it with per-artifact consent.

**Example:** "Clean up the worksheets in this workbook."

***

## What it does

Runs a 7-check catalog against one worksheet per invocation, tiers findings by severity, and applies deletions only after you approve each artifact individually. Read-only by default; mutation is opt-in. Every destructive step re-verifies workbook state before proceeding so nothing gets removed based on stale detection.

## When to use it

- "I inherited a workbook with a bunch of hidden test sheets I don't need."
- "My workbook has scratch calcs and dead-field placements slowing it down."
- "I want a pre-publish sweep to remove worksheet-level junk."

## When NOT to use it

- Not for dashboard-level cleanup like zone removal or container flattening (out of scope).
- Not for renaming worksheets (not supported).
- Not for calc cleanup (route to calc-linter and calc-hygiene-scan).
- Not for multi-workbook bulk cleanup (out of scope).
- Not for removing a worksheet referenced by a dashboard action config without your explicit candidate-with-warning acknowledgment.

## How to trigger it

- "clean up worksheets"
- "remove orphan sheets"
- "worksheet-cleanup"
- "audit unused worksheets"
- "prune this workbook"

## What you'll need

- Tableau Desktop 2024.3 or later with the MCP agent connected.
- The workbook open and saved at least once (unsaved changes may skew the mtime baseline).
- Write access to the workbook file for the mutation phase.

## Example walkthrough

**Input:** Clean up worksheets in the currently open workbook.

**Output:**

```
Phase 1 inventory (read-only):
  7-check catalog fired against 24 worksheets.
  Findings: 3 Warning, 2 Info.

Top findings:
  1. Cleanup-HiddenSheet-01 (Warning): "test_v2_hidden" hidden and unreferenced. Recommend delete.
  2. Cleanup-ScratchCalc-02 (Warning): "scratch_pad" has no shelf placements and no downstream refs.
  3. Cleanup-DeadField-03 (Warning): "Regional Trend" references [Old Segment] which no longer exists.

Phase 2 mutation (opt-in):
  Remove "test_v2_hidden"? y
  Workbook-fingerprint verified. Removing...
  Remove "scratch_pad"? y
  ...
```

Every deletion prompted individually; nothing was batched under a single approval.

## What you get back

- A cleanup report showing what was found and what was removed.
- A sibling-copy workbook by default (`{name}_cleaned.twbx`). `--in-place` only runs on explicit request.
- A `cleanup_report/1` handoff for downstream consumers (publish-readiness, workbook-auditor).

## Limitations

- One worksheet per invocation for the mutation phase. Bulk-worksheet deletion is refused.
- Cleanup-HiddenSheet-01 detection relies on Story-based hiding; right-click dashboard hide is not directly available in this Tableau version (platform gap).
- Dashboard-action references can be silently unreadable (platform gap). Findings flagged as candidate-with-warning require your explicit acknowledgment before removal.
- No undo. Sibling-copy default protects against irreversible mistakes; use `--in-place` only when you have a separate backup.

## Troubleshooting

- **"Workbook-fingerprint mismatch before delete."** The workbook state changed between Phase 1 and Phase 2 (someone else edited it, or you saved it manually). Re-run the inventory to refresh detection.
- **"Cannot verify dashboard-action reference for `sheet_X`."** Platform gap. The finding is emitted as candidate-with-warning; explicitly acknowledge if you want it removed anyway, or skip.
- **"Delete failed but skill marked applied."** Should not happen. If it does, check the sibling copy on disk; the mutation may have written to a temporary path.

## Support

File issues in the Tableau Studio Agent Skills repo.
