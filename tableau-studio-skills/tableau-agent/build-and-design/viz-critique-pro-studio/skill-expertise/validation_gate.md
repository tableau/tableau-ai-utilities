# Validation Gate (Read-Only, 5 Checks)

Every critique passes V1-V4 before delivery. V5 (Drift-Sample) fires only on second-in-session invocation with the same image; it does not block delivery, it attaches a drift-disclosure banner. Any failure on V1-V4 blocks delivery per HC#8. Fail-open is NOT applied since the skill is read-only.

## V1: Domain Coverage

**Check.** Every domain (1-7) has a score with rationale, or sentinel `"unscanned"` with reason (only for HC#12 long-form partial reports on Domains 4 and 7).

**Required per domain:**

- `domain_id` (1-7).
- `domain_name`.
- `score` (1-10 with optional half-point) OR sentinel `"unscanned"` with `reason` populated.
- `rationale` citing at least one image signal (or workbook XML signal if in XML-context mode).
- `confidence` (High / Medium / Low) when the signal is ambiguous.

**Sentinel `"unscanned"` acceptable only for:**

- Domain 4 (Layout) on long-form partial image per HC#12.
- Domain 7 (Interactive) on long-form partial image per HC#12.

Never acceptable for Domains 1, 2, 3, 5, 6.

**Fail action.** Re-derive the score from the domain's reference file. If a second run still fails, refuse delivery per HC#8. Never leave the score blank.

## V2: Ethics Cap Enforcement

**Check.** If any Critical or Warning ethics violation fired in Phase 1, the overall score is at or below the cap.

**Verification steps:**

1. Enumerate every ethics violation with its severity.
2. Determine highest cap (Critical = 59; Warning = 79; Info = no cap).
3. Confirm overall score is at or below the cap.
4. Confirm banner rendered as first section of the report per `ethics_privacy_gatekeeper.md`.

**Fail action.** Re-apply the cap. If HC#11 was bypassed, refuse delivery per HC#8. Never let the cap be silently overridden.

## V3: Handoff Completeness

**Check.** Every field in `viz_critique_report/1` populated per `skill-expertise/handoff_schema.md`.

**Verification steps:**

1. Every required field present with a non-blank value or sentinel.
2. `domains` list has 7 entries (one per domain, some potentially UNSCANNED).
3. **Per-domain `signals_evaluated` array is non-empty (minimum 1 signal per scored domain).** UNSCANNED domains may have empty signals_evaluated only when accompanied by an UNSCANNED reason.
4. `ethics_violations` list populated (empty `[]` if none fired).
5. `overall_score` populated with the ethics-capped value if applicable.
6. `raw_overall_score` populated with the pre-cap value for transparency.
7. `tier` matches the overall_score range.
8. `rebuild_handoff_payload` populated only when overall score is below 50 (Rework tier) or specific chart/layout fixes route to downstream skills.

**Fail action.** Identify missing field, populate with correct value or sentinel, re-run V3. If a second run still fails, refuse delivery per HC#8.

## V4: Mode and Determinism

**Check.** Mode field is populated and matches the workbook state. Image Only reports include the reduced-accuracy disclaimer. Domain scoring order matches the locked order. Anchor-matched field is populated per domain.

**Verification steps:**

1. `mode` field is `workbook_scan` or `image_only`; never null.
2. If `mode == image_only`, `image_only_disclaimers` includes the Domain 4 and Domain 7 reduced-accuracy notes.
3. `mode_source` is one of `workbook_open`, `workbook_closed`, `user_override`.
4. Per-domain `anchor_matched` populated (or null only when the domain is UNSCANNED per HC#12).
5. Domain scoring order in the report matches the locked order: Audience, Context, Chart, Layout, Type, Accessibility, Interaction.
6. Ethics cap application is the last score-modifying step (`overall_score <= raw_overall_score` when a cap fired).

**Fail action.** Repopulate the missing mode field, disclaimer, or anchor. If domain order was violated, re-order the report before delivery. If a second run still fails, refuse delivery per HC#8.

## V5: Drift-Sample (Non-Blocking)

**Check.** On second-in-session invocation targeting the same image, per-domain scores must not drift more than 1 point from the cached prior run.

**Detection strategy (hash-first with user-declared fallback):**

1. On first invocation, compute an image hash and cache it against the per-domain score array for the session.
2. On subsequent invocation, compute the hash of the current image and compare against the cache.
3. If hashes match, run drift comparison.
4. If hash is unavailable, unreliable, or ambiguous (e.g., paste-format drift), fall back to explicit user re-run declaration ("run it again on the same image," "same image, re-score," or equivalent).

**Verification steps:**

1. Retrieve cached per-domain scores keyed by image hash (or user-declared same-image flag).
2. Compute absolute delta per domain between new run and cached run.
3. For each domain, verify `abs(new_score - cached_score) <= 1`.
4. If any domain drifts more than 1 point, mark the drift and attach the disclosure banner.

**Drift-disclosure banner text (Tier A, one line):**

`Score drift detected: Domain [N] shifted [X] points from prior run. User decides which run to trust.`

**Tier B rendering:** A "Drift Sample" subsection under the ethics section listing every domain with drift, the prior score, the new score, and the delta.

**Non-blocking behavior.** V5 never blocks delivery. Report ships with the drift banner attached. HC#17 enforces the banner; V-gate output notes the drift for the fix log.

**Fail action.** Not applicable; V5 disclosure is the action. If drift patterns recur across multiple sessions, sharpen the offending domain's decision tree in its reference file per the fix log.

## Gate Execution Order

1. V1 (domain coverage) first. Cheapest to run; catches most failures.
2. V2 (ethics cap enforcement) next. Validates the cap was applied correctly.
3. V3 (handoff completeness) next. Depends on V1 and V2 passing.
4. V4 (mode and determinism) next. Confirms mode transparency and anchor-first scoring hygiene.
5. V5 (drift-sample) last. Non-blocking; attaches drift banner if same-image second run drifts more than 1 point per domain.

## What V-Gate Does NOT Check

- Whether the runtime behavior of interactive elements matches the design signals (route to `interaction-validator`).
- Whether the underlying data has quality issues (route to `data-quality-review`).
- Whether the chart-type advisory would produce a different verdict than Domain 3 (route to `chart-swap-advisor` for per-worksheet advisory).
- Whether text-copy is spell-correct (route to `desktop-spellcheck`).
- Whether format strings are drift-free (route to `format-drift-scanner`).

## Refuse to Fabricate

If the V-gate cannot pass after one retry, refuse delivery and diagnose. Never fake a V-gate pass. Never invent a domain score or an ethics violation. Never bypass the ethics cap.
