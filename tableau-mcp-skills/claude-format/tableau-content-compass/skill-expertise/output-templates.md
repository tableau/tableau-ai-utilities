# Output Templates

Layouts for project discovery lists, tiered content results, the No Match Found message, and the Coverage Assessment.

```
## Projects matching "[topic/keyword]"
 
| # | Project | Description | Parent | Owner |
|---|---------|-------------|--------|-------|
| 1 | [name] | [description, truncated to 60 chars] | [parent name, or "Top-level"] | [owner name, or "not shown" if only an id was returned] |
| 2 | [name] | [description] | [parent] | [owner] |
| 3 | [name] | [description] | [parent] | [owner] |
 
Which project should I search? (Pick a number, or say "all" to search across these.)
```

```
# Content Compass Results
 
**Query:** "[user's question or topic]"
**Project:** [project name]
**Searched:** [X] views, [Y] datasources, [Z] Pulse metrics
[**Partial:** N of M checked; not checked: [list]]  (include only if any step failed or was skipped)
 
---
 
## High Confidence
 
### 1. [View/Datasource/Metric Name]
**Type:** View | **Workbook:** [name] | **Owner:** [name]
**Score:** [N]/100
**Link:** [Open in Tableau]([url from get-view response])  (omit this line if no url came back; use "Location: Project > Workbook > View" instead)
**Why this matches:** [Name the top 2 scoring signals with points, e.g., "Name contains 'Sales' at word boundary (+30) and the datasource has a Region field (+25), scoring 65 total."]
**Usage:** [hitsTotal] views | Last updated: [date]  (omit usage if no count was returned)
 
<details>
<summary>Field evidence</summary>
 
Relevant fields found: `Region`, `Sales`, `Order Date`, `Category`
Datasource: [name] ([X] total fields)
Match signals: Name contains "Sales" (+30), fields include Region and Sales (+25), has date dimension for trending (+10)
</details>
 
---
 
### 2. [Next match...]
 
---
 
## Medium Confidence
 
### 3. [Match name]
**Type:** Datasource | **Owner:** [name]
**Score:** [N]/100
**Link (optional):** [Open in Tableau]([url, only if returned]) or "Location: Project > Workbook"
**Why this matches:** [Brief reasoning]
**Note:** [Why it's medium not high, e.g., "Has the right fields but no published view uses it for this specific analysis."]
 
<details>
<summary>Field evidence</summary>
[field details]
</details>
 
---
 
## Low Confidence
 
### 4. [Match name]
**Type:** Pulse Metric | **Definition:** [name]
**Score:** [N]/100
**Link (optional):** [Open in Tableau]([url, only if returned]) or "Location: Definition name"
**Why this matches:** [Brief reasoning]
**Note:** [Why it's low, e.g., "Tracks a related metric (Total Orders) but not the specific measure you asked about (Revenue)."]
 
---
 
## No Match Found (when applicable)
 
If nothing scores above 15:
 
> "I didn't find existing content that answers '[query]' in [project]. This looks like a gap. Options:
> - **Build it:** Use Tableau Dashboard Blueprint to design a new dashboard for this question.
> - **Check data:** Use Data Quality Sentinel to see if the underlying data even exists.
> - **Broaden search:** Want me to search the full site instead of just [project]?
> - **Look manually:** In Tableau, open [project] > Workbooks and scan the names, or ask the project owner whether it exists under another name."
```

```
---
 
## Coverage Assessment
 
**Fully covered:** [Yes/Partially/No] — [one sentence on whether existing content fully answers the query]
**Gaps identified:** [What's missing — e.g., "Regional breakdown exists but no time-trending view was found."]
**Suggestion:** [If partially covered: "The [view name] gets you 80% there. You'd need to add [X] to fully answer this." If not covered: "Consider building a new view. Dashboard Blueprint can help design it."]
```
