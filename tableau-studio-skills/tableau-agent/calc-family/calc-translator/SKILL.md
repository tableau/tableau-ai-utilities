---
name: calc-translator
description: "Use when the user says 'Translate this Excel formula', 'convert this DAX', 'translate this SQL', 'what would this look like in Tableau?' Turns one SQL, Excel, or Power BI DAX expression into a working Tableau calc, verifies it, and flags where the translation isn't exact."
---

# Calc Translator

You translate a single calc expression from SQL, Excel, or Power BI DAX into a working Tableau calculated field. One expression per invocation. Verification is mandatory. Semantic drift is reported honestly, not smoothed over. After a successful translation, optionally hand off to the Calc Optimizer skill for performance optimization and deeper verification.

**Why this shape.** Users who inherit content from other platforms currently have no repeatable way to port logic into Tableau. Direct translation is dialect-sensitive: `DATEADD` argument order differs between SQL Server and Tableau, DAX iterators have no direct Tableau equivalent, Excel `VLOOKUP` is a join not a calc. This skill encodes the dialect mappings, applies Tableaus calc-type judgment, writes the calc, verifies it against real data, flags cases where the translation is approximate, and routes performance-sensitive translations to the Calc Optimizer skill for optimization.

**File structure:** Single SKILL.md (this file). No reference files in v1 — all translation rules and drift patterns are inline below.

***

## When to use (full trigger detail)

Translates a single calc expression from SQL, Excel, or Power BI DAX into a working Tableau calculated field. Classifies the target calc type (row-level, aggregate, LOD, table calc), writes and verifies the calc via author-calc plus get-summary-data, reports semantic drift between the source dialect and Tableau, and optionally hands off to calc-optimizer for performance optimization and deeper verification once the translation lands. Trigger on translate this SQL, convert this DAX, translate this Excel formula, port this expression to Tableau, what would this look like in Tableau, rewrite this calc in Tableau. Do NOT trigger on. writing a Tableau calc from a natural-language description (defer to calc-writer), debugging an existing Tableau calc (defer to calc-debugger), migrating a full workbook or model (out of scope, single-expression only), or optimizing performance of an already-translated calc (hand off to calc-optimizer).

## Trigger Conditions

**Positive:** translate this SQL, convert this DAX to Tableau, translate this Excel formula, port this expression to Tableau, move this calc from Power BI, what would this look like as a Tableau calc, rewrite this in Tableau, help me convert this formula.

**Negative (do NOT trigger):**
- Writing a Tableau calc from natural-language description — defer to `calc-writer`
- Debugging an existing Tableau calc — defer to `calc-debugger`
- Optimizing performance of an already-translated calc — hand off to `calc-optimizer`
- Translating an entire workbook, model, or query — single expression only
- Building a Tableau data source connection to the source system — defer to `data-source-connector`
- Recommending whether to migrate at all — strategic question, not a translation task

***

## Scope Boundaries

**IN:**
- Single-expression translation from SQL (ANSI-standard, Snowflake, BigQuery, SQL Server, Redshift, Postgres dialects), Excel formulas, and Power BI DAX
- Calc-type routing (row-level, aggregate, LOD, table calc) based on source-expression pattern
- Field-resolution verification against the target data source
- Post-translation verification via get-summary-data
- Semantic-drift reporting when the translation is approximate
- Optional handoff to the Calc Optimizer skill for performance optimization

**OUT:**
- Multi-expression batch translation
- Data source connection setup or ETL
- Query performance tuning on the source system
- Parameter creation (author-parameter unreliable; source parameter references become manual instructions)
- Set or hierarchy creation — sets have no `column_ref` any tool can resolve (invisible to `list-available-fields`, `resolve-field`, and shelf placement regardless of creation method), so this is unresolvable through current tools. If a translation request also asks for a Top-N Set, propose a `RANK()`-based table calc filter instead (see Common Mistakes) — but note that placing it on the Filters shelf itself has no tool path either (no Filters-shelf placement command exists in this environment), so that last step is manual regardless of which alternative is used
- Any mutation of the source SQL / Excel / DAX artifact
- Deep performance optimization (defers to calc-optimizer)

***

## Tools You Use

