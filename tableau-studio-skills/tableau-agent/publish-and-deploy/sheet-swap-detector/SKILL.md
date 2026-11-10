---
name: sheet-swap-detector
description: "Use when the user says 'Duplicate worksheets', 'which sheets can I consolidate?', 'my worksheet list is a mess', 'redundant sheets'. Groups near-duplicate worksheets by type (filter, aggregation, sort, chart type, old version) and recommends how to consolidate each. Read-only."
---

# Tableau Sheet Swap Detector

Scans all worksheets in an open workbook, groups near-duplicates by field signature against a locked 5-cluster taxonomy, and recommends consolidation per cluster. Pairs with worksheet-cleanup (which handles orphans and empties) by owning the fuzzy-match duplicate-detection problem it does not cover.

## When to use (full trigger detail)

Find near-duplicate worksheets in a Tableau workbook and recommend consolidation. Scans all worksheets, groups fuzzy-match duplicates by field signature against a locked 5-cluster taxonomy (A filter variant, B aggregation variant, C sort variant, D chart-type variant, E deprecated version), reports clusters with per-cluster consolidation recommendation and numbered Desktop steps. Read-only. Trigger on "duplicate worksheets", "near-duplicate sheets", "which sheets can I consolidate", "my worksheet list is a mess", "redundant sheets", "cleanup duplicate views". Do NOT trigger for. orphan or empty sheets (route to worksheet-cleanup), unused fields (route to publish-readiness), calc duplication (route to calc-hygiene-scan), authoring or editing anything in Desktop (out of scope).

## Reference files

- **`skill-expertise/cluster-taxonomy.md`.** The locked A-E cluster definitions with field-signature matching rules and per-cluster consolidation recommendations.
- **`skill-expertise/consolidation-patterns.md`.** Named consolidation patterns (dynamic-zone-visibility, dashboard-action swap, delete-older-version) with numbered Desktop steps for each.

## When to use

Author has a workbook with many worksheets and suspects duplication. Wants a map of which ones overlap and what to do about each cluster.

## Hard Constraints

- **HC-1 Read-only.** No mutation.
- **HC-2 Locked A-E cluster taxonomy.** No ad-hoc clusters invented mid-run.
- **HC-3 Honest "no near-duplicates found" verdict.** Do not manufacture clusters.
- **HC-4 Never flag intentional variants as duplicates.** If the author declares a cluster is intentional, record and move on. Do not loop or re-flag.
- **HC-5 Per-cluster recommendation names a specific consolidation pattern** from consolidation-patterns.md. No vague "think about combining these" output.
- **HC-6 Standalone-safe routing.** Handoff to worksheet-cleanup for the actual deletion steps.
- **HC-7 No pasted URLs to community resources.**

## Workflow

**Tools used.** `list-dashboards` (to enumerate dashboards and discover which worksheets are on-dashboard vs. hidden; also used for Cluster E deprecated-version context when a sheet exists in the workbook but is not placed on any dashboard), `list-worksheets` (to enumerate every worksheet in the workbook, including hidden sheets; load-bearing read for cluster membership), `list-available-fields` (to resolve technical field names in Rows / Columns / Marks-card signatures and to confirm aggregation types for Cluster B signature matching), `get-worksheet-xml` (to extract per-sheet field signatures, filter configurations, aggregations, sort orders, and mark types directly from each worksheet; the load-bearing read for A/B/C/D cluster signature matching. Note: `get-dashboard-xml` returns zone layout only, not shelf-level data, and cannot be used for signature extraction), `get-dashboard-xml` (to enumerate which worksheets are placed on which dashboard, and at what index/zone, for Cluster E on-dashboard-vs-hidden context only), `get-workbook-inventory` (to pull last-modified metadata for Cluster E version-ordering heuristics; use when deprecated-version candidates surface and the author needs guidance on which copy is older).

Steps:

1. Call `list-worksheets` to enumerate all worksheets. If more than 50, confirm with author before proceeding (large-workbook scan can be noisy; offer to scope to a specific dashboard or set of sheets).
2. Call `get-worksheet-xml` once per worksheet to pull its field signature (Rows pills, Columns pills, Marks-card field placements, filter configurations, aggregation choices, sort orders, mark type). `get-dashboard-xml` returns zone layout only and does not carry shelf-level data. Do not rely on it for signature extraction.
3. Build a signature hash per sheet. Group sheets whose signatures match the A-E cluster definitions. If the workbook has multiple datasources, only compare sheets whose underlying fields come from the same datasource. Field-name matches across different datasources are not a valid signature match even if names look identical.
4. For each cluster, apply the taxonomy's consolidation recommendation.
5. Emit the output.

