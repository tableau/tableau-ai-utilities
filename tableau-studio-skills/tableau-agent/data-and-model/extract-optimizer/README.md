# Extract Optimizer

Audits Tableau extract configuration across four locked dimensions for refresh speed and storage efficiency. Advisory-only.

**Example:** Your extract refreshes in 20 minutes and the file is 3 GB. Optimizer audits and reports: no incremental refresh key configured (Warning), 47 hidden fields never placed on any sheet (Warning, ~38% pruning candidate), one filter used on every sheet with the same date range (Warning, 62% row-reduction candidate). All fixes as Desktop UI steps.

## What it does

Extracts get configured once and rarely revisited. Optimizer forces a systematic four-dimension review: incremental refresh, aggregation, hidden-field pruning, filter-at-extract. Every recommendation is quantified; hedging is banned by hard constraint.

## When to use it

- "Optimize this extract."
- "Why is my extract so slow to refresh?"
- "Why is my extract so big?"
- "Should I set up incremental refresh?"
- "Extract tuning."

## When NOT to use it

- Connection setup (use `data-source-connector`).
- Publishing to Server or Cloud (out of scope).
- Data-quality issues (use `data-quality-review`).
- Pre-publish hygiene across the whole workbook (use `publish-readiness`).
- Calc perf (use `calc-optimizer`).
- Dashboard-render perf (use `worksheet-builder`).

## The Four Dimensions

- **D1 Incremental Refresh Key:** monotonically increasing datetime or bigint field identified but not configured.
- **D2 Aggregation:** row-level extract with every sheet aggregating on the same few dimensions.
- **D3 Hidden-Field Pruning:** fields never placed on any shelf, encoding, filter, or tooltip.
- **D4 Filter-at-Extract:** filters used on every sheet with the same value or range.

## What you get back

- Findings grouped by dimension, severity-ranked Critical → Warning → Note.
- Every finding cites its dimension ID, evidence (specific fields or filters), quantified impact, and Desktop UI fix path.
- Handoff line if the follow-up is calc perf, dashboard perf, or cross-workbook hygiene.

## Limitations

- Cannot run Performance Recorder. Impact estimates from inventory, not measured latency.
- Cannot see refresh-log history. Can't diagnose historical events.
- Cannot detect connector-specific optimizations (push-down behavior).
- Row-reduction estimates are based on current filter values; actual reduction may vary as data grows.
- Never modifies extract settings. Desktop UI only.
