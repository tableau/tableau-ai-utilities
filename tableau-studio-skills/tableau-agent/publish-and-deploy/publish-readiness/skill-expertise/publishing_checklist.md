# Publishing Checklist Reference

Complete pre-publish checklist organized by domain. Each item is tagged with detectability status indicating whether the Desktop agent can check it via tools, or whether it must be reported as a user-verified item.

***

## Data Source(s)

### General

| Check | Detectable? | Method / Limitation |
|-------|-------------|---------------------|
| Descriptive datasource name (not "Sample - Superstore" left as default) | Partial | `list-workbook-datasources` returns the name; pattern-match against known defaults |
| Embedded credentials | No | Not exposed via any Desktop tool. Advise user to verify in Data > [datasource] > Edit Connection. |
| Refresh schedule configured (for extracts) | No | Server/Cloud-side configuration. Remind user to set post-publish. |
| Data freshness policy (for live connections) | No | Server/Cloud-side configuration. Remind user to set post-publish. |
| Remove/hide duplicative or unused fields | Yes | `list-available-fields` cross-referenced with sheet usage (see Checklist Category 1 in SKILL.md) |
| Logical/physical table relationships appropriate | Partial | Can see table count and relationship fields from inventory; cannot judge business appropriateness. Flag multi-table datasources for user review. |

### Published Datasource Metadata (Post-Publish Reminders)

These cannot be verified pre-publish from Desktop. Include as a reminder checklist:

- Create Lens(es) if applicable
- Add datasource description
- Document limitations
- Document entry criteria (who should use this data, for what)
- Document use cases
- Verify lineage is visible
- Confirm refresh schedule for Tableau extract
- Confirm refresh schedule for external ETL/ELT

***

## Fields & Calculations

| Check | Detectable? | Method / Limitation |
|-------|-------------|---------------------|
| Calculations validated for accuracy at different aggregation levels | No | Requires domain knowledge and manual testing. Remind user. |
| Calculations are not more complex than necessary | Partial | Can flag deeply nested calcs (3+ dependency levels) or calcs with 5+ function calls. Cannot judge business necessity. |
| Row-level and aggregate calculations used appropriately | Partial | Can detect mixed-aggregation patterns from formula text. Cannot judge intent. |
| Calculations commented with business logic | Partial | Can detect absence of comments in formula text (if formula starts immediately with no `//` lines). Cannot verify comment quality. |
| Unused fields hidden, unused calcs deleted | Yes | `list-available-fields` cross-referenced with usage. Note: agent cannot delete calcs (platform limitation). |
| Field names are meaningful | Partial | Can flag default-pattern names or very short/generic names (e.g., "Field1", "Calc1"). Cannot judge business meaning. |
| Field "Comments" populated | Partial | `list-available-fields` with verbosity:full may expose description/comment metadata. Coverage varies by datasource type. |
| Default data types set correctly | Partial | Can detect type from field metadata. Cannot judge if the default is correct for the business context. |
| Default aggregation set | Partial | Can see default aggregation. Cannot judge if SUM vs. AVG is correct for the measure's semantics. |
| Default format set (number, date, currency) | No | Format strings not reliably exposed via current tools. |
| Default color/shape set | No | Not exposed via current tools. |

***

## Dashboard(s): Style & Formatting

| Check | Detectable? | Method / Limitation |
|-------|-------------|---------------------|
| Each dashboard has a descriptive title | Yes | `get-workbook-inventory` returns title metadata. Flag blank or auto-generated titles. |
| Instructions/metric definitions/helper text included | No | Cannot inspect text objects on dashboards. Advise user to verify. |
| Extra borders, grid lines removed | No | Visual-only. Cannot inspect formatting via tools. |
| Labels or axis included for all charts | No | Cannot verify axis/label visibility. Advise user. |
| Color use is thoughtful and consistent | No | Cannot inspect color encoding. Recommend accessibility review. |
| Shape use is thoughtful and consistent | No | Cannot inspect shape encoding. |
| Tooltips formatted and consistent | Partial | Can detect tooltip fields via `get-summary-data` (fields on Detail). Cannot verify tooltip formatting. |
| Measures formatted appropriately | No | Format strings not exposed. |
| Font hierarchy clear and consistent | No | Visual-only. |
| "Command" options removed from tooltips | No | Cannot inspect tooltip configuration. Advise user to right-click > Tooltip > uncheck "Include command buttons." |

