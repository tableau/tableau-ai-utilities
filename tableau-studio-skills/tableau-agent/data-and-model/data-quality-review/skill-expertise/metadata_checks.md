# Metadata Checks

These checks run on `list-available-fields` output alone. They require no `get-summary-data` call and complete in seconds. They form the "Phase 0: Metadata Pre-Scan" and produce findings that feed into the same severity/scoring system as row-level checks.

***

## Severity Levels (same as checks.md)

| Level | Meaning |
|-------|---------|
| **Critical** | Actively corrupts analysis or makes the datasource unusable for its stated purpose. |
| **Warning** | Degrades usability, discoverability, or trust. Likely confuses consumers. |
| **Info** | Cosmetic or low-impact. Worth noting. |

***

## Check Categories

### M1. Naming Violations (Tableau Best Practices)

**Impact:** Poor field names confuse consumers, break self-service, and make datasources undiscoverable.

**Tableau naming conventions enforced:**

| Rule | Detection | Severity |
|------|-----------|----------|
| Dimensions should be Title Case | Field is dimension + not Title Case (e.g. "order date", "ORDER_DATE") | Warning (systemic) |
| Measures should be Title Case or sentence case | Field is measure + contains raw underscores or ALL_CAPS | Warning (systemic) |
| No raw underscores in display names | Field caption contains `_` (not just internal name) | Warning (systemic) |
| No system suffixes exposed | Caption ends with `__c`, `__r`, `__x`, `__mdt` | Warning (systemic) |
| No table-prefix redundancy | Caption starts with its parent logical table name (e.g. "Orders Order ID") | Info |
| Cryptic abbreviations | Caption is <4 chars AND not in allowed-short list (ID, Qty, Amt, Pct, YoY, MoM, QoQ, YTD, MTD, No, Nr, SKU, UPC, URL, ZIP, Lat, Long, Lon) | Warning |
| Generic/meaningless names | Caption matches: `^(value|field|col|column|data|info|item|measure|dim|metric)\d*$` (case-insensitive) | Warning |

**Systemic aggregation:** When >5 fields match the same naming pattern, report as one systemic finding: "[Pattern]: [count] fields. Examples: [top 5 captions]."

**False positive exclusions:**
- Parameters (skip entirely)
- Fields where internal name differs from caption (user already aliased it; check caption only)
- Calculated fields with `DQ Fix:` prefix (created by this skill)

***

### M2. Type & Role Mismatches (Inferred from Name)

**Impact:** A field whose name strongly implies one type/role but is configured differently will produce wrong aggregations or broken date hierarchies.

**Detection rules:**

| Pattern (case-insensitive match on caption) | Expected | Flag if | Severity |
|---------------------------------------------|----------|---------|----------|
| Contains: date, time, created, updated, modified, timestamp, _at, _on | DATE or DATETIME type | Type is STRING or INTEGER | Critical |
| Contains: count, qty, quantity, amount, total, sum, revenue, sales, cost, price, profit, margin | Numeric type + MEASURE role | Type is STRING, or role is DIMENSION | Warning |
| Contains: _id, id_, _key, _code, _fk, _pk, uuid, guid | DIMENSION role | Role is MEASURE | Warning |
| Contains: is_, has_, flag, active, enabled, disabled | BOOLEAN concept | Type is STRING with high cardinality (>10 distinct implied by name) | Info |
| Contains: pct, percent, rate, ratio | Numeric MEASURE | Type is STRING | Warning |
| Contains: name, description, comment, note, label, title, category, status, type, region, country, state, city | STRING DIMENSION | Role is MEASURE | Info |

**Word-boundary matching:** Match on word boundaries or field-caption start/end to avoid false positives (e.g. "considered" should not match "id"). Use substring matching only for prefix/suffix patterns (_id, is_, _at).

**Conflict with row-level Check #3:** If both M2 and Check #3 flag the same field for a type mismatch, keep only the Check #3 finding (it has actual data evidence). Remove the M2 finding to avoid double-counting.

***

### M3. Schema Hygiene

**Impact:** Structural signals indicating poor modeling, excessive complexity, or rushed development.

**Checks:**

