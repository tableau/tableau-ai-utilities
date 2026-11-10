# Diff Catalog Reference
Locked reference file for calc-migrator-diff-report's 7-finding-type catalog. Cited by HC#3 and V1. Every calc in the migration handoff maps against every applicable finding type; multi-type findings tier by highest severity. Every finding type below includes detection criteria, evidence pattern, threshold defense (where applicable), edge cases, and worked examples.

## Finding Type Precedence

**Severity tiering.** Warning-tier findings take precedence over Info-tier when multi-type tagging fires. Order among Warning-tier: finding ID ascending (DIFF-SENTINEL-03 before DIFF-VALIDATION-04). Order among Info-tier: finding ID ascending (DIFF-CLEAN-01 before DIFF-REMAP-02 before DIFF-IDENTICAL-07).

**Multi-type tagging.** A calc can trigger multiple finding types simultaneously (common: DIFF-REMAP-02 + DIFF-VALIDATION-04 both fire when field remap applied but target formula still fails validation). Skill emits all triggered finding IDs in `findings_triggered[]`; severity tier set by highest match.

**Fallback discipline.** When a finding's detection depends on data that's unavailable per calc (handoff missing formula body, re-validation tool call fails), skill emits `"unable to determine"` sentinel per HC#5. Other finding types on the same calc still evaluate.

***

## DIFF-CLEAN-01: Clean Migration

**Severity:** Info
**Signal source:** handoff + re-validation
**Routing:** None (no action needed)
**Detection:** Calc migrated successfully with all fields remapped, target formula passes re-validation, no sentinels emitted by calc-migrator, no staleness detected. All three conditions must hold.

**Evidence pattern:** `calc_name: "Profit Ratio"; source_formula: "SUM([Profit]) / SUM([Sales])"; target_formula: "SUM([Orders (Migrated)].[Profit]) / SUM([Orders (Migrated)].[Sales])"; field_remaps: [{from: "[Profit]", to: "[Orders (Migrated)].[Profit]"}, {from: "[Sales]", to: "[Orders (Migrated)].[Sales]"}]; sentinels: []; validation_status: "passed"; stale: false`.

**Edge cases:**
- Calc migrated with 0 field remaps AND target formula identical to source → fires DIFF-IDENTICAL-07 instead (no-op migration).
- Calc migrated with sentinels emitted → fires DIFF-SENTINEL-03 instead of DIFF-CLEAN-01.
- Calc migrated and validation status shows partial pass (e.g., syntax OK but type warning) → does not fire DIFF-CLEAN-01; fires DIFF-VALIDATION-04 instead.

**Worked example:**
Calc `Profit Ratio` migrates from Orders to "Orders (Migrated)" with `[Profit]` and `[Sales]` remapped to their target-DS equivalents. Handoff shows `validation_status: passed`, `sentinels: []`. Re-validation confirms formula-hash matches current state. Fires DIFF-CLEAN-01. Severity Info. No routing offered — this is a successful migration.

***

## DIFF-REMAP-02: Field Remap Applied

**Severity:** Info
**Signal source:** handoff `field_remaps[]`
**Routing:** None (informational)
**Detection:** Calc has one or more entries in handoff `field_remaps[]` for that calc. Fires informationally to surface the remaps to the diff reader. Does not itself indicate a problem.

**Evidence pattern:** `calc_name: "Regional Sales"; field_remaps: [{from: "[Sales]", to: "[Orders (Migrated)].[Sales]"}, {from: "[Region]", to: "[Orders (Migrated)].[Region]"}]; remap_count: 2`.

**Edge cases:**
- 0 field remaps → does not fire (nothing to surface).
- Field remap applied AND target formula still fails validation → DIFF-REMAP-02 fires informationally AND DIFF-VALIDATION-04 fires Warning-tier.
- Field remap uses handoff's exact `from` / `to` field references → skill quotes byte-identical per HC#6.

**Worked example:**
Calc `Regional Sales` = `SUM([Sales])` migrates to `SUM([Orders (Migrated)].[Sales])` with one remap entry: `{from: "[Sales]", to: "[Orders (Migrated)].[Sales]"}`. Fires DIFF-REMAP-02. Severity Info. No routing offered — surfacing the remap so the reader can see what changed.

***

## DIFF-SENTINEL-03: Sentinel Emitted by Calc-Migrator

**Severity:** Warning
**Signal source:** handoff `sentinels[]`
**Routing:** `calc-writer` (manual authoring)
**Detection:** Calc has one or more entries in handoff `sentinels[]` for that calc. Sentinels indicate calc-migrator was unable to resolve a field or the entire calc during migration; the target formula may be incomplete or reference `"unable to determine"` placeholders.

