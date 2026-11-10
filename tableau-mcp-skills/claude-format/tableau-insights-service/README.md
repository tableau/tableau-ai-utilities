# tableau-insights-service

A Claude skill that steers agents to answer business questions using the **Tableau Insights Service** (Pulse metric insights) before falling back to raw data queries.

## What it does

When a user asks a business question — about metric performance, trends, changes, anomalies, drivers, contribution, goals, forecasts, or KPIs — this skill instructs the agent to reason over Tableau's pre-computed statistical insights for governed metrics rather than querying raw data rows or answering from general knowledge. Raw datasource querying is used only as a fallback when the insights service can't answer.

All tools it relies on are provided by the **tableau-mcp** server, called by their bare names, such as `query-datasource`, with whatever prefix your session shows.

## When it triggers

The skill activates whenever an agent receives a business question about metric performance, trends, changes, anomalies, goals, drivers, or KPIs. See [skill-expertise/question-patterns.md](skill-expertise/question-patterns.md) for the full matrix of answerable patterns and what the service cannot answer.

## What it won't do

It does not trigger for dashboard layout, content discovery (use tableau-content-compass), or designing or auditing Pulse metric definitions (use pulse-blueprint). It never creates or edits Pulse metrics. If `viz-planner` or `worksheet-builder` aren't installed, it gives manual steps in Tableau for any build request.

## How it works

The workflow (defined in [SKILL.md](SKILL.md)) proceeds in five steps (plus a fallback and graceful-degradation rules for failures):

1. **Decide if the insights service applies** — match the question against known answerable patterns.
2. **Find the right metric(s)** — call `list-all-pulse-metric-definitions` and `list-pulse-metric-subscriptions` in parallel; subscribed metrics rank higher.
3. **Assemble full metric context** — fetch metric instances (`list-pulse-metrics-from-metric-definition-id`) and full definitions (`list-pulse-metric-definitions-from-definition-ids`, `DEFINITION_VIEW_FULL`).
4. **Choose the right tool:**
   - One metric, overview or range question → `generate-pulse-metric-value-insight-bundle` (`bundleType: 'detail'`)
   - One metric, "why / what changed / on track" question, or multiple metrics (one call per datasource) → `generate-pulse-insight-brief`; if the brief is empty, errors, or is rejected twice for one metric, try the bundle once, then fall back. Viz-state-only metrics (no `basic_specification`) can't use the bundle.
   - Same-name metrics are disclosed and resolved, or one clarifying question is asked when there is no basis to pick. Overviews with no metric named run a SUMMARIZE brief over up to 5 subscribed metrics.
5. **Present the answer** — lead with the direct answer, then 2–3 supporting signals (range questions use one compact table of completed periods instead of bullets).

**Fallback:** if the insights service can't answer (no matching metric, API error, empty result, or an unsupported question), the agent finds a datasource (`search-content` / `list-datasources`), reads its schema (`get-datasource-metadata`), queries it (`query-datasource`), interprets the results into a narrative answer, and always tells the user it fell back and why.

## Contents

| File | Purpose |
|---|---|
| [SKILL.md](SKILL.md) | The skill definition and step-by-step workflow. |
| [skill-expertise/question-patterns.md](skill-expertise/question-patterns.md) | Answerable question patterns mapped to insight types, plus what the service cannot answer. |
| [skill-expertise/metric-context-mapping.md](skill-expertise/metric-context-mapping.md) | Payload-field → source mapping for building insight requests from the Step 3 responses. |
| [skill-expertise/insight-payloads.md](skill-expertise/insight-payloads.md) | Request payload shapes for both insight tools and how to compute `now`. |

## Notes

- Insight calls take **5–25 seconds** — this latency is expected; do not retry immediately.
- Never call `generate-pulse-insight-brief` without a populated `metric_group_context`.
- Never call `generate-pulse-metric-value-insight-bundle` without the full `DEFINITION_VIEW_FULL` definition.
