---
name: interaction-validator
description: "Use when the user says 'Test my actions', 'is this filter working?', 'nothing happens when I click', 'does this parameter do anything?' Checks dashboard actions, parameters, set actions, and dynamic zone visibility for wiring problems, and says what needs a manual check."
---

# Interaction Validator

Post-build behavioral verification for dashboard wiring. No tool reads action
configuration, so this skill never diagnoses root cause — it triggers real
state changes (parameter values, simulated mark selections via filters, set
membership) and diffs `get-summary-data` before/after across every candidate
target sheet. Report is symptom-based: Sheet X did not respond to Y, not
the actions field mapping is wrong.

**Why this exists:** nobody manually clicks every mark and checks every target
sheet across every parameter value — this does that sweep systematically and
catches dead wiring that would otherwise persist silently for months.

***

## When to use (full trigger detail)

Checks dashboard actions, parameters, set actions, and dynamic zone visibility for wiring problems. As of 2026-08-07, most interaction types cannot be empirically triggered from this environment (no tool sets an existing parameters value or simulates a mark selection) — for those, this skill confirms the wiring is present/consistent and reports cannot verify, manual check required rather than a pass/fail. It still does real empirical diffing where possible (tooltip field presence, highlight mark-count changes, cross-datasource field-name matches). Trigger on test my actions, validate interactions, is this filter working, check my parameter, nothing happens when I click, why isnt this sheet updating, interaction validator, does this parameter do anything, is this set action connected, verify my dashboard wiring, did that fix it, retest this action, check if the wiring is fixed now, is dynamic zone visibility working, why wont this zone show/hide. Also offer proactively right after a dashboard build completes. Do NOT trigger for building or editing actions/parameters/sets/zone visibility (thats authoring — defer to the built-in Studio authoring skill (tableau-desktop-authoring) or calc-writer), data quality issues (defer to data-quality-review), performance problems, or interaction design/strategy (defer to viz-planner). Add a filter action is authoring; is my filter action working is this skill.

## Non-Negotiable Rule: State Restoration

Every phase must restore original state (parameter value, filter, set
membership) after testing. If a restoration step fails, **stop immediately and
tell the user** rather than continuing with an already-corrupted baseline —
dont push forward into the next phase on top of unknown state.

***

## Tool Signatures (Quick Reference)

### Currently Productive Tools (deliver value today)
- `get-workbook-inventory` — enumerate sheets, dashboards, parameters
- `list-available-fields` — field landscape and type metadata
- `get-summary-data` — read actual data (baseline health, tooltip field presence)

### Not Supported (platform gaps)
- `author-parameter` — create-only; cannot set existing parameter values
- Filter-shelf placement — no tool reaches Filters shelf (`add-field` target
  only supports rows/cols/encoding)
- Mark selection simulation — no tool exists for this

**get-summary-data**
- `worksheet` (string, optional if only one sheet) — target sheet name/id
- `columns` (array of strings, optional) — field names to include; omit for all shelved fields
- `maxRows` (integer, default 200, max 1000, optional)
- Returns: untyped tabular data matching the worksheets current shelf/encoding state. Row shape is not formally specified by the platform — parse dynamically based on what comes back.

**author-parameter**
- `caption` (string, required) — parameter name
- `value` (string, required) — value to set
- `datatype` (enum: integer|real|string|boolean|date, default integer)
- `members` (array of strings, optional) — discrete domain values
- Returns: no documented return schema. Confirm success by re-reading summary data on dependent sheets, not by parsing this tools response.

**get-workbook-inventory**
- No required parameters. Call once at the start of Phase 0 to enumerate sheets, dashboards, and parameters before any other tool call.

**list-available-fields**
- Optional `verbosity` (slim|full). Call once per datasource in Phase 0, after `get-workbook-inventory`, to know the field landscape before picking test dimensions in later phases.

***

## Phase 0: Orientation

1. `get-workbook-inventory` — enumerate sheets, dashboards, and any parameters listed.
2. `list-available-fields` on the primary datasource(s) to know the field landscape.
3. **Early exit:** If the dashboard contains only one sheet and no parameters are detected, report: No interactions to validate — this dashboard has a single sheet with no parameters, filters, or sets wired. and stop.
4. If more than one dashboard exists, ask which to validate (Which dashboard should I validate? Or all of them?). Skip the question if theres only one.
5. Note all parameters found. If none are discoverable, skip Phase 1 with a note rather than failing.
6. If the workbook has no dashboards at all (only loose worksheets), report: No dashboards found — interaction validation applies to dashboard wiring (filter/parameter/set actions), so theres nothing to test on standalone worksheets. and stop.

Scope table (whats testable, what isnt) is in `skill-expertise/scope.md` — consult
it once per session if unsure whether an interaction type can be verified.

