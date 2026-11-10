# Check Definitions

Checks are ordered by **analytic impact** — the degree to which an undetected issue corrupts aggregations, joins, filters, or visual encodings in Tableau. Higher-impact checks run first and produce higher default severities.

***

## Severity Levels

| Level | Meaning | When to assign |
|-------|---------|----------------|
| **Critical** | Actively corrupts calculations, joins, or aggregations. Analysis built on this field is unreliable until fixed. | Nulls in join keys, duplicate rows, type mismatches in measure fields, referential orphans. |
| **Warning** | Degrades accuracy or usability but doesn't silently break things. User may get misleading (not wrong) results. | Nulls in non-key dimensions, inconsistent casing, leading/trailing whitespace, moderate cardinality inflation. |
| **Info** | Cosmetic or low-impact. Worth knowing but unlikely to produce incorrect answers. | Minor whitespace, singleton outliers in low-importance fields, sparse fields that are rarely used. |

***

## Check Categories (Priority Order)

### 1. Duplicate Rows

**Impact:** Inflates every SUM, COUNT, and AVG. Breaks uniqueness assumptions in LOD calcs.

**Logic:**
- **Pick the right key before you start.** In a line-item/order-grain datasource, a header-level key (e.g. `Order ID`) is EXPECTED to repeat once per line item — that repetition is normal business structure, not a duplicate-row signal. Before treating any repeated key as a finding, identify the field that should be unique per row (a transaction/row-level ID, e.g. `Transaction UUID`, `Row ID`) and run the CNT vs CNTD comparison on THAT field, not on a header-level key that legitimately repeats.
- **Known tooling gap in this environment: fast-path worksheet-building tools (`kpi-text`, `magnitude-simple-bar`, `bind-template`'s templates) cannot bind a `CNT`/`CNTD` aggregation onto a dimension field** — they reject it as a type/kind mismatch even though `COUNTD(field)` is valid Tableau. See SKILL.md Step 3 for the confirmed gap. Do not substitute a visual scan of a sample for the real comparison and do not report "no duplicates" from that workaround alone.
- **Confirmed working alternative — the row-count-helper calc.** Since `SUM` derivations bind reliably even when `CNT`/`CNTD` don't, author a trivial calc whose formula is the literal `1` (e.g. `DQ Check: Row Count Helper`, integer measure), then build the candidate key (rows) + `SUM()` of that helper (measure) via any bar-type template. The summed value per key IS the true row count for that key — no `CNT`/`CNTD` binding needed. Sum every returned per-key count across the pull; it must equal the confirmed true population size (if it doesn't, the pull itself is still truncated — go back to the truncation check above). Any key with a summed count `> 1` is a real, confirmed duplicate. This is a workbook change (a new calc), so it needs the same propose-then-approve step as any other fix per SKILL.md's verify-before-apply rule. There is no ability to delete a calculated field once created — it remains in the datasource permanently unless the user removes it themselves in Desktop; be upfront about that when proposing it, even though it's diagnostic-only and has no ongoing analytical purpose. Only fall back to asking the user to check `COUNT` vs `COUNTD` directly in Desktop (drag the field on twice; right-click the second instance → Measure → Count Distinct) if this workaround isn't viable (e.g. user declines the extra calc).
- **Before checking for dupes, verify the sample isn't silently truncated — and don't stop checking just because the first pull "looks" complete.** `get-summary-data` caps at the configured sample size (default 1,000 rows). A dataset with more rows than that cap will have some rows dropped from the read — and dropped rows can hide the very duplicates you're checking for, because a row and its duplicate can land on opposite sides of the cut. A truncated pull can still look like a full scan: contiguous/sequential key values (e.g. ORD-00001...ORD-01000) can fill exactly `maxRows` rows, giving the false impression of a complete, orderly dataset when the true population is larger. Treat "the returned row count equals the requested `maxRows`" as an unconfirmed-truncation signal on its own, regardless of how clean or complete the visible rows look.
- Confirm true population size with an aggregate read that carries no row-level grain: put a non-key measure or `COUNT` of a candidate key field alone on the view (no dimensions) and read that single aggregated value. Compare it against the row count returned by the Detail-shelf pull.
- If total population size > the sample size used for the Detail-shelf pull, do NOT conclude "no duplicates" from that pull alone. Instead:
  1. For each candidate key field (Order ID, Transaction ID, primary ID, etc.), get `CNTD(field)` (distinct count) and `CNT(field)` (non-null count) as a single aggregated pair, no dimensions.
  2. If `CNT(field) > CNTD(field)` for any key field, duplicates exist — the gap size (`CNT - CNTD`) is the number of duplicate rows for that key.
  3. Identify which specific key values are duplicated by grouping on that key field with a `CNT` of another field as the aggregate; any group where the count is > 1 is a duplicate key. Do this at the aggregated grain (key field on rows, count as a measure) rather than pulling all raw rows, since the grouped read summarizes correctly regardless of the sample cap on ungrouped Detail pulls.
  4. If multiple independent-seeming key fields (e.g. Order ID and Transaction ID) show the exact same duplicate count and it isn't a coincidence of business logic (e.g. one legitimately repeats per header/line-item structure), treat this as evidence of true row-level duplication (the same record re-inserted), not independent key collisions.
