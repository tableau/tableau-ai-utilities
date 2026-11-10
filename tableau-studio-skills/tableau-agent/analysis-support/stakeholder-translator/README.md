# Tableau Stakeholder Translator

A read-only advisory skill that reads an open Tableau dashboard and translates it into plain language for a non-technical stakeholder. Produces a one-page translation layer: what this answers in plain words, what this does NOT answer (so you do not overclaim), three likely follow-up questions, and the one chart that carries the headline. Audience-shaped voice from a locked 5-profile taxonomy.

**Example:** "Translate this for my VP."

## What it does

Reads a live dashboard (titles, captions, tooltips, fields, data source) and rewrites what it shows into the stakeholder's own vocabulary. Swaps analyst jargon (`SUM(Sales)`, `[Order Date]`, calc references) for plain-language equivalents keyed to the declared audience. Names what the dashboard does NOT answer so the author does not accidentally overclaim in the meeting. Lists three questions the stakeholder is likely to ask, each tied to a specific sheet or data point in the dashboard (or explicitly flagged as unanswered).

Output ships as a five-section summary the author can paste into email, a prep doc, or a stakeholder briefing. Audience voice is shaped by a locked 5-profile taxonomy (C-suite, Business sponsor, Operational manager, External customer, Cross-functional peer). Non-standard phrasings ("my VP," "the readout," "my team") map to the closest profile with announcement so the author can correct.

## When to use it

- "I built this dashboard and need to send a plain-language summary to my VP before the meeting."
- "An external customer is going to see this dashboard. I need to strip out the internal jargon."
- "My Product peer is asking about this sales dashboard. How do I explain it in their vocabulary?"
- "I need to send a readout to the business sponsor who owns this metric."
- "The exec team gets five minutes. What are the two sentences I need to say?"

## When NOT to use it

- Not for a presenter script with speaker notes (use dashboard-walkthrough-generator)
- Not for the full metric dictionary (use data-scribe)
- Not for the stakeholder-handoff onepager (use workbook-summary-onepager)
- Not for scoring the dashboard's design (use viz-critique-pro-studio)
- Not for authoring or editing anything in Desktop (this skill is read-only advisory)

## How to trigger it

- "translate this for my VP"
- "plain language version"
- "explain this to a non-analyst"
- "stakeholder version"
- "jargon-free summary"
- "what does this answer in their words"

## What you'll need

- Tableau Studio open with the agent connected
- A workbook with at least one dashboard (if no workbook is open, the skill offers to walk through the audience-voice guide and jargon-swap list as reading reference instead of refusing)
- Your audience: C-suite, Business sponsor, Operational manager, External customer, or Cross-functional peer (the skill maps non-standard phrasings like "my VP" or "the readout" to the closest locked profile and announces the mapping so you can correct)

## The 5 audience voices

- **C-suite.** 1-2 minute attention budget. Headline-only. Strategic follow-ups ("what should we do," "trajectory," "comparison").
- **Business sponsor.** 3-5 minutes. Named metrics with definitions. Follow-ups about expectations ("I thought margin was higher").
- **Operational manager.** 3-5 minutes. Action-focused. Named entities. Tactical follow-ups ("which account should I call first").
- **External customer.** 5-10 minutes. Context-first. Defines every acronym on first use. No internal product names assumed.
- **Cross-functional peer.** 3-5 minutes. Uses the peer's domain vocabulary (if PM audience, product terms; if sales audience, pipeline terms). Relational follow-ups ("how does this affect my team").

If you declare Cross-functional peer, the skill asks which function (Product, Marketing, Sales, Support) before generating. Default on decline is Product.

## Example walkthrough

**Input:** "translate this for my VP" (with Overview dashboard active)

**Output (abridged, mapped to C-suite voice):**

```
Audience and dashboard confirmed. Overview dashboard, C-suite voice.

What this answers (in their words).
This dashboard shows how profitability is tracking across the business:
total revenue, how profit holds up as a share of sales across regions on
a map, and how sales break down by customer segment and by product. You
can filter by region, order date, and profit margin to narrow the view.

What this does NOT answer.
- Does not show cost drivers behind the profit measure.
- Does not cover customer-level or shipping performance.
- Does not project forward; this is historical only.

Three likely follow-up questions.
1. Which regions are dragging down our margin? Partially answered via
   the map's profit-ratio coloring. Not broken down by why.
2. Are we growing year over year? Not answered; this is a filtered
   snapshot, not a trend.
3. Which segment should we double down on? Answered via Sales by Segment.

The one chart that tells the headline.
Sale Map, which combines revenue magnitude and profit-ratio framing
in one view.
```

Save goes to your Downloads folder by default.

## What you get back

- A five-section translation layer in the declared audience voice
- "What this does NOT answer" required for every output (minimum 2 scope-boundary bullets, even on a clean dashboard, so you cannot accidentally overclaim)
- Three follow-up questions each tied to a specific sheet / data point OR explicitly flagged as "the dashboard does not answer this"
- A one-chart headline recommendation
- Optional `.md` or `.txt` save to the Downloads folder

## Limitations

- Read-only. The skill does not modify the workbook. All output is text.
- Translation names structure, not conclusions. "This dashboard shows revenue by region, sorted descending" is in scope. "Revenue is strong in the Northeast" is not; that is interpretation the author owns.
- Author declares the audience. If declined ("just pick one"), the skill defaults to Business sponsor voice and announces it.
- Cross-functional peer requires naming the peer's function. If declined, defaults to Product.
- One dashboard per run. Switching dashboards mid-run triggers fresh reads against the new target.
- Dashboards with 15+ sheets handled by translating the primary surface (KPI tile + headline chart + 1-2 supporting views). The skill names the omitted count and offers to extend on request.
- Splash / navigation / cover-page dashboards are flagged plainly rather than forced through the "already reads plain" verdict. The skill offers to translate the content dashboard they link to instead.
- `get-worksheet-xml` is deliberately avoided for dashboard-placed sheets due to a known 500 error on real data; the skill reads via `get-dashboard-xml` instead.

## Troubleshooting

- **"No workbook open."** The skill does not refuse. It offers to walk through the audience-voice guide and jargon-swap list so you know what the output will look like once a workbook is open.
- **"The dashboard already reads in plain language."** The skill detects this (titles and captions use everyday terms with no `SUM()` or raw field references) and skips the translation paragraph. Delivers the scope boundaries, follow-up questions, and headline chart anyway.
- **"I want a different voice now that I have seen the output."** Say "use operations voice" (or any other profile) mid-run. The skill re-emits only the voice-affected sections (translation paragraph, three questions). Scope boundaries and headline chart stay unchanged.
- **"The file save failed."** The skill emits the full translation inline anyway and names the save error. Copy from chat into your notes.
- **"The skill asked for a conclusion I did not want."** It should not fabricate one. If you ask it to "say we're growing" or "tell me X is strongest," it refuses and converts the request into a scope-boundary bullet (useful content) rather than fabricating the claim.

## Support

File issues in the Tableau Agent Skills repo.
