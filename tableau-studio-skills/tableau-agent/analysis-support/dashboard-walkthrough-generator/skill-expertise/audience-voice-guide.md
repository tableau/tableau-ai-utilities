# Audience Voice Guide

Locked audience taxonomy for dashboard-walkthrough-generator. Four profiles. The skill maps any author-declared audience to one of these before generating output. No ad-hoc profiles.

## Executive

**Who.** C-suite, VP level, board, senior stakeholder with 5-10 minutes.

**Tone.** Terse. Headline first. One number per sentence. Minimal jargon. No methodology detail unless asked. Confidence in the number, not in the chart construction.

**Length target.** 30-second elevator plus a 2-minute full walkthrough. Any longer and the audience disengages.

**Script shape.**
- Open with the headline number.
- Name the one chart that carries the headline.
- Walk through at most 3 supporting sheets.
- Close with a one-sentence "so what" that the author provides (not fabricated by the skill).

**Anticipated follow-ups (what to prep for).**
- Strategic. "What should we do about this." Not methodological.
- Trajectory. "Is this trending up or down." Pre-answer with the data point.
- Comparison. "How does this compare to last quarter / to target / to peers." Pre-answer if the data supports it.
- Confidence. "How sure are we." Pre-answer with the data source and refresh date.

## Analyst

**Who.** Fellow analyst, data engineer, data scientist, technical reviewer.

**Tone.** Technical. Named fields, aggregations, filters, and computation methods. Longer walkthrough tolerated. Comfortable with jargon the analyst audience shares.

**Length target.** 10-15 minutes total. Each sheet gets a methodology beat.

**Script shape.**
- Open with the data source and refresh date.
- For each sheet: fields on Rows / Columns, aggregation, filters, mark type, computation notes.
- Call out any LOD, table calc, or cross-DS join that shapes the result.
- Close with known limitations and open methodological questions.

**Anticipated follow-ups.**
- Methodology. "How is this computed." Pre-answer with the calc text or aggregation.
- Scope. "What does the extract cover." Pre-answer with the data source filter.
- Edge cases. "What happens for X." Pre-answer if visible in the data.
- Reproducibility. "Can I rebuild this." Pre-answer with the source table and key fields.

## Operations

**Who.** Line manager, ops lead, account manager, anyone whose follow-up is "what do I do next Monday."

**Tone.** Action-focused. What to do next, by when, by whom. Named entities (accounts, regions, products) over abstract summaries.

**Length target.** 5-8 minutes. Front-load the action.

**Script shape.**
- Open with the top-N action items the data surfaces.
- Each sheet: who is in the top-N, what to do about them.
- Avoid trend analysis unless it drives a specific action.
- Close with "here is who to call this week."

**Anticipated follow-ups.**
- Tactical. "Which account should I call first." Pre-answer with the ranked list.
- Attribution. "Why is X in the top-N." Pre-answer with the field that drove the rank.
- Timeline. "When did this change." Pre-answer with the time dimension on the chart.
- Ownership. "Who owns this." Pre-answer if the data has an owner field.

## External

**Who.** Customer, partner, external audience, cross-industry group.

**Tone.** Context-first. Define jargon. No internal acronyms. Assume the audience does not know the data source, the business, or the team.

**Length target.** 10 minutes. Context eats time; budget for it.

**Script shape.**
- Open with a 1-minute context block: what business, what data, what time period.
- For each sheet: define the measure and dimension before showing the chart.
- Avoid internal benchmarks ("below target") unless target is defined.
- Close with a plain-language summary of what the dashboard answers.

**Anticipated follow-ups.**
- Clarifying. "What does ARR mean." Pre-answer with the definition.
- Scope. "Is this all customers or just enterprise." Pre-answer with the filter.
- Framing. "What should I take away from this." Author owns the takeaway; skill does not fabricate.
- Comparison. "How does this compare to industry benchmarks." Author owns; skill does not fabricate benchmarks.

## Mapping ad-hoc audiences to locked profiles

The author may describe the audience in non-standard terms. Map before generating.

| Author's phrase | Mapped profile |
|---|---|
| "my boss" | Executive if VP+ title, Operations if direct manager |
| "my team" | Analyst |
| "my VP" | Executive |
| "the board" | Executive |
| "a customer" | External |
| "a partner" | External |
| "cross-functional group" | Analyst by default; ask if that is wrong |
| "mixed audience" | Pick one and warn: "walking through at the lowest-context audience in the group" |

State the mapping in the output so the author can correct.

## Voice violations to catch

- Using analyst-level jargon in an executive script.
- Using executive brevity in an external context (loses the audience).
- Fabricating conclusions in any voice (HC-3 violation regardless of audience).
- Mixing voices mid-script.
