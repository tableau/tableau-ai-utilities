# Interaction Validator

Post-build behavioral verification for Tableau dashboard wiring. Reads workbook state, triggers real state changes where the tools support it, and diffs before-and-after `get-summary-data` on every candidate target sheet. Reports which sheets responded (wired), which didn't (dead wiring), and which couldn't be verified from here (manual check required).

**Example:** "Verify my dashboard wiring" reports 2 filter actions confirmed cannot-verify (no tool simulates a mark selection), 1 parameter cannot-verify (no tool sets an existing parameter's value), 1 dynamic zone visibility candidate identified (needs manual check with exact Desktop click-path), 1 cross-datasource field-name match confirmed, plus 1 empirically-verified tooltip-field-presence pass. Ends with a Recommendations block.

***

## What it does

Sweeps the dashboard systematically so you don't have to manually click every mark and check every target sheet across every parameter value. Where the tool surface supports triggering a state change (e.g. verifying tooltip fields are on Detail, checking cross-datasource field-name matches), it does the real empirical diff. Where the tool surface can't trigger the interaction (no tool sets an existing parameter's value, no tool simulates a mark selection, no tool reaches the Filters shelf), it reports "cannot verify, manual check required" with the exact Desktop steps for you to run yourself.

Symptom-based, not root-cause. When a target sheet doesn't respond, the report says "Sheet X did not respond to Y" and appends the most likely root cause from a common-causes table — with an explicit caveat that confirmed diagnosis requires inspecting action configuration, which no tool exposes today.

Every phase restores original state (parameter value, filter, set membership) after testing. If a restoration step fails, the run stops immediately rather than pushing forward on unknown state.

## When to use it

- "I clicked a mark and nothing happened, is my filter action broken"
- "Did that fix actually work" (after you've edited action wiring in Desktop)
- "Verify all the interactions on this dashboard before I ship it"
- "Is my parameter actually connected to anything"
- "Is this dynamic zone visibility working"
- "Did the cross-datasource filter propagate"

## When NOT to use it

- Not for building or editing actions, parameters, sets, or zone visibility (that's authoring; use the built-in Studio authoring skill (`tableau-desktop-authoring`) or calc-writer)
- Not for data quality issues, nulls, or wrong values (use data-quality-review)
- Not for performance problems
- Not for interaction design or strategy questions like "what interactions should I add" (use viz-planner)
- Not for URL actions or go-to-sheet actions — these are untestable from this environment and get reported as "cannot verify, manual check required"
- Not for standalone worksheets. Interaction validation applies to dashboard wiring; workbooks with only loose worksheets have nothing to test.

## How to trigger it

- "Test my actions"
- "Validate interactions"
- "Is this filter working"
- "Check my parameter"
- "Nothing happens when I click"
- "Why isn't this sheet updating"
- "Interaction validator"
- "Does this parameter do anything"
- "Is this set action connected"
- "Verify my dashboard wiring"
- "Did that fix it"
- "Retest this action"
- "Check if the wiring is fixed now"
- "Is dynamic zone visibility working"
- "Why won't this zone show/hide"

## What you'll need

- Tableau Studio with the target workbook open and the dashboard you want validated already built
- The MCP tools Interaction Validator uses: `get-workbook-inventory`, `list-available-fields`, `get-summary-data`
- For dashboards with 8+ candidate source sheets, you'll be asked which to prioritize (default cap of 6 for filter-action sweeps because runtime is O(source × target))
- For dashboards with 20+ sheets, you'll be asked whether to validate all targets or focus on a specific zone

## Example walkthrough

**Input:** "Verify the wiring on my Regional Sales Overview dashboard."

**Output:**

```
Interaction Validation - Regional Sales Overview
Scanned 2026-09-11. 4 sheets, 3 parameters, 2 filter actions detected.

Tool-Gap Gate: no value-setting or mark-selection command found this
session (as of 2026-08-07). Phases 1, 2, 3, 5 skipped as a block; each
is reported under Untestable Items.

Pre-Test Baseline Gate: 4/4 sheets have >= 2 rows of baseline data.

Empirically Verified:
  - Tooltip field presence on "Top Customers": all 4 tooltip fields
    confirmed on Detail via get-summary-data. PASS.

Cross-Datasource Field-Name Check (Phase 5):
  - Sales_Extract and Customer_360 both expose a "Region" field with
    matching names. This is necessary but not sufficient for cross-DS
    filtering — Tableau also requires the fields to be explicitly
    linked (chain-link icon in the Data pane when both datasources
    are active). MANUAL CHECK: right-click Region on Customer_360 in
    the Data pane and confirm the chain-link icon is connected, not
    broken.

Dynamic Zone Visibility (Phase 4):
  - Candidate found: boolean parameter [Show Details].
  - Cannot confirm it's bound to a zone or trigger the toggle from
    here. MANUAL CHECK: click the zone once, then in the Layout pane
    (left side), use the Item hierarchy dropdown at the top to select
    the specific worksheet object (not a parent container). The
    "Control visibility using this field/parameter" checkbox appears
    near the TOP of the Layout pane once that exact item is selected,
    not the bottom. Confirm it's set to [Show Details], flip the
    value, verify the zone shows/hides.

Untestable Items (tool gap, not skill failure):
  - Parameter [Metric Selector]: cannot verify. Manually change on the
    dashboard, confirm "Trend by Region" and "Top Customers" respond.
  - Parameter [Fiscal Year]: cannot verify. Manually change, confirm
    "Region Map" and "Segment Detail" respond.
  - Filter action Region Map -> Segment Detail: cannot verify. Click
    a region on the map, confirm Segment Detail filters.
  - Filter action Region Map -> Top Customers: cannot verify. Click,
    confirm.

Recommendations:
  1. Highest priority: confirm the [Show Details] zone visibility
     binding, since dynamic zones fail silently when the binding is
     missing.
  2. Manually sweep the two parameters. If either has a target sheet
     that doesn't respond, check whether the parameter is on any
     shelf/encoding on that sheet.
  3. Manually test both filter actions. If a target doesn't respond,
     check the action's "Selected Sheets" vs "All Sheets" setting.

Caveat: these are probable causes based on common patterns. Confirmed
diagnosis requires inspecting action configuration, which is not
available through current tools.
```

## What you get back

- **Full validation report** structured per `skill-expertise/report_format.md`: Summary, per-phase result tables, Dead Wiring section, Untestable Items section, and 1-3 concrete Recommendations.
- **Empirical verification** where tools support it: tooltip field presence (via `get-summary-data`), highlight mark-count changes, cross-datasource field-name matches.
- **"Cannot verify, manual check required"** with exact Desktop click-paths for the interactions that can't be triggered from here today: parameter value changes, mark selections (filter actions, set actions), and dashboard zone visibility bindings.
- **Dead Wiring vs. Not Connected split.** A non-response isn't automatically a bug. Dead Wiring means the target has the same dimension as the source and plausibly should respond. Not Connected means no shared dimension — probably deliberate exclusion.
- **Common-causes table** appended when Dead Wiring is reported. Symptom → likely root cause (parameter not on any shelf, "Selected Sheets" instead of "All Sheets", cross-DS fields not linked despite matching names, etc.).
- **State restoration** after every test. Non-negotiable. If restoration fails, the run stops.
- **Retest mode.** After you report fixing a dead wire, Interaction Validator re-runs only the failing item's phase on the affected sheets and produces a delta report ("FIXED" vs "STILL DEAD").
- **Proactive offer** after viz-planner or worksheet-builder finishes assembling a dashboard. Offered once per session, doesn't auto-run, doesn't re-offer if declined.

## Limitations

- **Most interactions cannot be empirically triggered from this environment as of 2026-08-07.** No tool sets an existing parameter's value (`author-parameter` is create-only and throws "caption collision" on re-use). No tool simulates a mark selection. No tool reaches the Filters shelf as a proxy. Interaction Validator reports these as "cannot verify" with manual test instructions rather than pretending it verified them.
- **No root-cause diagnosis.** No tool reads action configuration. When a sheet doesn't respond, the report gives the symptom and the likely cause from a common-causes table with an explicit caveat that confirmed diagnosis requires inspecting action config in Desktop.
- **Highlight actions are visual-only.** No data change fires, so they can't be empirically diffed. Reported as "visual-only, not empirically verifiable."
- **URL actions and go-to-sheet actions are untestable** from this environment.
- **Sets are hard to discover** without XML access. Interaction Validator tries the field inventory and calc formula references first. If detection fails, it reports the limitation and asks you to name the set rather than guessing.
- **Read-only.** Never creates worksheets, calcs, actions, parameters, or sets. Never uses `author-parameter` to stage a test fixture (confirmed deterministically broken on Windows, not transient). If a fixture is needed, you're asked to create it manually.
- **Runtime scales with dashboard size.** Filter action sweeps are O(source × target). Cap defaults to 6 source sheets, adjustable on request.

## Troubleshooting

- **"Everything shows 'cannot verify'."** Expected as of the current platform version. The tools needed to set an existing parameter's value or simulate a mark selection don't exist yet. The manual test instructions in the report are the current workaround.
- **"A sheet shows 'excluded — insufficient baseline data'."** The Pre-Test Baseline Gate requires ≥ 2 data rows for meaningful diffing. If a target sheet has 0-1 rows, it's excluded from the diff to prevent false "no change detected" conclusions. Verify the datasource connection and shelf configuration on that sheet.
- **"A cross-datasource filter looks dead but the field names match."** Two possible causes: names don't match exactly (e.g. "Region" vs "Sales Region"), or names match but the fields aren't linked for data blending (user-confirmed 2026-08-07). Check the chain-link icon in the Data pane when both datasources are active. Interaction Validator names both possible causes in the report rather than assuming naming is the fix.
- **"The dynamic zone visibility MANUAL CHECK didn't work when I followed it."** The Layout pane control is easy to miss on first try. Confirmed sequence: click the zone once, then in the Layout pane use the Item hierarchy dropdown at the top to select the specific worksheet object (not a parent Tiled/Vertical/Horizontal container). The "Control visibility using this field/parameter" checkbox appears near the TOP of the Layout pane, not the bottom. If you can't find it, you're probably on a parent container instead of the exact item.
- **"The parameter change tested clean but the sheet still looks wrong."** Parameter drives a calc used only in a tooltip or Detail (not on primary encodings). The data changed, but the visible marks didn't. Add the calc to a visible shelf if it should affect the view.
- **"No diff shows anywhere across a whole phase."** Check whether a global filter is already applied and masking changes before concluding everything is broken. Interaction Validator reports the ambiguity rather than declaring a false "all broken."

## Support

File issues in the same channel you use for other Tableau Studio skill feedback. Include the workbook name, the dashboard name, which interaction you expected to work, the report Interaction Validator produced, and whether the manual check confirmed or contradicted the report.
