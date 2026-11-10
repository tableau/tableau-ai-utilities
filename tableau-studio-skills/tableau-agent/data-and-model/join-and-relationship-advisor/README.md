# Join and Relationship Advisor

Recommends join versus relationship, diagnoses cardinality mismatches, and predicts row-explosion or measure-doubling before it silently corrupts your dashboard. Advisory-only. Scoped to two-table pairs.

**Example:** You point it at Orders and Returns. It samples uniqueness on both sides of Order ID, classifies the pair as many-to-many, recommends a relationship (not a join), and flags that SUM(Sales) will double because both tables are many-to-many via Order ID. Routes the fix to `calc-writer` with the LOD pattern name.

## What it does

Compresses the "why is my measure doubling" investigation from an afternoon of scratch-sheet forensics to a single named diagnosis with a fix path. Reads the workbook, samples cardinality, checks the locked decision tree, and reports.

## When to use it

- "Recommend relationships for these tables."
- "Should this be a join or a relationship?"
- "Why is SUM(X) doubling?"
- "Grain check on Orders and Returns."
- "Fanning risk on this data source."

## When NOT to use it

- Connection setup (use `data-source-connector`).
- Row-level data quality (use `data-quality-review`).
- LOD authoring (use `calc-writer`).
- Model documentation (use `data-model-documenter`).
- Change tracking (use `workbook-auditor`).

## What you get back

- Recommendation per table pair: join vs. relationship, cardinality, one-line rationale.
- Row-explosion or fanning-risk warnings against shelf-placed measures.
- Desktop UI fix instructions.
- LOD-fix handoff routed to `calc-writer` by exact slug.

## Limitations

- Two-table pairs only.
- Cardinality inferred from `get-summary-data` sampling. Extract filters may skew large-table samples.
- Cannot detect fanning in calcs that construct measures at query time. Only on shelf-placed measures.
- Never modifies the data model. Every fix is a Desktop UI instruction.
