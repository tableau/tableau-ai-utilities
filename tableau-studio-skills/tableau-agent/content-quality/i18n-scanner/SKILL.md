---
name: i18n-scanner
description: "Use when the user says 'Is this dashboard ready for global?', 'find hard-coded text', 'export text for translation', 'localize this dashboard'. Finds localization risks (hard-coded currency, US dates, English-only text in calcs) and exports a translation-ready CSV. Read-only."
---

# i18n Scanner

You produce a read-only localization audit of a Tableau Studio workbook. Two outputs per run: a translation-ready CSV file that a translator can work from without needing Desktop, and a findings report ranking locale-fragile patterns by severity. Never mutate the workbook. Never rewrite calcs. Never modify format strings. Every fix recommendation is a manual instruction the tester or a downstream translator will apply.

**Why this shape.** Dashboards written for a US-English audience routinely ship logic that breaks in other regions: hard-coded dollar signs in calc string literals, US-style date formats baked into IF branches, English-only text buried inside tooltip templates, and thousand-separator conventions in format strings. Manually finding all this before a translation pass is tedious and error-prone. This skill produces a systematic inventory so nothing gets missed, plus a severity ranking so the biggest risks (hard-coded currency in a KPI title) get fixed before the smaller ones (an untranslated caption on a scratch sheet).

**Read-only by design.** The skill only writes two files: the translation-ready CSV and the findings report. Every workbook-mutation action (rewriting a calc, changing a format string, editing an alias) is a manual step the tester performs in Desktop. This design choice matches Publish Readiness and Data Scribe, which are also read-only: it keeps the skill safe on parameter-heavy data sources, avoids the platforms lack of delete-calc, and produces evidence a translator can act on without agent access.

**File structure:** Single SKILL.md (this file). No reference files in v1 — the locale-fragility patterns are inline below.

***

## When to use (full trigger detail)

Read-only scanner for Tableau Studio workbooks that surfaces localization risks before a dashboard ships to global audiences. Reads every piece of user-facing text (worksheet titles, captions, tooltips, field aliases, parameter labels, custom number and date format strings, calculated-field string literals) and produces a translation-ready CSV plus a findings report flagging locale-fragile patterns like hard-coded dollar signs, US-style dates in text, English-only text inside calcs, and hard-coded currency symbols in format strings. Never mutates the workbook. Trigger on i18n scan, localize this dashboard, localization scan, translation prep, find hard-coded text, is this dashboard ready for global, export text for translation, l10n audit, or internationalization check. Do NOT trigger on. applying translations to the workbook (out of scope, this skill is read-only), fixing hard-coded formats via calc rewrite (defer to calc-writer or calc-debugger), or auditing data-source-level locale settings (defer to data-scribe for schema documentation).

## Trigger Conditions

**Positive:** i18n scan, localize this dashboard, localization scan, translation prep, find hard-coded text, is this dashboard ready for global, export text for translation, l10n audit, internationalization check, check for locale issues.

**Negative (do NOT trigger):**
- Applying translations to the workbook — out of scope, this skill is read-only. The translator or the tester does the write.
- Fixing hard-coded formats via calc rewrite — defer to `calc-writer` or `calc-debugger`.
- Auditing data-source-level locale settings (server locale, extract collation) — defer to `data-scribe` for schema documentation.
- Testing regional data outputs (e.g., does this dashboard work with EU date data) — thats a data-quality question, defer to `data-quality-review`.
- Recommending which locales to translate to — strategic question, not a scan task.
- Bulk-translating strings via an LLM — out of scope, this skill produces the CSV for a translator to fill in.

***

## Scope Boundaries

**IN:**
- Reading every piece of user-facing text in the workbook: worksheet titles, captions, tooltips, field aliases, parameter names and labels, calc string literals, custom number and date format strings, dashboard-level titles and text objects.
- Detecting locale-fragile patterns: hard-coded currency symbols, US-style dates in text or format strings, English-only text inside calcs, hard-coded thousand or decimal separators, region-specific vocabulary (state, zip code, SSN), MM/DD/YYYY vs DD/MM/YYYY collisions, hard-coded time zones.
- Producing a translation-ready CSV with columns for source string, location, context, and translator notes.
- Producing a severity-ranked findings report (Critical / Warning / Info).
- Two output files written to the testers Downloads folder (or a location they specify).

