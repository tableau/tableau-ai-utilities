# Profiling Recipes

Query templates, classification and derivation tables, and correlation and time-series profiling procedures used during Phase 2.

## Step 2A: Field Classification Table

| Category | Detection Rule | Action |
|----------|---------------|--------|
| **Categorical Dimension** | dataType=STRING, columnClass=COLUMN, not geographic | Profile: distinct values + frequencies |
| **Geographic** | Field name contains City, State, Country, Region, Postal/ZIP, or dataCategory is geo | Profile: distinct values + frequencies |
| **Numeric Measure** | dataType=REAL or INTEGER, defaultAggregation in (SUM, AVG) | Profile: min, median, max, avg, stdev, count |
| **Date/Time** | dataType=DATE or DATETIME | Profile: min, max date range |
| **ID/Key** | Name contains *_id, *_key, "Order ID", or appears in join conditions | Generate: sequential or formatted |
| **Calculated Field** | columnClass=CALCULATION or formula present | Derive: compute per-row from base fields post-generation |
| **Bin** | columnClass=BIN | Skip: recreate from base field in Tableau |

## Step 2C: Profiling Query Templates

**Categorical dimensions (low cardinality):**
```json
{
  "fields": [
    {"fieldCaption": "<field>"},
    {"fieldCaption": "<id_field>", "function": "COUNT", "fieldAlias": "freq", "sortDirection": "DESC", "sortPriority": 1}
  ]
}
```
Count a non-null ID field (not the dimension itself) so the dimension and its count do not collide. For medium cardinality pass `limit: 50` on the query. Put all numeric aggregates for several measures in one query, and all COUNTD checks in one query, instead of one query per field.

**Numeric measures (get full statistical profile):**
```json
{
  "fields": [
    {"fieldCaption": "<field>", "function": "MIN", "fieldAlias": "min_val"},
    {"fieldCaption": "<field>", "function": "MAX", "fieldAlias": "max_val"},
    {"fieldCaption": "<field>", "function": "AVG", "fieldAlias": "avg_val"},
    {"fieldCaption": "<field>", "function": "MEDIAN", "fieldAlias": "median_val"},
    {"fieldCaption": "<field>", "function": "STDEV", "fieldAlias": "stdev_val"},
    {"fieldCaption": "<field>", "function": "COUNT", "fieldAlias": "row_count"}
  ]
}
```

**Date fields:**
```json
{
  "fields": [
    {"fieldCaption": "<field>", "function": "MIN", "fieldAlias": "earliest"},
    {"fieldCaption": "<field>", "function": "MAX", "fieldAlias": "latest"}
  ]
}
```

**Row count (run once, reuse for all null rate calculations):**
```json
{
  "fields": [
    {"fieldCaption": "<any_non_nullable_id_field>", "function": "COUNT", "fieldAlias": "total_rows"}
  ]
}
```

## Step 2D: Examples of Per-Row Computation

| Metadata Formula | Per-Row Computation | Explanation |
|-----------------|-------------------|-------------|
| `SUM([Profit])/SUM([Sales])` | `row.profit / row.sales` | Each row gets its own ratio |
| `[Sales] * (1 - [Discount])` | `row.sales * (1 - row.discount)` | Direct per-row calc |
| `DATEDIFF('day', [Order Date], [Ship Date])` | `(row.ship_date - row.order_date).days` | Per-row date diff |
| `IF [Profit] > 0 THEN 'Profitable' ELSE 'Loss'` | `'Profitable' if row.profit > 0 else 'Loss'` | Per-row conditional |

## Step 2E: Cross-Field Derivation Patterns

| Pattern | Rule |
|---------|------|
| ID contains `{YYYY}` pattern | Year in ID MUST match year of associated date field |
| Ship Date + Order Date | Ship Date MUST be ≥ Order Date |
| City + State + ZIP | Must be geographically valid combination |
| State + Region | Must match the profiled state→region mapping |
| Country + State | Must be valid (no US states in Canada, etc.) |
| Discount + Profit + Sales | If Discount > 0.3, Profit is more likely negative |

## Step 2F: Correlation Profiling Method and Generation

**Profiling method:**

For each pair of numeric measures, estimate their correlation direction and approximate strength using grouped averages. You cannot compute a raw Pearson r via the Tableau query API, so use this proxy approach:

1. Identify all numeric measure pairs (Sales↔Profit, Sales↔Discount, Profit↔Quantity, etc.). For N measures, there are N×(N-1)/2 pairs.
2. First read MIN, MEDIAN and MAX of field_A from its numeric profile (Step 2C) and use them to set four band edges (min, lower-half midpoint, median, upper-half midpoint, max). Then, for the most important pairs (up to 6 pairs — prioritize measures that are logically related), run ONE query per pair, using a calculated band dimension so all four bands come back together:

```json
{
  "fields": [
    {"fieldCaption": "A_band", "calculation": "IF [<field_A>] < <edge1> THEN 'B1' ELSEIF [<field_A>] < <edge2> THEN 'B2' ELSEIF [<field_A>] < <edge3> THEN 'B3' ELSE 'B4' END"},
    {"fieldCaption": "<field_B>", "function": "AVG", "fieldAlias": "avg_B"},
    {"fieldCaption": "<id_field>", "function": "COUNT", "fieldAlias": "row_count"}
  ]
}
```

