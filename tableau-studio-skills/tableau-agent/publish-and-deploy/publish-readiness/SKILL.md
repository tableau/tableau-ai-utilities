---
name: publish-readiness
description: "Use when the user says 'Am I ready to publish?', 'pre-publish check', 'clean this up before I publish', 'anything to fix before this goes live?' Runs a pre-publish checklist: unused fields, default names, missing titles, scratch sheets, performance risks, and calc hygiene. Read-only."
---

# Publish Readiness

You run a read-only hygiene and performance checklist against a workbook before a human publishes it to Server or Cloud. This covers workbook housekeeping (leftover debris, unclear naming), performance risks (mark count, slow calcs, filter overhead), calculation hygiene, and a reminder checklist of items only a human can verify (interactivity, formatting, compliance).

**Why this shape:** every other skill in this portfolio is honest that it can leave scratch-sheet debris behind on cleanup failure, and default Sheet 1/2/3 names or missing titles are the kind of thing an author stops noticing after enough edits. A dedicated last-look pass catches exactly the class of issue thats invisible to the person whos been staring at the workbook all day. The performance and calculation checks catch the works on my machine issues that only become painful after publish at scale.

***

## When to use (full trigger detail)

Run a read-only pre-publish checklist on a Tableau Studio workbook before it goes to Server/Cloud. Checks. unused/hidden fields, default worksheet names (Sheet 1/2/3), missing worksheet/dashboard titles, orphaned scratch sheets, performance concerns (mark count, COUNTD, filter configuration, dashboard sheet count), calculation hygiene, and naming consistency. Also provides a user-verified reminder checklist for items the agent cannot inspect (interactivity, formatting, compliance, documentation). Trigger on ready to publish, publish checklist, am I ready to publish this, clean this up before I publish, check before publishing, anything I should fix before this goes live, pre-publish check, publish readiness, performance check before publish. Do NOT trigger for. data quality issues in the underlying data (defer to data-quality-review), what changed since a prior version (defer to workbook-auditor), documenting field meaning (defer to data-scribe), building or editing charts/dashboards/calcs (defer to an authoring skill), actual publishing/permissions/Server-side governance (out of scope — this environment has no Server/Cloud REST API access, Desktop-only). This skill never publishes anything itself — it only reports what a human should clean up first.

## Desktop Agent Limitations (Read This First)

The Tableau Studio agent operates under significant tool-surface constraints. See `skill-expertise/agent_limitations.md` for the full inventory (5 categories, 20+ confirmed gaps). This skill is designed around what the agent CAN and CANNOT do.

**What the agent CAN do (tool-verified checks):**
- Read field inventory, types, formulas, and metadata (`list-available-fields`)
- Read workbook structure: sheets, dashboards, datasources (`get-workbook-inventory`, `list-worksheets`, `list-dashboards`)
- Read shelf contents on non-dashboard-bound sheets (`get-worksheet-xml`, but this 500s on dashboard-bound sheets)
- Cross-reference field usage across sheets
- Detect formula patterns (COUNTD, string operations, LOD, nested dependencies, hard-coded dates)
- Count sheets per dashboard
- Identify naming patterns and defaults
- Detect connection type (live vs. extract)

**What the agent CANNOT do (confirmed platform gaps):**
- See rendered visuals, formatting, colors, fonts, or layout (no screenshot capability)
- Trigger or test filter actions, parameter changes, or set actions (no mark-selection command; author-parameter crashes with `spawn ps ENOENT`)
- Inspect filter configuration (scope, Only Relevant Values, Show Apply Button, context filter status)
- Read dashboard container structure, zone placement, or canvas size
- Inspect tooltip formatting or Command button settings
- Read action configuration (which sheets targeted, which fields mapped)
- Verify export formatting (PDF, PPT, Excel)
- Check row-level security, permissions, or Server/Cloud settings
- Time rendering performance or run Performance Recorder
- Delete fields, calcs, sheets, or rename anything (no delete command exists)
- Detect or interact with Sets reliably (invisible to field-resolution tools)
- Suppress blocking modal dialogs that appear during operations (cosmetic but disruptive; user must dismiss)

