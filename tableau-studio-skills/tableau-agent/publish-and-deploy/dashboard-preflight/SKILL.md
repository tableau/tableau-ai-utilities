---
name: dashboard-preflight
description: "Use when the user says 'Preflight this dashboard', 'check my dashboard before I publish', 'is this dashboard ready for review?' Checks one dashboard's assembly (zones, sheet mapping, filter actions, parameters, titles, size, fit) and gives manual fix steps. Read-only."
---

# Dashboard Preflight

## When to use (full trigger detail)

Audit a Tableau dashboard for assembly hygiene before it ships to Publish Readiness or a stakeholder review. Runs a locked 8-check catalog covering zone alignment, sheet-to-zone mapping, filter-action wiring inventory, parameter linkage across sheets, title and caption presence per zone, canvas-size sanity, view-fit legality per chart type, and container-nesting soundness. Read-only. Every finding is a Desktop fix instruction the user applies manually. Trigger with preflight this dashboard, check my dashboard before I publish, is this dashboard ready for review, dashboard preflight, dashboard sanity check. Do NOT trigger on. full pre-publish hygiene across the workbook (defer to publish-readiness), text correctness (defer to desktop-spellcheck), localization fragility (defer to i18n-scanner), post-build interaction verification (defer to interaction-validator), building or editing dashboards (defer to viz-planner).

## Purpose

Audit one Tableau dashboard for assembly hygiene before it moves to Publish Readiness or a stakeholder review. Read-only. Every finding cites a locked catalog rule and produces a Desktop-fix instruction, never a mutation.

Positioned upstream of Publish Readiness in the pipeline. Publish Readiness owns whole-workbook hygiene (unused fields, orphaned scratch sheets, performance, calc hygiene, naming consistency). Dashboard Preflight owns single-dashboard assembly (zones, filters, parameters, titles, canvas, view fit, containers).

## Trigger Conditions

- preflight this dashboard
- check my dashboard before I publish
- is this dashboard ready for review
- dashboard preflight
- dashboard sanity check
- audit this dashboards assembly

## Do NOT Trigger On

- Whole-workbook pre-publish hygiene (defer to publish-readiness).
- Spelling and typography in stakeholder-visible text (defer to desktop-spellcheck).
- Localization fragility (defer to i18n-scanner).
- Post-build interaction verification (defer to interaction-validator).
- Building or editing dashboards (defer to viz-planner).
- Change-over-time (defer to workbook-auditor).
- Data-quality issues in the underlying data source (defer to data-quality-review).
- Content quality of tooltips, annotations, or text objects (defer to caption-and-tooltip-advisor).

## Scope Boundaries

- **IN.** Single-dashboard assembly audit against the locked 8-check catalog. Read-only output. Handoff schema `dashboard_preflight_report/1`.
- **OUT.** Any workbook mutation. Applying any fix. Content-quality checks. Post-publish site governance. Runtime interaction simulation. Multi-dashboard audits in one run.

**Cross-datasource dashboards.** For dashboards spanning multiple data sources, run each check per-DS where the check is DS-scoped (P-SHEET-02 sheet references, P-FILTER-03 filter-action fields, P-PARAM-04 parameter references). Cross-DS filter actions are inventoried as first-class findings and flagged with per-DS attribution. Cross-DS parameters resolve via `resolve-field` against every DS in the dashboard; failure on one DS is a Warning, failure on all is Blocking.

**Scale bands.** Explicit handling for the range of dashboard sizes:

- **Tiny (<5 zones).** Full 8-check catalog runs. No batching optimizations needed.
- **Typical (5-15 zones).** Full catalog. Batching per Tool Sequence.
- **Wide (15-30 zones).** Full catalog. Report renders Info findings inside a `<details>` collapsible block after the first 5, per `skill-expertise/report_template.md` overflow handling.
- **Very wide (30+ zones).** Full catalog. Warn the user up-front that the run will take longer. Offer to scope to a subset of zones if they name specific ones.
- **Multi-page dashboards.** One page per run per HC#2. If the user asks about pages 2-N, ask which page to preflight.

## Workflow Phases

- **Phase 0 Scope.** Identify the target dashboard. If the workbook contains multiple dashboards, ask the user which one. Reuse `get-workbook-inventory` output if a prior skill in the session already called it. **Prior-report reuse:** if a `dashboard_preflight_report/1` handoff for this dashboard already exists in session context (or on disk next to the workbook), offer to diff against it rather than re-scan from scratch. Diff-mode preflight re-runs only the checks whose inputs could have changed, per this trigger map:

- Zone count changed since the prior report → re-run P-ZONE-01, P-SHEET-02, P-TITLE-05, P-FIT-07, P-CONTAINER-08 (all zone-scoped checks).
- Any worksheet in `list-worksheets` was renamed or removed since the prior report → re-run P-SHEET-02.
- Dashboard-level filter actions changed (count or field list differs from prior report) → re-run P-FILTER-03.
- Parameter list on the dashboard changed → re-run P-PARAM-04.
- Canvas dimensions changed → re-run P-CANVAS-06.
- Any zones `x`/`y`/`width`/`height` differs from the prior reports inventory (moved or resized without a zone-count change) → re-run P-ZONE-01 and P-CONTAINER-08 for that zone and its parent container.
- The users own message in this session references a fix they just made (e.g., I just fixed the canvas size, I retitled that zone, I rewired the filter action) → re-run the specific check(s) that fix would affect, even if the fixed-report trigger map above wouldnt otherwise catch it. Session conversation is a valid diff-mode signal, not just the prior reports stored values.
- If none of the above changed, skip re-scanning and reuse all prior findings verbatim, noting in the report that this was a diff-mode run with no re-evaluated checks.
- **Phase 1 Inventory.** Read the dashboards zones, sheets, filter actions, parameters, dynamic-zone-visibility bindings, canvas size, and view-fit settings. Multi-datasource dashboards inventory each DS separately.
- **Phase 2 Run the 8-Check Catalog.** For each check in `skill-expertise/preflight_catalog.md`, evaluate the dashboard and record findings. Every finding cites a specific catalog rule ID (P-ZONE-01 through P-CONTAINER-08).
- **Phase 3 Assemble Report.** Group findings by severity (Blocking, Warning, Info). Every finding includes a Desktop-fix instruction. Pre-delivery count validation: every zone identified in Phase 1 accounted for in the report. Report shape follows `skill-expertise/report_template.md`.
- **Phase 4 Deliver.** Compact chat summary first (verdict + finding counts by severity + top 3 items). Offer to write the full report as a file to the users Downloads folder in `.txt` or `.md` format at their choice. If Publish Readiness is next in the pipeline, emit `dashboard_preflight_report/1` alongside the summary regardless of whether the file write happens.

**Delivery shape.**

- **Chat by default.** Compact summary (5-8 lines): dashboard name, zone count, verdict, severity counts, top 3 items by severity priority (Blocking first, then Warning, then Info). Skip the Unscanned Checks bullet in chat unless count > 0.
- **File on request.** If the user opts in (save the full report, yes write it out, put it in Downloads), write the full report per `skill-expertise/report_template.md` to the OS-appropriate Downloads folder: `%USERPROFILE%\Downloads\{workbook_name}_{dashboard_name}_preflight.md` on Windows, `$HOME/Downloads/{workbook_name}_{dashboard_name}_preflight.md` on macOS. Never hard-code a tilde-expanded path or a drive letter; resolve via the tool environment. Fresh-filename discipline: increment `_v2`, `_v3` on collision per the CSV BOM lesson from i18n Scanner. Confirm the exact resolved absolute path on save. **Naming convention:** the `_preflight` suffix is reserved to this skill; never reuse it for other skills exports, so a downstream consumer scanning Downloads can identify preflight output unambiguously.
- **No duplicate rendering.** Build the full report body (per `skill-expertise/report_template.md`) exactly once in memory. The chat summary is a truncated view of that same in-memory report, not a separately-generated pass; the file write (if requested) reuses the identical in-memory body. Never re-run Phase 2/3 assembly logic a second time to produce the file version.
- **Format choice.** Ask once per run: `.md` (default, renders with headers and severity emphasis) or `.txt` (plain text, easier for pasting into tickets). Remember the choice for the rest of the session.
- **Handoff emission.** `dashboard_preflight_report/1` always emitted to session context, whether the user writes a file or not. Downstream consumers (publish-readiness, workbook-auditor) read the handoff, not the file.
- **Refuse silent write.** Never write a file without explicit user opt-in. HC#1 read-only discipline extends to Downloads-folder writes: the user must confirm each save.

## Tool Sequence

Locked sequence to minimize latency and honor tool dependencies. Every phase batches where possible.

