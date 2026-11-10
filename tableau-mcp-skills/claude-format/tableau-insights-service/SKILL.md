---
name: tableau-insights-service
description: Use for business questions about metric performance, trends, changes, anomalies, drivers, goals, forecasts, or KPIs, such as 'why did X change', 'how is X trending', 'are we on track', 'what changed', 'summarize my metrics', 'how are we doing'. Try the Tableau insights service tools first, then fall back to a datasource query only when no metric fits. Do NOT trigger for workbook/dashboard layout or formatting, content-catalog navigation (use tableau-content-compass), designing or auditing Pulse metric definitions (use pulse-blueprint), or requests already scoped to raw row-level or ad-hoc SQL-style data pulls from a specific datasource (go straight to the datasource query path).
---

# Answering Business Questions with the Tableau Insights Service

When a user asks a business question — anything about metric performance, trends, changes, anomalies, goals, drivers, or KPIs — **always attempt the insights service first**. Only fall back to raw data queries or general answers if the insights service cannot answer it.

All tools named below are provided by the tableau-mcp server (tool names are written bare below, such as `query-datasource`; call them with whatever server prefix your session shows). Call them directly; never ask the user to run a tool. Never narrate the steps you're about to take — just take them.

## Step 1: Decide if the insights service applies

Insights service tools reason over pre-computed statistical insights for governed metrics — they do not query raw data rows. If the question is about metric performance, trends, changes, anomalies, drivers, contribution, goals, forecasts, or KPIs, the service can likely answer it.

"Always attempt the insights service first" means: for any *analytical* business question, try the service before raw queries or general answers. It does **not** apply to requests already scoped to a specific datasource or asking for raw/ad-hoc/SQL-style row pulls — those go straight to the datasource-query path (Fallback), skipping metric resolution entirely.

For the full matrix of answerable question patterns (and their insight types) plus what the service **cannot** answer, see `skill-expertise/question-patterns.md`. If the question clearly doesn't fit any answerable pattern, skip to **Fallback**.

## Step 2: Find the right metric(s)

In parallel, call `list-all-pulse-metric-definitions` (with `view: "DEFINITION_VIEW_BASIC"`) and `list-pulse-metric-subscriptions`. Subscriptions return metric IDs, so resolve them to definitions with `list-pulse-metrics-from-metric-ids` before ranking. On sites with many definitions, page through with `limit`/`pageSize` rather than assuming one call returns everything.

Rank candidates deterministically so two sessions pick the same metric(s):
1. A definition is a **candidate** if a *significant token* from the question appears in its name or description. A significant token is any noun or noun-phrase naming the measure, KPI, business subject, or entity being asked about — after dropping stopwords and generic analysis verbs ("show", "trend", "why", "change", "top", "compare", "how", "what"). Match case-insensitively on whole words/stems, not substrings.
2. Subscribed metrics (those in `list-pulse-metric-subscriptions`) outrank unsubscribed ones — they're what the user actively tracks.
3. Break remaining ties by strongest name/description token overlap with the question.

Count how many distinct metrics clear step 1 — this determines the tool path in Step 4. If none clears it, or two or more are tied at the top with no subscription to break the tie, ask ONE question — "Which metric are you asking about?" — and show the top 3–5 candidate names. If there are no candidates at all, skip the question and go to **Fallback**, whose first step asks the datasource question if nothing is found. This is the same single question everywhere: never ask both.

**Overview with no metric named** ("how are we doing?", "what should I focus on?"): if the user has subscriptions, skip the question and run `generate-pulse-insight-brief` with `ACTION_TYPE_SUMMARIZE` over the subscribed metrics, grouped by datasource (Step 4). If there are no subscriptions, go to Fallback. Cap the overview at the 5 most recently changed or most-tracked subscribed metrics, and say you limited it.

### Disambiguation — disclose-and-proceed (before Step 3)

When two or more candidates share the *same* display name, or otherwise tie (a tie with no subscription and no scope basis falls under "no basis" below, so the Step 2 question applies), resolve it as follows:

