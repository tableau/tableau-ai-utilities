---
name: format-drift-scanner
description: "Use when the user says 'Check my formatting', 'are my dates and numbers consistent?', 'format drift', 'check number formats'. Finds inconsistent number, date, currency, and font formats across the workbook and gives manual fix steps. Read-only."
---

# Format Drift Scanner

## When to use (full trigger detail)

Audit a Tableau workbook for number, date, and font format-string drift across measure placements, date pills, and text objects. Runs a locked drift catalog (currency-symbol mismatch, decimal-places mismatch, date-format mismatch, thousands-separator mismatch, font-family drift, font-size drift, negative-number-treatment drift) per data source per workbook, groups findings by drift type and severity, and produces a Desktop-fix report. Rescoped 2026-09-10 from format-consistency-scanner. number/date/font format-string drift only, no palette compliance (pixel-visibility blocked). Trigger with format drift, check my formatting, audit format consistency, are my dates and numbers consistent, format-drift-scanner, check number formats, date format audit. Do NOT trigger on.

## Purpose

Scan a Tableau workbook for format-string drift across every measure placement, date pill, and text object. Read-only. Every finding cites a locked drift-type rule and produces a Desktop-fix instruction, never a mutation.

Positioned parallel to desktop-spellcheck and i18n-scanner in the pipeline. Spellcheck owns text-copy correctness. i18n-scanner owns locale-fragility. Format Drift Scanner owns cross-worksheet format-string consistency (number formats, date formats, font families and sizes).

**Scope note (2026-09-10 rescope):** This skill was originally scoped as format-consistency-scanner with palette compliance as a fourth check. Palette compliance was dropped because color style-rules are silently dropped on apply and pixel-level color inspection is not available. Current scope is number-string, date-string, and font drift only.

## Trigger Conditions

- format drift
- check my formatting
- audit format consistency
- are my dates and numbers consistent
- format-drift-scanner
- check number formats
- date format audit
- font consistency check

## Do NOT Trigger On

