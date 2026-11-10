# Logic Explainer — Worked Examples

Three canonical outputs to lock the voice, structure, and level of detail expected from this skill. Read these before writing your first response of a session. They demonstrate: brief-mode discipline, three-tier confidence tagging, filter-visibility disclosure, fragility flagging, Set-invisibility phrasing, and pattern-library-adapted (never verbatim) rationale.

Do NOT copy these examples into a real response. They are shape references, not templates. Every real output must be tied to the actual fields and view on the sheet being explained.

***

## Example 1 — Worksheet Brief Mode

**Setup:** A worksheet named "Revenue Trend by Segment" on a workbook connected to a Sales datasource. Constructs identified in Phase 1: mark type Line, Rows = SUM(Sales), Columns = MONTH(Order Date), Color = Segment, one FIXED LOD (`{FIXED [Customer ID]: MIN([Order Date])}` used to derive `[Is New Customer]`), one filter on `[Order Date]` (trailing 24 months, context filter), one quick filter on `[Segment]`, one parameter `[Growth Threshold %]` driving a reference line calc, and a running-total table calc on SUM(Sales) computing along Table (Across).

**User asks:** "Explain the logic on this Revenue Trend sheet."

**Response (chat-brief):**

Line chart of monthly revenue by segment, built to show 24-month growth trajectory against a user-adjustable growth threshold. 7 constructs total.

- **Date filter (context, trailing 24 months) on `[Order Date]`** — context-filters first so the running total and reference-line calcs compute over exactly the visible window. Without context, the running sum would silently include out-of-view months. `[Confidence: High]` (matched idiom + legible formula agree)
- **`[Is New Customer]` = `{FIXED [Customer ID]: MIN([Order Date])} = [Order Date]`** — fixes the acquisition date at the customer grain so the segment filter can not dilute it. A regular calc would return "new" only within the filtered slice.
- **Running total on SUM(Sales), Along Table (Across)** — cumulative revenue framing rather than period-to-period; answers "how much revenue so far this window" not "how much this month."
- **Parameter `[Growth Threshold %]` drives a reference line** — lets the viewer stress-test the trend against different targets without editing the sheet. Classic parameter-driven what-if pattern.
- **Segment quick filter (not context)** — shapes which lines render but does NOT propagate to the FIXED LOD by design, preserving the new-customer flag across all segments.
- **Hidden-filter check:** no hidden filters. Every scope narrowing on this view has a visible control (date filter card, segment quick filter, growth-threshold parameter).

Nothing fragile flagged. Want the full long-form breakdown, or is this enough?

***

## Example 2 — Dashboard Brief Mode