| Tool | Purpose | When to skip |
|------|---------|--------------|
| `list-workbook-datasources` | Confirm target data source. Batch with list-available-fields in Phase 0. | Never skip. |
| `list-available-fields` | Enumerate fields and types on the target data source. | Never skip. |
| `resolve-field` | Confirm every source-side field reference has a Tableau counterpart. Batch all resolve calls in one turn — for expressions referencing 10+ fields (wide SUMIFS-style ports), still issue as one batched turn rather than splitting into multiple rounds. | Skip only if the source expression references zero fields. |
| `author-calc` | Write the translated calc. Name it with the `T:` prefix and 20-character cap. | Never skip. |
| `add-worksheet`, `rename-sheet` | Create a scratch worksheet for verification, then rename it to a distinct name. Reuse a scratch sheet only for a single edit cycle — if a second edit is needed on the same sheet later in the run, re-read it via `get-worksheet-xml` first, or create a new scratch sheet instead of trusting an earlier cache file (reusing across multiple edit cycles has caused silent field-drops and stale-cache apply rejections). | Skip if a suitable scratch sheet already exists AND no edit has been applied to it yet this run. |
| `add-field` | Place the calc for the verification probe (row-level calc on Detail; LOD calc as SUM/ATTR on Text with its dimension on Rows). | Never skip during verification. |
| `get-summary-data` | Verify the calc produces expected output. | Skip only when the data source is disconnected; in that case output UNVERIFIED and stop. |
| `Skill` (invoke Calc Optimizer) | Optional Phase 5 handoff to `calc-optimizer` for performance optimization. | Skip if the tester declines the handoff offer. |

**Never mutate the source system.** This skill translates *into* Tableau; it does not touch the origin SQL query, Excel workbook, or DAX model.

**One expression per run.** Multiple expressions run as separate Phase 0-6 cycles.

***

## Hard Constraints

1. **Verification is mandatory.** Every translated calc is verified via get-summary-data on a scratch worksheet. If verification is impossible (data source disconnected, sheet creation blocked, cloud timeout), state Unable to verify explicitly and refuse to declare the translation complete.

2. **Parameter-safe write path.** If the target data source contains any parameter-referencing calc (detected by scanning existing calc formulas for `[Parameters].` references), do not invoke `build-and-apply-worksheet` or `bind-template` with `auto_apply`. The corruption is silent and undetectable via formula readback. Use `add-worksheet` plus `add-field` only.

3. **Bare parameter names.** When a translation includes a parameter reference, the Tableau formula uses the bare parameter name, never `[Parameters].[X]`. Double-qualification breaks author-calc silently.

4. **20-character field name cap.** Every translated calc name is 20 characters or fewer. Propose a shortened name if source exceeds this; confirm with the tester before writing.

5. **Comment placement after formula.** author-calc collapses leading newlines. Translation comments go at the end of the formula, never at the top.

6. **Blocking-modal awareness.** If any tool call hangs, times out, or returns garbled results after a mutation, instruct the tester to check Tableau Studio for a modal dialog before continuing. Do not retry the call.

7. **Semantic drift is reported, not hidden.** When a translation is approximate (DAX `EARLIER()` has no direct Tableau equivalent; Excel `VLOOKUP` maps to a join), output both the closest Tableau expression and an explicit This is not an exact translation. Difference: X. caveat citing the Semantic Drift Catalog.

8. **No fabricated fields.** If a source-side field has no counterpart in the target Tableau data source, stop and ask the tester to map the field or provide the missing one. Never invent a field.

9. **Calc-type routing is deterministic.** The Tableau calc type is determined by pattern-matching the source expression against the Calc-Type Routing table, not by inference. Ties resolve to the tables rule, not the models judgment.

10. **Single-expression only.** If the tester pastes multiple expressions, ask which one to translate first and offer to re-run for the others. Do not batch.

11. **Calc Optimizer handoff is offered, never forced.** After a VERIFIED translation, offer the handoff to Calc Optimizer. Never auto-invoke. If the tester declines, close the run cleanly.

12. **Declined handoff is a valid completion state.** Not every translation needs optimization. If the tester says ship it as-is, the run is complete. Do not treat this as an incomplete or failed run.

***

## Common Mistakes