**Implication:** This skill produces two distinct outputs: (1) tool-verified findings the agent detected directly, and (2) a user-verified reminder checklist of items the human must check manually. These are clearly separated in the report. The agent never claims to have verified something it structurally cannot inspect.

**Storyboard scope:** Storyboards are checked for titles only. Sheet-level checks (performance, calcs, naming) apply to worksheets; storyboard-specific checks are out of scope.

**This skill does not check:** tooltip content, axis formatting, color encoding, dashboard sizing, container structure, font choices, export output, or any Server/Cloud-side configuration.

***

## File Structure

| File | Purpose |
|------|---------|
| SKILL.md | Workflow, constraints, checklist logic, error handling |
| skill-expertise/performance_checks.md | Performance-specific detection logic, thresholds, and reporting templates |
| skill-expertise/publishing_checklist.md | Complete publishing checklist with detectability status for every item |
| skill-expertise/agent_limitations.md | Full inventory of confirmed Desktop agent platform gaps (5 categories, 20+ items) |

***

## Tools You Use

| Tool | Purpose |
|------|---------|
| `get-workbook-inventory` | Sheets, dashboards, storyboards, titles, workbook file location, datasource list |
| `list-worksheets` / `list-dashboards` | Name lists for naming-convention checks and dashboard sheet counts |
| `list-available-fields` (verbosity: full) | Field inventory for unused-field, formula analysis, and performance checks |
| `list-workbook-datasources` | Datasource names, connection types (live vs. extract) |
| `get-worksheet-xml` | Per-sheet shelf contents for mark-count estimation. Avoid on dashboard-bound sheets (known 500/`operation-failed` reliability gap). Fall back to usage inference if unavailable, and note not checked for affected sheets. |

This skill calls no mutating tool. It reports; it never fixes, deletes, or renames anything itself.

**Batching rule:** call `get-workbook-inventory`, `list-worksheets`, `list-dashboards`, `list-available-fields`, and `list-workbook-datasources` exactly once, at the start of the workflow (Step 1). Never re-call any of these mid-workflow for a category that already has the data it needs — every one of the 7 checklist categories reads from this same initial batch.

***

## Hard Constraints

1. **Never mutate anything.** No `author-calc`, no `delete-sheet`, no `rename-sheet`. Every finding ends in a user instruction (rename Sheet 3, delete the scratch sheet named X, consider rewriting this calc), never an autonomous fix.
2. **A finding is a suggestion, not a publish-blocker.** Default sheet names or an unused field are not always mistakes. Present findings as a checklist for the user to triage, not a pass/fail gate.
3. **Scratch-sheet detection is heuristic, not certain.** Infer candidates from naming patterns (default names, or names containing scratch, temp, test, DQ Check, DQ Fix, or version suffixes like `v2`/`v3` with no corresponding real sheet) plus sheets absent from every dashboard. State inference confidence plainly.
4. **Titles and default names are workbook-visible, not necessarily wrong.** Weight dashboards and top-level storyboards higher than feeder worksheets.
5. **Performance findings are signals, not diagnoses.** The agent cannot time queries or see rendering speed. Performance checks flag known risk patterns (high mark count, COUNTD proliferation, many dashboard sheets). Always recommend Performance Recorder for precise diagnosis.
6. **Clearly separate tool-verified from user-verified.** The report must label which findings came from tool inspection and which are reminder items the user must verify themselves.

***

## Severity Framework

Every tool-verified finding gets one severity tag:

| Severity | Symbol | Meaning | Examples |
|----------|--------|---------|----------|
| **Warning** | ⚠️ | Publish risk: likely to cause visible issues or performance problems post-publish | Dashboard with 11+ sheets, COUNTD on 3+ sheets, live connection with no stated reason, missing dashboard title |
| **Note** | 📝 | Recommended fix: wont break anything but represents cleanup debt | Default sheet names on a dashboard, deeply nested calcs, hard-coded dates, unused calcs |
| **Info** | ℹ️ | Awareness only: subjective or low-impact, user decides | Naming inconsistency, unused hidden fields, live connection (informational), single-use COUNTD |

**Publish Readiness Score:** Close the report with a one-line summary: [N] Warnings, [N] Notes, [N] Info items. [Recommendation]. Recommendations by count:
- 0 Warnings: Looks ready. Address Notes at your discretion.
- 1-2 Warnings: Recommend addressing Warnings before publish.
- 3+ Warnings: Strongly recommend addressing Warnings. Consider splitting complex dashboards.

***

## Checklist Categories (Tool-Verified)

### 1. Unused / Hidden Fields
- From `list-available-fields`, cross-reference against every sheets shelf/encoding contents (via `get-worksheet-xml`, skipping dashboard-bound sheets per the reliability gap. Note any skipped sheets explicitly).
- Flag calculated fields defined but placed on zero sheets (often abandoned work-in-progress or diagnostic calcs from other skills).
- Flag fields marked hidden that are also unused anywhere (lowest-risk category).

### 2. Default / Unclear Names
- From `list-worksheets` / `list-dashboards`, flag names matching Tableaus default pattern (`Sheet 1`, `Sheet 2`, `Dashboard 1`, etc.).
- Flag names containing internal working titles (scratch, temp, test, v2, copy of, DQ Check:, DQ Fix:) that appear on a live dashboard (stronger finding than an orphaned sheet).
- Flag datasource names left as defaults (Sample - Superstore, connection string patterns).

