# Data Quality Review

Profiles and fixes data quality issues on a connected Tableau Studio datasource. Two scan layers: a Metadata Pre-Scan that runs in seconds from the field inventory (naming violations, type/role mismatches, near-duplicates, unused fields) and a Row-Level Deep Scan that samples actual data for nulls, dupes, whitespace, outliers, cardinality, dates, constants, and sparseness. Every proposed fix is additive, reversible, and requires your explicit approval before being applied.

**Example:** "Profile this datasource" returns a teaser in a few seconds: 47 fields (28 dimensions, 18 measures, 1 calc), 6 metadata findings (2 near-duplicate field names, 1 type mismatch, 3 naming violations), and the top 3 issues named inline. Then asks whether you want the full row-level scan or just the fixes.

***

## What it does

Systematically audits a live Tableau Studio datasource for the issues that quietly break analytics: field naming drift, type/role mismatches that produce wrong aggregations, near-duplicate fields nobody knows which to trust, nulls hiding inside key dimensions, whitespace and casing variants that fragment groups, outliers that skew averages.

Findings are evidence-backed. Metadata findings cite the field inventory. Row-level findings cite an actual `get-summary-data` read with a stated sample size (default 1,000 rows, adjustable). Detection uses locked thresholds and regex patterns, not model judgment, so two sessions running the same scan on the same datasource produce the same report.

Every fix is a calculated field, filter, or worksheet-level change. Nothing rewrites your data. Nothing deletes a field. If you approve a fix, an additive `author-calc` (or equivalent) makes the change; you can remove it just as easily.

Proactively offers a quick metadata teaser when a new datasource is connected. Doesn't re-offer if you decline.

## When to use it

- "Profile this datasource" (metadata-only teaser)
- "Any issues with this data before I start building"
- "Check my fields for naming problems"
- "DQ review, I inherited this workbook"
- "Any nulls or dupes in this data"
- "Audit this datasource end to end"

## When NOT to use it

- Not for performance tuning
- Not for data modeling or relationship design
- Not for ETL pipeline debugging
- Not for site governance, certification workflows, or Tableau Server/Cloud published-datasource scans (Desktop live connections only)
- Not for row-level security configuration
- Not for building or editing charts, dashboards, calcs, or datasource connections. If the ask is authoring rather than auditing existing data, use the built-in Studio authoring skill (`tableau-desktop-authoring`).

## How to trigger it

- "/datareview"
- "Check data quality"
- "Profile this datasource" (metadata-only)
- "Field hygiene"
- "Any issues with this data"
- "DQ review"
- "Data quality check"
- "Audit this datasource"
- "Check my fields"
- "Naming issues"
- "Find data issues"
- "Any nulls or dupes in this data"
- "Field profiler"
- "Scan this datasource"

## What you'll need

- Tableau Studio with the datasource actively connected (Desktop live connections only, no published-datasource scans)
- The MCP tools Data Quality Review uses: `list-available-fields`, `list-workbook-datasources`, `resolve-field`, `get-summary-data`, `add-field`, `remove-field`, `build-and-apply-worksheet`, `list-worksheets`, `get-workbook-inventory`, `author-calc`
- For row-level scans, a sample size preference (default 1,000). Adjustable up to full population.
- For very large datasources (>1M rows or slow live connections), Data Quality Review flags the size before sampling at the default cap and offers alternatives (date filter, extract review) for full coverage.

## Example walkthrough

**Input:** "Profile this datasource."

**Output (Phase 0 metadata teaser, in seconds):**

```
Quick profile of Sales_Dirty:
  47 fields (28 dimensions, 18 measures, 1 calc)
  6 metadata findings
    High:   2   (near-duplicate field names)
    Medium: 3   (naming violations)
    Low:    1   (type/role mismatch)

Top issues:
  - Near-duplicate: "Revenue" and "revenue " (trailing space).
    Analyst confusion risk. Fix: rename one and add a comment.
  - Near-duplicate: "Customer ID" (string) and "customer_id"
    (integer). Different casts, same concept. Fix: consolidate.
  - Type mismatch: field "Order Date" is typed String, should be
    Date. Aggregation will silently fail on any date function.

Want the full data scan (nulls, dupes, outliers)? Or just fix these?
```

If you accept the full scan, Data Quality Review runs the row-level deep scan with a stated sample size, then presents a triaged report with proposed fixes for each finding. Each fix is a specific calc or worksheet change you approve before it lands.