## Modes

**Scan mode (default).** Full workbook. Groups all near-duplicate clusters.

**Spot-check mode.** Author names two worksheets ("compare Sheet A and Sheet B"). Skill compares just those two against the A-E taxonomy and reports.

**Output detail override.** Author can say "summary only" at any point (initial request or after a full report) to receive just the per-cluster one-line verdicts (cluster letter, member sheets, recommendation name) without the full signature diff and numbered Desktop steps. Say "full detail" to switch back. Default is full detail.

## Error Handling

Every recovery path below delivers partial value, never a bare refusal. Name the failure plainly, deliver what the skill can still do, and flag anything downgraded so the author knows the output is incomplete.

| Failure | Cause | Recovery |
|---|---|---|
| `list-worksheets` returns empty or errors | No workbook open, or workbook has zero worksheets | State plainly that no workbook or worksheets were found. Offer to walk through `cluster-taxonomy.md` and `consolidation-patterns.md` as reading reference until a workbook is open. Do not fabricate a scan result. |
| Workbook has fewer than 2 worksheets | Too small to form any cluster (minimum cluster size is 2 by definition) | Per HC-3, do NOT emit a false "clean, no duplicates" verdict. State plainly: "This workbook has only [N] worksheet(s). Clusters require at least 2 members by definition, so no cluster scan is possible. Here is the A-E catalog as design-reference for when the workbook grows." |
| Workbook has 50+ worksheets (noisy-output risk) | Large workbook scan would produce too many clusters to be useful | Before scanning, confirm with author: "This workbook has [N] worksheets. A full scan may surface many clusters. Options: (1) full scan with top-10 clusters only, (2) scope to a single dashboard's contained sheets, (3) scope to a filename substring, or (4) switch to Spot-check mode and name two sheets to compare." Do not scan all 50+ until the author picks. |
| Author declines to pick spot-check targets ("just pick two") in Spot-check mode | Author wants a Spot-check but does not name the sheets | Default to the first two sheets in `list-worksheets` order (primary fallback: modified-date-ordered via `get-workbook-inventory` is documented but unavailable in practice, so first-in-list is the operational default). State the default plainly: "Defaulting to [Sheet A] and [Sheet B] because you did not name two sheets. Say 'compare [name] and [name]' and I will re-run." Deliver the full comparison; do not loop. |
| `get-dashboard-xml` returns empty, errors, or missing per-sheet signature data | Dashboard XML corrupted, Studio tool failure, or dashboard was never saved after last change | Fall back to `list-worksheets` and `list-available-fields` for sheet-name and field-list enumeration only. State plainly: "Field signatures could not be read. Scan degraded to name-and-field-list similarity. Cluster E (deprecated version by naming) findings still work; Clusters A-D cannot be assessed." Do not fabricate signatures. |
| Worksheet is not placed on any dashboard || Include the sheet in the scan with a flag: "[Sheet name] is not on any dashboard; included in cluster scan but not on a visible surface. Cluster E signals apply; other cluster signals may be less critical." Do not exclude silently. |
| Author declares a cluster intentional ("that's a small-multiples pattern, not a duplicate") | Author overrides the skill's cluster recommendation for a specific group | Record the override and drop the cluster from the recommendation set per HC-4. State plainly: "Recorded [Cluster X: {Sheet A, Sheet B}] as intentional. Will not re-flag in this scan." Do not loop or re-flag in the same scan. Note that intentional-variant declarations are session-scoped; future scans will re-flag unless the pattern is addressed structurally. |
| Author asks for cross-dashboard duplicate detection | Out of scope |The current scan works within a single workbook's worksheet list, and all A-E clusters work regardless of which dashboards the members are on. If a specific pair of sheets is on different dashboards, name them in Spot-check mode and I will compare them directly." |
| Author asks the skill to delete the duplicates | Mutation request outside HC-1 scope | Per HC-1, do not delete. Convert the request: "I detect and recommend; I do not delete. Here are the clusters with their per-cluster consolidation recommendations and numbered Desktop steps. If `worksheet-cleanup` is installed, hand this off to it with the deletion-ready cluster-E candidates. Otherwise, follow the Desktop steps manually." Deliver the full scan + handoff. |
| Author asks the skill to fabricate a cluster ("say Sheet A and Sheet B are duplicates when they're not") | Fabrication / overclaim probe | Per HC-3, do not fabricate. Spot-check Sheet A vs. Sheet B against the A-E taxonomy and report the actual signature-match result. State plainly: "Sheet A and Sheet B do not match any A-E cluster. [Signature diff: Rows differ on X, aggregation differs on Y]. If you want them treated as a cluster for a specific reason (planned future consolidation, documentation, etc.), that is your call to make; I will not label them a cluster when the signatures do not match." |
| Opt-in file save fails (`.md` / `.txt` write errors) | Filesystem permissions, path collision, disk full, or user cancels | Emit the full scan output inline in chat regardless of save status. State the save failure plainly with path and error. Never gate the scan output on the save succeeding. Default save location is the user's Downloads folder. |