- **Phase 0.** Reuse session-context `get-workbook-inventory` output if available. Otherwise, call `get-workbook-inventory` once. Also call `list-dashboards` in the same batch. Both calls in parallel; neither depends on the other.
- **Phase 1.** Single call to `get-dashboard-xml` for the target dashboard. Then batch `list-worksheets` + `list-available-fields` (verbosity: full) in parallel; neither depends on the other. Only call `get-worksheet-xml` per zone if Phase 2 checks require it (P-FIT-07 mark-type inference, P-TITLE-05 show-title flag), and only on zones that pass the platform-gap pre-check (worksheet not bound to a dashboard with real data).
- **Phase 2.** Evaluate all 8 checks in a single pass over the inventory. No additional tool calls. Reuse Phase 1 XML and field lists.
- **Phase 3 and Phase 4.** No tool calls. Assembly and delivery use in-memory state.

**Batching rules:**

- Never call `get-workbook-inventory` twice in one run.
- Never call `list-available-fields` twice unless the first return was truncated (verbosity mismatch).
- `get-worksheet-xml` calls only for zones where Phase 2 signals require XML detail beyond `list-available-fields`. Fallback if the call fails.
- `resolve-field` only when P-FILTER-03 needs to verify a filter-action field resolves; do not resolve every field on the dashboard.

**Early-exit condition.** If Phase 1 inventory returns zero zones (empty dashboard shell), skip Phase 2 entirely, deliver empty dashboard report, and route to viz-planner or worksheet-builder per HC#10.

## The 8-Check Catalog

Full detail lives in `skill-expertise/preflight_catalog.md`. Summary:

1. **P-ZONE-01 Zone Alignment.** All zones align to the dashboard grid; no zones extend past canvas bounds.
2. **P-SHEET-02 Sheet-to-Zone Mapping.** Every visible zone contains a valid worksheet reference; no dead-zone references to deleted sheets.
3. **P-FILTER-03 Filter-Action Wiring.** Every filter action has a valid source, valid target(s), and a resolvable field. Refuses to simulate action firing (thats interaction-validators job).
4. **P-PARAM-04 Parameter Linkage.** Every parameter referenced on this dashboard is linked to a live calc, filter, or dynamic-zone binding.
5. **P-TITLE-05 Title and Caption Presence.** Every worksheet zone has a title or an explicit no title flag; every dashboard has a title zone or an explicit no title caption.
6. **P-CANVAS-06 Canvas-Size Sanity.** Canvas dimensions match a known device class (Desktop 1400x900, Laptop 1200x800, Tablet 768x1024, Phone 375x812) OR are explicitly Fixed with a stated rationale in the dashboard caption.
7. **P-FIT-07 View-Fit Legality.** Each worksheets view fit matches the recommended fit for its chart type per the shared portfolio catalog (map/KPI = Entire View, time-series line = Fit Width, horizontal ranked bars = Fit Height, etc.).
8. **P-CONTAINER-08 Container-Nesting Soundness.** Container nesting has no orphan floating zones inside a tiled container, no zero-height/zero-width containers, no more than 4 levels of nesting.

## Hard Constraints

**HC#1 Read-only always.** Never invoke `author-calc`, `bind-template`, `build-and-apply-worksheet`, or any mutating tool. Every finding is a Desktop-fix instruction the user applies manually.

**HC#2 One dashboard per run.** Multi-dashboard audits require the user to invoke the skill once per dashboard. Batching is refused per HC#3.

**HC#3 Bulk-action refusal.** If the user says preflight all my dashboards or fix all these findings automatically, refuse and route: for the first, invoke once per dashboard; for the second, findings are Desktop-fix instructions, not agent-applied.

**HC#4 No fabricated findings.** Every finding cites a specific catalog rule ID from `skill-expertise/preflight_catalog.md`. If a check cannot run (e.g., `get-worksheet-xml` fails on a dashboard-bound sheet), the finding is flagged UNSCANNED with a rationale, not silently omitted.

**HC#5 User-named-check wins.** If the user asks for just the zone-alignment check, run only P-ZONE-01 and skip the rest. Do not force the full 8-check.

**HC#6 Never simulate interaction.** Filter-action wiring is checked structurally (source and target exist, field resolves) but action firing is out of scope. Defer to interaction-validator.

**HC#7 Sentinel discipline.** Use `null`, `[]`, `unscanned` for missing data; never blank fields in the handoff schema.