**"Profile" is metadata-only, deliberately.** If the ask uses "profile" in any form ("profile this datasource", "quick profile", "field profile"), the run stops at the teaser and offers the row-level scan. Only "DQ review", "check data quality", "audit this datasource", "any issues with this data", or an explicit "run the full scan" continues to the row-level phase without a second confirmation.

## What you get back

- **Two scan layers, opt-in.** Metadata Pre-Scan runs in seconds and is safe to run proactively. Row-Level Deep Scan samples actual data and is opt-in on non-full-audit triggers.
- **Metadata checks (M1-M5):** naming conventions, type/role mismatches, schema hygiene, near-duplicate field names, and unused fields.
- **Row-level checks (1-10):** nulls, duplicates, type mismatches, whitespace, casing variants, outliers, cardinality issues, date sanity, constants, and sparseness.
- **Locked thresholds and regex patterns**, not model judgment. Two sessions scanning the same datasource produce the same findings.
- **Severity-triaged report** with the datasource name, fields checked, sample size, and every finding cited with the evidence that surfaced it.
- **Additive, reversible fixes.** Every proposed fix is a calculated field, filter, or worksheet-level change. Never deletes a field. Never rewrites data. You approve before it's applied.
- **Field-scoping heuristic on wide datasources.** For 26-100 field datasources, Data Quality Review focuses on join keys, all measures, and dimensions already in use. For >100 fields, it recommends the top 25 by usage. You can override with "check all" or specific field names.
- **Full-population disclosure.** If the datasource has fewer rows than the sample size, the report says "full-population scan" instead of "sampled."
- **Business-term matching.** If you say "check my sales data" and there's a datasource called `Sales_Clean`, Data Quality Review suggests it proactively rather than stopping at "I don't see that."

## Limitations

- **Desktop live connections only.** No Tableau Server or Cloud published-datasource scans.
- **Sample-based on large datasources by default.** For >1M rows, the default 1,000-row sample is flagged and alternatives (date filter, extract review) are offered. Full-population scans are available on request but slower.
- **Metadata findings can only see what the field inventory exposes.** Findings labeled "from field inventory" are explicitly separated from row-level findings backed by data reads. Metadata inferences are never presented as if confirmed by data.
- **Row-level findings require an actual data read.** If `get-summary-data` fails on a target field, the finding is skipped and noted, not fabricated.
- **Does not modify data.** Every fix is additive (a new calc, a filter). Data Quality Review never edits raw data, and never deletes an existing field.
- **`author-calc` needs the internal datasource ID, not the display caption.** Data Quality Review pulls the internal ID from `list-workbook-datasources` or an earlier `resolve-field` call. If you see "Datasource not found" errors, the caption was passed instead of the ID.
- **Not a substitute for ETL fixes.** If the root cause of a data issue is upstream (bad source system, broken extract refresh, incorrect join), Data Quality Review flags the symptom. The workbook-level fix mitigates; the source system needs a separate fix.

## Troubleshooting

- **"It ran the row-level scan when I only asked for a profile."** "Profile" is metadata-only by design. If a full scan ran on a "profile" ask, that's a regression — file it. The intended behavior stops at the teaser and asks whether to continue.
- **"It said my field doesn't exist but I know it's there."** Data Quality Review checks the full field inventory before declaring a field missing. If yours has a different display name than you expect (e.g. "Sales" is actually "Total Revenue"), it'll surface the semantic match. If it still says missing, run `list-available-fields` and confirm the exact name.
- **"It's checking 28 fields but I want all 47."** For datasources with 26-100 fields, the default focuses on keys, measures, and dimensions already in use. Say "check all" or name specific fields to broaden.
- **"The sample size seems too small for this data."** Default is 1,000. Ask for a larger sample or a full-population scan. If the datasource has >1M rows, Data Quality Review will flag the tradeoff before sampling.
- **"It proposed a fix I don't understand."** Every fix names the finding it addresses, the calc/filter it would create, and what changes downstream. If it's unclear, ask "explain this fix" — Data Quality Review will walk through the mechanics before you approve.
- **"A metadata finding said 'pending confirmation' and then disappeared."** Deduplication gate. If M2 flags the same field that Check #3 would also catch at row level, M2 is marked "pending confirmation" and either kept or removed after the row-level scan runs. Working as designed.
- **"`author-calc` errored with 'Datasource not found'."** The internal federated ID needs to be passed, not the display caption. Data Quality Review normally pulls it from `list-workbook-datasources`. If it errored anyway, that lookup failed — restart the run and it retries.

## Support

File issues in the same channel you use for other Tableau Studio skill feedback. Include the datasource name, the number of fields and rows, the finding you disagreed with (or the finding you expected but didn't see), and the sample size used.