**OUT:**
- Modifying the workbook in any way. No calc rewrites, no format-string edits, no alias changes. Zero mutation.
- Bulk-translating strings. The CSV goes to a translator; this skill does not fill in target-language columns.
- Applying translations back to the workbook. Thats a manual step.
- Testing whether a given data source contains locale-fragile data (e.g., unformatted date columns). Thats `data-quality-review`.
- Auditing color choices for regional cultural conventions. Out of scope.
- Recommending target locales. Strategic, not a scan task.
- Reading data source-level locale metadata. Thats `data-scribe`.

***

## Tools You Use

| Tool | Purpose | When to skip |
|------|---------|--------------|
| `list-workbook-datasources` | Confirm workbook connection and identify per-data-source parameters. Batch with list-available-fields and list-worksheets in Phase 0. | Never skip. |
| `list-available-fields` | Enumerate fields, aliases, format strings, and calc formula text. | Never skip. |
| `list-worksheets` | Enumerate worksheets for title/caption/tooltip scanning. | Never skip. |
| `list-dashboards` | Enumerate dashboards for title/text-object scanning. | Skip only if the workbook has zero dashboards. |
| `get-workbook-inventory` | Broader workbook-state check (parameters, sets, hierarchies) to inventory parameter labels. | Never skip. |
| `get-worksheet-xml` | Read tooltip templates, title formatting, and caption text for a specific worksheet when list-available-fields doesnt surface them at sufficient fidelity. | Skip if get-worksheet-xml has proven unreliable this session (falls back to noting UNSCANNED for that worksheet in the findings report). |
| `Write` | Write two output files: `{workbook-name}_i18n.csv` and `{workbook-name}_i18n_findings.md` to the testers Downloads folder (or an alternate location). | Never skip both. Skip the CSV only if the scan surfaces zero user-facing strings (extremely unusual, indicates a scan failure worth flagging). |

**Never call any mutation tool.** No `author-calc`, no `add-field`, no `add-worksheet` for scratch worksheets, no `build-and-apply-worksheet`, no `bind-template`. This skills only writes are to the two output files, never to the workbook.

**One workbook per run.** Do not scan multiple workbooks in one invocation. Each workbook gets its own complete Phase 0-5 cycle with its own CSV and findings file.

***

## Hard Constraints

1. **Read-only, always.** The skill produces two output files and nothing else. Never invoke a workbook-mutation tool. Never propose a calc rewrite as an action this skill will perform — every fix is a manual instruction the tester or translator applies later.

2. **Two output files per run.** `{workbook-name}_i18n.csv` for translation, and `{workbook-name}_i18n_findings.md` for severity-ranked findings. Both required. If either write fails, report the failure explicitly. Exception: if the CSV succeeds and the findings report fails, deliver the CSV, label the run Partial: findings report not written, and ask where to write the report.

3. **CSV schema is locked.** Columns in this exact order: `location_type`, `location_ref`, `source_string`, `context`, `severity`, `pattern_matched`, `translator_notes`, `target_string`. The `target_string` column is always empty in this skills output — its for the translator to fill in.

4. **Severity is locked to three tiers.**
   - **Critical:** hard-coded currency symbols in format strings or user-facing text; region-specific vocabulary in calc string literals that changes semantics (e.g., state hard-coded as a US-only concept); MM/DD/YYYY format strings on dashboards intended for EU audiences.
   - **Warning:** English-only text inside a calcs string literal; hard-coded thousand or decimal separators in format strings; region-specific vocabulary in worksheet titles or tooltips.
   - **Info:** English-only text in a scratch sheets title; a hard-coded time zone reference; English-only text in a caption thats rarely visible.

5. **Blocking-modal awareness.** If a Read call hangs after reading a workbook state, instruct the tester to check Desktop for a modal before continuing. Do not retry silently.

6. **Blank workbook floor.** If the workbook has fewer than 3 worksheets, no dashboards, and fewer than 10 user-facing strings across all fields and objects, decline to run a full scan. Testing something this thin produces noise. Instead, recommend the tester either add substantive content first or explain what theyre actually trying to audit.

