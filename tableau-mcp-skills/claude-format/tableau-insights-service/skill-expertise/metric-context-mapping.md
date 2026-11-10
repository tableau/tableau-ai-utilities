# Metric Context: Payload-Field → Source Mapping

Everything needed to construct an insight payload comes from the two Step 3 responses:

- `list-pulse-metrics-from-metric-definition-id` → **metric instance** (`metric`)
- `list-pulse-metric-definitions-from-definition-ids` with `view: "DEFINITION_VIEW_FULL"` → **full definition** (`definition`)

No separate datasource lookup is required.

| Payload field | Source |
|---|---|
| `datasource.id` | `definition.specification.datasource.id` |
| `basic_specification.measure.field` | `definition.specification.basic_specification.measure.field` |
| `basic_specification.measure.aggregation` | `definition.specification.basic_specification.measure.aggregation` |
| `basic_specification.time_dimension.field` | `definition.specification.basic_specification.time_dimension.field` |
| `basic_specification.filters` | `definition.specification.basic_specification.filters` |
| `is_running_total` | `definition.specification.is_running_total` |
| `metric_specification` | `metric.specification` (measurement_period, filters, comparison) |
| `extension_options` | `definition.extension_options` |
| `representation_options` | `definition.representation_options` |
| `insights_options` | `definition.insights_options` |
| `metadata.name` | `definition.metadata.name` |
| `metadata.metric_id` | `metric.id` |
| `metadata.definition_id` | `definition.metadata.id` |
| `goals` | `metric.goals` (optional) |

**`goals` shape differs by tool.** The bundle (`generate-pulse-metric-value-insight-bundle`) expects a simple `goals: { target: { value } }`. The brief (`generate-pulse-insight-brief`) expects the richer `metric.goals` structure (`datasource_goals[]` and/or `metric_goals.target.value`). When building a bundle payload, reduce the instance's goal to `target.value`; when building a brief payload, pass the goal structure through as-is. Omit `goals` entirely if the metric has none.