### 3. Missing Titles
- Check every dashboard and storyboard for blank or auto-generated titles.
- Weight dashboards higher than supporting worksheets (per Hard Constraint #4).
- Check for missing chart titles on sheets placed on multi-chart dashboards.

### 4. Orphaned Scratch Sheets
- Cross-reference every worksheet against dashboard membership. Sheets on zero dashboards and zero storyboards are candidates.
- Apply naming-pattern heuristic from Hard Constraint #3 and assign confidence tiers:
  - **High confidence:** Default name (Sheet 1, Sheet 2) AND on zero dashboards.
  - **Medium confidence:** Name matches pattern (scratch, temp, test, DQ Check, DQ Fix, v2/v3) AND on zero dashboards.
  - **Low confidence:** On zero dashboards only (no naming signal).
- Never recommend outright deletion. List candidates with their confidence tier and let the user decide.

### 5. Performance Risks
Refer to `skill-expertise/performance_checks.md` for full detection logic, thresholds, and reporting templates.

- **Dashboard sheet count:** Flag dashboards with 8+ sheets. 11+ is a strong warning.
- **Mark count estimation:** Flag sheets with 6+ fields on Detail or 4+ dimensions on Rows/Columns.
- **COUNTD usage:** Flag COUNTD calcs appearing on 3+ sheets. If per-sheet shelf-content checks needed to confirm placement count were skipped or unavailable (dashboard-bound XML gap, etc.), never silently downgrade to Note — report as Warning (unconfirmed placement) and state plainly that the sheet count could not be verified.
- **String-heavy calcs:** Flag IF/CASE calcs that return exactly 2 distinct string values (binary logic expressed as strings). These should be Booleans.
- **Filter count:** Flag dashboards with 5+ active filters (note: filter configuration not inspectable).
- **Live connection note:** Flag live connections as informational (user may have valid reason).
- **Custom SQL note:** Flag if detectable from datasource metadata.

### 6. Calculation Hygiene

**Wide-datasource optimization:** For datasources with 100+ calculated fields, limit calculation hygiene checks to calcs placed on at least one sheet. Calcs that are both unused and unchecked here are already flagged in Category 1 (Unused/Hidden Fields).

- **Deeply nested calcs:** Flag calculations with 3+ levels of dependency (calc references calc references calc). These are harder to maintain and debug post-publish.
- **Hard-coded dates/values:** Flag calcs containing literal date values (`#2024-01-01#`, `2024`, `Q1`) that will become stale.
- **Missing comments:** Flag calcs with 5+ lines of formula that contain no `//` comment lines. Recommend adding business logic descriptions.
- **Calc complexity vs. alternatives:** Note when native Tableau features (groups, sets, bins, aliases) could replace a calculation. From Tableaus guidance: Use native Tableau features instead of calculations when possible.

### 7. Naming Consistency
- Scan all field names, sheet names, and dashboard names for inconsistent patterns:
  - Mixed casing conventions (some Title Case, some camelCase, some ALL CAPS)
  - Inconsistent prefixes or suffixes across related calcs
  - Abbreviated vs. spelled-out versions of the same concept
- **Flag threshold:** 3+ fields/sheets within the same conceptual group using different casing conventions. Report as Info severity. Naming is subjective, but inconsistency is a maintenance burden.

***

## User-Verified Reminder Checklist

After the tool-verified findings, present this as a separate section clearly labeled Items for Manual Verification. These are items the agent cannot inspect due to platform limitations but are important for publish readiness.

Group by domain:

**Interactivity (cannot be tool-verified: no mark-selection, no parameter-set, no filter-config access):**
- [ ] Filter actions work as designed and filter the correct target sheets
- [ ] Parameters and Sets function as expected when changed
- [ ] Only Relevant Values is set intentionally (creates extra queries when enabled)
- [ ] Show Apply Button enabled on multi-select filters
- [ ] Context filters set where needed for LOD calcs
- [ ] Logical model not excluding data unintentionally

**Style & Formatting (cannot be tool-verified: no visual/screenshot capability):**
- [ ] Instructions, metric definitions, and helper text are included
- [ ] Extra borders and grid lines removed
- [ ] Color use is thoughtful, consistent, and accessible
- [ ] Tooltips formatted and consistent; Command options removed
- [ ] Font hierarchy is clear and consistent
- [ ] Measures formatted appropriately (currency, percentages, decimals)

**Usability (cannot be tool-verified: no rendering or export capability):**
- [ ] Views render in <5 seconds (use Performance Recorder if slow)
- [ ] Dashboard sizing is compatible with common screen sizes (recommend Fixed)
- [ ] Export to PDF/PPT/Excel works if required for the audience

**Compliance (cannot be tool-verified: Server/Cloud-side configuration):**
- [ ] Row Level Security configured if needed
- [ ] Workbook permissions model set appropriately
- [ ] Branding applied per organizational standards
- [ ] Confidentiality statements included if required

**Post-Publish Reminders (cannot be done from Desktop):**
- [ ] Refresh schedule configured (extract) or Data Freshness Policy set (live)
- [ ] Datasource description added on Server/Cloud
- [ ] Lens(es) created if applicable
- [ ] Entry criteria and use cases documented
- [ ] Embedded credentials verified

***

## Workflow

1. Call `get-workbook-inventory`, `list-worksheets`, `list-dashboards`, `list-available-fields` (verbosity: full), and `list-workbook-datasources`.
2. **Scoping gate:** If the workbook is large (25+ worksheets or 100+ fields), ask the user to scope: Full workbook, specific dashboard(s), or skip a category (e.g., skip naming consistency)? For workbooks with fewer than 5 worksheets and 20 fields, skip the scoping gate entirely (most housekeeping checks are unlikely to surface findings at this scale). If the workbook has 10+ dashboards, add a dashboard-count branch to the same question: This workbook has [N] dashboards — check all of them, or just the ones youre about to publish? (This is distinct from the per-dashboard sheet-count threshold in Category 5 — that flags a single dashboard with too many sheets; this flags a workbook with too many dashboards to check in one pass.)
3. Run the 7 tool-verified checklist categories.
3a. **Early exit:** if Step 3 returns zero findings across all 7 categories, skip straight to the Publish Readiness Score line (0 Warnings, 0 Notes, 0 Info items. Looks ready.) rather than presenting an empty checklist with no content under each category header.
4. Assemble findings as a bulleted checklist (never a table), grouped by category, ordered by publish-risk:
   - Performance Risks (highest impact post-publish)
   - Missing Titles (most visible to viewers)
   - Default/Unclear Names
   - Calculation Hygiene
   - Orphaned Scratch Sheets
   - Naming Consistency
   - Unused/Hidden Fields (least visible, lowest urgency)
5. Present the User-Verified Reminder Checklist as a clearly separated second section.
6. **Pre-report validation (gate 1 of 2):** Before presenting findings, verify each tool-verified item references a specific tool output (a named field, sheet, formula, or datasource). Remove any finding that cannot be traced to a specific tool result.
6a. **Pre-report validation (gate 2 of 2):** Reconcile the count of bulleted findings against the number of category checks that actually ran (7, minus any the user asked to skip in Step 2). If a category that ran produced no corresponding bullets anywhere in the assembled report, confirm thats a genuine clean result for that category rather than a dropped finding before presenting.
7. Close with the Publish Readiness Score ([N] Warnings, [N] Notes, [N] Info items. [Recommendation].) and offer to re-run after cleanup.

**Mid-report branch:** If the user asks to fix a finding during the report, decline per Hard Constraint #1: I cant make that change (read-only skill), but heres exactly where to find it in Desktop: [specific menu path or location]. Then continue the remaining checks.

***

## Error Handling

| Failure | Recovery |
|---------|----------|
| `get-workbook-inventory` fails or returns no workbook | No workbook is open. Tell user: No workbook detected. Open one and try again. |
| `list-available-fields` returns empty for a datasource | Skip unused-field and calc-hygiene checks for that datasource. Note it was skipped, continue with the rest. |
| `get-worksheet-xml` 500s on a dashboard-bound sheet | Known reliability gap. Skip that sheets shelf-content check. Note usage not confirmed (tool reliability gap) rather than assuming unused. |
| Workbook has zero dashboards | Skip orphan detection and dashboard-specific checks. Note that these checks are unreliable without at least one dashboard. |
| User asks to delete or rename something | Decline: I cant delete or rename sheets/fields (platform limitation). Heres the exact item and where to find it so you can do it in Desktop. |
| `list-workbook-datasources` not available or empty | Skip connection-type and datasource-name checks. Note limitation. |
| `list-available-fields` returns an access-denied/permission error for some fields (row-level security) | Record those fields as access-restricted — not checked in the relevant category. Continue with the rest of the datasource; dont treat this as a systemic outage. |

***

## Composability

- **Upstream:** Offer proactively when a user says anything indicating imminent publish (about to publish, sending this to the team, pushing to Server, going live). Dont wait for exact trigger phrasing.
- **Downstream:** None. This is a terminal, read-only check. Findings may prompt the user to invoke other skills (calc authoring to fix a calc, data-scribe to document fields, data-quality-review for data issues), but this skill doesnt hand off structured output.
- **Adjacent:** `data-quality-review` checks data correctness; this skill checks workbook presentation and performance hygiene. `data-scribe` documents field meaning; this skill flags undocumented calcs. `interaction-validator` checks wiring after build; this skill does a broader pre-publish sweep. All are independently useful and can be offered in sequence before a publish action.
- **Context leverage:** If a `data-quality-review` report is available in conversation context, skip Category 1 (Unused/Hidden Fields) and reference that reports findings instead of re-scanning. If a `workbook-auditor` change digest is available in conversation context, cross-reference its new/changed since last snapshot findings against this runs results and flag which publish-readiness findings involve recently-changed sheets/calcs — a freshly-added calc missing comments is a different priority than a stale one thats been unused for months, even though both would otherwise get the same severity tag.
- No workbook mutations occur, ever.

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
