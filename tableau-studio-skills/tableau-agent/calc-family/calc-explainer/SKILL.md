---
name: calc-explainer
description: "Use when the user says 'Explain this calc', 'what does [calc name] do?', 'walk me through this calculated field', 'why is this calc built this way?' Explains one calculated field in plain language: what it computes, why it's built that way, and how it behaves. Read-only."
---


# Calc Explainer

## When to use (full trigger detail)

Explain a specific Tableau calculated field in plain language. Given a calc name from an open workbook, produces a four-dimension explanation. what it computes (plain language), why it is structured that way (technical rationale), how it fits in the calc family (reference-graph position from calc-documenter handoff if available, or re-derived locally), and what to expect at runtime (row-level vs aggregate behavior, LOD grain, table-calc addressing gotchas). Read-only. Trigger with explain this calc, what does {calc name} do, explain {calc name} in plain English, calc-explainer, walk me through this calculated field, why is this calc structured this way. Do NOT trigger on. bulk documentation of every calc (defer to calc-documenter), calc syntax debugging or NULL diagnosis (defer to calc-debugger), calc naming or hygiene audit (defer to calc-linter), calc optimization or performance rewrites (defer to calc-optimizer), writing or authoring new calcs (defer to calc-writer), applying changes to calc formulas (this skill is read-only), format-string drift on caption fonts (defer to format-drift-scanner).

## Purpose

Explain a single Tableau calculated field in plain language to the workbook author. Four locked dimensions per explanation: what the calc computes (author-facing prose), why it is structured that way (technical rationale citing patterns from `skill-expertise/explanation_patterns.md`), how it fits in the calc family (reference-graph position with parents and children named), and what to expect at runtime (row-level vs aggregate behavior, LOD grain implications, table-calc addressing notes). Read-only. Every explanation cites the formula substring or reference-graph entry that grounds it; no fabrication.

Positioned downstream of calc-documenter in the calc-family pipeline. If `calc_documentation/1` handoff is available in session context, calc-explainer consumes it. Otherwise, calc-explainer re-derives the same signals locally per HC#12.

## Trigger Conditions

- explain this calc
- what does {calc name} do
- explain {calc name} in plain English
- calc-explainer
- walk me through this calculated field
- why is this calc structured this way
- how does {calc name} work
- whats this formula doing

## Do NOT Trigger On

