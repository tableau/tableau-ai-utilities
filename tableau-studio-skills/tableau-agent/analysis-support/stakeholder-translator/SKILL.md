---
name: stakeholder-translator
description: "Use when the user says 'Translate this for my VP', 'plain-language version', 'explain this to a non-analyst', 'jargon-free summary'. Turns a dashboard into one page for a non-technical audience: what it answers, what it doesn't, likely questions, and the key chart. Read-only."
---

# Tableau Stakeholder Translator

Produces a plain-language translation of what a Tableau dashboard answers, in the voice of the stakeholder who will consume it. Scope-aware: names what the dashboard does NOT answer, so the author does not overclaim in the meeting.

## When to use (full trigger detail)

Translate a Tableau dashboard into plain language for a non-technical stakeholder. Produces a one-page translation layer. what this answers in plain words, what this does NOT answer, three likely follow-up questions, and the one chart that carries the headline. Audience-shaped voice from a locked 5-profile taxonomy (C-suite, business sponsor, operational manager, external customer, cross-functional peer). Read-only. Trigger on "translate this for my VP", "plain language version", "explain this to a non-analyst", "stakeholder version", "jargon-free summary", "what does this answer in their words". Do NOT trigger for. presenter scripts (route to dashboard-walkthrough-generator), metric dictionaries (route to data-scribe), handoff onepagers (route to workbook-summary-onepager), dashboard-level critique (route to viz-critique-pro-studio), authoring or editing anything in Desktop (out of scope).

## Reference files

- **`skill-expertise/stakeholder-voice-guide.md`.** Five locked audience profiles (C-suite, business sponsor, operational manager, external customer, cross-functional peer) with vocabulary rules and follow-up-question patterns.
- **`skill-expertise/jargon-swap-list.md`.** Common analyst-jargon terms with plain-language substitutions, keyed by audience profile.

## When to use

Author has built a technical dashboard and needs to describe it to a non-technical stakeholder. Wants a short rewrite plus the questions that stakeholder is likely to ask, not a design critique.

## Hard Constraints

- **HC-1 Read-only.** No mutation.
- **HC-2 Author declares audience before output.** Five locked profiles.
- **HC-3 Translation names structure and framing, never fabricates conclusions.** "This dashboard shows how our customer count has moved by region" is fine. "Customer growth is strong" is not.
- **HC-4 Honest "already plain" verdict.** If the dashboard labels and captions already read in plain language, say so and offer only the follow-up-question section.
- **HC-5 Required "What this does NOT answer" section.** Prevents overclaiming. The skill always surfaces at least one scope boundary even when the dashboard is clean.
- **HC-6 Standalone-safe routing.** Handoffs to dashboard-walkthrough-generator, data-scribe, workbook-summary-onepager all optional with manual fallbacks.
- **HC-7 Audience taxonomy locked.** No ad-hoc audience types.
- **HC-8 No pasted URLs to community resources.**

## Workflow

**Tools used.** `list-dashboards` (to enumerate dashboards and confirm which is the target), `list-worksheets` (to resolve zone-to-sheet mapping and identify sheets referenced in the translation), `list-available-fields` (to resolve technical field names for jargon-swap lookups and to identify data-source references for the Business sponsor voice), `get-dashboard-xml` (load-bearing read for current title, caption, label, and tooltip text; everything the translation actually swaps depends on this), `get-workbook-inventory` (to pull data-source names for the Business sponsor voice's "sourced from X" clarification; skip this call for C-suite and Operational manager audiences, which don't surface data-source detail by default).

**Why `get-dashboard-xml`, not `get-worksheet-xml`.** `get-worksheet-xml` has a confirmed 500/`operation-failed` risk on sheets that are already placed on a dashboard with real data (exactly the sheets this skill reads). `get-dashboard-xml` is used deliberately to avoid that failure mode, not as an oversight.

**General call-skipping rule.** Skip any read whose output the current branch cannot use. This already applies to `get-workbook-inventory` for C-suite/Operational audiences (above); it also applies to `list-available-fields` under the HC-4 "already plain" branch. If `get-dashboard-xml` text shows no analyst-jargon surfaces, do not call `list-available-fields` for jargon-swap lookups, since there is nothing left to swap.

**Mid-session audience change.** When the author asks for a different voice after already receiving output (see Error Handling table below), reuse the `get-dashboard-xml` read already in hand. Do not re-call it. Only the voice-dependent prose is regenerated.

Steps:

