---
name: dashboard-walkthrough-generator
description: "Use when the user says 'Walkthrough script', 'presenter notes', 'how do I present this?', 'talking points for this dashboard'. Writes a presenter script for a dashboard: walkthrough order, speaker notes per sheet, a 30-second version, and likely questions. Read-only."
---

# Tableau Dashboard Walkthrough Generator

Reads an open Tableau dashboard and produces a presenter script: numbered walkthrough order, per-sheet speaker notes, a 30-second elevator version, and likely stakeholder questions with the data points that answer each. Audience-shaped tone. Read-only text output.

## When to use (full trigger detail)

Generate a presenter script for a Tableau dashboard. numbered walkthrough order, per-sheet speaker notes, a 30-second elevator version, and likely stakeholder questions. Reads the open dashboard (sheets, titles, captions, filters, spatial layout) and produces an audience-shaped script the author can paste into meeting notes. Read-only. Trigger on "walkthrough script", "presenter notes", "how do I present this", "talking points for this dashboard", "elevator pitch for this viz", "notes for my meeting". Do NOT trigger for. designing a dashboard (route to viz-planner), scoring an existing dashboard (route to viz-critique-pro-studio), metric dictionary (route to data-scribe), stakeholder handoff onepager (route to workbook-summary-onepager), authoring or editing anything in Desktop (out of scope).

## Reference files

- **`skill-expertise/audience-voice-guide.md`.** Four locked audience profiles (executive, analyst, operations, external) with tone rules, length targets, and question-anticipation patterns per audience.
- **`skill-expertise/script-templates.md`.** Narration scaffolding for the walkthrough: opener patterns, sheet-transition patterns, pause-and-check patterns, closer patterns.

## When to use

Author has a dashboard built and needs to present it to a stakeholder. Wants presenter notes they can paste into meeting prep, not a design critique.

## Hard Constraints

- **HC-1 Read-only.** No mutation.
- **HC-2 Author declares audience before output.** Executive, analyst, operations, or external. Locked taxonomy from audience-voice-guide.md.
- **HC-3 Walkthrough names structure, not conclusions.** "This chart shows revenue by region sorted descending" is fine. "Revenue is strongest in the Northeast" is not; that is interpretation the author owns.
- **HC-4 Honest single-view verdict.** If the dashboard has only one sheet, say so and offer a short talking-points list rather than fabricating a multi-sheet walkthrough.
- **HC-5 No pasted URLs to community resources.**
- **HC-6 Standalone-safe routing.** Handoffs to viz-critique-pro-studio, data-scribe, workbook-summary-onepager carry manual fallbacks.
- **HC-7 Audience taxonomy locked.** No ad-hoc audience types ("my boss's boss," "a mixed group") outside the four locked profiles.

## Workflow

**Tools used.** `list-dashboards` (to enumerate dashboards and confirm which is the target), `list-worksheets` (to resolve zone-to-sheet mapping and identify sheets that may be hidden-on-phone or deprecated), `list-available-fields` (to identify KPI candidates by data type and to resolve field names for the Analyst voice), `get-dashboard-xml` (load-bearing read for spatial order, tab order, title text, caption text, and tooltip templates per sheet; everything the walkthrough actually describes depends on this), `get-workbook-inventory` (to pull data-source names and refresh-date metadata for the Analyst voice's "sourced from X, extract from Y" opener; skip this call when the audience is Executive or External, which don't surface data-source detail).

Steps:

1. Call `list-dashboards`. If more than one, ask which is the target. If `list-dashboards` returns empty or errors, state that no workbook or dashboard was found. Do not proceed, but offer to walk through the audience-voice guide so the author can preview how the output will shape once a workbook is open.
2. Ask the author to declare the audience from the locked taxonomy (executive, analyst, operations, external). If the author describes a non-standard audience ("my team," "my VP"), map to the closest locked profile and state the mapping.
3. Call `get-dashboard-xml` on the target dashboard to read sheet order, titles, captions, filters, and tooltip content.
4. Call `list-worksheets` and `list-available-fields` to resolve zone-to-sheet mapping and identify KPI sheets.
5. Build the walkthrough using audience-voice-guide.md tone rules and script-templates.md scaffolding.
6. Emit the output in the template below.

## Audience taxonomy (locked)

Full detail in `skill-expertise/audience-voice-guide.md`.

- **Executive.** Terse. Headline first. One number per sentence. 30 seconds max. Follow-ups anticipated are strategic ("what should we do about this").
- **Analyst.** Technical. Named fields, aggregations, filters. Longer walkthrough tolerated. Follow-ups are methodological ("how is this computed," "what does the extract cover").
- **Operations.** Action-focused. What to do next, by when, by whom. Follow-ups are tactical ("which account should I call first").
- **External.** Context-first. Define jargon. No internal acronyms. Follow-ups are clarifying ("what does ARR mean in this context").

## Error Handling