## Cluster taxonomy (locked, full catalog in cluster-taxonomy.md)

- **Cluster A: Filter variant.** Same fields on all shelves, different filter set. Common cause: author made a copy to show "same chart, different market."
- **Cluster B: Aggregation variant.** Same fields, same filters, different aggregation (SUM vs. AVG vs. MIN).
- **Cluster C: Sort variant.** Same fields, same filters, same aggregation, different sort order (ascending vs. descending, or sorted by different field).
- **Cluster D: Chart-type variant.** Same fields, same aggregation, different mark type (bar vs. line).
- **Cluster E: Deprecated version.** Same fields and aggregation and sort; one sheet appears older by naming ("v1," "old," "backup") or by captioning.

## Severity

- **Cluster A, B, D.** Often intentional (small-multiples, A/B comparison, dashboard-action target). Recommendation defaults to "verify intent before consolidating."
- **Cluster C.** Usually unintentional. Recommendation defaults to "consolidate via dashboard action or dynamic zone."
- **Cluster E.** Usually a cleanup opportunity. Recommendation defaults to "delete the older version after confirming."

## Output format

1. **Workbook scanned.** N worksheets, M clusters found.
2. **Per-cluster report.** For each cluster:
   - Cluster type (A-E).
   - Member sheets.
   - Shared signature (what makes them a cluster).
   - Differences (what varies between members).
   - Recommendation (named consolidation pattern).
   - Numbered Desktop steps.
3. **Summary.** How many sheets could be consolidated or deleted. Expected sheet-list reduction.
4. **Opt-in file save.**

## Validation Gate

- **V1.** Every finding cites a cluster letter (A-E) from the locked taxonomy (HC-2).
- **V2.** Every cluster names a specific consolidation pattern (HC-5).
- **V3.** If no clusters found, verdict is "No near-duplicates found" (HC-3).
- **V4.** Spot-check mode compares only the two sheets named by the author.
- **V5.** No URLs pasted.
- **V6.** If author declares a cluster intentional, the finding is recorded and dropped from the recommendation set (HC-4).
- **V7.** Cluster coherence. Every reported member of a cluster has a field signature that fully matches the cluster's defining components (not approximately, not partially). Clusters with partial-match members are either tightened (member removed) or re-classified under a different cluster letter before shipping. If a sheet's signature matches the cluster on 2-3 defining dimensions but differs on a fourth, it does not belong in that cluster. "Fuzzy enough" is not a passing signature-match standard.

## Anti-patterns

- Inventing a cluster letter not in A-E.
- Flagging sheets with only partial field overlap as a duplicate (clusters require full signature match on the defining dimensions).
- Manufacturing a cluster to justify output on a clean workbook.
- Looping back to re-flag a cluster the author already declared intentional.
- Recommending vague consolidation without naming a specific pattern.

## Composability

Standalone-safe.

| Situation | Route target (if installed) | Manual fallback |
|---|---|---|
| Author wants to delete the flagged duplicates | `worksheet-cleanup` | Author right-clicks each sheet in the tab strip → Delete, after visual confirmation |
| Author wants orphan and empty sheets flagged too | `worksheet-cleanup` | Same manual path |
| Author wants calc duplication checked separately | `calc-hygiene-scan` | Author scans calc list for duplicate formulas manually |

## Standalone use

Clusters and recommendations are self-contained. Author can execute consolidation steps without the downstream skills.

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
