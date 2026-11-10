# Publish Readiness

Runs a read-only pre-publish hygiene and performance sweep of a Tableau Studio workbook before you push it to Server or Cloud. Produces two clearly separated outputs: tool-verified findings the agent detected directly (unused fields, default sheet names, missing titles, orphaned scratch sheets, performance risks, calc hygiene, naming inconsistency) plus a user-verified reminder checklist for things only a human can check (interactivity, formatting, compliance, post-publish setup).

**Example:** "Am I ready to publish this?" returns 2 Warnings (a dashboard with 12 sheets, COUNTD used on 4 sheets), 5 Notes (default names on 3 sheets, 2 calcs missing comments), and 3 Info items (naming casing drift, live connection, one hidden unused field), plus the manual verification checklist grouped by domain. Closes with "2 Warnings, 5 Notes, 3 Info items. Recommend addressing Warnings before publish."

***

## What it does

The final read-only sweep before a workbook goes live. Every other skill in the portfolio can leave scratch-sheet debris behind on cleanup failure, and default `Sheet 1`/`Sheet 2` names or missing titles are the kind of thing an author stops noticing after a week of edits. This skill catches exactly that class of issue.

Two output sections, always clearly labeled. **Tool-verified findings** cite specific fields, sheets, formulas, or datasources from the inventory tools. **User-verified reminder checklist** groups items the agent structurally cannot inspect (visual formatting, filter action wiring, RLS, export output) by domain so you can run through them manually before publish.

Every finding gets a severity tag: Warning (publish risk), Note (recommended fix), or Info (awareness only). The report closes with a Publish Readiness Score line and a recommendation calibrated to the Warning count.

Never mutates anything. Every finding ends in a "here's where to find it in Desktop" instruction, never an autonomous fix. If you ask Publish Readiness to fix something mid-report, it declines and gives you the exact menu path or location.

## When to use it

- "Am I ready to publish this dashboard"
- "Any cleanup I should do before this goes live"
- "Publish checklist before I send this to Server"
- "Performance check before publish"
- "Last look before I push this to Cloud"

## When NOT to use it

- Not for data quality issues in the underlying data (use data-quality-review)
- Not for what changed since a prior version (use workbook-auditor)
- Not for documenting field meaning (use data-scribe)
- Not for building or editing charts, dashboards, or calcs (use an authoring skill)
- Not for actual publishing, permissions, or Server/Cloud governance. This environment has no Server/Cloud REST API access; Desktop-only.
- Not for verifying filter action wiring, parameter behavior, or Set actions (use interaction-validator)

## How to trigger it

- "Ready to publish"
- "Publish checklist"
- "Am I ready to publish this"
- "Clean this up before I publish"
- "Check before publishing"
- "Anything I should fix before this goes live"
- "Pre-publish check"
- "Publish readiness"
- "Performance check before publish"
- Automatically offered when you say "about to publish," "sending this to the team," "pushing to Server," or "going live"

## What you'll need

- Tableau Studio with the workbook open
- The MCP tools Publish Readiness uses: `get-workbook-inventory`, `list-worksheets`, `list-dashboards`, `list-available-fields` (verbosity: full), `list-workbook-datasources`, `get-worksheet-xml` (skipping dashboard-bound sheets per the known reliability gap)
- For large workbooks (25+ worksheets, 100+ fields, or 10+ dashboards), you'll be asked to scope: full workbook, specific dashboards, or skip a category

## Example walkthrough

**Input:** "Am I ready to publish this?"

**Output (bulleted, never a table):**

