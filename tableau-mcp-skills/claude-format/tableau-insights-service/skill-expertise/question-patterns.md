# Insights Service: Answerable Question Patterns

The insights service reasons over pre-computed statistical insights for governed metrics — it does not query raw data rows.

## Can answer

| Question pattern | Insight type(s) involved |
|---|---|
| "What's happening with [metric]?" / "Summarize [metric]" | Current Trend, Unexpected Values |
| "Why did [metric] go up/down?" / "What's driving [metric]?" | Top Drivers, Top Detractors, Top Contributors |
| "What changed most?" / "What's unusual?" / "Any anomalies?" | Unexpected Values, Trend Change Alert |
| "Which [dimension] is highest/lowest?" | Top Contributors, Bottom Contributors |
| "Which [dimension] is concentrated / dominating?" | Concentrated Contribution Alert |
| "Is there a trend?" / "What's the trend direction?" | Current Trend, Trend Change Alert |
| "Are we on track to hit goal?" / "Pace to goal?" | Pace to Goal, Forecast |
| "What's the forecast for [metric]?" | Forecast |
| "How does [metric] compare to a threshold or goal?" | Goal and Threshold Breakdown |
| "Which records or transactions are outliers?" | Record-Level Outliers |
| "Is [metric A] correlated with [metric B]?" | Correlated Metrics |
| "Tell me about [metric]" / "Give me an overview" / "What should I focus on?" | All of the above combined |

## Cannot answer

- Questions requiring custom SQL or arbitrary data slices not modeled as metrics
- Questions about data with no corresponding metric definition on the site
- Questions about workbook layout, viz formatting, or content catalog navigation
- Real-time streaming data or data below the metric's configured granularity

## Edge cases (handle, don't silently fail)

- **Metric has no goals** — pace-to-goal / on-track / threshold questions can't be answered for it. Say the metric has no goal configured and offer trend/forecast instead; omit `goals` from the payload.
- **Cross-datasource multi-metric** — the brief accepts metrics from different datasources but produces weaker, less-comparable results. Prefer grouping by datasource and making one call per datasource; if the user insists on comparing across, proceed but flag the reduced reliability.
- **Dimension asked about isn't in `allowed_dimensions`** — the service can't break down by it. Answer at the metric level and note the requested breakdown isn't available for this metric.
- **Granularity below the metric's configured level** (e.g. hourly on a daily metric) — out of scope; answer at the metric's granularity and say so.
