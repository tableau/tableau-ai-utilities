# Tableau Caption and Tooltip Advisor

A read-only advisory skill that reads an open Tableau dashboard and rewrites weak tooltips, captions, and labels. Produces audience-shaped rewrites tied to a locked 6-rule catalog (T1-T6), each with a severity, the current text, the proposed replacement, and the numbered Desktop step to apply the fix. Fills the gap between dashboard-caption-audit (presence check) and spellcheck (typo check) by owning the "the labels are there but they are bad" problem neither covers.

**Example:** "Rewrite my tooltips."

## What it does

Reads a live dashboard (titles, captions, tooltips, axis labels) and audits every text surface against a locked 6-rule catalog. For each weak surface, proposes a rewrite in the author's declared audience voice and gives numbered Desktop steps to apply it. Author owns execution; the skill never mutates the workbook.

Two modes. **Audit mode** returns a full severity-ranked finding list with before/after rewrites. **Rewrite-suggestions-only mode** returns the rewrites compressed by sheet with one combined Desktop-steps block at the end, for authors who already know what is wrong and just want the proposed text.

Pairs with dashboard-caption-audit (presence check), spellcheck (typo check), viz-critique-pro-studio (whole-dashboard scoring), and stakeholder-translator (plain-language translation) as optional downstream routes with manual fallbacks.

## When to use it

- "I built this dashboard and the tooltips show `SUM(Sales)` instead of a real label."
- "My dashboard title is still 'Insert title here' and I need to fix it before the review."
- "The tooltip template on this chart has raw `[Field]` references the viewer sees."
- "I want to rewrite the captions for an executive audience, not an analyst audience."
- "I want just the rewrites grouped by sheet, not a full severity report."

## When NOT to use it

- Not for presence-only audits (use dashboard-caption-audit)
- Not for typo-only checks (use spellcheck)
- Not for whole-dashboard critique (use viz-critique-pro-studio)
- Not for a plain-language translation of what the dashboard answers (use stakeholder-translator)
- Not for authoring or editing anything in Desktop (this skill is read-only advisory)

## How to trigger it

- "rewrite my tooltips"
- "fix my captions"
- "my tooltips look weird"
- "better tooltip text"
- "SUM of sales in tooltip looks ugly"
- "tooltip and caption review"
- "my labels are bad"

## What you'll need

- Tableau Studio open with the agent connected
- A workbook with at least one dashboard (if no workbook is open, the skill offers to walk through the T-catalog and audience-voice-rules as reading reference instead of refusing)
- Your audience: Executive, Analyst, Operations, or External (the skill maps non-standard phrasings like "the readout" to the closest profile with announcement so you can correct)
- Each contained sheet made active in Desktop one at a time during the scan (the skill asks before each one; this reduces the chance of stale-read failures on dashboard-placed sheets)

## The 6-rule catalog (T1-T6)

- **T1 Uninformative measure labels.** `SUM(Sales)` left as an axis label or tooltip row. Severity NEEDS ATTENTION.
- **T2 Raw field names in tooltips.** `[Order Date]` sitting in a tooltip template with no plain-language context. Severity NEEDS ATTENTION.
- **T3 Missing dashboard-level context caption.** Dashboard has no caption describing what it answers. Severity FAIL for External and C-suite audiences, NEEDS ATTENTION otherwise.
- **T4 Missing worksheet caption on complex views.** Worksheet has 3 or more pills on Rows and Columns with no caption. Severity NEEDS ATTENTION.
- **T5 Tooltip-field mismatch.** Tooltip references a field the viz does not visually encode (ghost field). Severity NEEDS ATTENTION.
- **T6 Placeholder text.** "Insert title here," "Double-click to edit," default sheet names like "Sheet 1." Severity FAIL.

Full catalog with regex-level detection signals and per-audience rewrite examples in `skill-expertise/tooltip-catalog.md`.

## The 4 audience voices

