# i18n Scanner

Reads every user-facing string in a Tableau workbook (worksheet titles, tooltips, aliases, parameter labels, calc string literals, custom number and date format strings) and produces two files: a translation-ready CSV a translator can work from without needing Desktop, and a severity-ranked findings report flagging locale-fragile patterns like hard-coded dollar signs, US-style dates, and English-only text baked into calcs. Read-only. Never mutates the workbook.

**Example:** "Is this dashboard ready for global?" returns 187 strings scanned, 4 Critical (a hard-coded `$` in a KPI format string, three US-only vocabulary calcs), 12 Warnings, 6 Info, and two files saved to your Downloads folder ready for the translator.

***

## What it does

Systematically inventories every piece of text in a workbook and cross-references it against a locale-fragility pattern table. The output is two files, always: a UTF-8 CSV with a locked schema (location, string, context, severity, translator notes, plus an empty target-string column for the translator to fill in), and a Markdown findings report ranking issues by severity and estimating fix time.

Severity is locked to three tiers by pattern match, not by model judgment. A hard-coded `$` in a format string is always Critical. English-only text inside a calc's string literal is always Warning. That mapping is stable so two sessions scanning the same workbook produce the same report.

## When to use it

- "Localize this dashboard, prep it for translation"
- "Is this workbook ready to ship to our EU customers"
- "Find all the hard-coded English text so we can translate it"
- "Export text for our translator, they'll fill in the target languages"
- "l10n audit before we publish"

## When NOT to use it

- Not for applying translations back to the workbook. This skill is read-only; the translator returns a filled-in CSV and the workbook author applies changes manually in Desktop.
- Not for rewriting a calc to fix a hard-coded format (defer to calc-writer or calc-debugger for the manual fix)
- Not for auditing data-source-level locale settings like server locale or extract collation (use data-scribe)
- Not for testing whether the data itself works in a given region (use data-quality-review)
- Not for recommending which locales to translate to. Strategic question, not a scan.
- Not for bulk-translating strings via an LLM. The CSV goes to a translator; the target column stays empty.

## How to trigger it

- "i18n scan"
- "Localize this dashboard"
- "Localization scan"
- "Translation prep"
- "Find hard-coded text"
- "Is this dashboard ready for global"
- "Export text for translation"
- "l10n audit"
- "Internationalization check"

## What you'll need

- Tableau Studio with the workbook you want scanned already open and connected
- The MCP tools i18n Scanner uses: `list-workbook-datasources`, `list-available-fields`, `list-worksheets`, `list-dashboards`, `get-workbook-inventory`, `get-worksheet-xml`, `Write`
- A save location for the two output files (defaults to your Downloads folder)
- Optional: a target audience note ("EU customers", "Japan"). Affects Critical severity assignment for date-format collisions and currency findings. If unspecified, i18n Scanner defaults to "general international" and applies Critical to any US-specific hard-coding.

## Example walkthrough

**Input:** "Run an i18n scan on this workbook. Target audience is EU customers."

**Output (in chat):**

```
i18n Scanner - Q3 Sales Health.twbx
Scanned 2026-09-11. Target audience: EU customers.

Total strings scanned: 187
  Critical: 4
  Warnings: 12
  Info:     6

Top 3 highest-severity findings:
  Critical - Hard-coded "$" in format string on field
             [Revenue (USD)]. Location: field format.
             Fix: use a locale-aware currency-format alternative,
             or move the currency indicator to a parameter-driven
             label the translator can adjust.
  Critical - MM/DD/YYYY hard-coded in format string on field
             [Order Date]. Location: field format.
             Fix: change to DD/MM/YYYY for EU audience.
  Critical - Region-specific vocabulary in calc [Region Bucket]:
             IF [Region] = "US-East" THEN "Domestic" ELSE
             "International" END. Location: calc formula.
             Fix: this calc silently mislabels every non-US region.
             Rewrite to use a region-agnostic dimension.

Files written:
  Q3_Sales_Health_i18n.csv (187 rows, UTF-8 BOM)
  Q3_Sales_Health_i18n_findings.md (full report + fix order)

Estimated fix time: 3-4 hours.

Next: send the CSV to your translator. They fill in the target_string
column. You apply the calc rewrites and format-string changes manually
in Desktop after translation returns.
```

The findings report on disk includes a Recommended Fix Order section (highest severity first), Translator Handoff Instructions (open in Excel, fill target column, return), and a plain-language summary paragraph safe to paste into Slack.

