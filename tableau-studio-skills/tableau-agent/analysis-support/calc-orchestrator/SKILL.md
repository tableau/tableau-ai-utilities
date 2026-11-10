---
name: calc-orchestrator
description: "Use when the user says 'Help me with a calc', 'I have a calc question', 'which skill handles this calc?' Routes an unclear calculation request to the right calc skill (write, debug, optimize, lint, or inventory), asking one clarifying question if two could fit."
---

# Calc Orchestrator

## When to use (full trigger detail)

Classify a calc-related ask against the five shipped calc-family peers (calc-writer, calc-debugger, calc-optimizer, calc-linter, calc-inventory) and route to the correct peer by exact slug. Pure routing skill. Zero calc-family execution logic of its own. Fires HC#4 one-clarifier when the ask matches 2+ peers. Refuses with exact-slug routing to non-calc-family skills (join-and-relationship-advisor, workbook-auditor, data-model-documenter, data-source-connector) when the ask isnt a calc-family concern. Relays the invoked peers handoff unmodified and appends a top-level calc_orchestrator_route/1 block naming which peer was chosen and why. Triggers on ambiguous asks like help me with a calc, I have a calc question, what should I do with this calc, which skill handles X, or route my calc ask. Do NOT trigger when the users ask clearly matches one peers positive-trigger phrasing (invoke that peer directly instead), when the ask is a non-calc data-model or workbook concern, or when the user names a specific peer by slug.

## Purpose

Pure router for calc-family asks. Classifies intent against the five shipped peers, invokes the correct one, and gets out of the way. Zero calc-family execution logic of its own.

## Trigger Conditions

Positive triggers: help me with a calc, I have a calc question, what should I do with this calc, which skill handles X, route my calc ask, or any calc-related ask where the users phrasing does not clearly match one specific peers positive-trigger table.

Do NOT trigger on the following. Route directly to the named peer or refuse per Non-Match Handling.

| User ask | Route to |
|---|---|
| Write a new calc for... | `calc-writer` directly, no orchestration needed |
| This calc is broken / returns wrong values / errors. | `calc-debugger` directly |
| This calc is slow / optimize it / speed this up. | `calc-optimizer` directly |
| Lint this / check style / rewrite for readability. | `calc-linter` directly |
| Inventory / list all calcs / catalog my calculated fields. | `calc-inventory` directly |
| User names a specific peer by slug (e.g., use calc-writer for X). | The named peer directly |
| Document the data model / tables and relationships. | `data-model-documenter` |
| This dashboard is slow / audit the whole workbook. | `workbook-auditor` |
| This join / relationship is slow. | `join-and-relationship-advisor` |
| Connect a data source / set up a connection. | `data-source-connector` |
| Why was this routed differently yesterday? | Scripted prior-turn-diagnosis refusal (no visibility). |

## Scope Boundaries