Scan before writing any calc:

- **Assuming SQL function argument order matches Tableau.** `DATEADD` in SQL Server is `(part, number, date)`; Tableau uses `(part, interval, date)` — similar order, different terminology. `DATEDIFF` returns a different signed value on certain boundaries. Always check the Translation Rules table.
- **Translating DAX `CALCULATE` naively.** CALCULATE with filter modifiers is not a Tableau row-level calc — it is an LOD. Route via the Calc-Type Routing table.
- **Translating Excel `VLOOKUP` as a Tableau calc.** VLOOKUP is a join, not a calc. Refuse translation and hand off to `join-and-relationship-advisor`.
- **Writing the calc before resolve-field confirms every reference.** author-calc will succeed and produce a broken calc if a field is unresolvable.
- **Skipping verification because the source expression looked simple.** Simple expressions are the most common source of silent semantic drift (rounding rules, null handling, integer vs. float division).
- **Preserving the source name verbatim when it exceeds 20 characters.** Propose a shortened name up front.
- **Applying the T: prefix in a way that produces a duplicate.** If `T: X` already exists, increment to `T: X v2`. Never overwrite.
- **Auto-invoking Calc Optimizer.** The handoff is offered, not forced. Skipping the offer is a valid choice.
- **Treating a declined Calc Optimizer handoff as a failed run.** If the tester says no thanks, ship as-is, the run is complete.
- **Burying a per-key predicate inside the aggregate.** When the logic is a per-key test (e.g. customers with 2+ orders), offer a standalone flag calc (`{ FIXED [key] : agg } >= n`, boolean dimension) alongside the aggregate rate. Testers often prefer the reusable flag. Warn that a plain SUM or COUNT over the flag counts rows, not keys; use COUNTD(IF flag THEN key END).

***

## Worked Example — DAX CALCULATE + FILTER

Demonstrates the highest-value routing decision this skill makes. Base agent without the skill would typically route this as a row-level calc and produce wrong output. The skill routes correctly to an LOD and verifies.

**Input from tester:**

> Translate this DAX to Tableau: CALCULATE(SUM(Sales[Amount]), FILTER(Sales, Sales[Region] = "West"))

**Without the skill (baseline agent behavior):**

The agent would likely produce something like `IF [Region] = "West" THEN SUM([Amount]) END` — which is a mixed-aggregation row-level calc, produces null in most contexts, and drops the dimensional filter context DAX implied. Silent semantic error.

**With the skill (Phase 0 → Phase 6):**

**Phase 0.** Tester confirms: DAX source, target data source is Sales_Extract (single connected DS, auto-selected). No parameter-referencing calcs detected. Standard write mode.

**Phase 1.** Parse and route.

> Parsing DAX. The expression uses CALCULATE with a FILTER modifier, which imposes dimensional filter context. Per the Calc-Type Routing table, this routes to an LOD, not a row-level calc.
>
> Fields referenced: Sales[Amount], Sales[Region]. Both must resolve on the target.
>
> Proposed routing: FIXED LOD on Region. Confirm before I resolve fields?

Tester: confirmed.

**Phase 2.** Batched resolve-field calls for Amount and Region. Both resolve. No parameters referenced.

**Phase 3.** Translate and write.

> Translation:
>
> ```
> { FIXED : SUM(IF [Region] = "West" THEN [Amount] END) }
> // Translated from DAX CALCULATE(SUM([Amount]), FILTER([Region] = "West")).
> ```
>
> Proposed name: `T: West Sales` (13 characters, under the 20-char cap).
>
> Pre-write validation:
> - No parameter double-qualification: PASS
> - Name length: PASS (13/20)
> - Comment position: PASS (at end)
> - No collision: PASS (no existing `T: West Sales`)
>
> Writing via author-calc now.

author-calc succeeds. Calc appears in list-available-fields.

**Phase 4.** Verify.

> Creating scratch worksheet `T-Verify-2026-09-01-1247`. Placing `Region` on Rows and `SUM([T: West Sales])` on Text.
>
> get-summary-data returns:
> - West: 145,230
> - Every other region: 145,230 (same value, because a table-scoped FIXED ignores the Region dimension in the view)
>
> Expected behavior for a table-scoped FIXED LOD with a West-only condition. VERIFIED.
>
> No drift caveat needed for this pattern — CALCULATE with a single equality filter maps cleanly to a FIXED LOD with a conditional aggregate.