| Failure | Cause | Recovery |
|---|---|---|
| `list-dashboards` returns empty or errors | No workbook open, or workbook has zero dashboards | State plainly that no workbook or dashboard was found. Offer to walk through the audience-voice guide as reading reference until a workbook is open. Do not proceed on an assumed dashboard. |
| Single-sheet dashboard | Target dashboard has exactly one worksheet | Per HC-4, emit a talking-points list rather than a numbered walkthrough. Keep the elevator, speaker notes for the one sheet, and the three likely questions. Skip the numbered walkthrough-order section explicitly. State the mode switch plainly. |
| Dashboard has no title or captions | Dashboard is auto-generated or title/caption zones removed | Proceed with the walkthrough using sheet names and field names in place of the dashboard title. Flag in the output: "This dashboard has no title or captions. The walkthrough uses sheet names as structural anchors." Do not fabricate a dashboard title. |
| `get-dashboard-xml` returns empty, errors, or missing spatial layout data | Dashboard XML corrupted, Studio tool failure, or dashboard was never saved after last change | Fall back to `list-worksheets` for sheet enumeration only. State plainly in the output: "Spatial order could not be read; walkthrough uses workbook-tab order instead of dashboard-canvas order." Do not fabricate spatial positions. |
| Author declares non-standard audience ("my boss's boss", "a mixed group") | Audience outside the four locked profiles | Map to the closest locked profile per audience-voice-guide.md mapping rules. State the mapping in the output ("Mapping 'mixed group' to External voice because that's the lowest-context audience likely present"). Let the author correct the mapping if wrong. |
| `list-worksheets` or `list-available-fields` returns empty or errors | Workbook has no worksheets enumerated, or field metadata call fails | Fall back to the sheet names and fields already read from `get-dashboard-xml`. State plainly: "Zone-to-sheet mapping and KPI-candidate detection used dashboard XML only; worksheet/field metadata was unavailable." Do not fabricate sheet or field names. |
| Author declines to pick an audience ("just pick one", silence, "whatever is fine") | Author wants the output but does not want to answer the audience question | Default to **Analyst** voice (middle of the four profiles for voice-mixing risk, safest fallback). State the default plainly in the opening line: "Defaulting to Analyst voice because you did not declare one. Say 'use executive voice' or any other profile and I will re-emit." Deliver the full output; do not loop on the audience question. |
| Author changes the audience mid-run | Author declared one audience, received partial output, then asks for a different voice | Do not force a full rerun. Re-emit only the sections affected by voice (elevator, speaker notes, likely-questions, closer). The numbered walkthrough-order and the dashboard-structural facts stay. State plainly: "Rewriting elevator, speaker notes, questions, and closer in [new audience] voice. Walkthrough order and structural facts unchanged." |
| Opt-in file save fails (`.md` / `.txt` write errors) | Filesystem permissions, path collision, disk full, or user cancels the save | Emit the full walkthrough content inline in chat regardless of save status. State the save failure plainly: "File save to [path] failed with [error]. Full walkthrough is in this response; copy and paste into your notes." Never gate the walkthrough itself on the save succeeding. |
| Dashboard has 20+ sheets (scalability edge) | Large dashboard with more sheets than fit in a reasonable walkthrough length | Walk through the top 5-7 sheets by spatial priority (KPI band first, then primary charts, then supporting views). State plainly: "This dashboard has [N] sheets. Walkthrough covers the 5-7 primary ones. [N-7] additional sheets are not shown; say 'extend to all sheets' or name specific ones to add." Do not emit a 20-section walkthrough; it exceeds a reasonable meeting-prep length regardless of audience. |

## Output format

1. **Dashboard and audience confirmed.** One sentence.
2. **30-second elevator.** One paragraph. The headline a stakeholder would remember if they heard nothing else.
3. **Numbered walkthrough order.** Sheet 1 to N. Each entry: what to point at, what question it answers, where to pause. If the dashboard has more than 8 sheets, group them into 2-3 thematic clusters (by topic or by dashboard zone proximity) rather than listing every sheet individually; name each cluster and summarize it as one walkthrough beat.
4. **Speaker notes per sheet.** What the data shows structurally (not interpretively, per HC-3), what to say, what to anticipate.
5. **Likely stakeholder questions.** Three, each tied to the data point that answers it.
6. **Opt-in file save.** Offer `.md` or `.txt` save of the full script. Default save location is the user's Downloads folder unless the author names a different path. Two-tier delivery per portfolio convention.

## Validation Gate

- **V1.** Audience is one of the four locked profiles.
- **V2.** Dashboard is named explicitly.
- **V3.** Walkthrough names structure, not conclusions (HC-3).
- **V4.** 30-second elevator is actually at or under 30 seconds spoken (roughly 75 words).
- **V5.** Three stakeholder questions, each tied to a specific data point.
- **V6.** No URLs pasted.
- **V7.** If dashboard has one sheet, verdict is a talking-points list, not a walkthrough (HC-4).
- **V8.** Voice consistency across the entire output. Every section (elevator, walkthrough order, speaker notes, likely-questions, closer) uses the declared audience voice. No sentence in an executive-voice run contains analyst-level jargon (e.g., named LODs, aggregation syntax). No sentence in an external-voice run assumes internal product knowledge. If any section drifts from the declared voice, revise before shipping.

## Anti-patterns

- Fabricating what the data shows ("revenue is strong"). Only name structure.
- Walking through sheets in XML order rather than spatial order on the dashboard.
- Running audience voice on an ad-hoc audience ("the people in the room") rather than the locked four.
- Generating a walkthrough for a one-sheet dashboard. Say so and give talking points instead.
- Mixing audience voices in a single run.

## Composability

Standalone-safe. Every route optional.

| Situation | Route target (if installed) | Manual fallback |
|---|---|---|
| Author wants a metric dictionary alongside | `data-scribe` | Author documents field meanings in the appendix of their notes manually |
| Author wants the handoff onepager | `workbook-summary-onepager` | Author composes a one-page summary from the walkthrough's elevator + section headlines |
| Author wants design critique first | `viz-critique-pro-studio` | Author reviews the dashboard against their team's design standard before presenting |

## Standalone use

If no downstream skill is available, the walkthrough script is self-contained. The author can present with just this skill's output.

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
