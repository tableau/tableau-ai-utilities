# Tableau Content Compass

**Find what already exists before you build something new.**

Every Tableau site accumulates content. Hundreds of views, dozens of datasources, Pulse metrics scattered across projects. When someone asks "do we have a dashboard for regional sales?" the answer is usually buried under layers of project folders and cryptic workbook names.

Content Compass is a Claude Desktop skill that searches your Tableau site's metadata, field names, view names, datasource schemas, and Pulse metric definitions to answer that question in seconds. You describe what you're looking for in plain language, and it finds what matches.

## What It Does

Content Compass searches across three layers of your Tableau site:

1. **Views and workbooks** (names, tags, descriptions, usage stats)
2. **Datasource fields** (the actual columns and measures available in your data)
3. **Pulse metric definitions** (pre-built KPIs and their configurations)

It scores every match on a 0-100 relevance scale, groups results into confidence tiers (High / Medium / Low), and tells you exactly *why* something matched. No guessing, no "maybe this one."

## Features

**Tiered relevance scoring.** Every result gets a transparent score based on concrete signals: word-boundary name matches (+30), field-level evidence (+25), description matches (+20), usage signals (+5), recency (+5). You see the math, not just a vague "relevant" label.

**Project discovery.** Don't know which project to search? Content Compass helps you find it. Keyword search, hierarchical browsing (drill into sub-projects), owner-based filtering, or just browse everything.

**Smart matching.** Understands that "churn" relates to "attrition" and "retention." Infers that "how are sales trending?" means you need a date field plus a sales measure. Expands your intent without inflating scores.

**Gap analysis.** When nothing matches, it tells you clearly and suggests next steps: build it (Dashboard Blueprint), check if the data exists (Data Quality Sentinel), or broaden the search.

**Memory loop.** Remembers which projects you searched, what gaps were found, and what content answered past questions. Next time you ask something similar, it skips redundant work or warns you early about known gaps.

**Direct links.** Top results are enriched with a clickable "Open in Tableau" link when Tableau returns a URL. When it doesn't, you get the location as "Project > Workbook > View" instead. URLs are never guessed.

**Graceful degradation.** API failures don't block results. If datasource metadata is unavailable, it proceeds with name-level matching and tells you confidence is lower. If Pulse has no definitions, it says so once and moves on.

## Scoring System

| Signal | Points | Definition |
|--------|--------|------------|
| Name match (word boundary) | +30 | Term appears as a complete word in the content name |
| Name match (substring only) | +15 | Term appears inside another word |
| Name match (synonym) | +15 | Related concept from the synonym table |
| Field match (exact) | +25 | Datasource field matches query term directly |
| Field match (implied) | +15 | Field matches an inferred measure or dimension |
| Description match | +20 | Content description references the topic |
| Tag match | +10 | Tags contain relevant terms |
| Pulse metric match | +20 | Metric name/definition matches the concept |
| Temporal capability | +10 | Has date fields when query implies time analysis |
| Usage signal (top quartile) | +5 | View count in top 25% of the project |
| Recency signal | +5 | Updated within the last 90 days |

Score cap: 100. No double-counting the same field across signal rows. The name signal counts once per item (best term match), and a field signal counts once per row however many fields match. So a word-boundary name match plus an exact field match is 55 (Medium); High needs one more signal. Usage is judged against the other results in the same project in this search; if Tableau returns no usage count, that signal is skipped.

**Confidence tiers:**
- **High (60-100):** Strong match. This content very likely answers your question.
- **Medium (35-59):** Partial match. Related, may answer part of your question.
- **Low (15-34):** Tangential. Worth knowing about, probably not the direct answer.

Results below 15 aren't shown.

## Prerequisites

- [Claude Desktop](https://claude.ai/download) with agent mode enabled
- [Tableau MCP connector](https://github.com/tableau/tableau-mcp) configured and authenticated to your Tableau site
- A Tableau site with published content (views, datasources, or Pulse metrics)

## Quick Example

**You:** "Do we have anything showing customer churn by region?"

**Content Compass:**
1. Asks which project to search (or uses your previously searched project from memory)
2. Extracts terms: "customer", "churn", "region"
3. Expands: churn → attrition, retention, cancellation
4. Searches views, datasources, and Pulse metrics
5. Scores matches against all signals
6. Returns tiered results with evidence

```
## High Confidence

### 1. Customer Retention Dashboard
Type: View | Workbook: Customer Analytics | Owner: Sarah Chen
Link: Open in Tableau (https://[pod].online.tableau.com/#/site/[site]/views/CustomerAnalytics/CustomerRetention)
Why this matches: Name contains "Customer" at word boundary (+30),
datasource has "Region" and "Churn Rate" fields (+25, counted once), has a date field for trending (+10), updated 12 days ago (+5).
Score: 70/100
```

## How It Connects to Other Skills

Content Compass is skill #10 in a suite of Tableau workflow skills. It's the starting point: find what exists, then hand off to specialized skills for deeper work.

| After Content Compass finds... | Hand off to... |
|-------------------------------|----------------|
| A view to evaluate | VizCritique Pro |
| A view to document | Tableau Scribe |
| A gap (nothing exists) | Dashboard Blueprint |
| A datasource to profile | Data Quality Sentinel |
| A Pulse metric to optimize | Pulse Blueprint |

## Installation

Copy the whole `tableau-content-compass` folder (`SKILL.md` plus the `skill-expertise/` files) into your Claude Desktop skills directory, or save it as a Cowork skill with its `skill-expertise/` files:

```
Skill name: tableau-content-compass
```


## Lifecycle (Phases)

| Phase | Purpose |
|-------|---------|
| 0. Context Check | Reads memory for prior searches, known gaps, preferred projects |
| 1. Intake | Confirms project scope and query (or triggers project discovery) |
| 2. Search Execution | Runs API calls across views, datasources, Pulse |
| 3. Relevance Scoring | Scores and tiers all matches |
| 4. Output | Delivers formatted results with evidence |
| 4.5. Pre-Delivery Validation | 6-point checklist before presenting |
| 5. Refinement | Handles "dig deeper", "try different terms", "broaden scope" |
| 5.5. Memory Update | Saves project, gaps, and top results for future sessions |

## Limitations

- Searches metadata only (names, fields, descriptions, tags). Cannot see what's *inside* a visualization (chart types, calculated fields, dashboard layout).
- Capped at 5 datasource metadata calls and 5 view detail calls per search to stay within reasonable API usage.
- Synonym expansion is a fixed table, not ML-based. It covers common business terms but won't know your organization's proprietary terminology.
- Usage stats (hit counts) are lifetime, not recent. A view with 1,000 historical views may not be actively used today.

## Author

Built by Adam Mico. Part of a broader effort to make Tableau practitioners' lives easier through AI-assisted workflows.
