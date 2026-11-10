# Handoff Schema — `calc_orchestrator_route/1` (Locked)

Every calc-orchestrator invocation emits this schema, including clarifiers and refusals. Schema is versioned; unknown versions refused by downstream.

Orchestrator does NOT emit any of the five peer schemas (`calc_write_handoff/1`, `calc_debug_handoff/1`, `calc_optimize_handoff/1`, `calc_lint_handoff/1`, `calc_inventory_handoff/1`). Those are the peers' exclusive scope. When orchestrator routes to a peer and that peer runs successfully, both schemas travel together in the delivery: the peer's handoff unmodified, plus this `calc_orchestrator_route/1` block alongside.

## Full Schema

```yaml
schema_version: calc_orchestrator_route/1
user_ask: {verbatim_string}
routing_decision: {routed_to_peer | clarifier_fired | refused_non_calc_family | refused_no_match | refused_peer_unavailable}
target_peer: {calc-writer | calc-debugger | calc-optimizer | calc-linter | calc-inventory | null}
candidate_peers:
  - {peer_slug}
  # list of peers considered during classification; may be empty for clarifier fires
routing_rationale: {short_string}
peer_response_relayed: {true | false}
peer_outcome: {succeeded | refused | error | not_applicable}
peer_refusal_reason: {short_string | null}
alternative_peers_named_in_clarifier:
  - {peer_slug}
  # only populated when routing_decision == clarifier_fired
non_calc_family_target: {data-model-documenter | workbook-auditor | join-and-relationship-advisor | data-source-connector | null}
alignment_drift_detected: {true | false}
alignment_drift_notes: {short_string | null}
run_metadata:
  timestamp: {ISO-8601}
  peer_availability_checks: {N}
notes: {optional_free_text}
```

## Field-by-Field

- **schema_version:** always exactly `calc_orchestrator_route/1`.
- **user_ask:** the user's ask verbatim, no paraphrase. Audit-critical.
- **routing_decision:** one of five outcomes:
  - `routed_to_peer` — successfully routed to a calc-family peer.
  - `clarifier_fired` — ambiguous ask; HC#2 clarifier fired; awaiting user response.
  - `refused_non_calc_family` — routed to a non-calc-family peer per HC#3.
  - `refused_no_match` — no peer (calc-family or otherwise) matched; user asked to clarify intent.
  - `refused_peer_unavailable` — target peer's SKILL.md not found at expected path per HC#9.
- **target_peer:** the calc-family peer routed to (only when `routing_decision == routed_to_peer`). Else `null`.
- **candidate_peers:** list of peers considered during Phase 2 classification. Even single-match routes populate this (with one entry) for auditability. Empty list only when `refused_no_match` and no candidates were even considered.
- **routing_rationale:** short string explaining the decision. Examples: "matched calc-debugger's 'this calc is broken' trigger verbatim"; "user named calc-writer explicitly per HC#5"; "ambiguous between calc-debugger and calc-optimizer; clarifier fired"; "no calc-family signal; routing to workbook-auditor for dashboard-level ask."
- **peer_response_relayed:** `true` if orchestrator ran the peer and relayed its response. `false` if clarifier fired, refusal delivered, or peer unavailable.
- **peer_outcome:** `succeeded` if peer ran and delivered its handoff cleanly. `refused` if peer refused per its own HC. `error` if peer errored during its own execution. `not_applicable` for clarifier fires and refusals.
- **peer_refusal_reason:** short string capturing the peer's refusal reason (only when `peer_outcome == refused`). Verbatim from the peer's own refusal message where possible.
- **alternative_peers_named_in_clarifier:** list of peer slugs named in the HC#2 clarifier (only when `routing_decision == clarifier_fired`). Empty list otherwise.
- **non_calc_family_target:** which non-calc-family peer was routed to (only when `routing_decision == refused_non_calc_family`). Else `null`.
- **alignment_drift_detected:** `true` if orchestrator noticed a mismatch between its `skill-expertise/peer_routing.md` trigger list and a peer's actual SKILL.md `Trigger Conditions` section during Phase 1 verification.
- **alignment_drift_notes:** short string describing the drift (only when `alignment_drift_detected: true`).
- **run_metadata:** operational metadata. `timestamp` when routing was delivered. `peer_availability_checks` for how many HC#9 Read calls were made this run.
- **notes:** optional free-text. Common uses: multi-peer match ambiguity notes, unusual clarifier patterns, follow-up peer suggestions.

## Downstream Consumer Expectations

- **The invoked peer's handoff** (whichever `calc_*_handoff/1` it emits) travels alongside `calc_orchestrator_route/1`, unmodified. Downstream consumers of the peer schema read the peer schema; downstream consumers of routing decisions (audit tools, workflow analyzers) read `calc_orchestrator_route/1`.
- **`workbook-auditor`** may consume `calc_orchestrator_route/1` for orchestration-audit rollups (e.g., "user routed 12 asks last week; 8 clarifier fires, 4 direct routes").
- Individual calc-family peers do NOT consume this schema — they consume the user's ask (or an upstream peer's handoff), never orchestrator metadata. Orchestrator is upstream of them, not downstream.

## "Clarifier Fired" Contract

When `routing_decision: clarifier_fired`:
- `target_peer: null`.
- `peer_response_relayed: false`.
- `peer_outcome: not_applicable`.
- `alternative_peers_named_in_clarifier` is a non-empty list of at least 2 peer slugs.
- `routing_rationale` explains the ambiguity (e.g., "ask matched both calc-debugger correctness signal and calc-optimizer perf signal; clarifier needed to distinguish").
- `notes` may include the exact clarifier phrasing used, for consistency across sessions.

## "Refused" Contracts

**`refused_non_calc_family`:**
- `target_peer: null`.
- `non_calc_family_target` names the routed-to peer (e.g., `workbook-auditor`).
- `routing_rationale` explains why the ask was non-calc-family.
- `peer_response_relayed: false`, `peer_outcome: not_applicable`.

**`refused_no_match`:**
- `target_peer: null`, `non_calc_family_target: null`.
- `candidate_peers: []`.
- `routing_rationale`: "no peer matched; user asked to clarify intent."

**`refused_peer_unavailable`:**
- `target_peer` names the peer that would have been routed to.
- `routing_rationale`: "target peer's SKILL.md not found at expected path per HC#9."
- `notes` should include the expected path checked.

## Refuse to Guess

Never fake a routing decision to satisfy the schema. If routing genuinely fails (e.g., no peer available, no clear match), populate the appropriate sentinel and note in `notes`. Never claim `peer_response_relayed: true` without an actual peer invocation. Never claim `target_peer` without matching a real peer slug from the routing table.
