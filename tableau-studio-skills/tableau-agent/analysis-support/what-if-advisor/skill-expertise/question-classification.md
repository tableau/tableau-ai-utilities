# Question Classification

Maps author's natural-language what-if question to the right W-mechanism (W1-W6) or the honest-limitation path (parameter-only).

## Classification rules

Apply in order. First match wins.

### Rule 1. Single-value reference

**Match signals (locked exact-match list, case-insensitive).** "line," "target," "mark," "break-even," "breakeven," "threshold," "benchmark," "goal."

**Example.** "Add a line at $1M so I can see which months hit target."

**Classification.** W1 reference line.

### Rule 2. Range reference

**Match signals (locked exact-match list, case-insensitive).** "band," "range," "zone," "corridor," "between," "tolerance."

**Example.** "Shade the forecast corridor on the trend."

**Classification.** W2 reference band.

### Rule 3. Projection or extension

**Match signals (locked exact-match list, case-insensitive).** "project," "extend," "extended," "where will this be," "if we keep going," "at this rate," "at the current rate."

**Example.** "Project this sales trend out six months."

**Classification.** W3 trend line extension. Always flag as projection, not prediction (HC-6).

### Rule 4. Membership-shift

**Match signals (locked exact-match list, case-insensitive).** "who would be in," "which would move to," "members of," "top-n if," "cutoff," "move into," "fall below," "fall out of."

**Example.** "Which accounts would move into the top-20 if they grew 15%."

**Classification.** W4 set-based scenario.

### Rule 5. Side-by-side overlay

**Match signals (locked exact-match list, case-insensitive).** "overlay," "compare to," "actual vs," "side by side," "on the same chart as."

**Example.** "Show actual revenue vs. what revenue would be at target."

**Classification.** W5 dual-axis overlay.

### Rule 6. Baked-in hypothetical as a reusable field

**Match signals (locked exact-match list, case-insensitive).** "a field for," "a calc for," "a measure that," "add it to the data," "create a calc," "create a field." Also matches the word "if" co-occurring with a formula shape ("if every customer spent 20% more").

**Example.** "Revenue if every customer spent 20% more."

**Classification.** W6 scenario calc. Handed off to calc-writer.

### Rule 7. Parameter-authoring-required (honest limitation)

**Match signals (locked exact-match list, case-insensitive).** "slider," "dropdown," "let the user pick," "when i change the input," "interactive scenario," "user-selected value," "let the user choose."

**Example.** "Let the user pick a growth rate from 0 to 50% and update the chart."

**Classification.** Parameter-only. Emit honest-limitation verdict (HC-3) with manual Desktop parameter path. State plainly that parameter authoring is weak in the current agent and recommend manual Desktop creation.

### Rule 8. Monte Carlo or probabilistic

**Match signals (locked exact-match list, case-insensitive).** "simulate," "probability," "distribution of outcomes," "monte carlo," "random."

**Example.** "Simulate revenue outcomes if churn is between 5 and 15%."

**Classification.** Out of scope. Emit honest-limitation verdict. Recommend external modeling (R, Python, Excel) and import results back into Tableau.

### Rule 9. Causality or prediction (not supported)

**Match signals (locked exact-match list, case-insensitive).** "cause," "predict," "forecast with," "confidence," "machine learning prediction."

**Example.** "Predict next quarter's revenue with 95% confidence."

**Classification.** Out of scope. The skill does not support predictive modeling. Recommend proper forecasting tools (Tableau's built-in Forecast feature via Analytics pane is close but should be flagged with its own uncertainty bounds).

## Ambiguous questions

When the author's question matches two or more rules:

1. Ask one clarifying question. Example: "Do you want a line at a specific value (W1), or do you want to see the projected trend (W3)?"
2. Classify based on the answer.
3. Do not pick for the author.

## Non-standard questions

If the question doesn't match any rule and isn't obviously parameter-only, Monte Carlo, or predictive, state the skill cannot classify it in-scope and ask the author to rephrase or declare the mechanism manually.

Example response: "I cannot map this question to a mechanism in my catalog. Could you tell me more specifically what you want to see on the chart? For example: a line at a value, a band showing a range, a projection extending the trend, or an overlay comparing two scenarios."

## Examples by classification

| Author's question | Classification | Reasoning |
|---|---|---|
| "Add a $1M target line" | W1 | Single value, "line" |
| "Shade the 25th-75th percentile" | W2 | Range, "shade" |
| "Where will revenue be in a year" | W3 | Projection, "where will" |
| "Who moves into the top-10 if they grow 20%" | W4 | Membership, "moves into" |
| "Overlay target on actuals" | W5 | Overlay, "overlay on" |
| "Create a calc for revenue +20%" | W6 | Baked-in field, "create a calc" |
| "Let the user choose growth 0-50%" | Parameter-only | Slider / user choice |
| "Simulate outcomes with random churn" | Out of scope | Monte Carlo |
| "Predict Q4 at 95% confidence" | Out of scope | Statistical prediction |

## Audience note

The question classification is audience-agnostic. The author's audience shapes nothing in the W-mechanism choice. (Compare: stakeholder-translator and caption-and-tooltip-advisor are audience-aware; what-if-advisor is not.)
