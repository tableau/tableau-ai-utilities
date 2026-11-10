# Consolidation Patterns

Named consolidation patterns referenced by the A-E cluster taxonomy. Each pattern has numbered Desktop steps the author applies manually.

## Pattern: dashboard-action-filter-swap

**When.** Cluster A (filter variant) where the author wants to collapse N filter-variant sheets into 1 sheet with a user-controlled filter.

**Prerequisite.** Author confirms the kept sheet carries the correct baseline configuration.

**Steps.**
1. In the Tabs strip, right-click each duplicate sheet other than the kept one → Delete. Confirm.
2. Add a new worksheet named "Filter Selector" (or similar). Drag the filter field onto Rows. Change the mark type to Text or Shape so the values show as a clickable list.
3. In the dashboard that will carry the kept sheet, drag Filter Selector onto the canvas as a floating zone.
4. Dashboard menu → Actions → Add Action → Filter.
5. In the action dialog: Source Sheets = Filter Selector. Target Sheets = the kept sheet. Run on = Select. Clearing the selection = Show all values.
6. Hide the Filter Selector title (right-click → Hide Title).
7. Test: click a value in Filter Selector; kept sheet should update.

## Pattern: measure-swap-via-dashboard-action

**When.** Cluster B (aggregation variant) where the author wants to collapse N aggregation-variant sheets.

**Prerequisite.** The aggregations are commutative-enough that users can swap between them without re-interpreting the chart.

**Note.** True aggregation-swap-via-parameter is blocked by the platform parameter-authoring weakness. This pattern uses dashboard-action-driven measure selection as a workaround.

**Steps.**
1. Confirm with the author which aggregation is the default. Keep that sheet. Delete the rest.
2. Create a "Measure Selector" worksheet: a text list of aggregation labels (e.g., "Sum," "Average," "Median") placed as a floating zone.
3. In the kept sheet, replace the measure with a CASE calc that selects the aggregation based on a parameter OR, if parameter authoring fails, keep both measures on the viz and use Measure Names on Filters to control which shows.
4. Add a dashboard action per the Pattern: dashboard-action-filter-swap steps, with the Measure Selector driving the Measure Names filter on the kept sheet.
5. Test: clicking a measure label in Measure Selector swaps the aggregation shown.

**Fallback if parameter authoring fails.** Keep both sheets. Rename to clarify ("Sales SUM," "Sales AVG"). Document the choice in the sheet captions.

## Pattern: dynamic-zone-visibility-swap

**When.** Clusters A, B, D (any multi-variant cluster) where parameter authoring is weak but the author wants a toggleable swap.

**Prerequisite.** Tableau 2022.3+ (dynamic zone visibility is a modern feature).

**Steps.**
1. In the dashboard that will carry the swap, add all variant sheets as separate zones in the same spatial location.
2. Create a toggle control (e.g., a Button or a parameter-less filter) that drives visibility.
3. On each zone, set Visibility Control to the toggle field.
4. Test: toggling the control switches which zone is visible.

**Fallback for pre-2022.3.** Keep all variants on separate dashboard tabs. Add a navigation button on the main tab that routes to each variant.

## Pattern: delete-older-version

**When.** Cluster E (deprecated version) or Cluster D (chart-type variant) where the author chose a type and wants to remove the other.

**Prerequisite.** Author confirmed the kept version has every feature the deleted version had.

**Steps.**
1. Open both sheets side-by-side in the Tabs strip.
2. Diff manually: fields, filters, aggregations, mark types, captions.
3. If the kept version is complete, right-click the deprecated sheet in the Tabs strip → Delete.
4. Save the workbook.

**Safety.** The author can undo the delete with Ctrl+Z before saving. Once saved, the deleted sheet is gone (unless the author has a backup copy of the .twbx).

## Pattern: rename-to-clarify

**When.** The author decides to keep multiple variants as intentional. The duplicates are not actually consolidated; they just need clearer naming so the next person inheriting the workbook understands.

**Steps.**
1. For each kept variant, right-click the tab name → Rename.
2. Rename to a pattern that includes the varying dimension: "Sales SUM," "Sales AVG," "Sales MEDIAN."
3. Add a caption to each sheet explaining why it exists: "Shown for peer-review audiences who need the average."
4. If the sheets are on dashboards, verify the dashboard labels still make sense.

**Follow-up.** Run caption-and-tooltip-advisor on the renamed sheets to make sure the new names flow through tooltips and captions correctly.

## Pattern selection logic

Each cluster letter has a default pattern:

| Cluster | Default pattern | Fallback |
|---|---|---|
| A | dashboard-action-filter-swap | rename-to-clarify |
| B | measure-swap-via-dashboard-action | rename-to-clarify |
| C | delete-older-version | dynamic-zone-visibility-swap |
| D | delete-older-version | rename-to-clarify |
| E | delete-older-version | (no fallback; this is cleanup) |

The skill emits the default pattern unless the author's declared constraints rule it out (parameter authoring blocked, Tableau version < 2022.3, etc.).

## Non-mutation discipline

The skill never applies any of these patterns itself. Every step above is a numbered Desktop instruction the author follows manually. HC-1 is non-negotiable.