**Phase 5.** Handoff offer.

> Translation is verified. This is an LOD. Want me to hand off to `calc-optimizer` for a performance optimization pass and deeper verification? (yes/no)

Tester: no thanks, ship as-is.

**Phase 6.** Deliver.

> Complete.
>
> - Source: `CALCULATE(SUM(Sales[Amount]), FILTER(Sales, Sales[Region] = "West"))`
> - Target: `T: West Sales` = `{ FIXED : SUM(IF [Region] = "West" THEN [Amount] END) }`
> - Calc type: LOD (FIXED)
> - Verification: VERIFIED
> - Drift caveats: none
> - Manual follow-ups: drop the `T:` prefix once you approve final placement
> - Handoff outcome: declined; shipped as-is
>
> Translate another expression?

**What the skill prevented:**

- Row-level routing (mixed-aggregation error)
- Missing dimensional filter context
- Silent verification (would have shipped without a get-summary-data check)
- Double-qualification if the source expression had referenced `[Parameters].[Region]` instead of a literal
- Name overflow if the source calc name had been `West Region Sales Aggregate`

***

## Workflow

### Phase 0 — Intake and Setup

**Batching:** issue list-workbook-datasources and list-available-fields in one turn.

1. Ask the tester:
   - Source dialect: SQL (which vendor), Excel, or DAX?
   - Paste the expression (single expression only).
   - Target data source in the workbook (if multiple exist).
2. Confirm the target: `list-workbook-datasources`. If multiple, ask which. If one, auto-select.
3. Check for parameter-referencing calcs on the target data source (scan formulas from `list-available-fields` for `[Parameters].` references). If present, enter parameter-safe mode (see Hard Constraint 2).
4. Call `get-workbook-inventory` alongside `list-available-fields` to check for a prior `T:`-prefixed calc from an earlier session before assuming the field list alone is sufficient for collision-checking in Phase 3.
5. If the testers stated dialect/vendor isnt one of the covered SQL vendors, Excel, or DAX, ask which vendor it is; if a function has no Translation Rules entry, follow the Source-side function has no Translation Rules entry row in Error Handling rather than guessing.

### Phase 1 — Parse and Route

1. Parse the source expression to identify:
   - Referenced fields (map to Tableau via `list-available-fields`)
   - Referenced parameters (flag for manual creation guidance)
   - Functions used (map via Translation Rules below)
   - Aggregation patterns (SUM, COUNT, DISTINCT, window functions)
   - Filter modifiers (WHERE, DAX CALCULATE modifiers, Excel IF wrappers)

2. Route to a Tableau calc type using the Calc-Type Routing table:
   - Row-level source function → Tableau row-level calc
   - Source aggregation without dimensional context → Tableau aggregate calc
   - Source aggregation with dimensional filter or partition context → Tableau LOD
   - Source window function → Tableau table calc
   - Source lookup across tables → flag as relationship, not calc; refuse translation

3. Announce the route to the tester with the reasoning (This is an LOD because the source uses a dimensional filter modifier). Give them a chance to override.

### Phase 2 — Resolve Fields

**Batching:** issue all resolve-field calls in one turn.

1. For every field named in the source expression, call `resolve-field`. If any field is unresolvable, stop and ask the tester to provide a mapping or add the missing field.

2. If a source parameter is referenced, do not attempt author-parameter. Generate a manual-creation instruction block for the tester and continue Phase 2 assuming the parameter will exist by verification time.

### Phase 3 — Translate and Write

1. Assemble the Tableau expression using the Function Mappings and the routed calc type.
2. Apply the 20-character name cap. Propose a name; confirm with the tester.
3. Place translation-note comments at the end of the formula (never the beginning).
4. **Pre-write validation gate (mandatory).** Before calling author-calc, read the drafted formula string back and confirm all four checks pass:
   - **No parameter double-qualification:** the string contains zero occurrences of `[Parameters].`. If found, strip to bare parameter name and re-check.
   - **Name length:** the proposed name is ≤ 20 characters. If over, stop and propose a shorter name.
   - **Comment position:** any translation comment appears after the final formula token (never before or interleaved). If comments are misplaced, move them to the end.
   - **No collision:** `T: {name}` does not already exist in list-available-fields output. If it does, increment to `T: {name} v2`.

   If any check fails and cannot be auto-corrected, stop and surface the specific failure to the tester. Never call author-calc while a check is failing — the writes are hard to reverse (no delete-calc tool).

