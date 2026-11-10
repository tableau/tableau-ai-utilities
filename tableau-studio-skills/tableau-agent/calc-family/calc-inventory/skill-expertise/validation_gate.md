# Validation Gate (Read-Only, 3 Checks)

Every inventory passes all 3 checks before delivery. Any failure blocks delivery per HC#8. Fail-open is NOT applied — the skill is read-only, so a V-gate failure means the inventory itself is incomplete or inconsistent, not a mutation risk. Refuse delivery and diagnose.

Different from calc-writer/debugger/optimizer/linter's 8-check gate because calc-inventory doesn't author anything. The 3-check gate is scoped to what a read-only cataloging skill can and must verify.

## V1 — Entry Completeness

**Check:** every entry in the inventory has all required schema fields populated (or sentinel values per HC#8).

Required fields per `skill-expertise/catalog_schema.md`:
- `calc_name`, `calc_type`, `formula`, `return_type`, `is_aggregated_flag`, `derivation_prefix`
- `references.fields`, `references.parameters`, `references.sets`, `references.hierarchies`, `references.nested_calcs`, `references.external_references`
- `style_violations` (list; may be empty), `perf_advisory_flags` (list; may be empty)
- `complexity.line_count`, `complexity.branch_depth`, `complexity.nested_lod_depth`
- `usage.shelf_placements`, `usage.dashboards`, `usage.flag`

**Sentinel values acceptable:** `null` for optional strings, `[]` for empty lists, `"unavailable_this_run"` for usage fields when `get-workbook-inventory` (dashboards) or `search-workbook-fields` (shelf placements) failed, `"unknown"` for `return_type` when not derivable.

**Sentinel values NOT acceptable:** blank strings, missing keys, `undefined`.

**Fail action:** identify which entries failed and re-derive missing fields. If a field cannot be derived (e.g., broken calc formula), populate the appropriate sentinel and record the reason in that entry's `notes`. Re-run V1. If a second run still fails, refuse delivery and route to user for diagnosis.

## V2 — Batch Reconciliation

**Check:** batched pagination results reconciled into a single inventory with zero duplicates and zero omissions.

Verification steps:
1. Total count in the final inventory must equal `list-available-fields`'s reported total calc count.
2. `calc_name` uniqueness: every name appears exactly once in the final inventory.
3. Reference graph rebuilt across all batches (nested-calc references may span batches).

**Fail action:** identify the reconciliation error (duplicate, omission, or count mismatch). If a duplicate, drop the older-batch entry (batches processed in order; later batches supersede earlier only when the calc's data is materially different, which shouldn't happen for a read-only inventory but is possible if the DS was modified mid-run). If an omission or count mismatch, re-run the affected batch(es). Refuse delivery if reconciliation still fails after one retry.

## V3 — Reference-Graph Consistency

**Check:** every nested-calc reference in the inventory resolves to another entry in the inventory OR is flagged as `external_reference: true` with rationale.

Verification steps:
1. For every entry, iterate `references.nested_calcs`. Each name MUST match another entry's `calc_name` in the inventory.
2. If a name does not match, move it from `references.nested_calcs` to `references.external_references` with a `notes` block explaining why (e.g., "references a calc from a different DS", "references a deleted or renamed calc").
3. Cycle detection: depth-first traversal from every root calc (a calc with no downstream references). Termination on revisiting an already-marked node. Cycles are reported in top-level `cycle_report`, NOT silently included in `nested_calcs`.

**Fail action:** V3 does NOT block delivery — unresolved references are moved to `external_references` with rationale. Cycles are reported, not resolved. V3 failure only blocks delivery if the reconciliation itself is broken (e.g., a name resolves to two different entries, which V2 should have caught first).

## Gate Execution Order

1. V1 (entry completeness) first — cheapest to run, catches most failures.
2. V2 (batch reconciliation) next — validates the inventory shape.
3. V3 (reference-graph consistency) last — depends on V1 + V2 passing to have complete data.

## What V-Gate Does NOT Check

Unlike calc-writer/debugger/optimizer/linter's 8-check gate, this gate does NOT check:

- Calc-type classification correctness at the semantics level (we trust `list-available-fields` and `resolve-field` output; the other peers' V-gates catch this at author-time).
- Aggregation wrapping validity (R-AGG-01/02) — that's calc-debugger/linter's job.
- LOD syntax/nesting/order-of-operations (R-LOD-01/02/03) — same.
- Table-calc partitioning (R-TC-01/02) — same.
- NULL handling (R-NULL-01) — same.
- Boolean semantics (R-BOOL-01) — same.
- Row-level string ops in aggregations (R-PERF-01) — noted as a `perf_advisory_flag` if present, but not V-gate-blocking.
- Calc naming (R-NAME-01) — noted as a `style_violation` if present, but not V-gate-blocking.
- Runtime equivalence (R-EQUIV-01) — inventory is read-only; no rewrite exists to verify.

Inventory catalogs what exists; it does not judge validity beyond internal consistency. Flag-derivation from style/perf catalogs surfaces judgment as advisory data, not gate blocks.

## Refuse to Fabricate

If V-gate cannot pass after one retry, refuse delivery and diagnose. Never fake a V-gate pass. Never populate fields with plausible-looking guesses to satisfy V1. Never suppress a cycle detection to make V3 pass.
