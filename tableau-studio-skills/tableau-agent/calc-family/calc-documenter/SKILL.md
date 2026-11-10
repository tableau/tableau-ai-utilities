---
name: calc-documenter
description: "Use when the user says 'Document my calcs', 'calc dictionary', 'map my calc dependencies', 'which calcs do I have?' Documents every calculated field in the workbook: formula, fields used, what uses it, sheets and dashboards, and aggregation level. Read-only."
---

# Calc Documenter

## When to use (full trigger detail)

Generate structural documentation for every calculated field in a Tableau workbook. Emits a per-calc dictionary with formula, fields referenced, reference graph (uses / used-by), sheets and dashboards using the calc, inferred aggregation level (row-level / aggregate / LOD fixed-include-exclude), and any existing author caption preserved verbatim. Read-only. Trigger with document my calcs, generate calc docs, calc dictionary, reference graph for calcs, calc-documenter, which calcs do I have, map my calc dependencies. Do NOT trigger on. single-calc explanation (defer to calc-explainer), calc syntax debugging (defer to calc-debugger), calc-family hygiene or naming audit (defer to calc-linter), applying documentation changes to calc captions (this skill is read-only), performance optimization (defer to calc-optimizer), workbook change-over-time (defer to workbook-auditor).

## Purpose

Generate structural documentation for every calculated field in a Tableau workbook. Emits a per-calc dictionary sorted by dependency order (or alphabetical fallback) with formula, referenced fields, reference graph, sheet/dashboard usage, inferred aggregation context, and preserved author captions. Read-only. Every entry cites XML evidence; no fabrication.

Positioned parallel to calc-inventory in the calc-family pipeline. Calc-inventory discovers what calcs exist; calc-documenter documents what each one is, does, and connects to. Downstream skills (calc-explainer, workbook-auditor, publish-readiness) consume the handoff.

## Trigger Conditions

- document my calcs
- generate calc docs
- calc dictionary
- reference graph for calcs
- calc-documenter
- which calcs do I have
- map my calc dependencies
- who uses this calc

## Do NOT Trigger On

