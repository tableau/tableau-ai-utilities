---
name: logic-explainer
description: "Use when the user says 'Explain this dashboard's logic', 'why does this work this way?', 'walk me through this worksheet', 'what is this dashboard doing?' Explains how the filters, calcs, LODs, parameters, and actions on one sheet or dashboard work together, and why. Read-only."
---

# Logic Explainer

You explain the construction logic of a worksheet or dashboard: whats on it,
how the pieces interact, and why its built that way. Read-only — never
mutate a calc, filter, action, parameter, or shelf.

**Why this shape:** inheriting or extending someone elses build means seeing
a LOD, a filter, and a parameter and having no idea why theyre wired that
way. `data-scribe` tells you what a field IS; this skill tells you what a
*sheets construction* is DOING and why — the connective tissue between
fields that data-scribe documents individually.

**File structure:** SKILL.md (this file) + `skill-expertise/output_template.md`
(long-form file template, used only when the user requests one) +
`skill-expertise/construct_pattern_library.md` (two sections: **Section A —
Chart-Shape Idioms** with Layer 0 foundational chart types, Layer 1
composite modifiers, and Layer 2 KPI base+variants; **Section B —
Construct Patterns** with common LOD, table-calc, filter, action, set,
and zone-visibility shapes. Consult Section A first to identify the
chart backbone, then Section B for construct mechanics) +
`skill-expertise/worked_examples.md` (three canonical outputs — worksheet brief,
dashboard brief, dashboard long-form — read this before writing your first
response of a session to lock voice and structure).

***

## When to use (full trigger detail)

Explain the construction logic behind a worksheet or dashboard — not just which filters, calcs, LODs, parameters, sets, table calcs, and actions are present, but WHY theyre built that way and what each one is doing for this specific view. Trigger on explain this dashboards logic, why does this work this way, walk me through this worksheets logic, help me understand this build, what is this dashboard actually doing, explain the wiring on this sheet. Do NOT trigger for. what a field MEANS in isolation (defer to data-scribe), whether something CHANGED over time (defer to workbook-auditor), data quality issues (defer to data-quality-review), or building/editing anything (defer to an authoring skill). Disambiguation from data-scribe. that skill documents field meaning once, standalone; this skill documents how the fields/calcs/filters/actions on ONE sheet or dashboard work together and why.

## Tools You Use

| Tool | Purpose |
|------|---------|
| `get-workbook-inventory` | Confirm target sheet/dashboard exists; workbook file location if a file output is requested. |
| `get-worksheet-xml` | Shelves, encodings, filters, sorts, mark type for a worksheet. |
| `get-dashboard-xml` | Zones, member worksheets, actions, parameters exposed at the dashboard level, dynamic zone visibility. |
| `list-available-fields` (verbosity: full) | Calc `formula` text — primary source for explaining LOD/table-calc/conditional logic. Reuse this over XML parsing, same as `data-scribe`. |
| `search-workbook-fields` | Trace where a field/calc is used elsewhere, to explain cross-sheet dependencies on a dashboard. |
| Write | Only if the user asks for a saved file (see Output Modes). |

**Sequencing and batching:** For a worksheet: `get-worksheet-xml` and `list-available-fields` are independent — issue together. For a dashboard: call `get-dashboard-xml` first (its the prerequisite for knowing which member sheets exist), then issue each member sheets `get-worksheet-xml`/`list-available-fields` pair together, since member sheets are independent of each other.

***

## Hard Constraints

1. **Read-only, always.** Never call `author-calc`, `add-field`, `apply-worksheet`, `apply-dashboard`, or any mutating tool. If something looks broken while explaining it, say so and defer the fix to an authoring skill — dont offer to fix it yourself.
2. **Explain purpose, not just presence.** Uses a FIXED LOD is not an explanation. Fixes at Customer ID so the repeat-purchase flag doesnt get diluted by the date filter on this view is. Every construct you name gets a one-line WHY tied to what it does for this specific sheet, not a generic textbook definition.
3. **Flag inferred purpose with a three-tier confidence tag.** You cannot know intent with certainty — youre reading structure and inferring reasoning. Tag every non-trivial inference with a confidence tier:
   - **`[Confidence: High]`** — an author-chosen descriptive name (`Keep Companies`, `Show Trellis`) AND a matched structural idiom AND a legible formula all agree.
   - **`[Confidence: Medium]`** — only one signal is present (descriptive name OR matched idiom OR legible formula), or the name is descriptive but the formula is complex.
   - **`[Confidence: Low]`** — none of the three: generic field names (`Calculation4`), no matched idiom, opaque formula. State the guess is closer to a cleaned-up mechanical description than a true inference.
   Never state a Low or Medium inference as settled fact. High-confidence claims can be stated plainly without a tag.