## What you get back

- **Two output files, always.** `{workbook-name}_i18n.csv` for the translator (UTF-8 with BOM so Excel on Windows opens it with correct multi-byte character rendering) and `{workbook-name}_i18n_findings.md` for the workbook author. Both required. If either write fails, the failure is reported explicitly rather than shipping a partial result.
- **Locked CSV schema.** Columns: `location_type`, `location_ref`, `source_string`, `context`, `severity`, `pattern_matched`, `translator_notes`, `target_string`. The target column is always empty; the translator fills it in.
- **Locked three-tier severity.** Critical (hard-coded currency, region-specific vocabulary in calcs that changes semantics, MM/DD/YYYY on EU dashboards). Warning (English-only text in calc literals, hard-coded separators, region-specific vocabulary in titles, hard-coded time zones, currency abbreviations in aliases). Info (scratch-sheet titles, rarely-visible captions, parameter list-value labels).
- **Recommended fix order** in the findings report, ordered by severity.
- **Translator handoff instructions** in the findings report so the translator knows exactly what to do with the CSV.
- **Mandatory summary paragraph** at the end of every findings report. Safe to paste into Slack.
- **Fix estimate** based on count and severity mix.
- **UNSCANNED section** for any worksheet where `get-worksheet-xml` failed (so tooltip content couldn't be read at fidelity). Never omitted silently.

## Limitations

- **Read-only, always.** Never rewrites calcs, edits format strings, changes aliases, or modifies the workbook in any way. Every fix is a manual step the workbook author performs after translation returns.
- **Does not fill in translations.** The `target_string` CSV column is always empty. A human translator (or a separate translation tool) completes that column.
- **Does not apply translations back.** Even after the translator returns the filled-in CSV, the workbook author does the alias edits, calc rewrites, and format-string updates manually in Desktop.
- **Cannot recommend target locales.** Strategic question, not a scan output.
- **Cannot scan text inside embedded images.** Dashboard image objects with text rendered as pixels are invisible.
- **Cannot read every tooltip at full fidelity when `get-worksheet-xml` fails on that worksheet.** The worksheet is added to UNSCANNED-TOOLTIPS in the findings report and the scan continues with what's readable.
- **One workbook per run.** Each workbook gets its own complete cycle with its own CSV and findings file. No merging.
- **Blank-workbook floor.** Workbooks with fewer than 3 worksheets, no dashboards, and fewer than 10 user-facing strings get declined with a note. Scans on thin content produce noise.
- **UTF-8 BOM only lands reliably on a fresh filename.** Overwriting an existing CSV at the same path can silently keep the old encoding. If a rewrite is needed, i18n Scanner writes to a new filename or asks you to delete the existing file first.

## Troubleshooting

- **"The CSV opens in Excel with garbled characters."** UTF-8 BOM should have prevented this. Check your editor's encoding indicator (Notepad++ bottom-right, VS Code status bar). If the BOM didn't land, the CSV was probably written over an existing file. Delete the old file and re-run, or write to a fresh filename.
- **"A worksheet is in UNSCANNED-TOOLTIPS."** `get-worksheet-xml` returned an error on that sheet (documented platform flakiness on dashboard-bound sheets). Tooltip content couldn't be read at fidelity; other categories on that worksheet were still scanned via `list-available-fields`. Nothing to do unless you specifically need tooltip coverage; if so, re-run the scan later.
- **"It said the workbook is below the Blank-workbook floor."** Fewer than 3 worksheets, no dashboards, and fewer than 10 user-facing strings. i18n Scanner declines these because they produce more noise than signal. Add substantive content or clarify what you're actually auditing.
- **"Zero findings on a workbook I know has hard-coded text."** Confirm the target audience note. Without one, the scanner defaults to "general international" and flags US-specific hard-coding as Critical. If you set the target audience to "US customers," some Critical findings drop to Warning. Also confirm the workbook is actually open and connected.
- **"A calc formula in the CSV has weird quoting."** Formulas containing quotes, commas, or newlines are escaped per RFC 4180 (wrapped in double-quotes, internal quotes doubled). Excel opens this correctly; some naive CSV parsers don't.
- **"The scan hung."** Check Desktop for a blocking modal dialog. i18n Scanner does not retry silently; it waits for you to confirm the modal is dismissed.

## Support

File issues in the same channel you use for other Tableau Studio skill feedback. Include the workbook name, the target audience note, the finding you disagreed with (or the finding you expected but didn't see), and the exact string and location.
