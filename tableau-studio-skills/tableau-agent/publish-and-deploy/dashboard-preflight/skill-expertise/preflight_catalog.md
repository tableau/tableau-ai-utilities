# Preflight Catalog (Locked, 8 Checks)

Every finding in `dashboard-preflight` cites one of these rule IDs. No fabricated rules; no severity reassignment; no check outside this catalog.

## P-ZONE-01 Zone Alignment

**Check:** every zone's coordinates fall within the dashboard canvas bounds AND align to the dashboard grid (no fractional pixel offsets that read as misalignment).

**Signals evaluated:**

- Zone `x + width` ≤ canvas width. Zone `y + height` ≤ canvas height. Zones extending past either dimension flagged Blocking.
- Zone `x` and `y` divisible by 2 (Tableau's default grid tick). Fractional-pixel zones flagged Warning.
- Adjacent zones with sub-pixel gaps or overlaps flagged Warning.

**Severity:** Blocking if a zone extends past canvas bounds; Warning if grid-alignment or gap/overlap issues; Info if only aesthetic-tier deviations.

**Desktop fix:** right-click zone, Edit position, set integer coordinates.

## P-SHEET-02 Sheet-to-Zone Mapping

**Check:** every visible worksheet zone references a live worksheet in the workbook. No dead references to deleted or renamed sheets.

**Signals evaluated:**

- Each worksheet-zone's `sheet` attribute resolves to a name in `list-worksheets` output.
- Dead references flagged Blocking (the zone renders empty or broken in Desktop).
- Floating text zones without a `sheet` attribute are legal and skipped.

**Severity:** Blocking always. Dead references are release-blockers.

**Desktop fix:** right-click zone > Remove, or rebind to a live sheet via Sheets pane.

## P-FILTER-03 Filter-Action Wiring

**Check:** every filter action on the dashboard has a valid source worksheet, at least one valid target worksheet, and a field that resolves in `list-available-fields`.

**Signals evaluated:**

- Source worksheet exists in this workbook.
- Target worksheet(s) exist in this workbook.
- Filter field resolves to a live field via `resolve-field`.
- Action name is non-empty (Blocking if empty; Tableau requires a name).

**Severity:** Blocking if source/target/field is missing or unresolvable. Warning if action name is missing.

**Desktop fix:** Dashboard > Actions > Edit; supply missing source, target, or field.

**Does NOT check:** whether the action actually fires (that's interaction-validator's scope) or whether "Selected Sheets" vs. "All Sheets" is the correct choice (defer to interaction-validator).

## P-PARAM-04 Parameter Linkage

**Check:** every parameter referenced on this dashboard is linked to at least one live calc, filter, or dynamic-zone-visibility binding.

**Signals evaluated:**

- Parameters appearing in a dashboard's parameter list are cross-referenced against `list-available-fields` calc formulas.
- Parameters that appear on the dashboard but are unreferenced flagged Warning (orphaned).
- Parameters referenced only in tooltips flagged Info (low-visibility use, may be intentional).

**Severity:** Warning for orphaned parameters. Info for tooltip-only. Never Blocking (Tableau permits unused parameters).

**Desktop fix:** if orphaned, right-click parameter > Remove, or wire it into a calc/filter/dynamic-zone binding. If tooltip-only and intentional, ignore.

## P-TITLE-05 Title and Caption Presence

**Check:** every worksheet zone has either a visible title or a documented "no title" caption. Dashboard has a title zone or an explicit "no title" caption.

**Signals evaluated:**

- Worksheet-zone `show-title` attribute or equivalent XML flag.
- Dashboard-level title zone present.
- Caption presence for zones flagged "no title" (documentation of intent).

**Severity:** Warning if a worksheet-zone has no title AND no caption. Info if dashboard-level title missing but worksheet titles present. Blocking never (titles are stylistic, not functional).

**Desktop fix:** double-click title area to add; or right-click zone > Show Title.

## P-CANVAS-06 Canvas-Size Sanity

**Note:** the device-class list below is a house-style default, not a Tableau platform requirement. Any fixed canvas size is technically valid in Tableau. This check exists to catch unintentional/unexplained sizing, not to enforce a single "correct" size.

**Check:** canvas dimensions match a known device class OR are explicitly Fixed with a stated rationale in the dashboard caption.

**Known device classes:**

- Desktop 1400x900 (or 1366x768, 1920x1080)
- Laptop 1200x800 (or 1280x720)
- Tablet 768x1024 (or 1024x768)
- Phone 375x812 (or 320x568, 414x896)
- Automatic (Tableau's default)

**Signals evaluated:**

- Canvas `width x height` matches a known device class.
- If mismatch, dashboard caption references the target audience or device (e.g., "Optimized for 4K displays").

**Severity:** Warning if mismatch AND no rationale in caption. Info if mismatch WITH rationale. Blocking never.

**Desktop fix:** Dashboard pane > Size > select preset, or add rationale to dashboard caption.

## P-FIT-07 View-Fit Legality

**Note:** the fit-by-chart-type table below is a house-style recommendation drawn from the shared portfolio catalog, not a Tableau-enforced rule. Tableau permits any fit on any mark type. A mismatch is a design suggestion, never a functional defect, which is why this check can never reach Blocking severity.

**Check:** each worksheet-zone's view fit aligns with the recommended fit for its chart type per the shared portfolio catalog.

**Locked recommendations:**

| Chart Type | Recommended Fit |
|---|---|
| Map / KPI text | Entire View |
| Time-series line | Fit Width |
| Area (time-series or category) | Fit Width |
| Horizontal ranked bars | Fit Height |
| Vertical bars | Fit Width |
| Scatter | Standard |
| Text table | Fit Width |
| Heatmap / highlight table | Fit Width |
| Bullet / gauge / bar-in-bar | Entire View |
| Pie (allowed only per anti-pattern gate) | Entire View |

**Area mark rationale.** Confirmed 2026-09-10 behavioral run on Superstore Shipping dashboard: Area was the recurring mark type falling through UNSCANNED. Area charts share the temporal-axis rendering behavior of line charts (width-scaling matters, height-scaling doesn't), so Fit Width is the correct recommendation. If the Area chart is used categorically (rare, but valid), Fit Width still applies since the primary axis is horizontal.

**Signals evaluated:**

- Worksheet's mark type inferred from XML.
- Zone's current view fit compared to catalog recommendation.

**Fallback for unrecognized mark types.** If a worksheet uses a mark type not in the table above (rare, but possible for custom or newly-introduced Tableau mark types), flag the zone UNSCANNED with `reason: fallback_unavailable` and note the unrecognized mark type. Never guess a recommendation. The recommendation table is closed to what's listed; extending it is a catalog revision, not a per-run inference.

**Severity:** Warning if mismatch. Info if the worksheet has multiple mark types (dual-axis) and one aligns.

**Desktop fix:** right-click zone > Fit > select recommended value.

## P-CONTAINER-08 Container-Nesting Soundness

**Check:** container structure is sound. No orphan floats inside tiled containers, no zero-dimension containers, container nesting no deeper than 4 levels.

**Signals evaluated:**

- Zone `layout` attribute (tiled vs. floating) matches its parent container's layout, OR is an explicit intentional float documented in caption.
- Container `width` and `height` non-zero (zero-dimension containers hide their contents).
- Container-depth traversal caps at 4 levels; deeper flagged Warning.

**Depth-4 heuristic source.** Empirical rule of thumb aligned with Viz Planner's `container_patterns.md` guidance: two-container-deep (outer tiled + inner horizontal/vertical) covers 90%+ of layouts; three-deep is common for KPI-header-plus-body-plus-footer patterns; four-deep is the practical upper bound before edit-in-Desktop friction outweighs layout precision. Deeper nesting also increases the risk of stale zone bindings when a container is resized (a documented Viz Planner testing finding, 2026-08).

**Severity:** Blocking for zero-dimension containers (contents invisible). Warning for orphan floats or depth > 4.

**Desktop fix:** rework container hierarchy in Layout pane; resize zero-dimension containers to positive dimensions.

## Severity Summary

| Rule | Blocking | Warning | Info |
|---|---|---|---|
| P-ZONE-01 | Canvas overflow | Grid misalignment, gap/overlap | Aesthetic tier |
| P-SHEET-02 | Dead sheet reference | - | - |
| P-FILTER-03 | Invalid source/target/field | Missing action name | - |
| P-PARAM-04 | - | Orphaned parameter | Tooltip-only reference |
| P-TITLE-05 | - | Missing worksheet title + caption | Missing dashboard title |
| P-CANVAS-06 | - | Mismatch + no rationale | Mismatch + rationale |
| P-FIT-07 | - | Mismatch with recommendation | Dual-axis partial-match |
| P-CONTAINER-08 | Zero-dimension container | Orphan float, depth > 4 | - |

## Sentinel Discipline

If a check cannot run (e.g., `get-worksheet-xml` fails on a dashboard-bound sheet, or `get-dashboard-xml` fails entirely), record the finding as `"unscanned"` with a rationale in the notes field. Never silently omit a check.

## Refuse to Fabricate

Every finding cites one of the 8 rule IDs. Never invent a rule. Never reassign severity. Never mark a check "passed" without evaluating its signals.