**Common sentinel reasons (from calc-migrator's contract):**
- Field on source DS has no counterpart on target DS.
- Calc references a parameter that doesn't exist on the target-DS scope.
- Calc uses a datasource-specific function (e.g., `MAKEPOINT` with spatial-column dependency) that the target DS doesn't support.
- Calc references a hidden field that couldn't be resolved.

**Evidence pattern:** `calc_name: "Custom Region Grouping"; sentinels: [{field: "[Custom Region]", reason: "no counterpart on target DS", placeholder: "unable to determine"}]; target_formula: "IIF([Custom Region] = 'North', 1, 0)  /* WARNING: [Custom Region] sentinel */"`.

**Edge cases:**
- Sentinel emitted but calc-migrator still produced a partial target formula → skill surfaces both the sentinel and the partial formula; routing to calc-writer for manual completion.
- Sentinel emitted and target formula is empty → skill surfaces the sentinel with an empty-target-formula flag; routing to calc-writer for from-scratch authoring.
- Multiple sentinels on one calc → skill enumerates all; routing to calc-writer once with the full sentinel list.

**Worked example:**
Calc `Custom Region Grouping` = `IIF([Custom Region] = 'North', 1, 0)`. Source DS has `[Custom Region]`; target DS does not. Handoff shows `sentinels: [{field: "[Custom Region]", reason: "no counterpart on target DS"}]`. Fires DIFF-SENTINEL-03. Severity Warning. Routing: calc-writer. Desktop next step: "Author `Custom Region Grouping` on the target DS manually, using the closest equivalent field. Route to calc-writer for guided authoring."

***

## DIFF-VALIDATION-04: Validation Failure Post-Migration

**Severity:** Warning
**Signal source:** handoff `validation_status` + re-validation
**Routing:** `calc-debugger` (NULL / error diagnosis)
**Detection:** Target formula fails validation. Fires when handoff `validation_status: "failed"` OR when re-validation of the target formula against the current workbook state returns an error, type mismatch, or NULL propagation risk.

**Validation status values (from calc-migrator's contract):**
- `passed`: syntax OK, types check, no NULL propagation risk.
- `failed`: hard failure (syntax error, type mismatch, undefined reference).
- `passed_with_warnings`: syntax OK but a type coercion or NULL-propagation risk was flagged.

**Evidence pattern:** `calc_name: "Weighted Discount"; source_formula: "SUM([Discount]) * [Price Weight]"; target_formula: "SUM([Orders (Migrated)].[Discount]) * [Price Weight]"; validation_status: "failed"; validation_error: "[Price Weight] parameter not in target-DS scope"`.

**Edge cases:**
- `passed_with_warnings` → still fires DIFF-VALIDATION-04 as Warning-tier; user should route to calc-debugger to review.
- Validation status is `null` or missing on handoff → emit `"unable to determine"` sentinel per HC#5; do not assume pass or fail.
- Re-validation contradicts handoff (handoff says passed, re-validation says failed) → fires DIFF-VALIDATION-04 AND fires DIFF-STALE-05 because state must have changed.

**Worked example:**
Calc `Weighted Discount` = `SUM([Discount]) * [Price Weight]` migrates to `SUM([Orders (Migrated)].[Discount]) * [Price Weight]`. `[Price Weight]` is a parameter that exists in source-DS scope but not target-DS scope. Handoff shows `validation_status: "failed"`, `validation_error: "[Price Weight] parameter not in target-DS scope"`. Fires DIFF-VALIDATION-04. Severity Warning. Routing: calc-debugger. Desktop next step: "Diagnose `Weighted Discount` on the target DS — parameter scope mismatch. Route to calc-debugger for NULL / error diagnosis."

***

## DIFF-STALE-05: Staleness Detected

**Severity:** Warning
**Signal source:** V5 formula-hash mismatch per calc, workbook-fingerprint mismatch
**Routing:** `calc-migrator` (re-run)
**Detection:** Formula-hash of the target formula from the handoff does not match the current workbook's formula-hash for that calc name on the target datasource, OR workbook fingerprint from the handoff does not match current workbook fingerprint. Either condition fires. Per-calc mismatch fires DIFF-STALE-05 for that calc; run-level mismatch marks the whole run stale and fires DIFF-STALE-05 for every calc.

**Evidence pattern:** `calc_name: "Profit Ratio"; handoff_formula_hash: "a4f2..."; current_formula_hash: "b3e1..."; stale: true; stale_reason: "target formula edited on workbook since migration ran"`.

**Edge cases:**
- Handoff fingerprint matches but per-calc formula-hash mismatches → user likely edited a specific calc after migration; fires DIFF-STALE-05 for that calc only.
- Handoff fingerprint mismatches → workbook state changed at any level since migration; skill marks the run stale and every calc's `stale` flag becomes `true`.
- Calc exists in handoff but calc no longer exists in current workbook (user deleted it) → skill emits `"unable to determine"` sentinel for formula-hash comparison; fires DIFF-STALE-05 with reason "calc no longer exists in target DS."

**Worked example:**
Calc `Profit Ratio` was migrated with `target_formula: "SUM([Orders (Migrated)].[Profit]) / SUM([Orders (Migrated)].[Sales])"`. Handoff formula-hash `a4f2...`. User then edited the calc on Desktop, changing it to `SUM([Orders (Migrated)].[Profit]) / SUM([Orders (Migrated)].[Adjusted Sales])`. Current formula-hash `b3e1...`. Fires DIFF-STALE-05. Severity Warning. Routing: calc-migrator. Desktop next step: "Re-run calc-migrator to refresh the migration handoff, or revert the manual edit on `Profit Ratio`."

***

## DIFF-UNMIGRATED-06: Unmigrated Calc

**Severity:** Warning
**Signal source:** source-DS calc list vs. handoff `migrated_calcs[]`
**Routing:** `calc-migrator` (re-run with wider scope)
**Detection:** A calc exists on the source datasource but is not present in the handoff `migrated_calcs[]`. Indicates calc-migrator was run with a narrower scope than the full source-DS calc list, or a calc was excluded by filter, or a calc failed migration and was silently dropped.

**Evidence pattern:** `source_datasource: "Orders"; source_calc_list_count: 12; migrated_calcs_count: 10; unmigrated_calcs: ["Legacy Discount Rate", "Q1 2025 Override"]`.

**Edge cases:**
- User intentionally excluded calcs from migration → skill still fires DIFF-UNMIGRATED-06 informationally; user can acknowledge by declining to route.
- Source-DS calc list unreadable via `list-available-fields` → emit `"unable to determine"` sentinel per HC#5; do not assume unmigrated.
- Handoff shows `migrated_calcs[]` matches source-DS calc list exactly → rule clears; not fired.

**Worked example:**
Source DS `Orders` has 12 calcs. Handoff `migrated_calcs[]` lists 10. Two calcs (`Legacy Discount Rate`, `Q1 2025 Override`) are in source but not in handoff. Fires DIFF-UNMIGRATED-06 for each. Severity Warning. Routing: calc-migrator. Desktop next step: "Re-run calc-migrator with wider scope to include `Legacy Discount Rate` and `Q1 2025 Override`, or acknowledge these were intentionally excluded."

***

## DIFF-IDENTICAL-07: Formula-Identical Migration

**Severity:** Info
**Signal source:** handoff formula comparison
**Routing:** None (informational; may indicate no-op migration)
**Detection:** Handoff shows `target_formula` byte-identical to `source_formula` AND no field remaps applied (`field_remaps: []`). Fires informationally to flag no-op migrations where the target formula didn't actually need any change to work on the target DS.

**Evidence pattern:** `calc_name: "Constant Threshold"; source_formula: "0.15"; target_formula: "0.15"; field_remaps: []; identical: true`.

**Edge cases:**
- Target formula identical AND field remaps present → does not fire DIFF-IDENTICAL-07 (remaps must be empty); fires DIFF-REMAP-02 instead.
- Target formula identical AND validation status `passed` → fires DIFF-IDENTICAL-07 alone; migration was a genuine no-op.
- Target formula identical AND validation status `failed` → fires DIFF-IDENTICAL-07 AND DIFF-VALIDATION-04 (rare but possible if datasource semantics differ).

**Worked example:**
Calc `Constant Threshold` = `0.15` (a bare constant). Source formula identical to target formula. No field remaps. Fires DIFF-IDENTICAL-07. Severity Info. No routing offered — informational flag that this calc's migration was a no-op (may indicate the calc could have been a parameter, but that's calc-hygiene-scan's concern via CH-HARDCODED-05).

***

## Failure Modes This Reference Prevents

- **False positive on DIFF-CLEAN-01.** Requires all three conditions (all fields remapped, validation passed, no sentinels). Any one missing routes to a Warning-tier finding instead.
- **Silent DIFF-STALE-05 miss.** V5 formula-hash per-calc check plus workbook-fingerprint check per HC#13. Both mechanisms independent; either fires the finding.
- **Fabricated field remaps.** DIFF-REMAP-02 evidence comes from handoff `field_remaps[]`; skill quotes verbatim per HC#6 and never infers.
- **DIFF-UNMIGRATED-06 false negative.** Requires enumerating source-DS calc list via `list-available-fields` and comparing to handoff. If `list-available-fields` fails on that DS, sentinel per HC#5 rather than silent miss.
- **DIFF-VALIDATION-04 dropped on `passed_with_warnings`.** Warning-tier finding fires even on `passed_with_warnings` so user can route to calc-debugger to review.
- **Confusion between diff-report's `diff_mode` and migration diff content.** `diff_mode` tracks this skill's own idempotency (fresh_scan / reused_verbatim / targeted_rescan). Migration-diff content is always the 7-finding-type report; `diff_mode` doesn't change what content is shown.
- **Byte-modified source or target formula in output.** HC#6 quotes handoff data verbatim; never paraphrases or reformats.
- **Skipping a finding on a specific calc when unresolvable.** Sentinel per HC#5, not silent skip.
