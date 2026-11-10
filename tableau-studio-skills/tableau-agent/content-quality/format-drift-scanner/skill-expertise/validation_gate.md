# Validation Gate (Read-Only, 3 Checks)

Every report passes all 3 checks before delivery. Any failure blocks delivery per HC#8. Fail-open is NOT applied since the skill is read-only.

## V1: Format-String Completeness

**Check:** every measure placement, date pill, and text object identified in Phase 1 has a resolved format string in Phase 2 (or sentinel `"unscanned"` with rationale).

**Required per placement:**

- `placement_id` (unique per placement across worksheets and DS).
- `element_type` (`measure_placement`, `date_pill`, or `text_object`).
- `worksheet_name` and `data_source_name` (or `workbook_scope` for text elements).
- `format_string` (extracted from XML) OR sentinel `"unscanned"` with `reason` populated.

**Fail action.** Re-derive the format string from the target worksheet's XML. If a second run still fails, refuse delivery per HC#8 or flag UNSCANNED. Never leave the format_string blank.

## V2: Drift-Catalog Match

**Check:** every finding cites one of the 7 catalog rule IDs (F-CURRENCY-01 through F-NEGATIVE-07) with the two-or-more differing format strings that fired the rule.

**Verification steps:**

1. Every finding has a `rule_id` from the locked 7-drift catalog.
2. Every finding has a `differing_format_strings` list with at least 2 entries.
3. Every finding cites the specific worksheets or elements where the drift occurred.
4. Cross-DS Info-by-default rule is applied correctly per HC#12.

**Fail action.** Re-run the drift detection against the baseline. If a second run still fails, refuse delivery per HC#8.

## V3: Handoff Completeness

**Check:** every field in `format_drift_report/1` populated per `skill-expertise/handoff_schema.md`.

**Verification steps:**

1. Every required field present with a non-blank value or sentinel.
2. `findings_by_drift_type` populated with all 7 drift-type counters (some may be 0).
3. `unscanned_placements` list populated when any placement was UNSCANNED (empty list otherwise).
4. Baseline format strings per drift type per DS populated for reproducibility.

**Fail action.** Identify the missing field, populate with the correct value or sentinel, and re-run V3. If a second run still fails, refuse delivery per HC#8.

## Gate Execution Order

1. V1 (format-string completeness) first. Cheapest to run; catches most failures.
2. V2 (drift-catalog match) next. Validates the drift-detection logic ran correctly.
3. V3 (handoff completeness) last. Depends on V1 and V2 to have complete data.

## What V-Gate Does NOT Check

- Whether the format strings represent locale-appropriate conventions (route to `i18n-scanner`).
- Whether the underlying data has quality issues (route to `data-quality-review`).
- Whether the chart type itself is right for the question (route to `chart-swap-advisor`).

## Refuse to Fabricate

If the V-gate cannot pass after one retry, refuse delivery and diagnose. Never fake a V-gate pass. Never invent a baseline format string; use the first-seen format string per HC#11.
