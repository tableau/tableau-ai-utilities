---
name: workbook-summary-onepager
description: "Use when the user says 'Summarize this workbook', 'one-pager please', 'stakeholder summary', 'hand off this workbook'. Writes a one-page summary for someone who won't open Desktop: what it shows, key metrics, data sources, dashboards, and known limits. Read-only."
---

# Workbook Summary Onepager

## When to use (full trigger detail)

Produce a single-page onepager summarizing a Tableau workbook for handoff to a stakeholder who wont open Desktop. Five locked sections. what this workbook shows (plain language), key metrics defined (calc-family), data sources used (data-and-model), dashboards included (build-and-design), known limitations (author-declared or empty-state). Read-only. Opportunistically consumes calc-documenter, data-model-documenter, and dashboard-caption-audit handoffs when available in session context; local-extract fallback otherwise with formula-hash and workbook-fingerprint staleness detection per HC#15. Two-tier delivery. compact Tier A chat summary plus opt-in Tier B file save as .md or .txt per HC#12. Trigger with summarize this workbook, one-pager please, workbook onepager, stakeholder summary, workbook-summary-onepager, hand off this workbook. Do NOT trigger on. exporting a live-data snapshot (out of scope, structural summary only), rewriting or editing the workbook based on the summary (route to calc-writer or viz-planner), multi-workbook batch summary (out of scope), or auditing dashboard tab order or print layout (route to dashboard-tab-order or dashboard-print-check).

## Purpose

Produce a single-page onepager summarizing a Tableau workbook for a stakeholder who will not open Desktop. Five locked sections aggregated from upstream handoffs (calc-documenter, data-model-documenter, dashboard-caption-audit) when available in session context; local-extract fallback otherwise. Read-only. File-write only for the onepager artifact. Every section cites its signal source per HC#3 so the reader can trace where each fact came from.

## Trigger Conditions

- summarize this workbook
- one-pager please
- workbook onepager
- stakeholder summary
- workbook-summary-onepager
- hand off this workbook
- give me a workbook summary
- write up this workbook for a colleague

## Do NOT Trigger On

- Live-data snapshot (query workbook for current metric values) → out of scope. Summary is structural, not data-content.
- Rewriting or editing the workbook based on the summary → route to `calc-writer` or `viz-planner`.
- Multi-workbook batch summary → out of scope. One workbook per run.
- Auditing dashboard tab order → route to `dashboard-tab-order`.
- Auditing dashboard print layout → route to `dashboard-print-check`.
- Grading the workbook design → route to `viz-critique-pro-studio`.
- Documenting every calc in detail → route to `calc-documenter` for the full dictionary.
- Explaining a single specific calc in plain language → route to `calc-explainer`.

## Scope Boundaries

