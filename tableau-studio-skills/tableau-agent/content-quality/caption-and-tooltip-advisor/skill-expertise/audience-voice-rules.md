# Audience Voice Rules

Per-rule voice modifiers for the T1-T6 catalog. Rewrites must land in the declared audience voice.

## Executive

**Length target per rewrite.** at or under 8 words for a tooltip row, at or under 20 words for a caption.

**Voice.** Headline-first. Business terms. No fields, no aggregations.

**Examples.**
- `SUM(Sales)` → "Total revenue"
- `COUNTD(Customer ID)` → "Unique customers"
- Caption: "Revenue by region, this quarter vs. last."

## Analyst

**Length target per rewrite.** at or under 15 words for a tooltip row, at or under 40 words for a caption.

**Voice.** Named fields acceptable. Methodology notes acceptable in captions.

**Examples.**
- `SUM(Sales)` → "Sales total"
- `COUNTD(Customer ID)` → "Distinct customer count"
- Caption: "Sum of sales by region, from the Orders extract, filtered to the current fiscal year."

## Operations

**Length target per rewrite.** at or under 10 words for a tooltip row, at or under 25 words for a caption.

**Voice.** Action-focused. Named entities. Time-bound.

**Examples.**
- `SUM(Sales)` → "Sales this period"
- `COUNTD(Customer ID)` → "Active customers now"
- Caption: "Top accounts by sales. Priority list for the week."

## External

**Length target per rewrite.** at or under 12 words for a tooltip row, at or under 35 words for a caption.

**Voice.** Context-first. Define measures. No internal jargon.

**Examples.**
- `SUM(Sales)` → "Total sales in the window shown"
- `COUNTD(Customer ID)` → "Number of unique customers"
- Caption: "Shows how our total sales have moved over the last four quarters, broken out by region."

## Length enforcement

If a proposed rewrite exceeds the audience's length target, the skill shortens before emitting. If shortening would strip meaning, the skill flags and asks the author to resolve.

## Voice-consistency check

A single run must use one voice for every rewrite. If the declared audience is "executive" and a rewrite reads analyst-technical, the Validation Gate (V4) catches it before output.

## Non-standard-audience handling

If the author declares an audience not in the four locked profiles (e.g., "my team's weekly standup"), the skill maps to the closest profile and states the mapping in the output: "Mapping 'weekly standup' to Operations voice. Say if that is wrong."

Common mappings:
| Author's phrase | Mapped profile |
|---|---|
| "the exec readout" | Executive |
| "my team" | Analyst |
| "the standup" | Operations |
| "a customer-facing deck" | External |
| "my VP" | Executive |
| "a cross-functional review" | Analyst |

## Avoid

- Mixing voices in a single run.
- Fabricating any business conclusion in any voice (HC-3 regardless of audience).
- Using analyst methodology in external captions.
- Using external-length captions in executive output (over-length burns attention budget).
