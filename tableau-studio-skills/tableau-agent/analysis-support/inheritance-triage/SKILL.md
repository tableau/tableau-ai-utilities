---
name: inheritance-triage
description: "Use when the user says 'I inherited this workbook', 'where do I start?', 'orient me', 'which sheets are hardest?' Gives a short orientation on an inherited workbook (key dashboards, data sources, calc complexity, where to start) or ranks every sheet 1-10 by complexity. Read-only."
---

# Tableau Inheritance Triage

Orient an author who just opened an unfamiliar workbook. Deliberately-shallow entry point to the exhaustive-documentation skills. Produces a one-page orientation summary and a per-worksheet complexity ranking.

## When to use (full trigger detail)

Orient an author who just inherited a Tableau workbook. Two modes. Orient mode produces a deliberately-shallow one-page summary (headline, primary dashboards, data sources, calc complexity tiers, sheet complexity top-10, where to start reading). Complexity-score mode ranks every worksheet 1-10 against a locked 6-factor rubric (C1 mark count, C2 calc nesting, C3 table-calc, C4 LOD, C5 filter count, C6 cross-DS). Routes to data-scribe, calc-documenter, workbook-summary-onepager, workbook-auditor as optional handoffs with manual fallbacks. Read-only. Trigger on "I inherited this", "orient me", "where do I start", "triage this workbook", "5-minute summary", "rank these sheets by complexity", "which sheets are hardest". Do NOT trigger for. exhaustive metric dictionary (data-scribe), exhaustive calc catalog (calc-documenter), stakeholder onepager (workbook-summary-onepager), change tracking (workbook-auditor), authoring in Desktop.

## Reference files

- **`skill-expertise/complexity-rubric.md`.** The locked C1-C6 complexity rubric with per-factor evidence signals, scoring rules, and tier boundaries.
- **`skill-expertise/triage-output-template.md`.** The one-page Orient-mode template with word-count caps per section.

## When to use

Author just opened a workbook built by someone else (consultant, departed colleague, previous self) and wants a 5-minute orientation plus a prioritization hint for which worksheets to tackle first.

## Hard Constraints

- **HC-1 Read-only.** No mutation.
- **HC-2 Orient-mode output capped at 500 words / one page.** Deliberately-shallow is the point.
- **HC-3 Honest "this workbook is simple, no triage needed" verdict.** For workbooks under 5 sheets and 10 calcs, emit a 2-sentence summary and skip the full orientation.
- **HC-4 Locked C1-C6 complexity rubric.** No ad-hoc factors.
- **HC-5 Routes to exhaustive skills optional.** Data-scribe, calc-documenter, workbook-summary-onepager, workbook-auditor all offered as handoffs with manual fallbacks.
- **HC-6 Never fabricate changelog data.** If `get-workbook-inventory` modified-date is absent, say so.
- **HC-7 Standalone-safe.**
- **HC-8 Complexity score is a prioritization aid, not a quality judgment.** A score-10 sheet is not "bad," just complex. The output never calls complex sheets wrong.
- **HC-9 No pasted URLs to community resources.**

## Workflow

**Tools used.** `list-dashboards` (to enumerate dashboards for Orient-mode Section 2), `list-worksheets` (to enumerate every worksheet for C1-C6 scoring; load-bearing read for scope), `list-available-fields` (to resolve the data-source origin per field for C6 cross-DS check, and to pull calc text for C2 nesting-depth parsing and C4 LOD-pattern detection), `get-workbook-inventory` (to pull last-modified-date for the headline; HC-6 degrade path if unavailable), `get-worksheet-xml` (to extract per-sheet shelf-level signatures: Rows pills, Columns pills, Marks card, filters-shelf field count for C5, table-calc delta glyphs for C3, pill-count density proxy for C1; the load-bearing read for all per-sheet scoring). Note: `get-dashboard-xml` returns zone layout only, not shelf-level data, and cannot be used for C1-C6 scoring.

Steps:

1. Call `list-dashboards`, `list-worksheets`, `list-available-fields`, `get-workbook-inventory`.
2. If workbook has fewer than 5 sheets AND fewer than 10 calcs, emit the HC-3 short-circuit summary and stop.
3. Otherwise:
   - Build the headline (what this workbook is, modified-date if available).
   - Enumerate primary dashboards (3-5) with 1-sentence "answers X" phrases.
   - Count data sources and name each.
   - Tier calcs by complexity (simple / LOD-heavy / nested).
   - Call `get-worksheet-xml` on each worksheet and score against C1-C6. Surface the top-10.
   - Compose the "where to start reading" recommendation.
   - Flag any known issues workbook-auditor would catch (default sheet names, orphan sheets, hidden sheets).
4. Emit the Orient-mode output template.
5. If the author triggered Complexity-score mode directly, skip the orient summary and emit only the ranked worksheet list.

## Error Handling

Every recovery path below delivers partial value, never a bare refusal. Name the failure plainly, deliver what the skill can still do, and flag anything downgraded so the author knows the output is incomplete.