- **IN.** One workbook per run. Read-only. Five-section locked catalog. Opportunistic handoff consumption from `calc_documentation/1`, `data_model_documentation/1`, and `caption_audit_report/1` when in session context. Local-extract fallback via `list-available-fields`, `get-workbook-inventory`, `get-worksheet-xml`, `get-dashboard-xml`. `signal_source` labeled per section (`handoff` or `local_extract`). Handoff staleness detection per HC#15 (portfolio-wide). Two-tier delivery: compact Tier A chat + opt-in Tier B file save as `.md` or `.txt`.
- **OUT.** Any workbook mutation. Live-data snapshot (queries for current metric values). Multi-workbook runs. PDF or DOCX output (`.md` and `.txt` only). Rewriting content the author declared (author caption preserved verbatim per HC#5).

## The 5-Section Onepager Catalog (Locked)

Every section is populated from upstream handoff, local extract, or an empty-state prose fallback. No section is silently omitted. Full detection criteria and worked examples in `skill-expertise/section_catalog.md`.

| # | Section | Signal source preference | Required |
|---|---|---|---|
| 1 | What this workbook shows | Workbook-level author caption (if present), else local-extract dashboard-title aggregation | Yes |
| 2 | Key metrics defined | `calc_documentation/1` handoff → top 5 most-referenced calcs. Local-extract fallback: `list-available-fields` on primary datasource. | Yes |
| 3 | Data sources used | `data_model_documentation/1` handoff → per-DS summary with row count and relationship shape. Local-extract fallback: `get-workbook-inventory` datasource enumeration. | Yes |
| 4 | Dashboards included | `caption_audit_report/1` handoff → dashboard names with title/caption presence flags. Local-extract fallback: `get-workbook-inventory` dashboard enumeration. | Yes |
| 5 | Known limitations | Workbook-level author caption Known limitations: section (if declared), else empty-state prose (No known limitations documented in workbook caption.) | Yes |

**No section omitted.** If a section cant be populated with real evidence, the skill renders an empty-state prose fallback rather than skipping the section per HC#5 and HC#6.

**Section ordering is locked** per HC#7. Same input produces byte-identical section ordering.

## Workflow Phases

- **Phase 0 Scope.** Confirm workbook is open via `get-workbook-inventory`. If the call fails, returns no workbook, or the session is disconnected, stop and tell the user to confirm Tableau Studio is open with a workbook loaded — do not proceed to Phase 1 on an empty or failed inventory read. Ensure one workbook per run per HC#2. When local-extract falls back to `list-available-fields` (Section 2) and that call returns empty on a connected-but-broken datasource, retry once, then render Section 2 as Metric definitions could not be read this run (tool error) with `signal_source: empty_state` and reason `read_failed`. Never use the No calcs defined prose for a read failure.
- **Phase 1 Handoff Discovery.** Check session context for three upstream handoffs: `calc_documentation/1`, `data_model_documentation/1`, `caption_audit_report/1`. For each, verify workbook-fingerprint match against current state per HC#15 staleness detection. Populate `handoffs_available[]` with fresh handoffs; log stale or missing handoffs in `handoffs_missing[]`.
- **Phase 2 Section Population (numbered checklist).**
  1. Section 1 (What this workbook shows): read workbook caption via `get-workbook-inventory` (if the XML exposes it). If empty, aggregate dashboard titles from `get-dashboard-xml` across all dashboards — issue these as one batched pass over the dashboard list rather than one call per dashboard, and reuse the same batch for Section 4s dashboard enumeration instead of re-reading.
  2. Section 2 (Key metrics): if `calc_documentation/1` handoff is fresh, extract top 5 most-referenced calcs from the reference graph. If missing/stale, local-extract the primary datasources calc list via `list-available-fields` and rank by name-recency (weaker signal, labeled clearly).
  3. Section 3 (Data sources): if `data_model_documentation/1` handoff is fresh, extract per-DS summary. If missing/stale, local-extract from `get-workbook-inventory` datasource enumeration with `row_count: unknown` sentinel.
  4. Section 4 (Dashboards): if `caption_audit_report/1` handoff is fresh, extract dashboard names with title/caption presence flags. If missing/stale, local-extract dashboard names from `get-workbook-inventory` with `title_present: unknown` sentinels.
  5. Section 5 (Known limitations): parse workbook caption for a Known limitations: or Limitations: section. If absent, render empty-state prose.
- **Phase 3 Signal-Source Attribution.** For each section, populate `signal_source: handoff | local_extract | empty_state`. HC#5 requires transparent attribution; user must be able to tell where each fact came from.
- **Phase 4 Validate.** Run the 4-check V-gate: section coverage, signal-source attribution, ordering determinism, handoff completeness.
- **Phase 5 Deliver.** Two-tier: compact Tier A chat summary with all 5 sections in ~25 lines. Optional Tier B file save requires user path confirmation per HC#12 and format choice (`.md` or `.txt` only).

## Hard Constraints

**HC#1 Read-only against the workbook always.** Never mutates. File-write only for the onepager artifact (Tier B).

**HC#2 One workbook per run.** Multi-workbook runs refused.

**HC#3 5-section coverage locked.** No section omitted, no fabricated section added. Every section renders content or an empty-state prose fallback.

**HC#4 Refuse to fabricate.** No inferred metrics, no guessed row counts, no invented author intent. Sentinels: `null`, `unknown`, empty-state prose.

**HC#5 Signal-source labeled per section.** Every section emits `signal_source: handoff | local_extract | empty_state` so the reader can trace attribution. Never render a fact without stating its origin.

**HC#6 Author caption preserved verbatim.** If the workbook has an author caption (workbook-level or per-dashboard), its quoted byte-identical in the relevant section. Skill supplements around author intent; never rewrites or paraphrases.

**HC#7 Ordering determinism** (portfolio-wide HC#14). Section order locked (Section 1 → Section 5). Same input produces byte-identical output.

**HC#8 Diff-mode transparency** (portfolio-wide HC#13). Repeat invocations against unchanged workbook + handoff state emit `diff_mode: reused_verbatim` in Tier A. Fresh-scan / reused-verbatim / targeted-rescan enum.

**HC#9 Handoff-or-local labeled.** Every handoff-consuming section records which handoffs were fresh, which were stale, and which fell back to local-extract. `handoffs_consumed[]` and `handoffs_missing[]` populated in the report metadata.

**HC#10 Never silent file write.** Tier B save requires user path confirmation AND format choice (`.md` or `.txt`). No default writes to Downloads.

**HC#11 Empty-state prose over blank sections.** When a section has no data (no calcs, no dashboards, no author-declared limitations), render explicit empty-state prose (No calcs defined in this workbook, No known limitations documented in workbook caption) rather than a blank line.

**HC#12 Length cap.** Tier A output stays under 30 lines total across all 5 sections. Tier B is unbounded but structured per the same 5-section skeleton.

**HC#13 Handoff staleness detection required** (portfolio-wide HC#15). For each of the 3 upstream handoffs, verify workbook-fingerprint match against current state. Mismatch forces local-extract fallback for that section. Fingerprint mechanism verified sound during dashboard-tab-order behavioral run.

**HC#14 Reference-file grounding.** All 5 sections cite their detection criteria and worked examples in `skill-expertise/section_catalog.md`. Skill cites the reference file when a user challenges section content.

**HC#15 File format lock.** Tier B supports `.md` or `.txt` only. If user requests an unsupported format, skill refuses with a route to convert `.md` externally.

**HC#16 Wide-workbook scale handling.** For workbooks with 50+ calcs or 10+ dashboards, skill emits a wide-workbook-notice in Tier A (this workbook has N calcs and M dashboards; Section 2 truncates to top 5 by reference count, Section 4 truncates to top 10 dashboards, full list lands in Tier B). Truncation applies to Tier A only; Tier B is unbounded.

## Validation Gate (4-Check)

- **V1 Section Coverage.** All 5 sections rendered in locked order.
- **V2 Signal-Source Attribution.** Every section has `signal_source` populated per HC#5.
- **V3 Ordering Determinism.** Same workbook + same handoff state → byte-identical output per HC#7.
- **V4 Handoff Completeness.** `handoffs_consumed[]` and `handoffs_missing[]` populated. Fingerprint match verified for every consumed handoff.

## Two-Tier Delivery

**Tier A (chat).** Compact 5-section summary in ~25 lines total.

Template:

```
**Workbook Summary Onepager: {workbook_name}**
Signal sources: {N} handoff, {N} local_extract, {N} empty_state
Diff mode: {fresh_scan | reused_verbatim | targeted_rescan}

**1. What this workbook shows.** {plain-language summary}
**2. Key metrics defined.** {top 5 calcs by reference count}
**3. Data sources used.** {datasource names with row-count / relationship-shape summary}
**4. Dashboards included.** {dashboard names with title/caption presence flags}
**5. Known limitations.** {author-declared limitations OR empty-state prose}

Save full onepager to file? (.md or .txt)
```

**Tier B (opt-in file save).** Full onepager `.md` (default) or `.txt` written to user-confirmed path per HC#10. Unbounded length; same 5-section skeleton. Includes handoff YAML block with `signal_source` per section.

## Handoff Schema

Emits `workbook_summary/1`:

```yaml
workbook_summary:
  version: 1
  run_timestamp: <ISO 8601>
  workbook:
    name: <string>
    fingerprint: <sha256>
  diff_mode: <fresh_scan | reused_verbatim | targeted_rescan>
  handoffs_consumed:
    - schema: <calc_documentation/1 | data_model_documentation/1 | caption_audit_report/1>
      fresh: <boolean>
      fingerprint_match: <boolean>
  handoffs_missing: [<schema_name>]
  sections:
    - id: 1
      name: What this workbook shows
      signal_source: <handoff | local_extract | empty_state>
      content: <string>
    - id: 2
      name: Key metrics defined
      signal_source: <handoff | local_extract | empty_state>
      content: <string>
      metric_count: <int>
      truncation_applied: <boolean>
    - id: 3
      name: Data sources used
      signal_source: <handoff | local_extract | empty_state>
      content: <string>
    - id: 4
      name: Dashboards included
      signal_source: <handoff | local_extract | empty_state>
      content: <string>
      dashboard_count: <int>
      truncation_applied: <boolean>
    - id: 5
      name: Known limitations
      signal_source: <handoff | local_extract | empty_state>
      content: <string>
      author_declared: <boolean>
  tier_b_saved:
    path: <string|null>
    format: <md | txt | null>
  v_gate:
    v1_section_coverage: <pass|fail>
    v2_signal_source_attribution: <pass|fail>
    v3_ordering_determinism: <pass|fail>
    v4_handoff_completeness: <pass|fail>
```

Downstream consumers: `publish-readiness` (post-summary pre-publish sweep), `workbook-auditor` (summary delta across runs).

## Common Mistakes (Anti-Patterns)

- **Fabricating row counts or metric values.** When `data_model_documentation/1` handoff is missing, emit `row_count: unknown` sentinel. Never guess.
- **Silently omitting a section.** HC#3 requires all 5 sections rendered. Empty-state prose per HC#11 for sections with no data.
- **Rewriting the author caption.** HC#6 preserves author intent verbatim. Skill supplements around it; never paraphrases.
- **Auto-invoking calc-documenter / data-model-documenter / dashboard-caption-audit.** Opportunistic consumption per HC#9; never chains-call upstream skills. User runs upstream skills separately if fresh handoffs are wanted.
- **Silent file write on Tier B save.** HC#10 requires path confirmation and format choice (`.md` or `.txt` only).
- **Requesting unsupported output format.** PDF, DOCX, HTML refused per HC#15. Route to external converter.
- **Ignoring handoff staleness.** HC#13 requires fingerprint verification. Stale handoff forces local-extract fallback, never silent stale-data rendering.

## Adjacent-Skill Routing

- **Upstream opportunistic:** `calc-documenter` (produces `calc_documentation/1`), `data-model-documenter` (produces `data_model_documentation/1`), `dashboard-caption-audit` (produces `caption_audit_report/1`).
- **Downstream opt-in:** `publish-readiness` (post-summary pre-publish sweep), `workbook-auditor` (summary delta tracking).
- **Refusal routes:** live-data snapshot → out of scope; workbook rewrites → `calc-writer` / `viz-planner`; tab-order audit → `dashboard-tab-order`; print-layout audit → `dashboard-print-check`; dashboard design scoring → `viz-critique-pro-studio`.

## Known Limitations

- **Live-data snapshot out of scope.** Summary is structural, not data-content. Section 2 lists metric definitions; not their current values.
- Supports `.md` and `.txt` only per HC#15.
- **Workbook-level author caption may not be exposed by all `get-workbook-inventory` implementations** in this environment. Section 1 falls back to dashboard-title aggregation if the caption is empty or unreadable.
- **`get-worksheet-xml` reliability gap on dashboard-bound sheets**. Section 4 dashboard enumeration may hit unreadable dashboards; skill emits `unknown` sentinel for those dashboards per HC#5.
- **DPC-style aspect-ratio and orientation properties are out of scope.** Section 4 lists dashboards by name and caption presence; layout details defer to `dashboard-print-check`.
- **`resolve-field` case-sensitivity concern** (a known platform gap, shared with calc-family skills). Section 2 metric-ranking uses handoff data preferentially to avoid triggering this gap.

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