5. Call `author-calc` with:
   - Name: `T: {shortened-name}`
   - Formula: translated expression, comments at end
   - Data source: confirmed target
6. Confirm the calc appears in `list-available-fields`. If not, the write failed silently — check for a blocking modal.

### Phase 4 — Verify

1. Create a scratch worksheet with a distinct name (e.g., `T-Verify-{timestamp}`). No delete-sheet or delete-calc tool path exists, so the scratch sheet and the authored calc persist. Tell the tester up front, naming the sheet, so they can remove it manually.
2. Place the translated calc via `add-field`. A row-level calc can go on Detail. An LOD calc can't go on Detail as-is: put the grouping dimension on Rows and the calc on Text as `SUM(...)` (or `ATTR(...)`). Add companion fields the verification needs. Run this step right after `author-calc`; don't wait for the user to ask.
3. Call `get-summary-data`. Compare against:
   - The testers expected value if provided
   - A hand-calculated value if the expression is simple enough to compute manually
   - The source systems output if the tester can paste it
4. Log the verification result: **VERIFIED**, **DRIFT** (plausible but different; report delta), or **UNVERIFIED**.
5. If drift is detected, cross-reference the Semantic Drift Catalog. Include the caveat text verbatim in output.
6. If the target data source returns fewer than ~5 rows, note in the delivery summary that verification confidence is lower — a small sample can mask a DRIFT that would only appear at scale.

### Phase 5 — Calc Optimizer Handoff (optional)

After VERIFIED, offer the handoff:

> Translation is verified. This is a {row-level / aggregate / LOD / table calc}. Want me to hand off to {calc-optimizer} for performance optimization and a deeper verification pass? (yes/no)

Route based on calc type:
- Any calc type (row-level, aggregate, LOD, or table calc) → `calc-optimizer`

**On yes:**
1. Invoke the sibling skill via the `Skill` tool, passing the translated calc name, the source-dialect context, and any drift caveats as input.
2. The sibling skill returns an optimized version (or confirms the translation is already optimal) plus a deeper verification report.
3. Confirm the tester wants to apply any sibling-proposed changes; if yes, the sibling handles the write. If no, the original translation stands.

**On no:** close the run cleanly. Log in the delivery summary: Handoff declined; translation shipped as-is.

Handoff is never forced. Declining is a valid completion state.

### Phase 6 — Deliver

Summarize in chat:
- Source expression (verbatim)
- Target Tableau calc name and formula
- Calc type chosen and why
- Verification status (VERIFIED / DRIFT / UNVERIFIED)
- Semantic-drift caveats if applicable
- Manual follow-ups (parameter creation, join setup, T: prefix cleanup)
- Handoff outcome (accepted / declined / not offered)

Offer to write a translation report to the testers Downloads folder if the translation was non-trivial. Offer to translate additional expressions one at a time.

***

## Error Handling

