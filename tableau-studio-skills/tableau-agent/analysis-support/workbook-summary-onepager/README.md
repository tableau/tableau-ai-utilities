# Workbook Summary Onepager

Produce a single-page onepager summarizing a Tableau workbook for a stakeholder who won't open Desktop. Five locked sections aggregated from upstream handoffs when available; local-extract fallback otherwise.

**Example:** "Summarize this workbook for a stakeholder handoff."

***

## What it does

Aggregates three upstream handoffs (calc-documenter, data-model-documenter, dashboard-caption-audit) into 5 locked sections: what the workbook shows, key metrics defined, data sources used, dashboards included, and known limitations. Every section carries a signal-source label (handoff, local_extract, or empty_state) so a reader can trace any fact back to its origin.

## When to use it

- "I need a one-pager on this workbook for a colleague who won't open Desktop."
- "I want to hand this workbook off to a stakeholder with context, not just the file."
- "I need a pre-publish summary of what's inside."

## When NOT to use it

- Not for a live-data snapshot with current metric values (structural summary only).
- Not for rewriting or editing the workbook based on the summary (route to calc-writer or viz-planner).
- Not for multi-workbook batch summary (out of scope).
- Not for tab-order or print-layout audits (route to dashboard-tab-order or dashboard-print-check).
- Not for scoring the workbook design (route to viz-critique-pro-studio).

## How to trigger it

- "summarize this workbook"
- "one-pager please"
- "workbook onepager"
- "stakeholder summary"
- "workbook-summary-onepager"
- "hand off this workbook"

## What you'll need

- Tableau Desktop 2024.3 or later with the MCP agent connected.
- The workbook open.
- Optionally: fresh handoffs from calc-documenter, data-model-documenter, and dashboard-caption-audit for the richest summary. Without them, the skill falls back to local-extract cleanly.

## Example walkthrough

**Input:** Summarize the currently open Superstore workbook.

**Output:**

```
Workbook Summary Onepager: Superstore

1. What this workbook shows. [signal_source: local_extract]
   Sales performance (Overview, Product), customer analysis (Customers),
   shipping logistics (Shipping), order-level detail (Order Details),
   and a sales-commission model (Commission Model).

2. Key metrics defined. [signal_source: handoff, top 5 by reference count]
   Achievement (estimated), Days to Ship Actual, Days to Ship Scheduled,
   Profit Ratio, Sales per Customer.

3. Data sources used. [signal_source: handoff, partial DS coverage]
   Sample - Superstore (3 tables, 33 fields).
   [signal_source: local_extract] Sales Commission, Sales Target
   (row_count: unknown; no data-model handoff for these two).

4. Dashboards included. [signal_source: handoff]
   Overview, Product, Customers, Commission Model, Shipping - all fully titled.
   Order Details - placeholder title flagged.

5. Known limitations. [signal_source: empty_state]
   No known limitations documented in workbook caption.

Save full onepager to file? (.md or .txt)
```

## What you get back

- Tier A: compact 25-line chat summary with 5 sections and signal-source attribution.
- Tier B (opt-in): full onepager saved as `.md` or `.txt` to a user-confirmed path.
- A `workbook_summary/1` handoff for downstream consumers (publish-readiness, workbook-auditor).

## Limitations

- Live-data snapshot out of scope. Section 2 lists metric definitions, not their current values.
- Supports `.md` and `.txt` only.
- Workbook-level author caption may not be exposed by all `get-workbook-inventory` implementations; falls back to dashboard-title aggregation.
- Data-model handoff is one-datasource-per-run. Multi-DS workbooks get partial handoff coverage plus local-extract fallback for uncovered DSes; the skill labels this transparently.
- `list-available-fields` doesn't surface the Desktop Description field (platform gap), so calc descriptions from Section 2 rely on handoff data preferentially.

## Troubleshooting

- **"Section 3 shows partial coverage."** Expected on multi-DS workbooks; data-model-documenter is one-DS-per-run. Run it against each datasource for full coverage.
- **"Skill wants a file path before saving."** HC#10 refuses silent writes. Provide an explicit path plus format choice (`.md` or `.txt`).
- **"Rerun produced different content."** Should not happen for the same workbook state. If it does, check whether upstream handoffs went stale between runs; the fingerprint check should have caught it.

## Support

File issues in the Tableau Studio Agent Skills repo.
