# Validation Gate (Read-Only, 3 Checks)

Every preflight report passes all 3 checks before delivery. Any failure blocks delivery per HC#8. Fail-open is NOT applied since the skill is read-only.

Different from the calc-family 8-check gate because dashboard-preflight is a read-only auditing skill scoped to one dashboard, not a mutating calc author.

## V1: Finding-Catalog Match

**Check:** every finding in the report references one of the 8 catalog rule IDs (P-ZONE-01 through P-CONTAINER-08) OR the sentinel value `"unscanned"` with a rationale.

**Required per finding:**

- `rule_id` from the 8-check catalog (`P-ZONE-01`, `P-SHEET-02`, `P-FILTER-03`, `P-PARAM-04`, `P-TITLE-05`, `P-CANVAS-06`, `P-FIT-07`, `P-CONTAINER-08`) or `"unscanned"`.
- `severity` (`Blocking`, `Warning`, `Info`).
- `zone_reference` OR `dashboard_scope: true` for dashboard-level findings.
- `desktop_fix_instruction` (non-empty string; concrete Desktop UI steps).
- `notes` (optional free-text; required when `rule_id: "unscanned"`).

**Fail action:** identify the invalid finding, re-derive the correct rule_id from the catalog, and re-run V1. If a second run still fails, refuse delivery per HC#8.

## V2: Zone-Count Reconciliation

**Check:** every zone identified in Phase 1 inventory appears in at least one Phase 2 finding (as a hit) or is accounted for by at least one "no finding" evaluation record.

**Verification steps:**

1. Phase 1 zone count = Phase 2 accounted-for count. Mismatch is a V2 fail.
2. `dashboard_scope: true` findings account for dashboard-level checks (P-CANVAS-06, dashboard-level P-TITLE-05, dashboard-level P-FILTER-03).
3. Every worksheet-zone accounted for by at least one of P-ZONE-01, P-SHEET-02, P-TITLE-05, P-FIT-07, P-CONTAINER-08 (findings OR clean evaluations).

**Fail action:** identify the unaccounted zones, re-run Phase 2 checks against them, re-run V2. If still failing, refuse delivery.

## V3: Handoff-Completeness

**Check:** every field in `dashboard_preflight_report/1` populated per `skill-expertise/handoff_schema.md`. Sentinel values (`null`, `[]`, `"unscanned"`) are acceptable substitutes for empty content. Blank strings and missing keys are NOT acceptable.

**Required fields per schema:**

- `schema_version: dashboard_preflight_report/1`
- `dashboard_name`, `dashboard_id`, `workbook_name`
- `zone_count`, `findings_count_by_severity` (`blocking`, `warning`, `info`)
- `findings` (list; may be empty if dashboard is clean)
- `unscanned_checks` (list of rule IDs skipped with rationale)
- `run_metadata` (timestamp, tool_failures encountered, fallback_paths used)
- `handoff_ready: true` OR `handoff_ready: false` with a `handoff_block_reason`

**Fail action:** identify the missing fields, populate per HC#7 sentinel discipline, re-run V3. If still failing, refuse delivery.

## Gate Execution Order

1. V1 (finding-catalog match) first, cheapest to run.
2. V2 (zone-count reconciliation) second, validates completeness.
3. V3 (handoff-completeness) last, depends on V1 + V2.

## What V-Gate Does NOT Check

Unlike the calc-family 8-check gate, this gate does NOT check:

- Calc-side semantics (that's calc-family's job).
- Runtime interaction firing (that's interaction-validator's job).
- Content correctness of tooltips, annotations, titles (that's caption-and-tooltip-advisor, desktop-spellcheck, i18n-scanner).
- Publish-hygiene items outside dashboard assembly (publish-readiness).

Dashboard-preflight audits assembly hygiene; it does not judge content or runtime behavior.

## Refuse to Fabricate

If V-gate cannot pass after one retry, refuse delivery per HC#8 and diagnose. Never fake a V-gate pass. Never invent a `rule_id`. Never omit a check without recording it as UNSCANNED.