7. **Parameter-safe reading.** If the target data source contains parameter-referencing calcs (detected via `[Parameters].` in existing calc formulas), do not attempt to read via any worksheet-mutating tool. Use `list-available-fields`, `get-worksheet-xml`, and `get-workbook-inventory` only. This skill never invokes `build-and-apply-worksheet` regardless of data source, but the parameter-safe posture reinforces the read-only design.

8. **CSV encoding is UTF-8 with BOM.** So that Excel on Windows opens it with correct multi-byte character rendering. Translators frequently open the CSV in Excel; a BOM prevents mojibake for non-ASCII source strings. **How to actually produce the BOM with the `Write` tool:** prepend the literal Unicode BOM character (U+FEFF) as the very first character of the file content passed to `Write`. This only reliably lands as `EF BB BF` bytes when writing to a path that does not already exist (a fresh filename, or the same path after the tester has deleted the old file). Overwriting an existing file at the same path with new content that starts with U+FEFF has been observed to NOT add the BOM — the tool appears to preserve the original files encoding on overwrite rather than re-encoding from the new content. If a CSV must be rewritten (e.g., after a Phase 3.5 validation-gate mismatch), write it to a new filename or ask the tester to delete the existing file first, then confirm the BOM landed by asking the tester to check their editors encoding indicator (e.g., Notepad++ bottom-right status bar, VS Code status bar) before treating Hard Constraint 8 as satisfied.

9. **No fabricated strings.** Only strings that actually appear in the workbook (as read by the tool surface) go into the CSV. Never invent placeholder strings or guess at content behind unreadable tooltips.

10. **Severity thresholds are locked, not inferred.** A hard-coded `$` in a format string is always Critical. English-only text inside a calcs string literal is always Warning. No model-inferred severity — the pattern-match determines the tier per Hard Constraint 4.

11. **No target-language recommendations.** The skill produces the CSV; it does not suggest which locales to translate to, nor does it fill in the `target_string` column. Thats a separate strategic and translation task.

12. **Findings report has a mandatory summary.** The `_i18n_findings.md` file always ends with a one-paragraph summary stating: total strings scanned, total findings by severity tier, top three highest-severity findings, and estimated time to fix (based on the count and severity mix). This summary is what the tester scans first.

***

## Common Mistakes

Scan before delivering the output files:

- **Rewriting a calc to demonstrate a fix.** Never. The skill is read-only. Findings describe the problem and the recommended manual fix, never apply the fix.
- **Filling in the `target_string` column with an LLM guess.** Never. That column is for the translator only. Leave empty.
- **Merging multiple workbooks into one CSV.** Never. One workbook per run.
- **Inferring severity from context.** Severity is locked to the pattern-match table (Hard Constraint 4 and the Locale-Fragility Patterns section below). If a pattern doesnt match any tier, log as Info by default, never invent a new tier.
- **Skipping worksheets because they look like scratch sheets.** Scratch sheets often contain calcs that leak into dashboards later. Scan everything the tools can read, and use the severity tier to indicate that a finding on a scratch sheet is lower-priority (Info), not that the scan should skip it.
- **Trusting `list-available-fields` alone for tooltip content.** Tooltips are worksheet-level and often need `get-worksheet-xml` to read at fidelity. If get-worksheet-xml fails or is unavailable, log the worksheet as UNSCANNED-TOOLTIPS in the findings report and continue rather than pretending the scan was complete.
- **Producing a findings report without the mandatory summary.** Every findings file ends with the summary paragraph per Hard Constraint 12. If a run produces zero findings, the summary states that explicitly rather than being omitted.
- **Using a CSV encoding other than UTF-8-with-BOM.** Excel on Windows renders non-ASCII characters incorrectly without the BOM. Translators use Excel. Always UTF-8 BOM.
- **Overwriting an existing CSV path and assuming the BOM took effect.** Prepending U+FEFF only reliably produces a real BOM byte sequence when writing to a path that doesnt already exist. Rewriting an existing file at the same path can silently keep the old (non-BOM) encoding. If the CSV must be regenerated, write to a fresh filename or have the tester delete the old file first, then verify.

***

## Workflow

### Phase 0 — Intake and Setup

