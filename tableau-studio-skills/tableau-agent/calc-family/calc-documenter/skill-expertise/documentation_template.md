# Documentation Template (Locked, Chat + File)

Every `calc-documenter` delivery follows this shape. Compact Tier A chat + opt-in Tier B file. Never deviate from the section order; never rename headers.

## Tier A: Compact Chat Summary

```markdown
**Calc Documentation: {workbook_name}**
Datasources: {N} · Total calcs: {N} · Graph shape: {linear | tree | DAG | cyclic}
{Cycle banner if CD-CYCLE-01 fired, one line, e.g.: "Cycle detected (CD-CYCLE-01): {A} → {B} → {A}. See full report."}
{PARTIAL-EXTRACT banner if HC#9 fired, one line, e.g.: "Datasource {DS} returned partial calc list; documented calcs shown."}

Per-datasource TL;DR:
- {DS-A}: {N} calcs, {N} row-level, {N} aggregate, {N} LOD, {N} with author captions
- {DS-B}: same shape

Top 3 most-referenced calcs (used-by count):
1. {calc_name}: used by {N} other calcs, on {M} sheets
2. {calc_name}: used by {N}, on {M}
3. {calc_name}: used by {N}, on {M}

Save the full dictionary to Downloads? (.md default, .txt option, or skip)
```

**Compact summary rules.**

- Target under 25 lines total.
- Datasources line always shown.
- Cycle banner and PARTIAL-EXTRACT banner render only if fired; one line each.
- Per-datasource TL;DR renders in `list-workbook-datasources` enumeration order per HC#15.
- Top 3 selection locked: sort by used-by count descending, then by sheet count descending, then by calc name ascending; take the first 3. Ties never depend on judgment.
- Save-file offer is the last line.

**Never in Tier A.**

- Per-calc formula.
- Full field-reference list.
- Full reference graph.
- Author captions (preserved in Tier B).
- Handoff schema payload.

## Tier B: Full Dictionary File

Path: `{Downloads}/{workbook_name}_calc-documentation.md` (or `.txt`). Fresh-filename discipline: increment `_v2`, `_v3` on collision.

