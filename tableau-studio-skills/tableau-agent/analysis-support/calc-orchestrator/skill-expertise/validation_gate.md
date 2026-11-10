# Validation Gate (Routing-Only, 3 Checks)

Every routing decision passes all 3 checks before delivery. Any failure blocks the routing per HC#7. Fail-open is NOT applied — orchestrator is pure routing with no mutation risk, so a V-gate failure means the routing decision itself is incomplete or inconsistent, not a mutation risk. Refuse to route and diagnose.

Scoped narrowly because orchestrator doesn't execute calc logic — the invoked peer runs its own 3-check (calc-inventory) or 8-check + R-EQUIV-01 (calc-writer/debugger/optimizer/linter) gate. Orchestrator's V-gate covers only routing correctness.

## V1 — Peer Availability

**Check:** the target peer's SKILL.md exists at its expected path per HC#9.

Verification: Read the expected path (`skills/skill-<peer-name>/SKILL.md`). Confirm the file exists and its frontmatter `name` field matches the expected peer slug.

Peer paths verified:
- `calc-writer` → `skills/calc-writer/SKILL.md`
- `calc-debugger` → `skills/calc-debugger/SKILL.md`
- `calc-optimizer` → `skills/calc-optimizer/SKILL.md`
- `calc-linter` → `skills/calc-linter/SKILL.md`
- `calc-inventory` → `skills/calc-inventory/SKILL.md`

**Fail action:** if the target peer's SKILL.md is missing or mismatched, refuse routing per HC#9. Set `routing_decision: refused_peer_unavailable` in the handoff. Never route to a peer that isn't available. Do not fall back to a different peer.

## V2 — Routing Rationale Non-Empty

**Check:** every routing decision has a non-blank `routing_rationale` field in the handoff.

Sentinel values acceptable for other fields (`target_peer: null` for clarifier fires and refusals), but `routing_rationale` MUST be a real explanation, never blank, never a placeholder.

**Fail action:** if rationale cannot be articulated, the routing decision itself is suspect. Refuse to route and diagnose. Do not emit a routing decision with a fake rationale.

## V3 — Trigger-Table Alignment (Advisory)

**Check:** the peer routing table in `skill-expertise/peer_routing.md` matches each shipped peer's SKILL.md `Trigger Conditions` section.

Verification (best-effort, non-blocking): during Phase 1 peer availability check, briefly compare the peer_routing.md trigger list for the target peer against the peer's own SKILL.md trigger list. If drift is detected, note in handoff `alignment_drift_detected: true` with a short description, but proceed with routing.

It does not block the current routing decision — orchestrator delivers, notes the drift, and flags it for review.

**Fail action:** V3 does NOT block routing. Drift is advisory. Note in handoff and continue.

## Gate Execution Order

1. V1 (peer availability) first — cheapest to run, catches the most consequential failure (routing to a missing peer).
2. V2 (routing rationale non-empty) next — validates the routing decision has real reasoning.
3. V3 (trigger-table alignment) last — advisory only, never blocks.

## What V-Gate Does NOT Check

Unlike calc-writer/debugger/optimizer/linter's 8-check gate (which validates calc semantics, aggregation, LOD syntax, return type, R-EQUIV-01) or calc-inventory's 3-check gate (which validates catalog schema, batch reconciliation, reference-graph consistency), this gate does NOT check:

- Whether the target peer will succeed at its own task — that's the peer's own V-gate's responsibility.
- Whether the user's ask is well-formed — orchestrator routes even ambiguous or malformed asks (via clarifier or refusal).
- Whether the peer's handoff, once returned, is schema-valid — the peer emits its own handoff; orchestrator relays it unmodified.
- Runtime equivalence — orchestrator does not rewrite calcs. No R-EQUIV-01 needed.

Orchestrator's V-gate is scoped to the routing decision itself, not to the outcome of the invoked peer.

## Refuse to Fabricate

If V-gate cannot pass on V1 or V2, refuse the routing decision. Never fake a peer availability check. Never emit a routing decision with a blank or placeholder rationale. Never suppress an alignment-drift finding to make V3 pass — flag it in the handoff regardless.
