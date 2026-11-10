# Desktop Spellcheck

Reads every stakeholder-visible piece of text in a Tableau workbook (titles, captions, dashboard text, field aliases, calc names, tooltips, annotations, parameter names), runs it against a dictionary plus a user-maintained allow-list, and produces a severity-scored report. Read-only. Never mutates the workbook.

**Example:** "Spellcheck this workbook" returns a summary showing 2 Critical, 1 High, 4 Medium, 0 Low across 12 sheets, with the top findings inline (each with the exact string and location), then offers to write the full 8-section report to your Downloads folder.

***

## What it does

Catches the copy errors everyone stops seeing after staring at a workbook for a week. Misspellings, capitalization drift ("Revenue" vs "revenue" vs "REVENUE" across sheets), curly quotes where straight ones belong, double spaces, trailing whitespace, mixed apostrophe styles.

Severity is fixed by check family, not by how bad something looks. Dictionary misspellings in stakeholder-facing locations are Critical. Capitalization drift is High. Typography and whitespace issues are Medium. Repeated unknown tokens and singular/plural inconsistency are Low. That mapping is locked so two sessions grading the same workbook produce the same report.

Terminology consistency ("Target" vs "Budget", "customer" vs "client") is deliberately out of scope. It produced too many false positives in early design.

## When to use it

- "Proofread this workbook before I publish it"
- "Find typos in this dashboard"
- "Check my copy for consistency"
- "Text review, I've been staring at this for a week"
- "Someone told me there's a typo somewhere, find it"

## When NOT to use it

- Not for calc logic review (use calc-orchestrator)
- Not for field naming discipline at the schema level (use data-quality-review)
- Not for dashboard hygiene beyond text — layout, sizing, formatting (use publish-readiness)
- Not for terminology consistency across a glossary. Deliberately out of scope.
- Not for translation or localization
- Not for published Server or Cloud content. Desktop workbook only.

## How to trigger it

- "Spellcheck this workbook"
- "Check my copy"
- "Find typos in this dashboard"
- "Proofread this workbook"
- "Copy consistency check"
- "Text review before publishing"
- "Desktop-spellcheck"

## What you'll need

- Tableau Studio with the workbook open
- The MCP tools Desktop Spellcheck uses: `get-worksheet-xml`, `list-available-fields`, `list-workbook-datasources`, `get-workbook-inventory`
- `skill-expertise/allow-list.txt`, which ships with the skill and is pre-filled with Tableau, Salesforce, and common business terms. Add your own terms to it. If it's missing, a minimal fallback list is used and a warning is printed.
- **Keep a copy of your added terms before updating the skill.** Installing a new version replaces `skill-expertise/allow-list.txt`; merge your terms back in afterward.
- For dashboard-bound sheets where `get-worksheet-xml` fails, you'll be asked for the `.twb` or `.twbx` file path so the XML can be parsed directly from disk.

## Example walkthrough

**Input:** "Spellcheck this workbook."

**Output (compact summary shown in chat first):**

```
Desktop Spellcheck - Q3 Regional Sales.twbx
Scanned 12 sheets + 3 dashboards. Allow-list: 47 terms loaded.

Findings summary:
  Critical: 2
  High:     1
  Medium:   4
  Low:      0
  Total:    7

Top findings:
  Critical - "recieve" on Dashboard "Executive Summary", text object
             top-right. Suggested: "receive".
  Critical - "seperately" on Worksheet "Segment Detail", worksheet
             title. Suggested: "separately".
  High     - Capitalization drift: "Revenue" appears 34 times,
             "revenue" appears 3 times, "REVENUE" appears 1 time.
             Most common: "Revenue". Flagging the 4 outliers.
  Medium   - Curly quote in tooltip on "Top Customers": "customer's"
             uses U+2019 apostrophe. Prefer straight apostrophe.
  Medium   - Double space in dashboard title "Q3 Regional  Sales".

Not Scanned: none. All sheets scanned.
Allow-list suggestions: "MEDDIC" flagged 6 times.

Want the full findings report as a file? I can write it to your
Downloads folder as .md or .txt.
```