## Tool-Gap Gate (Consolidated Check)

No tool sets an existing parameter's value, places a filter, or simulates a
mark selection (confirmed 2026-08-07). Record this once and skip Phases
1, 2, 3, and 5 as a block. Do not enter each phase individually only to
exit with the same cannot verify conclusion.

Proceed directly to:
- **Pre-Test Baseline Gate** (confirm sheets have data)
- **Phase 4: Dynamic Zone Visibility** (candidate detection only)
- **Phase 5: Cross-Datasource Filter Check** (field-name matching only, no
  triggering)
- **Tooltip field-presence check** (confirm tooltip fields on Detail via
  `get-summary-data`)
- **Report rendering** (using the grouped Untestable Items block for all
  skipped phases)

This avoids entering 4 phases only to immediately exit each one, saving tokens
and producing a less repetitive report.
## Pre-Test Baseline Gate

Before diffing in any phase, confirm that `get-summary-data` returns ≥ 2 data
rows for each target sheet. If a sheet returns empty or single-row data:
- Exclude it from that phases diff
- Note in the report: Sheet [X] excluded — insufficient baseline data for meaningful comparison (0–1 rows). Verify datasource connection and shelf configuration.

This prevents false no change detected conclusions on sheets that simply have no data to diff.

## Phase 1: Parameter Sweep

**Confirmed 2026-08-07: this phase cannot currently execute as designed.**
`author-parameter` is create-only — calling it again on an existing caption to
change its value throws caption collision instead of updating it, and no
tool sets an existing parameters current value. Skip straight to reporting:
Cannot verify — no tool available to change an existing parameters value.
Manually test by changing the [Parameter Name] control on the dashboard and
confirming [sheet(s)] respond. Do not attempt the steps below until a working
tool exists.

Per parameter (if a working value-set path is ever found): read baseline
`get-summary-data` on every sheet in the target
dashboard (batch this in one pass) → change the parameter to a different valid
value (next member if discrete, midpoint if range, a
known-valid alternate if string) → read post-change summary data on every sheet
(batch this too) → diff → **restore the original value** → record which sheets
changed (responsive) vs. didnt (either not wired to the parameter, or wired
only to a non-visible calc like a tooltip).

For range/continuous parameters, avoid picking a midpoint that coincidentally
falls on the same bucket/breakpoint as the original value (e.g. same bin in a
histogram calc) — if the first diff shows no change, retry once with a value
clearly outside the original bucket before concluding non-responsive.

On live (non-extract) connections, allow a brief pause between the mutate call
and the post-change read — an immediate re-read can return a stale cached
result and produce a false no change detected.

## Phase 2: Filter Action Sweep (per dashboard)

**Confirmed 2026-08-07: the apply a filter on the source sheet approximation
below cannot currently execute.** It requires placing a filter on the source
sheets Filters shelf, but `add-field`s `target` parameter only supports
`rows`/`cols`/`encoding` — there is no tool path to the Filters shelf at all.
Even where reachable, a Filters-shelf filter is not the same event as a mark
selection, which is what a filter action actually fires on — so the
approximation was already an imperfect proxy, and it can no longer even be
attempted. Skip this phases steps and report per source→target pair: Cannot
verify — no tool can reach the Filters shelf or simulate a mark selection.
Manually click a mark on [source sheet] and confirm [target sheet(s)] filter
as expected. Do not stage `add-field` edits and leave them unapplied as a
substitute test — an unapplied cache file proves nothing about the live
dashboard.

Simulates a mark selection since no tool selects marks directly (kept below
for reference in case a Filters-shelf or mark-selection command is added
later). Source sheet
cap defaults to 6 (flag and ask the user to prioritize if more exist, since
this is O(source x target)); if the user specifies a different cap (e.g.,
test all 10), honor their preference with a note about increased runtime.

Per candidate source sheet:

1. Pick a low-cardinality dimension on that sheet using this tiebreaker order:
   dimension already on Color or Shape mark → then lowest cardinality (< 8
   members preferred) → then alphabetical as final tiebreaker. This ensures
   consistent test selection across sessions. If no dimension on the sheet has
   < 8 members, drop the threshold and use whichever dimension has the lowest
   cardinality available — dont skip the sheet.
2. Baseline `get-summary-data` on every other sheet on the dashboard.
3. Apply a filter isolating one member of that dimension on the source sheet.
4. Post-action `get-summary-data` on every other sheet.
5. Diff — which targets narrowed to that member (wired) vs. didnt (not targeted, or broken).
6. **Remove the filter**, restoring the source sheet.

## Phase 3: Set Action Sweep

