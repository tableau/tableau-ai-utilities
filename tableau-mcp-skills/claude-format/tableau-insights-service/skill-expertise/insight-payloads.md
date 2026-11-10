# Insight Request Payloads

Field values are sourced per `metric-context-mapping.md`.

## Computing `now` (brief only)

`now` is a field on `generate-pulse-insight-brief` **only** — the bundle request's `options` object rejects it (`additionalProperties: false`, no `now` field), so never add `now` to a bundle request.

To compute it for the brief: `now` = today minus the largest `offset_from_today` across the metrics' `extension_options` (use 0 if absent), formatted `YYYY-MM-DD`.

## Single metric — `generate-pulse-metric-value-insight-bundle`

Do **not** include a `now` field anywhere in this request. Populate `extension_options.allowed_dimensions`/`allowed_granularities` and `insights_options.settings` from the full definition — empty arrays here cause API errors even though they pass schema validation. If the metric is based on an embedded workbook datasource rather than a published one, add `id_type: 'DATASOURCE_ID_TYPE_WORKBOOK_DATASOURCE'` under `definition.datasource`. `id_type` is bundle-only: a brief's `datasource` allows only `id`, so route embedded-datasource metrics to the bundle.

```
bundleRequest:
  bundle_request:
    version: 1
    options:
      output_format: 'OUTPUT_FORMAT_HTML'
      time_zone: 'UTC'
      language: 'LANGUAGE_EN_US'
      locale: 'LOCALE_EN_US'
    input:
      metadata:
        name: <metric definition name>
        metric_id: <metric instance ID>
        definition_id: <metric definition ID>
      metric:
        definition: <from specification in full definition; must include datasource, basic_specification, is_running_total>
        metric_specification: <from metric instance>
        extension_options: <from full definition>
        representation_options: <from full definition>
        insights_options: <from full definition>
        goals: <from metric instance goals, if any; bundle takes goals.target.value>
bundleType: 'detail'
```

## Multiple metrics — `generate-pulse-insight-brief`

Build `metric_group_context` by pairing each metric instance with its full definition. Infer `action_type` from the question:

| Question intent | `action_type` |
|---|---|
| "why / what caused / what changed / what's driving / what are the top" | `ACTION_TYPE_ANSWER` |
| "should I / advise / what are the risks / are we on track / forecast" | `ACTION_TYPE_ADVISE` |
| "summarize / what is / what's happening / overview / how are we doing / what should I focus on (with no metric named)" | `ACTION_TYPE_SUMMARIZE` |

For compound questions, use `ACTION_TYPE_ADVISE` — it covers the broadest scope. Overviews over subscribed metrics use `ACTION_TYPE_SUMMARIZE`; use `ADVISE` only when the user asks what to do.

```
briefRequest:
  language: LANGUAGE_EN_US
  locale: LOCALE_EN_US
  now: <computed above>
  messages:
    - role: ROLE_USER
      action_type: <inferred above>
      content: <user's original question, verbatim>
      metric_group_context_resolved: true
      metric_group_context: <assembled from Step 3, one entry per metric>
```

Each `metric_group_context` entry nests like this:

```
- metadata: { name, metric_id, definition_id }
  metric:
    definition: { datasource, basic_specification, is_running_total }
    metric_specification: <from metric instance>
    extension_options: <from full definition>
    representation_options: <from full definition>
    insights_options: <from full definition>
    goals: { metric_goals: { target: { value } }, datasource_goals: [...] }
    # datasource_goals entries require minimum_granularity, benchmark_sentiment_type and name; pass them through as returned, never rebuild them
    # viz-state-only metrics (no basic_specification) cannot use the bundle
```

Group metrics by datasource and send one brief per datasource.

Do not call this tool without a populated `metric_group_context`.

For multi-turn follow-up, carry the previous answer as a `ROLE_ASSISTANT` message before the new `ROLE_USER` turn, and reuse `metric_group_context`. Every message, including the `ROLE_ASSISTANT` one, must carry `action_type`, `content`, `metric_group_context` and `metric_group_context_resolved`, or validation fails.
