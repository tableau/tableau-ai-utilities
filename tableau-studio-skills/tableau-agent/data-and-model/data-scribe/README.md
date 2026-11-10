# Data Scribe

Generates a field-level metric dictionary (Markdown or plain-text file) from a connected Tableau Studio datasource. Documents what each field is, how each calc works, representative sample values, and which sheets use each field. Read-only for the datasource, one file write for the output. One datasource per run.

**Example:** "Document this datasource" produces `Sales_Clean_metric_dictionary.md` written next to your workbook: 47 fields organized by category (Dimensions, Measures, Dates, Calcs, Groups), every calc explained in plain English with dependencies mapped, sample values captured for dimensions and date ranges, and a Usage Map showing which sheets place each field.

***

## What it does

Automates the tedious "open someone else's workbook and reverse-engineer every field by hand" loop. Reads the full field inventory, extracts calc formulas from `list-available-fields` (verified as the primary source, not XML parsing), samples real values via a temporary scratch sheet, maps field usage across worksheets, and assembles it all into a durable artifact you can share.

Descriptions inferred from field names, sample values, and usage context are flagged inline as `[Inferred: ... Verify with data owner]`. Nothing is presented as fact that isn't confirmed by the tools.

Calculated fields output in dependency order (leaf calcs first, compound calcs after) so the file reads top-to-bottom without forward references. Circular references get flagged rather than silently dropped or arbitrarily ordered.

## When to use it

- "I inherited this workbook, what's in it"
- "Onboarding doc for this datasource"
- "Document this dataset before I forget what everything means"
- "Metric dictionary for our BI team's shared datasource"
- "Export field documentation as a Markdown file"

## When NOT to use it