- Bulk documentation of every calc in the workbook (defer to `calc-documenter`).
- Calc syntax debugging or NULL diagnosis (defer to `calc-debugger`).
- Calc naming or hygiene audit (defer to `calc-linter`).
- Calc optimization or performance rewrites (defer to `calc-optimizer`).
- Writing or authoring new calcs (defer to `calc-writer`).
- Applying changes to calc formulas (all fixes are Desktop-manual per HC#1).
- Format-string drift on caption fonts (defer to `format-drift-scanner`).
- Data-quality issues (defer to `data-quality-review`).
- Performance analysis (defer to `calc-optimizer`).

## Scope Boundaries

- **IN.** One calc per run. Name-based lookup from an open workbook via `list-available-fields` + `resolve-field`. Four-dimension explanation. Opportunistic consumption of `calc_documentation/1` handoff when available in session context. Cross-datasource references named but not fully resolved. Read-only. Handoff schema `calc_explanation/1`.
- **OUT.** Any workbook mutation. Bulk-workbook explanation (route to calc-documenter). Calc rewriting or optimization. Explaining a calc that doesnt exist in an open workbook (user must open the workbook or provide the name of a calc that resolves).

**Multi-datasource workbooks.** If the calc name is ambiguous across datasources (same name in two datasources), skill asks one clarifying question (Explain Profit Ratio from Orders or from Returns?) before proceeding.

**Handoff consumption pattern.** If `calc_documentation/1` handoff is in session context AND references the target calc, calc-explainer uses the handoffs reference-graph and aggregation classification. Otherwise, skill re-derives the same signals locally via `list-available-fields`, `resolve-field`, and formula pattern-matching. Report includes `handoff_consumed: true|false` for transparency.

## The 4-Dimension Explanation Model

Every explanation includes these four dimensions in this order:

| # | Dimension | What it answers | Grounded in |
|---|---|---|---|
| 1 | **What it computes** | Plain-language description of the output | Formula verbatim, cited substring per operation |
| 2 | **Why it is structured this way** | Technical rationale for the specific pattern used | Pattern from `explanation_patterns.md` (e.g., SUM-of-ratios pattern for correct aggregation) |
| 3 | **How it fits in the calc family** | Parents (uses), children (used by), and context | Reference graph from handoff or re-derived locally |
| 4 | **What to expect at runtime** | Row-level vs aggregate behavior, LOD grain, table-calc gotchas | Aggregation classification from `calc-documenter`s patterns |

**Explanation length.** Target 3-5 sentences per dimension. Total explanation under 25 lines. No preamble, no meta-commentary, no marketing.

## Workflow Phases

- **Phase 0 Scope.** Confirm workbook is open via `get-workbook-inventory`. Ask user for the calc name if not stated. Resolve via `resolve-field`. If ambiguous across datasources, ask one clarifying question.
- **Phase 1 Handoff Check.** Look for `calc_documentation/1` handoff in session context. If present AND references the target calc, use it for Dimension 3 (reference-graph) and Dimension 4 (aggregation classification). Set `handoff_consumed: true`. Otherwise proceed to Phase 2.
- **Phase 2 Local Extract (if no handoff).** Read formula from `list-available-fields`. Parse formula for field references. Resolve each via `resolve-field`. Classify aggregation via `explanation_patterns.md` precedence rules (same six types as calc-documenter). Build local reference graph by scanning other calcs in the same datasource for references to this calc (used-by list).
- **Phase 3 Compose Explanation.** For each of the four dimensions, generate 3-5 sentences grounded in the extracted signals. Cite formula substrings, referenced calcs, and pattern names.
- **Phase 4 Validate.** Run the 4-check V-gate: dimension coverage, formula citation, handoff-or-local-source labeled, no fabricated references.
- **Phase 5 Deliver.** Compact single-tier chat output. Optional handoff to calc-debugger if user asks about NULL behavior, or to calc-optimizer if user asks about performance.

## Hard Constraints

**HC#1 Read-only always.** Never invoke `author-calc`, `bind-template`, `build-and-apply-worksheet`, or any mutating tool. Explanation is emitted; nothing is written back to the workbook.

**HC#2 One calc per run.** Multi-calc explanations refused; route to `calc-documenter` for bulk. User invokes calc-explainer separately per calc.

**HC#3 Bulk-action refusal.** Explain every calc in my workbook refused; skill is one-calc-per-run. Route to calc-documenter.

**HC#4 Locked four-dimension model.** Every explanation includes all four dimensions in order. No dimension omitted. No fabricated dimension added. If a dimension cannot be populated (e.g., calc has zero references so Dimension 3 has empty parents/children), render the empty state explicitly (No parents; no children) rather than skipping the dimension.

**HC#5 Ground every claim.** Every sentence in the explanation cites either a formula substring, a referenced calc name, or a pattern name from `explanation_patterns.md`. No unsupported generalizations. No this calc probably... language.

**HC#6 Never auto-invoke another skill.** Adjacent-skill routing (calc-debugger for NULLs, calc-optimizer for performance) is an opt-in handoff.

**HC#7 Sentinel discipline.** Use `null` and empty-state prose (No parents; no children) for absent references. Never blank a dimension.

**HC#8 Refuse to fabricate.** V-gate refuses explanations that cite formula substrings not present in the actual formula, or reference calcs not present in the workbook.

**HC#9 Partial-info handling.** If the calcs formula references a field that `resolve-field` cannot locate (deleted, renamed), render as `unresolved: <raw>` and note the resolution failure in Dimension 3 rather than fabricating.

**HC#10 Adjacent-skill routing.** NULL diagnosis → `calc-debugger`. Performance concerns → `calc-optimizer`. Hygiene audit → `calc-linter`. Bulk explanation → `calc-documenter`. Rewriting → `calc-writer`.

**HC#11 Author caption preserved.** If the calc has an existing author caption, quote it verbatim in Dimension 1 as the authors stated intent. Skills explanation supplements the caption; never rewrites, paraphrases, or contradicts it silently. If the skills technical read conflicts with the author caption, note the conflict transparently.

**HC#12 Handoff-or-local-source labeled.** Every explanation includes `signal_source: handoff | local_extract` in the handoff payload. User can tell which path fired without re-reading the reference-graph section.

**HC#13 Guide the user actively.** If the calc name is ambiguous, ask one clarifying question. If the calc doesnt exist, list the closest matches (top 3 by name similarity) and offer to proceed with one.

**HC#14 Grounded prose ordering locked.** Within each dimension, sentences render in this order: (1) claim, (2) formula-substring or reference-graph citation, (3) implication for the reader. Never rearrange. This is the same anchor-first discipline pattern as viz-critique-pro-studio and calc-documenter.

**HC#15 Handoff staleness detection required.** When consuming a `calc_documentation/1` handoff, the target calcs current formula MUST match the handoffs stored formula (byte-exact after whitespace normalization). Mismatch forces `local_extract` fallback per V5 and is logged in `run_metadata.notes`. Never render a handoff-sourced explanation against a stale formula. Author changes to a calc between the handoff run and the explainer run are the primary reason for this rule.

## Single-Tier Delivery

**Chat output only.** No opt-in file save. Explanation lives in chat.

Template:

```
**Calc Explanation: {calc_name}** ({datasource_name})
Signal source: {handoff | local extract}
{Author caption if present, quoted verbatim, one line}

**What it computes.**
{3-5 sentences. Cite formula substrings.}

**Why it is structured this way.**
{3-5 sentences. Cite pattern name from explanation_patterns.md.}

**How it fits in the calc family.**
Parents (uses): {list or none}
Children (used by): {list or none}
{2-3 sentences of context.}

**What to expect at runtime.**
Type: {row-level | aggregate | LOD-fixed | LOD-include | LOD-exclude | table-calc}
{3-5 sentences. Cite aggregation implications, LOD grain, or table-calc addressing.}

Next: {one-line routing suggestion, or no downstream skill recommended.}
```

**Never rendered.** Improvement recommendations (calc-explainer explains, does not recommend fixes; thats calc-optimizers job). Fabricated context. Marketing prose.

**Ancillary file save.** If user asks to save the explanation, offer `.md` or `.txt` in Downloads via the standard opt-in path-confirmation flow. Not the default path.

## Validation Gate (5-Check Read-Only)

**V1 Dimension Coverage.** All four dimensions rendered in order with 3-5 sentences each (or explicit empty-state prose per HC#4/7).

**V2 Formula Citation.** Every claim in Dimension 1 (What it computes) cites a formula substring or aggregation function name. No unsupported prose.

**V3 Reference Grounding.** Every parent/child name in Dimension 3 exists in the workbook (verified via handoff or `resolve-field`). No fabricated references.

**V4 Handoff-or-Local Labeled.** `signal_source` field populated. If handoff was used, target calc must actually appear in the handoffs `datasources[].calcs[]` list.

**V5 Formula-Hash Cross-Check (handoff mode only).** When `signal_source: handoff`, hash the target calcs current formula from `list-available-fields` and compare against the handoffs stored formula for the same calc. If the hashes mismatch, the handoff is stale (calc changed since the handoff was generated). Force fallback to `signal_source: local_extract`, log the drift in `run_metadata.notes` (handoff formula-hash mismatch; fell back to local extract), and re-derive Dimensions 3 and 4 locally. Never render a handoff-sourced explanation against a stale formula.

V-gate failure on V1-V4 blocks delivery per HC#8. V5 does not block delivery; it forces the local_extract fallback and continues.

## Tool Sequence

- **Phase 0.** `get-workbook-inventory` (never twice per run). `list-available-fields` for calc lookup. `resolve-field` on the target calc name.
- **Phase 1.** In-memory handoff check. No tool calls.
- **Phase 2 (if no handoff).** `list-available-fields` on the target datasource for the calcs formula. `resolve-field` per formula reference (batched, 20 per parallel call). For used-by construction: iterate through other calcs in the same datasource and pattern-match for references to the target calc.
- **Phase 3-4.** In-memory composition and validation. No tool calls.
- **Phase 5.** Chat delivery. No tool calls unless the user asks to save the explanation.

**Batching rules.** `resolve-field` batches capped at 20 per parallel call (matches calc-documenter HC#5). Never call `get-workbook-inventory` or `list-available-fields` twice per run.

**Early-exit condition.** If the calc name doesnt resolve after user disambiguation, exit gracefully with Calc {name} not found in the open workbook. Closest matches: {top 3}. Which one?

## Handoff Contract

Emits `calc_explanation/1` per `skill-expertise/handoff_schema.md`. Consumed by:

- **calc-debugger.** Consumes when user routes to NULL diagnosis on the same calc.
- **calc-optimizer.** Consumes when user routes to performance analysis on the same calc.
- **workbook-auditor.** Consumes when tracking explanation deltas across runs (calc changed, explanation shifted).

## Known Limitations

- **No cross-datasource full resolution.** If the calc references a field in another datasource that isnt loaded, Dimension 3 lists the reference as `cross_datasource: {ds_name}.{field_name}` without traversing it.
- **Table-calc addressing.** Skill notes that table calcs have partition/addressing configured on the worksheet, not in the calc XML. Dimension 4 describes the pattern (WINDOW_SUM, RUNNING_SUM, etc.) but does not specify the addressing per worksheet.
- **Author caption conflicts.** If the author caption conflicts with the skills technical read (e.g., caption says returns average but formula is SUM), HC#11 requires transparent flagging. Skill does not decide who is right.
- **`list-available-fields` reliability gap**. If it returns partial results, skill exits with an explicit failure rather than fabricating an explanation.
- **Set / parameter references.** Explained as field references without enumerating set membership or parameter value list.

## Error Handling

| Failure | Response |
|---|---|
| Workbook not open | Ask: Please open the workbook containing the calc youd like explained. |
| Calc name not stated | Ask: Which calc would you like explained? Provide the name from your workbook. |
| Calc name doesnt resolve | List top 3 closest name matches, offer to proceed with one, or exit if user declines. |
| Calc name ambiguous across datasources | Ask one clarifying question with datasource names. |
| `get-workbook-inventory` fails | Retry once. If still failing, exit gracefully. |
| `list-available-fields` returns partial | Exit with explicit failure per Known Limitations; do not fabricate. |
| `resolve-field` returns no match for a formula reference | Render as `unresolved: <raw>` in Dimension 3 per HC#9. |
| Handoff exists but doesnt reference the target calc | Fall back to local extract per HC#12. Note in `signal_source: local_extract`. |
| User asks to explain multiple calcs | Refuse per HC#2. Route to calc-documenter for bulk. |
| User asks to fix or rewrite the calc | Refuse per HC#1 and HC#10. Route to calc-writer or calc-optimizer. |
| User asks to skip a dimension | Refuse per HC#4. Four-dimension model is locked. |
| User asks for performance analysis of the calc | Refuse per HC#10. Route to calc-optimizer with the explanation payload. |
| User asks about NULL behavior of the calc | Offer to route to calc-debugger; do not diagnose here. |

## Examples

**Example 1: Aggregate calc with handoff.**

User (workbook open with calc_documentation/1 in session): explain Profit Ratio

Skill runs Phase 0 (resolve), Phase 1 (handoff hit), skips Phase 2, composes:

```
**Calc Explanation: Profit Ratio** (Orders)
Signal source: handoff
Author caption: Overall profit margin, aggregate not row-level.

**What it computes.**
Profit Ratio returns the ratio of total profit to total sales, aggregated to whatever grain the worksheet is displaying. Formula: `SUM([Profit]) / SUM([Sales])`. The numerator sums profit across the current row context; the denominator sums sales across the same context.

**Why it is structured this way.**
SUM-of-ratios avoids the average-of-averages pitfall (Pattern: agg-first-then-divide). If the calc were `AVG([Profit] / [Sales])`, each rows ratio would be averaged, which is arithmetically wrong for a portfolio-level margin. The SUM-then-divide pattern respects the underlying dollars.

**How it fits in the calc family.**
Parents (uses): [Profit], [Sales]
Children (used by): Regional Profit YoY, Discount Impact Score, Top 10 Profit Filter
Profit Ratio is a mid-level utility calc; two of its three children are dashboard-facing.

**What to expect at runtime.**
Type: aggregate
Aggregate calcs cannot be placed on Detail; must go on a shelf with a partition context (e.g., Region on Rows). If you try to filter by Profit Ratio directly at the row level, Tableau will refuse and offer to aggregate first. LOD grain matters: this calc respects the shelf-defined grain.

Next: If you need to diagnose why Profit Ratio returns NULL for a specific segment, route to calc-debugger.
```

**Example 2: Row-level calc, no handoff.**

User (workbook open, no prior calc-documenter run): explain Discount Impact

Skill runs Phase 0 + Phase 2 (local extract) + Phases 3-4. Renders same 4-dimension shape with `signal_source: local_extract`.

**Example 3: Ambiguous calc name.**

User: explain Growth Rate

Skill: Growth Rate appears in two datasources: Orders and Returns. Which one?

User: Orders

Skill proceeds normally with `datasource: Orders`.

**Example 4: Calc doesnt exist.**

User: explain Return Rate

Skill: No calc named Return Rate in the open workbook. Closest matches: Return Ratio (Returns), Rate of Return (Orders), Return Percentage (Orders). Which one, or should I exit?

## Relationship to Other Skills

- **Downstream of calc-documenter.** Consumes `calc_documentation/1` handoff when available for reference-graph and aggregation context.
- **Peer to calc-debugger.** Explainer describes what the calc does; debugger diagnoses why it isnt doing it. NULL diagnosis routes to debugger.
- **Peer to calc-optimizer.** Explainer describes the pattern; optimizer proposes a faster equivalent. Performance concerns route to optimizer.
- **Upstream of workbook-auditor.** Auditor consumes explanation deltas across runs for change tracking.

## MCP Skill Mapping

Desktop-native. No MCP dependency. Uses standard Desktop tools (`get-workbook-inventory`, `list-available-fields`, `resolve-field`).

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
