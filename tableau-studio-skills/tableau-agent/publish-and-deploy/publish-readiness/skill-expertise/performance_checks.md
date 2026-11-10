# Performance Checks Reference

Detectable performance concerns to flag before publish. These are derived from the Tableau Workbook Performance Checklist (help.tableau.com) and prioritized by what the Desktop agent can actually observe via its tool surface.

***

## What the Agent Can Detect

### Mark Count / View Complexity

**Signal:** Sheets with high field density on Rows/Columns/Detail shelves (via `get-worksheet-xml` or field count from `list-available-fields` cross-referenced with sheet placement).

**Why it matters:** The majority of slow dashboards are caused by too many marks rendered at once. Each field on Detail multiplies the mark count.

**Threshold:** Flag sheets with 6+ fields on Detail shelf, or 4+ dimensions on Rows/Columns combined. These are yellow flags, not errors.

**What to report:** "[Sheet X] has [N] fields on Detail and [M] dimensions on Rows/Columns. High mark counts slow rendering. Consider whether all Detail fields are needed, or if some can move to tooltips or be removed."

***

### Dashboard Sheet Count

**Signal:** Dashboard with 8+ visible sheets (from `get-workbook-inventory`).

**Why it matters:** Each sheet on a dashboard fires its own query. More sheets = more queries = slower initial load. Tableau's guidance: "The majority of slow dashboards are caused by too many charts on a single dashboard."

**Threshold:**
- 8-10 sheets: Note ("consider whether all are needed on initial load")
- 11+ sheets: Warning ("strongly consider splitting into multiple dashboards or using guided analytics")

**What to report:** "[Dashboard X] contains [N] sheets. Consider guided analytics (filter actions revealing detail on demand) rather than showing everything at once."

***

### COUNTD Usage

**Signal:** Calculated fields using `COUNTD` (detectable from formula text via `list-available-fields` with verbosity:full).

**Why it matters:** COUNTD is one of the slowest aggregation functions. From Tableau's checklist: "COUNTD is one of the slowest function types, avoid when possible."

**Threshold:** Flag any calc using COUNTD that appears on 3+ sheets. Single-use COUNTD is often fine; repeated use compounds the cost.

**What to report:** "[Calc X] uses COUNTD and appears on [N] sheets. If exact distinct counts aren't required, consider COUNT or a pre-aggregated field."

***

### String-Heavy Calculations

**Signal:** Calculated fields with string operations (CONTAINS, FIND, REPLACE, LEFT, RIGHT, MID, REGEXP) that could potentially be Booleans or integers.

**Why it matters:** "Strings and dates are slow, numbers and Booleans are fast." String comparisons generate more expensive queries than numeric or Boolean checks.

**Threshold:** Flag calcs that produce a string result via IF/CASE logic where a Boolean (True/False) would convey the same information. This is a judgment call, not an automatic flag.

**What to report:** "[Calc X] returns string values via IF/CASE logic. If the output is binary (two categories), a Boolean calc would perform better."

***

### Filter Configuration Concerns

**Signal:** From `get-workbook-inventory` or `get-worksheet-xml`, detect:
- Filters applied to "All Using This Data Source" (applies to multiple worksheets, creating multiple queries)
- Filters set to "Only Relevant Values" (creates a query each time other filters change)
- Cross-database filters without "Show Apply Button"

**Why it matters:** "Filtering is one of the most common causes of poorly performing workbooks." Each filter configuration choice has query multiplier effects.

**Threshold:** Flag any dashboard with 5+ active filters (not just filter actions). Note: cannot always detect filter configuration details from available tools; report what's observable and note limitations.

**What to report:** "[Dashboard X] has [N] filters. Consider: Are 'Only Relevant Values' filters creating redundant queries? Would filter actions reduce query load? Is 'Show Apply Button' enabled on multi-select filters?"

***

### Extract vs. Live Connection

**Signal:** From `list-workbook-datasources` or datasource metadata, detect connection type.

**Why it matters:** "Extracts are a quick and easy way to make most workbooks run faster. If you don't need real-time data and aren't working over billions of rows, you should try them."

**Threshold:** Flag live connections as an informational note (not a warning). The user may have a valid reason for live.

**What to report:** "[Datasource X] uses a live connection. If real-time data isn't required, an extract may improve load times. If live is intentional, ensure a Data Freshness Policy is configured post-publish."

***

### Custom SQL

**Signal:** From datasource metadata or connection details (if visible in inventory).

**Why it matters:** "Avoid using custom SQL." Custom SQL bypasses Tableau's query optimizer and can prevent query folding.

**Threshold:** Flag if detectable. This is not always visible from available tools.

**What to report:** "[Datasource X] appears to use custom SQL. Custom SQL bypasses Tableau's query optimizer. Consider using Tableau's native join/relationship modeling or moving logic to a database view."

***

## What the Agent Cannot Detect (Advise Only)

These are important performance factors that require user verification because no tool exposes the necessary information:

| Factor | Why It Matters | What to Ask the User |
|--------|---------------|---------------------|
| Dashboard sizing (fixed vs. automatic) | Fixed-size dashboards don't re-render for different window sizes | "Is your dashboard set to Fixed size? Automatic sizing re-renders on every resize." |
| Query batching (same LOD across sheets) | Sheets at the same detail level can batch into a single query | "Do your dashboard sheets share the same level of detail where possible?" |
| Referential integrity | Enables join culling (unused tables don't query) | "Is 'Assume Referential Integrity' enabled on your datasource joins?" |
| Index coverage on live databases | Filters are more efficient on indexed columns | "Are the fields you filter on indexed in your database?" |
| Custom geocoding inflation | Can massively inflate workbook file size | "Are you using custom geocoding? This can inflate .twbx size significantly." |

***

## Performance Recorder Reminder

The agent cannot run or read Performance Recorder results. When performance concerns are flagged, always recommend:

"For precise diagnosis, run Help > Settings and Performance > Start Performance Recording in Desktop, interact with the slow view, then stop recording. The resulting dashboard shows exactly where time is spent (queries, calculations, rendering)."
