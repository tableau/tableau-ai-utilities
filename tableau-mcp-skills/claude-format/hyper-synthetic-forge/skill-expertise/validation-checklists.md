# Validation Checklists

Statistical, categorical, correlation, temporal, consistency, and privacy checks run in Phase 5.

## Phase 5: Validation Checks

### Statistical Accuracy Checks

For each profiled numeric field, compute and compare:

| Metric | Profiled | Generated | Variance | Status |
|--------|----------|-----------|----------|--------|
| Sales avg | $228.23 | [value] | [x]% | ✓/✗ |
| Sales min | $0.44 | [value] | — | ✓/✗ |
| Sales max | $22,638 | [value] | — | ✓/✗ |
| Profit avg | $28.67 | [value] | [x]% | ✓/✗ |
| Quantity avg | 3.79 | [value] | [x]% | ✓/✗ |

**Threshold:** If any average deviates by more than 10% from profiled AND calibration escape hatch was not already triggered (user accepted variance), flag it for correction.

**Injected rows:** Rows modified by anomaly injection (Phase 4B) are excluded from the mean, seasonal and trend checks; report them separately (count and what changed). Imperfections (Phase 4C) are applied after this validation passes; afterwards re-run only the privacy, ID/key and cross-field checks.

### Categorical Distribution Checks

For each profiled categorical field, verify generated frequencies are within ±3 percentage points of profiled:

| Category | Profiled % | Generated % | Status |
|----------|-----------|-------------|--------|
| Office Supplies | 60% | [x]% | ✓/✗ |
| Furniture | 22% | [x]% | ✓/✗ |
| Technology | 18% | [x]% | ✓/✗ |

### Correlation Direction Checks

For each profiled correlation pair, verify the generated data preserves the relationship:

| Pair | Profiled Direction | Generated Direction | Status |
|---|---|---|---|
| Sales ↔ Profit | Positive | [result] | ✓/✗ |
| Discount ↔ Profit | Negative | [result] | ✓/✗ |

**Method:** Sort generated data by field_A, split into quartiles, check that field_B's average moves in the expected direction. If violated, flag for regeneration of the dependent field.

### Temporal Pattern Checks (if applied)

- [ ] Monthly averages follow the profiled seasonal curve (within ±15% of expected seasonal index)
- [ ] Overall trend direction matches profiled direction (growth/decline/flat)
- [ ] Day-of-week distribution matches profiled weights (within ±5pp)

### Cross-Field Consistency Checks

- [ ] Every Order ID year matches its Order Date year
- [ ] Every Ship Date ≥ its Order Date
- [ ] Every City is valid for its State (no city/state mismatches)
- [ ] Every State is valid for its Region (matches profiled mapping)
- [ ] Every State is valid for its Country
- [ ] Every calculated field is computed correctly from base fields (spot-check 5 random rows)
- [ ] No orphaned foreign keys (every Returns.Order_ID exists in Orders)
- [ ] No duplicate values in fields marked unique
- [ ] Null rates match profiled rates within ±2 percentage points

### Privacy Checks

- [ ] No real values copied from PII-like columns (name, email, phone, address, ID-like)
- [ ] No real full name + real address + real phone/email combination
- [ ] Synthetic names only (no celebrities, public figures)
- [ ] Randomized street numbers if addresses present