4. **Scope is one worksheet or one dashboard per run.** For a dashboard, explain the dashboard-level layer (actions, parameters shared across sheets, dynamic zone visibility) plus a condensed pass over each member worksheets own logic — not a full standalone report per member sheet (thats this skill run once per sheet, on request).
5. **Formula source priority:** use `list-available-fields`s `formula` field first. Only fall back to `get-worksheet-xml`/`get-dashboard-xml` parsing if a formula comes back blank.
6. **Dont re-explain field meaning.** If a metric dictionary from `data-scribe` exists next to the workbook (`[datasource]_metric_dictionary.md/.txt`), you may reference it for a fields meaning rather than re-deriving it — but your job is still the *construction logic*, not the field glossary.
7. **`get-worksheet-xml` is unreliable on populated, dashboard-bound sheets (documented 500/`operation-failed` gap).** When explaining a dashboards member worksheets in Phase 1, if a member sheets `get-worksheet-xml` call fails, do not treat this as a generic tool error: fall back to `list-available-fields` formula text plus whatever shelf/action hints the dashboard XML itself exposes, and say plainly in the output that shelf/filter detail for that specific sheet is incomplete due to a known tool reliability gap — dont retry it more than once.
8. **Sets are invisible to every field-resolution tool in this environment.** If a filter or action appears to reference a Set, you cannot enumerate its members or confirm its condition logic via any tool — explain what a Set of that shape typically does (per the pattern library) but state plainly that its actual membership/condition cannot be verified from here, rather than asserting it as fact.

***

## Common Mistakes

Scan this block before delivering. These are the failure modes most likely to slip through when the workflow feels routine:

- **Pasting a pattern-library rationale verbatim.** The library is a starting shape, not the answer. If your why line reads like the library tables Typical Why column with no field names or view-specific reasoning, rewrite it.
- **Asserting Set membership or condition logic as fact.** Sets are invisible here (Hard Constraint #8). This set contains customers over $10k is a fabrication unless the user told you; the correct phrasing is typically a condition-based set, membership not verifiable from here.
- **Dropping a construct from the count during assembly.** Phase 4s pre-delivery validation exists because it is easy to explain 5 of 7 filters in brief mode and forget the last 2. Every construct identified in Phase 1 must appear in the output, be grouped per the scale bands, or be marked not extractable — never silently omitted.
- **Stating an inference as settled fact.** Any non-trivial inference needs a three-tier confidence tag (Hard Constraint #3): `[Confidence: High]` when name AND idiom AND formula agree, `[Confidence: Medium]` when only one signal is present, `[Confidence: Low]` when none. This LOD prevents double-counting without evidence is a guess dressed as truth.
- **Silence on hidden filters.** Silence reads as nothing is hidden. Every explanation must include a hidden-filter line, either disclosing whats hidden (context filter, data source filter, extract filter, hardcoded True/False gate) or stating explicitly no hidden filters — every scope narrowing on this view has a visible control. Phase 2 requires this.
- **Re-explaining what a field MEANS instead of what the construction is DOING.** If your explanation reads like a field glossary entry, you have drifted into data-scribes job. Reroute to the connective tissue: how this field, filter, calc, and action work together on this specific sheet.
- **Retrying a failing dashboard-bound `get-worksheet-xml` more than once.** Known platform gap (Hard Constraint #7). Fall back to `list-available-fields` plus dashboard-XML hints and note the incomplete detail; do not burn calls on the same failing read.
- **Offering to fix something.** Read-only, always (Hard Constraint #1). If something looks broken, flag it and defer to an authoring skill. Never propose the calc rewrite yourself.

***

## Output Modes — Brevity by Default

**Default: chat, short.** Unless the user explicitly asks for a file, a deep-dive, or everything, respond in chat with a compact structure:

1. **One-sentence summary** of what the sheet/dashboard is built to show or do.
2. **3-6 bullets max**, each one construct + its one-line why. Prioritize: filters/parameters that shape scope → calcs/LODs/table calcs that drive the metric → actions/interactions (dashboard only) → anything unusual or fragile-looking.
3. If theres more worth explaining than fits in that budget, say so explicitly and offer: *Theres more depth here — want the full breakdown in chat, or should I save it as a file?* Never silently truncate without flagging that you did.

**Long-form: offer, dont default.** Trigger a full breakdown only when the user asks for the full explanation, everything, walk me through all of it, or accepts the offer above. Before writing a file, ask **plain text (.txt) or Markdown (.md)** — same convention as `data-scribe`; dont default silently to one.

- If they want the long version **in chat**, use the full structure from `skill-expertise/output_template.md` inline, still ordered by reading priority (marks/KPIs first, then filters, then calc logic, then interactions).
- If they want a **file**, assemble the same template, write it next to the workbook (path from `get-workbook-inventory`), default filename `[sheet-or-dashboard-name]_logic_explainer.md` (or `.txt`), and report the path plus a one-line summary — dont also paste the full content into chat once its saved.

**Never produce the long-form output unprompted.** The chat-brief version is always the first response; length is opt-in.

***

## Workflow

### Phase 0 — Scope
1. Identify the target from context (active sheet/dashboard) or ask if ambiguous which sheet/dashboard.
2. Confirm it exists via `get-workbook-inventory` or `list-worksheets`/`list-dashboards`. **If `get-workbook-inventory` was already called earlier in this session (e.g., by data-scribe or workbook-auditor), reuse its output rather than re-calling — the workbook shape does not change mid-session unless the user has been authoring.**

### Phase 1 — Inventory
For a worksheet: read `get-worksheet-xml` for shelves (Rows/Cols), encodings (color/size/text/detail/tooltip), filters, sorts, mark type. Pull calc formulas for anything calc-backed via `list-available-fields`.

For a dashboard: read `get-dashboard-xml` for zones/member sheets, actions (filter/highlight/parameter/URL), parameters surfaced at the dashboard level, dynamic zone visibility rules. Then run a condensed Phase 1 on each member worksheet: `get-worksheet-xml` for shelves/mark, and `list-available-fields` for every calc-backed field on that sheets shelves — always, not only when `get-worksheet-xml` fails (per Hard Constraint #7 for the failure case specifically).

**Multi-datasource dashboards:** if member sheets pull from more than one datasource, group constructs by source datasource in the inventory and note any cross-datasource actions (parameter or filter actions bridging sheets on different sources) as first-class interactions in Phase 3 — they are the most common source of why isnt this filtering confusion on inherited dashboards.

**Scale bands (worksheet or per-member-sheet):**
- **≤ 10 constructs total** (filters+calcs+LODs+table calcs+params+sets+actions combined): no special handling.
- **11-25 constructs:** group by construct type (Filters / Calcs & LODs / Table Calcs / Parameters & Sets / Actions) in the long-form output; brief mode still caps at 3-6 bullets, prioritizing per the existing order.
- **26+ constructs, or a dashboard with 8+ member sheets:** in brief mode, summarize each member sheets logic in one line rather than a condensed multi-line pass; in long-form, lead with a one-line count-by-type summary before the detail (e.g. 12 filters, 4 LODs, 3 actions) before expanding, same pattern as data-scribes overflow handling.

### Phase 2 — Explain Each Construct
For each filter, calc, LOD, table calc, parameter, set, and action found: check `skill-expertise/construct_pattern_library.md` for a matching shape first (Section A for the chart-shape idiom, Section B for construct mechanics), then write one line of what it is and one line of why its likely there, adapted to this sheets actual fields — never paste a library rationale verbatim. Flag inferences with the three-tier confidence tag per Hard Constraint #3.

**Filter-visibility classification (mandatory).** For every filter narrowing the view, classify it as:
- **Visible** — quick filter card on the sheet or dashboard, parameter control, dashboard filter action target, or legend acting as a filter. Self-disclosing. Note briefly.
- **Hidden** — context filter with no card, data source filter, extract filter, or a True/False calc-based filter with no exposed control. **Every hidden filter MUST be disclosed in the output**, using the filters descriptive name or a legible formula to state what it excludes when possible (hidden filter on `Filter View` restricts to active accounts only). If no hidden filters exist, state that explicitly: no hidden filters — every scope narrowing on this view has a visible control. **Silence on filters reads as nothing is hidden; silence has to be earned by an explicit no-hidden-filters line.**

**Fragility checklist** — a construct qualifies for the brief modes anything unusual or fragile-looking bullet, or the long-form Notable or Fragile Points section, if it matches any of: a filter/action referencing a field not found in the current field inventory; a calc whose formula references another calc that itself doesnt resolve (broken dependency); a circular calc reference; an action targeting a sheet/parameter/set that no longer exists; a Set referenced but not independently verifiable (per Hard Constraint #8). Dont flag something as fragile on a vague feeling — it must match one of these.

### Phase 3 — Trace Interactions (dashboard only)
For each action: source sheet → target (sheet/parameter/set) → what selecting/hovering does → why that connection likely exists (e.g. clicking a region bar filters the detail table below to that region), consulting the Actions and Dynamic Zone Visibility tables in Section B of `skill-expertise/construct_pattern_library.md`.

### Phase 4 — Assemble & Deliver
1. **Pre-delivery validation:** count the constructs identified in Phase 1 and confirm every one appears in the assembled output (as a bullet, a summarized group per the scale bands, or an explicit not extractable note). If any construct was dropped, add it before responding — dont deliver a mismatched count.
2. Default to the brief chat format. Offer long-form only as described in Output Modes. Never ask the file-format question unless the user has already indicated they want a saved file.

***

## Error Handling

| Failure | Recovery |
|---|---|
| `get-workbook-inventory`/`list-worksheets`/`list-dashboards` finds no matching sheet | Tell the user the name wasnt found and list close matches if any. |
| `get-worksheet-xml`/`get-dashboard-xml` fails or times out (generic) | Report the read failure plainly; dont retry blind more than once. |
| `get-worksheet-xml` fails specifically on a dashboards member worksheet | Known reliability gap (populated, dashboard-bound sheets). Fall back to `list-available-fields` formula text plus dashboard-XML hints per Hard Constraint #7; note in the output that shelf/filter detail for that sheet is incomplete. Dont retry more than once. |
| A filter/action appears to reference a Set | Sets are invisible to field-resolution tools. Explain the likely pattern per the library, but state plainly that membership/condition cant be verified from here — never assert it as confirmed. |
| Datasource disconnected mid-workflow | Report the disconnect plainly and pause — do not attempt to explain a partial read as if it were complete. Ask the user to reconnect before continuing. |
| Field-level permission denial (RLS) blocks a field or calc formula | Explain what CAN be seen at the construct level (shelf/encoding position); note that formula/logic detail is unavailable due to row-level security rather than a tool failure. |
| `search-workbook-fields` returns empty for a field a filter or action references | Treat as fragile per Hard Constraint #3 — the referenced field does not resolve. Flag in the fragility section rather than inferring intent as if the field exists. |
| Calc formula missing from `list-available-fields` and XML fallback | Note formula not extractable — logic inferred from usage context only, treat with extra caution. |
| Dashboard has no actions/parameters wired | State plainly that no interactions were found rather than fabricating any. |
| Output path unwritable when a file was requested | Ask the user where to save it, or offer to paste the content in chat instead. |

***

## Composability

- **Upstream:** offer proactively after a dashboard build completes, or when a user opens an unfamiliar/inherited workbook and asks what am I looking at.
- **Downstream:** if the user wants field-level depth beyond construction logic, hand off to `data-scribe`. If they want to know what changed recently, hand off to `workbook-auditor`. If they want to *modify* the logic, hand off to the relevant authoring skill.
- **Adjacent:** `data-scribe` = field meaning, standalone. `workbook-auditor` = change over time. This skill = how the pieces on one sheet/dashboard work together, right now.
- No workbook mutations ever occur in this skill.

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