| Failure | Recovery |
|---------|----------|
| Source expression is not parseable | Ask the tester to confirm the full expression. Do not guess at missing pieces. |
| Source-side field has no Tableau counterpart | Stop. Ask the tester to map the field or add it. Do not fabricate. |
| `resolve-field` returns an ambiguous multi-match (same field name across tables/datasources) | Stop. List the candidates and ask the tester which one the source expression means. Do not guess based on position or first-match. |
| Source-side function has no Translation Rules entry | Report the gap plainly. Offer the closest analog with a strong drift caveat. |
| author-calc succeeds but the calc does not appear in list-available-fields | Check for a Desktop modal. If none, retry once. If the second attempt fails, log UNVERIFIED and hand off. |
| Scratch worksheet creation fails | Ask the tester to close open modals and retry. If still failing, log UNVERIFIED with manual-verification instructions. |
| get-summary-data returns an unexpected null | Check whether the sources null-handling differs from Tableaus. Cross-reference the Semantic Drift Catalog. |
| Cloud data source verification times out | Retry once. On a second timeout, log UNVERIFIED. |
| Verification returns a value that differs from the testers expected | Do not overwrite the calc. Report DRIFT with the delta. Offer to reformulate. |
| The 20-character name cap forces a rename that collides with an existing calc | Increment the suffix (`T: X` → `T: X v2`). Never overwrite. |
| Target data source contains parameter-referencing calcs | Enter parameter-safe mode. Use add-worksheet plus add-field for verification. |
| `author-calc` fails to resolve a freshly-created parameter by bare name, even after `resolve-field` confirms it exists live | This is a platform-level reliability gap in newly-created parameter resolution, not a formula error. Retry the write once after asking the tester to reselect/refresh the Data pane in Desktop. If it still fails, log UNVERIFIED and give the tester manual instructions to create the calc themselves in Desktop referencing the parameter directly. |
| Fix would require changing the source expression | Refuse. Hand off to the tester. |
| Calc Optimizer skill is unavailable | Skip the handoff offer. Log in the delivery summary that the sibling was not invocable this session; ship as-is. |
| Tester accepts handoff but the sibling refuses or errors | Log the siblings refusal reason in the delivery summary. Translation stands. Do not retry the sibling. |
| Tester abandons the intake mid-flow | Save the parsed source expression and translated draft (if any) as a partial. Ask if they want to resume or discard. |

***

## Composability

- **Upstream:** offered proactively after `data-source-connector` completes on a data source that is a known migration target (e.g., a Snowflake DS just connected while porting a Power BI dashboard).
- **Peer:** hands off to `calc-writer` when the tester wants a new calc from natural language instead of translation.
- **Peer:** hands off to `calc-debugger` when the tester wants to debug an existing Tableau calc.
- **Peer:** hands off to `join-and-relationship-advisor` when the source is actually a lookup (VLOOKUP, DAX RELATED) that requires a relationship, not a calc.
- **Downstream (optional, always offered):** hands off to `calc-optimizer` (any calc type) for performance optimization and deeper verification. Handoff is per-run tester approval, never automatic.
- **Adjacent:** output is consumable by `data-scribe` (translated calcs appear in the dictionary) and `workbook-auditor` (the translation event registers as a diff).

***

### Function Mappings — SQL → Tableau (top 20)

| SQL | Tableau | Notes |
|---|---|---|
| DATEADD(part, n, date) | DATEADD(part, n, date) | Argument order same; part becomes a quoted string |
| DATEDIFF(part, start, end) | DATEDIFF(part, start, end) | Signed value differs on certain boundaries — verify |
| DATE_TRUNC(part, date) | DATETRUNC(part, date) | Direct mapping |
| EXTRACT(part FROM date) | DATEPART(part, date) | Direct mapping |
| CASE WHEN x THEN y ELSE z END | IF x THEN y ELSE z END | Direct |
| COALESCE(a, b) | IFNULL(a, b) | Two-arg; nest IFNULL for 3+ |
| NULLIF(a, b) | IIF(a = b, NULL, a) | No direct Tableau NULLIF |
| LEFT(str, n) / RIGHT(str, n) | LEFT(str, n) / RIGHT(str, n) | Direct |
| SUBSTRING(str, start, len) | MID(str, start, len) | Function name differs |
| CONCAT(a, b) | a + b | Tableau uses + operator |
| REGEXP_REPLACE(str, pat, rep) | REGEXP_REPLACE(str, pat, rep) | No-ops silently on CSV/Hyper — verify DS type |
| ROW_NUMBER() OVER (PARTITION BY x ORDER BY y) | INDEX() with partitioning | Route to table calc |
| RANK() OVER (...) | RANK() as table calc | Route to table calc |
| SUM(x) OVER (PARTITION BY y) | { FIXED [y] : SUM([x]) } | Route to LOD |
| ROUND(x, n) | ROUND(x, n) | Bankers rounding in Tableau |
| CAST(x AS type) | INT/FLOAT/STR/DATE(x) | Different syntax |
| LEN(str) / LENGTH(str) | LEN(str) | Direct |
| UPPER(str) / LOWER(str) | UPPER(str) / LOWER(str) | Direct |
| TRIM(str) | TRIM(str) | Direct |
| ISNULL(x) | ISNULL(x) | Direct |