Verify this calculated-band query on the first pair. If the server rejects it, fall back to one query per band with a `QUANTITATIVE_NUMERICAL` `RANGE` filter (`"field": {"fieldCaption": "<field_A>"}`, `min`, `max`).

Check whether field_B's average rises, falls, or stays flat across the four bands.

3. Classify each pair:

| Pattern Across Quartiles | Classification | Generation Strategy |
|---|---|---|
| B rises as A rises | Positive correlation (strong if monotonic, moderate if mostly) | Generate B as function of A + noise |
| B falls as A rises | Negative correlation | Generate B inversely from A + noise |
| B flat or erratic | No meaningful correlation | Generate independently |

**Recording correlations in schema proposal:**

```
Correlation Matrix (profiled):
- Sales ↔ Profit: positive (moderate) — B rises in 3 of 4 bands
- Sales ↔ Quantity: positive (weak) — B rises slightly, not in every band
- Discount ↔ Profit: negative (moderate) — B falls in 3 of 4 bands
- Quantity ↔ Discount: no correlation
```

**Generation with correlations (Phase 4):**

For positively correlated fields (e.g., Sales→Profit, moderate strength):
1. Generate Sales independently using its profiled distribution
2. Generate Profit as: `profit = correlation_factor * sales * profit_margin + noise`
   - Where `correlation_factor` controls tightness (stronger relationship = less noise; strengths are qualitative, not a measured r)
   - `profit_margin` calibrates to match profiled Profit avg
   - `noise = random.gauss(0, σ)` where σ controls scatter
3. Clamp Profit to its profiled [min, max] range
4. Verify: generated correlation direction matches profiled direction

For negatively correlated fields (e.g., Discount→Profit):
1. Generate Discount independently
2. Adjust Profit: rows with higher discount get a negative profit modifier
   - `profit_modifier = -1 * discount_value * scaling_factor + noise`

## Step 2G: Time-Series Profiling Method and Generation

**Profiling method:**

1. **Trend detection** — Query monthly or quarterly aggregates to detect growth/decline:

```json
{
  "fields": [
    {"fieldCaption": "<date_field>", "function": "TRUNC_QUARTER"},
    {"fieldCaption": "<measure>", "function": "AVG", "fieldAlias": "period_avg"}
  ]
}
```

Compare first-half average to second-half average:
- If second_half > first_half × 1.10 → "growth trend detected (~X% annualized)"
- If second_half < first_half × 0.90 → "decline trend detected (~X% annualized)"
- Otherwise → "flat / no significant trend"

2. **Seasonality detection** — Query by month (if ≥2 years of data) or by quarter:

```json
{
  "fields": [
    {"fieldCaption": "<date_field>", "function": "TRUNC_MONTH"},
    {"fieldCaption": "<measure>", "function": "AVG", "fieldAlias": "monthly_avg"}
  ]
}
```

Use monthly AVG (per-row value level), never SUM, which mixes volume and value. The seasonal index scales row values only; rows per month are not shaped by it (see Phase 4 Temporal Pattern Application).

Look for repeating patterns: if the same months consistently over/under-index relative to the annual average (e.g., Nov-Dec always 40%+ above average → holiday seasonality), record the seasonal curve.

3. **Day-of-week effect** — Query by weekday:

```json
{
  "fields": [
    {"fieldCaption": "<date_field>", "function": "TRUNC_DAY"},
    {"fieldCaption": "<measure>", "function": "COUNT", "fieldAlias": "daily_count"}
  ]
}
```

Group results by day-of-week and compute relative weights (e.g., Monday=18%, Tuesday=17%, ..., Saturday=8%, Sunday=5%).

**Recording temporal patterns in schema proposal:**

```
Temporal Patterns (profiled):
- Trend: +12% YoY growth (Sales rising across quarters)
- Seasonality: Q4 spike (Nov +35%, Dec +42% above annual avg), Q1 dip (Jan -20%)
- Day-of-week: Weekdays 80% of volume (Mon-Fri 16% each), Weekends 20% (10% each)
```

**Generation with temporal patterns (Phase 4):**

When generating date-indexed rows:

1. **Apply trend:** Scale each row's numeric values by a time-position factor:
   - `trend_factor = 1.0 + (annualized_growth_rate × years_from_start)`
   - Rows near the start of the date range get factor ≈1.0; rows near the end get factor ≈1.0 + total_growth

2. **Apply seasonality:** Multiply by a monthly seasonal index:
   - Construct a 12-element array of seasonal multipliers from profiling (e.g., `[0.80, 0.85, 0.95, 1.00, 1.05, 1.00, 0.95, 0.90, 1.00, 1.10, 1.35, 1.42]`)
   - Each row's value is multiplied by the seasonal index for its month

3. **Apply day-of-week weighting:** When distributing dates, use profiled weekday weights instead of uniform random. This means more rows fall on high-activity days.

4. **Combine multiplicatively:** `final_value = base_value × trend_factor × seasonal_index`

5. **Re-calibrate:** After applying temporal patterns, verify that the overall average still matches the profiled average (temporal shaping can drift the mean). Apply the same calibration algorithm from Phase 4's Numeric Calibration section.

**User options presented in schema proposal:**

```
Temporal options:
(a) Apply all detected patterns (trend + seasonality + day-of-week) [recommended]
(b) Apply seasonality only (no growth trend)
(c) Flat generation (ignore temporal patterns — dates uniform, values time-independent)
(d) Custom: specify your own growth rate or seasonal peaks
```
