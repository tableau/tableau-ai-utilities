# Performance Hierarchy (Locked, 5 Tiers)

Tier ranking authority for calc-optimizer. Never invent a new tier or reorder tiers mid-run. Every optimization delivery reports movement using this catalog.

## Tier 1 (Fastest)

Bare row-level references, boolean row-level flags, INT arithmetic on native measures, simple arithmetic on native measures.

- `[Sales]` (bare reference)
- `[Sales] > 500` (boolean row-level flag)
- `[Sales] * 1.1` (arithmetic on native measure)
- `INT([Order ID])` (type coercion on indexed field, if `[Order ID]` is stored as string but numerically valued)
- `[Order Date]` (bare date reference)

**Why fast:** compiled to native SQL/columnar operations. No cross-row work. No LOD context. No string parsing.

## Tier 2

Aggregated arithmetic, single-dimension FIXED LOD, IF/ELSEIF chains on aggregates.

- `SUM([Profit]) / SUM([Sales])` (aggregated arithmetic)
- `IF SUM([Sales]) > 100 THEN SUM([Sales]) END` (aggregate IF)
- `{FIXED [Region] : SUM([Sales])}` (single-dimension FIXED LOD)
- `{FIXED [Order ID] : SUM([Sales])}` (grain-preserving FIXED LOD)

**Why not tier 1:** requires one aggregation pass, which costs a group-by. Still one pass total.

## Tier 3

Multi-dimension FIXED LOD, INCLUDE/EXCLUDE LOD, string equality on indexed fields, DATEPARSE on stored date strings.

- `{FIXED [Region], [Category] : SUM([Sales])}` (multi-dimension FIXED)
- `{INCLUDE [Category] : SUM([Sales])}` (INCLUDE LOD, executes after dimension filters)
- `{EXCLUDE [Segment] : SUM([Sales])}` (EXCLUDE LOD)
- `[Region] = 'West'` (string equality on indexed dimension)
- `DATEPARSE('yyyy-MM-dd', [Date String])` (parse cost, but bounded)

**Why not tier 2:** multi-dimension group-by costs more than single-dimension; INCLUDE/EXCLUDE recompute per view; DATEPARSE parses every row.

## Tier 4

Nested LODs (depth 1), CONTAINS / STARTSWITH / ENDSWITH on non-aggregated strings, DATEDIFF inside filter context, table calcs where a FIXED LOD would suffice, IF/ELSEIF chains deeper than 4 levels.

- `{FIXED [Region] : AVG({FIXED [Order ID] : SUM([Sales])})}` (nested LOD depth 1)
- `CONTAINS([Product Name], 'Chair')` (row-level string search)
- `STARTSWITH([Customer Name], 'A')`
- `WINDOW_SUM(SUM([Sales]))` used where `{FIXED [dim] : SUM([Sales])}` would achieve the same semantics
- Deeply nested IF/ELSEIF (>4 branches)

**Why not tier 3:** nested LODs require multiple group-by passes; row-level string ops parse every row; table calcs post-process the query result and can't be pushed to the source.

## Tier 5 (Slowest)

COUNTD on high-cardinality fields, REGEXP_MATCH / REGEXP_REPLACE, nested LODs (depth 2+), row-level string ops inside aggregations, cross-datasource blending inside calc context, DATEDIFF nested inside COUNTD.

- `COUNTD([Customer ID])` on a data source with 100k+ customers
- `REGEXP_MATCH([Product Name], 'Chair|Table|Desk')`
- `{FIXED [Region] : AVG({FIXED [Category] : AVG({FIXED [Sub-Category] : SUM([Sales])})})}` (nested depth 2+)
- `SUM(IF CONTAINS([Product Name], 'Chair') THEN [Sales] ELSE 0 END)` (row-level string op inside aggregation)
- Cross-datasource blend: `[Primary].[Sales] / [Secondary].[Target]` inside a calc

**Why slowest:** cardinality-dependent group-bys, regex compilation, multi-pass LODs, row-level string parsing inside aggregations, cross-DS network hops.

## REGEXP_MATCH → CONTAINS Rewrite: Substring-Collision Warning (Locked)

