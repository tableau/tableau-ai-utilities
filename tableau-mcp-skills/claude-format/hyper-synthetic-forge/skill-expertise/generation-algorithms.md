# Generation Algorithms

Numeric calibration algorithm and detailed generation rules used during Phase 4.

## Phase 4: Numeric Calibration Algorithm

**For log-normal distributed fields (Sales, Revenue, Amounts):**

1. Target: generated_avg ≈ profiled_avg (within 10%), range approximately [profiled_min, profiled_max]
2. Estimate log-normal parameters from profiled stats (the median and average are both profiled in Step 2C):
   - `σ = sqrt(2 * ln(profiled_avg / profiled_median))` (capped at σ ≤ 2.5 to prevent extreme skew)
   - `μ = ln(profiled_median)`
   - Only if the median is unavailable or not below the average, fall back to `σ = sqrt(2 * ln(profiled_max / profiled_avg))` (same cap) and `μ = ln(profiled_avg) - σ²/2`
3. Generate all values: `value = random.lognormvariate(μ, σ)`
4. Clamp each value to [profiled_min, profiled_max]

**Calibration verification — multi-attempt with escape hatch:**

After generating all values for a numeric field:
1. Compute generated_avg = mean(values)
2. Compute variance_pct = (generated_avg - profiled_avg) / profiled_avg

**Attempt 1:** If |variance_pct| > 0.10:
- Apply scaling factor: multiply all values by (profiled_avg / generated_avg)
- Re-clamp to [profiled_min, profiled_max]
- Recompute generated_avg

**Attempt 2:** If still |variance_pct| > 0.10 after scaling:
- Adjust μ: increase μ by 0.2 if under-shooting, decrease by 0.2 if over-shooting
- Regenerate the entire field with new μ
- Apply scaling again if needed

**Attempt 3 (final):** If still |variance_pct| > 0.10:
- Compute final variance percentage
- **STOP attempting corrections.** Present to user:
  "Calibration note: [Field] generated avg is $[X] vs profiled $[Y] ([Z]% variance). The distribution shape makes exact calibration difficult within the profiled range. Options: (a) Accept this variance, (b) I can use a simpler uniform distribution that hits the target average exactly but loses the realistic shape, or (c) adjust the acceptable range."
- Wait for user decision before proceeding.

**For normal distributed fields (Scores, Ratings):**
1. μ = profiled_avg
2. σ = (profiled_max - profiled_min) / 6 (99.7% within range)
3. Generate: `value = random.gauss(μ, σ)`, clamp to [profiled_min, profiled_max]
4. Verify generated_avg within 10% (normal distributions self-calibrate well; if not, apply same escape hatch)

**For integer fields (Quantity):**
1. Use weighted random from profiled range, with geometric decay (lower values more common)
2. Verify generated_avg is within 10% of profiled_avg
3. If not: adjust weights (increase probability of higher values if avg is too low, or vice versa)

## Phase 4: Generation Rules

1. **Names:** Synthetic, culturally plausible, non-famous. Use diverse first/last name pools (100+ each). Never use placeholder patterns like "Customer_1" unless explicitly requested.

2. **Emails:** Pattern `{first}.{last}@{domain}` with synthetic domains (example.com, testcorp.net) unless company specified. Add numeric suffix if uniqueness requires.

3. **IDs with date component:** Extract the date from the associated date field. `ORD-{YYYY}-{#####}` → YYYY = year(order_date) for that row. **NEVER** generate the year independently of the date field.

4. **Sequential IDs without date:** Start from 1 (or user-specified), increment by 1. Format with zero-padding per profiled pattern.

5. **Dates:**
   - Generate within user-specified range (override profiled range if user provides one)
   - Weekday weighting: use profiled day-of-week weights (default if not profiled: Mon-Fri 16% each, Sat-Sun 10% each; a domain template may override)
   - Respect ordering constraints: Ship Date ≥ Order Date, End Date ≥ Start Date
   - Ship Date delay depends on Ship Mode (Same Day: 0, First Class: 1-3, Second Class: 2-5, Standard: 3-7 days)

6. **Categorical fields:** Generate using profiled frequency distributions. Example: if Category is Office Supplies 60%, Furniture 22%, Technology 18% — use weighted random selection matching those exact percentages.

7. **Geographic data:**
   - Use REAL countries, states, cities
   - Validate hierarchy: City must exist in State, State must exist in Country
   - Match profiled geographic distributions (CA 20%, NY 11%, TX 10%...)
   - State→Region mapping must match profiled relationship exactly
   - Postal codes must be plausible for the city/state (use real ZIP ranges)
   - **Fallback for ambiguous geography:** If a city name exists in multiple states (e.g., "Springfield"), always tie it to the state already selected for that row. If no valid city can be confirmed for a state, select from a known-good list of major cities for that state. Never leave a geographic field unvalidated — if in doubt, use the state capital or largest city.

8. **Nulls:** For each field with profiled null rate > 0, apply that exact null rate randomly. If no null profiling was possible, default to 0% (NOT NULL) unless user specifies otherwise.

9. **Cross-field correlations (enforce all):**
   - State → Region (must match profiled mapping)
   - Country → Currency (if present)
   - City → valid for State
   - Discount level → Profit direction (higher discount = lower/negative profit probability)
   - ID year component → Date year (must match)
   - Profiled numeric correlations (Sales↔Profit, etc.) — use correlation-aware generation

10. **Calculated fields:** Compute per-row AFTER generating all base fields. Apply the row-level interpretation of the formula (see Step 2D examples). Validate that computed values are reasonable (no division by zero, no infinite values). If row.sales = 0 and formula divides by sales, set result to NULL for that row.
