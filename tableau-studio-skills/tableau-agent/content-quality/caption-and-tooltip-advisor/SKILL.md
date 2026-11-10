---
name: caption-and-tooltip-advisor
description: "Use when the user says 'Rewrite my tooltips', 'fix my captions', 'my tooltips look weird', 'SUM of Sales in the tooltip looks ugly'. Flags weak tooltips, captions, and labels on a dashboard and proposes rewrites for your audience, with steps to apply them. Read-only."
---

# Tableau Caption and Tooltip Advisor

Reads an open Tableau dashboard, finds weak captions, tooltips, and labels against a locked 6-rule catalog, proposes rewrites in the author's declared audience voice. Pairs with dashboard-caption-audit (presence check) and spellcheck (typo check) by owning the "the labels are there but they are bad" problem neither covers.

## When to use (full trigger detail)

Audit tooltips and captions on a Tableau dashboard and propose rewrites. Reads current tooltip, caption, and label text; flags weak ones against a locked 6-rule catalog (T1-T6. uninformative measure labels, raw field names in tooltips, missing dashboard context captions, missing worksheet captions on complex views, tooltip-field mismatches, placeholder text); proposes rewrites inline with numbered Desktop steps. Author-declared audience shapes the voice. Read-only. Trigger on "rewrite my tooltips", "fix my captions", "my tooltips look weird", "better tooltip text", "SUM of sales in tooltip looks ugly", "tooltip and caption review", "my labels are bad". Do NOT trigger for. presence-only audits (route to dashboard-caption-audit), typo-only checks (route to spellcheck), whole-dashboard critique (route to viz-critique-pro-studio), authoring or editing anything in Desktop (out of scope).

## Reference files

- **`skill-expertise/tooltip-catalog.md`.** The locked T1-T6 rule set with per-rule evidence signals, severity ceilings, and rewrite patterns.
- **`skill-expertise/audience-voice-rules.md`.** Four-profile audience taxonomy (executive, analyst, operations, external) with per-rule voice modifiers.

## When to use

Author has a dashboard with populated captions and tooltips that read poorly. Wants rewrites, not presence checks.

## Hard Constraints

- **HC-1 Read-only.** Author applies rewrites manually in Desktop.
- **HC-2 Locked T1-T6 catalog.** No ad-hoc rules invented mid-run.
- **HC-3 Proposed text names structure, never fabricates conclusions.** "Total revenue by region" is fine. "Revenue is strong" is not.
- **HC-4 Honest "captions and tooltips read well" verdict.** No manufactured findings.
- **HC-5 Audience declaration shapes voice.** Executive terse, analyst technical, operations action, external context-first. Locked taxonomy.
- **HC-6 Numbered Desktop steps per proposed rewrite.** Every T-rule finding carries the exact Desktop path to apply the fix.
- **HC-7 Standalone-safe routing.**
- **HC-8 No pasted URLs to community resources.**

## Workflow

**Tools used.** `list-dashboards` (to enumerate dashboards and confirm which is the target), `list-worksheets` (to enumerate sheets on the target dashboard and resolve zone-to-sheet mapping for T4 complexity scoring), `list-available-fields` (to resolve technical field names for jargon rewrites in T1 and T2 and to detect tooltip-field mismatches for T5), `get-dashboard-xml` (reads dashboard-level title/context-caption and layout only; used for T3), `get-worksheet-xml` (load-bearing read for current tooltip templates, worksheet captions, and axis-label text per sheet contained in the target dashboard; used for T1, T2, T4, T5; call once per contained sheet, never once for the whole dashboard, since this data does not exist at the dashboard-XML level), `get-workbook-inventory` (to pull data-source names for Analyst and External voice rewrites that benefit from "sourced from X" context; ensure the data-source context is in hand for those two audiences, which may mean a fresh call on a first run or reusing an already-in-hand read on a subsequent mid-session voice change. Skip this call entirely for Executive and Operations audiences, which do not surface data-source detail in their rewrite patterns).

Steps:

1. Call `list-dashboards`. Confirm target.
2. Ask the author to declare audience (executive / analyst / operations / external).
3. Call `get-dashboard-xml` to read the dashboard title/context caption (for T3) and the list of contained sheets. Ask the author to make each contained sheet active in Desktop in turn (one at a time is fine) before calling `get-worksheet-xml` on it. An active sheet reduces the chance of a stale or dashboard-bound-sheet read failure. Call `get-worksheet-xml` once per contained sheet to read that sheet's tooltip template, worksheet caption, and axis-label text (for T1, T2, T4, T5).
4. Run T1-T6 against the extracted text. For each weak item, propose a rewrite in the declared audience voice.
5. Emit the output: findings by T-rule with current text + proposed rewrite + Desktop step.
6. If no findings, emit the honest "reads well" verdict (HC-4).

