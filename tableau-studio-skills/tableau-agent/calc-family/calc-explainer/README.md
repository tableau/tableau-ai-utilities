# Calc Explainer

Explain a single Tableau calculated field in plain language, grounded in the actual formula and its place in the workbook's calc family.

**Example:** Ask "explain Profit Ratio" and get a four-dimension answer that names what it computes, why it uses SUM-of-ratios structure, what other calcs depend on it, and how it behaves at runtime.

## What it does

Given the name of a calculated field in an open Tableau workbook, produces a compact four-dimension explanation: what the calc computes, why it is structured that way, how it fits with the workbook's other calcs, and what to expect at runtime (row-level vs aggregate behavior, LOD grain, table-calc gotchas). Every sentence cites either the formula, a specific pattern, or a named reference. Read-only. Nothing gets written back to the workbook.

## When to use it

- "I inherited this workbook and I need to understand a specific calc before I touch it"
- "I want to know why this Profit Ratio uses SUM(Profit) / SUM(Sales) instead of AVG(Profit / Sales)"
- "I need to explain a LOD or table calc to a stakeholder in plain English"
- "I want to see which other calcs depend on this one before I edit it"
- "I want the runtime story (row vs aggregate, LOD grain) without opening the calc editor"

## When NOT to use it

- Not for documenting every calc in the workbook (use `calc-documenter` for bulk)
- Not for diagnosing why a calc returns NULL (use `calc-debugger`)
- Not for calc naming, comments, or hygiene audit (use `calc-linter`)
- Not for rewriting a slow calc (use `calc-optimizer`)
- Not for authoring a new calc (use `calc-writer`)
- Not for applying edits (this skill is read-only)

## How to trigger it

- "explain this calc"
- "what does Profit Ratio do"
- "explain Profit Ratio in plain English"
- "walk me through this calculated field"
- "why is this calc structured this way"

## What you'll need

- Tableau Studio with the target workbook open
- The name of the calc you want explained (skill lists closest matches if the name is off)
- Optional: a prior `calc-documenter` run in the same session (skill will consume its handoff automatically if the stored formula still matches)

## Example walkthrough

**Input:** "Explain Profit Ratio"

**Output:**

```
Calc Explanation: Profit Ratio (Orders)
Signal source: local extract

What it computes.
Returns the ratio of total profit to total sales as an aggregate. Formula: SUM([Profit]) / SUM([Sales]). Produces a percentage-shaped decimal usable in KPI callouts and profitability breakdowns.

Why it is structured this way.
Uses the agg-first-then-divide pattern. Aggregating numerator and denominator separately before division prevents each row's ratio from being weighted equally, which would misrepresent the workbook total. This is the standard structure when the reader wants overall profitability rather than the average of per-row profitability.

How it fits in the calc family.
Parents (uses): Profit, Sales
Children (used by): Profitable Threshold, Profit Ratio YoY
Consumed downstream by two calcs and referenced on three worksheets. Editing this formula will ripple into both children.

What to expect at runtime.
Aggregate calc. Cannot be placed on the row-level shelf; must sit on a dimension partition (Category, Region, etc.). Table-calc addressing does not apply. If the workbook is filtered, the ratio recomputes against the filtered totals rather than the full dataset.
```

The four dimensions land in the same order every run. If the calc has no parents or no children, that empty state prints explicitly rather than being skipped.

## What you get back

- Four-dimension explanation in one chat block, typically 15 to 25 lines
- Signal-source label (handoff vs local extract) so you can trust the provenance
- Author caption quoted verbatim if the calc has one
- Handoff schema `calc_explanation/1` for downstream skills (calc-debugger, calc-optimizer)

## Limitations

- One calc per run. Multi-calc requests route to `calc-documenter`.
- Case-sensitive name lookup. "WindowSum" will not resolve to "WindowSUM"; the skill offers the closest match rather than guessing.
- Cross-datasource references are named but not traversed (the target calc's parents in another datasource show as `cross_datasource_reference: Orders.Sales` without full resolution).
- Table-calc partition and addressing detail is left to the sheet-level context, not extracted per calc.
- Set and parameter references are treated as field references. Set membership and parameter value lists are not enumerated.

## Troubleshooting

- **"Calc name not found"** then the skill lists the top 3 closest matches by name similarity. Retry with the exact name (case matters).
- **"Ambiguous calc name across datasources"** then the skill asks one clarifying question ("Explain Profit Ratio from Orders or from Returns?"). Answer with the datasource name.
- **"Signal source: local extract" when you expected handoff** then the calc's current formula differs from what `calc-documenter` recorded. This is V5 staleness detection working correctly. Re-run `calc-documenter` if you want fresh handoff data.
- **A dimension prints "no parents; no children"** then the calc genuinely has no references. Not a failure; the empty state is rendered per HC#4.

## Support

File issues in the Tableau Agent Skills repo.
