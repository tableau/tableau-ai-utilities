# Cluster Taxonomy (A-E)

Locked near-duplicate cluster definitions for sheet-swap-detector. Every finding cites a cluster letter.

## Field signature components

A sheet's signature is composed of:

- **Rows pills:** field names, aggregation, discrete/continuous, sort order.
- **Columns pills:** field names, aggregation, discrete/continuous, sort order.
- **Marks card:** mark type (Automatic / Bar / Line / etc.), fields on Color / Size / Label / Detail / Tooltip / Shape / Angle / Path.
- **Filters shelf:** fields and filter configurations (keep / exclude, numeric range, categorical selection, top-N).
- **Pages shelf:** fields present.
- **Sort configuration on each discrete pill.**

Two sheets match on a signature component when the component is identical. A cluster is defined by which components must match and which may differ.

## Cluster A: Filter variant

**Match requirements.** Rows pills identical, Columns pills identical, Marks card identical.

**Difference allowed.** Filters shelf differs. Filter configurations may be entirely different sets.

**Common cause.** Author copied a sheet to show "same chart, different market" or "same chart, different time window."

**Severity.** Often intentional. Default recommendation: verify intent before consolidating.

**Consolidation pattern.** `dashboard-action-filter-swap`: one sheet with a dashboard action driving the filter from a selector sheet. Replaces N duplicates with 1 + 1 selector.

**Desktop steps summary.** Keep one of the duplicates. Delete the rest. Add a selector worksheet (list of filter values). Configure a dashboard action: Dashboard menu → Actions → Add Action → Filter → source is selector, target is the kept sheet.

## Cluster B: Aggregation variant

**Match requirements.** Rows pills' field names identical, Columns pills' field names identical, Marks card field names identical, Filters identical.

**Difference allowed.** Aggregation on one or more measures (SUM vs. AVG vs. MIN vs. MAX vs. MEDIAN).

**Common cause.** Author needed to show the same chart with multiple aggregations for different audiences.

**Severity.** Often intentional for small-multiples. Default recommendation: verify intent.

**Consolidation pattern.** `measure-swap-via-dashboard-action`: one sheet with the aggregation driven by a dashboard-action-selected measure, when parameter authoring is weak. Alternatively, keep both if the aggregations serve different audiences.

**Desktop steps summary.** If keeping both: rename to clarify the aggregation in the sheet name ("Sales SUM," "Sales AVG"). If consolidating: use a Measure Names + Measure Values pattern on one sheet showing both aggregations side-by-side.

## Cluster C: Sort variant

**Match requirements.** Rows pills, Columns pills, Marks card, Filters, and aggregations all identical.

**Difference allowed.** Sort configuration on one or more discrete pills (ascending vs. descending, or sorted by a different field).

**Common cause.** Author needed "top 10" and "bottom 10" views. Or author forgot a sheet existed and rebuilt the same chart with different sort.

**Severity.** Usually unintentional. Default recommendation: consolidate.

**Consolidation pattern.** `interactive-sort-via-parameter-action`: one sheet whose sort is user-togglable. Blocked by parameter weakness in current platform; fallback is `dynamic-zone-visibility-swap` or `delete-older-version`.

**Desktop steps summary.** Confirm which sort is the one users want by default. Delete the other version. If both are needed, keep both and rename clearly ("Top 10 Products," "Bottom 10 Products").

## Cluster D: Chart-type variant

**Match requirements.** Rows pills, Columns pills, Marks-card field placements, Filters, aggregations, sort all identical.

**Difference allowed.** Mark type (Bar vs. Line vs. Area vs. Circle vs. Square).

**Common cause.** Author exploring chart options and left both versions.

**Severity.** Often an exploration artifact. Default recommendation: verify intent; delete the one that is not the chosen format.

**Consolidation pattern.** `delete-older-version` after confirming the intended chart type.

**Desktop steps summary.** Confirm with the author which chart type is intended. Right-click the other sheet in the tab strip → Delete.

## Cluster E: Deprecated version

**Match requirements.** Rows pills, Columns pills, Marks card, Filters, aggregations, sort, mark type all identical OR nearly identical.

**Difference allowed.** None functionally. Difference is in naming or captioning:
- Sheet name contains "v1," "v2," "old," "backup," "copy," "deprecated," "DO NOT USE," "archived."
- Caption contains language indicating one is older ("replaced by," "see Sheet X").

**Common cause.** Author kept the old version "just in case" after a redesign.

**Severity.** Usually a cleanup opportunity.

**Consolidation pattern.** `delete-older-version` after confirming the kept version has every feature.

**Desktop steps summary.** Diff the two sheets to confirm the kept version has all the features. Right-click the deprecated sheet in the tab strip → Delete. Save.

## Partial-match handling

If two sheets match on some signature components but not enough for any single cluster:

- 2-3 matching components: not a cluster. Do not flag.
- Full match on Rows + Columns + Marks but filters, aggregation, sort, and mark type all differ: not a cluster. Do not flag.

The clusters are defined to catch high-confidence duplicates. Partial matches surface noise.

## Multi-cluster sheets

A sheet can be a member of multiple clusters only if it is in multiple pairs with different sheets. If Sheet A matches Sheet B as Cluster C (sort variant) AND matches Sheet C as Cluster D (chart-type variant), report two clusters:

- Cluster C: {A, B}
- Cluster D: {A, C}

Do not merge into a single "A, B, C" group unless all three share the same cluster-defining differences.

## Minimum cluster size

A cluster requires at least 2 member sheets. A single sheet is not a cluster.

## Spot-check mode behavior

Compares exactly 2 sheets named by the author. Reports:

- Match: which cluster letter they fall into.
- No match: field-signature diff explaining why they are not a cluster.

Spot-check does not scan the rest of the workbook.