## Modes

**Audit mode (default).** Full T1-T6 scan with rewrites.

**Rewrite-suggestions-only mode.** Compressed output: only the rewrites, grouped by sheet. Skip pass/fail reporting. Author triggers with "just the rewrites" or "give me the rewrites only."

## Error Handling

Every recovery path below delivers partial value, never a bare refusal. Name the failure plainly, deliver what the skill can still do, and flag anything downgraded so the author knows the output is incomplete.

| Failure | Cause | Recovery |
|---|---|---|
| `list-dashboards` returns empty or errors | No workbook open, or workbook has zero dashboards | State plainly that no workbook or dashboard was found. Offer to walk through `tooltip-catalog.md` and `audience-voice-rules.md` as reading reference until a workbook is open. Do not proceed on an assumed dashboard. |
| Dashboard has zero tooltip/caption surfaces | Dashboard is new or uses only chart titles; no tooltip templates have been customized and no caption zones exist | State plainly: "This dashboard has no customized tooltips or captions yet. No audit is possible until something has been written to review. Here are the T1-T6 rules to design to before you build them, so you can skip the rewrite step entirely." Deliver the catalog summary as a design-reference, not a false "already reads well" verdict (which would conflate "no text" with "good text"). |
| `get-dashboard-xml` returns empty, errors, or missing text | Dashboard XML corrupted, Studio tool failure, or dashboard was never saved after last change | Fall back to `list-worksheets` and `list-available-fields` for sheet and field enumeration only. State plainly: "Current tooltip and caption text could not be read; audit cannot run. Here is a T1-T6 design-reference the author can hand-check against." Do not fabricate current tooltip or caption text. |
| `get-worksheet-xml` fails on one or more contained sheets (e.g., a dashboard-bound-sheet read failure) while others succeed | Known Desktop reliability gap on some dashboard-bound sheets, or the author has not made that sheet active | Ask the author to make the failing sheet active in Desktop and retry once. If it still fails, proceed with the audit on the sheets that did read successfully. State plainly which sheet(s) could not be read and that findings for those sheets are incomplete, not absent. Do not fabricate tooltip, caption, or axis-label text for an unread sheet. |
| `list-worksheets` or `list-available-fields` returns empty or errors | Workbook has no worksheets enumerated, or field metadata call fails | Fall back to text already read from `get-dashboard-xml`. State plainly: "Zone-to-sheet mapping and T5 ghost-field detection used dashboard XML only; worksheet/field metadata was unavailable. T5 findings may be incomplete." Do not fabricate sheet or field names. |
| Author declares non-standard audience ("my VP", "the readout", "a mixed group") | Audience outside the four locked profiles | Map to the closest locked profile per `audience-voice-rules.md` mapping rules. State the mapping in the output ("Mapping 'the readout' to Executive voice because that's the typical skip-level audience"). Let the author correct the mapping if wrong. Deliver the full audit; do not loop. |
| Author declines to pick an audience ("just pick one", silence, "whatever") | Author wants the audit but does not want to answer the audience question | Default to **Analyst** voice (middle of the four profiles for voice-mixing risk; named fields and methodology notes acceptable, which is the safest fallback since analyst voice drifts least when applied to the wrong audience). State the default plainly: "Defaulting to Analyst voice because you did not declare one. Say 'use executive voice' or any other profile and I will re-emit." Deliver the full output; do not loop. |
| Author changes the audience mid-run | Author declared one audience, received audit output, then asks for a different voice | Do not force a full re-scan. Re-emit only the proposed rewrites in the new voice; the findings list (which T-rule fired where) stays. State plainly: "Rewriting proposed text in [new audience] voice. Findings and Desktop steps unchanged." Reuse the `get-dashboard-xml` read already in hand; do not re-call it. |
| Dashboard is placeholder-text-only (all text is "Sheet 1", "Dashboard 1", "Insert title here", etc.) | Dashboard was created but never populated with real content | Per T6, every finding will be a placeholder FAIL. State plainly: "This dashboard appears to be an empty template. Every text surface is placeholder content. Rather than emit 15 identical T6 findings, here is a single consolidated recommendation: replace all placeholder text with real content before running the audit again." Do not emit a 15-finding T6 cascade. |
| Opt-in file save fails (`.md` / `.txt` write errors) | Filesystem permissions, path collision, disk full, or user cancels | Emit the full rewrite set inline in chat regardless of save status. State the save failure plainly with path and error. Never gate the audit output on the save succeeding. Default save location is the user's Downloads folder. |
| Author asks the skill to fabricate caption text that overclaims ("say revenue is strong", "write a caption that says Northeast is leading") | User requests an interpretive statement rather than a structural rewrite | Per HC-3, do not fabricate. State plainly: "I rewrite labels to name what the chart shows structurally, not what it means. 'Revenue by region, sorted descending' is in scope. 'Revenue is strong in the Northeast' is not; that is interpretation the author owns. Here is the structural rewrite instead." Deliver the structural rewrite in place of the fabricated one. |

