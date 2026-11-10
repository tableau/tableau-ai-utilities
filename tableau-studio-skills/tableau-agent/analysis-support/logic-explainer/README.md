# Logic Explainer

Explains the construction logic of a Tableau worksheet or dashboard. Not just what's on it, but why each filter, calc, LOD, parameter, set, and action is there and what it's doing for this specific view.

**Example:** "Walk me through this dashboard's wiring" returns a 4-bullet brief covering the map's filter action, the parameter action driving the title, the dynamic zone tied to a Set, and a fragility note on the two member sheets whose XML couldn't be read.

***

## What it does

Reads a worksheet or dashboard and explains how the pieces work together. You get one line per construct: what it is, and a plain-English "why" tied to the actual fields on the view. Read-only — never mutates anything, never offers to fix a broken calc.

Built for the situation where you inherit or open someone else's workbook and see a FIXED LOD, a context filter, and a parameter action wired together with no comments and no idea how they interact.

## When to use it

- "I inherited this dashboard and have no idea what it's doing"
- "I need to understand why this LOD is here before I touch it"
- "I'm about to modify this sheet and want to know what the filters are actually doing"
- "There's a hidden filter somewhere breaking my numbers, find it"
- "Explain the action wiring on this dashboard"

## When NOT to use it

- Not for what a single field means in isolation (use data-scribe instead)
- Not for what changed in a workbook over time (use workbook-auditor instead)
- Not for data quality issues like nulls or type mismatches (use data-quality-review instead)
- Not for building or editing anything — this skill is strictly read-only. Hand off to an authoring skill for changes.

## How to trigger it

- "Explain this dashboard's logic"
- "Why does this work this way"
- "Walk me through this worksheet's logic"
- "Help me understand this build"
- "Explain the wiring on this sheet"

## What you'll need

- Tableau Studio with the workbook you want explained already open
- The MCP tools this skill uses: `get-workbook-inventory`, `get-worksheet-xml`, `get-dashboard-xml`, `list-available-fields`, `search-workbook-fields`
- Optional: a metric dictionary from `data-scribe` in the same folder as the workbook. If present, this skill will reference it for field meaning rather than re-deriving.

## Example walkthrough

**Input:** "Explain the logic on this Revenue Trend sheet." (worksheet with a Line mark, monthly revenue by segment, a FIXED LOD for new-customer detection, a context filter on Order Date, a running-total table calc, and a parameter-driven reference line)

**Output:**

```
Line chart of monthly revenue by segment, built to show 24-month growth
trajectory against a user-adjustable growth threshold. 7 constructs total.

- Date filter (context, trailing 24 months) on [Order Date] — context-filters
  first so the running total computes over exactly the visible window.
  [Confidence: High]

- [Is New Customer] = {FIXED [Customer ID]: MIN([Order Date])} = [Order Date]
  — fixes the acquisition date at the customer grain so the segment filter
  doesn't dilute it.

- Running total on SUM(Sales), Along Table (Across) — cumulative framing,
  answers "how much revenue so far this window" not "how much this month."

- Parameter [Growth Threshold %] drives a reference line — lets the viewer
  stress-test the trend against different targets without editing the sheet.

- Segment quick filter (not context) — shapes which lines render but does NOT
  propagate to the FIXED LOD by design, preserving the new-customer flag.

Hidden-filter check: no hidden filters. Every scope narrowing on this view
has a visible control.

Nothing fragile flagged. Want the full long-form breakdown, or is this enough?
```

Brief mode is the default. If there's more depth worth covering, the skill offers a long-form breakdown (chat or saved file). Never truncates silently.

## What you get back

- **Brief mode (default):** one-line summary + 3-6 bullets prioritizing filters/params → calcs/LODs → actions → anything fragile. Confidence-tagged inferences. Mandatory hidden-filter check line.
- **Long-form mode (on request):** full breakdown organized as Summary → What You See → What Shapes the Scope → What Drives the Metric → How It Connects → Notable or Fragile Points → Not Covered This Run. Chat or saved to `[sheet-name]_logic_explainer.md` next to the workbook.
- **Confidence tags** on every non-trivial inference: `[Confidence: High]` when the name, structural idiom, and formula all agree; `[Confidence: Medium]` when only one signal is present; `[Confidence: Low]` when none.
- **Fragility callout** for filters referencing missing fields, broken calc dependencies, actions pointing at non-existent sheets, or Sets that can't be verified.

## Limitations

- **Sets are invisible.** Tableau Studio's field-resolution tools cannot enumerate Set members or verify condition logic. This skill will explain what a Set of the observed shape typically does, but flags plainly that actual membership can't be confirmed from here. Ask the workbook author.
- **Dashboard-bound member sheets sometimes fail to return XML.** Known platform gap. When it happens, the skill falls back to `list-available-fields` formula text plus dashboard-XML hints, and states in the output that shelf/filter detail for that specific sheet is incomplete. Does not retry more than once.
- **Row-level security can hide calc formulas.** If RLS blocks a formula, the skill notes what's visible at the shelf/encoding level and states plainly that logic detail is unavailable due to permissions rather than a tool failure.
- **One sheet or one dashboard per run.** For a dashboard, member sheets get a condensed pass. If you want a full standalone report on each, run the skill once per sheet.
- **Explains, never fixes.** If something looks broken, the skill flags it and defers to an authoring skill. It will not propose a rewrite.

## Troubleshooting

- **"It's not finding my sheet."** The skill checks `get-workbook-inventory` first. If the name doesn't match exactly, it lists close matches. Confirm the sheet name in Tableau's tab bar and try again.
- **"Shelf detail says 'incomplete due to known platform gap.'"** This is the dashboard-bound member sheet issue. Not a skill failure. Open the member sheet directly (not from the dashboard tab) and run the skill against it for full detail.
- **"It says a Set's membership can't be verified."** Correct behavior. Sets are opaque to every field-resolution tool in this environment. Ask the workbook author for the Set's condition, or open the Set definition in Tableau Studio to inspect it manually.
- **"The output is shorter than I expected."** Brief mode is the default. Say "give me the full long-form" or accept the offer at the end of the response.
- **"It's asking me plain-text or Markdown for a file I didn't ask for."** The file-format question only fires when you asked for a saved file. If it's asking unprompted, restate that you want the answer in chat.

## Support

File issues in the same channel you use for other Tableau Studio skill feedback. Include the sheet or dashboard name, what you expected, and what you got.