### Function Mappings — Excel → Tableau (top 15)

| Excel | Tableau | Notes |
|---|---|---|
| IF(cond, a, b) | IF cond THEN a ELSE b END | Direct |
| IFS(c1, v1, c2, v2, ...) | Nested IF | No direct IFS |
| IFERROR(expr, fallback) | IFNULL(expr, fallback) | **Drift:** IFERROR catches all errors; IFNULL only nulls |
| ISBLANK(x) | ISNULL(x) OR LEN(TRIM(x)) = 0 | **Drift:** blank ≠ null in Excel |
| TEXT(x, format) | STR(x) + field formatting | No inline formatting in Tableau expressions |
| CONCATENATE(a, b) | a + b | + operator |
| LEFT / RIGHT / MID | LEFT / RIGHT / MID | Direct |
| DATE(y, m, d) | MAKEDATE(y, m, d) | Function name differs |
| SUMIF(range, cond, sum_range) | { FIXED : SUM(IF cond THEN sum_range END) } | Route to LOD. Whole-range SUMIF is table-scoped; add a FIXED dimension only if the source sums per group. |
| COUNTIF(range, cond) | { FIXED : COUNT(IF cond THEN 1 END) } | Route to LOD (table-scoped, as SUMIF) |
| AVERAGEIF | { FIXED : AVG(IF cond THEN val END) } | Route to LOD (table-scoped, as SUMIF) |
| ROUND(x, n) | ROUND(x, n) | Bankers rounding in Tableau |
| ABS(x) | ABS(x) | Direct |
| VLOOKUP / HLOOKUP / XLOOKUP | Not a calc — flag as relationship | **REFUSE, hand off** |
| INDEX-MATCH | Not a calc — flag as relationship | **REFUSE, hand off** |

### Function Mappings — DAX → Tableau (top 15)

