# Handoff Schema — `calc_inventory_handoff/1` (Locked)

Every successful `calc-inventory` invocation emits this schema, including "empty inventory" verdicts. Downstream calc-family peers and workbook-auditor may consume it. Schema is versioned; unknown versions refused by downstream.

## Full Schema

```yaml
schema_version: calc_inventory_handoff/1
datasource_name: {name}
datasource_id: {luid}
total_count: {N}
calcs:
  - # Full per-calc entry per skill-expertise/catalog_schema.md
    calc_name: {string}
    calc_type: {row_level | aggregate | lod_fixed | lod_include | lod_exclude | table_calc}
    formula: {formula_text}
    return_type: {number | string | date | datetime | boolean | spatial | unknown}
    is_aggregated_flag: {true | false}
    derivation_prefix: {none | sum | usr}
    references: {...}
    style_violations: [...]
    perf_advisory_flags: [...]
    complexity: {...}
    usage: {...}
    notes: {optional_free_text}
  - # ...one entry per calc
unused_calcs:
  - {calc_name}
  # calcs with usage.flag == "unused"
cycle_report:
  - cycle: [{calc_name_1}, {calc_name_2}, ..., {calc_name_1}]
    detected_at: {timestamp}
  # empty list if no cycles
batching_method: {single_pass | paginated_20 | paginated_20_plus_field_batching}
usage_metadata_available: {true | false}
run_metadata:
  timestamp: {ISO-8601}
  total_batches: {N}
  reconciliation_retries: {N}
notes: {optional_free_text}
```

## Field-by-Field

- **schema_version:** always exactly `calc_inventory_handoff/1`.
- **datasource_name / datasource_id:** identifies the target DS. Multi-source workbooks require HC#1 clarifier before this handoff can be built.
- **total_count:** the number of calcs in the inventory. `0` for empty-inventory verdicts.
- **calcs:** list of catalog entries per `catalog_schema.md`. Empty list `[]` for empty-inventory verdicts.
- **unused_calcs:** convenience list of calc names with `usage.flag: "unused"`. Empty list if all calcs are in use. Derived from `calcs[].usage.flag`; kept separate for downstream ease-of-use.
- **cycle_report:** list of nested-calc cycles detected during V3. Empty list if no cycles. Each entry names the full cycle chain.
- **batching_method:** how the enumeration was performed. `single_pass` for <20 calcs. `paginated_20` for 20-99 calcs. `paginated_20_plus_field_batching` for 100+ calcs.
- **usage_metadata_available:** `true` only if both `get-workbook-inventory` (dashboards) and `search-workbook-fields` (shelf placements) succeeded and populated `usage.*` fields with real data for every entry. `false` if either tool failed for any entry, even if the other tool's data is real — see per-entry `usage.unavailable_this_run` for which half is missing.
- **run_metadata:** operational metadata for debugging/audit. `timestamp` when the inventory was delivered. `total_batches` for pagination stats. `reconciliation_retries` for V2 retry count (should be 0 or 1).
- **notes:** optional free-text. Common uses: multi-batch reconciliation warnings, external-reference callouts, DS-wide caveats.

## Downstream Consumer Expectations

- **`workbook-auditor`** consumes when running dashboard-level or workbook-wide audits. Reads full `calcs` list plus `unused_calcs` and `cycle_report`.
- **`calc-linter`** may consume single-calc entries (via `calcs[i]`) when the user picks one from an inventory delivery and says "lint that one." Reads `formula`, `calc_name`, `style_violations` for prior-flagged context.
- **`calc-optimizer`** may consume single-calc entries similarly. Reads `formula`, `calc_name`, `perf_advisory_flags` for prior-flagged context.
- **`calc-debugger`** does NOT consume this schema (calc-debugger starts from a broken calc, not from an inventory).
- **`calc-writer`** does NOT consume this schema (starts fresh from natural-language ask).
- **`data-model-documenter`** may reference `total_count` and `unused_calcs` count for its calc-dependency-graph section rollup.

## "Empty Inventory" Verdict Contract

When `total_count: 0`:
- `calcs: []`.
- `unused_calcs: []`.
- `cycle_report: []`.
- `batching_method: single_pass`.
- `usage_metadata_available` reflects the actual availability of both `get-workbook-inventory` and `search-workbook-fields` (may be true or false).
- `notes` should explain scope of check (e.g., "Data source `Sample - Superstore` has zero calculated fields.").

## Bulk-Action Refusal Contract

If the ask was a bulk-fix that got refused (e.g., "bulk-lint all flagged calcs"), calc-inventory does NOT emit this schema. Instead, calc-inventory refuses per HC#10 with routing guidance to the appropriate peer (calc-linter, calc-optimizer, calc-debugger) one calc at a time. The refusal is not a delivery.

## Refuse to Guess

If any required field can't be populated (e.g., `datasource_id` unresolvable, `total_count` mismatch after V2 retry), refuse delivery per HC#8. Never fake fields to satisfy the schema. Never claim `usage_metadata_available: true` if any entry has sentinel `"unavailable_this_run"`.