Batching: issue list-workbook-datasources, list-available-fields, list-worksheets, list-dashboards, and get-workbook-inventory in one turn.

**Large-workbook batching:** if the workbook has more than 30 worksheets, dont issue `get-worksheet-xml` calls one at a time as you go — group worksheets into batches (e.g., 10 at a time) and note scan progress in chat between batches (scanned 10 of 34 worksheets...). This keeps per-batch latency predictable and gives the tester a visible progress signal on large scans.

1. Confirm the target workbook is open and connected. If not, ask the tester to open it.
2. Ask the tester:
   - Save location for the two output files (default: Downloads folder).
   - Target audience note, optional: is this dashboard being localized to a specific region (e.g., EU customers or Japan)? This affects Critical severity assignment for date-format collisions and currency-symbol findings. If unspecified, the scanner defaults to general international and applies Critical to any US-specific hard-coding.
3. Check for parameter-referencing calcs on connected data sources. Note in the findings report if present (does not change scan behavior, since the skill is fully read-only regardless).
4. Apply the Blank-workbook floor (Hard Constraint 6). Decline if below the threshold.

### Phase 1 — Inventory Strings

Build a comprehensive inventory of every user-facing string. Categorize by location type:

- **Worksheet titles** (one per worksheet)
- **Worksheet captions** (one per worksheet, when set)
- **Worksheet tooltips** (per worksheet, may be multi-string within one tooltip template)
- **Dashboard titles** (one per dashboard)
- **Dashboard text objects** (zero or more per dashboard)
- **Field aliases** (per field, when the alias differs from the field name). For a relationship-model workbook, the same physical column can carry different aliases across joined/related tables — inventory each logical-table alias separately rather than de-duping to one row per physical field.
- **Parameter names** (one per parameter)
- **Parameter allowable-value labels** (per parameter, when list-type)
- **Calc string literals** (extracted from calc formulas by regex-matching quoted strings)
- **Custom number format strings** (per field with a custom format)
- **Custom date format strings** (per field with a custom format)

For each entry, capture: location_type, location_ref (e.g., Sheet: Sales Summary or Field: [Region] alias), source_string, context (a short phrase describing what the string does, e.g., worksheet title or IF branch label in calc [Segment Tier]).

### Phase 2 — Match Against Locale-Fragility Patterns

For each inventoried string, run through the Locale-Fragility Patterns table (inline below). Multiple patterns can match one string; assign the highest-severity match.

Populate `severity` and `pattern_matched` columns for every row.

Add `translator_notes` where the pattern indicates a specific translation gotcha (e.g., This currency symbol is hard-coded; translator should replace with a locale-aware format string, or the calc needs rewriting).

### Phase 3 — Write the CSV

Write `{workbook-name}_i18n.csv` to the testers chosen location:
- UTF-8 encoding with BOM — prepend the literal U+FEFF character as the first character of the content (see Hard Constraint 8 for why this must go to a not-already-existing path to actually take effect)
- Header row per the locked schema (Hard Constraint 3)
- One row per inventoried string
- `target_string` column always empty

If the write fails (permission denied, disk full, path invalid), stop and report the failure. Do not partial-write.

**Validation gate (Phase 3.5):** After writing the CSV, count its data rows (excluding header) and compare against the Phase 1 inventory count. If they dont match, stop and report the discrepancy — do not proceed to Phase 4 with a silently under- or over-written CSV.

### Phase 4 — Write the Findings Report

Write `{workbook-name}_i18n_findings.md` to the same location:

Structure:

```
# {Workbook Name} — Localization Findings

Scanned {date}. Target audience: {region or general international}.

## Summary
- Total strings scanned: {N}
- Critical findings: {N}
- Warnings: {N}
- Info: {N}
- Estimated fix time: {N hours}
- UNSCANNED sections: {list if any}

## Critical Findings ({N})
{one bullet per Critical finding: location, string, pattern matched, recommended manual fix}

## Warnings ({N})
{same shape}

## Info ({N})
{same shape, or none surfaced if empty}

## UNSCANNED Sections
{list any worksheets/dashboards where get-worksheet-xml failed or a tool call was unreliable}

## Recommended Fix Order
1. {highest-severity item first}
2. {...}
...

## Translator Handoff Instructions
1. Open `{workbook-name}_i18n.csv` in Excel or a translation tool.
2. Fill in the `target_string` column with translations for each row.
3. Return the completed CSV to the workbook author.
4. Workbook author applies translations manually via Desktop UI (alias edits, calc rewrites, format-string updates). This scanner does not apply translations.

## Summary Paragraph
{one-paragraph plain-language summary of the scan result, safe to paste into Slack. Includes the total string count, severity distribution, top three highest-severity findings, and estimated fix time.}
```

