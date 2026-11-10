# Calc Orchestrator

Pure router for calc-family asks. Classifies the user's intent against the five shipped calc-family peers (`calc-writer`, `calc-debugger`, `calc-optimizer`, `calc-linter`, `calc-inventory`), invokes the correct peer by exact slug, and relays the peer's response unmodified plus a `calc_orchestrator_route/1` metadata block. Zero calc-family execution logic of its own.

**Example:** You paste `SUM([Profit]) / SUM([Sales])` and say "help me with this calc." The skill notices the ask is ambiguous (could be write / debug / optimize / lint / inventory), fires an HC#2 one-clarifier naming the three most-likely candidates (`calc-debugger` for correctness, `calc-optimizer` for perf, `calc-linter` for style), waits for your answer, then invokes the peer you named. The peer's response is relayed unmodified, plus a `calc_orchestrator_route/1` block records which peer was chosen and why.

## What it does

Reads the user's ask. Classifies against the peer routing table in `skill-expertise/peer_routing.md`. Cases:

- **Single-match:** routes immediately to that peer by exact slug.
- **Multi-match (2+ peers):** fires an HC#2 one-clarifier naming the candidates. Never picks silently.
- **Non-calc-family match:** refuses with exact-slug routing to `data-model-documenter`, `workbook-auditor`, `join-and-relationship-advisor`, or `data-source-connector`.
- **No match:** refuses, asks user to clarify intent.

Runs a 3-check routing-only V-gate before delivery (V1 peer availability, V2 routing rationale non-empty, V3 trigger-table alignment advisory). Emits `calc_orchestrator_route/1` alongside every routing decision, including clarifiers and refusals.

## When to use it

Fires on ambiguous calc-family asks: "help me with a calc," "I have a calc question," "what should I do with this calc," "which skill handles X," "route my calc ask." Or when the user pastes a formula without a clear verb.

Do NOT invoke when the user's ask clearly matches one peer's positive-trigger phrasing — invoke that peer directly instead. Do NOT invoke when the ask is a non-calc concern (data-model, workbook, join, connection) — route to the appropriate non-calc-family peer.

## What makes this skill distinctive

- **Pure routing scope (HC#1).** Zero calc-family execution logic of its own. Never authors, debugs, optimizes, lints, or inventories. If routing fails, orchestrator refuses — it does not fall back to running calc logic itself.
- **Trigger-table alignment discipline (HC#8).** Peer trigger phrases in `skill-expertise/peer_routing.md` are transcribed verbatim from each peer's shipped SKILL.md.
- **User-named peer wins (HC#5).** If the user names a peer by slug in their ask ("use calc-writer for X"), orchestrator routes there directly. No second-guessing.
- **No silent fallback (HC#4).** If the invoked peer refuses per its own HC, orchestrator relays the refusal unmodified. Never re-routes silently to a different peer.
- **No chain orchestration (HC#6).** Multi-peer chains like "write, then debug, then optimize" get a clarifier explaining each peer runs standalone. Orchestrator does not run internal loops.
- **Runtime peer availability (HC#9).** Before routing, orchestrator confirms the target peer's SKILL.md exists at its expected path. Never routes to a missing peer.

## Handoff contract

Orchestrator does NOT emit any peer schema (`calc_write_handoff/1` through `calc_inventory_handoff/1`) — those are the peers' exclusive scope. Orchestrator emits `calc_orchestrator_route/1` alongside every routing decision, including clarifiers and refusals. The peer's own handoff travels alongside, unmodified.

Required non-blank fields in `calc_orchestrator_route/1`: `user_ask`, `routing_decision`, `target_peer` (or `null`), `candidate_peers`, `routing_rationale`, `peer_response_relayed`.

Downstream consumers of routing metadata: `workbook-auditor` may consume for orchestration-audit rollups. Individual calc-family peers do NOT consume this schema — they consume the user's ask directly, never orchestrator metadata.

## Hard constraints in force

- HC#1: pure routing; zero execution logic.
- HC#2: one-clarifier discipline for ambiguous asks.
- HC#3: exact-slug refusals to non-calc-family peers.
- HC#4: no silent fallback after a peer refuses.
- HC#5: user-named peer wins.
- HC#6: no chain orchestration.
- HC#7: emit routing metadata alongside every decision.
- HC#8: trigger-table alignment with peer SKILL.md files.
- HC#9: runtime peer availability check.
- HC#10: no prior-turn diagnosis.

Full spec in `SKILL.md`. Peer Routing Table in `skill-expertise/peer_routing.md`. Validation Gate in `skill-expertise/validation_gate.md`. Handoff schema in `skill-expertise/handoff_schema.md`.