| Check | Threshold | Severity |
|-------|-----------|----------|
| Excessive field count | >100 fields: Warning; >200 fields: Critical | As stated |
| No dimensions present | All fields are measures | Warning |
| No measures present | All fields are dimensions (excluding calcs) | Info |
| Excessive calc ratio | >60% of fields are calculated: Warning; >80%: Critical | As stated |
| Very long calc formulas | Formula length >500 chars: Info; >1000 chars: Warning | As stated |
| Deeply nested logic | Formula contains >5 IF/CASE/IIF nesting levels | Warning |
| Hardcoded string literals | Formula contains >3 string comparisons (brittle to value changes) | Info |

**Counting:** Each schema check is one finding regardless of how many fields contribute to it. "Excessive field count" is one finding, not one per field.

***

### M4. Near-Duplicate / Redundant Fields

**Impact:** Confuses consumers, inflates the field list, creates ambiguity about which field to use.

**Detection logic:**

1. **Exact caption duplicates:** Two or more fields with the identical caption (different internal names). Always a problem.
   - Severity: Warning

2. **Near-duplicate captions:** Normalize captions (lowercase, strip underscores/spaces/hyphens, strip common suffixes like "name", "value", "field") and group. If two+ fields collapse to the same normalized form, flag.
   - Examples: "Customer Name" and "CustomerName" and "customer_name"; "Order Date" and "OrderDate"
   - Severity: Info (may be intentional aliases across tables)

3. **Same-name different-table:** In multi-table datasources, the same caption appearing in two logical tables (e.g. "ID" in both Orders and Returns). Not always wrong but worth flagging for disambiguation.
   - Severity: Info

**Systemic aggregation:** If >5 near-duplicate groups exist, aggregate: "[N] near-duplicate field groups detected. Examples: [top 3 groups]."

***

### M5. Unused / Low-Signal Fields

**Impact:** Clutter in the data pane reduces discoverability and increases cognitive load for consumers.

**Detection logic (metadata-only heuristics):**

| Signal | Interpretation | Severity |
|--------|---------------|----------|
| Field is hidden (`isHidden: true` if exposed by API) | Already suppressed by author; no action needed | Skip (don't flag) |
| Field caption is a generic auto-increment pattern (e.g. "F1", "F2", "Column1", "Unnamed: 0") | Likely an artifact of CSV/Excel import with no header row | Warning |
| Field has no description AND is not used in any calc formula AND has a generic/system name | Low-value candidate | Info |

**Important:** Desktop's `list-available-fields` does not expose usage data (which sheets use which fields). This check is heuristic only. Always phrase findings as "candidate for review" not "confirmed unused."

**Do NOT flag:**
- Fields with meaningful captions even if unused (user may plan to use them)
- Join keys (even if never placed on a viz, they serve a structural purpose)
- Fields that appear in other fields' calc formulas (they're dependencies)

***

## Scoring Integration

Metadata findings feed into the same score formula as row-level findings (from checks.md):

```
Score = 100 - (Critical x 15) - (Warning x 6) - (Info x 1, capped at 5 total)
```

**Important:** When both a metadata finding (M2) and a row-level finding (Check #3) flag the same field for the same issue, count it ONCE (keep the row-level version, which has evidence). The metadata pre-scan is a fast first pass; row-level checks are the ground truth.

***

## Report Integration

Metadata findings appear in the report BEFORE row-level findings, under a separate heading:

```
### Metadata Findings (from field inventory)

- **[Pattern/Check]** -- [Severity] -- [description]. Fields: [count]. Examples: [top 3].
  *Fix:* [one-line proposed fix or "Advisory only"].
```

If zero metadata findings: omit the section entirely (don't write "No metadata findings").

***

## Relationship to Row-Level Checks

| Metadata check | Row-level counterpart | Priority rule |
|---|---|---|
| M2 (type mismatch from name) | Check #3 (type mismatch from data) | If both fire on same field, keep Check #3 only |
| M4 (near-duplicate captions) | Check #5 (inconsistent casing) | Both can coexist (different issues) |
| M5 (unused/low-signal) | Check #9 (constant/zero-variance) | Both can coexist |
| M1, M3 | No row-level equivalent | Always report |
