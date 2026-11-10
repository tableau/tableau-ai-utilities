Full output skeleton for the generated metric dictionary. Fill every bracketed slot; omit a whole section if that category has zero members (e.g. no Sets exist).

```markdown
# Metric Dictionary: [Datasource Name]
Generated: [date]
Workbook: [workbook name]
Total Fields: [count] (Dimensions: X | Measures: Y | Calcs: Z | Parameters: P)

***

## Dimensions

### [Field Name]
- **Type:** String / Integer / Boolean
- **Role:** Dimension
- **Cardinality:** [Low/Medium/High] ([count] distinct values)
- **Sample Values:** value1, value2, value3, value4, value5
- **Used In:** Sheet1, Sheet3, Dashboard1
- **Description:** [Plain-English description inferred from name, values, and context]

[repeat for each dimension]

For a multi-table or blended datasource, add a **Source Table** property to each field entry (see Multi-table rule #7 in SKILL.md) and, where a relationship/blend introduces fanout risk, a `[Note: appears at [grain] in [table] — joins may duplicate rows at finer grain.]` line. For an empirically-confirmed blend link (a field verified via a manually-built worksheet to be the active link between two separate datasources), use `[Blend note — EMPIRICALLY CONFIRMED: ...]`; for behavior inferred from standard Tableau mechanics but not independently re-verified this run, use `[Blend note — NOT empirically tested this session, standard Tableau behavior: ...]`. Never present the two as equally certain.

***

## Measures

### [Field Name]
- **Type:** Decimal / Integer
- **Default Aggregation:** SUM / AVG / COUNT / etc.
- **Range:** [min] to [max] (avg: [avg])
- **Used In:** Sheet1, Sheet2
- **Description:** [Plain-English description]

[repeat for each measure]

***

## Field Family Summary (300+ fields, "all" requested, repetitive naming detected)

Use this block INSTEAD OF individual Dimension/Measure entries for a group of fields sharing a detected naming pattern (e.g. a numbered suffix) or flagged as near-duplicates by tooling during sampling. Every family member's name must still appear (via the naming pattern line) so no field is dropped from coverage — see SKILL.md Phase 1 rule #8.

### [Family Name] (e.g. "Cost M01 through Cost M24", N fields)
- **Naming pattern:** [prefix][NN] — list the first and last member names to make the pattern unambiguous
- **Type / Default Aggregation:** [shared across the family]
- **Description:** [Plain-English description of what the family represents]
- **Representative samples (grand total, or count/avg for boolean-style flags):**
  - [First member] = [value]
  - [Middle member, if sampled] = [value]
  - [Last member] = [value]
- **Disclosure (required):** "[N] of [M] fields in this family were individually sampled; the rest share the confirmed naming pattern and are listed by name only, not independently verified."

[repeat for each detected family; a 300+ field datasource without repetitive naming still gets full individual Dimension/Measure entries as normal]

***

## Date/Time Fields

### [Field Name]
- **Type:** Date / DateTime
- **Range:** [earliest] to [latest]
- **Granularity Levels:** Year, Quarter, Month, Week, Day
- **Used In:** Sheet1 (Month level), Sheet4 (Year level)
- **Description:** [Plain-English description]

***

## Calculated Fields

### [Calc Name]
- **Formula:** `[full formula]`
- **Type:** [LOD / Table Calc / Basic / String / Date / Conditional]
- **Returns:** [data type]
- **Dependencies:** [fields and calcs this references]
- **Referenced By:** [calcs that depend on this one]
- **Parameters Used:** [if any]
- **Plain English:** [One-sentence explanation of what this calc computes]
- **Used In:** Sheet2, Sheet5

[repeat for each calc, ordered by dependency chain — leaf calcs first, compound calcs after their dependencies]

If a circular reference is detected (see SKILL.md Phase 2 rule #6), list the involved calcs together at the end of this section instead of forcing them into the dependency order:

### Circular Reference: [Calc A] <-> [Calc B]
- **Note:** Circular reference detected — dependency order not determinable. [Calc A]'s formula references [Calc B]; [Calc B]'s formula (directly or transitively) references [Calc A] back.
- Document each calc's own formula/type/plain-English fields as normal, just without a resolved position in the dependency ordering.

***

## Parameters

### [Parameter Name]
- **Data Type:** String / Integer / Float / Date / Boolean
- **Current Value:** [value]
- **Allowable Values:** [list] or [range: min to max, step]
- **Purpose:** [One-sentence: what selecting a different value changes]
- **Referenced By:** [calcs/filters that use this parameter]

***

## Sets

Per Hard Constraint #3b, Sets have no reliable automated discovery tool in this environment. Omit this section entirely only if Phase 1's inventory turned up zero Set-shaped fields; otherwise include the line: "Sets not scanned this run — no reliable discovery tool for this environment; check Desktop's Data pane manually." Never fabricate a Set entry from inference.

### [Set Name] (only if genuinely discoverable from inventory)
- **Based On:** [dimension field]
- **Membership Logic:** [condition or manual list]
- **Used In:** [sheets/calcs]

***

## Groups & Bins

### [Name]
- **Based On:** [source field]
- **Type:** Group (manual) / Bin (automatic)
- **Definition:** [group members or bin size]

***

## Hierarchies

Per Hard Constraint #3b, custom Hierarchies have no reliable automated discovery tool in this environment (standard date hierarchies that Tableau creates implicitly for date fields don't need this caveat — note those inline on the date field's own entry instead). Omit this section only if Phase 1's inventory turned up zero custom-hierarchy fields; otherwise include: "Custom hierarchies not scanned this run — no reliable discovery tool for this environment; check Desktop's Data pane manually."

### [Hierarchy Name] (only if genuinely discoverable from inventory)
- **Levels:** Level1 > Level2 > Level3
- **Used In:** [sheets with drill-down enabled]

***

## Field Usage Summary

### Most-Used Fields (5+ sheets)
- [Field] — used in [N] sheets: [sheet list]

### Unused Fields (defined but never placed)
- [Field] ([type]) — [note]

[These may be candidates for cleanup — see data-quality-review for hygiene analysis]

***

## Notes
- [Any anomalies discovered during documentation]
- [Fields where the purpose was unclear from name/values alone — flagged for manual review]
```
