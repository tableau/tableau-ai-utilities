# API Enum Reference

Exact Tableau Pulse API enum values to use in all blueprints, recommendations, and audit checks.

**Insight Types:**
- `INSIGHT_TYPE_CURRENT_TREND`
- `INSIGHT_TYPE_NEW_TREND`
- `INSIGHT_TYPE_TOP_DRIVERS`
- `INSIGHT_TYPE_TOP_DETRACTORS`
- `INSIGHT_TYPE_BOTTOM_CONTRIBUTORS`
- `INSIGHT_TYPE_RISKY_MONOPOLY`
- `INSIGHT_TYPE_UNUSUAL_CHANGE`
- `INSIGHT_TYPE_RECORD_LEVEL_OUTLIERS`

**Granularities:**
- `GRANULARITY_BY_DAY`
- `GRANULARITY_BY_WEEK`
- `GRANULARITY_BY_MONTH`
- `GRANULARITY_BY_QUARTER`
- `GRANULARITY_BY_YEAR`
- `GRANULARITY_BY_FISCAL_QUARTER`
- `GRANULARITY_BY_FISCAL_YEAR`

**Comparison Types:**
- `TIME_COMPARISON_PREVIOUS_PERIOD`
- `TIME_COMPARISON_YEAR_AGO_PERIOD`
- `TIME_COMPARISON_FISCAL_YEAR_AGO_PERIOD`

**Sentiment Types:**
- `SENTIMENT_TYPE_UP_IS_GOOD`
- `SENTIMENT_TYPE_DOWN_IS_GOOD`
- `SENTIMENT_TYPE_NONE`

**Number Format Types:**
- `NUMBER_FORMAT_TYPE_NUMBER`
- `NUMBER_FORMAT_TYPE_CURRENCY`
- `NUMBER_FORMAT_TYPE_PERCENT`

**Currency Codes (common):**
- `CURRENCY_CODE_USD`, `CURRENCY_CODE_EUR`, `CURRENCY_CODE_GBP`, `CURRENCY_CODE_JPY`
- `CURRENCY_CODE_UNSPECIFIED` (flag as issue in audit)

**Measurement Period Range:**
- `RANGE_LAST_COMPLETE`
- `RANGE_CURRENT_PARTIAL`

**Row-Level Fields:**
- `row_level_id_field` (identifier column)
- `row_level_name_field` (display name column)
- `row_level_entity_names` (singular_noun, plural_noun)

**Not enum-verified (label as plain-language suggestions, not API values):**
- Aggregation names (SUM, COUNT, COUNTD, AVG)
- Goal/benchmark direction (above or below target)
