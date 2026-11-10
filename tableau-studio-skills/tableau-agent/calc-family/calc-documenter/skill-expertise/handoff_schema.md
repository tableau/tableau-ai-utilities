# Handoff Schema for `calc_documentation/1` (Locked)

Every successful `calc-documenter` invocation emits this schema. Downstream skills (`calc-explainer`, `calc-linter`, `calc-debugger`, `workbook-auditor`, `publish-readiness`) may consume it. Schema is versioned; unknown versions refused by downstream per HC#8.

## Full Schema

```yaml
schema_version: calc_documentation/1
workbook_name: {name}
datasources_count: {N}
total_calcs: {N}
graph_shape: {linear | tree | DAG | cyclic}
cycles:
  - chain: [{calc_a}, {calc_b}, ..., {calc_a}]
    affected_calcs: [{list}]
partial_extract_datasources:
  - datasource_name: {name}
    reason: {short_string}
datasources:
  - datasource_name: {name}
    calc_count: {N}
    calcs:
      - calc_name: {name}
        datasource_qualifier: {name}
        type: {row-level | aggregate | LOD-fixed | LOD-include | LOD-exclude | table-calc | unclassified | conflict}
        formula: {verbatim_string}
        fields_referenced: [{list_of_resolved_names_or_unresolved_sentinels}]
        uses: [{list_of_other_calc_names}]
        used_by: [{list_of_other_calc_names}]
        on_sheets: [{list}]
        on_dashboards: [{list}]
        aggregation_pattern_cited: {short_pattern_string}
        cross_datasource_references: [{list_or_empty}]
        author_caption: {verbatim_or_null}
        author_annotation: {verbatim_or_null}
        in_cycle: {true | false}
top_referenced_calcs:
  - calc_name: {name}
    used_by_count: {N}
    on_sheets_count: {N}
routing:
  calc_explainer: {true | false}
  calc_linter: {true | false}
  calc_debugger: {true | false}
  workbook_auditor: {true | false}
  publish_readiness: {true | false}
  rationale: {short_string}
delivery:
  tier_a_rendered: {true | false}
  tier_b_saved: {true | false}
  tier_b_file_path: {absolute_path_or_null}
  tier_b_format: {md | txt | null}
run_metadata:
  timestamp: {ISO-8601}
  tool_failures: [{list_or_empty}]
notes: {optional_free_text}
```

## Field-by-Field

- **schema_version.** Always `calc_documentation/1`.
- **workbook_name.** Name of the audited workbook.
- **datasources_count / total_calcs.** Aggregate counts.
- **graph_shape.** One of `linear` (calcs form a single chain, no branching), `tree` (each calc has at most one parent), `DAG` (directed acyclic graph, multiple parents allowed), `cyclic` (at least one cycle detected).
- **cycles.** List of every detected cycle with the chain and affected calcs. Empty `[]` if no cycles.
- **partial_extract_datasources.** HC#9 flagged datasources with reason. Empty `[]` when all extracts completed cleanly.
- **datasources[].calcs[].** Every calc with full 5-dimension documentation.
- **datasources[].calcs[].datasource_qualifier.** Datasource name, redundantly included on each calc for downstream consumption without traversal.
- **datasources[].calcs[].fields_referenced.** Resolved via `resolve-field`. Unresolved references render as `"unresolved: <raw_reference>"` per HC#7.
- **datasources[].calcs[].uses / used_by.** Reference graph. Empty `[]` for calcs with no dependencies.
- **datasources[].calcs[].author_caption / author_annotation.** Preserved verbatim per HC#11. `null` if not present.
- **datasources[].calcs[].in_cycle.** True if this calc participates in any detected cycle.
- **top_referenced_calcs.** Convenience field for downstream skills to identify high-value calcs quickly. Sorted by used_by_count descending. Cap at 5 entries.
- **routing.** Downstream skill routing flags based on findings:
  - `calc_explainer: true` when at least one calc has no author_caption (candidate for natural-language explanation).
  - `calc_linter: true` when 30%+ of calcs have no author_caption (documentation hygiene gap).
  - `calc_debugger: true` when any cycle detected (CD-CYCLE-01 fired).
  - `workbook_auditor: true` always (deltas across runs).
  - `publish_readiness: true` when total_calcs >= 10 (documentation completeness matters at scale).
- **delivery.** Tier A / Tier B state.
- **run_metadata.** Operational context.

## Downstream Consumer Expectations

- **`calc-explainer`.** Consumes when `routing.calc_explainer: true`. Uses the reference graph position and formula to produce a natural-language explanation of a specific calc requested by the user.
- **`calc-linter`.** Consumes when `routing.calc_linter: true`. Uses `author_caption` presence and naming conventions to flag hygiene gaps.
- **`calc-debugger`.** Consumes when `routing.calc_debugger: true` (cycle detected). Uses the cycle chain to guide cycle-breaking rewrite.
- **`workbook-auditor`.** Consumes documentation deltas across runs (calc added / removed / formula changed / caption changed).
- **`publish-readiness`.** Consumes when `routing.publish_readiness: true`. Uses caption presence as a documentation-completeness signal.

## Verdict Contracts

**"Fully documented workbook" (all calcs have author captions):**

- Every calc's `author_caption` is a non-null string.
- `routing.calc_linter: false`.
- `routing.calc_explainer: false`.

**"Cyclic calc-family workbook":**

- `graph_shape: "cyclic"`.
- `cycles` list has at least one entry.
- At least one calc has `in_cycle: true`.
- `routing.calc_debugger: true`.

**"Partial-extract run":**

- `partial_extract_datasources` list has at least one entry.
- Corresponding datasource's `calcs[]` reflects only what was successfully extracted.
- Report includes PARTIAL-EXTRACT banner.

## Refuse to Guess

If any required field cannot be populated, refuse delivery per HC#8. Never fake a formula. Never invent a field reference. Never bypass HC#11 (author caption verbatim). Never skip cycle detection.
