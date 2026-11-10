# Tableau Sheet Swap Detector

A read-only advisory skill that scans every worksheet in an open Tableau workbook, groups near-duplicate sheets against a locked 5-cluster taxonomy (A filter variant, B aggregation variant, C sort variant, D chart-type variant, E deprecated version), and recommends a specific consolidation pattern per cluster with numbered Desktop steps. Fills the gap between worksheet-cleanup (orphan and empty detection) and spellcheck/caption audits by owning the "my worksheet list is a mess with near-duplicates" problem neither covers.

**Example:** "Which worksheets can I consolidate?"

## What it does

Reads a live workbook and groups near-duplicate worksheets by field signature against a locked 5-cluster taxonomy. For each cluster, names a specific consolidation pattern (dashboard-action-filter-swap, measure-swap-via-dashboard-action, delete-older-version) and gives numbered Desktop steps to apply it. The author owns execution; the skill never mutates the workbook.

Two modes. **Scan mode** sweeps the entire workbook and groups every near-duplicate pair into a cluster. **Spot-check mode** compares exactly two sheets the author names ("compare Sales by Segment and Sales by Segment - West") and reports the signature-match result for just those two.

Pairs with worksheet-cleanup (orphan and empty sheets), publish-readiness (unused fields), and calc-hygiene-scan (duplicate calc formulas) as optional downstream routes, each with a manual Desktop fallback.

## When to use it

- "My worksheet tab strip is a mess. I know there are duplicates in there somewhere."
- "I inherited a workbook with 40 worksheets and I need to figure out which ones overlap."
- "Which sheets can I consolidate before publishing this to prod?"
- "I need to find redundant views before the migration."
- "Is Sales by Segment the same as Sales by Segment - West or is one actually different?"

## When NOT to use it

- Not for orphan or empty sheet detection (use worksheet-cleanup)
- Not for unused field detection (use publish-readiness)
- Not for duplicate calc formula detection (use calc-hygiene-scan)
- Not for authoring or editing anything in Desktop (this skill is read-only advisory)

## How to trigger it

- "duplicate worksheets"
- "near-duplicate sheets"
- "which sheets can I consolidate"
- "my worksheet list is a mess"
- "redundant sheets"
- "cleanup duplicate views"
- "compare [Sheet A] and [Sheet B]" (triggers Spot-check mode)

## What you'll need

- Tableau Studio open with the agent connected
- A workbook with at least 2 worksheets (clusters require minimum 2 members by definition; a workbook with only 1 worksheet triggers reading-reference mode rather than a false "clean" verdict)
- If the workbook has 50+ worksheets, the skill will ask you to scope the scan before proceeding (full scan, scope to one dashboard, scope to a filename substring, or Spot-check mode)
- Each contained worksheet is read via `get-worksheet-xml` for shelf-level signatures. The scan does not require you to activate sheets one-by-one; the skill iterates automatically.

## The 5-cluster catalog (A-E)

- **Cluster A Filter variant.** Same fields on Rows and Columns and Marks, different filter configuration. Common cause: author copied a sheet to show "same chart, different market." Default severity NEEDS ATTENTION (often intentional). Pattern: `dashboard-action-filter-swap`.
- **Cluster B Aggregation variant.** Same fields and filters, different aggregation (SUM vs. AVG vs. MIN). Default severity NEEDS ATTENTION. Pattern: `measure-swap-via-dashboard-action`.
- **Cluster C Sort variant.** Same fields and filters and aggregation, different sort order (ascending vs. descending, or sorted by different field). Default severity NEEDS ATTENTION (usually unintentional). Pattern: `delete-older-version`.
- **Cluster D Chart-type variant.** Same fields and aggregation and sort, different mark type (bar vs. line). Default severity NEEDS ATTENTION. Pattern: `delete-older-version` (confirm chart type with author first).
- **Cluster E Deprecated version.** Full signature match on everything. One sheet appears older by naming ("v1", "old", "backup") or by captioning. Default severity CLEANUP OPPORTUNITY. Pattern: `delete-older-version`.

Full catalog with signature-component matching rules and per-cluster recommendations in `skill-expertise/cluster-taxonomy.md`.

## The 5 consolidation patterns

- **dashboard-action-filter-swap.** Keep one duplicate. Add a selector sheet. Dashboard action drives filter from selector to kept sheet. Replaces N duplicates with 1 kept sheet + 1 selector.
- **measure-swap-via-dashboard-action.** Keep one duplicate. Parameterize the measure or use a dashboard action to swap aggregations. Replaces N duplicates with 1 kept sheet + 1 measure selector.
- **delete-older-version.** After confirming the newer sheet is the authoritative one, delete the older. Lowest-cost consolidation.
- **dynamic-zone-visibility.** For dashboards with chart-type variants, use dynamic zone visibility to swap mark types based on a parameter.
- **merged-single-sheet-with-set-action.** For sort or chart-type variants that are actually two separate business questions, keep both but merge common elements via set actions.