If you confirm, the full 8-section report (Header, Critical, High, Medium, Low, Not Scanned, Allow-list suggestions, Footer) gets written to disk with the file path returned in chat. The full report doesn't also get pasted into chat once it's saved.

## What you get back

- **Severity scoring by check family, not by feel.** Dictionary miss = Critical. Capitalization drift = High. Typography/whitespace = Medium. Repeated unknown tokens = Low. Locked mapping for reproducibility.
- **Every finding cites the exact string and exact location.** No invented findings. If Desktop Spellcheck couldn't verify a finding by re-reading the source XML on a spot check, the report gets rebuilt before delivery.
- **Two-tier extraction.** Tier 1 uses MCP tools. Tier 2 falls back to disk XML parsing when `get-worksheet-xml` fails on a dashboard-bound sheet (documented platform flakiness). Sheets that fail both tiers appear in a "Not Scanned" section, never omitted silently.
- **Early-exit sampling on large workbooks.** For workbooks with more than 40 stakeholder-visible text sources, a fast first pass on the first 5 sheets alphabetically. If it comes back clean, you're asked whether to run the full scan. Prevents 20-minute scans on already-clean workbooks.
- **Allow-list suggestions.** Terms flagged 3+ times get surfaced at the end so you can add them to `skill-expertise/allow-list.txt` for future runs.
- **Post-fix re-scan offer.** After you fix issues in Desktop, Desktop Spellcheck can re-run and produce a delta report (what was fixed, what remains, what new issues appeared). Not automatic; wait for your "I fixed these, check again."
- **Summary first, full report on request.** The 8-section report goes to a file. Chat gets a compact summary with the top 3-5 findings.

## Limitations

- **Cannot check text baked into images.** Dashboard image objects with text rendered as pixels are invisible.
- **Cannot check text in URL actions or Tableau-rendered navigation buttons.**
- **Cannot tell intentional stylized copy from typos.** Product names, deliberate capitalizations, and internal jargon should live in `skill-expertise/allow-list.txt`.
- **Does not check terminology consistency.** "Customer" vs "client" or "sales" vs "revenue" is deliberately out of scope. Adding it back would reduce reproducibility across sessions.
- **Desktop workbooks only.** Cannot scan published Server or Cloud content.
- **Small dictionary variance.** If no local dictionary is available, Desktop Spellcheck falls back to a built-in English word list and notes the fallback in the report header. Some domain terms may not be recognized in the fallback mode.
- **Field descriptions are never in scope**, even implicitly under "tooltips." That's a separate category that would produce noise here.

## Troubleshooting

- **"`get-worksheet-xml` returned a 500 on my dashboard sheet."** Documented platform flakiness. Desktop Spellcheck asks for the `.twb` or `.twbx` file path and parses the XML from disk. If neither works, the sheet goes into "Not Scanned" and the scan continues with what's readable.
- **"It's flagging our product name as a misspelling."** Add it to `skill-expertise/allow-list.txt`, one term per line, case-sensitive. Terms in the allow-list are never flagged under any severity. If it's flagged 3+ times, Desktop Spellcheck will suggest adding it in the report's "Allow-list suggestions" section.
- **"The report is empty but I know there's a typo."** Confirm the category containing the typo is in scope. Field descriptions are never scanned. Text baked into image objects can't be read. If the typo is in a live URL action or navigation button, that also falls outside the scannable surface.
- **"It said the file is missing an allow-list."** Optional. The scan continues with a minimal fallback list and prints a warning. Reinstall the skill to restore `skill-expertise/allow-list.txt`, or recreate it there and add your terms.
- **"The severity looks wrong on this finding."** Severity is fixed by check family, not by judgment. See the mapping in the report footer. If the check family is right and the severity feels too high or too low, that's a design choice for reproducibility.
- **"The report is huge."** By default, only the compact summary goes into chat. The full report goes to a file. If you asked to see it in chat instead, it renders as plain text (not markdown) because the chat panel doesn't render markdown syntax.

## Support

File issues in the same channel you use for other Tableau Studio skill feedback. Include the workbook name, the finding you disagreed with (or the finding you expected but didn't see), the exact string, and the location.
