# Join vs. Relationship Decision Tree (Locked)

Deterministic decision-tree table indexed by (cardinality, referential integrity assumption, performance need). Never interpret; look up the row.

## Decision Tree

| Cardinality | Referential Integrity | Performance Need | Recommendation | Why |
|---|---|---|---|---|
| One-to-one | Yes | Any | Relationship | Simplest model, no fanning risk, contextual joins by Tableau. |
| One-to-one | No / unknown | Any | Relationship | Same as above; RI unknown just means contextual join runs a LEFT. |
| One-to-many | Yes | Standard | Relationship | Preserves grain of many-side; measures on either side aggregate correctly. |
| One-to-many | Yes | Performance-critical | Join (INNER or LEFT) | Static join is faster for very large fact-dimension pairs when the model is stable. |
| One-to-many | No / unknown | Standard | Relationship | Tableau infers correct grain; safer than a join for unknown RI. |
| Many-to-one | Yes | Standard | Relationship | Mirror of one-to-many; same reasoning. |
| Many-to-many | Any | Any | Relationship (required) | Joins on many-to-many cause row explosion. Relationships preserve grain via contextual joins. |
| Many-to-many with a bridge table | Any | Standard | Relationship (both edges to the bridge) | Standard star/snowflake with a bridge. Never join across the bridge; relationship both edges. |

## When to Prefer Join (Rare)

Prefer a join only when all four conditions hold:
1. Cardinality is one-to-one or one-to-many (never many-to-many).
2. Referential integrity is confirmed (no orphan keys on either side).
3. The model is stable and won't grow tables (adding a third table forces a rework).
4. Performance is critical AND the join provides measured (Performance Recorder) improvement.

If any condition fails, use a relationship.

## Sampling for Cardinality

Cardinality classification for a candidate key pair:

- Compute `COUNTD(key) / COUNT(*)` on each table.
- Ratio of 0.99 or higher → the side is "one" (each row has a unique key value).
- Ratio below 0.99 → the side is "many" (keys repeat).
- Referential integrity is "Yes" only when every key value on the many side also appears on the one side in the sampled rows; any orphan key, or a sample below 1,000 rows, means "unknown".
- Performance need is "Performance-critical" only when the user says so; otherwise "Standard".
- Cardinality is the product: one-to-one, one-to-many, many-to-one, many-to-many.

Sample size: use `get-summary-data` default. On extract-configured sources with filters, sampling reflects the extract, not the source.

## Refuse to Fabricate

If a candidate key pair doesn't fit any row above (e.g., composite keys, temporal joins with a range), report "outside current decision tree; consult manual join-configuration docs" rather than picking a row that doesn't fit.
