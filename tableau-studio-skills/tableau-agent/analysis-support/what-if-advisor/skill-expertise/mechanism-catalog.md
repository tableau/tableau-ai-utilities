# Mechanism Catalog (W1-W6)

Locked what-if mechanisms for what-if-advisor. Every recommendation cites one of W1-W6.

## W1. Reference line

**When.** Author wants a single-value horizontal or vertical line drawn on a continuous axis to mark a target, baseline, threshold, or comparison value.

**Example questions.**
- "Add a line at $1M revenue so I can see which months hit target."
- "Show the break-even point."
- "Compare current to last year's number on the same chart."

**Prerequisites.** Target sheet has at least one continuous axis.

**Desktop steps.**
1. On the target sheet, click the Analytics pane (left side, next to Data).
2. Drag "Reference Line" onto the viz, drop on the continuous axis.
3. In the dialog: Scope = Entire Table (or Per Pane / Per Cell if needed). Value = Constant → enter the hypothetical number. Label = Custom → write the label text.
4. Formatting: set line color (recommend grey or a brand accent), line style (dashed for hypothetical), label position (right-aligned, above/below).
5. Click OK.

**Caveat section content.** "A reference line is a visual overlay. It does not alter the data behind the chart. The line reflects your declared value, nothing more."

## W2. Reference band

**When.** Author wants a shaded range on a continuous axis to mark an acceptable zone, forecast corridor, quartile band, or tolerance.

**Example questions.**
- "Show the acceptable range for conversion rate."
- "Shade the forecast corridor on the trend."
- "Highlight the Q2-Q3 interquartile range."

**Prerequisites.** Same as W1.

**Desktop steps.**
1. Analytics pane → drag "Reference Band" onto the continuous axis.
2. In the dialog: Scope → Entire Table. Band From = Constant → enter the lower bound. Band To = Constant → enter the upper bound. OR use aggregations (e.g., AVG - 1 STDEV to AVG + 1 STDEV).
3. Fill color: light, low-opacity (recommend 10-15% opacity so marks remain readable).
4. Labels: write "Target range," "Acceptable zone," or custom.
5. Click OK.

**Caveat section content.** "A reference band is a visual overlay. It does not filter the data or change aggregations. The band reflects declared bounds, nothing more."

## W3. Trend line extension (projection)

**When.** Author wants a projection of the current trend into the future ("where will this be at the current rate").

**Example questions.**
- "Project this sales trend out six months."
- "If we keep growing at this rate, when will we hit $10M."
- "Extend the churn trend."

**Prerequisites.** Target sheet has a time dimension on Columns (or a continuous numeric dimension) and a continuous measure.

**Desktop steps.**
1. On the target sheet, click the Analytics pane.
2. Drag "Trend Line" onto the viz. Choose model: Linear (default), Logarithmic, Exponential, Polynomial, or Power.
3. Right-click the trend line → Edit Trend Lines → check "Allow a trend line per color" if the viz has a color dimension and you want separate trends per series.
4. To extend the trend into the future: use the X-axis Edit Axis → set the Range to Fixed → extend the "to" value past the last data point by the desired amount. The trend line draws into the extended range.
5. Add an annotation at the extended point naming the projected value and the extension method ("Linear projection, +6 months").

**Caveat section content.** "This is a projection, not a prediction (HC-6). The trend line extends the current slope under the assumption that no conditions change. Business factors (seasonality, interventions, external shocks) will likely cause the actual path to deviate. Use this to orient a conversation, not to commit to a number."

## W4. Set-based scenario

**When.** Author wants to compare current membership against hypothetical membership based on a what-if threshold ("customers who would be in the top-N if their revenue grew 10%").

**Example questions.**
- "Which accounts would move into the top-20 if they grew 15%."
- "Which products would fall below the discontinuation threshold if demand dropped 20%."
- "Compare current cohort to a hypothetical cohort shifted by X."

**Prerequisites.** Target sheet uses a dimension (customer, product, region, etc.) that can be grouped into a set. The what-if is a shift on a measure.

**Desktop steps.**
1. Right-click the dimension in the Data pane → Create → Set.
2. In the Set dialog, use the "By Field" tab. Field = the hypothetically-shifted measure. For a 10% growth hypothetical, use a calc field like `[Revenue] * 1.10`. Condition = Top-N or threshold.
3. Create a second set for the current (non-shifted) membership using `[Revenue]` directly.
4. On the target sheet, drag both sets onto the Marks card (Color or Detail) to show which members are in the current set, the hypothetical set, both, or neither.
5. Add a legend or caption explaining the four-way membership.

**Caveat section content.** "Set membership comparison shows who would be where under a declared shift. It does not prove causation (why they would move). It does not predict whether the shift will happen."

## W5. Dual-axis overlay

**When.** Author wants to see actual and hypothetical as two measures on the same chart, side-by-side at each data point.

**Example questions.**
- "Show actual revenue vs. what revenue would be at target."
- "Overlay forecast on actuals."
- "Compare current to adjusted current."

**Prerequisites.** Target sheet has a continuous measure.

**Desktop steps.**
1. On the target sheet, create a calc field for the hypothetical: `[Measure] * 1.10` (or whatever the hypothetical shift is).
2. Drag the hypothetical calc onto the opposite side of the axis (if measure is on Rows, drag calc to Columns, or vice versa).
3. Right-click the second axis → Dual Axis.
4. Right-click one of the two axes → Synchronize Axis so both scales align.
5. Format: use different mark types (actual = bar, hypothetical = line) OR different colors to distinguish.
6. Add labels on each series.

**Caveat section content.** "The dual-axis overlay shows actual and hypothetical in the same frame. It does not blend or average them. The hypothetical reflects your declared formula, nothing more."

## W6. Scenario calc

**When.** Author wants a fixed hypothetical value baked into the data model as a calc field, usable across many sheets.

**Example questions.**
- "Revenue if every customer spent 20% more."
- "Projected 2027 numbers assuming 15% YoY growth."
- "Churn adjusted to the industry average."

**Prerequisites.** Author declares the hypothetical formula.

**Desktop steps (handed off to calc-writer).**
1. Formula template: `[Base Measure] * (1 + [Hypothetical Rate])` or similar.
2. Calc name suggestion: `[Base Measure] (Hypothetical)` for clarity.
3. Hand off to calc-writer with the template and author-declared values. calc-writer runs the 8-check Validation Gate before delivery.

**Caveat section content.** "A scenario calc is a static field. It will not update if the underlying measure changes beyond what the formula references. Hypothetical values must be hand-updated when business context changes."

**Fallback if calc-writer is not installed.** The skill emits the formula template as text. The author pastes it into Tableau's calc editor manually: Data pane → right-click → Create Calculated Field → paste → name it → OK.

## Mechanism selection logic

The skill picks based on the shape of the author's question. See question-classification.md for the mapping rules.

## Mechanisms deliberately excluded

- **Parameter-driven scenarios.** Blocked by platform constraint (HC-3). If a question genuinely needs user-driven value selection, the skill emits the honest-limitation verdict and the manual Desktop parameter path.
- **Monte Carlo simulation.** Out of scope.
- **Scenario-planning extensions.** Out of scope.