1. Call `list-dashboards`. Confirm target. If `list-dashboards` returns empty or errors, state so and offer to walk through the stakeholder-voice-guide as reading reference until a workbook is open.
2. Ask the author to declare the audience from the five locked profiles. Map any non-standard phrasing before proceeding.
3. Call `get-dashboard-xml` to read current title, caption, and tooltip text.
4. Apply the jargon-swap-list against identified technical terms.
5. Generate the five-section output.

## Audience taxonomy (locked)

Full detail in `skill-expertise/stakeholder-voice-guide.md`.

- **C-suite.** 1-2 minute attention budget. Headline only. Strategic follow-ups.
- **Business sponsor.** 3-5 minute budget. Named metrics with definitions. Follow-ups about expectations.
- **Operational manager.** 3-5 minute budget. What to do next. Follow-ups are tactical.
- **External customer.** 5-10 minute budget. Define everything. Follow-ups are clarifying.
- **Cross-functional peer.** 3-5 minute budget. Shared vocabulary from their function. Follow-ups are relational ("how does this affect my team").

## Error Handling

| Failure | Cause | Recovery |
|---|---|---|
| `list-dashboards` returns empty or errors | No workbook open, or workbook has zero dashboards | State plainly that no workbook or dashboard was found. Offer to walk through the stakeholder-voice-guide and jargon-swap-list as reading reference until a workbook is open. Do not proceed on an assumed dashboard. |
| Dashboard already reads in plain language | Dashboard title, captions, and tooltips use plain-language terms with no analyst-jargon surfaces | Per HC-4, state "The dashboard already reads in plain language. Here is the follow-up-question set anyway." Deliver sections 3-5 (scope boundaries, three questions, headline chart). Skip section 2 (translation paragraph) explicitly. |
| `get-dashboard-xml` returns empty, errors, or missing text | Dashboard XML corrupted, Studio tool failure, or dashboard was never saved after last change | Fall back to `list-worksheets` and `list-available-fields` for sheet and field enumeration only. State plainly in the output: "Dashboard title and caption text could not be read; translation uses sheet and field names only." Do not fabricate title text. |
| `list-worksheets` or `list-available-fields` returns empty or errors | Workbook has no worksheets enumerated, or field metadata call fails | Fall back to data already read from `get-dashboard-xml`. State plainly: "Jargon-swap lookups used dashboard XML only; worksheet/field metadata was unavailable." Do not fabricate sheet or field names. |
| Author declares non-standard audience ("my boss's boss", "a mixed group", "the readout") | Audience outside the five locked profiles | Map to the closest locked profile per stakeholder-voice-guide.md mapping rules. State the mapping in the output ("Mapping 'the readout' to C-suite voice because that's the typical skip-level audience"). Let the author correct the mapping if wrong. |
| Author declines to pick an audience ("just pick one", silence, "whatever works") | Author wants the output but does not want to answer the audience question | Default to **Business sponsor** voice (middle of the five profiles for voice-mixing risk, assumes some business vocabulary but defines terms on first use). State the default plainly: "Defaulting to Business sponsor voice because you did not declare one. Say 'use C-suite voice' or any other profile and I will re-emit." Deliver the full output; do not loop on the audience question. |
| Author changes the audience mid-run | Author declared one audience, received the translation, then asks for a different voice | Do not force a full rerun. Re-emit sections 2 (translation paragraph) and 4 (three questions in stakeholder voice) in the new voice. Sections 1 (confirmation), 3 (scope boundaries), and 5 (headline chart) stay. State plainly: "Rewriting translation and questions in [new audience] voice. Scope boundaries and headline chart unchanged." |
| Author asks for a conclusion the dashboard does not support ("tell me we're growing", "say the Northeast is strongest") | User requests an interpretive statement rather than a plain-language translation | Per HC-3, do not fabricate. State plainly: "The dashboard does not assert that conclusion. The translation names what the dashboard shows structurally; the interpretation is yours to make." Add the request as a scope-boundary bullet in section 3. |
| Opt-in file save fails (`.md` / `.txt` write errors) | Filesystem permissions, path collision, disk full, or user cancels | Emit the full translation content inline in chat regardless of save status. State the save failure plainly with path and error. Never gate the translation itself on the save succeeding. Default save location is the user's Downloads folder. |
| Dashboard has 15+ sheets (scalability edge) | Large dashboard with more sheets than fit in a translation of this length | Translate the primary surface (KPI tile + headline chart + 1-2 supporting views). State plainly: "This dashboard has [N] sheets. Translation covers the primary [K] sheets by spatial priority. [N-K] additional sheets are not translated; say 'extend to all sheets' or name specific ones to add." Do not emit a 15-section translation; it exceeds a stakeholder's attention budget regardless of audience. |
| Cross-functional peer declared without specifying the peer's function | Author picked Cross-functional peer voice (e.g., "translate this for a peer") without naming the peer's domain. The voice depends on the function (Product → roadmap/feature vocabulary; Marketing → campaign/attribution vocabulary; Sales → pipeline/quota vocabulary; Support → ticket/CSAT vocabulary) | Ask once: "Which function is this peer in: Product, Marketing, Sales, or Support?" If the author answers, use that function's vocabulary. If the author says "just pick one" or declines, default to **Product** (safest generalization: product vocabulary is widely understood across teams). State the default plainly: "Defaulting to Product function because you did not name one. Say 'they are in Sales' or any other function and I will re-emit." Deliver the full output; do not loop. |
| Dashboard appears to be a splash / navigation / cover page | Dashboard has very few sheets, text-only zones dominate, nav buttons or image zones carry the layout, or the only sheet is a title/branding placeholder with no measure encoding. HC-4 "already plain" might fire by accident on such a dashboard, but there is no actual data content to translate | Detect the splash pattern (fewer than 2 data-encoding sheets, or more text/image zones than chart zones). State plainly: "This dashboard appears to be a cover or navigation page rather than a content dashboard. Point me at the content dashboard it links to and I will translate that one. If you did want this one translated anyway (e.g. the cover text itself is the deliverable), say 'translate the cover page' and I will proceed." Do not emit the five-section translation on a splash page. Do not falsely trigger the HC-4 verdict. |