| Failure | Cause | Recovery |
|---|---|---|
| No workbook open (`list-dashboards` or `list-worksheets` returns empty or errors) | No workbook open, Studio tool failure, or workbook has zero worksheets | State plainly that no workbook or worksheets were found. Offer to walk through `complexity-rubric.md` and `triage-output-template.md` as reading reference until a workbook is open. Do not fabricate a triage. |
| Workbook has 0 worksheets | Workbook exists but is empty | Short-circuit: "This workbook has 0 worksheets. Nothing to triage yet. Open or build the first sheet to proceed. If you want to understand the triage output format in advance, I can walk you through `triage-output-template.md`." |
| Workbook has fewer than 5 sheets AND fewer than 10 calcs (HC-3 short-circuit) | Small-workbook case | Emit the HC-3 2-sentence summary per the `triage-output-template.md` short-circuit template: "This workbook is small. [N] sheets, [M] calcs, [K] data source(s). No full triage needed. Start with [the one or two dashboards]; everything else is a worksheet feeding them." Skip the 8-section orient output. Do not emit a false "clean, nothing to orient" output on a small-but-valid workbook. |
| `get-workbook-inventory` returns no modified-date | Server did not expose last-modified metadata, or workbook has never been saved | Per HC-6, state plainly: "Modified date not available in the file metadata." Deliver all other orient-mode sections normally. Do not fabricate a date or author. |
| `get-worksheet-xml` fails on one or more sheets | Studio tool error, unsaved sheet, or a dashboard-bound sheet with no standalone XML | Score the sheets that succeeded. For each failed sheet, include it in the ranked list with "unscored (XML did not load)" and skip the C-factor breakdown. State plainly at the top of the output: "[N] of [M] sheets scored. [N-M] could not be scored because shelf XML did not load; re-save those sheets and re-run to include them." Do not fabricate scores. |
| `get-summary-data` not available for C1 mark count | Tool unavailable in this session, or workbook not connected to data | Default C1 to 1 point for every sheet and announce "unverified mark counts (C1 defaulted to 1 point across all sheets)" at the top of the output. Alternatively, offer to self-report: "If you can tell me the approximate mark count per top-10 sheet, I will re-score C1 with real numbers." Deliver the ranking with the degraded C1 regardless. |
| Workbook has 100+ sheets (scalability) | Noisy-output risk; full scoring would exceed useful attention budget | Before scoring, confirm with author: "This workbook has [N] sheets. Options: (1) full scan with top-20 complexity surfaced in orient mode, (2) scope to a single dashboard's contained sheets, (3) scope to sheets scoring 7+ only (defer full ranking), (4) scope to a filename substring. Pick one and I will proceed." Do not scan silently. |
| Author asks "is this workbook good or bad" | HC-8 interpretive-request guard | Per HC-8, do not render a quality judgment. Convert to structural output: "Complexity scores are for prioritization, not quality judgment. A score-10 sheet is often the right design for its question; a score-2 sheet is often a scratch pad. Here is the structural ranking." Deliver the full orient or complexity output. |
| Author asks the skill to delete, hide, or clean up sheets | HC-1 mutation guard | Per HC-1, do not mutate. Convert: "I orient and prioritize; I do not clean up. If `worksheet-cleanup` is installed, hand off there with the orphan-and-empty flags from Section 7. Otherwise, use the issues list to clean up manually in Desktop." Deliver the triage regardless. |
| Author asks for a dashboard-level complexity score | Out of rubric scope | State plainly: "Complexity-score mode scores per-worksheet, not per-dashboard,. A dashboard's complexity rolls up from its contained sheets. If you want a dashboard-level roll-up now, I can emit the top-3 scoring sheets per dashboard as a scoping aid. |
| Author asks to run both modes simultaneously | Scope ambiguity between Orient and Complexity-score | Default to Orient mode first (Section 5 already includes the complexity top-10). Offer Complexity-score mode as a follow-up: "Orient output emitted. Say 'full complexity ranking' and I will emit the full per-sheet C1-C6 breakdown as a follow-up." Do not merge both into one over-cap output. |
| Opt-in file save fails | Filesystem permissions, path collision, disk full, or user cancels | Emit the full orient or complexity output inline in chat regardless of save status. State the save failure plainly with path and error. Never gate the triage output on the save succeeding. Default save location is the user's Downloads folder. |
| Author asks for cross-session persistence of orient output | Out of scope | Save output to Downloads folder (per the opt-in save path) and name the saved file as the reference artifact: "Future-you can re-read this file instead of re-running the triage. If the workbook changes substantially, re-run." Do not promise cross-session memory the skill does not have. |
| Workbook sheets reference deleted or broken fields | Field in XML not resolvable via `list-available-fields` | Score what can be scored on the sheet. Flag the broken reference in Section 7 (Known Issues): "[Sheet name] references [N] deleted or unresolvable field(s); score is partial." Do not refuse to score. |
| Author asks to invent or guess at sheet purposes beyond what the structure shows | HC-8-adjacent interpretive-request | Decline interpretive guessing: "Section 2 'Answers X' phrases are structural (what the chart shows), not interpretive (what the data means). I will not guess at sheet purpose beyond shelf composition. If you can tell me the business context, I will fold it into the headline." Deliver the structural output; offer to re-emit with author-provided context. |