- **Executive.** 8-word tooltip, 20-word caption max. Headline-first. Business terms. No fields, no aggregations.
- **Analyst.** 15-word tooltip, 40-word caption. Named fields acceptable. Methodology notes in captions.
- **Operations.** 10-word tooltip, 25-word caption. Action-focused. Named entities. Time-bound.
- **External.** 12-word tooltip, 35-word caption. Context-first. Define measures. No internal jargon.

If you declare something else ("the readout," "my VP," "the standup"), the skill maps it to the closest profile and announces the mapping so you can correct.

## Example walkthrough

**Input:** "rewrite my tooltips" (Overview dashboard active, Executive voice declared)

**Output (abridged, Audit mode):**

```
Dashboard and audience confirmed. Overview, Executive voice.

Verdict: Needs attention.

Findings:
- T4 Missing worksheet caption on complex view. Sheet: Sales by Segment
  (3 pills on Rows+Columns: Segment, Sales, Order Date; no caption).
  Proposed (Executive): "Monthly sales by segment."
  Desktop step: Right-click Sales by Segment > Caption > Show Caption,
    then edit the caption text to the proposed text.

- T4 Missing worksheet caption on complex view. Sheet: Sales by Product
  (3 pills on Rows+Columns: Category, Sales, Order Date; no caption).
  Proposed (Executive): "Monthly sales by category."
  Desktop step: Right-click Sales by Product > Caption > Show Caption,
    then edit the caption text to the proposed text.

No T1, T2, T3, T5, or T6 findings.

File save: .md, .txt, or chat only?
```

Save goes to your Downloads folder by default.

## What you get back

- A severity-ranked list of findings, each tied to one of the T1-T6 rules
- A proposed rewrite per finding in the declared audience voice, length-targeted
- Numbered Desktop steps to apply each rewrite manually
- An honest "Needs attention" verdict with the real findings (never a manufactured list on a clean dashboard; never a false "Reads well" verdict on a dashboard with no tooltip text at all)
- Optional `.md` or `.txt` save to the Downloads folder

## Limitations

- Read-only. The skill does not modify the workbook. All output is text.
- Proposed text names what the chart shows structurally, not what it means. "Monthly sales by segment" is in scope. "Northeast is winning" is not; that is interpretation the author owns.
- Author declares the audience. If declined ("just pick one"), the skill defaults to Analyst voice (safest voice-mixing fallback) and announces it.
- One dashboard per run. Switching dashboards mid-run triggers fresh reads against the new target.
- Dashboards with zero customized tooltips and no captions trigger a design-reference mode rather than a false "Reads well" verdict. The skill offers the T1-T6 rules as design guidance to apply before building the text.
- Placeholder-only dashboards (every text surface is "Sheet 1" / "Insert title here" / default) trigger a single consolidated recommendation instead of a 15-finding T6 cascade.
- Tooltip and caption text lives in per-worksheet XML. The skill reads it via `get-worksheet-xml` on each contained sheet (with the author directed to make each sheet active first), not via a single dashboard-level call.

## Troubleshooting

- **"No workbook open."** The skill does not refuse. It offers to walk through the T-catalog and audience-voice-rules as reading reference until a workbook is open.
- **"The dashboard already reads in plain language."** The skill detects this (titles and captions use everyday terms with no `SUM()` or raw field references) and emits the honest verdict with only the real findings (if any).
- **"The skill asked me to make a sheet active."** During the audit, the skill asks you to activate each contained sheet one at a time before it reads that sheet's XML. This reduces the chance of a stale or dashboard-bound-sheet read failure.
- **"I want a different voice now that I have seen the output."** Say "use operations voice" (or any other profile) mid-run. The skill re-emits only the proposed rewrites in the new voice. The findings list and Desktop steps stay unchanged.
- **"The file save failed."** The skill emits the full rewrite set inline anyway and names the save error. Copy from chat into your notes.
- **"The skill refused to write a caption I asked for."** It should refuse if the caption would state an interpretation the dashboard does not structurally show (e.g., "Northeast is winning"). It delivers a structural rewrite in place.

## Support

File issues in the Tableau Agent Skills repo.
