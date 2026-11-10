# Handoff Schema for `calc_explanation/1` (Locked)

Every successful `calc-explainer` invocation emits this schema. Downstream skills (`calc-debugger`, `calc-optimizer`, `workbook-auditor`) may consume it. Schema is versioned; unknown versions refused by downstream per HC#8.

## Full Schema

```yaml
schema_version: calc_explanation/1
workbook_name: {name}
calc_name: {name}
datasource_name: {name}
signal_source: {handoff | local_extract}
handoff_reference: {calc_documentation/1_id_or_null}
formula: {verbatim_string}
author_caption: {verbatim_or_null}
aggregation_type: {row-level | aggregate | LOD-fixed | LOD-include | LOD-exclude | table-calc | unclassified | conflict}
pattern_matched: {pattern_name_from_explanation_patterns_md | none}
dimensions:
  what_it_computes: {prose_string_3_to_5_sentences}
  why_structured_this_way: {prose_string_3_to_5_sentences}
  how_it_fits: {prose_string_3_to_5_sentences}
  what_to_expect_at_runtime: {prose_string_3_to_5_sentences}
reference_graph:
  parents: [{list_of_field_or_calc_names}]
  children: [{list_of_calc_names_using_this}]
  cross_datasource_references: [{list_or_empty}]
  unresolved: [{list_or_empty}]
routing_offered:
  calc_debugger: {true | false}
  calc_optimizer: {true | false}
  calc_linter: {true | false}
  reason: {short_string_or_null}
delivery:
  tier_a_rendered: {true | false}
  file_saved: {true | false}
  file_path: {absolute_path_or_null}
  file_format: {md | txt | null}
formula_hash_current: {sha256_or_null}
formula_hash_handoff: {sha256_or_null}
staleness_detected: {true | false | not_applicable}
run_metadata:
  timestamp: {ISO-8601}
  handoff_consumed: {true | false}
  fallback_reason: {handoff_missing | handoff_target_absent | handoff_stale_formula | not_applicable}
  tool_failures: [{list_or_empty}]
  notes: {optional_free_text}
```

## Field-by-Field

- **schema_version.** Always exactly `calc_explanation/1`.
- **calc_name / datasource_name.** Target calc identity. Disambiguated if the workbook has same-named calcs across datasources per HC#13.
- **signal_source.** `handoff` if calc_documentation/1 was in session context AND referenced this calc; `local_extract` otherwise. Per HC#12.
- **handoff_reference.** ID of the calc_documentation/1 report consumed, or null if signal_source is local_extract.
- **formula.** Verbatim from workbook XML. Same source as calc-documenter.
- **author_caption.** Preserved verbatim per HC#11. Null if not present.
- **aggregation_type.** One of six types from calc-documenter's classification. If cited from handoff, reused verbatim. If re-derived locally, matches the same six-type set per `explanation_patterns.md` precedence rules.
- **pattern_matched.** Name of the pattern from `explanation_patterns.md` that fired for Dimension 2. `none` if no pattern matched (renders as "non-canonical structure" in prose per HC#4).
- **dimensions.** Four fixed keys with 3-5 sentences each. Empty-state prose for absent references per HC#7.
- **reference_graph.** Parents (uses), children (used by), cross-datasource references, unresolved references. Same shape as calc-documenter's per-calc entry but only for the target calc.
- **routing_offered.** Downstream routing offered post-delivery based on user question or explanation content:
  - `calc_debugger: true` if user asked about NULLs or the explanation surfaces a NULL-handling pattern.
  - `calc_optimizer: true` if user asked about performance or the explanation surfaces an optimize-candidate pattern (e.g., string-boolean-in-two-branches).
  - `calc_linter: true` if the calc has no author caption and no distinctive pattern (candidate for hygiene review).
- **delivery.** Chat rendered by default. File save is opt-in and rare for calc-explainer.
- **formula_hash_current.** SHA-256 of the target calc's current formula (whitespace-normalized) as read from `list-available-fields`. Populated on every run.
- **formula_hash_handoff.** SHA-256 of the same calc's formula as stored in the consumed `calc_documentation/1` handoff. Populated only when `signal_source: "handoff"`; `null` otherwise.
- **staleness_detected.** True when hashes mismatch AND handoff was attempted. False when hashes match. `not_applicable` when no handoff was attempted (local_extract from the start).
- **run_metadata.fallback_reason.** When `signal_source: "local_extract"`, records why: `handoff_missing` (no handoff in session context), `handoff_target_absent` (handoff exists but doesn't reference target calc), `handoff_stale_formula` (hashes mismatched per V5). `not_applicable` when handoff was consumed successfully.
- **run_metadata.notes.** Free-text log of any staleness detection or drift observations. Cited by downstream consumers if `staleness_detected: true`.
- **run_metadata.** Operational context.

## Downstream Consumer Expectations

- **`calc-debugger`.** Consumes when `routing_offered.calc_debugger: true`. Uses `formula`, `reference_graph.parents`, and `reference_graph.unresolved` to trace NULL propagation.
- **`calc-optimizer`.** Consumes when `routing_offered.calc_optimizer: true`. Uses `pattern_matched` to propose a specific optimize path (e.g., string-boolean-in-two-branches → Boolean rewrite).
- **`workbook-auditor`.** Consumes explanation deltas across runs (calc formula changed, pattern shifted, aggregation type changed).

## Verdict Contracts

**"Handoff-consumed explanation":**

- `signal_source: "handoff"`.
- `handoff_reference` populated with the source report's identifier.
- `aggregation_type` reused verbatim from handoff.
- `reference_graph` reused from handoff.

**"Local-extract explanation":**

- `signal_source: "local_extract"`.
- `handoff_reference: null`.
- `aggregation_type` re-derived locally via `explanation_patterns.md` precedence rules.
- `reference_graph` re-derived by scanning other calcs in the same datasource.

**"Unresolved-reference explanation":**

- `reference_graph.unresolved` list has at least one entry.
- Dimension 3 prose notes the resolution failure per HC#9.
- Skill does not fabricate the missing reference.

**"Ambiguous-name explanation":**

- Skill asked one clarifying question per HC#13 before proceeding.
- Handoff includes the datasource that was resolved.

**"Stale-handoff explanation" (V5 fallback):**

- `signal_source: "local_extract"` (forced by V5).
- `staleness_detected: true`.
- `formula_hash_current` and `formula_hash_handoff` both populated and unequal.
- `run_metadata.fallback_reason: "handoff_stale_formula"`.
- `run_metadata.notes` explains the mismatch (e.g., "formula changed since handoff was generated").
- Explanation is re-derived locally; never renders against the stale handoff.

## Refuse to Guess

If any required field cannot be populated, refuse delivery per HC#8. Never fake a pattern match. Never fabricate a reference. Never bypass HC#11 (author caption verbatim).
