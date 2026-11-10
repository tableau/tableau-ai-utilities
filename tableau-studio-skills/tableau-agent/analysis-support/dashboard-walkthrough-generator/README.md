# Tableau Dashboard Walkthrough Generator

A read-only advisory skill that reads an open Tableau dashboard and produces a presenter script: numbered walkthrough order, per-sheet speaker notes, a 30-second elevator version, and the three questions a stakeholder is likely to ask. Audience-shaped tone from a locked 4-profile taxonomy. Author pastes the output into meeting prep.

**Example:** "Walkthrough script for my VP."

## What it does

Reads a live dashboard (sheets, titles, captions, filters, spatial layout) and generates presenter notes in the author's declared audience voice. Names what each chart shows structurally. Does not fabricate conclusions. Pairs with viz-critique-pro-studio (critique the design), data-scribe (document the metrics), and workbook-summary-onepager (handoff doc) as optional downstream routes with manual fallbacks when those skills are not installed.

Output ships as a Summary paragraph, numbered walkthrough order, per-sheet speaker notes, three stakeholder questions each tied to a specific data point, a one-chart headline recommendation, and an opt-in `.md` or `.txt` save to the Downloads folder.

## When to use it

- "I built this dashboard and have to present it to my VP tomorrow. What should I say?"
- "I want a 30-second elevator pitch I can start the meeting with."
- "What questions will the exec team ask when I show this?"
- "I need meeting-prep notes in plain language for an operational manager."
- "I need an analyst-grade walkthrough with named fields and aggregations."

## When NOT to use it

- Not for scoring the dashboard's design (use viz-critique-pro-studio)
- Not for the full metric dictionary (use data-scribe)
- Not for the stakeholder-handoff onepager (use workbook-summary-onepager)
- Not for designing a dashboard from scratch (use viz-planner)
- Not for authoring or editing anything in Desktop (this skill is read-only advisory)

## How to trigger it

- "walkthrough script"
- "presenter notes"
- "how do I present this"
- "talking points for this dashboard"
- "elevator pitch for this viz"
- "notes for my meeting"

## What you'll need

- Tableau Studio open with the agent connected
- A workbook with at least one dashboard (if no workbook is open, the skill offers to walk through the audience-voice guide as reading reference instead of refusing)
- Your audience: Executive, Analyst, Operations, or External (the skill maps non-standard phrasings like "my VP" or "my team" to the closest locked profile and tells you the mapping)

## The 4 audience voices

- **Executive.** Terse. Headline first. One number per sentence. 30 seconds max. Follow-ups are strategic.
- **Analyst.** Technical. Named fields, aggregations, filters. Methodology beat per sheet. Follow-ups are methodological.
- **Operations.** Action-focused. What to do next, by when, by whom. Follow-ups are tactical.
- **External.** Context-first. Defines jargon on first use. No internal acronyms. Follow-ups are clarifying.

If you declare something else ("my boss's boss", "a customer", "the standup"), the skill maps it to the nearest profile and announces the mapping so you can correct.

## Example walkthrough

**Input:** "walkthrough script" (with Overview dashboard active)

**Output (abridged, Executive voice):**

```
Dashboard and audience confirmed: Overview, Executive voice.

30-second elevator. This dashboard is a profitability snapshot across
regions, segments, and products. One tile shows total sales for the
period. A map shows which regions are most and least profitable. Two
charts below break that sales number out by customer segment and by
product line.

Numbered walkthrough order:
1. Total Sales. The headline number.
2. Sale Map. Profit ratio by region, colored on the map.
3. Sales by Segment and Sales by Product.

Likely stakeholder questions:
1. What is our total sales for the period? → Total Sales tile.
2. Which region has the lowest profit ratio? → Sale Map color encoding.
3. What should we do about it? → Not answered by the chart; your call.

File save: .md, .txt, or chat only?
```

Save goes to your Downloads folder by default.

## What you get back

- A 30-second elevator paragraph at or under 75 words
- A numbered walkthrough order (sheet 1 to N) with pause notes
- Speaker notes per sheet in the audience voice
- Three likely stakeholder questions, each tied to a specific data point in a named sheet
- A one-chart headline recommendation
- Optional `.md` or `.txt` save to the Downloads folder

## Limitations

- Read-only. The skill does not modify the workbook. All output is text.
- Walkthrough names structure, not conclusions. "The bar chart shows revenue by region, sorted descending" is in scope. "Revenue is strong in the Northeast" is not; that is interpretation the author owns.
- Author declares the audience, not the skill. If declined ("just pick one"), the skill defaults to Analyst voice and announces it.
- One dashboard per run. Switching dashboards mid-run triggers fresh reads against the new target, not a continuation of the old one.
- Dashboards with 20+ sheets are handled by walking the top 5 to 7 by spatial priority (KPI band first, then primary charts, then supporting views). The skill names the omitted count and offers to extend on request.
- A Tableau Studio limitation: the Dashboard "Show Title" checkbox leaves the `<title>` node in the dashboard XML. The skill's no-title detection cannot be exercised by that toggle alone.

## Troubleshooting

- **"No workbook open."** The skill does not refuse. It offers to walk through the audience-voice guide so you know what the output will look like once a workbook is open.
- **"The elevator is too long."** V4 enforces a 75-word cap. If output drifts over, the skill revises before shipping. If it still looks long on your end, ask for a trim and re-emit.
- **"I started with executive but want operations now."** Say "use operations voice" mid-run. The skill re-emits the elevator, speaker notes, questions, and closer in the new voice. The walkthrough order and structural facts stay unchanged.
- **"The file save failed."** The skill emits the full walkthrough inline anyway and names the save error. Copy from chat into your notes.
- **"The skill fabricated a conclusion I did not ask for."** It should not. If it does, that is an HC-3 violation. Report it; expected behavior is to decline with "the dashboard does not assert that conclusion; the interpretation is yours to make."

## Support

File issues in the Tableau Agent Skills repo.