## Output format

1. **Audience and dashboard confirmed.** One sentence with the mapping if the audience was non-standard.
2. **What this answers (in their words).** One paragraph. Plain language. Jargon swapped per jargon-swap-list.
3. **What this does NOT answer.** Required scope boundaries. At least 2 bullet points even on a clean dashboard (HC-5).
4. **Three likely follow-up questions.** Each with: the question in stakeholder voice, where the dashboard answers it (sheet + data point), where it doesn't (if applicable).
5. **The one chart that tells the headline.** Named sheet + 1-sentence framing of why that sheet carries the headline. Tie-break rule when more than one sheet looks headline-worthy: prefer the sheet containing the single largest KPI/BAN tile; if none exists, prefer the topmost-left sheet in the dashboard's zone order.
6. **Numbered Desktop steps** if any title, caption, or tooltip rewrite is needed to support the translation (optional section, only if the current labels will fail the audience).

## Validation Gate

- **V1.** Audience is one of five locked profiles.
- **V2.** Dashboard named explicitly.
- **V3.** Translation uses plain language (jargon-swap-list applied).
- **V4.** "What this does NOT answer" section is present with at least 2 bullets.
- **V5.** Three follow-up questions, each tied to a specific data point OR explicitly flagged as "the dashboard does not answer this."
- **V6.** No fabricated business conclusions (HC-3).
- **V7.** No URLs pasted.
- **V8.** Voice consistency across the entire output. Sections 2 (translation paragraph), 4 (three questions in stakeholder voice), and the headline-chart framing in section 5 all use the declared audience voice. No sentence in a C-suite run contains analyst-level jargon (named LODs, aggregation syntax, chart-mechanic references). No sentence in an External customer run assumes internal product knowledge. No sentence in a Cross-functional peer run uses the sender's domain jargon when their jargon is different. If any section drifts from the declared voice, revise before shipping.

## Anti-patterns

- Fabricating a conclusion in plain language ("revenue is strong" → "customer growth is strong" is the same violation in a different voice).
- Skipping the "What this does NOT answer" section when the dashboard looks clean.
- Running C-suite voice with analyst-level jargon.
- Mapping an unknown audience to "cross-functional peer" without stating the mapping.
- Promising the dashboard answers a stakeholder question it does not have the data to answer.

## Composability

Standalone-safe.

| Situation | Route target (if installed) | Manual fallback |
|---|---|---|
| Author wants a presenter script after the translation | `dashboard-walkthrough-generator` | Author uses the translation sections directly as talking points |
| Author wants a metric dictionary alongside | `data-scribe` | Author pastes the "what this answers" paragraph plus a field list manually |
| Author wants a stakeholder-handoff onepager | `workbook-summary-onepager` | Author merges the translation + a one-paragraph headline |

## Standalone use

The five-section output is self-contained. Author can send it to the stakeholder directly or paste into email.

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