```
Publish Readiness Report - Q3 Regional Sales
Scanned 2026-09-11. 4 dashboards, 14 worksheets, 47 fields, 11 calcs.

Tool-Verified Findings (ordered by publish risk)

Performance Risks
  Warning - "Regional Detail" dashboard has 12 sheets. Above the
            11+ threshold. Consider splitting for load performance.
  Warning - [Distinct Customers] uses COUNTD and appears on 4 sheets
            (above the 3+ threshold). COUNTD scales poorly on large
            datasources. Consider a precomputed alternative if the
            underlying source is >1M rows.
  Note    - [Segment Health] calc returns "Good" or "At Risk" as
            strings (binary logic). Convert to Boolean for smaller
            engine footprint.

Missing Titles
  Warning - Dashboard "Q3 Overview" has a blank title. Viewers see
            the tab name only.
  Note    - Worksheet "Regional Bar" has no chart title and appears
            on "Regional Detail" dashboard.

Default / Unclear Names
  Note    - "Sheet 3" appears on the "Executive Summary" dashboard.
            Rename to describe its content.
  Note    - Datasource still named "Sample - Superstore". Rename to
            match the actual source.

Calculation Hygiene
  Note    - [Adjusted Margin] has 3 levels of nested calc references
            ([Adjusted Margin] -> [Margin Rate] -> [Base Margin]).
            Harder to maintain post-publish.
  Note    - [Q3 Cutoff Date] contains hard-coded literal #2024-09-30#.
            Will become stale next quarter.

Orphaned Scratch Sheets
  Note    - "Sheet 5" is on zero dashboards. High-confidence
            candidate (default name + no dashboard membership).
  Info    - "DQ Check: Nulls" is on zero dashboards. Medium-
            confidence candidate (name matches scratch pattern).

Naming Consistency
  Info    - 4 calcs use "Rev" abbreviation, 3 use "Revenue" spelled
            out. Consider standardizing.

Unused / Hidden Fields
  Info    - [Legacy Region Code] is hidden and unused. Safe to leave
            or clean up.

Items for Manual Verification (agent cannot inspect these)

Interactivity
  [ ] Filter actions work as designed
  [ ] Parameters and Sets function as expected when changed
  [ ] "Only Relevant Values" is set intentionally
  [ ] "Show Apply Button" enabled on multi-select filters
  [ ] Context filters set where needed for LOD calcs
  [ ] Logical model not excluding data unintentionally

Style & Formatting
  [ ] Instructions, metric definitions, and helper text included
  [ ] Extra borders and grid lines removed
  [ ] Color use is thoughtful, consistent, and accessible
  [ ] Tooltips formatted; "Command" options removed
  [ ] Font hierarchy is clear and consistent
  [ ] Measures formatted appropriately (currency, percentages)

Usability
  [ ] Views render in <5 seconds (use Performance Recorder if slow)
  [ ] Dashboard sizing compatible with common screen sizes
  [ ] Export to PDF/PPT/Excel works if required

Compliance
  [ ] Row Level Security configured if needed
  [ ] Workbook permissions model set appropriately
  [ ] Branding applied per organizational standards
  [ ] Confidentiality statements included if required

Post-Publish
  [ ] Refresh schedule configured (extract) or Data Freshness
      Policy set (live)
  [ ] Datasource description added on Server/Cloud
  [ ] Lens(es) created if applicable
  [ ] Entry criteria and use cases documented
  [ ] Embedded credentials verified

Publish Readiness Score
  2 Warnings, 5 Notes, 3 Info items. Recommend addressing Warnings
  before publish.

Want to re-run after cleanup?
```

## What you get back