Full pattern definitions with per-pattern Desktop steps in `skill-expertise/consolidation-patterns.md`.

## Example walkthrough

**Input:** "which sheets can I consolidate" (workbook has F2 Cluster A fixture staged: Sales by Segment and Sales by Segment - West with identical shelves and only Region filter differing)

**Output (abridged, Scan mode):**

```
Workbook scanned. 26 worksheets, 1 cluster found.

Cluster A: Filter variant
  Members: Sales by Segment, Sales by Segment - West
  Shared signature: Rows=[Segment], Columns=[SUM(Sales)], Marks=Bar
  Difference: Filters shelf. Sales by Segment has no Region filter.
    Sales by Segment - West has Region=West only.
  Severity: Needs attention (often intentional).
  Recommendation: dashboard-action-filter-swap pattern.
  Numbered Desktop steps:
    1. Decide which to keep (default: Sales by Segment, the broader one).
    2. Build a selector worksheet with Region values.
    3. Dashboard menu, Actions, Add Action, Filter.
       Source = selector sheet. Target = Sales by Segment.
       Pass [Region] on select.
    4. Delete Sales by Segment - West from the Tabs strip.
    5. Verify the dashboard action: click a Region in the selector,
       confirm Sales by Segment updates.

Summary: 1 sheet could be consolidated (if the pair is unintentional).
Expected sheet-list reduction: 26 to 25.

File save: .md, .txt, or chat only?
```

Save goes to your Downloads folder by default.

## What you get back

- A per-cluster report with cluster letter, member sheets, shared signature, differences, severity, named consolidation pattern, and numbered Desktop steps
- A workbook-level summary: how many sheets could be consolidated or deleted, expected sheet-list reduction
- An honest "No near-duplicates found" verdict if the scan finds nothing (never a manufactured cluster on a clean workbook)
- Optional `.md` or `.txt` save to the Downloads folder

## Limitations

- Read-only. The skill does not modify the workbook. All output is text.
- Clusters require at least 2 members by definition. A workbook with only 1 worksheet triggers reading-reference mode rather than a false "clean" verdict.
- Field signatures live in `get-worksheet-xml` per worksheet. The scan iterates automatically; the skill does not use `get-dashboard-xml` for signature extraction because that tool returns zone layout only.
- Cross-datasource false-positive guard: if two sheets have identical shelf signatures but their fields come from different datasources, they are not reported as a cluster. V7 of the Validation Gate enforces this.
- The current scan works regardless of which dashboards the members are on; to compare sheets across different dashboards specifically, use Spot-check mode.
- The current scan includes dashboard-less sheets with a flag.
- Intentional-variant declarations are session-scoped. If a cluster is intentional (small-multiples pattern, A/B test), declaring it drops the finding for that scan only. Future scans will re-flag unless the pattern is addressed structurally.
- 50+ worksheet workbooks trigger a scope-pick confirmation before scanning to prevent noisy output.
- `get-workbook-inventory` modified-date metadata is unavailable in practice, so when the author declines to pick Spot-check targets, the skill defaults to the first two sheets in `list-worksheets` order rather than the two most-recently-modified.

## Troubleshooting

- **"No workbook open."** The skill does not refuse. It offers to walk through `cluster-taxonomy.md` and `consolidation-patterns.md` as reading reference until a workbook is open.
- **"My workbook only has 1 worksheet."** The skill states plainly that clusters require at least 2 members and offers the A-E catalog as design-reference for when the workbook grows. It will not emit a false "clean, no duplicates" verdict on an under-sized workbook.
- **"My workbook has 60 worksheets."** The skill asks you to scope: full scan with top-10 clusters only, scope to one dashboard's contained sheets, scope to a filename substring, or switch to Spot-check mode. Full scan proceeds only after you pick.
- **"Two of my sheets look identical but the skill did not report a cluster."** Check whether the two sheets reference fields from different datasources. The V7 cross-datasource guard refuses to cluster sheets with same-named fields coming from different datasources, because the shelf signatures look identical but the underlying data is different. If both sheets are on the same datasource and still not clustered, their shelf composition likely differs on a defining dimension (chart type, aggregation, or a Rows/Columns field).
- **"The skill reported a cluster I meant to keep separate (small-multiples pattern)."** Say "the [Cluster X] pair is intentional small-multiples" and the skill will record the override and drop the cluster from the recommendation set for the current scan.
- **"The skill asked me if I want to delete the duplicates."** It should refuse mutation per HC-1 and convert the request into detect-and-handoff. The deletion steps go through worksheet-cleanup (if installed) or you execute them manually in Desktop.
- **"The file save failed."** The skill emits the full scan output inline anyway and names the save error. Copy from chat into your notes.
- **"The skill asked me whether two look-alike sheets are duplicates when they are not."** You can decline the finding. If you ask the skill to say they are duplicates when they are not (fabrication probe), the skill refuses per HC-3 and spot-checks the two sheets against A-E to report the actual signature-match result.

## Support

File issues in the Tableau Agent Skills repo.