- Text-copy correctness like spelling and typography (defer to `desktop-spellcheck`).
- Localization fragility, hard-coded currency, regional date-format collisions (defer to `i18n-scanner`).
- Applying format changes (all fixes are Desktop-manual per HC#1).
- Dashboard assembly hygiene (defer to `dashboard-preflight`).
- Chart-type selection (defer to `chart-swap-advisor`).
- Whole-workbook pre-publish hygiene (defer to `publish-readiness`).
- Change-over-time (defer to `workbook-auditor`).
- Data-quality issues in the underlying data (defer to `data-quality-review`).
- Calc-behind-the-format authoring (defer to calc-orchestrator).

## Scope Boundaries

- **IN.** Number format-string drift audit across every measure placement per data source. Date format-string drift audit across every date pill. Font family and font size drift audit across text objects, axis labels, tooltip labels, and worksheet titles. Locked severity tiers per drift catalog. Read-only output. Handoff schema `format_drift_report/1`.
- **OUT.** Any workbook mutation. Applying any format change. Palette / color compliance. Rendered visual output evaluation (pixel-level anything). Locale fragility. Text correctness. Whole-workbook governance.

**Cross-datasource workbooks.** Number format drift is per-DS-scoped: a currency-symbol mismatch on DS-A does not fire against DS-B. Date format drift is per-DS-scoped too. Font drift is workbook-scoped (fonts are UI-level, not DS-scoped). Cross-DS format drift produces a distinct finding severity: Info-tier when a legitimate business reason (multi-currency reporting) explains the difference, Warning-tier when no rationale is documented.

**Scale bands.**

- **Tiny (<10 measure placements).** Full audit. No batching needed.
- **Typical (10-50 placements).** Full audit. Batching per Tool Sequence.
- **Wide (50-100 placements).** Full audit. Info findings collapse into a `<details>` block after the first 5 per drift type.
- **Very wide (100+ placements).** Full audit. Warn user up-front of longer runtime. `get-worksheet-xml` batches capped at 10 worksheets per parallel call regardless of workbook size (per Tool Sequence). Offer to scope by data source or drift-type per HC#5; if the user declines to scope and the workbook exceeds 300 placements, proceed but cap Info-tier findings rendered inline at 5 per drift type (per Overflow Handling in `skill-expertise/report_template.md`) rather than holding the full set in context.

## Workflow Phases

- **Phase 0 Scope.** Confirm workbook is open. Reuse `get-workbook-inventory` output if a prior skill already called it. **Prior-report reuse:** if a `format_drift_report/1` handoff exists in session context or on disk, offer to diff. Diff-mode trigger map:
  - Measure count changed since prior report → full re-scan.
  - Date-pill count on any worksheet changed → full re-scan.
  - Any worksheet renamed, added, or removed → full re-scan.
  - User session references a format fix (I just aligned the currency symbols on Sales) → re-scan the affected drift type.
  - If none of the above changed, reuse prior findings verbatim and note diff-mode in the report.
- **Phase 1 Inventory.** Enumerate every measure placement (via `search-workbook-fields` for shelf placements), every date pill (via `get-worksheet-xml`), and every text object with a font declaration (via `get-worksheet-xml` and `get-dashboard-xml`). Multi-DS workbooks inventory per DS.
- **Phase 2 Extract Format Strings.** For each measure placement, capture the resolved format string from the worksheet XML. For each date pill, capture the date-format string. For each text object, capture font family and font size.
- **Phase 3 Detect Drift.** Compare format strings within each drift type per the classification rules in `skill-expertise/drift_catalog.md`. First finding for a drift type establishes the baseline; subsequent format strings that differ fire the drift rule.
- **Phase 4 Assemble Report.** Group findings by drift type (Currency, Decimals, Date, Separator, Font Family, Font Size, Negative Treatment) and severity (Blocking, Warning, Info). Every finding includes a Desktop-fix instruction. Report shape follows `skill-expertise/report_template.md`.
- **Phase 5 Deliver.** Compact chat summary first (drift-type counts + top 3 findings). Offer to write the full report to Downloads (`.md` or `.txt`).

## The 7-Drift Catalog

Full detail lives in `skill-expertise/drift_catalog.md`. Summary:

1. **F-CURRENCY-01 Currency-Symbol Mismatch.** Measures within the same DS use inconsistent currency symbols ($, €, £, ¥, etc.) or mix formatted-currency with plain-number formatting.
2. **F-DECIMAL-02 Decimal-Places Mismatch.** Same measure appears with different decimal-place formats across worksheets (SUM(Sales) shows as $1,234 on one sheet and $1,234.56 on another).
3. **F-DATE-03 Date-Format Mismatch.** Same date field renders with different format strings across worksheets (MM/DD/YYYY on one, DD-MMM-YYYY on another, YYYY-MM-DD on a third).
4. **F-SEPARATOR-04 Thousands-Separator Mismatch.** Same measure uses inconsistent thousands separators (1,234 vs 1234 vs 1 234 vs 1.234).
5. **F-FONT-FAMILY-05 Font-Family Drift.** Multiple font families used across text objects, axis labels, tooltips, or worksheet titles without a stated design rationale.
6. **F-FONT-SIZE-06 Font-Size Drift.** Font sizes vary across similar text elements (worksheet titles at 12pt on some sheets and 14pt on others; tooltip labels at 9pt vs 11pt).
7. **F-NEGATIVE-07 Negative-Number-Treatment Drift.** Negative numbers rendered inconsistently (parentheses `(1,234)` vs minus-sign `-1,234` vs red-color vs both).

## Hard Constraints

**HC#1 Read-only always.** Never invoke `author-calc`, `bind-template`, `build-and-apply-worksheet`, or any mutating tool. Every finding is a Desktop-fix instruction the user applies manually via right-click > Format > select field/axis/tooltip > adjust.

**HC#2 One workbook per run.** Multi-workbook audits are refused. Users invoke separately per workbook.

**HC#3 Bulk-action refusal.** If the user asks to fix all format drift or align every currency symbol, refuse and route: format changes are Desktop-manual per HC#1.

**HC#4 No fabricated findings.** Every finding cites a specific drift-catalog rule ID (F-CURRENCY-01 through F-NEGATIVE-07) with the specific format strings that differ. If a format string cannot be read (e.g., `get-worksheet-xml` fails on a dashboard-bound sheet), flag UNSCANNED with `reason: fallback_unavailable`.

**HC#5 User-named-drift-type wins.** If the user asks for just check the date-format drift or audit only currency symbols, run only the specified drift type and skip the rest.

**HC#6 Never localize.** Locale-fragility (regional date-format collisions, hard-coded currency for global audiences) routes to i18n-scanner. Drift Scanner treats format strings as-authored, not as-locale-appropriate.

**HC#7 Sentinel discipline.** Use `null`, `[]`, `unscanned` for missing data. Never blank fields in the handoff schema.

**HC#8 Refuse to fabricate.** If the V-gate cannot pass after one retry, refuse delivery and diagnose. Never fake a V-gate pass.

**HC#9 Partial-info handling.** If the ask includes partial context (audit format drift but skip the fonts), deliver on the specified drift types and note which were skipped.

**HC#10 Adjacent-skill routing.** Text-copy correctness routes to `desktop-spellcheck`. Locale fragility routes to `i18n-scanner`. Dashboard assembly hygiene routes to `dashboard-preflight`. Chart-type selection routes to `chart-swap-advisor`.

**HC#11 Baseline-first classification.** For each drift type within a DS scope (or workbook scope for fonts), the first observed format string becomes the baseline. Subsequent format strings that differ fire the drift rule. Never invent a synthetic baseline; use the first-seen format string.

**HC#12 Cross-DS drift is Info-by-default.** Same measure name across different data sources with different formats is Info-tier, not Warning, unless a rationale is missing from the workbook caption. Multi-currency reporting is a legitimate use case; drift within one DS is not.

## Common Mistakes

Behaviors this skill must never exhibit, even under user pressure:

1. **Inferring drift from field name alone.** Two measures named Sales on different worksheets are not automatically a mismatch; read the actual format strings from XML. Names are user-authored and unreliable.
2. **Fabricating a drift finding to fill an empty severity band.** If Blocking count is zero, render `_None._`. Never invent a fake drift finding.
3. **Rewriting the drift catalog mid-run.** The 7-drift catalog and severity assignments are locked in `skill-expertise/drift_catalog.md`.
4. **Silently skipping placements that fail `get-worksheet-xml`.** Every placement identified in Phase 1 must appear in the report, even if downstream format-string extraction fails. Missing placements are UNSCANNED, not omitted.
5. **Applying a fix in Desktop.** All findings are Desktop-manual per HC#1. Never invoke `author-calc`, `bind-template`, or any mutating tool.
6. **Confusing legitimate multi-currency reporting with drift.** Cross-DS format differences with a documented rationale are Info-tier, not Warning per HC#12.
7. **Treating font-family drift as always-Warning.** Two font families for the same element category (e.g., Tableau Light for KPIs vs Tableau Book for body text) is a legitimate design choice when documented. Undocumented drift is the Warning case.

## Validation Gate (3-Check Read-Only)

**V1 Format-String Completeness.** Every measure placement, date pill, and text object identified in Phase 1 has a resolved format string in Phase 2 (or sentinel `unscanned` with rationale). No placements silently omitted.

**V2 Drift-Catalog Match.** Every finding references a specific catalog rule ID (F-CURRENCY-01 through F-NEGATIVE-07) with the two-or-more differing format strings that fired the rule.

**V3 Handoff Completeness.** Every field in `format_drift_report/1` populated per `skill-expertise/handoff_schema.md`. Sentinel values acceptable per HC#7.

Any V-gate failure blocks delivery per HC#8. Fail-open is NOT applied since the skill is read-only.

## Tool Sequence

Locked sequence to minimize latency and honor tool dependencies.

- **Phase 0.** Reuse session-context `get-workbook-inventory` if available. Otherwise, call `get-workbook-inventory` + `list-worksheets` + `list-dashboards` + `list-workbook-data-sources` in parallel.
- **Phase 1.** `list-available-fields` (verbosity: full) per DS in parallel. `search-workbook-fields` for shelf placements per measure. Batch worksheet XML reads (`get-worksheet-xml`) in groups of ~10 with inline progress notes for workbooks with 30+ worksheets.
- **Phase 2.** Extract format strings from Phase 1 XML in memory. No additional tool calls.
- **Phase 3-4.** In-memory drift detection and assembly. No tool calls.
- **Phase 5.** No tool calls unless file-write opted in.

**Batching rules.**

- Never call `get-workbook-inventory` twice per run.
- Never call `list-available-fields` twice per DS unless truncated.
- `get-worksheet-xml` called once per worksheet. Reuse session-context reads from prior skills.
- `resolve-field` only when a fields DS scope is ambiguous.

**Early-exit condition.** If Phase 1 inventory returns zero measure placements AND zero date pills AND zero text objects, skip Phases 2-4, deliver no formattable elements in this workbook report.

## Handoff Contract

Emits `format_drift_report/1` per `skill-expertise/handoff_schema.md`. Consumed by:

- **publish-readiness.** Format drift counts inform pre-publish hygiene summary.
- **workbook-auditor.** Format-drift findings enrich change digests when the user aligns formats.
- **i18n-scanner.** Format drift findings that overlap with locale patterns are noted (e.g., `$` symbol at the currency drift level is a candidate locale finding).

## Known Limitations

- `get-worksheet-xml` reliability on dashboard-bound populated sheets (platform gap). Fallback: use `list-available-fields` metadata (limited format-string surface). Placements flagged UNSCANNED when fallback fails.
- Cannot detect rendered visual differences that are not encoded in the format string (e.g., a locale override at render time).
- Cannot detect font drift on chart marks (mark labels vs. axis labels) when the underlying mark type doesnt expose font attributes in XML.
- One workbook per run. Batching refused per HC#3.

## Error Handling

| Failure | Response |
|---|---|
| `get-workbook-inventory` fails | Report tool failure, ask user to reopen workbook. Do not proceed. |
| `list-available-fields` fails | Retry once. If still failing, refuse delivery and diagnose. Do not partially inventory. |
| `get-worksheet-xml` fails on dashboard-bound sheet | Fallback to `list-available-fields` metadata. Flag partial placements as UNSCANNED with `reason: fallback_unavailable`. |
| `get-dashboard-xml` fails | Flag dashboard-level text-object findings as UNSCANNED. Continue with worksheet-level checks. |
| `search-workbook-fields` fails | Flag shelf-placement-count findings as UNSCANNED. Continue with format-string audit on any placements found via `get-worksheet-xml` direct reads. |
| Datasource disconnects mid-run | Flag every check depending on that DS as UNSCANNED with `reason: tool_failure`. Continue with DS-independent checks (font drift). |
| Field-level permission denial (RLS) blocks a measure | Flag the specific placement UNSCANNED with `reason: fallback_unavailable`. Never treat as absence. |
| Workbook has zero measure placements AND zero date pills AND zero text objects | Report no formattable elements in this workbook. Suggest viz-planner or worksheet-builder. |
| User asks to align formats automatically | Refuse per HC#1 and HC#3. Route to Desktop UI (Format pane) with the list of drift findings. |
| User asks about color palette drift | Refuse per HC#10 and scope note. |
| User asks about text spelling | Refuse per HC#10. Route to desktop-spellcheck. |
| User asks about locale fragility | Refuse per HC#10. Route to i18n-scanner. |

## Examples

**Example 1: Clean workbook.** User: Check my formatting. Agent inventories 45 measure placements, 12 date pills, 28 text objects across 3 data sources. All format strings within each drift category align. Reports 0 Blocking, 0 Warning, 0 Info. Format-string consistency across all 3 data sources and 8 worksheets. Emits handoff.

**Example 2: Currency-symbol drift.** User: Are my numbers consistent? Agent finds SUM(Sales) formatted as `$#,##0` on one worksheet and `#,##0` (no currency) on another within the same DS. Reports F-CURRENCY-01 Warning with the two format strings and the Desktop-fix: Right-click SUM(Sales) on the affected worksheet > Format > Numbers > Currency (Custom).

**Example 3: Cross-DS Info.** User: Format drift audit. Agent finds Sales measure formatted as `$#,##0` in USD DS and `€#,##0` in EUR DS. Reports F-CURRENCY-01 Info (not Warning) per HC#12: Multi-DS currency difference detected. Not flagged as drift; documented as legitimate multi-currency reporting.

**Example 4: Bulk-action refusal.** User: Fix all format drift. Agent refuses per HC#1 and HC#3: Format changes are Desktop-manual. I can list every drift finding with the specific right-click > Format path, and you apply each in Desktop. Want the full list?

**Example 5: Scoped audit (HC#5).** User: Just check the date formats. Agent runs F-DATE-03 only, reports drift findings for date pills only, notes in the handoff that other drift types were skipped by user request.

## Relationship to Other Skills

- **Peer to desktop-spellcheck.** Spellcheck owns text-copy correctness. Format Drift Scanner owns format-string consistency.
- **Peer to i18n-scanner.** i18n-scanner owns locale-fragility. Format Drift Scanner owns cross-worksheet drift regardless of locale.
- **Upstream of publish-readiness.** Drift findings inform pre-publish hygiene.
- **Adjacent to dashboard-preflight.** Preflight owns assembly hygiene. Drift Scanner owns format-string hygiene.
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