- Group rows by all field values (once dropped-row risk is ruled out or the check is done at the correct grain). Any group with count > 1 is a duplicate.
- Report: number of duplicate rows, which row/key values are repeated, and the duplication count.

**Severity:** Critical (always).

**Notes:** This checks exact row duplicates only (all fields identical) plus exact key-duplicate detection (same primary/business key repeated). Near-dupes (same entity, slightly different field values) are out of scope for the default run.

***

### 2. Null Values

**Impact:** Nulls break joins (NULL != NULL), skew aggregations (excluded from AVG/COUNT), and create misleading filter behavior.

**Logic per field:**
- Count rows where the field value is Null.
- Calculate null percentage: `null_count / total_rows * 100`.
- Thresholds:
  - 0% nulls → pass (no finding)
  - >0% and <=5% → Info (unless the field is a join key or primary key, then Warning)
  - >5% and <=25% → Warning
  - >25% → Critical

**Severity modifiers:**
- If the field is a known join/relationship key (per the workbook's relationship or join configuration) OR its name contains any of these substrings (case-insensitive): `_id`, `id_`, `uuid`, `_key`, `key_`, `_code`, `code_`, `fk_`, `pk_` — bump severity one level up.
- If the field is a measure (numeric, aggregatable): bump to at least Warning at any null rate above 0%, because nulls silently drop from aggregations.

***

### 3. Data Type Mismatches (Mixed Types)

**Impact:** Causes silent aggregation failures, broken filters, and incorrect sort orders. A "number stored as string" won't SUM.

**Logic:**
- For string fields, test each non-null value against these locked detection patterns:

**"Looks Numeric" patterns (test in order, use first match):**

Flexible (handles currency, percentages, thousands separators):
```
^-?\$?\d{1,3}(,?\d{3})*(\.\d+)?%?$
```
Matches: 123, -45.67, $1,000.50, 99.9%, -0.01

Strict scientific (for engineering/ML data):
```
^-?\d+(\.\d+)?([eE][-+]?\d+)?$
```
Matches: 100, -3.14, 1.5e-10, 6.022E23

**"Looks Date-Like" pattern:**
```
^(\d{4}[-/.]\d{2}[-/.]\d{2}|\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})([ T]\d{2}:\d{2}(:\d{2})?(\.\d+)?)?$
```
Matches: 2026-03-15, 03/15/2026, 2026.03.15, 2026-03-15T14:30:00

**Detection thresholds:**
- If >=10% of non-null values in a string field match a numeric pattern → flag "likely numeric stored as string."
- If >=10% of non-null values in a string field match the date pattern → flag "likely date stored as string."
- For numeric fields: check for sentinel values that suggest categorical encoding. Flag if the field contains 3 or fewer distinct values from this set: {-1, 0, 1, 99, 999, 9999, -999}.

**Severity:** Critical (numeric-as-string or date-as-string); Warning (sentinel values in numeric fields).

***

### 4. Leading/Trailing Whitespace

**Impact:** Breaks exact-match filters, inflates dimension cardinality (duplicates that look identical in viz but differ by invisible chars), and breaks joins.

**Logic per string field:**
- Compare each value to its trimmed form: `value != TRIM(value)`.
- Count affected rows.
- Threshold: any occurrence above 0 is a finding.

**Severity:**
- Field is a join key or used in filters → Warning
- Field is a general dimension → Info (unless cardinality inflation exceeds 5%, then Warning)

***

### 5. Inconsistent Casing

**Impact:** Inflates dimension cardinality. "New York", "new york", "NEW YORK" become three separate marks/filter values.

**Logic per string field:**
- Group values by their lowercase form.
- Any group with multiple original casings is a finding.
- Report: the distinct casing variants and how many rows each covers.

**Severity:**
- If inconsistent casing causes cardinality inflation >10% for that field → Warning
- Otherwise → Info

***

### 6. Outliers / Implausible Values

**Impact:** Skews averages, stretches axes, and can mask real patterns. A single $1B row in a $10K-average dataset dominates every viz.

**Prerequisite:** Do NOT run this check on fields already flagged as "sentinel values in numeric field" by Check #3. Those fields have categorical encoding issues, not outlier problems.

**Logic per numeric measure:**
- Calculate Q1, Q3, IQR from the sample.
- Flag values below Q1 - 3*IQR or above Q3 + 3*IQR (extreme outliers).
- For the negative-value sub-check, use this explicit list of field-name substrings that imply non-negative values (case-insensitive match):

**Non-negative field-name patterns:**

| Category | Substrings |
|----------|-----------|
| Counts & Totals | count, qty, quantity, num_, number_of, total_ |
| Identifiers & Keys | _id, id_, uuid, _key, _code, index, zip |
| Physical Quantities | age, height, width, length, depth, weight, size, distance |
| Durations & Time Spans | duration, seconds, minutes, hours, days, latency, ttl |
| Unit Prices & Rates | price, cost, fee, rate |

**Explicitly NOT non-negative** (do not flag negatives in these): amount, balance, profit, revenue, delta, change, difference, margin, net, variance.

If a numeric field's name contains any substring from the non-negative table AND the field contains values < 0, flag those negative values.

**Severity:**
- Extreme outliers (>3x IQR) in key measures → Warning
- Negative values in non-negative fields → Warning
- Mild outliers (1.5x-3x IQR) → Info

**Notes:** Do not flag outliers as Critical. They may be legitimate data. The user decides whether to filter or investigate.

**Duplicate-row contamination warning:** if Check #1 (Duplicate Rows) found duplicate keys/rows in this datasource, re-run outlier detection AFTER accounting for them, or verify suspected outliers against a per-record read rather than the aggregated view total. A worksheet grouped by all dimensions collapses true duplicate rows onto one mark, and `SUM` on that mark silently doubles (or N-tuples) the displayed measure value — producing a value that looks like an extreme outlier but is actually two (or more) normal records folded together. Before reporting a numeric outlier as a finding, check whether the affected row's key also appears in the duplicate-row finding; if so, verify the true per-record value (e.g. via a boolean test calc placed at row grain, or by isolating one copy) before concluding the value itself is implausible.

***

### 7. High Cardinality Dimensions

**Impact:** Dimensions with very high cardinality relative to row count produce unreadable vizzes, slow performance, and often indicate a field that should be a measure or needs binning.

**Logic per string/dimension field:**
- Count distinct values in the sample.
- Calculate cardinality ratio: `distinct_values / sample_size`.
- Thresholds:
  - Ratio > 0.9 (nearly unique per row) → flag as "potential identifier/key, not useful as dimension"
  - Ratio > 0.5 → flag as "high cardinality, consider grouping or filtering"

**Severity:**
- Ratio > 0.9 → Warning (likely a row-level ID being used as a dimension)
- Ratio > 0.5 → Info

***

### 8. Date Field Issues

**Impact:** Broken date hierarchies, incorrect trend analysis, failed date filters.

**Logic per date field:**
- Check for future dates beyond today + 1 year (possible data entry errors).
- Check for dates before a reasonable floor (before 1900-01-01).
- Check for suspicious clustering (truncation detection): if >90% of date values have day-of-month = 1, flag as "likely truncated to month-start." This suggests the source system is rounding dates, which masks daily patterns.

**Severity:**
- Future dates > 1 year out → Warning
- Pre-1900 dates → Warning
- Truncation pattern (>90% on day 1) → Info

***

### 9. Constant / Zero-Variance Fields

**Impact:** No analytic value. Adds clutter, confuses users, may indicate a broken ETL pipeline.

**Logic per field:**
- Count distinct non-null values in the sample.
- If distinct count = 1 (constant) → finding.
- For numeric fields: if standard deviation = 0 → finding.

**Severity:**
- Constant field → Info (unless it's a measure that should vary, then Warning)

***

### 10. Sparse Fields

**Impact:** Low fill rate means the field is unreliable for analysis. Users may build calcs on it without realizing 80% of values are missing.

**Logic per field:**
- This differs from the null check: a field can be "sparse" if it's mostly null OR mostly a single default/placeholder value (e.g., "N/A", "Unknown", "0", "-").
- Count rows where the value is null OR matches common placeholder patterns: "", "N/A", "n/a", "NA", "None", "null", "Unknown", "TBD", "0" (for strings).
- Calculate effective fill rate: `(total - placeholder_count) / total * 100`.
- Thresholds:
  - Fill rate < 25% → finding
  - Fill rate < 50% → finding (lower severity)

**Severity:**
- Fill rate < 25% → Warning (field is mostly unusable without imputation)
- Fill rate 25%-50% → Info

***

## Running Checks Efficiently

To minimize tool calls:

1. Batch related fields together on the scratch worksheet where possible.
2. Pull a single `get-summary-data` read and run multiple checks against the same data.
3. Remove fields and add the next batch after each round.
4. If a field fails an early check (e.g., >50% nulls), still run later checks on the non-null values. Multiple issues can coexist.

***

## Reporting Findings

For each finding, record:

- **Field name** (resolved, exact)
- **Check category** (from the list above)
- **Severity** (Critical / Warning / Info)
- **Evidence** (specific values, counts, percentages from the actual data read)
- **Affected row count / percentage**
- **Recommended fix** (reference to `fixes.md` recipe)

***

## Data Quality Score

Compute a score per datasource after all findings for that datasource are triaged. This is a weighted-deduction score, not a simple count — severity and breadth both matter.

**Formula:**

1. Start at 100 points.
2. For each Critical finding: deduct 15 points. If the finding's affected-rows percentage is >=50%, deduct 22.5 points instead (15 x 1.5).
3. For each Warning finding: deduct 6 points. If the finding's affected-rows percentage is >=50%, deduct 9 points instead (6 x 1.5).
4. For each Info finding: deduct 1 point, capped at a combined maximum of 5 points deducted from Info findings regardless of how many exist.
5. Sum all deductions and subtract from 100. Floor the result at 0 (score cannot go negative).
6. This uses ALL findings from the full check run, not just the top-5 shown in the report — the score must reflect the true state of the data even when the report display is capped.

**Grade bands:**

| Score | Grade | Meaning |
|-------|-------|---------|
| 90-100 | A | Production-ready |
| 75-89  | B | Usable, minor cleanup |
| 60-74  | C | Needs fixes before trusted analysis |
| 40-59  | D | Significant integrity risk |
| 0-39   | F | Not analysis-ready |

**Multi-datasource rollup:** when reviewing more than one datasource in a session, report a score per datasource plus one overall figure computed as the unweighted average of the per-datasource scores (round to nearest whole number). If any single datasource scores F, call that out explicitly in the rollup even if the average lands in a higher band — a single F-grade datasource is a risk the average can hide.

**Presentation:** show the score as `Score: [N]/100 ([Grade])` directly under the Sample size line in the report header, before the Findings section.