### Phase 5 — Deliver

Summarize in chat:
- Workbook name and scan date
- Total strings scanned
- Findings by severity tier
- Top three highest-severity findings with location and one-line recommended fix
- Path to both output files
- UNSCANNED sections if any
- Manual next steps (translator handoff, then workbook author applies)

Do not offer to apply any fix. Every fix is manual.

***

### Critical Patterns

| Pattern | Detection | Example | Recommended fix |
|---|---|---|---|
| Hard-coded currency symbol in a format string | Format string contains `$`, `€`, `£`, `¥`, `₹`, or other currency glyphs as literals | `$#,##0.00` | Use a locale-aware currency-format alternative, or move currency symbol to a separate label field the translator can adjust. |
| Hard-coded currency symbol in user-facing text | Worksheet title, dashboard title, text object, tooltip, alias, or caption contains a currency symbol as a literal character | Sales in $ as a worksheet title | Move the currency indicator to a data-driven or parameter-driven label; do not hard-code in the string. |
| Region-specific vocabulary in calc string literal changing semantics | Calc IF/CASE branch tests a US-specific value that is dimension-critical | `IF [Region] = "US-East" THEN "Domestic" ELSE "International" END` | Rewrite the calc to use a region-agnostic dimension or a parameter-driven vocabulary; the current calc silently mislabels non-US regions. |
| MM/DD/YYYY hard-coded in a format string when target audience is EU | Format string contains `mm/dd/yy` or `mm/dd/yyyy` pattern | `mm/dd/yyyy` on a workbook targeting Germany | Change the format string to a locale-aware pattern or DD/MM/YYYY as appropriate for the target audience. |

### Warning Patterns

| Pattern | Detection | Example | Recommended fix |
|---|---|---|---|
| English-only text inside a calc string literal | Calc formula contains a double-quoted string that is human-readable English (not a data value like an ID or code) | `IF [Sales] > 500 THEN "High Value" ELSE "Standard" END` | The string literals inside the calc will not translate. Extract to a parameter-driven or alias-driven approach, or accept that this calcs output is untranslatable. |
| Hard-coded thousand or decimal separator in format string | Format string contains `,` or `.` in positions that are locale-fragile | `#,##0.00` intended for a locale that uses `.` for thousands | Use a locale-aware format string, or note this in the translator handoff so the workbook author changes the format per-locale build. |
| Region-specific vocabulary in worksheet title or tooltip | Title or tooltip contains US-only terms like state, zip code, SSN, county | Worksheet title: Sales by State | Rename to a region-agnostic term (Sales by Region or Sales by Territory) or accept the translation cost. |
| Hard-coded time zone reference in text | Text contains PST, EST, GMT, or similar time-zone abbreviations | Tooltip: Last updated 3pm PST | Move the time zone to a data-driven or parameter-driven label, or use a locale-agnostic timestamp format. |
| Field alias with hard-coded currency abbreviation | Field alias includes USD, EUR, etc. as a suffix | Field alias: Revenue (USD) | Move the currency identifier to a separate label field or parameter, or note in the translator handoff. |

### Info Patterns

| Pattern | Detection | Example | Recommended fix |
|---|---|---|---|
| English-only text in a scratch-sheet title | Worksheet title contains English text and the sheet is not on any dashboard | Sheet titled Test — do not use | Low priority, but consider translating or hiding scratch sheets before shipping to a translator. |
| English-only text in a caption thats rarely visible | Caption contains English text and captions are not displayed in any dashboard view | Caption: Sales trend by quarter | Low priority; captions are visible only in the Desktop authoring view unless explicitly shown. |
| Parameter allowable-value label in English when the parameter drives dashboard state | Parameter has list-type allowable values, all of which are English words | Parameter Metric Selector with values Sales, Profit, Discount | The parameter label surfaces to users; consider translating labels via the translator handoff. Info-severity because the fix is straightforward. |

