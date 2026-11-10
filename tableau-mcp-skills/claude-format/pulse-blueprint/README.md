# Pulse Blueprint

**A Claude skill that designs, audits, and optimizes Tableau Pulse metric definitions. Built for [Claude Desktop](https://claude.ai/download) and the [Tableau MCP](https://github.com/tableau/tableau-mcp).**

## How It Works

Describe what you want to track ("how are monthly sales trending?") and the skill finds the right datasource, picks the measure and time dimension, selects dimensions for slicing, configures insight types, and hands you an implementation-ready spec sheet. You configure it in the Tableau Pulse UI.

```
Pulse Metric Blueprint: Monthly Pipeline Coverage

Definition Spec

| Property | Value |
|----------|-------|
| Name | Pipeline Coverage |
| Datasource | Sales Opportunity Rebuild (RLS) |
| Measure | OPPORTUNITY_TOTAL_ACV |
| Aggregation | SUM |
| Time Dimension | CLOSE_DATE |
| Is Running Total | false |

Configuration Spec

| Property | Value |
|----------|-------|
| Allowed Granularities | GRANULARITY_BY_WEEK, GRANULARITY_BY_MONTH, GRANULARITY_BY_QUARTER |
| Allowed Dimensions | AE - Region, Account - Segment, Deal Band, Account Executive, Type |
| Sentiment | SENTIMENT_TYPE_UP_IS_GOOD |
| Number Format | NUMBER_FORMAT_TYPE_CURRENCY |
| Currency Code | CURRENCY_CODE_USD |
| Comparisons | TIME_COMPARISON_PREVIOUS_PERIOD, TIME_COMPARISON_YEAR_AGO_PERIOD |

Insight Settings

| Insight Type | Enabled |
|-------------|---------|
| INSIGHT_TYPE_CURRENT_TREND | Yes |
| INSIGHT_TYPE_TOP_DRIVERS | Yes |
| INSIGHT_TYPE_TOP_DETRACTORS | Yes |
| INSIGHT_TYPE_UNUSUAL_CHANGE | Yes |
| INSIGHT_TYPE_RISKY_MONOPOLY | No |
| INSIGHT_TYPE_RECORD_LEVEL_OUTLIERS | Yes |

Suggested Filtered Metrics

| Name | Filter | For |
|------|--------|-----|
| Pipeline - Enterprise | Account - Segment = Enterprise | Enterprise AEs |
| Pipeline - APAC | AE - Region = APAC | Regional leadership |
| Pipeline - Q3 Close | Close Quarter = Q3 | Forecasting team |
```

## Four Entry Points

| Entry Point | What It Does |
|-------------|-------------|
| Business Questions | "How are sales trending?" -> finds datasource, designs full metric blueprint |
| From Datasource | Points at a datasource, recommends up to 5 prioritized metrics per pass |
| Audit Existing | Reviews all current Pulse definitions for configuration gaps, scores them |
| Optimize Existing | Compares definition config against available datasource fields, recommends improvements |

## Audit Checks

| Check | Severity | What It Catches |
|-------|----------|-----------------|
| No description | HIGH | Empty or missing definition description |
| No sentiment set | HIGH | SENTIMENT_TYPE_NONE on a metric where up or down has a business meaning (neutral metrics such as headcount are not flagged) |
| All insights disabled | HIGH | No insight types enabled at all |
| Stale datasource | MEDIUM | Datasource content not updated in 90+ days (`updatedAt`; not extract refresh) |
| Too few dimensions | MEDIUM | Less than 3 allowed dimensions |
| Key insights disabled | MEDIUM | TOP_DRIVERS or CURRENT_TREND disabled |
| Single comparison only | MEDIUM | Exactly one comparison, and it is not PREVIOUS_PERIOD (a lone PREVIOUS_PERIOD is reported once, as Missing YoY) |
| Orphan definition | MEDIUM | Definition with 0 metrics created under it |
| Name quality | MEDIUM | Generic names like "1", "test", single characters |
| Currency mismatch | MEDIUM | Currency format set but code is UNSPECIFIED |
| Missing granularities | MEDIUM | Only 1-2 granularities allowed |
| Running total misuse | MEDIUM | is_running_total on a rate or average metric |
| Too many dimensions | LOW | More than 12 dimensions (dilutes insights) |
| Missing YoY comparison | LOW | No year-ago comparison configured |
| No goals set | LOW | No targets or benchmarks defined |
| No row-level config | LOW | Missing entity ID/name fields for outlier detection |
| Metric sprawl | LOW | More than 10 filtered metrics under one definition (true count fetched, since the full view shows at most 5) |

## Design Principles

The skill is opinionated about what makes a good metric. Eight principles guide every recommendation:

1. Fewer, better metrics. 5 well-configured beats 20 half-baked.
2. Match granularity to decision cadence. Monthly for execs, weekly for ops.
3. Sentiment is mandatory for actionable metrics. Without it, Pulse can't tell you if a change is good or bad.
4. Dimensions should answer "why" questions. Each one explains movement.
5. Top Drivers + Current Trend = minimum viable insights. Always enable these two.
6. Row-level config unlocks outlier detection. If you have entities (deals, customers), configure them.
7. Year-over-year comparison reveals seasonality. Always include it.
8. Running totals are for accumulating metrics only. Never for rates or averages.

## Key Features

- **Zero-config execution.** Describe what you want to track in plain language. The skill infers the datasource, fields, and configuration.
- **Deduplication.** Checks existing definitions before recommending new ones. Won't create duplicates.
- **Validation gates.** Every blueprint passes a 7-item completeness checklist. Every audit score gets arithmetic verification.
- **Exact API enums.** Specs use the Pulse API values (INSIGHT_TYPE_*, GRANULARITY_BY_*, etc.) so you can configure directly from the blueprint. Anything not enum-verified is labeled as a plain-language suggestion.
- **Dimension selection heuristic.** Picks 5-10 dimensions based on cardinality (3-50 values, checked with a `COUNTD` query when permitted, otherwise labeled "cardinality unverified"), business relevance, and "why" explanatory power.
- **Memory caching.** Remembers prior audits for delta comparison and delivered blueprints for deduplication.
- **Opinionated insight settings.** Recommends which insights to enable/disable based on metric type, not blanket defaults.
- **Graceful degradation.** Handles 403s, timeouts, partial responses, and missing datasources without failing.

## Requirements

- Claude Desktop with the Tableau MCP connected
- Tableau Cloud or Server REST API access
- Minimum permissions: `list-datasources` + `get-datasource-metadata` + `list-all-pulse-metric-definitions`
- Optional: `query-datasource` (cardinality checks and goal baselines) and `list-pulse-metrics-from-metric-definition-id` (true metric counts in audits)

## Installation

1. Save the whole `pulse-blueprint` folder (`SKILL.md` plus the `skill-expertise/` files) to your Claude skills directory. Installing `SKILL.md` alone leaves out the templates and reference tables it reads.
2. Trigger with: "pulse blueprint", "recommend metrics", "what should I track?", "audit my pulse metrics", or "optimize my metrics"

## Important Limitation

**This Tableau MCP exposes no Pulse create, edit, or delete tool.** This skill cannot create, update, or delete metric definitions. It produces implementation-ready blueprints that you configure manually in the Tableau Pulse UI. The output gives you everything you need: field names, enum values, dimension lists, and insight settings.

## Companion Skills

| Skill | Handoff |
|-------|---------|
| Data Quality Sentinel | Profile datasource quality before designing metrics on it |
| Governance Scanner | Check if the datasource is stale or uncertified |
| Dashboard Blueprint | Design a Tableau dashboard using the same datasources |
| Tableau Calc Engine | Write calculated fields needed for custom measures |
| Tableau Scribe | Document the metrics after they're configured |

## Limitations

- Cannot create or modify Pulse metric definitions (this MCP exposes no tool for it)
- Audit checks read definition metadata only; it uses small aggregate `query-datasource` calls (cardinality, baselines) but does not validate data values or null rates
- Dimension cardinality is checked with a `COUNTD` query only when `query-datasource` is permitted; otherwise it is labeled "cardinality unverified"
- Datasource freshness check depends on the `updatedAt` timestamp (last content change, not extract refresh; refresh schedules are not exposed)
- Can list only the current user's own Pulse subscriptions, so there is no site-wide subscriber or usage signal
- Audit scoring uses fixed severity weights (not customizable per organization)
- Checks that can't run (inaccessible datasource, capped metric count) are reported as "not checked" and the audit is labeled Partial
