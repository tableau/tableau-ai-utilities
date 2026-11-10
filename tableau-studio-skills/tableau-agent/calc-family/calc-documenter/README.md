# Calc Documenter

Generate structural documentation for every calculated field in a Tableau workbook. One run, one dependency-sorted dictionary, ready to hand off to a colleague or archive with the workbook.

**Example:** Point it at a Superstore-style workbook with 25 calcs across three datasources and get back a per-calc entry with formula, referenced fields, uses / used-by graph, sheet and dashboard usage, aggregation classification, and preserved author captions.

## What it does

Scans every calculated field in an open Tableau workbook and produces a five-dimension dictionary entry per calc: formula (verbatim), fields referenced, reference graph (uses and used-by), sheet / dashboard usage, and aggregation context (row-level, aggregate, LOD-fixed, LOD-include, LOD-exclude, or table-calc). Author captions and in-formula `//` comments are preserved verbatim. Read-only. Nothing gets written back to the workbook. Chat delivers a compact summary; the full dictionary saves to a file only if you confirm the path.

## When to use it

- "I inherited a workbook with 40 calcs and I need to understand what's there before I touch it"
- "I need to hand this workbook off and want a proper calc dictionary as part of the handoff"
- "I want to see the reference graph so I know which calcs get consumed by other calcs vs. dead ends"
- "I need to run this before calc-explainer or calc-linter so the downstream skills have a handoff to consume"
- "I want to catch circular calc references or unused calcs during a governance sweep"

## When NOT to use it

- Not for explaining a single calc in plain language (use `calc-explainer`)
- Not for diagnosing why a calc returns NULL (use `calc-debugger`)
- Not for calc naming, hygiene, or comment audit (use `calc-linter`)
- Not for calc performance rewrites (use `calc-optimizer`)
- Not for authoring new calcs (use `calc-writer`)
- Not for cross-workbook or multi-workbook bulk runs (one workbook per invocation)

## How to trigger it

- "document all calcs in this workbook"
- "generate a calc dictionary"
- "calc-documenter"
- "produce a calc reference for this workbook"
- "build a dependency graph of the calcs"

## What you'll need

- Tableau Studio with the target workbook open
- Every relevant datasource loaded (calcs in unloaded datasources will be flagged PARTIAL-EXTRACT rather than fabricated)
- A Downloads path or user-specified folder for the optional file output

## Example walkthrough

**Input:** "document all calcs in this workbook" (Superstore with three datasources: Orders, Sales Commission, Sales Target)

**Tier A chat output:**

```
Calc Documentation Summary
Workbook: Superstore.twbx
Datasources: 3 (Orders, Sales Commission, Sales Target)
Total calcs: 25
Reference graph shape: DAG (no cycles)

TL;DR by datasource:
- Orders: 18 calcs. 3 LOD, 2 table-calc, 8 aggregate, 5 row-level.
- Sales Commission: 4 calcs. All aggregate. 100% undocumented (routing.calc_linter: true).
- Sales Target: 3 calcs. 1 LOD-fixed, 2 aggregate.

Top 3 most-referenced calcs:
1. Profit Ratio (Orders): used_by_count 4
2. Sales (Orders): used_by_count 3
3. Regional Sales (Orders): used_by_count 2

Save full dictionary to file?
```

**Tier B (opt-in file output, after path confirmation):** a `.md` document with per-datasource sections, dependency-order-sorted per-calc entries (formula verbatim, referenced fields via resolve-field, reference graph, sheet and dashboard usage, aggregation classification, author caption / annotation), and a handoff YAML block ready for downstream skills to consume.

## What you get back

- Compact chat summary (Tier A): datasource count, total calcs, reference-graph shape, per-datasource TL;DR, top 3 most-referenced calcs
- Optional full dictionary file (Tier B): per-calc entries in dependency order with all five dimensions plus optional author caption / annotation
- Handoff schema `calc_documentation/1` consumed by calc-explainer, calc-linter, calc-debugger, workbook-auditor, and publish-readiness
- Cycle detection flag if any circular references are found (rare, since Tableau blocks most cycles at authoring time)
- Adjacent-skill routing signals (e.g., `routing.calc_linter: true` if a datasource has zero author captions)

## Limitations

- One workbook per run. Bulk-workbook runs are refused.
- `list-available-fields` reliability gap can produce partial calc lists on some workbooks. The skill flags PARTIAL-EXTRACT per datasource rather than fabricating around missing data.
- Cross-datasource references are named (`cross_datasource_reference: Orders.Sales`) but not fully resolved if the target datasource is not loaded.
- Table-calc addressing and partitioning are not documented per calc (deferred to sheet-level context).
- Author caption XML path is not exposed by Desktop UI; only in-formula `//` comments are captured under `author_annotation`. The `author_caption` field remains empty for calcs authored via Desktop.
- Cycle detection code path exists but cannot be exercised via native authoring, since Tableau blocks circular formula references at authoring time. Requires malformed-XML injection to test.

## Troubleshooting

- **"PARTIAL-EXTRACT flagged on datasource X"** then `list-available-fields` returned partial results. Reload the datasource in Desktop or verify it is loaded, then re-run.
- **"get-worksheet-xml failed on sheet Y"** then the sheet is dashboard-bound and hits a known reliability gap. Skill emits `"unresolved: xml-read-failed"` per HC#7 and continues. Sheet-level usage for that one sheet will be missing; the rest of the dictionary is intact.
- **"Save aborted, no path confirmed"** then HC#12 blocked a silent file write. Confirm a Downloads path when prompted (skill will not default-save).
- **A calc appears twice**  then the same name exists in multiple datasources. Skill prefixes with datasource name (`Orders.Profit Ratio` vs `Returns.Profit Ratio`) to disambiguate.
- **"100% undocumented, routing.calc_linter: true"** then the datasource has zero author captions. Not a failure; the handoff offers `calc-linter` for hygiene follow-up.

## Support

File issues in the Tableau Agent Skills repo.