Rewriting `REGEXP_MATCH([field], 'A|B|C')` as `CONTAINS([field],'A') OR CONTAINS([field],'B') OR CONTAINS([field],'C')` is NOT guaranteed value-preserving even when both sides use matching case-sensitivity. Any target word that is a substring of a longer, unrelated word produces a false positive under CONTAINS that a case-sensitive REGEXP_MATCH on the literal alternation may not share, and vice versa. Confirmed example (Sample - Superstore, `'Chair|Table|Desk'`): product names containing "Portable," "Adjustable," "Printable/Imprintable," or "CHAIRMAT" collide on the substrings "table"/"chair" embedded in a larger word, producing real value differences (~213 mismatched rows out of ~9,994) between the original and the naive rewrite — this is NOT a hypothetical edge case, it reproduced live in testing. Case-normalizing both sides (wrapping in `UPPER()`) does not fix this; it can introduce a *different* set of substring-collision false positives instead of removing the original mismatch source.

**Implication for Phase 3/4:** never treat a REGEXP_MATCH→CONTAINS-OR rewrite as safe by construction. Always run R-EQUIV-01 (mandatory, no exception) and treat a mismatch as a signal to add explicit word-boundary safety (e.g., a regex with `\b` boundaries preserved as REGEXP_MATCH, or a CONTAINS check paired with a delimiter/whitespace test) rather than assuming a second case-adjustment attempt will fix it. If two independent rewrite attempts both fail equivalence, fail-open per HC#8 rather than guessing at a third variant.

## Optimization Movement Rules

- **Target one full tier drop.** A rewrite that moves from tier 4 to tier 2 is a strong optimization. Half-tier improvements are noted but not prioritized.
- **Never sacrifice value equivalence for tier movement.** If a tier-2 rewrite subtly changes returned values, deliver the tier-3 equivalent instead. HC#2 is inviolable.
- **Filter-order-of-operations preserved.** FIXED executes before dimension filters (unless promoted to context); INCLUDE/EXCLUDE after. Optimizer must not silently change which stage the calc executes at.
- **Tier 1 targets are rare.** Most aggregated calcs cannot drop below tier 2. Deliver "already optimal" if the calc is a bare aggregated ratio and the aggregation itself is unavoidable.

## Perf-Advisory Flags (Advisory-Only, Never Block Delivery)

- `PA-COUNTD-HIGH-CARDINALITY` — COUNTD on a field with >50k distinct values.
- `PA-REGEXP-IN-AGGREGATE` — REGEXP_MATCH inside SUM/AVG/COUNT.
- `PA-CONTAINS-IN-AGGREGATE` — CONTAINS inside SUM/AVG/COUNT.
- `PA-LOD-NESTED-DEPTH-2` — Nested LOD at depth 2 or deeper.
- `PA-TABLE-CALC-WHERE-LOD-WOULD-WORK` — Table calc where a FIXED LOD achieves the same semantics.
- `PA-CROSS-DS-BLEND` — Cross-datasource reference inside a calc.
- `PA-DATEDIFF-IN-FILTER` — DATEDIFF used as a filter argument.
- `PA-NESTED-IF-DEEP` — IF/ELSEIF chain deeper than 4 branches.
- `PA-STRING-ARITHMETIC` — Arithmetic on a String-typed field (implicit conversion cost).

Emitted in the `perf_advisory` block of `calc_optimize_handoff/1`. Never blocks delivery — advisory-only for downstream awareness.

## Connection-Type Caveat

Tier rankings are architectural heuristics based on typical extract behavior, not measured query-plan benchmarks. On live connections to pushdown-capable databases (e.g., Snowflake, BigQuery), the database's own optimizer can narrow or reverse some tier gaps — a tier-4 rewrite may not measurably outperform tier 5 on every backend. State this caveat in the handoff `notes` when the datasource is a live connection. Never claim an "always slower" relationship as a measured fact for a specific user's environment — it is a directional ranking, not a guarantee.

## Refuse to Fabricate

If a calc doesn't cleanly fit any of the five tiers, ask the user for context (e.g., typical data volume) rather than inventing a tier. Never invent a tier 0 or tier 6.
