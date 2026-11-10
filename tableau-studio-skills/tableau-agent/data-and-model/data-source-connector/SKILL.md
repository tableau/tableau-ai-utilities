---
name: data-source-connector
description: "Use when the user says 'How do I connect to Snowflake?', 'which connector for X?', 'OAuth, PAT, or password?' Recommends the right Desktop connector and sign-in method for a new data source, with prerequisites and numbered setup steps. Advisory only."
---

# Data Source Connector

## When to use (full trigger detail)

Guide a Tableau Studio user through choosing the right connector and auth pattern for a new data source. Advisory-only. Reads a natural-language source description (Snowflake with SSO, Postgres on RDS), recommends the correct Desktop connector, walks through auth setup (OAuth, PAT, password, key-pair) with prerequisites (drivers, service accounts, network), and produces numbered Desktop UI steps. Triggers on connect to X, how do I connect to X, which connector for X, start a new data source, auth for X, OAuth or PAT or password. Do NOT trigger for first-run where do I start (use the built-in Studio onboarding skill, onboarding-concierge), data-modeling questions once connected (use join-and-relationship-advisor), or data-quality profiling (use data-quality-review).

## Purpose

Guide a Tableau Studio user through choosing the right connector and auth pattern for a new data source. Advisory-only. Every step is a Desktop UI instruction because no connect-datasource MCP tool exists. Compresses the which connector, which auth decision from a 20-minute internal debate into a single named recommendation with rationale.

## Trigger Conditions

connect to X, how do I connect to X, how do I set up this connection, which connector for X, start a new data source, start a new datasource, auth for X, which auth pattern, OAuth or PAT or password.

Do NOT trigger on: first-run where do I start (defer to the built-in Studio onboarding skill, `onboarding-concierge`); data-modeling questions once connected (defer to `join-and-relationship-advisor`); data-quality questions (defer to `data-quality-review`); Tableau Cloud vs. Server publishing (out of scope, connection is Desktop-side only).

## Scope Boundaries

- IN: connector recommendation given a source description; auth pattern recommendation for the described environment (SSO, OAuth, PAT, password, key-pair); driver and prerequisite callouts (ODBC driver install, service account setup, network reachability); initial multi-file or multi-table setup guidance (Union vs. multi-table drag).
- OUT: actually creating the connection (Desktop UI, not tool-accessible); joins, relationships, or grain (defer to `join-and-relationship-advisor`); data-quality profiling after connection (defer to `data-quality-review`); publishing the data source to Server or Cloud (out of scope, Desktop-only environment); credential management or vault integration (out of scope).

### Edge-Case Boundaries

| Edge Case | Handling |
|---|---|
| Web Data Connector (WDC) | Refuse. WDC retired 2024. Recommend REST-to-file bridge or Tableau Extract API for custom sources. |
| Custom REST API | Refuse. Not in catalog. Recommend Extract API or third-party bridge. |
| SharePoint list | Refuse. Not in catalog. Recommend export to Excel/CSV or a Power Automate flow to a Tableau-compatible target. |
| Salesforce SOQL custom query | Route to Salesforce connector; custom SOQL is a post-connection concern (Initial SQL dialog). |
| Multi-file union across a folder | Route to Text file connector with the Union option; not a separate connector. |
| Cross-Server federation | Out of scope, Server/Cloud concern. Refuse. |
| Preview-tier connector not yet in catalog | Refuse. Catalog covers Desktop 2026.2 GA connectors. |
| Custom SQL / connection-string override needed after connection | Route to the connectors official Tableau documentation (Initial SQL dialog); out of scope for this skills recommendation. |
| Driver version drift between Desktop releases | Report the catalogs Desktop 2026.2 driver requirement and flag that it may lag the users installed Desktop version; direct them to the connectors official driver page to confirm current requirements. |

## Hard Constraints

- HC#1: Advisory-only. Zero mutating tool calls. No `connect-datasource` tool exists in the Desktop tool surface. Every action is a Desktop UI instruction.
- HC#2: Never fabricate a connector. If the source isnt in `skill-expertise/connector_catalog.md`, report no matching Desktop connector, try ODBC generic rather than inventing one.
- HC#3: Never fabricate an auth pattern. Use the locked rubric in `skill-expertise/auth_patterns.md`.
- HC#4: One clarifying question maximum. If the source is ambiguous, ask exactly one clarifier. Never chain three.
- HC#5: Refuse out-of-scope questions by exact slug (`join-and-relationship-advisor`, `data-quality-review`, `onboarding-concierge`).
- HC#6: Validation Gate before delivery. Every recommendation must pass V1 (catalog membership), V2 (rubric membership), V3 (UI-path currency). Failing any gate blocks delivery.
- HC#7: User-disagreement branch is scoped. Offer at most one alternate connector plus one alternate auth. Never chain a third alternate; route to official docs instead.

