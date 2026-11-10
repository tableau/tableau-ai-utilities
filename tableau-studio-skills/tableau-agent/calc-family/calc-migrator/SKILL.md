---
name: calc-migrator
description: "Use when the user says 'Migrate this calc', 'move this calc to another data source', 'port this calc to another data source'. Copies one calculated field to a different data source in the same workbook, remaps its fields, and verifies it. The source calc is never changed."
---

# Calc Migrator

## When to use (full trigger detail)

Migrate one Tableau calculated field from a source datasource to a target datasource within the same open workbook, with formula parse, field-reference resolution against the target schema, aggregation preservation, per-field consent, and sibling-copy write via `author-calc` (target-side, `_migrated` suffix). Same-schema only (source and target must share referenced field names). Requires a fresh `calc_documentation/1` handoff from calc-documenter with formula-hash match. Read-only against the source calc; mutating only on the target datasource under explicit user go-ahead per field-rewrite. Trigger with migrate this calc, move calc to another datasource, calc-migrator, port this calc to another data source. Do NOT trigger on. bulk-calc migration (not supported), cross-workbook migration (out of scope), rewriting calc semantics like aggregate-to-LOD (route to calc-optimizer), authoring new calcs from scratch (route to calc-writer), explaining a calc (route to calc-explainer), diagnosing NULLs (route to calc-debugger), producing a before/after report (route to calc-migrator-diff-report post-migration).

## Purpose

Migrate a single Tableau calculated field from a source datasource to a target datasource inside the same open workbook. Read against the source; sibling-copy write on the target via `author-calc` with a `_migrated` suffix. Original source calc is never touched. Every field-reference rewrite requires user consent; the final composed formula requires an explicit go-ahead before `author-calc` fires. Same-schema only: source and target must share the names of every field the source calc references, or the migration is refused with a routing recommendation.

Consumes calc-documenter's `calc_documentation/1` handoff for the reference graph and aggregation classification; refuses to run without it.

## Trigger Conditions

- migrate this calc
- move {calc name} to {datasource}
- port this calc to {datasource}
- calc-migrator
- copy this calculation to another data source
- same calc but on {target datasource}

## Do NOT Trigger On

- Bulk-calc migration across many calcs → not supported.
- Cross-workbook migration → out of scope; copy the calc manually.
- Rewriting calc semantics (aggregate → LOD, table-calc → LOD-fixed) → route to `calc-optimizer`.
- Authoring a new calc from scratch → route to `calc-writer`.
- Explaining what the source calc does → route to `calc-explainer`.
- Diagnosing why the migrated calc returns NULL → route to `calc-debugger`.
- Producing a before/after diff report → route to `calc-migrator-diff-report` after the migration completes.
- Cross-schema migration (target datasource lacks fields the source references with the same name) → refuse with a clean route to manual authoring.

## Scope Boundaries

