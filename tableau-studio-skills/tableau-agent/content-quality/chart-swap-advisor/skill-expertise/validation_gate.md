# Validation Gate (Read-Only, 3 Checks)

Every recommendation passes all 3 checks before delivery. Any failure blocks delivery per HC#8. Fail-open is NOT applied since the skill is read-only.

## V1: Classification Confidence

**Check.** Every question-type classification carries a High / Medium / Low tag with the signals that support it.

**Required per classification.**

- `question_type` from the 9-type taxonomy (one of: Temporal, Categorical, Composition, Distribution, Correlation, Ranking, Geographic, Status/KPI, Sequential) OR `refused_no_match` with rationale.
- `confidence` (`High`, `Medium`, or `Low`).
- `supporting_signals` list (non-empty for High and Medium; may include a single weak-signal note for Low).
- `classification_notes` (required when confidence is Low; explains why the closest match is weak).

**Sentinel values acceptable.** `null` for `classification_notes` when confidence is High or Medium. `"unscanned"` for `confidence` when `get-worksheet-xml` fallback failed and mark type could not be inferred.

**Fail action.** Re-derive the classification from the taxonomy. If a second run still fails, refuse delivery per HC#8. Never leave the confidence blank.

## V2: Anti-Pattern Gate Completeness

**Check.** Every run evaluates the full anti-pattern catalog against the current chart.

**Verification steps.**

1. Every anti-pattern ID in `skill-expertise/anti_patterns.md` (AB-1 through AB-6, W-1 through W-7, I-1 through I-2) is evaluated. Skipped IDs are a V2 fail.
2. Auto-Block anti-patterns cannot be silently downgraded to Warning or Info. HC#11 enforcement is a V2 check.
3. Multiple matching anti-patterns all fire; the verdict is the highest severity.

**Fail action.** Identify the skipped or downgraded anti-pattern. Re-run the gate. If a second run still fails, refuse delivery per HC#8.

## V3: Handoff Completeness

**Check.** Every field in `chart_swap_recommendation/1` populated per `skill-expertise/handoff_schema.md`.

**Verification steps.**

1. Every required field present with a non-blank value or a sentinel (`null`, `[]`, `"unscanned"`).
2. `rebuild_handoff_payload` populated when verdict is Swap Recommended or Anti-Pattern Block; empty (`null`) when verdict is Keep.
3. `anti_patterns_matched` list is empty (`[]`) when no anti-pattern fires, never blank.

**Fail action.** Identify the missing field, populate with the correct value or sentinel, and re-run V3. If a second run still fails, refuse delivery per HC#8.

## Gate Execution Order

1. V1 (classification confidence) first. Cheapest to run; catches most failures.
2. V2 (anti-pattern gate completeness) next. Validates the recommendation logic ran.
3. V3 (handoff completeness) last. Depends on V1 and V2 passing to have complete data.

## What V-Gate Does NOT Check

Unlike calc-family's 8-check gate, this gate does NOT check:

- Whether the recommended chart type will render correctly in Desktop (runtime; `worksheet-builder` owns this).
- Whether the user will accept the recommendation (user-side decision).
- Whether the current chart's underlying data is correct (route to `data-quality-review`).
- Whether the recommended chart's calc dependencies exist (route to `calc-orchestrator`).
- Format-string drift on the current chart (route to `format-drift-scanner`).

## Refuse to Fabricate

If the V-gate cannot pass after one retry, refuse delivery and diagnose. Never fake a V-gate pass. Never invent a supporting signal to reach a Medium or High confidence tag.