- **If you have a basis to pick** — one candidate has data for the period/scope the question needs and the others don't, one matches the question's scope more closely, or a subscription favors one — **pick that one and proceed, but you MUST disclose the collision in your answer**: name the metric you used, note that a same-named (or closely-matching) metric also exists with one distinguishing detail (datasource, owner, or description), and invite the user to redirect you if they meant the other. Example: *"I used ACE Current Security Defects on the daily work-history source; a same-named metric also exists on the live GUS-Work source — tell me if you meant that one."*
- **If you have NO basis to pick** — the same-named candidates are genuinely indistinguishable for this question (e.g. all return comparable data, none matches the scope better) — ask ONE clarifying question listing 3–5 candidates by display name, each with a distinguishing detail. Never raw IDs.

**Never fabricate a user decision.** Do not write "the one you ruled out," "the one you picked," or any phrasing that attributes a choice to the user that they did not explicitly make. If *you* narrowed the set, say so in your own voice ("I used…"), and always leave the door open to switch.

An explicit metric-definition **ID** supplied upstream (see Composability) resolves the collision outright — use it and skip this step. A metric merely mentioned earlier by *name* does NOT resolve a same-name collision; disclose it every time you answer.

## Step 3: Assemble full metric context

For each relevant definition, call both in parallel:
1. `list-pulse-metrics-from-metric-definition-id` (parameter `pulseMetricDefinitionID`) → metric instances, each with `id`, `specification.measurement_period`, `specification.filters`, `specification.comparison`, and `goals`. **Pick one instance per definition:** the one the user is subscribed to; otherwise the default instance (no filters). Disclose the choice in the caveat line when other instances exist.
2. `list-pulse-metric-definitions-from-definition-ids` (parameters `metricDefinitionIds` as an array, and `view: "DEFINITION_VIEW_FULL"`) → the full definition

**Everything needed to construct the insight payload comes from these two responses — no separate datasource lookup is required.** For the payload-field → source mapping, see `skill-expertise/metric-context-mapping.md`.

Prefer metrics that share the same datasource — cross-datasource analysis is possible but produces weaker results. Never skip this step; incomplete definitions produce poor results from both insight tools.

## Step 4: Choose the right tool

Decide deterministically:

- **Multiple metrics** (question spans two or more, compares metrics, follows up on a brief, or is an overview over subscriptions) → `generate-pulse-insight-brief`. **Group metrics by datasource and make one call per datasource**, then combine the answers; note when metrics from different datasources were answered separately.
- **One metric, question starts with why / what changed / are we on track / should I** → `generate-pulse-insight-brief`.
- **One metric, overview / "tell me about" / range or time-series question / a specific insight type** → `generate-pulse-metric-value-insight-bundle` with `bundleType: 'detail'` (performance over time, trend summary, top contributors per dimension, followup insights).
- **If the brief is empty, errors, or is rejected twice for a single-metric question**, call the `detail` bundle once (only if the definition has a `basic_specification`), then go to the datasource-query Fallback. **Multi-metric** brief failures go straight to Fallback; a partial brief is presented as covered, with omitted metrics named (see Error handling).

Build the request payloads, infer `action_type`, and compute `now` per `skill-expertise/insight-payloads.md`. Never call `generate-pulse-insight-brief` without a populated `metric_group_context`, and never call `generate-pulse-metric-value-insight-bundle` without the full `DEFINITION_VIEW_FULL` definition. **Pre-flight, before every call:** `allowed_dimensions` and `insights_options.settings` are non-empty; no `now` on a bundle; `metric_group_context` is non-empty on a brief; every message carries its required fields. Latency is 5–25 seconds for both insight calls — this is expected; do not fire a duplicate call while one is in flight.

**Viz-state-only metrics can't use the detail bundle.** If the definition has no `basic_specification` (it's defined from a viz/viz-state rather than a basic measure+time dimension), the `detail` bundle is not constructible — its schema requires a `basic_specification`. For such a metric the brief→bundle fallback does not apply: if the brief is unavailable, skip straight to the datasource-query Fallback. Do not attempt a bundle call you can't populate.

