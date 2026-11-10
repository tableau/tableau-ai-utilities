# Jargon Swap List

Common analyst-jargon terms with plain-language substitutions, keyed by audience profile. The skill applies this swap during translation output.

## Aggregation terms

| Analyst term | C-suite / Sponsor | Operational | External |
|---|---|---|---|
| `SUM(Sales)` | total revenue | total revenue | total sales |
| `COUNTD(Customer)` | unique customers | distinct customers | number of customers |
| `AVG(Order Value)` | average order size | average order size | typical order size |
| `MEDIAN(Days)` | typical | typical | middle value |
| `MIN(Date)` | earliest | first | starting date |
| `MAX(Date)` | latest | most recent | ending date |

## Time terms

| Analyst term | Plain |
|---|---|
| YoY | year over year |
| QoQ | quarter over quarter |
| MoM | month over month |
| MTD | month to date |
| QTD | quarter to date |
| YTD | year to date |
| FY2026 | fiscal year 2026 |

## Business metric acronyms

Define on first use for Business sponsor, Operational, and Cross-functional audiences. Spell out fully for External.

| Acronym | Plain |
|---|---|
| ARR | annual recurring revenue |
| MRR | monthly recurring revenue |
| NRR | net revenue retention |
| GRR | gross revenue retention |
| LTV | customer lifetime value |
| CAC | customer acquisition cost |
| NPS | net promoter score |
| CSAT | customer satisfaction |
| SLA | service-level agreement |
| TAM | total addressable market |
| CTR | click-through rate |
| CPC | cost per click |

## Tableau-mechanic terms (always swap for non-analyst audiences)

| Analyst term | Plain |
|---|---|
| LOD / level of detail | custom aggregation |
| INCLUDE LOD | row-level calculation |
| FIXED LOD | preset grouping |
| EXCLUDE LOD | ignores filter |
| table calc | running calculation |
| context filter | priority filter |
| extract | saved data snapshot |
| live connection | real-time pull |
| data source | underlying data |
| worksheet | chart |
| dashboard | report |
| parameter | user-selected value |
| mark | data point |
| pill | field placement |
| shelves | chart layout controls |
| drill-down | detail view |
| filter action | click-to-filter |

## Statistics terms

| Analyst term | C-suite / Sponsor | External |
|---|---|---|
| p-value | statistical confidence | significance level |
| r-squared | fit of the model | how well the pattern explains the data |
| standard deviation | typical variation | spread of values |
| outlier | unusual value | value that stands out |
| median | middle value | typical value |
| mean | average | average |

## Internal-product terms

Author must declare these per workbook. The skill asks once per translation session if any product name appears in the dashboard labels and is not in a standard dictionary. Author provides the plain-language description; the skill uses it in the translation.

Example (hypothetical):
- "Project Falcon" → "our new enterprise onboarding workflow"
- "Red Zone metric" → "customers at risk of churn"

## Swap discipline

- **Always swap** for external customer audience.
- **Define on first use** for business sponsor, operational, cross-functional.
- **Light swap** for C-suite (headline-focused; swap technical mechanics but not business acronyms the C-suite knows).
- **Never swap** for the analyst audience (handled by dashboard-walkthrough-generator, not this skill).

If no analyst-jargon terms appear in the dashboard labels, note that in the output: "The dashboard already reads in plain language. Here is the follow-up-question set anyway."
