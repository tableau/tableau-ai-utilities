# Dashboard Caption Audit

Audits an open Tableau workbook for missing or default titles and captions across dashboards, worksheets, dashboard text objects, and phone / tablet device-layout variants.

**Example:** Ask for a caption audit on a workbook where half your worksheets still say "Sheet 1" and three dashboards ship with the placeholder `<Sheet Name>` text, and you get back a prioritized eight-rule report with exact locations and manual-fix steps.

## What it does

Scans every dashboard, worksheet, and text object in an open Tableau workbook for title and caption hygiene against an eight-rule completeness catalog. Catches missing titles, missing captions, empty text objects, default names in English / French / Spanish / German, device-layout inheritance duplicates, and placeholder-title text like `<Sheet Name>` that Tableau leaves in when you disable auto-title. Read-only. Every finding is a manual Desktop-fix instruction; you apply the fix. Two-tier delivery: compact chat summary plus opt-in file save.

## When to use it

- "I have a workbook that ships with 'Sheet 1' worksheet titles and I want to catch them before publish"
- "I want to run a monthly QA sweep across a governance library for caption completeness"
- "I'm auditing device-layout variants (phone / tablet) and want to know which ones inherit stale defaults from desktop"
- "I need a prioritized list of caption gaps for a workbook I'm about to hand off"
- "I want to verify a workbook has no placeholder title text before it goes to a stakeholder"

## When NOT to use it

- Not for spellcheck or typography (use `desktop-spellcheck` for text hygiene)
- Not for tooltip content audit (out of scope)
- Not for caption position or sizing sanity (out of scope)
- Not for format-string drift on caption fonts (use `format-drift-scanner`)
- Not for dashboard assembly hygiene like zone alignment or filter-action wiring (use `dashboard-preflight`)
- Not for calc-family metadata audit (use `calc-linter`)

## How to trigger it

- "caption audit"
- "check my titles and captions"
- "audit dashboard captions"
- "dashboard-caption-audit"
- "find missing titles in this workbook"

## What you'll need

- Tableau Studio with the target workbook open
- Every relevant dashboard and worksheet accessible via `get-dashboard-xml` and `get-worksheet-xml`
- A Downloads path or user-specified folder for the optional file output

## Example walkthrough

**Input:** "caption audit" on a workbook with 3 dashboards, 12 worksheets, phone layouts on 2 dashboards

**Tier A chat output:**

```
Caption Audit Summary
Workbook: SalesReview_Q3.twbx
Dashboards: 3 | Worksheets: 12 | Device layouts: 2 phone
Findings: 7 Warning, 3 Info

TL;DR (top 3 Warnings):
1. Dashboard "Executive Overview" phone layout inherits default "Sheet 1" title
   from desktop but desktop title was manually set to "Q3 Sales Rollup"
   (DC-DEVICE-07)
2. Worksheet "Untitled" retains default name across 4 dashboard placements
   (DC-DEFAULT-NAME-06)
3. Dashboard "Regional Detail" title reads "<Sheet Name>" placeholder text
   (DC-TITLE-08)

Full rule breakdown:
- DC-TITLE-01 Dashboard title missing: 0
- DC-CAPTION-02 Dashboard caption missing: 2 (Info)
- DC-WS-TITLE-03 Worksheet title missing: 1 (Warning)
- DC-WS-CAPTION-04 Worksheet caption missing: 1 (Info)
- DC-TEXT-EMPTY-05 Text object empty: 0
- DC-DEFAULT-NAME-06 Default name: 4 (Warning)
- DC-DEVICE-07 Device-layout inheritance duplicate: 1 (Warning)
- DC-TITLE-08 Placeholder title text: 1 (Warning)

Save full report to file?
```

**Tier B (opt-in file output, after path confirmation):** a `.md` document with per-dashboard sections, per-worksheet findings, exact Desktop-fix instructions per rule, and a handoff YAML block for downstream skills.

## What you get back

- Compact chat summary (Tier A): totals, top 3 Warnings sorted deterministically, per-rule breakdown
- Optional full report (Tier B): every finding with exact location and Desktop-fix instruction
- Handoff schema `caption_audit_report/1` for downstream skills (dashboard-preflight, desktop-spellcheck, format-drift-scanner, viz-planner, workbook-auditor)
- Deterministic ordering: same input produces byte-identical top-3 across runs (HC#14 + HC#15)

## Limitations

- One workbook per run. Bulk-workbook runs are refused.
- Locale coverage for default-name detection is English, French, Spanish, and German. Other languages will fall through to non-detection.
- Tooltip content is not audited (use `caption-and-tooltip-advisor` for tooltip rewrites).
- Caption position and sizing are not audited (out of scope).
- Spellcheck of caption text is out of scope (defer to `desktop-spellcheck`).
- Font-family or font-size drift in captions is not detected here (defer to `format-drift-scanner`).

## Troubleshooting

- **"get-worksheet-xml failed on dashboard-bound sheet"** then hits a known reliability gap on dashboard-bound worksheets. Skill emits `"unresolved: xml-read-failed"` per HC#7 and continues. That one sheet's caption findings will be missing; the rest of the audit is intact.
- **"Placeholder title text not caught"** then the placeholder pattern is outside DC-TITLE-08's regex.
- **"Default name not caught in language X"** then the locale isn't in the four-language regex list. English, French, Spanish, German covered.
- **"Save aborted, no path confirmed"** then HC#12 blocked a silent file write. Confirm a Downloads path when prompted.
- **"Same top-3 not identical across runs"** should not happen; V4 gate enforces deterministic ordering. If it does, file a bug with both run outputs.

## Support

File issues in the Tableau Agent Skills repo.