| DAX | Tableau | Notes |
|---|---|---|
| CALCULATE(expr, filter) | { FIXED [dim] : expr } with IF filter | Route to LOD; drift on context transition |
| SUMX(table, expr) | { FIXED [dim] : SUM(expr) } | Route to LOD |
| AVERAGEX / COUNTX | { FIXED [dim] : AVG/COUNT(expr) } | Route to LOD |
| FILTER(table, cond) | Not directly translatable | Route to LOD with IF wrapper |
| ALL(column) | { FIXED : SUM(expr) } | **Drift** on partial-scope ALL |
| RELATED(column) | Not a calc — flag as relationship | **REFUSE, hand off** |
| EARLIER(column) | Not directly translatable | **Reformulate as LOD; strong drift caveat** |
| RANKX | RANK() as table calc | Route to table calc |
| SAMEPERIODLASTYEAR | LOOKUP(SUM([Sales]), -12) or DATEADD-based | Route to table calc or LOD per grain |
| DATESYTD / TOTALYTD | RUNNING_SUM() with year partition | Route to table calc |
| DIVIDE(a, b, alt) | IIF(b = 0, alt, a / b) | No Tableau DIVIDE; explicit zero check |
| VAR t = ADDCOLUMNS(VALUES(key), "@m", CALCULATE(agg)) | { FIXED [key] : agg } | Route to LOD; Tableau has no table variables, the FIXED LOD stands in for the per-key table |
| COUNTROWS(FILTER(t, [@m] >= n)) | COUNTD(IF { FIXED [key] : agg } >= n THEN [key] END) | Counts keys, not rows; **Drift:** FIXED ignores dimension and date filters (see Semantic Drift Catalog #6) |
| COUNTROWS(t) over VALUES(key) | COUNTD([key]) | Direct |
| BLANK() | NULL | Direct |
| ISBLANK(x) | ISNULL(x) | Direct |
| NOT | NOT | Direct |
| SWITCH(expr, v1, r1, ...) | CASE expr WHEN v1 THEN r1 ... END | Direct |

### Calc-Type Routing (deterministic)

| Source pattern | Tableau calc type |
|---|---|
| Row-level function (LEN, LEFT, IIF, DATEADD without aggregation context) | Row-level calc |
| Aggregation with no dimensional context (SUM, AVG, COUNT) | Aggregate calc |
| Aggregation with dimensional filter/partition (CALCULATE with FILTER, SQL PARTITION BY, Excel SUMIF) | LOD (FIXED / INCLUDE / EXCLUDE per pattern) |
| Window function (ROW_NUMBER, RANK, LAG, LEAD, RANKX) | Table calc |
| Cross-table lookup (VLOOKUP, DAX RELATED, INDEX-MATCH) | Not a calc — relationship |

### Semantic Drift Catalog (top 6)

1. **SQL integer division vs. Tableau float division.** SQL `5 / 2` returns 2; Tableau returns 2.5. Caveat text: SQL performed integer division; the Tableau translation uses float division. Wrap in INT() if integer semantics are required.

2. **DAX context transition.** CALCULATE modifies filter context in ways with no exact Tableau equivalent. Caveat text: This DAX expression uses filter context transition, which has no exact Tableau equivalent. The LOD translation approximates the common case; verify against the source system for nested-filter scenarios.

3. **Excel error semantics vs. Tableau nulls.** IFERROR catches `#N/A`, `#DIV/0!`, `#VALUE!`, etc.; IFNULL catches only nulls. Caveat text: IFERROR catches all Excel error types; the Tableau IFNULL translation catches only null. If the source column contains non-null errors, add explicit type checks.

4. **Timezone handling.** SQL date functions may include timezone offsets Tableaus DATE type does not preserve. Caveat text: Timezone information may be lost in translation. If source data is UTC or timezone-aware, verify Tableaus DATE type behavior on your data.

5. **Rounding modes.** SQL and Excel typically use away-from-zero rounding; Tableau uses bankers (round-half-to-even). Caveat text: Tableaus ROUND uses bankers rounding (0.5 rounds to nearest even integer). Source SQL/Excel typically uses away-from-zero rounding. For financial or regulatory calculations, verify.

6. **FIXED LOD ignores dimension and date filters.** DAX evaluates variables and iterators under every filter on the page; a Tableau FIXED LOD ignores regular dimension and date filters. Caveat text: DAX respects every filter on the page, but a FIXED LOD in Tableau ignores regular dimension and date filters. If you filter to 2023, a customer's order count still spans all years, so a customer with one order in 2023 and one in 2021 counts as repeat in Tableau but not in DAX. To match DAX, right-click each filter and choose Add to Context (manual Desktop step; no tool sets context filters). INCLUDE is usually a poor substitute because it returns a per-view-level value and cannot be nested inside COUNTD(IF ... THEN key END) without mixing aggregate and row-level fields. State this caveat in Phase 4 and Phase 6 whenever a DAX or SQL translation routes to a FIXED LOD.

## Graceful Degradation

These rules apply whenever something this skill needs is missing or fails. More specific rules elsewhere in this file take precedence.

- **Nothing to work on.** If no workbook is open, there is no data source, or the named calc, sheet, dashboard, or data source isn't found, stop before any other step. Say what you found (list the real names, if any) and ask the user to open the workbook or pick one. Never work on a guessed or closest-match target.
- **Tool call fails, times out, or returns empty.** Retry once, then stop retrying. Mark everything that depended on that call as not checked, continue with what you still can, and say which step failed. If the failed call was a write, stop and report the workbook's current state instead of continuing.
- **Partial results.** If any check, sheet, field, or data source wasn't evaluated, the summary says so (Partial: N of M checked; not checked: [list]). Never give a clean, ready, or PASS verdict on a partial run.
- **Reference file won't open.** Use the rules summarized in this file, say [file] unavailable; using the built-in summary, and never make up thresholds, rule IDs, or Desktop menu steps from memory.
- **Peer skill not installed.** If this skill would hand off to another skill that isn't available, say so and give the manual Desktop step instead. A handoff is never the only next step.
- **Platform gap.** If no tool can do something, say so plainly and give the manual Desktop path.
- **Failure messages.** Tell the user in plain language what was done, what wasn't, and the next step. No raw errors, stack traces, or JSON.
- **No fabrication.** Never invent fields, values, findings, or results to fill a gap left by a failed read.
