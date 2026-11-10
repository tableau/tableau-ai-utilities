# Extract Dimensions Catalog (Locked)

Four locked audit dimensions. Never invent D5. Every finding cites its dimension ID.

## D1. Incremental Refresh Key

**Signature.** Extract is configured as Full refresh, but the underlying data source has a monotonically increasing datetime or bigint field that would support incremental refresh.

**Detection.**
- The extract's current refresh mode (Full vs. Incremental) is not independently confirmable from this tool surface — no listed tool reads that configuration. Do not claim to have checked it.
- Instead, scan fields for incremental-refresh-key candidates regardless of current mode: datatypes datetime, date, or bigint; name patterns like `_at`, `updated_at`, `created_at`, `id`, `sequence`, `event_time`.
- Sample via `get-summary-data` MIN + MAX to confirm monotonic increase.
- Report the finding as "candidate key identified" and note explicitly that the user should verify the extract's current refresh mode via Data → [datasource] → Extract → Edit before applying, since this skill cannot confirm whether it's already configured.

**Severity.** Warning if a strong candidate exists. Note if candidates exist but coverage across the fact table is unclear.

**Fix path.** Data → [datasource] → Extract → Edit → All rows / Incremental refresh → New rows identified by [field].

**Impact.** Estimate refresh-time reduction as `(1 - new-rows / total-rows)` percentage.

## D2. Aggregation

**Signature.** Extract is row-level, but every sheet aggregates on the same small set of dimensions (typically 2-4 dimensions plus a date grain).

**Detection.**
- Enumerate every sheet's dimension shelf.
- Identify the intersection: dimensions used on every sheet.
- If intersection is small (2-4 dimensions) and consistent, aggregation-on-extract is a candidate.

**Severity.** Note (aggregation trades granularity for size; may not fit every use case).

**Fix path.** Data → [datasource] → Extract → Edit → Aggregation → Aggregate data for visible dimensions.

**Impact.** Estimate row reduction as `(row-count post-aggregation / row-count pre-aggregation)`. Sample via `get-summary-data` COUNTD on the aggregation dimensions.

## D3. Hidden-Field Pruning

**Signature.** Extract contains fields never referenced by any sheet's shelves, encodings, filters, or tooltips.

**Detection.**
- Enumerate all fields in the data source.
- Enumerate all field placements across all sheets (shelves, encodings, tooltips, filters).
- Fields in the data source but not in any placement are pruning candidates.

**Severity.** Warning if >20% of total fields are candidates. Note if 5-20%. Info if <5%.

**Fix path.** Data → [datasource] → Extract → Edit → Hide All Unused Fields (or right-click each field → Hide).

**Impact.** Estimate file-size reduction as `(unused-field-count / total-field-count)` percentage. Not exact (some fields are wider than others).

## D4. Filter-at-Extract

**Signature.** A filter used on every sheet with the same value or range. Currently applied at query time on each sheet rather than at extract-creation time.

**Detection.**
- Enumerate every filter on every sheet.
- Group filters by field. If a field is filtered on every sheet with the same value/range, it's a candidate.

**Severity.** Warning if row-reduction estimate >30%. Note if 10-30%. Info if <10%.

**Fix path.** Data → [datasource] → Extract → Edit → Add [field] filter with the same value/range currently applied per sheet.

**Impact.** Estimate row reduction via `get-summary-data` count with vs. without the filter. Report the percent reduction.

## Refuse to Fabricate

If an optimization idea doesn't fit D1-D4 (e.g., custom SQL rewrites, materialized views, source-side denormalization), report "outside current audit scope; consult source-side optimization docs" and.
