# Script Templates

Narration scaffolding for walkthrough output. The skill composes final text by filling these templates with dashboard-specific content read from `get-dashboard-xml`.

## 30-second elevator opener

**Executive.** "This dashboard shows [headline measure] by [primary dimension] over [time window]. The headline: [one data-point structural statement]. The full view breaks it down by [top 2 dimensions used]."

**Analyst.** "This dashboard tracks [measure, aggregation] against [dimensions and filters], sourced from [data source name]. [N] sheets total. Primary question: [what the author declared]."

**Operations.** "This dashboard tells you [action class, e.g. who to prioritize]. [N] sheets, each ranking [entity] by [measure]. We will walk from highest-priority to lowest."

**External.** "This dashboard shows how our [measure] has moved over [time window]. We look at it from [N] angles. I will define each measure before we get to the chart."

## Sheet transition opener

- "Next sheet: [sheet title]. This chart answers [structural question]."
- "Moving to [sheet title], we are looking at [measure] across [dimension]."
- "Over here is [sheet title], which breaks the headline down by [field]."

## Per-sheet structural statement (never interpretive)

**OK (structural).**
- "This bar chart shows [measure, aggregation] by [dimension], sorted descending."
- "The map colors each [geo dimension] by [measure, aggregation]."
- "This line chart tracks [measure] over [time dimension] at [granularity] granularity."

**NOT OK (interpretive, HC-3 violation).**
- "Revenue is strong in the Northeast."
- "Churn is a problem in the enterprise segment."
- "The trend is accelerating."

The author owns interpretation. The skill names structure.

## Pause-and-check pattern

For audiences that may ask questions mid-walkthrough (analyst, external).

- "Any questions on [sheet] before we move on?"
- "Does the [measure definition] match how you think about [concept]?"

For audiences that typically save questions for the end (executive, operations).

- Skip pause-and-check beats.
- Add a single "questions welcome at the end" beat near the opener.

## Closer patterns

**Executive.** "Headline: [restate the elevator in one sentence]. Author's take: [placeholder for author to fill in]."

**Analyst.** "Known limitations: [data source filter, refresh date, extract scope]. Open methodological questions: [author placeholder]."

**Operations.** "This week: [top-N action items]. Owner: [author or named person]. Review next: [cadence]."

**External.** "Summary: [plain-language restatement]. Questions: [open floor]."

## Likely-stakeholder-questions template

Three questions per walkthrough, each tied to a specific data point already in the dashboard. Each question is accompanied by: (a) what to say in response, (b) which sheet or chart to show, (c) the data point that answers it.

Example (Executive, revenue dashboard):

1. **Q: How did we do this quarter vs. last?** Point to the YoY sheet. Data point: the delta label.
2. **Q: Which region is driving the number?** Point to the region map. Data point: the top-colored region.
3. **Q: Is this trending up or down?** Point to the trend sheet. Data point: the slope between the last two periods.

If the dashboard does not have the data to answer a plausible stakeholder question, say so plainly rather than fabricating.

## Elevator word-count target

30 seconds spoken is roughly 75 words at normal pace. The elevator block must be at or under this. V4 of the Validation Gate enforces this.

## Opt-in file-save format

Default save location is the user's Downloads folder. Only save elsewhere if the author explicitly names a different path.

When the author accepts file save:

```markdown
# Walkthrough: [Dashboard Name]

**Audience.** [Executive | Analyst | Operations | External]
**Dashboard.** [Name], read [date]

## 30-second elevator
[elevator paragraph]

## Walkthrough order
1. [Sheet 1 name] - [structural statement] - [pause note]
2. [Sheet 2 name] - [structural statement] - [pause note]
...

## Speaker notes
### [Sheet 1 name]
[structural statement, methodology if analyst, action if operations, definition if external]
...

## Likely questions
1. **Q:** [question]
   **A:** [response + sheet + data point]
...

## Closer
[audience-appropriate closer]
```

Author pastes into their meeting prep doc. The skill does not deliver the walkthrough live during the meeting.
