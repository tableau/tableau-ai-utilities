# Audit and Optimization Templates

Output templates for the Pulse Metric Audit report and the Optimization report.

## Pulse Metric Audit Report Template

```
## Pulse Metric Audit -- [N] definitions reviewed

### [GRADE] -- [SCORE]/100
> [One-line verdict]

| Definition | Score | Grade | Issues |
|-----------|-------|-------|--------|
| [Name] | [score] | [grade] | [count] |

### Delta (vs. last audit)
[If cache exists: "+2.5 pts from last audit (was C+, now B-). Improved: [x]. Degraded: [y]."]

### Top Issues

[HIGH] "[Definition Name]" -- [Issue]
  Impact: [why this matters]
  Fix: [exactly what to change in Tableau Pulse UI]

### Quick Wins
1. [Action] -- [effort estimate]
```

## Optimization Report Template

```
## Optimization: [Metric Definition Name]

### Current Configuration
[Summary table of what's set now]

### Recommended Changes

| Change | Current | Recommended | Impact |
|--------|---------|-------------|--------|
| Add dimension | [not in allowed_dimensions] | "[Field Name]" | Enables breakdown by [business concept] |
| Enable insight | INSIGHT_TYPE_UNUSUAL_CHANGE disabled | Enable | Catches anomalies early |
| Add granularity | GRANULARITY_BY_MONTH only | + GRANULARITY_BY_WEEK | Faster signal for ops teams |
| Set sentiment | SENTIMENT_TYPE_NONE | SENTIMENT_TYPE_UP_IS_GOOD | Insights can indicate good/bad direction |
| Add comparison | TIME_COMPARISON_PREVIOUS_PERIOD only | + TIME_COMPARISON_YEAR_AGO_PERIOD | Reveals seasonality patterns |

### Suggested New Filtered Metrics

| Name | Filter | Granularity | For |
|------|--------|-------------|-----|
| [Metric] - APAC | Region = APAC | GRANULARITY_BY_MONTH | Regional leadership |
```