**HC#8 Refuse to fabricate.** If the V-gate cannot pass after one retry, refuse delivery and diagnose. Never fake a V-gate pass.

**HC#9 Partial-info handling.** If the ask includes partial context (preflight this dashboard, but skip the canvas check), deliver on the specified checks and note which checks were skipped and why.

**HC#10 Adjacent-skill routing.** Content-quality asks (tooltips, annotations, text) route to caption-and-tooltip-advisor. Whole-workbook hygiene asks route to publish-readiness. Interaction-behavior asks route to interaction-validator. Chart-selection asks route to chart-swap-advisor.

**HC#11 Severity-tier override.** The user may scope the delivered report to a single severity band (show me Blocking only, just the Warnings). Honor the request; still run the full 8-check catalog internally, but render only the requested severity in the chat summary. The handoff schema always includes all findings regardless of the display filter.

## Common Mistakes

Behaviors this skill must never exhibit, even under user pressure:

1. **Inferring rule fit from zone names alone.** Never conclude a zone violates P-FIT-07 because its name suggests a chart type. Always read the actual mark type from XML or `list-available-fields`. Zone names are user-authored and unreliable.
2. **Fabricating findings to fill a severity band.** If Blocking count is zero, render `_None._` in that section per the report template. Never invent a Warning-tier finding to make the report feel useful.
3. **Rewriting the catalog mid-run.** The 8-check catalog and severity assignments are locked in `skill-expertise/preflight_catalog.md`. Do not adjust severity based on user pressure (thats really a Blocking, right?) without a documented catalog revision.
4. **Skipping the V-gate when running under time pressure.** V1 catalog match, V2 zone-count reconciliation, V3 handoff-completeness always run per the read-only V-gate. HC#8 refuses delivery on failure; do not paper over a failure with `unscanned`.
5. **Silent tool failure absorption.** If `get-dashboard-xml` fails, the fallback path is documented in Error Handling and every partial finding is flagged UNSCANNED with a reason. Never proceed as if the failure did not happen.
6. **Applying a fix in Desktop.** Every finding is a Desktop-fix instruction the user applies manually per HC#1. Never invoke `author-calc`, `bind-template`, `build-and-apply-worksheet`, or any mutating tool.
7. **Batching multi-dashboard runs.** Per HC#3, one dashboard per run. If the user names three dashboards, ask which one first and offer to invoke separately for the rest.
8. **Reordering the severity sections in the report.** Blocking, Warning, Info is the locked order per `skill-expertise/report_template.md`. Do not reorder even if a section is empty; empty sections render as `_None._`.

## Validation Gate (3-Check Read-Only)

**V1 Finding-Catalog Match.** Every finding in the report references a specific catalog rule ID (P-ZONE-01 through P-CONTAINER-08). Sentinel `unscanned` acceptable for checks that could not run.

**V2 Zone-Count Reconciliation.** The dashboards zone count from Phase 1 inventory matches the total zone-references in Phase 2 findings (each zone accounted for by at least one check outcome, even if the outcome is no finding).

**V3 Handoff-Completeness.** Every field in `dashboard_preflight_report/1` populated per `skill-expertise/handoff_schema.md`. Sentinel values acceptable per HC#7.

Any V-gate failure blocks delivery per HC#8. Fail-open is NOT applied since the skill is read-only.

## Handoff Contract

Emits `dashboard_preflight_report/1` per `skill-expertise/handoff_schema.md`. Consumed by:

- **publish-readiness.** Skips its own dashboard-hygiene checks when it sees a fresh preflight report in context.
- **workbook-auditor.** Preflight findings enrich change digests.

## Known Limitations

- `get-worksheet-xml` reliability on dashboard-bound populated sheets (platform gap). Fallback: use `list-available-fields` formula text plus dashboard-XML hints. Findings flagged UNSCANNED when the fallback still fails.
- **P-FILTER-03 is structurally UNSCANNED in the current tool environment.** `get-dashboard-xml` does not expose an `<actions>` block on any dashboard, and no dedicated actions-listing tool exists. Confirmed empirically 2026-09-10 across 2 dashboards on Superstore. Every P-FILTER-03 evaluation currently returns `unscanned` with `reason: fallback_unavailable`. This is a tool-surface gap, not a skill defect; the check remains in the catalog so it can activate once an actions-listing tool becomes available. Users needing filter-action verification should route to `interaction-validator` for behavioral testing, understanding it faces the same tool-surface gap and reports symptoms rather than confirmed root cause.
- Cannot verify visual result of any zone alignment. Sees coordinates, not pixels.
- Cannot simulate interaction firing (defer to interaction-validator).
- One dashboard per run. Batching refused per HC#3.

