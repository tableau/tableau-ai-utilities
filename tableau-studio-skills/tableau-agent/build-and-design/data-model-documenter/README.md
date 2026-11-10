# Data Model Documenter

Exports a Tableau data source's logical model to a shareable markdown file. Read-only plus one file write. Current-state snapshot; no diff.

**Example:** You point it at a Snowflake data source with five tables and 12 relationships. It writes `snowflake_prod_model.md` next to the workbook with a table inventory (name, row-count estimate, field count), relationship map (cardinality, join conditions), calc-dependency graph, and a per-table field appendix. You share the file with a coworker who doesn't have Tableau access.

## What it does

The logical model lives inside the .twb and is hard to share. Documenter reads workbook state, extracts the model, and produces a single shareable markdown output. Deterministic; two runs on the same source produce the same file (modulo row-count sample variance on live sources).

## When to use it

- "Document this data model."
- "Export the tables and relationships."
- "Share this data source structure."
- "Make a data model doc for handoff."

## When NOT to use it

- Field-meaning documentation (use `data-scribe`).
- Change tracking over time (use `workbook-auditor`).
- Recommending model changes (use `join-and-relationship-advisor`).
- Connection setup (use `data-source-connector`).
- Data-content audit (use `data-quality-review`).

## What you get back

- Markdown file written to disk (default: `{datasource-name}_model.md` next to the workbook).
- Sections: data source metadata, table inventory (with row-count estimates), relationship map (cardinality + join conditions), calc-dependency graph, per-table field appendix.
- Chat summary: file path plus one-line inventory of what was documented.

## Sections in the Output File

1. **Data source metadata:** name, connection type, extract vs. live, extract config summary.
2. **Table inventory:** each table with row-count estimate and field count.
3. **Relationship map:** each pair with cardinality, join condition, referential-integrity assumption.
4. **Calc-dependency graph:** each calc with formula and referenced fields.
5. **Appendix:** per-table field list with datatype and role.

## Limitations

- Row-count estimates on live connections may not equal true source count.
- Cannot detect model changes over time (`workbook-auditor`).
- Cannot document field meaning beyond table-and-datatype level (`data-scribe`).
- Cannot document sets, hierarchies, or parameters that don't surface via `list-available-fields`. Noted as "not extractable."
- One data source per run.
- No publishing anywhere. Desktop file write only.