```markdown
# Calc Documentation: {workbook_name}

**Report generated:** {ISO-8601 timestamp}
**Workbook:** {workbook_name}
**Datasources:** {N}
**Total calcs:** {N}
**Graph shape:** {linear | tree | DAG | cyclic}
**Cycles detected:** {N or none}
**PARTIAL-EXTRACT datasources:** {list or none}

## Summary

{One paragraph summarizing calc-family structure. Cite total counts, graph shape, most-referenced calcs, and any cycles or partial extracts. Tone: neutral-technical.}

## Cycle Warnings

{Render only if CD-CYCLE-01 fired. Otherwise omit section entirely.}

- **[CD-CYCLE-01] Circular Dependency**
  - **Chain:** {A} → {B} → {C} → {A}
  - **Affected calcs marked `in_cycle: true`:** {list}
  - **Impact:** Reference graph does not render a valid dependency chain for these calcs. Aggregation context is best-effort.
  - **Desktop fix:** Break the cycle by rewriting one calc in the chain to not reference the others. Route to `calc-debugger` for cycle-breaking guidance.

## Per-Datasource Sections

### Datasource: {datasource_name}

**Calc count:** {N}
**Type breakdown:** {N row-level, N aggregate, N LOD, N table-calc}
**Documented (with author caption):** {N}

{Per-calc entries in dependency order, least-referenced first. Alphabetical on ties. Format:}

#### {calc_name}

- **Type:** {row-level | aggregate | LOD-fixed | LOD-include | LOD-exclude | table-calc}
- **Formula:**
  ```
  {formula from XML, with any internal Calculation_NNNN... tokens that reference other calcs substituted for their resolved caption/name per HC#16; unresolvable tokens left raw and flagged "unresolved: <raw_token>"}
  ```
  {If any substitution occurred, append directly below the code block: "(stored internally as [<raw_token>, ...]; captions shown above)"}
- **Fields referenced:** {list of resolved field names, or "unresolved: <raw>" per HC#7}
- **Uses:** {list of other calcs this depends on, or "none"}
- **Used by:** {list of other calcs that depend on this, or "none"}
- **On sheets:** {list of worksheet names, or "not on any shelf"}
- **On dashboards:** {list of dashboard names via filter or parameter, or "none"}
- **Aggregation pattern cited:** {short pattern description that fired the classification}
- **Cross-datasource references:** {list or none}
- **Author caption:** {verbatim if present, or "none"}
- **Author annotation:** {verbatim if XML comment attached, or "none"}
- **Cycle status:** {in_cycle: true | omitted}

{Repeat per calc within the datasource. Repeat per datasource.}

## Handoff Payload

```yaml
schema: calc_documentation/1
workbook_name: "{name}"
datasources: {N}
total_calcs: {N}
graph_shape: "{linear | tree | DAG | cyclic}"
cycles:
  - chain: [{calc_a}, {calc_b}, {calc_c}]
    affected_calcs: [{list}]
partial_extract_datasources: [{list or empty}]
datasources:
  - name: "{ds_name}"
    calc_count: {N}
    calcs:
      - name: "{calc_name}"
        type: "{row-level | aggregate | LOD-fixed | LOD-include | LOD-exclude | table-calc}"
        formula: "{verbatim}"
        fields_referenced: [{list}]
        uses: [{list}]
        used_by: [{list}]
        on_sheets: [{list}]
        on_dashboards: [{list}]
        aggregation_pattern: "{cited pattern}"
        cross_datasource_references: [{list or empty}]
        author_caption: "{verbatim or null}"
        author_annotation: "{verbatim or null}"
        in_cycle: {true | false}
routing:
  calc_explainer: {true | false}
  calc_linter: {true | false}
  calc_debugger: {true | false}
  workbook_auditor: {true | false}
  publish_readiness: {true | false}
delivery:
  tier_a_rendered: {true | false}
  tier_b_saved: {true | false}
  tier_b_file_path: {absolute_path_or_null}
  tier_b_format: {md | txt | null}
run_metadata:
  timestamp: {ISO-8601}
  tool_failures: [{list or empty}]
```

## Next Steps

{One or two-line concrete pointer based on the graph shape and cycle count. Never generic.}

## Reference

- Aggregation pattern classification: `aggregation_patterns.md` in the skill directory.
- Handoff schema: `handoff_schema.md`.
```

## Section Rendering Rules (Tier B)

**Header block.** Always renders skill version, timestamp, workbook name, datasource count, total calc count, graph shape, cycles-detected count, and PARTIAL-EXTRACT list.

**Summary section.** 1 paragraph. Plain-language. Neutral-technical tone.

**Cycle Warnings.** Renders only if CD-CYCLE-01 fired. If empty, section omitted entirely.

**Per-datasource sections.** Every datasource renders a section, even those with zero calcs (renders "No calculated fields in this datasource"). Never omit a datasource that appears in `list-workbook-datasources`.

**Per-calc entries.** All 5 required dimensions rendered per HC#4. Author caption and annotation preserved verbatim per HC#11. Dependency-order sort per HC#15.

**Handoff Payload.** Always rendered as a YAML block.

**Next Steps.** Concrete pointer per graph shape. Cyclic → route to calc-debugger. Undocumented calcs → route to calc-linter. Never generic.

## Overflow Handling

- **Many calcs (100+).** No inline cap in Tier B; every calc renders. Dependency-order sort preserves scan-ability. Consider a summary index at the top listing calc names in order.
- **Many datasources (10+).** Every datasource renders a section, in enumeration order.
- **Long formulas (multi-line).** Preserved verbatim in the code block. No sanitization.

## File-Write Confirmation Flow

1. Tier A chat summary renders with save-file offer.
2. If user opts in:
   - Confirm format (.md default, .txt option).
   - Resolve Downloads folder OS-agnostically. Windows: `%USERPROFILE%\Downloads\`. macOS: `$HOME/Downloads/`.
   - Confirm the exact save path before writing.
   - Write per Tier B shape.
   - Report path back in chat.
3. If user declines, no file is written. Handoff schema still emits to session context.

Never write silently. HC#12 non-override.

Fresh-filename discipline: append `_v2`, `_v3` on collision.

## Refuse to Fabricate

Never render a calc entry without its verbatim formula. Never invent a field reference not present in the formula. Never invent an aggregation classification unsupported by the aggregation_patterns.md pattern set. Never suppress an author caption or annotation. Never render the full dictionary in Tier A chat.