**Confirmed 2026-08-07: this phase cannot currently execute.** Change Set
Values actions fire on mark selection, same gap as Phase 2 — nothing here can
simulate a click, so trigger a membership change on the sets underlying
dimension below has no tool-driven path. Report per source→set pair: Cannot
verify — no tool can simulate a mark selection to trigger the set action.
Manually click a mark on [source sheet] and confirm set membership /
downstream sheets respond as expected.

Sets are hard to discover without XML access. Try field inventory / calc
references first; if a calcs formula references a set (IN/OUT logic), thats
your target. If detection fails entirely, dont guess — report: Could not
enumerate sets from available tools. To test set actions, tell me which set to
target, and skip the phase.

If a set is identified: find or stage a calc exposing IN/OUT for that set on a
sheets Detail (prefer an existing sheet; only build a scratch sheet if no
existing one exposes the calc) → baseline → trigger a membership change on the
sets underlying dimension → re-read → diff whether the IN/OUT classification
moved → **restore set state** → record which downstream sheets/calcs responded.

## Phase 4: Dynamic Zone Visibility Check

Dynamic zone visibility hides/shows a dashboard zone (a container or a floating
sheet/object) based on a boolean parameter or field. No tool here reads
dashboard-layout XML (zone visibility bindings live there, not in worksheet
XML), so detection is indirect:

1. From `get-workbook-inventory` and any parameters noted in Phase 0, look for
   a boolean parameter or boolean-typed calc whose name suggests a
   show/hide role (e.g. Show Details, Toggle Panel). If none is found,
   report: No boolean parameter/calc found suggesting dynamic zone visibility
   — if a zone should be toggled, tell me which parameter or field controls
   it, and skip the rest of this phase.
2. If a candidate is found, this still cannot be triggered end-to-end for the
   same reason as Phase 1: no tool sets an existing parameters value, and
   theres no tool to read whether a given zones Control visibility using
   setting is actually bound to that candidate (that binding lives in
   dashboard-zone XML, not worksheet XML, and `get-worksheet-xml` only covers
   worksheets). Report: Found candidate visibility control **[name]**, but
   cannot confirm its bound to a zone or trigger the toggle from here.
   Manually check it in Desktop: click the zone once, then in the **Layout**
   pane (left side), use the **Item hierarchy** dropdown at the top to select
   the specific worksheet object (not a parent Tiled/Vertical/Horizontal
   container) — the **Control visibility using this field/parameter**
   checkbox appears near the **top** of the Layout pane once that exact item
   is selected, not the bottom. Set it to **[name]**, then flip the value and
   confirm the zone shows/hides. Confirmed by user 2026-08-07: the controls
   position (top vs. bottom of the pane) and its dependency on selecting the
   exact item via the hierarchy dropdown were both easy to miss on first try —
   lead with the hierarchy-dropdown step, not just check the Layout pane.
3. Do not guess which zone a candidate parameter controls, and do not claim a
   zone is wired for dynamic visibility without seeing it confirmed in
   Desktop — this phase is detection-of-a-candidate only, not verification.
4. Never call `author-parameter` to stage a test fixture for this phase (or
   any phase) — confirmed deterministically broken on Windows, not transient. If a fixture parameter is needed, ask the
   user to create it manually.

## Phase 5: Cross-Datasource Filter Check

Only if the dashboard spans multiple datasources. Match shared dimension names
across datasources → filter a shared value on a sheet from datasource A → check
whether sheets from datasource B respond → report active/inactive. If two
fields look like the same concept but have different names (e.g. Region vs.
Sales Region), flag that mismatch explicitly — its a likely cause of dead
cross-DS filtering, but you cannot fix naming here, only report it. (Note: this
phase has the same filter-simulation gap as Phase 2 — see that phases
2026-08-07 confirmation note.)

**User-confirmed dead-wiring cause, 2026-08-07:** a cross-DS filter action can
fail even when the field names match exactly (e.g. both datasources have a
Category field with identical string values) — Tableau requires the fields
to be explicitly **linked** for cross-datasource filtering to propagate, not
just same-named. This is a data-blending relationship the user sets up in the
Data pane (right-click the field on the secondary datasource → look for a
broken vs. connected chain-link icon next to the field name when both
datasources are active in the same view), separate from and in addition to
matching names. When reporting a dead cross-DS filter with matching field
names, name **both** possible causes, not just the naming-mismatch one: (1)
names dont match, or (2) names match but the fields arent linked — ask the
user to check the chain-link icon in the Data pane before assuming a naming
fix is needed.

## Phase 6: Retest (On Request)

After the user reports fixing a dead wire, re-run only the failing items
phase on the affected sheets. Do not re-run the entire validation — scope the
retest to:
- The specific parameter, source sheet, or set that was flagged
- Only the target sheets that were non-responsive

Compare results to the prior report and update status:
- FIXED: Sheet [X] now responds to [interaction]
- STILL DEAD: Sheet [X] remains non-responsive to [interaction]