- Single-calc natural-language explanation (defer to `calc-explainer`).
- Calc syntax debugging or NULL diagnosis (defer to `calc-debugger`).
- Calc-family hygiene, naming, or commenting audit (defer to `calc-linter`).
- Rewriting or applying documentation changes (all fixes are Desktop-manual per HC#1).
- Performance optimization (defer to `calc-optimizer`).
- Change-over-time (defer to `workbook-auditor`).
- Data-quality issues (defer to `data-quality-review`).
- Chart-type advisory (defer to `chart-swap-advisor`).
- Format-string drift (defer to `format-drift-scanner`).

## Scope Boundaries

- **IN.** One workbook per run. Every calculated field across every datasource in the workbook. Formula extracted verbatim from XML. Fields referenced (measures, dimensions, parameters, other calcs) parsed from formula and cross-referenced against `list-available-fields`. Reference graph (uses / used-by) constructed across the calc family. Sheets and dashboards pinning each calc to a shelf. Inferred aggregation context (row-level, aggregate, LOD fixed-include-exclude). Author captions preserved verbatim. Read-only. Handoff schema `calc_documentation/1`.
- **OUT.** Any workbook mutation. Applying doc changes to calc captions. Explaining a specific calc in plain language (calc-explainer). Naming or hygiene audit (calc-linter). Performance analysis. Multi-workbook runs.

**Cross-datasource workbooks.** Each datasources calcs documented in its own section. Cross-datasource references (calc in DS-A referring to a field in DS-B) flagged in the doc entry as `cross_datasource_reference`.

## The 5-Dimension Documentation Model

Every calc gets these five documentation dimensions:

| Dimension | Source | Verbatim? |
|---|---|---|
| Formula | `list-available-fields` `formula` attribute, with internal `Calculation_NNNN...` field-name tokens swapped for their resolved caption/name (see HC#16) | Yes, modulo caption substitution |
| Fields referenced | Parsed from formula, resolved via `resolve-field` | List, deduplicated |
| Reference graph | Cross-computed from every calcs Fields Referenced list | Directed (uses → used-by) |
| Sheet/dashboard usage | `get-worksheet-xml` shelves + `get-dashboard-xml` filters/parameters | List by name |
| Aggregation context | Inferred from formula (SUM/AVG/COUNT → aggregate; FIXED/INCLUDE/EXCLUDE → LOD-typed; no aggregate → row-level) | Enum |
| Author caption | XML `caption` attribute or worksheet-scoped description | Preserved verbatim |

**Sixth dimension (optional).** If a `<comment>` or annotation exists in the XML attached to the calc, include as `author_annotation`. Rare in most workbooks.

## Workflow Phases

- **Phase 0 Scope.** Confirm workbook is open via `get-workbook-inventory`. Enumerate datasources via `list-workbook-datasources`. For each datasource, enumerate calcs via `list-available-fields` filtered to calc-type fields. Ask user to scope only if total calc count exceeds 100 (default: all).
- **Phase 1 Extract.** For each calc: read formula, caption, aggregation attribute from XML. Parse formula for field references. Resolve each reference via `resolve-field` (batched per HC#5). Extract sheet/dashboard usage via `get-worksheet-xml` and `get-dashboard-xml`.
- **Phase 2 Build Reference Graph.** For every pair of calcs (A, B), if As formula references B, record A → B (uses) and B → A (used-by). Detect cycles; flag any circular dependency as `CD-CYCLE-01`.
- **Phase 3 Infer Aggregation Context.** For each calc, classify as row-level, aggregate, or LOD-fixed/LOD-include/LOD-exclude via formula pattern match. Cite the pattern that fired the classification.
- **Phase 4 Assemble Dictionary.** Sort calcs by dependency order (least-referenced first), fall back to alphabetical on ties. Group by datasource. Emit per-calc entries per `skill-expertise/documentation_template.md`.
- **Phase 5 Deliver Tier A.** Compact chat summary: total calc count, dependency-graph shape (linear, tree, DAG, cyclic), top 3 most-referenced calcs, save-file offer.
- **Phase 6 Deliver Tier B (opt-in).** Full dictionary written to Downloads as `.md` (default) or `.txt` only after user confirms path.

## Hard Constraints

**HC#1 Read-only always.** Never invoke `author-calc`, `bind-template`, `build-and-apply-worksheet`, or any mutating tool. Documentation is emitted; nothing is written back to the workbook.

**HC#2 One workbook per run.** Multi-workbook doc runs refused. Users invoke separately.

**HC#3 Bulk-action refusal.** Document all calcs and apply captions refused; skill is read-only per HC#1.

**HC#4 Locked five-dimension model.** Every calc entry includes formula, fields referenced, reference graph position, sheet/dashboard usage, aggregation context, and (if present) author caption. No dimension omitted. No fabricated dimension added.

**HC#5 Batching cap.** `resolve-field` batches capped at 20 per parallel call; `get-worksheet-xml` batches capped at 10 sheets per parallel call. Sequence remaining sheets in additional batches.

**HC#6 Never auto-invoke another skill.** Adjacent-skill routing (calc-explainer for natural-language explanation, calc-linter for hygiene) is an opt-in handoff.

**HC#7 Sentinel discipline.** Use `null`, `[]`, `unresolved` for missing XML fields. Never blank fields in the handoff schema. Field references that cannot be resolved via `resolve-field` render as `unresolved: <raw_reference>` in the doc entry.

**HC#8 Refuse to fabricate.** V-gate refuses fabricated field references, invented aggregation classifications, or missing formula citations.

**HC#9 Partial-info handling.** If `list-available-fields` returns partial results (per a known reliability gap), flag `PARTIAL-EXTRACT` for that datasource with reason; do not proceed with incomplete evidence.

**HC#10 Adjacent-skill routing.** Natural-language explanation → `calc-explainer`. Hygiene audit → `calc-linter`. Debugging → `calc-debugger`. Optimization → `calc-optimizer`.

**HC#11 Author caption preserved verbatim.** If the calc has an existing caption, description, or annotation in XML, include it in the entry as `author_description` or `author_annotation` verbatim. Never rewrite, paraphrase, or omit. Author intent is preserved even if it conflicts with the skills structural doc.

**HC#12 Never write the longform file silently.** File-save requires explicit user opt-in with path confirmation. Full dictionary lives in the file only; chat renders summary + top 3 only.

**HC#13 Guide the user actively.** Silence during evaluation is a defect. Announce progress on 50+ calc runs (per-datasource progress markers).

**HC#14 Cycle detection required.** Reference-graph construction detects and flags circular dependencies as `CD-CYCLE-01`. Never rendered as a valid dependency graph; cycles are flagged and the affected calcs marked `in_cycle: true`.

**HC#15 Ordering locked.** Dictionary entries render in dependency order (topological sort, least-referenced first). Alphabetical on ties. Within-datasource sort only; datasources render in `list-workbook-datasources` enumeration order.

**HC#16 Formula display must use resolved captions, not internal field IDs.** `list-available-fields` returns raw formula text containing internal tokens like `[Calculation_0831103151444568]` wherever the formula references another calc by its underlying column name rather than its caption. Before rendering a Formula line, every such token MUST be substituted with the referenced calc's resolved caption/name (e.g. `[Calculation_0831103151444568]` → `[Days to Ship Actual]`), using the same `resolve-field` lookups already performed for Fields Referenced in Phase 1. If a token cannot be resolved, leave it as the raw internal ID and flag it `"unresolved: <raw_token>"` per HC#7 — never silently display an unresolved internal ID as if it were final. When substitution occurs, append one line directly under the Formula block: `(stored internally as [<raw_token>, ...]; captions shown above)` so the reader knows the formula was translated, not misquoted. This check is part of V2 (Formula Citation) and blocks delivery on failure per HC#8.

## Two-Tier Delivery

### Tier A: Compact chat summary (always renders)

Target under 25 lines.

```
**Calc Documentation: {workbook_name}**
Datasources: {N} · Total calcs: {N} · Graph shape: {linear | tree | DAG | cyclic}
{Cycle banner if CD-CYCLE-01 fired, one line}

Per-datasource TL;DR:
- {DS-A}: {N} calcs, {N} row-level, {N} aggregate, {N} LOD, {N} with author captions
- {DS-B}: same shape

Top 3 most-referenced calcs (used-by count):
1. {calc_name}: used by {N} other calcs, on {M} sheets
2. {calc_name}: used by {N}, on {M}
3. {calc_name}: used by {N}, on {M}

Save the full dictionary to Downloads? (.md default, .txt option, or skip)
```

### Tier B: Full dictionary file (opt-in)

Path: `{Downloads}/{workbook_name}_calc-documentation.md` (or `.txt`). Fresh-filename discipline on collision.

Contents per `skill-expertise/documentation_template.md`:

- Header (skill version, timestamp, workbook name, calc count, graph shape).
- Cycle warnings section (if any CD-CYCLE-01 fired).
- Per-datasource sections with per-calc entries in dependency order:
  - Name and caption (author caption verbatim if present).
  - Formula (verbatim from XML, code-block formatted).
  - Fields referenced (list; resolved names).
  - Reference graph position: `Uses: [list]`, `Used by: [list]`.
  - Sheet/dashboard usage: `On sheets: [list]`, `On dashboards: [list]`.
  - Aggregation context: `Type: {row-level | aggregate | LOD-fixed | LOD-include | LOD-exclude}`. Pattern cited.
  - Cross-datasource references (if any).
  - Author annotation (if any XML `<comment>` attached).
- Handoff schema payload (`calc_documentation/1`) at the bottom.

**File-save discipline (HC#12).** User opts in, format confirmed, path confirmed OS-agnostically, fresh-filename discipline on collision.

## Validation Gate (4-Check Read-Only)

**V1 Dimension Coverage.** Every calc entry has all 5 required dimensions populated (formula, fields referenced, reference graph position, sheet/dashboard usage, aggregation context) or sentinel with reason.

**V2 Formula Citation.** Every field-reference cites the formula substring that mentioned it. No fabricated references. Formula display text contains no unresolved internal `Calculation_NNNN...` tokens where a caption resolution was available (HC#16); any token that genuinely could not be resolved is flagged, not silently shown raw.

**V3 Handoff Completeness.** Every field in `calc_documentation/1` populated per `skill-expertise/handoff_schema.md`.

**V4 Ordering + Cycle Discipline.** Entries render in dependency order (topological sort). Cycles flagged per HC#14. Author captions preserved per HC#11. Datasource enum order per HC#15.

V-gate failure blocks delivery per HC#8.

## Tool Sequence

- **Phase 0.** `get-workbook-inventory` (never twice per run). `list-workbook-datasources` for datasource enumeration. `list-available-fields` per datasource, filtered to calc fields.
- **Phase 1.** `resolve-field` per formula reference (batched, 20 per parallel call). `get-worksheet-xml` per worksheet with calcs on shelves (batched, 10 per parallel call). `get-dashboard-xml` per dashboard with calc-driven filters/parameters.
- **Phase 2-4.** In-memory reference-graph construction and dictionary assembly. No tool calls.
- **Phase 5.** Chat delivery. No tool calls.
- **Phase 6.** File-write to Downloads only on opt-in per HC#12.

**Batching rules.** Never call `get-workbook-inventory` twice per run. Never call `list-available-fields` twice per datasource. Batch `resolve-field` and `get-worksheet-xml` per HC#5. If a `get-worksheet-xml` batch call fails, retry the failed sheets individually rather than failing the whole batch — a single dashboard-bound sheet 500 (see Known Limitations) should not blank out usage data for the other sheets in that batch.

**Early-exit condition.** If `list-workbook-datasources` returns zero datasources (workbook not open or empty), exit with No datasources found; open a workbook with calculated fields to document.

## Handoff Contract

Emits `calc_documentation/1` per `skill-expertise/handoff_schema.md`. Consumed by:

- **calc-explainer.** Uses the reference graph to explain how a specific calc fits into the calc family.
- **calc-linter.** Uses author-caption presence to flag under-documented calcs.
- **calc-debugger.** Uses reference graph to trace NULL propagation across dependent calcs.
- **workbook-auditor.** Consumes documentation deltas across runs (calc added, removed, changed).
- **publish-readiness.** Verifies critical calcs are documented before publish.

## Known Limitations

- **`list-available-fields` reliability gap**. Some workbooks return partial calc lists. HC#9 flags PARTIAL-EXTRACT rather than fabricating.
- **Cross-datasource references.** Detected but not always resolvable if the target datasource isnt loaded. Rendered as `cross_datasource_reference: {ds_name}.{field_name}` without full resolution.
- **Table-calc computed context.** Table calcs (WINDOW_SUM, RUNNING_SUM, etc.) have partition/addressing configured on the worksheet, not in the calc XML. Aggregation context lists these as `table-calc`; specific addressing not documented per calc (defers to sheet-level docs).
- **Set / parameter references.** Documented as fields but the underlying set membership or parameter value list is not enumerated (thats set-audit and parameter-manager territory, both out of scope).
- **Author caption formatting.** Preserved verbatim including any markdown, line breaks, or special characters. No sanitization.
- **`get-worksheet-xml` reliability gap on dashboard-bound sheets.** Confirmed to intermittently 500 on populated worksheets already placed on a dashboard. When this fires for a given sheet, render that sheets `on_sheets`/`on_dashboards` contribution as `unresolved: xml-read-failed` per HC#7 sentinel discipline rather than omitting the dimension or silently rendering an incomplete usage list.

## Error Handling

| Failure | Response |
|---|---|
| Workbook not open | Ask: Please open the workbook youd like documented. |
| `get-workbook-inventory` fails | Retry once. If still failing, exit gracefully. |
| `list-workbook-datasources` returns empty | Exit with No datasources found; nothing to document. |
| `list-available-fields` returns partial | Flag PARTIAL-EXTRACT for that datasource per HC#9. |
| `resolve-field` returns no match for a formula reference | Render as `unresolved: <raw_reference>` in the entry per HC#7. |
| Circular calc dependency detected | Flag CD-CYCLE-01. Do not render a valid dependency chain. Mark affected calcs `in_cycle: true`. |
| `get-worksheet-xml` 500s on a dashboard-bound sheet | Retry that sheet once individually. If it still fails, render `on_sheets`/`on_dashboards` for that calc as `unresolved: xml-read-failed` per HC#7; do not fail the whole run. |
| Workbook has 100+ calcs | Ask user to scope; default to all. |
| Workbook has 0 calcs | Exit with No calculated fields found; nothing to document. |
| User asks to fix or apply captions | Refuse per HC#1. Route to Desktop-manual instructions. |
| User asks to explain a specific calc | Refuse per HC#10. Route to `calc-explainer` with handoff payload. |
| User asks to audit calc hygiene | Refuse per HC#10. Route to `calc-linter`. |
| User asks to document multiple workbooks | Refuse per HC#2. |
| User asks to skip V-gate | Refuse per HC#8. |
| User asks to save file without path confirmation | Refuse per HC#12. |
| User asks to omit the reference graph | Refuse per HC#4. Ref graph is a locked dimension. |

## Examples

**Example 1: Compact workbook, mixed calc types.**

User: document my calcs

Skill runs Phases 0-4 silently, delivers Tier A:

```
**Calc Documentation: Sales Overview**
Datasources: 2 · Total calcs: 18 · Graph shape: DAG

Per-datasource TL;DR:
- Orders: 12 calcs, 4 row-level, 6 aggregate, 2 LOD, 5 with author captions
- Returns: 6 calcs, 3 row-level, 3 aggregate, 0 LOD, 2 with author captions

Top 3 most-referenced calcs (used-by count):
1. Profit Ratio: used by 4 other calcs, on 7 sheets
2. Regional Sales YoY: used by 3, on 5 sheets
3. Discount Impact: used by 2, on 3 sheets

Save the full dictionary to Downloads? (.md default, .txt option, or skip)
```

**Example 2: Cyclic dependency detected.**

Skill detects Calc A references Calc B, Calc B references Calc C, Calc C references Calc A. Tier A adds banner:

```
**Cycle detected (CD-CYCLE-01):** Profit Ratio → Discount Impact → Profit Ratio. Chain is not renderable as a valid dependency graph; see full report for details.
```

Marks all three calcs `in_cycle: true` in Tier B.

**Example 3: Refuse to explain.**

User: explain what Profit Ratio does in plain English

Skill: Natural-language explanation of a specific calc is `calc-explainer`s scope. Ive emitted the `calc_documentation/1` handoff with the Profit Ratio entry (formula, refs, usage, aggregation context). Want me to route the request to calc-explainer with the doc payload?

## Relationship to Other Skills

- **Peer to calc-inventory.** Inventory discovers what calcs exist; this skill documents what each one is.
- **Peer to calc-linter.** Linter audits naming and commenting hygiene; this skill emits doc content on top of what exists.
- **Upstream of calc-explainer.** Explainer consumes the reference graph to place a specific calc in context.
- **Upstream of publish-readiness.** Publish-readiness uses author-caption presence as a documentation-completeness signal.

## MCP Skill Mapping

Desktop-native. No MCP dependency. Uses standard Desktop tools (`get-workbook-inventory`, `list-workbook-datasources`, `list-available-fields`, `resolve-field`, `get-worksheet-xml`, `get-dashboard-xml`).

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