- **Two clearly separated sections:** tool-verified findings (agent inspected) and user-verified reminder checklist (agent cannot inspect). The report never claims to have verified something it structurally cannot see.
- **7 tool-verified categories:** Unused/Hidden Fields, Default/Unclear Names, Missing Titles, Orphaned Scratch Sheets (with High/Medium/Low confidence tiers), Performance Risks, Calculation Hygiene, Naming Consistency.
- **Severity per finding:** Warning (publish risk), Note (recommended fix), Info (awareness only).
- **Publish Readiness Score line** at the end: "[N] Warnings, [N] Notes, [N] Info items. [Recommendation]." Recommendations calibrated to Warning count (0 = ready; 1-2 = recommend addressing; 3+ = strongly recommend, consider splitting complex dashboards).
- **Ordered by publish risk** in the report: Performance first (highest impact post-publish), then Missing Titles (most visible to viewers), through Unused/Hidden Fields (least visible, lowest urgency).
- **Context leverage.** If a `data-quality-review` report exists in the conversation, Publish Readiness skips Category 1 (Unused/Hidden Fields) and references it. If a `workbook-auditor` change digest exists, Publish Readiness cross-references recently-changed sheets/calcs so a freshly-added uncommented calc is prioritized differently than a stale one.
- **Bulleted, never tabular.** Findings render as bullets grouped by category; chat surfaces render tables unreliably.
- **User-verified reminder checklist** grouped by Interactivity, Style & Formatting, Usability, Compliance, and Post-Publish.

## Limitations

- **Cannot see visuals.** No screenshot capability. Everything visual (colors, fonts, layout, dashboard sizing, container structure, tooltip formatting) goes into the manual verification checklist.
- **Cannot inspect filter configuration.** "Only Relevant Values," "Show Apply Button," context filter status, filter action scope, parameter action wiring — none are readable from the tool surface. All go into the manual checklist.
- **Cannot time queries.** Performance findings are risk-pattern signals, not measured diagnoses. Always recommends Performance Recorder for precise timing.
- **Cannot check Server or Cloud settings.** RLS, permissions, refresh schedules, embedded credentials — all Server/Cloud-side, all in the manual checklist.
- **Cannot delete or rename anything.** Every finding ends in "here's where to find it in Desktop." No `delete-sheet`, no `rename-sheet`, no `author-calc`.
- **Scratch-sheet detection is heuristic.** Naming patterns (`Sheet 1`, `scratch`, `temp`, `test`, `v2`, `DQ Check`) plus zero dashboard membership. Confidence tier (High/Medium/Low) is stated on every candidate. Never recommends outright deletion.
- **Dashboard-bound sheets skipped for shelf-content checks** (known `get-worksheet-xml` 500 reliability gap). Publish Readiness notes "not checked" for affected sheets rather than assuming unused.
- **Sets are invisible to the tools.** Any Set-related finding is out of scope; the manual checklist prompts you to verify Set behavior manually.

## Troubleshooting

- **"It said COUNTD is a Warning but I need distinct counts."** Warning ≠ don't do it. Warning means it's a publish risk to be aware of. If COUNTD is required for your metric, the recommendation is precomputing where possible, not eliminating the calc.
- **"An orphan candidate is actually my archive tab."** Working as designed. Orphans are candidates, not delete recommendations. Confidence tiers help you triage; you decide.
- **"A dashboard-bound sheet was marked 'usage not confirmed'."** `get-worksheet-xml` 500s on those sheets. Publish Readiness never assumes unused when it can't verify usage; it flags the gap and continues.
- **"Publish Readiness declined to delete a sheet I asked it to remove."** Read-only, always. It gave you the exact location in Desktop instead. Delete manually.
- **"I got 0 Warnings but the score line says 'Address Notes at your discretion.'"** Working as designed. 0 Warnings means no publish risks were detected. Notes are cleanup debt you can defer or address.
- **"An early-exit shortcut skipped my checklist."** If Publish Readiness returns zero findings across all 7 categories, it skips straight to the score line ("0 Warnings, 0 Notes, 0 Info items. Looks ready.") rather than presenting empty category headers. Genuinely clean workbook.
- **"It scoped the run without asking me."** For workbooks under 5 worksheets and 20 fields, the scoping gate is skipped (most checks won't surface findings at that scale). For larger workbooks, Publish Readiness asks.

## Support

File issues in the same channel you use for other Tableau Studio skill feedback. Include the workbook shape (sheets, dashboards, fields), the finding you disagreed with (or the finding you expected but didn't see), and the severity Publish Readiness assigned.