## Tools Used

**None.** Advisory-only skill. Zero Desktop tool calls, zero MCP tool calls, zero file writes. Every action is a Desktop UI instruction the user executes manually.

## Source-Description Classification (Locked)

Every intake description falls into exactly one of three classes. Never interpret; look up the class.

| Class | Signature | Action |
|---|---|---|
| **CLEAR** | User names a specific product AND a specific hosting mode AND a specific auth environment (e.g., Snowflake, SSO through Okta). | Proceed directly to Phase 1 Connector Match. No clarifier. |
| **AMBIGUOUS** | User names the product but omits hosting mode OR omits auth environment (e.g., Postgres with no host, MySQL for a dashboard). | Ask exactly one clarifier targeting the missing dimension. See Clarifier Rules below. |
| **OUT-OF-CATALOG** | User names a source not in `skill-expertise/connector_catalog.md` (e.g., custom REST API, proprietary sensor data). | Report no matching Desktop connector, try ODBC generic per HC#2. Do not run clarifier. |

**Clarifier Rules (fire at most once per invocation):**

- If hosting mode is missing, ask in plain language: Does your company run this itself, is it hosted by a cloud provider, or is it only reachable through a work VPN? (technical framing for reference: self-hosted, cloud-hosted like RDS/Cloud SQL/Azure, or on-prem behind a VPN)
- If auth environment is missing, ask in plain language: When you log into this normally, do you sign in with your company account (like Okta), a shared login your team uses, or your own personal username/password? (technical framing for reference: SSO/Okta, service account, or personal credentials)
- If both are missing: pick the one that most narrows the catalog+rubric intersection. Usually hosting mode.
- After the single clarifier, proceed with the closest-match row even if the answer is partial. Never chain a second clarifier.

## Workflow Phases

0. **Phase -1 Existing-Datasource Check.** If workbook inventory is available (`get-workbook-inventory` or equivalent), check whether a similarly-named or same-source datasource is already connected before recommending a new one. If a likely match exists, surface it first (It looks like {existing_datasource_name} may already connect to this source — want to reuse it instead of adding a new connection?) and only proceed to Phase 0 if the user confirms a new connection is wanted.
1. **Phase 0 Intake.** If the user hasnt already named a source, open with a plain-language question a novice can answer without jargon: What data do you want to connect — and where does it live (like a file on your computer, a database, or an online app like Salesforce)? Then classify the answer as CLEAR, AMBIGUOUS, or OUT-OF-CATALOG per the table above. Fire the one clarifier (in the same plain-language style, not the technical hosting/auth wording) if AMBIGUOUS.
2. **Phase 1 Connector Match.** Match the source description against `skill-expertise/connector_catalog.md`. Return primary connector plus one alternate if applicable.
3. **Phase 2 Auth Recommendation.** Match the environment description (SSO, service account, personal credentials) against `skill-expertise/auth_patterns.md`. Recommend the auth type with a one-line why this.
4. **Phase 3 Prerequisites.** Enumerate any driver installs, service account setup, or network requirements needed before the Desktop UI will succeed.
5. **Phase 4 Desktop UI Walkthrough.** Produce numbered Desktop UI steps (Data menu → New Data Source → connector name → dialog fields → auth choice → test connection).
6. **Phase 4.5 Validation Gate.** Before delivery, confirm all three:
   - **V1 Catalog membership.** The recommended connector name appears in `skill-expertise/connector_catalog.md`. If not, drop the recommendation and fall back to ODBC generic.
   - **V2 Rubric membership.** The recommended auth pattern appears in `skill-expertise/auth_patterns.md` at a row whose Source Type + Environment matches the intake. If not, ask the one clarifier or report the mismatch honestly.
   - **V3 UI-path currency.** The Desktop UI walkthrough targets the current Desktop 2026.2 menu paths (Data → New Data Source → connector). Never invent menu paths.
   If any of V1/V2/V3 fails, do NOT deliver the recommendation as-is. State the failure explicitly and either re-scope or refuse.
7. **Phase 4.6 User-Disagreement Branch (conditional).** If the user disputes the recommendation after Phase 4.5 delivery:
   - Offer one alternate connector (from the same catalog rows Alternate column, if present, otherwise ODBC generic).
   - Offer one alternate auth pattern (from the same source-type rows next-most-common auth, per the rubric).
   - If the user rejects both alternates, refuse further alternatives and route to the connectors official Tableau documentation. Never chain a third alternate.
8. **Phase 5 Handoff.** Modeling questions → `join-and-relationship-advisor`. Quality questions → `data-quality-review`. Never invoke; hand the trigger phrase back.

## Error Handling

