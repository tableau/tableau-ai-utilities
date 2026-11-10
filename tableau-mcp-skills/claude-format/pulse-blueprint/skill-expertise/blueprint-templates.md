# Blueprint and Recommendation Templates

Output templates for the Pulse Metric Blueprint and the Recommended Pulse Metrics list.

## Pulse Metric Blueprint Template

```
## Pulse Metric Blueprint: [Metric Name]

### Definition Spec

| Property | Value |
|----------|-------|
| Name | [Clear, concise metric name] |
| Description | [1-2 sentences explaining what this measures and why] |
| Datasource | [Name] (LUID: [id]) |
| Measure | [Field name] |
| Aggregation | [SUM / COUNT / COUNTD / AVG, plain names; confirm in the Pulse UI] |
| Time Dimension | [Field name] |
| Is Running Total | [true/false] |
| Filters (definition-level) | [Any fixed filters, or "None"] |

### Configuration Spec

| Property | Value |
|----------|-------|
| Allowed Granularities | [e.g., GRANULARITY_BY_WEEK, GRANULARITY_BY_MONTH, GRANULARITY_BY_QUARTER] |
| Allowed Dimensions | [List of 5-10 field names; mark any "cardinality unverified"] |
| Sentiment | [SENTIMENT_TYPE_UP_IS_GOOD / SENTIMENT_TYPE_DOWN_IS_GOOD / SENTIMENT_TYPE_NONE] |
| Number Format | [NUMBER_FORMAT_TYPE_NUMBER / NUMBER_FORMAT_TYPE_CURRENCY / NUMBER_FORMAT_TYPE_PERCENT] |
| Currency Code | [CURRENCY_CODE_USD / etc., or N/A] |
| Comparisons | [TIME_COMPARISON_PREVIOUS_PERIOD, TIME_COMPARISON_YEAR_AGO_PERIOD] |

### Insight Settings

| Insight Type | Enabled | Why |
|-------------|---------|-----|
| INSIGHT_TYPE_CURRENT_TREND | Yes | [reason] |
| INSIGHT_TYPE_NEW_TREND | Yes | [reason] |
| INSIGHT_TYPE_TOP_DRIVERS | Yes | [reason] |
| INSIGHT_TYPE_TOP_DETRACTORS | Yes | [reason] |
| INSIGHT_TYPE_BOTTOM_CONTRIBUTORS | [Yes/No] | [reason] |
| INSIGHT_TYPE_RISKY_MONOPOLY | [Yes/No] | [reason] |
| INSIGHT_TYPE_UNUSUAL_CHANGE | [Yes/No] | [reason] |
| INSIGHT_TYPE_RECORD_LEVEL_OUTLIERS | [Yes/No] | [reason -- requires row-level fields] |

### Suggested Filtered Metrics

| Metric Name | Filter | Granularity | Range | Use Case |
|-------------|--------|-------------|-------|----------|
| [Name] - [Segment] | [Field] = [Value] | GRANULARITY_BY_MONTH | RANGE_LAST_COMPLETE | [Who uses this view] |
| [Name] - [Region] | [Field] = [Value] | GRANULARITY_BY_WEEK | RANGE_CURRENT_PARTIAL | [Who uses this view] |

### Row-Level Settings (if applicable)

| Property | Value |
|----------|-------|
| row_level_id_field | [Field that uniquely identifies a record] |
| row_level_name_field | [Human-readable label field] |
| Entity Singular | [e.g., "Deal", "Customer", "Campaign"] |
| Entity Plural | [e.g., "Deals", "Customers", "Campaigns"] |

### Goals (if applicable)

| Property | Value |
|----------|-------|
| Target Value | [number or "Recommend user defines based on historical baseline"] |
| Benchmark Sentiment | [Plain words: above target is good / below target is good / none; confirm in the Pulse UI] |
```

## Recommended Pulse Metrics Template

```
## Recommended Pulse Metrics for [Datasource Name]

### Priority 1: [Metric Name]
[One-line description of business value]
- Measure: [field] ([aggregation])
- Time Dimension: [field]
- Key Dimensions: [top 3-5]
- Sentiment: [SENTIMENT_TYPE_UP_IS_GOOD / DOWN_IS_GOOD]
- Filtered view idea: [one segment worth its own filtered metric, or "None"]
- Why first: [reasoning -- highest business impact, most complete data, etc.]

### Priority 2: [Metric Name]
...

### Not Recommended (and why)
- [Field that looks like a metric but isn't a good fit]: [reason]
```