**Setup:** A dashboard "Regional Sales Overview" with 4 member sheets: `Region Map`, `Segment Detail`, `Trend by Region`, `Top Customers`. `get-dashboard-xml` reveals 2 filter actions (map -> detail sheets on select), 1 parameter action (map -> `[Selected Region]` parameter), dynamic zone visibility on an alert banner bound to a Set called `[At-Risk Regions]`. `get-worksheet-xml` succeeds on Region Map and Top Customers, fails on Segment Detail and Trend by Region (documented member-sheet gap per Hard Constraint #7).

**User asks:** "Walk me through this dashboard's wiring."

**Response (chat-brief):**

Regional sales dashboard, built as a map-driven drill: click a region, everything else re-filters. 4 sheets, 3 actions, 1 dynamic zone. `Segment Detail` and `Trend by Region` shelf/filter detail is incomplete due to the known dashboard-bound member-sheet reliability gap (see fragility note below).

- **Filter action: `Region Map` -> `Segment Detail` + `Top Customers`, on select** — the map is acting as the primary selector; clicking a region redraws both detail views. Standard drill-from-summary pattern.
- **Parameter action: `Region Map` -> `[Selected Region]` parameter, on select** — the same click also sets a parameter, which the trend chart's title calc reads. This is why the trend chart title changes on selection even though it has no filter action on it. `[Confidence: High]` (title-calc reference to `[Selected Region]` confirms the intent)
- **Dynamic zone visibility on the alert banner, bound to Set `[At-Risk Regions]`** — banner appears when the current filter state intersects the set. Membership of the set cannot be verified from here (Sets are invisible to field-resolution tools per Hard Constraint #8); typical shape for this pattern is a condition-based dynamic set on a threshold calc, but confirm with the workbook author before assuming which regions qualify.
- **Trend by Region hides on parameter reset** — verified from dashboard XML but the trigger calc is on Segment Detail (unreadable). `[Confidence: Low]` (trigger calc formula not accessible; guess based on parameter naming, closer to a mechanical description than a true inference)

**Hidden-filter check:** trailing 24-month date filter is inherited from workbook-level scope with no dashboard control — hidden. Everything else narrowing this dashboard flows through visible controls (region map click, parameter action).

**Fragile:** `Segment Detail` and `Trend by Region` shelf detail unavailable this run (known platform gap). The `[At-Risk Regions]` Set is referenced but not enumerable.

Want the full long-form with per-sheet expansion where readable?

***

## Example 3 — Dashboard Long Form (Same Dashboard as Example 2)

**Triggered when:** the user accepted the "full breakdown" offer from Example 2, and asked for Markdown output saved to disk.

**Response (in chat, before saving):** "Assembling the long-form. Saving as `Regional_Sales_Overview_logic_explainer.md` next to the workbook. One-line summary after save."

**File content (following `output_template.md` structure):**

```
# Regional Sales Overview — Construction Logic

## Summary
A map-driven regional sales dashboard built around a single primary selector: the region map. Clicking a region cascades through a filter action, a parameter action, and a dynamic zone visibility rule to reshape three downstream views simultaneously. The dashboard is optimized for the "pick a region, see everything about it" workflow, not for cross-region comparison.

## What You See
Region Map (filled map, Color = SUM(Sales)) as the top-left primary control. Segment Detail (bar chart, Rows = Segment, Cols = SUM(Sales)) and Top Customers (table, Customer Name + SUM(Sales) sorted descending) as the two detail zones. Trend by Region (line chart, MONTH(Order Date) x SUM(Sales), Color = Region) as the bottom secondary view. Alert banner zone above the map is bound to dynamic zone visibility on the `[At-Risk Regions]` Set.

Shelf/encoding detail for Segment Detail and Trend by Region is incomplete this run due to the known dashboard-bound member-sheet reliability gap (Hard Constraint #7). What is stated for those sheets is derived from `list-available-fields` formula text plus dashboard-XML hints, not from shelf-level XML.

## What Shapes the Scope
- **Trailing 24-month date filter** — applied at the workbook level (visible in dashboard XML as an inherited filter); keeps the trend view honest and prevents the map from mixing legacy data into the current-year color scale.
- **`[Selected Region]` parameter** (default: "All") — used by the trend chart's title calc AND by the dynamic zone visibility rule. The single parameter drives both a display element and a layout element, which is why resetting it has a cascade effect.
- **Region filter action from the map** — filters `Segment Detail` and `Top Customers` on select. The exclusion of `Trend by Region` from this action is deliberate: the trend is meant to show all regions with the selected one visually emphasized, which happens via the parameter's title calc, not via filtering. `[Confidence: High]` (verified by the trend chart NOT being a target of the filter action)

## What Drives the Metric
- **`[Sales]`** — raw measure, aggregated as SUM everywhere it appears. No LODs on this dashboard.
- **`[Selected Region Label]` = `IF [Parameters].[Selected Region] = "All" THEN "All Regions" ELSE [Parameters].[Selected Region] END`** — human-readable label used in the trend chart title. Trivial but load-bearing; the parameter itself would show as the raw region key without this wrapper.
- **`[At-Risk Regions]` Set** — referenced by the alert banner's dynamic zone visibility rule. Membership and condition CANNOT be verified from this environment (Sets are invisible to field-resolution tools, Hard Constraint #8). Based on the pattern library, this is most likely a condition-based dynamic set (e.g., regions where sales fell below a threshold), but confirm with the workbook author.

## How It Connects
- **Filter action** — Source: `Region Map`, Trigger: select, Targets: `Segment Detail` + `Top Customers`, Effect: filters both to the selected region. Rationale: classic drill-from-summary pattern; the map is a selector, the detail sheets are the payoff.
- **Parameter action** — Source: `Region Map`, Trigger: select, Target: `[Selected Region]` parameter, Effect: sets the parameter to the clicked region's key. Rationale: drives the trend-chart title label AND the dynamic zone visibility, so a single click updates two things the filter action cannot reach.
- **Dynamic zone visibility** — Zone: alert banner, Bound to: Set `[At-Risk Regions]`. Effect: shows the banner when the current selection intersects the set. Rationale: an ambient warning tied to a data-defined condition rather than a hard-coded region list, so it stays accurate as data changes. Trigger condition not fully verifiable from here (see What Drives the Metric).

## Notable or Fragile Points
- **Sheet XML unreadable for `Segment Detail` and `Trend by Region`.** Known platform gap for populated, dashboard-bound sheets. Shelf/filter detail for these two sheets is derived, not observed. Do not treat their construction as fully documented.
- **`[At-Risk Regions]` Set is unverifiable.** Referenced in dynamic zone visibility but its members and condition are opaque to every field-resolution tool. Ask the author to confirm before relying on the banner's trigger logic.
- **Parameter action AND filter action share a source (`Region Map`) with different scopes.** Not fragile per se, but a common source of "why did clicking do THAT" confusion for downstream editors. Worth flagging to any future maintainer.

## Not Covered This Run
- Row-level shelf/encoding detail for `Segment Detail` and `Trend by Region` (see fragility note).
- `[At-Risk Regions]` Set membership and condition logic (Sets invisibility).
- Any changes over time to this build — for that, hand off to `workbook-auditor`.
```

**Post-save chat message:** "Saved to `Regional_Sales_Overview_logic_explainer.md` next to the workbook. Summary: map-driven regional drill using a single parameter and filter action with a dynamic zone tied to an unverifiable Set — 3 sheets fully readable, 2 partial due to the known platform gap."

***

## Voice Rules Extracted from These Examples

Use as a mental checklist before delivering any brief-mode response:

- **First sentence names the sheet type AND its purpose in one line.** "Line chart of monthly revenue built to show 24-month growth" — not "This is a worksheet with several filters."
- **Every bullet leads with the construct's identifier in bold**, then a dash, then one line of construction reasoning tied to actual fields on the sheet.
- **Three-tier confidence tags** (`[Confidence: High]`, `[Confidence: Medium]`, `[Confidence: Low]`) follow any bullet whose "why" is inferred rather than directly confirmed. High = name + idiom + formula all agree. Medium = only one signal. Low = generic name, no matched idiom, opaque formula. High-confidence claims can stand without a tag; Medium and Low must always be tagged.
- **Hidden-filter check is mandatory**, either as a dedicated bullet ("hidden filter on `X` restricts to Y") or an explicit "no hidden filters" line when none exist. Silence is not an option.
- **Fragility gets its own explicit callout at the end**, not woven into individual bullets, so the reader can scan for risk in one place.
- **Never state Set membership as fact.** The phrasing "typically a [pattern] but membership not verifiable from here" is the canonical Set language.
- **End with a genuine offer, not a rhetorical one.** "Want the long-form?" is fine; "let me know if you have questions" is filler.