## Step 5: Present the answer

**Before presenting, run this audit — all four must pass, or go to Fallback:**
1. **Non-empty:** the response contains at least one insight/answer, not an empty or error payload.
2. **On-topic:** it addresses the metric(s) and dimension the user actually asked about, not a different one.
3. **Traceable:** every claim you present maps to a value or insight in the response — do not fill gaps with outside knowledge or invented numbers.
4. **Complete:** for a multi-metric brief, confirm the answer covers each metric you sent in `metric_group_context`; if one is missing, say so rather than implying full coverage.

If check 1, 2 or 3 fails, treat it as an insights-service miss and follow the Step 4 failure routing, ending in **Fallback**. If only check 4 fails (partial multi-metric coverage), present the covered metrics, name the omitted ones, and offer to query them separately; use Fallback only for zero coverage. Never present an off-topic or empty insight as if it were the whole answer. Never surface raw HTML, tool names, definition/metric IDs, or payload internals to the user.

- **Bundle responses:** parse the HTML insight groups and surface sections in this priority order, stopping once you have a direct answer plus 2–3 supporting signals: (1) the insight group that directly answers the question's intent (e.g. drivers for a "why" question, pace/forecast for a "goal" question); (2) the current-value/trend summary; (3) top contributors/detractors; (4) unexpected values or trend-change alerts. Lead with the direct answer, then list 2–3 supporting signals as bullets.
- **Range / time-series questions ("this year", "monthly/quarterly over time", "trend by month", "each week since…"):** the answer is the metric's **performance-over-time series**, not the current-vs-prior comparison. Read that series first — do **not** anchor the headline on the current-period or MTD comparison, which reports only the latest (often partial) period and under-answers the range question. **Exclude or explicitly label the partial current period** (a month/quarter/week still in progress is not comparable to completed ones); report the completed periods as the series and note the partial one separately. Deliver the full requested range in one pass — don't return a truncated series and wait to be asked again. **Render the series as one compact table of completed periods (period, value, change) in place of the signal bullets**, keep the bold lead line, and put the partial period on the caveat line.
- **Brief responses:** return the answer from `brief_text` or `answer`. If source insights are present, list the top 2–3 supporting signals as bullets below.
- **Multi-turn follow-up (brief only):** carry the previous answer as `ROLE_ASSISTANT` in `messages` before the new `ROLE_USER` turn (every message, including the assistant turn, carries `action_type`, `metric_group_context` and `metric_group_context_resolved`), and reuse `metric_group_context` — don't re-fetch unless the user asks about different metrics.

Render every answer to this skeleton so output is consistent across sessions:

```
**<direct answer to the question, one or two sentences, with the key number>**

- <supporting signal 1 — a metric value, trend, driver, or contributor from the response>
- <supporting signal 2>
- <supporting signal 3 — optional>

<optional one-line caveat: goal missing, cross-datasource comparison, dimension not available, or fallback disclosure>
```

This skeleton is mandatory, not illustrative — it is the hand-off surface downstream skills depend on (see Composability). Enforce it literally:

- **The lead line MUST be bold** (`**…**`) and MUST be the direct answer with the key number — never open with preamble, a restated question, or an unbolded sentence.
- **Maximum 3 signal bullets.** Drop the third if it's weak; never pad to three, and never exceed three.
- **The caveat is its own line, never a bullet.** Include it only when one applies (goal missing, cross-datasource, dimension unavailable, fallback disclosure); omit it otherwise. Do not fold it into the bullet list.
- Metric names in prose use the definition's display name, never its ID.

A correct rendering looks exactly like this (note the bold lead line and the caveat set apart from the bullets):

```
**Bug Cases fell 7.7% to 48 for the week of Sep 13 — a normal move, well within its expected range.**

- Down-trending since mid-2025 (low volatility); since lower is better, that's the healthy direction.
- The dip is mostly fewer Closed-Resolved cases (−10) and Core-product cases (−8).

The monthly Pulse tile may look like a cliff drop — that's the current partial period, not a real decline.
```

