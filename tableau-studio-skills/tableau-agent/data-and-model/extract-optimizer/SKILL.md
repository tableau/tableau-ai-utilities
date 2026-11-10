---
name: extract-optimizer
description: "Use when the user says 'Why is my extract so slow?', 'why is my extract so big?', 'optimize this extract', 'set up incremental refresh'. Reviews extract settings (incremental key, aggregation, hidden fields, extract filters) and recommends changes with expected impact. Advisory only."
---

# Extract Optimizer

## When to use (full trigger detail)

Advise on Tableau extract configuration for refresh speed and storage efficiency. Audits four locked dimensions (D1 Incremental Refresh Key, D2 Aggregation, D3 Hidden-Field Pruning, D4 Filter-at-Extract) with quantified impact per recommendation. Advisory-only. Refuses live-connection sources with a create an extract first message. Triggers on optimize this extract, extract settings, extract configuration audit, why is my extract so slow, why is my extract so big, incremental refresh setup, should I aggregate, extract tuning. Do NOT trigger for connection setup (use data-source-connector), Server/Cloud publishing (out of scope), calc perf (use calc-optimizer), dashboard-render perf (use worksheet-builder), or cross-workbook hygiene (use publish-readiness).

## Purpose

Advise on Tableau extract configuration for refresh speed and storage efficiency. Extracts are configured once at setup and rarely revisited, so misconfigurations accumulate silently as extracts grow. Audits four dimensions, quantifies impact, and produces Desktop UI instructions for every recommendation.

## Trigger Conditions

optimize this extract, extract settings, extract configuration audit, why is my extract so slow to refresh, why is my extract so big, incremental refresh setup, should I aggregate this extract, extract tuning, help me tune my extract.

Do NOT trigger on: connection setup (`data-source-connector`); publishing to Server/Cloud (out of scope); data-quality issues (`data-quality-review`); pre-publish hygiene (`publish-readiness`); calc-level perf (`calc-optimizer`); dashboard-render perf (`worksheet-builder`).

## Scope Boundaries

- IN: four-dimension audit of every extract in the workbook (D1 Incremental Refresh Key, D2 Aggregation, D3 Hidden-Field Pruning, D4 Filter-at-Extract). Quantified impact (rows removed, fields pruned, filter-scope narrowing). Severity-tiered findings.
- OUT: connection or auth setup (`data-source-connector`); Server/Cloud extract publishing (out of scope); Performance Recorder analysis (Desktop-only, no MCP tool); calc-level perf (`calc-optimizer`); dashboard-render perf (`worksheet-builder`); cross-workbook hygiene (`publish-readiness`); mutating extract settings (Desktop UI only).

### Edge-Case Boundaries

| Edge Case | Handling |
|---|---|
| Live connection (no extract) | HC#4 refusal. Create an extract first, then re-invoke. |
| Cross-DS extract behavior | Refuse. |
| Federated sources (multi-source extracts) | Refuse. |
| Extract file corruption (post-refresh) | Refuse: extract file appears corrupted; re-refresh from Data → Extract → Refresh. |
| Refresh currently in progress | Wait or refuse: extract refresh in progress; re-invoke after refresh completes. |
| Connector-specific push-down (Snowflake, BigQuery) | Report standard four-dimension audit. |
| Sample size below 1,000 rows per extract | Report findings; flag quantified impacts as unverified: sample size below reliable threshold. |

## Hard Constraints

- HC#1: Advisory-only. Zero mutating tool calls. Every fix is a Desktop UI instruction.
- HC#2: Four dimensions locked (D1-D4) in `skill-expertise/extract_dimensions.md`. Never invent a fifth.
- HC#3: Quantified impact required for every recommendation. Should improve performance hedging is banned.
- HC#4: Live-connection refusal. If the target has no extract, refuse with create an extract first, then re-invoke.
- HC#5: Batched inventory calls. Phase 1 batches all inventory tools; never re-call mid-workflow.
- HC#6: Refuse out-of-scope questions by exact slug.
- HC#7: Validation Gate before delivery. Every recommendation must pass V1 (D-ID cited), V2 (severity matches rubric), V3 (quantified impact present).
- HC#8: Disagreement branch is scoped. Offer at most one alternate recommendation. Never chain a second alternate; route to Tableau docs.
- HC#9: Dimension precedence when multiple D-dimensions fire on same extract: D3 > D4 > D2 > D1. Higher precedence wins; lower still reports but flagged as secondary. Ties resolved by higher percent-reduction wins, then by D-precedence.

## Tools Used

- `list-workbook-datasources` — Phase 1 (batched inventory).
- `list-worksheets` — Phase 1 (sheet enumeration for field-placement + filter cross-reference).
- `list-dashboards` — Phase 1 (batched with worksheets).
- `list-available-fields` (verbosity: full) — Phase 1 (field inventory, calc detection).
- `get-summary-data` — Phase 3, 4, 5 (row-count + aggregation + filter-impact sampling).

Zero mutating tool calls. Zero file writes.

### Phase 1 Batching Order

Batch call sequence in this exact order (never mid-workflow re-call):

1. `list-workbook-datasources` (identifies extracts vs. live).
2. `list-worksheets` + `list-dashboards` (sheet inventory).
3. `list-available-fields` (verbosity: full) per data source.

Sampling calls (`get-summary-data`) happen in Phase 3-5, one per dimension needing sample data, batched per field where possible.

## Sample-Size Reliability Threshold

Impact estimates are reliable when the sample includes at least **1,000 rows**. Below that threshold:

- Report findings using the locked severity rubric.
- Flag the quantified impact as **unverified: sample size below reliable threshold (1,000 rows).**
- Severity does not downgrade.