## Error Handling

| Failure | Response |
|---|---|
| `get-workbook-inventory` fails | Report tool failure, ask user to reopen workbook. Do not proceed. |
| `get-dashboard-xml` fails on target dashboard | Flag UNSCANNED for structural checks that depend on it. Continue with checks that use `list-available-fields`. |
| `get-worksheet-xml` fails on dashboard-bound sheet | Fallback to `list-available-fields` + dashboard-XML hints discipline. Flag partial as UNSCANNED. |
| Multi-dashboard workbook, user did not name target | Ask one clarifying question with dashboard names. |
| User asks preflight all dashboards | Refuse per HC#3. Suggest one-at-a-time invocation. |
| User asks to apply findings | Refuse per HC#1. All fixes are Desktop-manual. |
| Dashboard has zero zones (empty shell) | Report empty dashboard with no findings. Suggest viz-planner or worksheet-builder. |
| `resolve-field` returns no match for a filter-action field | Flag P-FILTER-03 Blocking for that action (field no longer resolves). Do not skip the action or guess a replacement field. |
| Any tool call times out or returns a partial/empty result mid-run | Flag the affected check(s) UNSCANNED with `reason: tool_failure`, log the tool in `run_metadata.tool_failures`, and continue with the remaining checks rather than aborting the whole run. |
| Datasource disconnects mid-run (live connection drops) | Flag every check depending on that DS as UNSCANNED with `reason: tool_failure`, note the DS name in `run_metadata.tool_failures`, and continue with DS-independent checks (P-ZONE-01, P-TITLE-05, P-CANVAS-06, P-CONTAINER-08). Do not retry the connection. |
| Field-level permission denial (RLS) blocks `list-available-fields` or `resolve-field` for a filter/parameter field | Flag the specific finding UNSCANNED with `reason: fallback_unavailable` and a note that the field is permission-restricted, not missing. Never treat a permission denial as a dead reference (P-SHEET-02) or unresolved field (P-FILTER-03 Blocking); those imply the field doesnt exist, which isnt established here. |

## Examples

**Example 1: Clean dashboard.** User: Preflight this dashboard. Agent inventories the dashboard, runs the 8-check catalog, finds zero blocking issues, reports 0 Blocking, 2 Warning (canvas size not a known device class, view fit on Chart-3 not aligned with chart type), 3 Info. Ready for publish-readiness. Emits handoff.

**Example 2: Dead zone reference.** User: Sanity-check my Sales Overview dashboard. Agent runs the catalog, finds P-SHEET-02 finding: Zone Q4 Trend references worksheet Q4 Trend Detail which no longer exists in the workbook. Fix in Desktop: right-click the zone > Remove, or rebind to a live sheet. Blocking severity.

**Example 3: Multi-dashboard workbook, no target.** User: Preflight my dashboards. Agent asks: Which dashboard? Workbook contains: Executive Summary, Regional Detail, Product Performance.

**Example 4: Bulk-action refusal.** User: Preflight all three dashboards. Agent refuses per HC#3: One dashboard per run. Invoke separately for each. Which one first: Executive Summary, Regional Detail, or Product Performance?

**Example 5: Partial-check ask.** User: Just check the zone alignment on this dashboard. Agent runs P-ZONE-01 only per HC#5, skips the other seven, reports findings for zone-alignment only, notes in the handoff that seven checks were skipped by user request.

## Relationship to Other Skills

- **Upstream of publish-readiness.** Preflight report is a handoff input.
- **Peer to caption-and-tooltip-advisor.** Preflight owns assembly; caption-and-tooltip-advisor owns tooltip and caption content.
- **Peer to chart-swap-advisor.** Preflight owns view-fit legality per chart type; chart-swap-advisor owns whether the chart type itself is right.
- **Adjacent to interaction-validator.** Preflight checks wiring structurally; validator checks wiring behaviorally.
- **Adjacent to logic-explainer.** Preflight audits assembly; logic-explainer explains construction.
- **Never overlaps with data-quality-review, data-scribe, calc-family, or worksheet-builder.**

## MCP Skill Mapping

Desktop-native. No MCP dependency.

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