- Not for data quality issues like nulls, dupes, or outliers (use data-quality-review — same fields, different question)
- Not for building or editing charts, dashboards, or calcs (use a calc-authoring or dashboard-building skill)
- Not for describing what a worksheet visually shows (that's the wiring/logic story, not the field glossary)
- Not for multiple datasources in one run. Multi-datasource asks run as sequential single-datasource cycles.
- Not for Server or Cloud published datasources. Desktop live connections only.
- Not for modifying a calc, even to "fix" one that looks broken during extraction. Documentation-only.

## How to trigger it

- "Document this datasource"
- "Metric dictionary"
- "Field dictionary"
- "What do these fields mean"
- "Data dictionary"
- "Define these metrics"
- "I inherited this workbook, what's in it"
- "Onboarding doc for this data"
- "Export field documentation"

## What you'll need

- Tableau Studio with the workbook open and the datasource actively connected
- A saved workbook so Data Scribe can write the dictionary next to it. If the workbook path resolves inside a temp directory (e.g. `AppData\Local\Temp`), you'll be asked where to save instead of defaulting there.
- The MCP tools Data Scribe uses: `get-workbook-inventory`, `list-available-fields` (verbosity: full), `get-worksheet-xml`, `add-worksheet`, `delete-sheet`, `add-field`, `get-summary-data`, `resolve-field`, `Write`
- File format preference: plain text (`.txt`) or Markdown (`.md`). Data Scribe asks; no silent default.

## Example walkthrough

**Input:** "Generate a metric dictionary for Sales_Clean."

**Output (chat summary after the file is written):**

```
Data Scribe - Sales_Clean_metric_dictionary.md

Wrote to: C:\Users\...\Documents\My Tableau Repository\Sales Q3.twb
          folder / Sales_Clean_metric_dictionary.md

Fields documented: 47
  Dimensions: 18
  Measures:   14
  Dates:       3
  Calcs:      11 (2 LOD, 1 table calc, 4 basic, 4 conditional)
  Groups:      1

Calc dependency order applied. No circular references.

Parameters found via calc formula scanning: 2
  [Metric Selector] - toggles which measure is displayed on
                      "Regional Trend" and 3 other sheets.
  [Fiscal Year]     - filters Order Date on 5 sheets. Allowable
                      values: unknown - check parameter definition
                      in Desktop.

Sample values captured for 32 fields via scratch sheet
"scribe-scratch-2026-09-11" (deleted after sampling).

Notes:
  - Sets/Hierarchies not scanned this run - no reliable discovery
    tool for this environment; check Desktop's Data pane manually.
  - Field [Legacy Region Code] has no data available (all NULL in
    sample); flagged for the data owner.

Usage flags:
  - 3 fields defined but never placed on any sheet.
  - 4 fields used on 5+ sheets (core metrics).
```

The file itself follows the template in `skill-expertise/output_template.md`: a summary header, then Dimensions, Measures, Dates, Calculated Fields (in dependency order), Groups/Bins, Parameters, a Usage Map, and a Notes section.

## What you get back

- **A Markdown or plain-text file** written next to the workbook. Default filename `[datasource-name]_metric_dictionary.md`. Configurable via user preference.
- **Every field categorized:** Dimensions, Measures, Date/Time, Calculated Fields, Groups/Bins, Hierarchies (when present).
- **Every calc explained in plain English** with its formula, referenced fields/calcs, calc type (Basic / LOD / Table Calc / String / Date / Conditional), and any `[Parameters].` references.
- **Dependency-ordered calc list.** Leaf calcs first, compound calcs after. Circular references flagged rather than silently reordered.
- **Sample values for dimensions and dates.** Low-cardinality (<10 members) gets a full member list. Medium (10-50) gets top 10 by row count plus total count. High (>50) gets 3-5 representative values plus the count.
- **Measure statistics.** Min, max, avg from summary data. Grand-total SUM at minimum for every measure, even when full stats aren't feasible.
- **Parameter documentation** via formula scanning. Since parameters aren't directly enumerable, Data Scribe scans every calc formula for `[Parameters].[...]` references and documents the ones it finds. If a parameter isn't wired into any calc, it won't appear.
- **Usage map.** Field → sheets using it. Fields on 0 sheets flagged (defined but never placed). Fields on 5+ sheets flagged (core metrics).
- **Update mode.** If a dictionary already exists, Data Scribe offers to update it (preserving user-edited descriptions, appending new fields, flagging removed ones) rather than regenerating from scratch.
- **Family-level summary for repetitive fields.** For 300+ field datasources with numbered patterns (e.g. `Cost M01`..`Cost M24`), Data Scribe groups them as a family, samples 2-3 representative members, and lists all names so nothing gets dropped from coverage.

## Limitations

- **Read-only for the datasource.** Never modifies a calc, adds a field, or changes anything about the datasource. The only workbook mutation is a temporary scratch sheet, always cleaned up.
- **Sets and Hierarchies are not scanned.** No reliable discovery tool exists for this environment. The Notes section states this explicitly rather than silently omitting the sections.
- **Parameters are only discovered via calc formula scanning.** A parameter that exists in the workbook but isn't referenced in any calc won't appear in the dictionary. Data Scribe states this plainly ("no parameters found via calc scanning — this does not guarantee none exist").
- **Parameter allowable values are best-effort.** One `resolve-field` attempt per parameter; if that doesn't yield a domain, Data Scribe records "unknown — check parameter definition in Desktop" and moves on. Never calls `author-parameter` to probe (deterministic crash on Windows).
- **Hard stop on parameter-referencing calcs during sampling.** If any calc on the datasource references a parameter, Data Scribe will not call `build-and-apply-worksheet` or worksheet-mutating tools during Phase 4. This is a confirmed unresolved corruption risk. Sample values won't be gathered in that case; the file states this plainly.
- **Cloud connections may return timeouts.** Snowflake, BigQuery, Databricks, Redshift, and similar have higher per-query latency. A timeout is treated as a dropped connection, not a tool outage, and affected fields get "Cloud connection timeout — retry after re-authenticating in Desktop."
- **Very large live connections (300+ fields) sample fewer rows.** Default `maxRows: 100` on those to keep response time reasonable.
- **Blended (not related) datasources have a real tool limitation.** `build-and-apply-worksheet` refuses to bind fields from two different datasources onto one template. Sampling each blended datasource's own fields works normally; sampling cross-datasource blend behavior requires you to build the minimal worksheet manually in Desktop.

## Troubleshooting

- **"It said 'No workbook detected'."** No workbook is open in Desktop. Open the workbook with the connected datasource and re-run.
- **"It said 'No fields returned'."** The datasource is likely disconnected or in an error state. Reconnect or refresh the extract in Desktop, then re-run.
- **"It flagged a calc as 'formula not extractable'."** The `formula` field came back missing from `list-available-fields` and the XML fallback also couldn't read it. Rare. Inspect the calc manually in Desktop.
- **"It said 'Circular reference detected'."** Calc A references B and B (directly or transitively) references A. Data Scribe flags both at the end of the Calculated Fields section rather than picking an arbitrary order. Fix the circular dependency in the workbook if it matters.
- **"A field says 'Access restricted'."** Row-level security or a permission denial blocked the sample query. Data Scribe records the restriction and continues with other fields rather than treating it as a systemic outage.
- **"A scratch sheet didn't get deleted."** Cleanup failure. Data Scribe warns you by name so you can delete it manually. The dictionary still gets written.
- **"Desktop looks stuck."** A blocking dialog may be open. Tableau Studio has no command to dismiss it, so Data Scribe stops issuing calls and asks you to check for and dismiss any error popup. This is prevention-only; retries queue behind the same blocked thread.
- **"The workbook path resolves inside a temp folder."** Data Scribe won't default to writing there. It asks where to save instead.
- **"I want to update the existing dictionary, not regenerate."** When a dictionary file with the target filename already exists, Data Scribe asks: Update or Regenerate. Update preserves user-edited descriptions, appends new fields, and flags removed ones.

## Support

File issues in the same channel you use for other Tableau Studio skill feedback. Include the datasource name, field count, whether the datasource has parameter-referencing calcs, and what you expected in the output vs. what appeared.
