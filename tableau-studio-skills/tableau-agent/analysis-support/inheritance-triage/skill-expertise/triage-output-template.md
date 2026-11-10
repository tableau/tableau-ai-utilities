# Triage Output Template (Orient mode)

One-page template for inheritance-triage Orient-mode output. Word count hard-capped at 500 (HC-2).

## Section 1: Headline

**Target.** 1-2 sentences.
**Word budget.** 40.

**Pattern.** "This workbook is [name or inferred-purpose]. Last modified [date] by [author if available]."

**If modified-date not available.** "This workbook is [name]. Modified date not available in the file metadata (HC-6)."

**Example.** "This workbook is a 2026 sales performance dashboard. Last modified 2026-08-14 by jsmith."

## Section 2: Primary dashboards

**Target.** 3-5 bullets.
**Word budget.** 100 total (20 per bullet).

**Pattern.** Each bullet: "- **[Dashboard name]** ([N sheets]). Answers [structural question]."

**"Answers X" guidance.** Structural, not interpretive. "Shows revenue by region over time" is fine. "Shows that revenue is strong" is not (HC-8-adjacent discipline from phone-layout-blueprint).

**Example.**
- **Executive Overview** (4 sheets). Shows total revenue by region, by month, and by segment, with a KPI tile.
- **Product Detail** (2 sheets). Shows product-level revenue and profit at the SKU level.

**If more than 5 dashboards.** Pick the 5 highest-sheet-count or 5 most-recently-modified. Mention the omitted count: "3 additional dashboards not shown."

## Section 3: Data sources

**Target.** Count + names.
**Word budget.** 40.

**Pattern.** "**Data sources.** [N] total: [name 1], [name 2], ...."

**Example.** "**Data sources.** 3 total: Orders (primary), Customers, Products."

**If more than 7 data sources.** Note it and name the top 5 by sheet-count references.

## Section 4: Calc complexity tiers

**Target.** 3 lines.
**Word budget.** 50.

**Pattern.**
```
Calcs: N total.
- Simple (row-level or basic aggregates): M
- LOD-heavy (one or more FIXED / INCLUDE / EXCLUDE): O
- Nested (calc references another calc): P
```

**Example.**
```
Calcs: 23 total.
- Simple: 12
- LOD-heavy: 7
- Nested: 4
```

## Section 5: Sheet complexity top-10

**Target.** Compact table.
**Word budget.** 120.

**Pattern.** Markdown table with columns: Sheet, Score, Tier.

**Example.**
```
| Sheet | Score | Tier |
|---|---|---|
| Customer Cohort Retention | 10 | Complex |
| Revenue Trend FY26 | 8 | Complex |
| Product Profit by Segment | 7 | Complex |
| Regional Breakdown | 5 | Moderate |
| Monthly Sales | 4 | Moderate |
| ... | | |
```

**If workbook has under 10 sheets.** Show all sheets. If over 10, show top-10 and note count omitted: "15 additional sheets not shown; run Complexity-score mode for the full list."

## Section 6: Where to start reading

**Target.** 1-2 sentences.
**Word budget.** 50.

**Pattern.** "Start with [Dashboard X] to see the headline. Then read [sheet Y]'s calc, since it drives [other sheet]. The [Complex] sheets will take the longest; save them for a focused reading pass."

**Example.** "Start with Executive Overview to see the headline revenue number. Then read the Customer Cohort Retention calcs, since they drive the Executive Overview's KPI tile. The three Complex sheets will take 20+ minutes each; schedule time."

## Section 7: Known issues flag

**Target.** Bulleted list.
**Word budget.** 80.

**Pattern.** Only flag issues that are visible from the tools. Examples: default sheet names ("Sheet 1," "Dashboard 1"), orphan sheets (not on any dashboard), hidden sheets (useful signal), broken field references.

**Example.**
- 2 sheets named "Sheet 7" and "Sheet 12" (default names).
- 1 orphan sheet ("Scratch_v3") not placed on any dashboard.
- 3 hidden sheets, likely intentional for action-config.

**If no issues.** Omit the section.

## Section 8: Optional handoffs

**Target.** Short list.
**Word budget.** 100.

**Pattern.** One line per handoff target. Each: "**[Target skill]**: [what it adds]. If not installed, [manual fallback]."

**Example.**
- **data-scribe**: full metric dictionary. If not installed, read field descriptions manually from the Data pane.
- **calc-documenter**: full per-calc dictionary. If not installed, read calcs individually from the Data pane.
- **workbook-summary-onepager**: stakeholder-handoff onepager. If not installed, combine this orient summary with a one-paragraph headline manually.
- **workbook-auditor**: change tracking going forward. If not installed, snapshot the workbook manually and diff against future versions.

## Total word budget

40 + 100 + 40 + 50 + 120 + 50 + 80 + 100 = 580 words.

Section 7 (Known issues) is optional and often zero; typical output lands around 480-520 words. The 500-word cap is tight on purpose per HC-2.

## Trimming discipline when over cap

If output exceeds 500 words:

1. Trim Section 2 (Primary dashboards): shorten "Answers X" phrases.
2. Trim Section 7 (Known issues): list only the top 3.
3. Trim Section 8 (Optional handoffs): combine into one paragraph.

Never trim Section 1 (Headline), Section 5 (Sheet complexity top-10), or Section 6 (Where to start reading). Those are the load-bearing orienting content.

## HC-3 short-circuit template

For workbooks under 5 sheets AND under 10 calcs:

```
This workbook is small: [N] sheets, [M] calcs, [K] data source(s). No full triage needed. Start with [the one or two dashboards]; everything else is a worksheet feeding them.
```

2 sentences. ~40 words. Done.
