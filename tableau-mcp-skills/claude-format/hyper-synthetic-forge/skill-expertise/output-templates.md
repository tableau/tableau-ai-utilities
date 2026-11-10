# Output Templates

Schema proposal, validation summary, and saved-schema JSON templates used in Phases 3, 5, and 7.

## Phase 3: Schema Proposal Template

```
📋 Hyper Synthetic Forge — Schema: [datasource name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tables: [list with relationships]
Target rows: [n] (clone mode default: min(profiled total_rows, 10,000))
Date range: [user-specified or profiled]
Parameters: [name=value] (if any detected)

| # | Field | Type | Strategy | Profiled Stats | Null Rate |
|---|-------|------|----------|---------------|-----------|
| 1 | Order ID | STRING | Formatted: ORD-{YYYY}-{#####} (year from Order Date) | — | 0% |
| 2 | Order Date | DATE | Uniform across [date range], weekday-weighted | 2020-01-03 to 2023-12-30 | 0% |
| 3 | Sales | REAL | Log-normal, calibrated: μ=X, σ=Y → avg≈$228 | avg=$228, min=$0.44, max=$22,638 | 0% |
| ... | ... | ... | ... | ... | ... |

Calculated fields (per-row derivation):
- Profit Ratio = row.profit / row.sales (from formula: SUM([Profit])/SUM([Sales]))

Skipped fields (aggregate/LOD — Tableau will recompute):
- [none, or list any LOD expressions]

Correlation Matrix (profiled):
- Sales ↔ Profit: positive (moderate) — B rises in 3 of 4 bands
- Discount ↔ Profit: negative (moderate) — B falls in 3 of 4 bands

Temporal Patterns:
- Trend: +12% YoY growth
- Seasonality: Q4 spike (Nov +35%, Dec +42%)
- Day-of-week: 80% weekday / 20% weekend

Null rates:
- [field]: [X]% null (or "all fields non-null" if none detected)
```

## Phase 5: Validation Results Summary Template

```
✓ Forge complete — validation passed
- Sales avg: $231.04 (profiled: $228.23, variance: +1.2%)
- Profit avg: $27.95 (profiled: $28.67, variance: -2.5%)
- All categorical distributions within ±3pp
- Correlations preserved: Sales↔Profit (positive ✓), Discount↔Profit (negative ✓)
- Temporal patterns applied: Q4 spike visible, +12% YoY trend confirmed
- All cross-field rules enforced
- Null rates verified
- 10,000 rows across 3 tables, referential integrity confirmed
```

## Phase 7: Saved Schema JSON Template

```json
{
  "schema_name": "<user-chosen name or datasource name>",
  "schema_version": 1,
  "seed": 42,
  "created_from": "<datasource LUID or 'description-based'>",
  "created_at": "<ISO timestamp>",
  "tables": [
    {
      "name": "<table_name>",
      "fields": [
        {
          "name": "Sales",
          "type": "REAL",
          "category": "numeric_measure",
          "distribution": "lognormal",
          "params": {"mu": 4.2, "sigma": 1.3},
          "profiled_stats": {"min": 0.44, "max": 22638, "avg": 228.23},
          "null_rate": 0.0
        },
        {
          "name": "Order Date",
          "type": "DATE",
          "category": "date",
          "range": {"start": "2020-01-03", "end": "2023-12-30"},
          "null_rate": 0.0
        },
        {
          "name": "Order ID",
          "type": "STRING",
          "category": "id",
          "format": "ORD-{YYYY}-{#####}",
          "date_source": "Order Date",
          "start": 1
        },
        {
          "name": "Category",
          "type": "STRING",
          "category": "categorical_dimension",
          "distribution": "weighted",
          "values": {"Office Supplies": 0.60, "Furniture": 0.22, "Technology": 0.18},
          "null_rate": 0.0
        }
      ],
      "correlations": [
        {"field_a": "Sales", "field_b": "Profit", "direction": "positive", "strength": "moderate"}
      ],
      "temporal_patterns": {
        "trend": {"type": "growth", "rate": 0.12},
        "seasonality": [0.80, 0.85, 0.95, 1.00, 1.05, 1.00, 0.95, 0.90, 1.00, 1.10, 1.35, 1.42],
        "day_of_week": [0.16, 0.16, 0.16, 0.16, 0.16, 0.10, 0.10]
      }
    }
  ],
  "row_count": 10000,
  "parameters": [{"name": "<parameter name>", "value": "<value used while profiling>"}],
  "foreign_keys": [
    {"child": "Returns.Order ID", "parent": "Orders.Order ID", "rate": 0.05}
  ],
  "imperfections": {"enabled": false, "severity": "light", "types": [], "answer_key": false},
  "injections": [],
  "cross_field_rules": [
    {"type": "date_ordering", "earlier": "Order Date", "later": "Ship Date"},
    {"type": "geographic_hierarchy", "fields": ["City", "State", "Region"]},
    {"type": "id_date_sync", "id_field": "Order ID", "date_field": "Order Date"}
  ],
  "calculated_fields": [
    {"name": "Profit Ratio", "formula": "row.profit / row.sales", "depends_on": ["Profit", "Sales"]}
  ]
}
```
