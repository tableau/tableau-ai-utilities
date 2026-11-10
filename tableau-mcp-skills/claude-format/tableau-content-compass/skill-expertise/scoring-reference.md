# Scoring Reference

Signal weights table used to score content relevance from 0 to 100.

| Signal | Weight | Description |
|---|---|---|
| **Name match (word boundary)** | +30 | View/workbook/datasource name contains a search term at a word boundary (case-insensitive). "Sales" matches "Regional Sales Report" but NOT "Wholesale Tracker." |
| **Name match (substring only)** | +15 | Name contains the term as a substring but not at word boundary. "sale" inside "Wholesale" scores here, not at +30. |
| **Name match (synonym)** | +15 | Name contains a synonym or related concept from the synonym table. |
| **Field match (exact)** | +25 | Datasource fields include exact terms from the query (e.g., "Region", "Sales") |
| **Field match (implied)** | +15 | Fields match implied measures/dimensions (e.g., query mentions "revenue" and field is "Sales Amount") |
| **Description match** | +20 | Content description references the topic |
| **Tag match** | +10 | Tags contain relevant terms |
| **Pulse metric match** | +20 | Metric name/definition matches the query concept |
| **Temporal capability** | +10 | Has date fields when user's query implies time analysis |
| **Usage signal (top quartile)** | +5 | Usage count (`hitsTotal`, or `usage.totalViewCount` if that is what the tool returns) is in the top 25% of the items in this search's candidate set for the same project. If no usage count is returned, skip this signal. |
| **Recency signal** | +5 | Updated within the last 90 days |

**Rules:**
- The name signal is awarded once per item, using the best match across all query terms.
- A field signal is awarded once per signal row. List every matched field as evidence; points are not multiplied by field count.
- Name (word boundary, +30) plus exact field (+25) is 55, which is Medium. High (60+) needs at least one more signal.
- Views-only searches skip field signals; High is still reachable through name, description, tag, usage, and recency (maximum without fields is 70).