- IN: classifying calc-family asks against the five peers locked trigger tables, invoking the correct peer by exact slug, firing an HC#4 one-clarifier when 2+ peers match, refusing non-calc-family asks with exact-slug routing to the appropriate non-calc-family skill, emitting `calc_orchestrator_route/1` routing metadata alongside the invoked peers handoff.
- OUT: authoring, debugging, optimizing, linting, or inventorying calcs (each is the exclusive scope of the corresponding peer); running V-gates (only peers author, and each has its own gate); resolving field references (peers do this at their Phase 1); emitting any of the five peer schemas (`calc_write_handoff/1` through `calc_inventory_handoff/1`) directly; running multi-peer chains like write then debug then optimize as a single orchestrated pass (each peer runs standalone; if user wants a chain, they invoke each peer in turn or use each peers HC#1 sequential-mode).

### Edge-Case Boundaries

| Edge Case | Handling |
|---|---|
| Ask clearly matches one peers positive-trigger phrasing | Route immediately to that peer by exact slug. No clarifier. `calc_orchestrator_route/1` records the single-match rationale. |
| Ask matches 2+ peers positive-trigger phrasing | HC#2 one-clarifier: name the candidate peers explicitly (e.g., This could be `calc-debugger` for correctness or `calc-optimizer` for perf. Which is it?). Never pick silently. |
| Ask contains no calc-family signal but is data-model or workbook-level | Refuse and route to the appropriate non-calc-family peer by exact slug (`join-and-relationship-advisor`, `workbook-auditor`, `data-model-documenter`, `data-source-connector`). |
| Ask is ambiguous between help me with a calc (orchestrator) and a specific peer (e.g., user pastes a formula but doesnt say what they want) | Fire the HC#2 clarifier naming the most likely 2-3 peers. Never assume intent. |
| User names a peer explicitly (use calc-writer for X) | Route to that peer directly per HC#5. Do not second-guess the users routing choice. |
| Peers handoff arrives with an error state (peer refused per its own HC) | Relay the refusal unmodified per HC#4. Append `calc_orchestrator_route/1` with `outcome: peer_refused` and the peers refusal reason. Do not attempt fallback to another peer. |
| User asks for a multi-peer chain in one message (e.g., write, then lint, then inventory it) | Fire an HC#2 clarifier: each peer runs standalone; want me to route to `calc-writer` first, then you re-invoke `calc-linter` and `calc-inventory` afterward on the resulting calc? Never orchestrate a chain internally per HC#6. |
| User asks a question about the calc family itself (what does calc-linter do?) | Answer briefly from the calc-family portfolio, no peer invoked. Route the actual work to the correct peer only when the user makes an actionable ask. |
| Non-calc-family ask arrives (e.g., make this dashboard prettier) | Refuse with exact-slug routing to the non-calc-family peer per HC#3. Never absorb. |
| The invoked peer emits an unknown schema version | Route back to the user: Downstream peer emitted schema version X, which I cannot relay. Verify peer version compatibility. Never fake a schema translation. |
| The invoked peer errors mid-run (a tool-level failure, distinct from a refusal per its own HC) | Summarize the error in one plain sentence (which step failed, whether anything changed, what to try next); put the raw error only in the route metadata `notes`. Set `peer_outcome: error` in `calc_orchestrator_route/1`, `peer_response_relayed: false`. Never re-route to another peer and never silently retry the same peer — surface the error and let the user decide whether to retry. |
| Target peers SKILL.md not found at expected path | Refuse per HC#9. Report the missing peer to the user; ask them to install or verify path. Never route to a peer that isnt available. |
| Users answer to an HC#2 clarifier does not disambiguate (e.g., both / either / not sure / an answer that names a peer NOT in the clarifiers candidate list) | Fire exactly one follow-up clarifier that either narrows to a single peer OR asks the user to pick the closest fit from the original candidate list. Never route silently to a default. Never chain more than one follow-up clarifier per session. If the user still cannot disambiguate after the follow-up, refuse and ask the user to reframe the ask from scratch. Record in handoff `notes: clarifier follow-up fired; user response was [x]; resolved to [peer] OR refused.` |

## Hard Constraints

- HC#1: Pure routing. Zero calc-family execution logic of its own. Never authors, debugs, optimizes, lints, or inventories a calc. If the routing targets peer cant run, orchestrator refuses and reports the state, never falls back to executing calc logic itself.
- HC#2: One-clarifier discipline. Ambiguous asks get exactly one combined clarifier naming the candidate peers explicitly, never chained.
- HC#3: Exact-slug refusals for non-calc-family asks. Route to `join-and-relationship-advisor`, `workbook-auditor`, `data-model-documenter`, or `data-source-connector` by name when the ask isnt a calc-family concern. Never absorb.
- HC#4: No silent fallback. If the invoked peer refuses per its own HC, orchestrator relays the refusal unmodified. Never re-route silently to a different peer.
- HC#5: Trust the users explicit peer choice. If the user names a peer by slug, route to that peer, do not second-guess.
- HC#6: No chain orchestration. Multi-peer chains (write then debug then optimize) get a clarifier explaining each peer runs standalone. Orchestrator does not run internal loops across peers.
- HC#7: Emit `calc_orchestrator_route/1` metadata alongside every routing decision, including refusals and clarifiers. Never route silently without leaving an audit trail.
- HC#8: Trigger-table alignment. Peer trigger tables in `skill-expertise/peer_routing.md` MUST match each peers shipped SKILL.md verbatim.
- HC#9: Runtime peer availability check. Before routing, confirm the target peers SKILL.md exists at its expected path. If not, refuse and route to the user for peer installation. Never route to a peer that isnt available.
- HC#10: No prior-turn diagnosis. Why did you route this differently yesterday? gets the scripted refusal. Orchestrator has no session memory.

## Tools Used

Orchestrator itself uses NO Tableau-specific tools. It reads the users ask, classifies intent, and invokes a peer. The peer runs its own tool sequence.

Orchestrator does use:
- `Read` — Phase 1 (peer availability check; confirm target peers SKILL.md is at the expected path per HC#9).
- No file writes. Skill is compute-only; the invoked peer writes if desired.

## Peer Routing Table (Locked)

Full table in `skill-expertise/peer_routing.md`. Summary of positive-trigger classification per peer:

| Peer | Primary triggers | Route when the ask is about... |
|---|---|---|
| `calc-writer` | write a new calc, author a calc, create a calculated field, I need a calc that... | Authoring new calcs from a natural-language spec. |
| `calc-debugger` | this calc is broken, returns wrong values, returns NULL when it shouldnt, debug this calc | Correctness bugs in an existing calc. |
| `calc-optimizer` | this calc is slow, make this calc faster, speed up this calculation, perf-tune this | Performance rewrites that preserve returned values. |
| `calc-linter` | lint this calc, check style, rewrite for readability, does this follow our house style | Style, naming, comment, or formatting violations. |
| `calc-inventory` | list all calcs, inventory the calcs, catalog my calculated fields | Data-source-wide cataloging (not single-calc work). Quality or hygiene audits ("audit my calcs") go to `calc-hygiene-scan`. |
| `calc-translator` | translate SQL to Tableau, port this DAX, convert Excel formula, translate this expression, SQL to Tableau calc | Single-expression translation from SQL / Excel / DAX into a Tableau calculated field. |

## Non-Calc-Family Routing Table (Locked)

For asks that arrive at orchestrator but arent calc-family concerns:

| Non-calc-family peer | Route when the ask is about... |
|---|---|
| `data-model-documenter` | Data model, tables, relationships, join conditions, cardinality, calc-dependency graph at the data-source level. |
| `workbook-auditor` | Dashboard-level or workbook-level concerns (dashboard slowness, mark counts, extract config, workbook-wide style consistency). |
| `join-and-relationship-advisor` | Join type, relationship type, cardinality issues, fanning, grain issues at the model level. |
| `data-source-connector` | Connecting a new data source, authenticating to a database, setting up a Tableau connection. |

## Maintenance: Adding a New Peer

Adding a 6th+ calc-family peer requires updating three files in lockstep, in this order: (1) `skill-expertise/peer_routing.md` — add the peers expected path, verbatim positive triggers, and anti-triggers; (2) `SKILL.md`s Peer Routing Table summary and Non-Match Handling table; (3) `skill-expertise/handoff_schema.md`s `target_peer` enum. A peer added to only one of these three files is an alignment-drift risk per HC#8 — flag it the same way as any other trigger-table drift.

## Phase Sequence

- **Phase 0.** Read the users ask. Extract calc-family signals (formula pasted, calc name mentioned, verb like debug / optimize / lint / inventory / write).
- **Phase 1.** Peer availability check per HC#9. Confirm target peer(s) SKILL.md exist at expected paths. If any candidate peer is missing, exclude it from consideration and note in routing metadata.
- **Phase 2.** Classify against the peer routing table. Cases:
  - **Single match:** route immediately. Skip to Phase 4.
  - **Multi-match (2+ peers):** fire HC#2 one-clarifier naming the candidate peers explicitly. Wait for user response.
  - **No calc-family match, but non-calc-family match:** route to the non-calc-family peer per HC#3.
  - **No match anywhere:** refuse. Ask user to clarify their intent.
- **Phase 3.** (Only if clarifier was fired.) Re-classify based on users clarifier response.
- **Phase 4.** Invoke the target peer by exact slug. Relay the peers full response unmodified to the user.
- **Phase 5.** Emit `calc_orchestrator_route/1` metadata block alongside the peers handoff, naming the routing decision, alternative candidates considered, and the reason.

## Handoff Contract

Orchestrator does NOT emit any of the five peer schemas (`calc_write_handoff/1`, `calc_debug_handoff/1`, `calc_optimize_handoff/1`, `calc_lint_handoff/1`, `calc_inventory_handoff/1`). Those are the peers exclusive scope.

Orchestrator emits `calc_orchestrator_route/1` alongside every routing decision (including refusals and clarifiers). Full schema in `skill-expertise/handoff_schema.md`. Required non-blank fields:

- `schema_version`, `user_ask` (verbatim), `routing_decision` (`routed_to_peer` / `clarifier_fired` / `refused_non_calc_family` / `refused_no_match` / `refused_peer_unavailable`)
- `target_peer` (only if `routing_decision == routed_to_peer`; else `null`)
- `candidate_peers` (list of peers considered before routing)
- `routing_rationale` (short string explaining the decision)
- `peer_response_relayed` (true / false; false if clarifier fired or refusal)

The peers own handoff (whichever `calc_*_handoff/1` it emits) travels alongside `calc_orchestrator_route/1`, unmodified.

## Report Structure (Locked)

Every routing decision renders this exact structure:

- **Routing decision:** one line naming the target peer or the refusal reason.
- **Rationale:** why this peer, or why the ask doesnt fit any peer.
- **Candidate peers considered:** list of peers evaluated during classification.
- **Peers response** (if routed and peer ran successfully): the peers full delivery, unmodified.
- **`calc_orchestrator_route/1` YAML** with structured routing metadata.

For clarifier fires, only the first three sections render; the peers response is deferred until the user answers.

## Refuse to Fabricate

Never route silently without emitting `calc_orchestrator_route/1`. Never invoke a peer that isnt available at its expected path. Never re-route to a different peer after the first peer refuses per its own HC. Never orchestrate a multi-peer chain internally, always route each peer standalone.

Never invoke calc-family logic directly. If a users ask cant be routed to a peer, refuse with a clear explanation, never fall back to executing calc work as the orchestrator.

## Graceful Degradation

These rules apply whenever something this skill needs is missing or fails. More specific rules elsewhere in this file take precedence.

- **Nothing to work on.** If no workbook is open, there is no data source, or the named calc, sheet, dashboard, or data source isn't found, stop before any other step. Say what you found (list the real names, if any) and ask the user to open the workbook or pick one. Never work on a guessed or closest-match target.
- **Tool call fails, times out, or returns empty.** Retry once, then stop retrying. Mark everything that depended on that call as not checked, continue with what you still can, and say which step failed. If the failed call was a write, stop and report the workbook's current state instead of continuing.
- **Partial results.** If any check, sheet, field, or data source wasn't evaluated, the summary says so (Partial: N of M checked; not checked: [list]). Never give a clean, ready, or PASS verdict on a partial run.
- **Reference file won't open.** Use the rules summarized in this file, say [file] unavailable; using the built-in summary, and never make up thresholds, rule IDs, or Desktop menu steps from memory.
- **Peer skill not installed.** If this skill would hand off to another skill that isn't available, say so and give the manual Desktop step instead. A handoff is never the only next step.
- **Platform gap.** If no tool can do something, say so plainly and give the manual Desktop path.
- **Failure messages.** Tell the user in plain language what was done, what wasn't, and the next step. No raw errors, stack traces, or JSON.
- **No fabrication.** Never invent fields, values, findings, or results to fill a gap left by a failed read.