**STOP — output gate. Before you send any answer, verify all four; if any fails, reformat before sending:**
1. Is the **first line bold** (`**…**`) and the direct answer with the key number? (Not a plain sentence, not preamble.)
2. Are there **3 or fewer** bullets?
3. Is the caveat (if any) on **its own line**, not a bullet?
4. Are there **no** tool names, HTML, or definition/metric IDs, with metrics named by display name?

Do not emit the answer until all four are yes. This gate applies to every answer regardless of length — a "quick read" is still bold-lead + ≤3 bullets.

## Fallback: when the insights service can't answer

If insights service tools fail (no matching metric, API error, empty result) or the question clearly doesn't match an answerable pattern, fall through this chain, then always tell the user you fell back and why.

0. **If a definition matched but the insight failed**, use that definition's own `datasource.id` as the datasource and skip to step 2. If its `id_type` is `DATASOURCE_ID_TYPE_WORKBOOK_DATASOURCE` (embedded), also pass the workbook LUID as `workbookLuid` to `get-datasource-metadata` and `query-datasource`. A brief cannot carry `id_type`, so route embedded-datasource metrics to the bundle.
1. **Find a datasource** — call `search-content` with terms from the question, or `list-datasources` and scan names/descriptions. Pick the most relevant published datasource. If nothing matches, ask ONE question: "I couldn't find an insights service metric for that. Do you know which datasource or workbook contains this data?"
2. **Understand the schema** — call `get-datasource-metadata` with the datasource LUID to retrieve its fields, dimensions, and measures. Use the actual field names; never guess them.
3. **Query the datasource** — call `query-datasource` with `{datasourceLuid, query: {fields: [{fieldCaption, function?}], filters?}, limit}`, translating the business question into aggregation, filters, and grouping using the field names from the metadata. Aggregate; never pull raw rows.
4. **Interpret and answer** — reason over the results into a narrative answer (as an insight brief would); don't just return raw rows.

> "No insights service metric was found for that subject, so I queried the [datasource name] datasource directly."

## Error handling

Recover per failure mode rather than retrying blindly:

| Failure | What you'll see | Recovery |
|---|---|---|
| Payload rejected (schema/validation error) | Tool returns a validation error naming a field | Re-map the offending field per `skill-expertise/metric-context-mapping.md` and check for the known traps in `skill-expertise/insight-payloads.md` (no `now` on the bundle; non-empty `allowed_dimensions`/`insights_options.settings`; correct `id_type`, which applies to the bundle only — a brief datasource carries only `id`). Fix and call once more; if it rejects again, follow the Step 4 failure routing. |
| Empty or error insight result | Success response but no insights, or an API error body | Do not present it. Single metric: try the `detail` bundle once if a `basic_specification` exists, then Fallback. Multiple metrics: Fallback. Tell the user. |
| Partial multi-metric result | Brief covers some but not all metrics in `metric_group_context` | Partial brief: present covered metrics, name omitted ones, and offer to query them separately. Use Fallback only for zero coverage. |
| No metric matches (Step 2) | No definition clears the candidate rule | Go to Fallback; its first step asks the one datasource question if nothing is found. Ask "Which metric…?" only when candidates tie. |
| List/definition call fails | `list-*` tool errors or times out | Retry that single call once; if it still fails, proceed with whatever metrics did resolve, or go to Fallback if none did. |
| Timeout / no response in ~25s | Call hangs past the expected latency window | Do not fire a duplicate call. Wait; if it ultimately errors, treat as empty result above. |
| Permission / RLS denial (fallback path) | `query-datasource` or `get-datasource-metadata` returns an authorization/row-level-security error | Do not retry the same query. Tell the user they lack access to that datasource or the specific fields, and ask if there's another datasource they can use. |
| Datasource disconnected / unreachable (fallback path) | `query-datasource`/`get-datasource-metadata` returns a connection or extract-refresh error | Report that the datasource is currently unavailable; suggest retrying later or naming an alternate datasource. Do not fabricate an answer. |
| Insights feature not enabled on site | Brief or bundle returns "AI-powered Pulse insights are not enabled … requires Tableau+" | Permanent site-level failure — do not retry. For a single-metric question, use the `detail` bundle instead of the brief; if that also fails, go to Fallback and tell the user the insights feature isn't enabled on their Tableau site. |

