# Peer Routing Table (Locked)

Routing authority for calc-orchestrator. Every routing decision cites this table by peer slug and matched trigger. Never invent a peer. Never route to a peer whose SKILL.md isn't available at its expected path.

Peer trigger phrases below are transcribed verbatim from each peer's shipped SKILL.md `Trigger Conditions` section.

## `calc-writer`

**Expected path:** `skills/calc-writer/SKILL.md`

**Positive triggers (matched from calc-writer's SKILL.md):**
- "write a new calc"
- "author a calc"
- "create a calculated field"
- "I need a calc that..."
- "make me a calc"
- "how do I write a calc that..."
- "build a calc for..."

**Route when the ask is about:** authoring a NEW calc from a natural-language spec. Not fixing, not optimizing, not linting an existing one.

**Anti-triggers (route elsewhere):**
- If a formula is pasted alongside a correctness question → `calc-debugger`.
- If a formula is pasted alongside a performance question → `calc-optimizer`.
- If a formula is pasted alongside a style question → `calc-linter`.
- If the ask is "list all calcs" scoped → `calc-inventory`.

## `calc-debugger`

**Expected path:** `skills/calc-debugger/SKILL.md`

**Positive triggers:**
- "this calc is broken"
- "returns wrong values"
- "returns NULL when it shouldn't"
- "debug this calc"
- "fix this calc"
- "why is this calc returning X"
- "this calc errors" / "this calc has a syntax error"

**Route when the ask is about:** correctness bugs in an existing calc. Wrong values, unexpected NULL, syntax errors, aggregation errors, LOD grain issues.

**Anti-triggers:**
- If the calc "works but is slow" → `calc-optimizer` (not correctness).
- If the ask is "the join is wrong" or "the model is wrong" → `join-and-relationship-advisor` (not calc-side).
- If the ask is "clean up the name/style" → `calc-linter` (not correctness).

## `calc-optimizer`

**Expected path:** `skills/calc-optimizer/SKILL.md`

**Positive triggers:**
- "this calc is slow"
- "make this calc faster"
- "speed up this calculation"
- "why is this calc slow"
- "perf-tune this calc"
- "optimize this calc"

**Route when the ask is about:** performance rewrites that preserve returned values. Tier-drop candidates, R-EQUIV-01 verification, already-optimal verdicts.

**Anti-triggers:**
- If the calc returns wrong values (even if also slow) → `calc-debugger` first, per calc-optimizer's HC#10 debug-before-optimize.
- If the slowness is model-level (joins, relationships, fanning) → `join-and-relationship-advisor`.
- If the ask is "rename this for consistency" → `calc-linter`.

## `calc-linter`

**Expected path:** `skills/calc-linter/SKILL.md`

**Positive triggers:**
- "lint this calc"
- "check this calc's style"
- "rewrite for readability"
- "does this calc follow our house style"
- "check my calc naming"
- "style-check this calc"

**Route when the ask is about:** style, naming, comment, or formatting violations against the 12-rule catalog. NOT correctness or performance.

**Anti-triggers:**
- If the ask is "fix wrong values" → `calc-debugger`.
- If the ask is "make this faster" (even framed as "this is bloated / cleaner would be faster") → `calc-optimizer`.
- If the ask is data-source-wide "how many long-named calcs do I have" → `calc-inventory` first, then per-calc `calc-linter` if user opts in.

## `calc-inventory`

**Expected path:** `skills/calc-inventory/SKILL.md`

**Positive triggers:**
- "list all calcs in this data source"
- "inventory the calcs"
- "catalog my calculated fields"
- "show me every calc in this workbook"
- "what calcs exist here"

**Route when the ask is about:** data-source-wide cataloging. Reference graph, usage flags, cycle detection.

**Anti-triggers:**
- If the ask is single-calc scoped (even "look at this one calc") → `calc-writer` / `calc-debugger` / `calc-optimizer` / `calc-linter` per the specific verb.
- If the ask is workbook-wide beyond calcs (dashboards, worksheets) → `workbook-auditor`.
- If the ask is data-model scoped (tables, relationships) → `data-model-documenter`.
- If the ask is a quality or hygiene audit of calcs ("audit my calcs", naming drift, unused calcs, nesting) → `calc-hygiene-scan`.

## `calc-translator`

**Expected path:** `skills/calc-translator/SKILL.md`

**Positive triggers (matched from calc-translator's SKILL.md):**
- "translate SQL to Tableau"
- "port this DAX"
- "convert Excel formula"
- "translate this expression"
- "SQL to Tableau calc"
- "port this formula to Tableau"
- "convert this DAX to Tableau"

**Route when the ask is about:** single-expression translation from SQL (ANSI, Snowflake, BigQuery, SQL Server, Redshift/Postgres), Excel, or Power BI DAX into a working Tableau calculated field. Includes source-dialect classification, deterministic calc-type routing, and post-translation verification via `get-summary-data`.

**Anti-triggers (route elsewhere):**
- If the ask is authoring a NEW calc from a natural-language spec (not a translation from another dialect) → `calc-writer`.
- If the ask is optimizing a translated calc after it lands → route to calc-translator FIRST (per its own workflow), then optionally to `calc-optimizer` per user opt-in.
- If the ask is multi-expression batching or whole-workbook migration → refuse with a note that batch translation is out of scope for calc-translator's single-expression scope.

**Peer coordination note:** calc-translator is the second calc-family peer sharing the `tableau-calc-engine` MCP mapping. calc-orchestrator routes single-expression source-dialect ports directly to calc-translator, never to calc-writer for the same ask.

## Multi-Peer Match Handling

When the ask matches 2+ peers' positive triggers, fire the HC#2 clarifier with all matching candidates named explicitly. Never pick silently.

Common multi-match patterns:

| Ambiguity pattern | Candidate peers | Clarifier phrasing |
|---|---|---|
| "This calc is broken AND slow" | calc-debugger, calc-optimizer | "Correctness first, then perf? calc-debugger fixes the wrong values; once it works, calc-optimizer speeds it up. Do them in that order?" |
| "Rewrite this calc" (no context on why) | calc-writer, calc-linter, calc-optimizer | "Rewrite for what? New logic (calc-writer), style (calc-linter), or performance (calc-optimizer)?" |
| "Fix this calc" (no context on failure mode) | calc-debugger, calc-linter | "Fix a correctness bug (calc-debugger) or a style violation (calc-linter)?" |
| "Audit these calcs" | calc-inventory, calc-linter | "Full data-source cataloging (calc-inventory) or single-calc style check (calc-linter)?" |
| "Make this calc better" | calc-optimizer, calc-linter | "Better how? Performance (calc-optimizer) or readability/style (calc-linter)?" |
| "Translate this and also make it faster" | calc-translator, calc-optimizer | "Translation first (calc-translator handles the SQL/Excel/DAX port and verifies equivalence), then optimization (calc-optimizer takes the verified translation)? Or is speed the actual bottleneck? calc-translator's Phase 5 offers optional handoff to calc-optimizer after the translation lands." |
| "Translate this into a new calc" (ambiguous between porting and authoring) | calc-translator, calc-writer | "Port from an existing SQL/Excel/DAX expression (calc-translator), or author a new calc from a natural-language spec (calc-writer)?" |

## Explicit-Peer Naming (HC#5)

If the user names a peer by slug in their ask ("use calc-writer for this"), route to that peer directly. Do not second-guess the user's routing choice. Even if the ask would more naturally fit a different peer, the user's explicit named choice wins.

Record the explicit routing in `calc_orchestrator_route/1` with `routing_rationale: "user named peer explicitly"`.

## Non-Calc-Family Refusal Routing (HC#3)

When the ask has no calc-family signal but matches a non-calc-family peer:

| Non-calc-family ask signal | Route to |
|---|---|
| "Document the data model," "explain the tables," "map the relationships" | `data-model-documenter` |
| "The extract is slow," "refresh takes too long," "optimize this extract" | `extract-optimizer` |
| "What changed in this workbook," "did anyone edit this calc" | `workbook-auditor` |
| "This join is fanning," "cardinality issues," "relationship type is wrong" | `join-and-relationship-advisor` |
| "Connect a new data source," "set up authentication," "the data source won't load" | `data-source-connector` |
| Other calc skills not in the routing table: document calcs (`calc-documenter`), explain a calc (`calc-explainer`), calc hygiene scan (`calc-hygiene-scan`), move a calc to another data source (`calc-migrator`), diff a migration (`calc-migrator-diff-report`) | Name the skill and its trigger phrase. Don't refuse. |
| No peer matches anywhere | Refuse. Ask user to clarify intent. Never absorb. |

## Peer-Refusal Relay (HC#4)

If the invoked peer refuses per its own HC (e.g., calc-writer refuses per HC#5 no-field-fabrication), orchestrator relays the refusal unmodified. Never re-route silently to a different peer.

Record in handoff:
```yaml
routing_decision: routed_to_peer
target_peer: calc-writer
peer_response_relayed: true
peer_outcome: refused
peer_refusal_reason: "HC#5 field fabrication refusal: [NonExistentField] not resolvable"
```

## Refuse to Fabricate

Never route to a peer whose SKILL.md is missing at its expected path (HC#9). Never invent a peer trigger not in this table. Never merge two peers into a single silent routing decision.