***

## Dashboard(s): Filters & Interactivity

| Check | Detectable? | Method / Limitation |
|-------|-------------|---------------------|
| Actions work as designed and filter appropriately | No | Cannot simulate mark selection or trigger filter actions (platform limitation: no mark-selection command). Advise manual testing. |
| Parameters and Sets function as designed | No | Cannot change existing parameter values (author-parameter is create-only, caption collision on existing). Advise manual testing. |
| Logical model not excluding data unintentionally | No | Requires domain knowledge of expected results. |
| Context filters used where needed with LOD calcs | Partial | Can detect LOD calcs from formula text. Cannot verify context filter placement (no Filters shelf access). Advise user. |
| Filters function as designed | No | Cannot trigger filters. Advise manual testing. |
| Filters apply to all applicable sheets | Partial | Can see filter-related fields across sheets but cannot confirm filter scope configuration. |
| Filter options customized (All option, Apply button, Relevant Values, selection type) | No | Filter UI configuration not exposed via tools. Advise user to verify each filter's settings. |

***

## Usability

| Check | Detectable? | Method / Limitation |
|-------|-------------|---------------------|
| Views render in <5 seconds | No | Cannot time rendering. Advise Performance Recorder. |
| Instructions/definitions easily found | No | Visual layout judgment. |
| Filters, legends, labels appropriately placed | No | Cannot inspect dashboard zone layout. |
| Export formatting (PDF, PPT, Excel) works | No | Cannot test export. Advise manual verification. |
| Dashboard sizing compatible with common screens | Partial | Can note if dashboard exists (from inventory) but cannot read its size setting. Recommend fixed 1400x900 or similar. |

***

## Compliance & Maintainability

| Check | Detectable? | Method / Limitation |
|-------|-------------|---------------------|
| Row Level Security (RLS) configured | No | Server/Cloud-side. Remind user. |
| Workbook permissions model set | No | Server/Cloud-side. Remind user. |
| Branding applied | No | Visual inspection only. |
| Confidentiality statements included | No | Cannot inspect text objects. |
| Auditability and versioning plan | No | Organizational process. Remind user. |
| ETL/data lineage documented | No | External documentation. Remind user. |
| Entry criteria clear | No | External documentation. Remind user. |
| Query and refresh duration stable | No | Requires monitoring over time. Remind user to check post-publish. |
| Hard-coded values not used (e.g., date filters) | Partial | Can detect calcs with literal date values (e.g., `#2024-01-01#` or `"2024"`) from formula text. Cannot detect filter hard-coding. |
| Calculations performed in ETL where applicable | No | Architectural judgment. Remind user. |

***

## Knowledge Transfer & Documentation

| Check | Detectable? | Method / Limitation |
|-------|-------------|---------------------|
| Developer comments in workbook | No | Not exposed via tools. |
| Calculation comments present | Partial | Can detect `//` comment lines in formula text. |
| Dashboard layer naming | No | Cannot inspect container/zone names. |
| Color-coded workbook tabs | No | Tab color not exposed. |
| Naming conventions consistent | Yes | Can scan all sheet/dashboard/field names for patterns. |
| Unused worksheets deleted | Yes | Cross-reference sheets against dashboard membership (existing Category 4). |
| Worksheets on dashboards hidden | Partial | Can detect sheets placed on dashboards, but cannot verify the "hide sheet" setting is toggled. Advise user. |
| Containers used, extra containers removed | No | Cannot inspect dashboard container structure. |
| Action naming clear | No | Cannot read action configuration. Advise user. |
| Actions apply as designed | No | Cannot trigger actions (mark-selection gap). Advise manual testing. |