## Common mistakes (do not do these)

- **Fabricating findings.** Never invent numbers, trends, or drivers the insight response didn't return. If the data isn't there, say so or fall back.
- **Answering from general knowledge** when the insights service returned nothing — that's a Fallback trigger, not a license to guess.
- **Leaking internals.** No raw HTML, tool names, template shapes, or definition/metric IDs in the user-facing answer.
- **Skipping Step 3.** Incomplete definitions silently degrade both insight tools.
- **Adding `now` to a bundle request** — it's brief-only (see `skill-expertise/insight-payloads.md`).
- **Retrying a slow insight call.** 5–25s latency is expected; a duplicate call just doubles the wait.
- **Treating an empty or off-topic response as the answer** — it must clear the Step 5 audit first.
- **Anchoring a range question on the current period.** For a "this year" / "over time" / "by month" question, lead with the performance-over-time series and label the partial current period — don't headline the latest (partial) period and force a second ask for the full series.
- **Absorbing authoring work.** If a request combines an insights question with a build/rebuild ask, answer the insights part and hand the authoring to `viz-planner` / `worksheet-builder` by name. If those skills aren't installed, say so and give the manual steps in Tableau instead. Do not attempt the build yourself, and do not silently drop it.

## Composability

This skill is designed to chain with other skills and workflows:

- **Read-only, no collisions.** It creates no Tableau objects (no worksheets, calcs, or datasources), so it never conflicts with authoring skills running before or after it. The fallback's `query-datasource` reads only.
- **Stable output contract.** The Step 5 skeleton (bold answer line → signal bullets → optional caveat) is the hand-off surface. A downstream skill (e.g. a report-builder or Slack-summarizer) can consume the answer line as the headline and the bullets as evidence without re-parsing tool output.
- **Composes after selection skills.** If an upstream step has already resolved a specific metric definition ID, skip Step 2's ranking and pass that ID straight into Step 3.
- **Hands off on miss.** When the insights service can't answer, this skill degrades to the datasource-query path itself rather than failing — but if a dedicated data-query skill is present, defer to it at the Fallback boundary instead of duplicating that work.
- **Hands off authoring.** If a request also asks to build or rebuild a worksheet or dashboard, do the insights part and hand the authoring off by name to `viz-planner` (dashboards) or `worksheet-builder` (single sheets). If neither is installed, say so and give the manual steps in Tableau instead; the handoff is never the only next step. This skill never creates Tableau objects.
- **Metric-definition changes are out of scope.** If a request asks to create, edit, or fix a *Pulse metric definition* itself, decline: this skill is read-only. For design or audit of definitions, hand off to `pulse-blueprint` if installed; creation and edits happen in Tableau Pulse directly. For finding existing content on the site, hand off to `tableau-content-compass` if installed. Answer any insights part of the request first, then state the definition change is out of scope.

## Graceful Degradation

These rules apply whenever something this skill needs is missing or fails. The Error handling table, Fallback chain and Step 5 audit are the specific rules for tool failures, empty results, partial briefs and missing peer skills, and they take precedence. The rules below cover what those do not.

- **Reference file won't open.** Use the rules summarized in this file, say [file] unavailable; using the built-in summary, and never make up thresholds, field names, or patterns from memory.
- **Platform gap.** If no tool can do something, say so plainly and give the manual path in Tableau.
- **Failure messages.** Tell the user in plain language what was done, what wasn't, and the next step. No raw errors, stack traces, or JSON.
- **No fabrication.** Never invent fields, values, findings, or results to fill a gap left by a failed read.