## Modes

**Orient mode (default).** One-page summary. Called by "orient me," "triage this workbook," etc.

**Complexity-score mode.** Per-worksheet C1-C6 ranking only. Called by "rank these sheets by complexity," "which sheets are hardest."

## Complexity rubric summary (full in complexity-rubric.md)

Each worksheet scores 1-10. Sum of C-factor contributions.

- **C1 Mark count.** 0-3 points. 0 if under 100 marks, 1 if 100-500, 2 if 500-5000, 3 if 5000+. Author-reported if `get-summary-data` not run.
- **C2 Calc nesting depth of fields used.** 0-2 points. 0 if no nested calcs, 1 if one level, 2 if two or more levels.
- **C3 Table-calc presence.** 0 or 1 point.
- **C4 LOD presence.** 0, 1, or 2 points. 0 if no LODs, 1 if INCLUDE or EXCLUDE, 2 if FIXED.
- **C5 Filter count.** 0-2 points. 0 if under 3 filters, 1 if 3-5, 2 if 6+.
- **C6 Cross-DS references.** 0 or 2 points. 2 if any field on the sheet references a different data source than the primary one.

**Tier boundaries.**
- 1-3: Simple.
- 4-6: Moderate.
- 7-10: Complex.

## Output format (Orient mode)

Per `skill-expertise/triage-output-template.md`:

1. **Headline.** 1-2 sentences. What this workbook is + last-modified-date.
2. **Primary dashboards.** 3-5 bullets. Each: dashboard name + "answers X" + sheet count.
3. **Data sources.** Count + names.
4. **Calc complexity tiers.** 3 lines: simple count, LOD-heavy count, nested count.
5. **Sheet complexity top-10.** Nested bulleted list, not a markdown table (the chat surface does not render tables): one bullet per sheet with score and tier inline, e.g. "- Sheet Name, score 5, Moderate".
6. **Where to start reading.** 1-2 sentences. "Start with dashboard X, then calc Y."
7. **Known issues flag.** Default sheet names, orphan sheets, hidden sheets.
8. **Optional handoffs.** Line for each: "If you want a full metric dictionary, use data-scribe. If not installed, [manual fallback]."

Word count cap: 500.

## Output format (Complexity-score mode)

1. **All worksheets ranked by score.** Full list, not just top-10. Sort order (per `complexity-rubric.md` Tie-breaking and Edge cases): primary sort by score descending; within a tied score, sort by named-field-count on the sheet descending, then alphabetical by sheet name; hidden sheets sort to the bottom of the entire ranked list regardless of score (flag each as hidden inline).
2. **Per-sheet factor breakdown.** C1-C6 contribution per sheet as a nested bulleted list, not a markdown table (the chat surface does not render tables): one top-level bullet per sheet (score, tier) with a nested sub-bullet listing the C1-C6 contributions.
3. **Simple / moderate / complex buckets.** Count per bucket.

## Validation Gate

- **V1.** Workbook named explicitly (or workbook-level identifier if no name set).
- **V2.** Orient-mode output at or under 500 words (HC-2).
- **V3.** Every complexity score cites C1-C6 contributions (HC-4).
- **V4.** HC-3 short-circuit fires for workbooks under 5 sheets and 10 calcs.
- **V5.** Modified-date absence stated plainly if not available (HC-6).
- **V6.** No URLs pasted.
- **V7.** Routes to exhaustive skills carry manual fallbacks (HC-5).
- **V8.** Complexity scores are never framed as quality judgments (HC-8).

## Anti-patterns

- Running Orient mode on a trivial workbook (should short-circuit per HC-3).
- Exceeding 500 words in Orient mode.
- Inventing a C-factor not in C1-C6.
- Fabricating a modified-date when `get-workbook-inventory` returns none.
- Framing a complex worksheet as "bad" or "wrong" (HC-8).
- Running the full orient summary when the author triggered Complexity-score mode.
- Pasting a URL to any community resource.

## Composability

Standalone-safe.

| Situation | Route target (if installed) | Manual fallback |
|---|---|---|
| Author wants the full metric dictionary after orientation | `data-scribe` | Author reads field descriptions manually from the Data pane |
| Author wants the full calc catalog | `calc-documenter` | Author inspects calcs individually from the Data pane |
| Author wants a stakeholder-handoff onepager | `workbook-summary-onepager` | Author composes a onepager from the orient summary + a one-paragraph headline |
| Author wants to track changes going forward | `workbook-auditor` | Author snapshots the workbook manually and diffs against future versions |

## Standalone use

The Orient-mode output is self-contained. The complexity ranking is self-contained. Author can act on either without any downstream skill installed.

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
