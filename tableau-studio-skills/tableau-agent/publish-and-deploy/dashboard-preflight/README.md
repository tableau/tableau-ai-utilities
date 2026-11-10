# Dashboard Preflight

**Audit one dashboard's assembly hygiene before it ships.** Read-only. Every finding is a Desktop-fix instruction, never a mutation.

## When to Use

- You built a dashboard and want a sanity check before publish.
- A stakeholder review is scheduled and you want to catch the obvious stuff first.
- You inherited a dashboard and want to know what needs cleanup before you show it.

## When Not to Use

- **Whole-workbook hygiene.** Use `publish-readiness` for unused fields, orphaned scratch sheets, performance, calc hygiene, naming consistency across the workbook.
- **Text correctness.** Use `desktop-spellcheck` for spelling, capitalization, typography.
- **Localization.** Use `i18n-scanner` for hard-coded currency, date-format collisions, region-specific vocabulary.
- **Interaction behavior.** Use `interaction-validator` for testing whether filter actions actually fire.
- **Tooltip and annotation content.** Use `caption-and-tooltip-advisor` for weak tooltips and captions.
- **Chart selection.** Use `chart-swap-advisor` if you're not sure the chart type is right.
- **Building or editing.** Use `viz-planner` or `worksheet-builder` for authoring.

## The 8-Check Catalog

Every run evaluates the dashboard against a locked catalog of 8 checks. Each finding cites a specific rule ID:

| ID | Check | What It Catches |
|---|---|---|
| P-ZONE-01 | Zone Alignment | Zones extending past canvas bounds, misaligned grid placement |
| P-SHEET-02 | Sheet-to-Zone Mapping | Dead references to deleted sheets |
| P-FILTER-03 | Filter-Action Wiring | Filter actions with invalid sources, targets, or fields |
| P-PARAM-04 | Parameter Linkage | Parameters referenced but not connected to any calc, filter, or dynamic zone |
| P-TITLE-05 | Title and Caption Presence | Missing titles on worksheets or the dashboard itself |
| P-CANVAS-06 | Canvas-Size Sanity | Canvas dimensions not matching a known device class without explicit rationale |
| P-FIT-07 | View-Fit Legality | View fit mismatched with chart type per the shared portfolio catalog |
| P-CONTAINER-08 | Container-Nesting Soundness | Orphan floats, zero-dimension containers, excessive nesting depth |

## What You Get

A report grouped by severity (Blocking, Warning, Info). Every finding includes a Desktop-fix instruction. Optional handoff to Publish Readiness so it skips its own dashboard-hygiene checks.

## Example Trigger Phrases

- "Preflight this dashboard"
- "Check my dashboard before I publish"
- "Is this dashboard ready for review"
- "Dashboard sanity check"
- "Audit this dashboard's assembly"

## Output Handoff

Emits `dashboard_preflight_report/1` per the locked schema in `skill-expertise/handoff_schema.md`. Consumed by publish-readiness and workbook-auditor.

## Known Limitations

- One dashboard per run. Batching is refused.
- `get-worksheet-xml` reliability on dashboard-bound populated sheets can cause partial UNSCANNED findings. Fallback to `list-available-fields` + dashboard-XML hints.
- Cannot verify visual pixel-level alignment. Sees coordinates, not rendered output.
- Cannot simulate interaction firing (use interaction-validator for that).

## Distribution

Ships with Tableau Studio. Also available on Skills Exchange for latest-version pulls between Studio releases.