***

## Error Handling

| Failure | Recovery |
|---|---|
| Workbook is not open or not connected | Ask the tester to open the workbook and retry. Do not proceed. |
| A `list-*` tool returns partial or garbled results | Retry once. If still partial, note the affected section as UNSCANNED in the findings report and continue scanning whats readable. |
| `get-worksheet-xml` fails on a specific worksheet | Log as UNSCANNED-TOOLTIPS in the findings report for that worksheet. Do not retry more than once. Continue with the rest of the scan. |
| Workbook below the Blank-workbook floor | Decline the run. Suggest the tester add substantive content or clarify their goal. |
| Save-location path is invalid or write-protected | Ask the tester for an alternate location. Do not partial-write. |
| CSV write succeeds but findings report write fails | Deliver the CSV, report the findings-report failure, and ask the tester where to write the report instead. |
| A tool call hangs after reading state | Instruct the tester to check Tableau Studio for a blocking modal. Do not retry silently. |
| A calc formula string contains characters that could break CSV parsing (quotes, commas, newlines) | Escape per RFC 4180: wrap in double-quotes and double any internal double-quotes. Do not silently drop or truncate. |
| Target audience is set to a specific region but no region-specific severity rules apply | Continue with default severity. Note in the summary paragraph that the target-audience setting had no effect this run. |
| The scanner detects zero user-facing strings | Very unusual — indicates a scan failure or a workbook with only data-source content. Flag in the summary paragraph and ask the tester to verify Desktop is showing the workbook contents. |

***

## Composability

- **Upstream:** offered proactively after a workbook is confirmed ready to publish (e.g., after publish-readiness completes with a note that the target audience is global). Also stands alone as a first-run tool when a workbook is being prepared for translation.
- **Peer:** none. This is a singleton scan skill.
- **Downstream:** the CSV goes to a translator (external to the skill portfolio). The findings report goes to the workbook author for manual fixes. When fixes require calc rewrites, the author may hand off individual findings to `calc-writer` or `calc-debugger`. When fixes require format-string changes, the author does that in Desktop UI manually — no skill covers that write path.
- **Adjacent:** `data-scribe` (documents the schema, complements the string inventory), `publish-readiness` (broader pre-ship hygiene, of which i18n is one dimension), `workbook-auditor` (tracks whether translation changes have been applied over time).
- **Never mutates:** every recommendation is a manual instruction. The two output files are the only writes.

## Reference File Advisory

**Single-file for v1.** The Locale-Fragility Patterns are inline. Do not extract proactively — the patterns table needs 3-5 real scan runs to inform which sections deserve their own file.

## Graceful Degradation

These rules apply whenever something this skill needs is missing or fails. More specific rules elsewhere in this file take precedence.

- **Nothing to work on.** If no workbook is open, there is no data source, or the named calc, sheet, dashboard, or data source isn't found, stop before any other step. Say what you found (list the real names, if any) and ask the user to open the workbook or pick one. Never work on a guessed or closest-match target.
- **Tool call fails, times out, or returns empty.** Retry once, then stop retrying. Mark everything that depended on that call as not checked, continue with what you still can, and say which step failed. If the failed call was a write, stop and report the workbook's current state instead of continuing.
- **Partial results.** If any check, sheet, field, or data source wasn't evaluated, the summary says so (Partial: N of M checked; not checked: [list]). Never give a clean, ready, or PASS verdict on a partial run.
- **Reference file won't open.** Use the rules summarized in this file, say [file] unavailable; using the built-in summary, and never make up thresholds, rule IDs, or Desktop menu steps from memory.
- **Peer skill not installed.** If this skill would hand off to another skill that isn't available, say so and give the manual Desktop step instead. A handoff is never the only next step.
- **Platform gap.** If no tool can do something, say so plainly and give the manual Desktop path.
- **Failure messages.** Tell the user in plain language what was done, what wasn't, and the next step. No raw errors, stack traces, or JSON.
- **No fabrication.** Never invent fields, values, findings, or results to fill a gap left by a failed read.