- **IN.** One source calc + one target datasource + one migration per run. Same-schema only. Formula parse, field-reference resolution against target DS via `resolve-field`, aggregation reclassification against target DS schema, dependency remapping when the source calc references another calc that also exists on the target. Sibling-copy write via `author-calc` on the target DS with `_migrated` suffix. Per-field consent per rewrite. Final-formula go-ahead before `author-calc` fires. Handoff schema `calc_migration_report/1`.
- **OUT.** Any mutation of the source calc. Any datasource-model mutation on the target (new joins, relationships, field additions). Multi-calc, multi-workbook, multi-migration runs. Cross-schema field-name mapping. Semantic rewrites (aggregation type changes, LOD introduction, table-calc conversion). Bulk consent (per-field consent is HC#2).

**Same-schema rule.** The target datasource must contain every field the source calc references, with the same name. If the source calc references `[Sales]` and `[Category]`, both must resolve on the target via `resolve-field`. If any referenced field is unresolvable, migration is refused with `unresolved_references[]` populated and a manual-authoring route offered.

**Handoff consumption pattern.** Skill requires `calc_documentation/1` in session context with the target calc present in the handoffs calc list. If calc-documenter isn't installed, say so and offer two paths: (a) a read-only local extract of this one calc via `list-available-fields` and `resolve-field`, labeled `signal_source: local_extract`, with every consent step still required; or (b) the manual Desktop path: right-click the source calc > Copy, right-click the target data source > Paste, then fix any red field references. If missing, skill refuses with run calc-documenter first routing. If stale (V5 formula-hash mismatch), skill refuses with re-run calc-documenter routing. No local-extract fallback to protect the mutating write from stale-signal risk.

## Workflow Phases

- **Phase 0 Scope.** Confirm workbook is open via `get-workbook-inventory`. If `get-workbook-inventory` fails, times out, or returns empty for a workbook expected to be open, stop immediately and report the failure rather than proceeding on an unconfirmed workbook state. Ask user for source calc name if not stated. Resolve source calc via `resolve-field`. Ask user for target datasource. Confirm target datasource exists via `list-available-fields`.
- **Phase 0.5 Target Diff (mandatory, read-only, runs before offering any migration).** When the user names both datasources but not a specific calc, or names a calc without having seen the diff, compare the two datasources first. (1) List the calculated fields on the source datasource from `list-available-fields` (name, caption, formula). (2) For each, call `resolve-field` with the target `datasource` and record `missing_on_target` or `present_on_target`. (3) For each `present_on_target`, read the target formula from `list-available-fields` (or the cached workbook XML) and compare it to the source formula after whitespace normalization; record `identical` or `differs`. (4) Report in bullets: missing on target (migration candidates), present and differs (candidates only if the user wants to overwrite-by-sibling, `Migrated` suffix still applies), present and identical (nothing to do). (5) Note that `resolve-field` only looks up names taken from the source, so calcs that exist only on the target are not detected; say so rather than implying completeness. (6) Offer only the candidates from step 4, then continue to Phase 1 for the one calc the user picks. Never offer to migrate a calc that is present and identical. If the target datasource is not returned by `list-available-fields`, state that and use `resolve-field` with the target `datasource` name from `list-workbook-datasources` instead.
- **Phase 1 Handoff Check (mandatory).** Look for `calc_documentation/1` handoff in session context. If missing, refuse and route to calc-documenter. If present, verify the source calcs current formula hash matches the handoffs stored hash per V5. Mismatch = refuse and route to re-run calc-documenter. No local fallback.
- **Phase 2 Same-Schema Verification (numbered checklist).**
  1. Extract the field-reference list from the source calc formula via the handoffs `fields_referenced`. Exclude any field name that appears only as an LOD dimension declaration (between `{FIXED`/`{INCLUDE`/`{EXCLUDE` and `:`); those are deferred to Phase 3s LOD-dimension check and refusal routing, not this generic pass.
  2. Deduplicate the list; batch fields into groups of 20 for `resolve-field` calls per HC batching cap.
  3. For each referenced field, call `resolve-field` against the target datasource.
  4. Record each result in `resolution_log[]` as `resolved | unresolved`.
  5. If any field returns `unresolved`, populate `unresolved_references[]` with the exact field names.
  6. If `unresolved_references[]` is non-empty, abort migration with the missing-field refusal template from `skill-expertise/aggregation_preservation.md`.
  7. If all fields resolve, proceed to Phase 3.
- **Phase 3 Aggregation Preservation Check.** Classify the source calcs aggregation type per the locked decision tree in `skill-expertise/aggregation_preservation.md` (LOD-fixed → LOD-include → LOD-exclude → table-calc → aggregate → row-level). If the source is LOD-fixed, LOD-include, or LOD-exclude and the target DS lacks any of the LOD dimensions, refuse migration and route to calc-optimizer with the missing-LOD-dimension refusal template.
- **Phase 4 Per-Field Consent.** For each field reference in the source formula, present the user with the target-DS-resolved reference and ask for explicit confirmation. Track consent per field in `consent_log[]`. No batching; one field per prompt.
- **Phase 5 Compose Migrated Formula.** Assemble the final formula string using confirmed field references. Preserve author caption verbatim per HC#11. Assemble the target calc name as `{source_name} Migrated` (with a space, following Tableau naming conventions).
- **Phase 6 Final Go-Ahead.** Present the composed formula to the user with the proposed target calc name. Wait for explicit go-ahead. No implicit assent; user must state yes or equivalent to advance.
- **Phase 7 Sibling-Copy Write.** Invoke `author-calc` on the target datasource with the composed formula and `_migrated` naming. Verify write via read-back per calc-writers discipline. If `author-calc` fails or times out (non-deterministic hang), fall back to Desktop-manual instructions with the composed formula for the user to paste manually.
- **Phase 8 Validate.** Run the 5-check V-gate: schema coverage, handoff-hash match, per-field consent complete, final go-ahead recorded, sibling-copy discipline held (source untouched, target has new calc with `_migrated` suffix).
- **Phase 9 Deliver.** Compact single-tier chat output confirming migration status. Optional handoff to calc-migrator-diff-report for a before/after diff artifact.

## Hard Constraints

**HC#1 Source calc is read-only always.** Never invoke `author-calc`, `bind-template`, or any mutating tool against the source datasource. Source formula, source caption, source annotations, source references all remain byte-identical after the run.

**HC#2 Per-field consent required.** Every field-reference rewrite requires explicit user confirmation. No batching under one yes. User can approve fields one at a time or decline. Declined fields abort the migration with `unresolved_references[]` populated.

**HC#3 Final-formula go-ahead required.** The composed formula is presented in full before `author-calc` fires. No implicit assent. User states yes or equivalent to advance. Any other response aborts.

**HC#4 Refuse to fabricate.** No inferred field mappings. No guessed aggregation reclassification. No invented dependency remapping. If any resolution fails, abort with a manual-authoring route rather than proceed.

**HC#5 Handoff required upstream.** Migration cannot start without a fresh `calc_documentation/1` handoff (V5 formula-hash match). No local-extract fallback. This is stricter than calc-explainers opportunistic pattern because the write mutates state; stale signals are unacceptable.

**HC#6 Same-schema only.** If the target DS lacks any field the source calc references (by name), refuse with `unresolved_references[]` and route to manual authoring.

**HC#7 Aggregation preservation.** If the source calcs aggregation type cannot be preserved on the target (e.g., LOD-fixed dimensions missing), refuse with rationale and route to calc-optimizer for a semantic rewrite. Skill does not silently change aggregation type.

**HC#8 One calc, one target, one migration per run.** Multi-calc, multi-target, or multi-migration requests refused; not supported.

**HC#9 One workbook per run.** Cross-workbook migration refused; out of scope.

**HC#10 Sibling-copy discipline.** Target calc is always named `{source_name} Migrated` (with space per Tableau naming). Never overwrite an existing calc on the target DS. If a calc with that name already exists, append version suffix (`Migrated v2`, `Migrated v3`) per fresh-filename discipline.

**HC#11 Author caption preserved verbatim.** Source calcs caption (if present) is copied byte-identical to the target calc. Sources in-formula `//` annotations are copied byte-identical. Skill never rewrites, paraphrases, or removes author intent.

**HC#12 `author-calc` timeout fallback.** If `author-calc` hangs (documented non-deterministic hang) or fails, skill emits the composed formula in chat plus Desktop-manual paste instructions. Migration status marked `pending_manual_apply` rather than `applied`. Once the user reports the manual paste is done, skill re-reads the target calc via `list-available-fields` or `resolve-field` and confirms the formula matches the composed formula byte-for-byte before upgrading status to `applied` — a users done is not itself sufficient confirmation for a mutating write.

**HC#13 Never batch consent.** Even if the user says approve all field mappings, skill still presents each field individually. Per-field discipline is non-negotiable for a mutating skill.

**HC#14 Read-back verification.** After `author-calc` succeeds, skill reads the newly-created target calc and verifies the formula matches the composed formula byte-for-byte. Mismatch = migration marked failed, target calc flagged for user review.

**HC#15 Sentinel discipline.** Missing data uses `null`, `[]`, `unresolved: <raw>`, or `unknown`. Never fabricate to fill a schema field.

**HC#16 Wide-formula scale handling.** For source calcs referencing more than 15 unique fields, skill emits a wide-formula-notice in Phase 2 output (this calc references N fields; per-field consent will require N confirmations) and offers an opt-in bulk-review path: user reviews the full field-mapping table once, then confirms with a single confirm all mappings acknowledgment. Bulk-review still requires the user to have read the full mapping table (skill emits the table before requesting bulk confirmation). Bulk-review does NOT change HC#3 final-formula go-ahead requirements; that remains a separate explicit confirmation.

## Validation Gate (5-Check)

- **V1 Schema Coverage.** Every field the source calc references resolves on the target DS via `resolve-field`. `unresolved_references[]` empty.
- **V2 Handoff-Hash Match.** Source calcs current formula hash matches the handoffs stored hash. Staleness detected = abort.
- **V3 Per-Field Consent Complete.** `consent_log[]` shows explicit user approval for every field reference.
- **V4 Final Go-Ahead Recorded.** `final_goahead_timestamp` populated. No implicit or empty.
- **V5 Sibling-Copy Discipline.** Source calc byte-identical to pre-run state (verified by re-reading source formula). Target calc created with `_migrated` suffix. Read-back verified.

## Common Mistakes (Anti-Patterns)

- **Batching per-field consent under one yes.** Even if the user says approve all field mappings, skill iterates each field individually per HC#2 / HC#13. Bulk-review path per HC#16 is a separate opt-in mode for wide formulas and still requires the mapping table to be shown before the bulk acknowledgment.
- **Running without a fresh calc-documenter handoff.** HC#5 refuses this. No local-extract fallback. Mutating writes cannot survive stale reference-graph signals.
- **Silent aggregation swap.** Never reclassify a source LOD-fixed as an aggregate on the target because the outer SUM was seen first. Precedence Rule 1 in `skill-expertise/aggregation_preservation.md` blocks this.
- **Mutating the source calc.** HC#1 makes the source calc byte-identical before and after the run. Never touch it.
- **Skipping the final-formula go-ahead.** HC#3 requires explicit user yes on the composed formula. No implicit assent from any prior consent.
- **Overwriting an existing target calc.** HC#10 fresh-filename discipline appends `Migrated v2`, `Migrated v3` on collision. Never overwrite.
- **Fabricating field mappings.** If any field on the source calc fails to resolve on the target datasource, refuse the migration per HC#4. Do not guess a similar-named field.
- **Ignoring `author-calc` timeout.** HC#12 fallback lands to Desktop-manual paste with `pending_manual_apply` status. Never silently mark a hung migration as successful.

## Handoff Schema

Emits `calc_migration_report/1`:

```yaml
calc_migration_report:
  version: 1
  run_timestamp: <ISO 8601>
  source:
    calc_name: <string>
    datasource: <string>
    formula: <verbatim>
    formula_hash: <sha256>
    aggregation_type: <enum>
    caption: <string|null>
    annotations: <string|null>
  target:
    datasource: <string>
    calc_name: <string, e.g. Profit Ratio Migrated>
    formula: <verbatim composed>
    aggregation_type: <enum, preserved>
    caption: <string|null, byte-identical to source>
    annotations: <string|null, byte-identical to source>
  consent_log:
    - field: <string>
      resolved_on_target: <boolean>
      approved: <boolean>
      timestamp: <ISO 8601>
  unresolved_references: []
  final_goahead:
    given: <boolean>
    timestamp: <ISO 8601>
  status: <applied | pending_manual_apply | refused | failed>
  read_back_verified: <boolean>
  routing_offered:
    calc_migrator_diff_report: <boolean>
    calc_debugger: <boolean>
    calc_optimizer: <boolean>
  v_gate:
    v1_schema_coverage: <pass|fail>
    v2_handoff_hash_match: <pass|fail>
    v3_per_field_consent: <pass|fail>
    v4_final_goahead: <pass|fail>
    v5_sibling_copy_discipline: <pass|fail>
```

Downstream consumers:

- **calc-migrator-diff-report**. Consumes to produce before/after diff artifact.
- **workbook-auditor.** Tracks migration deltas across runs.
- **publish-readiness.** Verifies migrated calc is documented and referenced before publish.

## Single-Tier Delivery

Chat-only output. No opt-in file save (calc-migrator-diff-report handles the file artifact separately).

Template:

```
**Calc Migration: {source_name} → {target_datasource}**
Status: {status}
Source hash match: {v2 pass/fail}
Fields resolved on target: {N of N}
Per-field consent: {N of N approved}
Final go-ahead: {timestamp}

Migrated calc: **{target_name}** on {target_datasource}
Formula: {composed_formula}

Read-back verified: {yes/no}

Adjacent skill routing:
- Want a diff report? → calc-migrator-diff-report
- Runtime NULL diagnosis? → calc-debugger
- Semantic rewrite considered? → calc-optimizer
```

## Adjacent-Skill Routing

- **Upstream mandatory:** calc-documenter (must produce `calc_documentation/1` handoff first).
- **Downstream opt-in:** calc-migrator-diff-report (before/after artifact), calc-debugger (NULL diagnosis on migrated calc), calc-optimizer (semantic rewrite if aggregation preservation fails), workbook-auditor (change tracking), publish-readiness (post-migration sweep).
- **Refusal routes:** cross-schema migration → manual authoring in Desktop; multi-calc migration → not supported; cross-workbook migration → out of scope.

## Known Limitations

- **Same-schema only.** Cross-schema (target lacks sources field names) refused.
- **`author-calc` reliability gap**. Non-deterministic hangs; HC#12 fallback lands to Desktop-manual paste when the hang fires.
- **`resolve-field` case-sensitive** (platform gap). Field names must match exactly.
- **Cross-datasource field references** in the source calc are named but not resolved on the target if the sources cross-DS target isnt loaded. Skill refuses in that case per HC#4.
- **No aggregation semantic changes.** LOD-fixed source that cant preserve dimensions on target = refusal, not silent rewrite.
- **Cycle detection unbuildable via native authoring** (platform limitation). If the target DS already has a calc that references the migrated calcs name (rare, only via a pre-existing naming collision), fresh-filename discipline in HC#10 handles the collision, not cycle detection.
- **Parameter references in source calc.** If the source references a parameter, the target must have the same parameter by name. Fresh-parameter-resolution failure applies here; skill flags rather than fabricates.
- **`author-calc` cannot resolve a freshly-created parameter** (confirmed 2026-08-31). If migration composes a formula that references a parameter created earlier in the same session, author-calc may fail; HC#12 fallback lands to manual paste.
- **`author-calc` session-stale write failures independent of read path** (confirmed 2026-09-17 during calc-migrator-diff-report behavioral testing). Observed repeatedly: `author-calc` fails with a stale-Desktop-session error while `resolve-field` succeeds against the same session moments before and after. This is a write-path-specific reliability gap, not a general connectivity loss — do not assume the whole session is down just because a write fails; re-verify with a read call before concluding disconnection, and land on the HC#12 manual-paste fallback rather than repeatedly retrying the write.

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