| Situation | Response |
|---|---|
| Source not in catalog | Report no matching Desktop connector, try ODBC generic, provide ODBC generic setup steps. |
| Ambiguous source (e.g., Postgres with no host) | Ask exactly one clarifying question. Pick closest match after one round. |
| User asks to just connect it | Refuse: no connect-datasource tool exists. Here are the Desktop UI steps. |
| User asks about modeling after connection | Route to `join-and-relationship-advisor` by exact slug with the verbatim trigger phrase. |
| User asks about data quality after connection | Route to `data-quality-review` by exact slug with the verbatim trigger phrase. |
| Driver install fails (ODBC connector rejects no driver found) | Report the failing driver, link to vendor download page name, note that Desktop must be restarted after driver install for the connector to appear. |
| Network unreachable (Desktop test-connection returns cannot resolve host or timeout) | Report the specific failure mode. Ask user to confirm VPN status, DNS resolution of the source host, and any firewall allow-list requirements. Never guess the cause. |
| Credential refresh expired (OAuth token or PAT rejected after prior success) | Report credential refresh failed; token or PAT expired. For OAuth, direct to re-authenticate via Data → Data Source → Edit Connection. For PAT, direct to sources admin console for token rotation. |
| Validation Gate fails V1 (connector not in catalog) | Do NOT deliver the recommendation. Fall back to ODBC generic and state the fallback explicitly. |
| Validation Gate fails V2 (auth not in rubric) | Do NOT deliver the recommendation. Ask the one clarifier or report the mismatch honestly. |
| Validation Gate fails V3 (UI path not current) | Do NOT deliver the recommendation. Report the specific menu path uncertainty and defer to the current Desktop help. |

## Known Limitations

- **Custom SQL and connection-string overrides are out of scope.** The catalog covers standard Desktop connectors. If a user needs custom SQL initial-SQL or a hand-crafted connection string, the skill defers to the connectors official Tableau documentation.
- **Driver version mismatches are not tracked.** The catalog reflects Desktop 2026.2 driver requirements. If a connector version-drifts between Desktop releases, the skills driver recommendation may lag.
- **Environment claims are unverifiable.** The skill relies on the users environment description (SSO vs. PAT vs. password). If the user misstates the environment, the recommendation is wrong through no fault of the skill.
- **Retired connectors and preview connectors.** Web Data Connector (WDC) is retired (2024). Preview-tier connectors may not appear in the catalog until they reach GA.
- **Custom source types (REST APIs, SharePoint lists, proprietary formats).** If a source isnt in the catalog and ODBC generic isnt a fit, the skill refuses rather than fabricating.

## Output Template

Every delivery follows `skill-expertise/output_template.md` (locked). Sections in fixed order: Recommended Connector, Recommended Auth, Prerequisites, Desktop UI Walkthrough, Handoff. Optional Handoff YAML (`schema_version: connection_handoff/1`) for downstream skills that want a machine-parseable handoff. Validation Gate failures block template rendering; see the template file for fallback handling per V1/V2/V3.

## Downstream Handoff Contract

Downstream skills (`join-and-relationship-advisor`, `data-quality-review`) may request a machine-parseable handoff. When requested, emit a fenced YAML block with `schema_version: connection_handoff/1` and these keys:

- `datasource_name` — the connected data sources name in the workbook.
- `connector` — the primary connector name (from catalog).
- `auth_pattern` — the auth pattern name (from rubric).
- `hosting_mode` — one of self_hosted, cloud_hosted, on_prem_vpn.
- `extract_or_live` — one of extract, live, not_yet_configured.
- `verified` — true if Validation Gate passed, false otherwise.
- `notes` — optional free text.

Downstream skills should refuse unknown schema versions (`connection_handoff/2` and up) rather than guessing at forward-compatibility.

## Common Mistakes to Avoid

- Fabricating a connector name for an obscure source. If the catalog doesnt list it, say so.
- Chaining clarifying questions past the first. Pick the closest match after one round.
- **Asking a second clarifying question when both hosting mode and auth environment are missing.** HC#4 allows exactly one clarifier total. If both dimensions are unknown, ask only the hosting-mode question, then pick the auth row for the closest match and state that assumption explicitly in the recommendation. Never ask a follow-up auth question after the hosting-mode clarifier has already been answered.
- Drifting into modeling advice. Refuse and route.
- Recommending an auth pattern not in the rubric. If the environment description doesnt map cleanly, ask the clarifier or report the mismatch honestly.
- Skipping the Validation Gate. Every recommendation must pass V1, V2, V3 before delivery.
- Rendering the output template on a gate failure. Fall back per template files failure handling.

## MCP Skill Mapping

No direct MCP equivalent. Desktop-agent-native connection-guidance skill.

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
