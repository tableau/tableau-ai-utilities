# Scale Tiers, Multi-Calc Mode, and Data Source Types (Locked)

Moved from SKILL.md on 2026-11-03 to keep the always-loaded skill lean. Read this for very wide (100+ field) or very large data sources, multi-calc runs, and blended, federated, live, or multi-table sources.

calc-writer adapts Phase 1 field-inventory strategy and Phase 4 verification behavior based on data source size. Every scale tier has explicit handling.

## Field-Count Tiers

| Tier | Field Count | Phase 1 Strategy |
|---|---|---|
| Narrow | <10 fields | Single `list-available-fields` call. Skip batching. Full inventory in one call. |
| Typical | 10-50 fields | Single `list-available-fields` call. No batching required. |
| Wide | 50-100 fields | Single call still viable; consider batching if response payload approaches token cap. |
| Very Wide | 100-200 fields | Batch in groups of ~10 with inline progress notes. Reuse inventory across chained invocations in-session. |
| Massive | 200+ fields | Batch in groups of ~10. Recommend user narrow scope to a specific logical table before proceeding. If user refuses, batch anyway with a note about likely token pressure. |

## Row-Count Tiers (Verification Confidence)

| Tier | Row Count | Verification Behavior |
|---|---|---|
| Tiny | <100 rows | Verification runs; mark `verified: true, sample_size: N` but note "very small dataset; verification is directional." |
| Small | 100-999 rows | Verification runs; mark `sample_size: "below_threshold"` per Sample-Size Reliability rule. |
| Standard | 1,000-999,999 rows | Verification runs; mark `verified: true, sample_size: N`. |
| Large | 1M-100M rows | Verification runs on a sample; sample_size is the actual rows returned. Note in handoff that this is a sample, not the full extract. |
| Very Large | 100M+ rows | Verification samples per default; `get-summary-data` may return a truncated result. Note the truncation explicitly in handoff `notes`. |

## Multi-Calc Sequential Mode

Multi-calc mode (HC#1 opt-in) runs the full pipeline per calc, one at a time, in the order the user named them. Explicit runtime characteristics:

- **N calcs = N inventory reuses.** Phase 1 inventory from calc #1 is reused for calcs #2 through #N in the same invocation.
- **N calcs = N V-gate passes.** Every calc runs all 8 checks independently. No shared V-gate.
- **N calcs = N handoff YAMLs, only when HC#7 applies.** One `calc_write_handoff/1` per calc, emitted in order, when a downstream calc skill requested it.
- **Failure isolation.** If calc #3 fails V-gate, calcs #4 through #N still proceed. Failed calcs report the specific V-gate rule failure; downstream peers see the failure count in a session summary at the end.
- **Session summary.** After the last calc, calc-writer emits a summary: "N of M calcs shipped successfully. Failed: [calc-X (R-gate-fail), calc-Y (field-missing)]."

## Data Source Type Branching

| Data Source Type | Handling |
|---|---|
| Extract (.hyper) | Full verification supported. Preferred for verified-tier confidence. |
| Live connection | Verification runs but sample may reflect connection latency; note in handoff. |
| Cross-DS blend | Refuse per Edge-Case Boundary (blended sources use query-time joins; calc semantics differ). |
| Federated multi-source | Refuse per Edge-Case Boundary; route to `calc-translator` if source-dialect port required. |
| Multi-table (relationships) | Confirm which logical table before authoring; document grain in handoff notes.
