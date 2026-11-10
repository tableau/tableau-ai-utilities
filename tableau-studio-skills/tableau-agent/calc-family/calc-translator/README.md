# Calc Translator

Translates a single calculated expression from SQL, Excel, or Power BI DAX into a working Tableau calculated field. Classifies the target calc type, writes the calc, verifies it against real data, and reports semantic drift honestly when the translation is approximate.

**Example:** "Translate this DAX: `CALCULATE(SUM(Sales[Amount]), FILTER(Sales, Sales[Region] = "West"))`" returns a FIXED LOD (`{ FIXED [Region] : SUM(IF [Region] = "West" THEN [Amount] END) }`), authored via `author-calc`, placed on a scratch sheet, verified via `get-summary-data`, and marked VERIFIED with no drift caveat needed. Baseline agent behavior would misroute this to a row-level calc and silently produce wrong numbers.

***

## What it does

Takes one expression from another dialect and ports it to Tableau, one at a time. It parses the source, routes to the correct Tableau calc type (row-level, aggregate, LOD, or table calc), maps every function through a dialect-specific translation table, resolves every field reference against your target datasource, writes the calc, and verifies the output against real data on a scratch sheet.

Semantic drift is reported, not hidden. When a translation is approximate (DAX `EARLIER()` has no direct Tableau equivalent; Excel `IFERROR` catches errors that `IFNULL` doesn't; SQL integer division doesn't match Tableau's float division), Calc Translator gives you the closest expression AND an explicit caveat citing the drift catalog.

After a verified translation, it optionally hands off to Calc Optimizer for a performance pass. Handoff is offered, never forced.

## When to use it

- "Translate this SQL to Tableau"
- "Convert this DAX to a Tableau calc"
- "Port this Excel formula to Tableau"
- "What would this Snowflake expression look like as a Tableau calc"
- "Move this Power BI measure to Tableau"

## When NOT to use it

- Not for writing a Tableau calc from a natural-language description (use calc-writer)
- Not for debugging an existing Tableau calc (use calc-debugger)
- Not for optimizing performance of an already-translated calc (that's the Phase 5 handoff to calc-optimizer)
- Not for migrating a whole workbook, model, or query (single expression only)
- Not for setting up a data source connection (use data-source-connector)
- Not for VLOOKUP, XLOOKUP, INDEX-MATCH, or DAX RELATED. Those are joins, not calcs. Calc Translator refuses and hands off to join-and-relationship-advisor.

## How to trigger it

- "Translate this SQL"
- "Convert this DAX to Tableau"
- "Translate this Excel formula"
- "Port this expression to Tableau"
- "What would this look like in Tableau"
- "Rewrite this calc in Tableau"
- "Help me convert this formula"

## What you'll need

- Tableau Studio with the target datasource actively connected
- The source expression pasted verbatim, and the dialect stated (SQL and which vendor, Excel, or DAX)
- The MCP tools Calc Translator uses: `list-workbook-datasources`, `list-available-fields`, `resolve-field`, `author-calc`, `add-worksheet`, `rename-sheet`, `add-field`, `get-summary-data`, `get-workbook-inventory`
- One expression per invocation. Multiple expressions run as separate cycles.

## Example walkthrough

**Input:** "Translate this SQL to Tableau: `SUM(Amount) OVER (PARTITION BY Region)`"

**Output (Phase 0 through Phase 6):**

```
Phase 0 - Intake and Setup
  Dialect: SQL (vendor: Snowflake, per your session context)
  Target datasource: Sales_Extract (auto-selected, only one connected)
  Parameter-referencing calcs on target: none. Standard write mode.

Phase 1 - Parse and Route
  Aggregation with a PARTITION BY dimensional context.
  Per the Calc-Type Routing table, this routes to an LOD, not a
  window/table calc.
  Fields referenced: Amount, Region.
  Proposed routing: FIXED LOD on Region. Confirm before I resolve?

  [user confirms]

Phase 2 - Resolve Fields
  Batched resolve-field for Amount and Region. Both resolve.

Phase 3 - Translate and Write
  Formula:
    { FIXED [Region] : SUM([Amount]) }
    // Translated from SQL SUM(Amount) OVER (PARTITION BY Region).

  Proposed name: T: Region Total (15 chars, under 20-char cap).
  Pre-write validation gate:
    - No parameter double-qualification: PASS
    - Name length: PASS (15/20)
    - Comment position: PASS (at end)
    - No collision: PASS
  Writing via author-calc.
  Confirmed present in list-available-fields.

Phase 4 - Verify
  Scratch sheet: T-Verify-2026-09-11-1523
  Placed [T: Region Total] and [Region] on Detail.
  get-summary-data returned per-region totals matching source.
  Status: VERIFIED. No drift caveat needed.

Phase 5 - Handoff Offer
  This is an LOD. Want me to hand off to calc-optimizer for a
  performance pass and deeper verification? (yes/no)
```

If you decline the handoff, the run closes with a delivery summary: "Handoff declined; translation shipped as-is."

## What you get back

- **Deterministic calc-type routing.** Source pattern (aggregation, partition context, window function, lookup) maps to one Tableau calc type via the routing table, not by model judgment.
- **Function mappings for three dialects.** Top 20 SQL functions (across Snowflake, BigQuery, SQL Server, Redshift, Postgres, ANSI), top 15 Excel functions, top 15 DAX functions. Each entry includes drift notes where the mapping is approximate.
- **Semantic drift catalog** for the six most common approximate translations: SQL integer vs. float division, DAX context transition, Excel error semantics vs. Tableau nulls, timezone handling, rounding modes, and FIXED LODs ignoring dimension and date filters (fix: Add to Context). Caveat text is included verbatim in the output when the drift applies.
- **Pre-write validation gate.** Every calc is checked for parameter double-qualification, name length (20-char cap), comment position (comments go at the end because `author-calc` collapses leading newlines), and name collision (`T:` prefix) before being written.
- **Mandatory verification.** Every translated calc is placed on a scratch sheet and read via `get-summary-data`. Status is VERIFIED, DRIFT (delta reported), or UNVERIFIED (verification impossible, run does not close as complete).
- **Optional Calc Optimizer handoff.** After VERIFIED, offers a routing-based handoff to calc-optimizer (any calc type) for a performance pass. Declining is a valid completion state.
- **Manual follow-ups called out.** Parameter creation, join setup where a VLOOKUP was refused, `T:` prefix cleanup once the translation is approved.

## Limitations

- **One expression per run.** Multiple expressions get sequential cycles, not a batch.
- **Refuses lookup translations.** VLOOKUP, HLOOKUP, XLOOKUP, INDEX-MATCH, DAX RELATED are joins, not calcs. Calc Translator refuses and hands off to join-and-relationship-advisor.
- **Does not create parameters.** If the source references a parameter, Calc Translator names it, describes its type/default, and gives manual creation instructions. `author-parameter` is documented as unreliable and Calc Translator will not use it.
- **Does not create Sets or hierarchies.** Sets are invisible to `resolve-field`, `list-available-fields`, and shelf-placement tools regardless of how they're created. For a Top-N Set translation, Calc Translator proposes a `RANK()`-based table calc filter instead, and notes that placing it on the Filters shelf is a manual Desktop step (no Filters-shelf placement tool exists in this environment).
- **DAX `EARLIER()` and full `CALCULATE` context transition have no exact Tableau equivalent.** The translation approximates the common case with a strong drift caveat. Verify against the source system for nested-filter scenarios.
- **Small samples reduce verification confidence.** If the target datasource returns fewer than ~5 rows on the verification probe, Calc Translator notes lower confidence in the delivery summary. Drift that only appears at scale can be masked.
- **Does not mutate the source artifact.** SQL query, Excel workbook, and DAX model are read-only. Calc Translator translates into Tableau, never modifies the origin.
- **20-character name cap.** Every translated calc name is capped at 20 chars. Longer source names get a proposed short name; Calc Translator confirms with you before writing.

## Troubleshooting

- **"The translation returned wrong numbers."** Check the drift status in the delivery summary. If it says VERIFIED with no drift caveat, verify at scale (the verification sample may have been small). If it says DRIFT, the delta is reported and Calc Translator will offer to reformulate.
- **"`author-calc` succeeded but the calc isn't in `list-available-fields`."** Check Tableau Studio for a blocking modal dialog. Calc Translator does not retry against a blocked Desktop. Dismiss the modal, then it retries once.
- **"A freshly-created parameter isn't resolving by bare name."** Known platform reliability gap in new-parameter resolution, distinct from the `author-parameter` Windows bug. Reselect or refresh the Data pane in Desktop and retry. If still failing, Calc Translator gives manual instructions to create the calc in Desktop's editor directly.
- **"`resolve-field` returned multiple matches for the same field name."** Same field name across tables or datasources. Calc Translator stops and asks you to pick — it will not guess based on position or first-match.
- **"The source function has no Translation Rules entry."** Calc Translator reports the gap plainly, offers the closest analog with a strong drift caveat.
- **"Verification says UNVERIFIED."** Datasource may have disconnected or the cloud query timed out. Calc Translator retries once, and on a second failure logs UNVERIFIED with manual verification instructions rather than declaring the run complete.

## Support

File issues in the same channel you use for other Tableau Studio skill feedback. Include the source dialect and vendor, the exact source expression, the translated calc, the verification status, and any drift caveat that appeared.
