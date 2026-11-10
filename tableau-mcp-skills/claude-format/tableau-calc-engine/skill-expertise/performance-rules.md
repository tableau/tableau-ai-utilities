# Performance Optimization Reference

The performance hierarchy and optimization decision tree for calculations.

### The Performance Hierarchy (Fastest → Slowest)

1. Datasource-materialized columns — Fastest
2. Row-level calculations — Very fast
3. Simple aggregates (SUM, COUNT, AVG) — Fast
4. FIXED LOD — Moderate (cost depends on grain and datasource; cheap at a coarse grain, costly at a fine grain)
5. INCLUDE/EXCLUDE LOD — Moderate
6. Basic table calculations — Moderate
7. Nested LOD — Slow
8. Complex table calculations (nested WINDOW/LOOKUP) — Slow
9. String ops on high-cardinality (CONTAINS, REGEXP) — Very slow
10. Nested table calcs with LOD inputs — Slowest

### Optimization Decision Tree

| Current Pattern | Better Alternative | When |
|---|---|---|
| `CONTAINS([field], "x")` on 1M+ rows | Boolean column in datasource | String matching expensive at scale |
| Nested FIXED inside FIXED | Single FIXED with compound dimensions | `{ FIXED [A], [B] : ... }` |
| LOD used only for one view | Regular aggregate | View already has the right grain |
| TOTAL() in many cells | Percent-of-total via EXCLUDE or FIXED LOD | Test both; neither is always faster |
| LOOKUP across many rows | Fewer marks (aggregate higher, filter earlier) | Table calcs run on the returned result set |
| COUNTD on high-cardinality | Approximate count in DB | Exact distinct is expensive |
| >5 IIF/IF branches | Group calc or lookup table | Long branch chains are hard to maintain and can be slower on large data |

**Note:** this ranking is a rule of thumb. Cost depends on data volume, grain, and datasource. Confirm with Tableau's Performance Recorder before recommending a rewrite as faster.