## Workflow Phases

1. **Phase 0 Intake.** Confirm target data source via `list-workbook-datasources`. If live connection, execute HC#4 refusal.
2. **Phase 1 Inventory.** Batch-call per Phase 1 Batching Order above. Never re-call mid-workflow.
3. **Phase 2 D1 Incremental Refresh Key.** Identify candidate keys (monotonically increasing datetime or bigint) via field scan and MIN/MAX sampling. Current refresh-mode configuration isnt tool-confirmable; report the candidate and direct the user to verify current mode in Desktop before applying. Flag Warning if a strong candidate exists.
4. **Phase 3 D2 Aggregation.** If row-level extract with every sheet aggregating on the same few dimensions, recommend aggregation-on-extract with correct grain.
5. **Phase 4 D3 Hidden-Field Pruning.** Cross-reference every field vs. sheet placement. Fields never placed anywhere become pruning candidates. Estimate file-size reduction.
6. **Phase 5 D4 Filter-at-Extract.** Filters used on every sheet with the same value or range become filter-at-extract candidates. Report row-reduction estimate.
7. **Phase 5.5 Precedence Resolution.** When multiple D-dimensions fire on same extract, apply HC#9 precedence (D3 > D4 > D2 > D1). Higher precedence rendered primary; lower rendered secondary with precedence note. On tied percent-reduction, D-precedence breaks the tie.
8. **Phase 5.7 Validation Gate.** Before delivery, confirm all three:
   - **V1 D-ID citation.** Every finding cites a dimension ID (D1-D4). No unlabeled findings.
   - **V2 Severity match.** Every severity matches `impact_rubric.md`. No off-rubric severity.
   - **V3 Quantified impact.** Every recommendation cites a specific row/field/size number. No hedged language.
   Failing any gate blocks delivery. Drop the finding or report the gate failure honestly.
9. **Phase 5.8 Disagreement Branch (conditional).** If user disputes a recommendation:
   - Offer one alternate (typically the next-highest-precedence dimensions fix).
   - If rejected, route to Tableaus extract configuration docs. Never a second alternate.
10. **Phase 6 Report Assembly.** Grouped by dimension, severity-ranked (Critical first). Each finding: D-ID, evidence, quantified impact, Desktop UI fix path, precedence note if secondary.
11. **Phase 7 Handoff.** Calc perf → `calc-optimizer`. Dashboard perf → `worksheet-builder`. Full pre-ship → `publish-readiness`. Emit `extract_audit_handoff/1` YAML if downstream skill requested.

## Output Template

Every delivery follows `skill-expertise/output_template.md` (locked). Sections in fixed order: Summary, Findings by Dimension, Handoff. Validation Gate failures block template rendering per templates fallback handling.

## Downstream Handoff Contract

Downstream skills may request `extract_audit_handoff/1`:

- `datasource_name` — the audited data source.
- `extracts` — array (one entry per extract found); each has `extract_name`, `findings` (D1-D4 with severity, quantified_impact_string, verified), `dimension_precedence_applied` (bool).
- `summary_counts` — `critical`, `warning`, `note`, `info` integer counts.
- `verified` — true if all findings sample sizes ≥ 1000, false otherwise.
- `notes` — optional free text.

Downstream skills refuse unknown schema versions.

## Error Handling

| Situation | Response |
|---|---|
| Live connection, no extract | HC#4 refusal. Ask user to create extract first. |
| No extracts in workbook | Report cleanly: no extracts to audit. |
| Sampling returns zero rows | Report extract appears empty or disconnected. |
| Sampling partial (some fields returned, others failed) | Proceed with returned fields. Flag failed dimensions as sampling failed: not audited. |
| Multi-extract mid-audit failure | Complete audit on extracts that succeeded. Report failed extract separately. |
| Extract file corruption | Refuse: extract file appears corrupted; re-refresh from Data → Extract → Refresh. |
| Refresh in progress | Refuse: extract refresh in progress; re-invoke after refresh completes. |
| Cross-DS or federated extracts | Refuse per Edge-Case Boundary. |
| Symptom outside D1-D4 | Say the symptom is outside this audit's four dimensions (D1-D4) and suggest Desktop's Performance Recorder (Help > Settings and Performance > Start Performance Recording) to find the cause. |
| User asks to modify extract settings | Refuse: Desktop UI action. Provide dialog paths. |
| Validation Gate fails V1 | Drop the unlabeled finding. |
| Validation Gate fails V2 | Recompute severity from rubric. |
| Validation Gate fails V3 | Do NOT deliver a hedged recommendation. List the dimension under 'Not quantified: sampling insufficient' with the extract name, so the user knows it wasn't checked. Never count it as clean. |

## Common Mistakes to Avoid

- Hedging impact (should improve performance). Quantify or drop the finding.
- Running Performance Recorder-style analysis. Not available; stick to config audit.
- Drifting into calc, dashboard, or cross-workbook perf. Refuse and route.
- Overwriting a batched inventory. Batch once in Phase 1.
- Skipping the Validation Gate. Every finding must pass V1, V2, V3.
- Chaining alternates past the first. HC#8 caps at one.

## Known Limitations

- **Cannot run Performance Recorder.** Impact estimates from inventory, not measured latency.
- **Cannot see refresh-log history.** Cant diagnose historical events.
- **Row-reduction estimates for D4 depend on current filter values.** Actual reduction may vary as data grows.
- **Sample size below 1,000 rows flags impacts as unverified.**

## MCP Skill Mapping

No direct MCP equivalent. Desktop-agent-native extract-configuration skill.

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