## Rule catalog summary (full catalog in tooltip-catalog.md)

- **T1 Uninformative measure labels.** `SUM(Sales)` left as the axis label or tooltip measure name. Severity: NEEDS ATTENTION. Rewrite to a plain-language label in the audience voice.
- **T2 Raw field names in tooltips.** `[Order Date]` in a tooltip template. Severity: NEEDS ATTENTION.
- **T3 Missing dashboard-level context caption.** Dashboard has no caption describing what it answers. Severity: FAIL for external and C-suite audiences, NEEDS ATTENTION otherwise.
- **T4 Missing worksheet caption on complex views.** Worksheet has 3+ pills on Rows + Columns and no caption. Severity: NEEDS ATTENTION.
- **T5 Tooltip-field mismatch.** Tooltip references a field the viz does not visually encode. Severity: NEEDS ATTENTION (user confusion).
- **T6 Placeholder text.** "Insert title here," "Double-click to edit," default sheet names like "Sheet 1." Severity: FAIL.

## Output format (Audit mode)

1. **Dashboard and audience confirmed.** One sentence.
2. **Verdict.** "Ships broken" / "Needs attention" / "Reads well."
3. **Findings ranked by severity.** Per finding:
   - Rule ID (T1-T6).
   - Current text (quoted).
   - Proposed rewrite in audience voice.
   - Numbered Desktop step to apply.
4. **Rewrite preview.** Side-by-side current vs. proposed for the top findings.
5. **Opt-in file save.** `.md` or `.txt` with the full rewrite set per two-tier delivery.

## Output format (Rewrite-suggestions-only mode)

1. **Dashboard and audience confirmed.**
2. **Rewrites by sheet.** Grouped list. Each: current → proposed.
3. **One combined Desktop-steps block** at the end.

## Validation Gate

- **V1.** Audience is one of four locked profiles.
- **V2.** Dashboard named explicitly.
- **V3.** Every finding cites a T-rule ID (HC-2).
- **V4.** Every proposed rewrite names structure, never conclusions (HC-3).
- **V5.** Every rewrite has a numbered Desktop step (HC-6).
- **V6.** If no findings, verdict is "Reads well" and no rewrites are manufactured (HC-4).
- **V7.** No URLs pasted (HC-8).
- **V8.** Voice consistency across every proposed rewrite in a single run. Every rewrite uses the declared audience voice. No proposed rewrite in an Executive-voice run contains analyst-level jargon (named LODs, aggregation syntax, chart-mechanic references). No proposed rewrite in an External-voice run assumes internal product knowledge or uses undefined acronyms. No proposed rewrite in an Operations-voice run reads as abstract strategy (should be action-focused and named-entity). If any single rewrite drifts from the declared voice, revise before shipping.

## Anti-patterns

- Inventing a T-rule not in the locked catalog.
- Fabricating a business conclusion in a rewrite ("Northeast is strong").
- Running audit on a clean dashboard and manufacturing findings to justify output.
- Rewriting into a voice different from the declared audience.
- Omitting the Desktop step for any proposed rewrite.
- Pasting a URL to any community resource.

## Composability

Standalone-safe.

| Situation | Route target (if installed) | Manual fallback |
|---|---|---|
| Author wants a presence check too | `dashboard-caption-audit` | Author checks each sheet manually for missing titles/captions |
| Author wants typo check alongside | `spellcheck` | Author reads through for typos manually |
| Author wants a full dashboard critique | `viz-critique-pro-studio` | Author reviews against their team's design standard |
| Author wants a plain-language rewrite of the whole dashboard | `stakeholder-translator` | Author composes a stakeholder paragraph from the rewrites |

## Standalone use

The rewrite set and numbered Desktop steps are self-contained.

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