If a prior Interaction Validation Report exists in this sessions context,
automatically reference it when generating the retest report — highlight what
changed vs. what persists.

***

## Dead Wiring vs. Likely-Intentional

A non-response isnt automatically a bug. In the report, split non-responses
into:
- **Dead Wiring (Action Required):** target sheet contains the same dimension
  as the filter source — it plausibly *should* respond and didnt.
- **Not Connected (Likely Intentional):** target has no shared dimension —
  softer heading, probably deliberate exclusion.

Highlight actions are visual-only (no data change) — flag as visual-only, not
empirically verifiable rather than pass/fail. URL and go-to-sheet actions are
untestable in this environment — report them as cannot verify, manual check
required, dont attempt to simulate them.

***

## Common Causes (Symptom → Likely Root Cause)

When reporting Dead Wiring, append the most likely cause from this table to
help the user know where to look (but caveat that this skill detects symptoms,
not confirmed root cause):

| Symptom | Likely Root Cause |
|---|---|
| Target non-responsive to parameter change | Calc references the parameter but isnt placed on any shelf/encoding on the target sheet |
| Target non-responsive to filter action | Filter action excludes this target sheet, OR the targets datasource doesnt contain the filtered dimension |
| Only some targets respond to filter | Action is configured with Selected Sheets rather than All Sheets — non-responding targets are excluded |
| Set action has no downstream effect | Set is not referenced in any calc on the target sheet, OR the set calc exists but isnt on a shelf |
| Cross-DS filter inactive | Two possible causes: (1) dimension names dont match exactly across datasources (e.g. Region vs. Sales Region), OR (2) names match exactly but the fields arent explicitly **linked** for data blending (user-confirmed 2026-08-07) — check the chain-link icon next to the field in the Data pane when both datasources are active. |
| Parameter change affects data but not visible marks | Parameter drives a calc used only in a tooltip or detail — not visible on primary encodings |

**Caveat in every report:** These are probable causes based on common patterns. Confirmed diagnosis requires inspecting action configuration, which is not available through current tools.

***

## Scaling Guidance

**For dashboards with 20+ sheets:** Ask before running: This dashboard has
[N] sheets — want me to validate all targets, or focus on a specific
zone/section? If the user specifies a focus area, only include those sheets
as targets (still test all source sheets within that zone up to the cap).

***

## Output

Render the full report using the structure in `skill-expertise/report_format.md`.
Always include Summary, per-phase result tables, a Dead Wiring section, an
Untestable Items section, and 1-3 concrete Recommendations. Skip a phases
section entirely (dont render an empty table) if that phase found nothing to
test (e.g. no parameters exist).

***

## Error Handling

| Failure | Recovery |
|---|---|
| `get-summary-data` returns empty | Retry once without changing the sheet. Still empty: exclude the sheet from the baseline and note 'no data returned; check the data source connection'. Never add fields to shelves. |
| Parameter change fails | Report could not test [parameter] — verify it exists and has a valid domain and move on. |
| `author-parameter` errors caption collision when trying to change an existing parameters value | This is the expected/confirmed outcome as of 2026-08-07, not a transient failure — do not retry. Report per Phase 1s guidance: no tool sets an existing parameters value; give manual test instructions instead. |
| Filter/set action test needs to simulate a mark selection | Confirmed 2026-08-07: no tool does this, and no tool reaches the Filters shelf as a proxy. Do not stage an `add-field` edit and leave it unapplied as a substitute — report cannot verify, manual check required per Phases 2-3s guidance instead. |
| Dashboard has 8+ candidate source sheets | Cap at 6 (or user-specified cap), ask the user which to prioritize. |
| Set detection fails | Report the limitation, ask the user to name the set. |
| No diff shows anywhere across a whole phase | Check whether a global filter is already applied and masking changes before concluding everything is broken — report the ambiguity rather than a false all broken. |
| Target sheet data identical pre/post but plausibly should respond | Flag: Sheet [X] may respond on a field not currently visible — add [suspected field] to Detail and retest, dont just mark it dead. |
| Baseline gate fails (< 2 rows) | Exclude from diff, note in report. Do not attempt to diff single-row or empty sheets. |

***

## Proactive Offer

After `viz-planner` or `worksheet-builder` finishes assembling a dashboard,
offer once: Want me to verify all interactions are wired correctly? Dont
auto-run — the user may still be tweaking the build. Dont re-offer for the
same dashboard in the same session if declined.

***

## Out of Scope

Building/editing actions, parameters, or sets (→ the built-in Studio authoring skill, tableau-desktop-authoring, /
calc-writer), data quality issues (→ data-quality-review), performance tuning,
and interaction design/strategy (→ viz-planner). This skill only reads and
temporarily perturbs state — it never creates worksheets, calcs, or actions.

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
