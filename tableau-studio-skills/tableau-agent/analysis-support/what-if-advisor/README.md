# Tableau What-If Advisor

A read-only advisory skill that reads your what-if question, maps it to a locked 6-mechanism catalog of non-parameter approaches (W1 reference line, W2 reference band, W3 trend line extension, W4 set-based scenario, W5 dual-axis overlay, W6 scenario calc), and emits numbered Desktop steps. Explicitly works around the Studio parameter-authoring weakness by routing to mechanisms the platform does support. Fills the gap between viz-planner (full dashboard design) and calc-writer (writing the calc itself) by owning the "which mechanism fits this what-if" problem neither covers.

**Example:** "Project this sales trend out 6 months."

## What it does

Takes your natural-language what-if question and classifies it against a 9-rule mapping into one of six locked W-mechanisms (W1-W6) or into one of three honest-limitation paths (parameter-only, Monte Carlo, predictive). Returns the mechanism recommendation, numbered Desktop steps, and a caveat section stating what the analysis does and does not prove. You own execution; the skill never mutates the workbook.

Two output paths. **Verified-fit path** reads the named target sheet via `get-worksheet-xml` to confirm prerequisites (continuous axis for W1/W2, time dimension on Columns for W3, continuous measure for W5) before emitting the recommendation. **General-recommendation path** proceeds on your question wording alone when you want a mechanism-level answer first; prerequisites are announced as unverified and you confirm fit before executing.

Pairs with calc-writer (W6 scenario calc authoring), calc-debugger (W6 debugging), calc-optimizer (W6 performance), and viz-planner (dashboard redesign around the what-if) as optional downstream routes, each with a manual Desktop fallback.

## When to use it

- "Project this sales trend out 6 months."
- "Add a $1M target line to this chart."
- "Which customers would move into the top-10 if revenue grew 15%?"
- "Overlay actual sales vs. sales if we hit 10% higher."
- "Create a reusable calc for revenue if every customer spent 20% more."
- "Shade the acceptable range between $500K and $1.5M."

## When NOT to use it

- Not for writing the W6 calc itself (use calc-writer; this skill hands off with seed values)
- Not for debugging an existing calc (use calc-debugger)
- Not for optimizing calc performance (use calc-optimizer)
- Not for full dashboard redesign around the what-if (use viz-planner)
- Not for parameter authoring (platform-weak in Studio; the skill routes to a manual Desktop parameter path with the agent-reliability caveat)
- Not for Monte Carlo simulation (recommends external modeling in R/Python/Excel; offers W6 midpoint as partial answer)
- Not for predictive modeling with confidence intervals (points to Tableau's Forecast feature on the Analytics pane)
- Not for authoring or editing anything in Desktop (this skill is read-only advisory)

## How to trigger it

- "what if analysis"
- "add a scenario"
- "project this trend"
- "hypothetical scenario on [measure]"
- "run a what if"
- "which [dimension] would move into [top-N] if [measure] grew X%"
- "overlay actual vs. [hypothetical]"
- "create a calc for [measure] +X%"

## What you'll need

- Tableau Studio open with the agent connected
- A workbook with the target sheet (optional updated flow; if omitted, the skill uses the general-recommendation path and announces prerequisites as unverified)
- Your hypothetical value, if the mechanism requires one (W1 target, W2 band bounds, W4 shift percentage, W5 overlay formula, W6 calc rate). The skill will not invent business-realistic values (HC-5); if you decline to name one, it offers three options and defaults to a `[VALUE]` placeholder you replace before executing.

## The 6-mechanism catalog (W1-W6)

- **W1 Reference line.** Static value drawn as a line on a continuous axis. For "target line," "break-even," "last-year baseline." Caveat: visual overlay, does not alter the data.
- **W2 Reference band.** Range drawn as a shaded band. For "acceptable zone," "quartile range," "forecast corridor." Caveat: visual overlay, does not validate the range.
- **W3 Trend line extension.** Linear or non-linear trend projection via Analytics pane. For "where will this be in 6 months at current rate." Always flagged as projection, not prediction (HC-6).
- **W4 Set-based scenario.** Membership comparison via sets with a shifted-measure calc. For "customers who would move into the top-N if their revenue grew 10%." Caveat: membership comparison, not causation.
- **W5 Dual-axis overlay.** Actual vs. hypothetical as two measures on the same chart with Synchronize Axis. For "actual revenue vs. revenue if we hit target." Caveat: overlay, does not blend.
- **W6 Scenario calc.** Fixed-value calc field encoding a one-off hypothetical. For "revenue if every customer spent 20% more." Handed off to calc-writer with seed values; falls back to manual-paste formula template. Caveat: static field, must be hand-updated.

Full catalog with per-mechanism Desktop step blocks and example questions in `skill-expertise/mechanism-catalog.md`.

## The 9 classification rules

Applied in order; first match wins:

1. Single-value reference ("line," "target," "break-even") → **W1**
2. Range reference ("band," "range," "zone," "corridor") → **W2**
3. Projection or extension ("project," "extend," "where will this be at this rate") → **W3**
4. Membership-shift ("who would move into," "top-N if") → **W4**
5. Side-by-side overlay ("overlay," "actual vs.," "side by side") → **W5**
6. Baked-in hypothetical as a reusable field ("a calc for," "a measure that") → **W6**
7. Parameter-authoring-required ("slider," "let the user pick") → honest-limitation path with manual Desktop parameter steps
8. Monte Carlo or probabilistic ("simulate," "distribution of outcomes") → out of scope; offers external modeling + W6 midpoint fallback
9. Causality or prediction ("predict with 95% confidence") → out of scope; points to Tableau's Forecast feature

Full classification rules with example questions and ambiguity handling in `skill-expertise/question-classification.md`.

## Example walkthrough

**Input:** "project this sales trend out 6 months" (Monthly Sales Trend active: continuous MONTH(Order Date) on Columns, SUM(Sales) on Rows)

**Output (abridged, Verified-fit path):**

```
What-if question confirmed: "project this sales trend out 6 months."
Target sheet: Monthly Sales Trend (active). Prerequisites verified
via get-worksheet-xml: continuous MONTH(Order Date) on Columns,
SUM(Sales) on Rows. Time dimension on Columns confirmed.

Classification: W3 trend line extension (projection, not prediction).

Why W3. The question asks where the series lands under a continued-
rate assumption; that is a slope extension via the Analytics pane,
not a hypothetical-value overlay.

Desktop steps.
1. Click the Analytics pane.
2. Drag Trend Line onto the viz. Choose Linear.
3. Right-click the X-axis, Edit Axis. Set Range to Fixed and extend
   the "to" value 6 months past the last data point.
4. Add an annotation at the extended point naming the projected
   value and the method ("Linear projection, +6 months").

Caveats.
This is a projection, not a prediction (HC-6). It extends the current
slope assuming no conditions change. Seasonality, promotions, and
other business factors will cause real results to deviate.

File save: .md, .txt, or chat only?
```

Save goes to your Downloads folder by default.

## What you get back

- A classification against one of W1-W6, or one of the honest-limitation paths (parameter-only, Monte Carlo, predictive)
- A "why this mechanism" explanation (1-2 sentences)
- Numbered Desktop steps from the mechanism catalog
- A caveat section stating what the analysis does and does not prove
- For W6: a handoff block with seed values (field, aggregation, hypothetical value, calc-name suggestion) for calc-writer, with a manual-paste fallback
- Optional `.md` or `.txt` save to the Downloads folder

## Limitations

- Read-only. The skill does not modify the workbook. All output is text.
- Will not write the W6 calc itself (HC-1). W6 outputs are formula templates handed off to calc-writer or pasted manually.
- Will not recommend parameter authoring outside the honest-limitation path (HC-3). Parameter authoring is unreliable in the current Studio agent; a manual Desktop path is provided for authors who need user-driven value selection.
- Will not invent business-realistic hypothetical values (HC-5). If you decline to declare one, you get three options: state a value, use a `[VALUE]` placeholder, or declare baseline + shift for the skill to calculate.
- W3 trend extensions are always flagged as projections, not predictions (HC-6). No causality or forecasting claims.
- W1-W2 require a continuous axis on the target sheet. If the sheet has no continuous axis, the skill offers W4/W5/W6 alternatives.
- W3 requires a time dimension on Columns. If the sheet has no time dimension, the skill offers W1/W5/W6 alternatives.
- Monte Carlo simulation is out of scope. External modeling in R/Python/Excel is recommended; a single-point W6 midpoint calc is offered as a partial answer.
- Predictive modeling with confidence intervals is out of scope. Tableau's Forecast feature on the Analytics pane is pointed to; W3 trend extension is offered as a weaker fallback.
- Sensitivity tables across many hypothetical rates are out of scope (HC-4). A hand-built matrix via multiple W6 calcs is offered as an in-platform alternative; external modeling is the other path.

## Troubleshooting

- **"No workbook open."** The skill does not refuse. It offers to walk through `mechanism-catalog.md` and `question-classification.md` as reading reference until a workbook is open.
- **"I did not name a target sheet."** The skill uses the general-recommendation path, proceeds on your question wording alone, and announces "prerequisites unverified." Confirm fit on your actual target sheet before executing the Desktop steps.
- **"The target sheet does not have a continuous axis."** The skill states plainly that W1/W2 cannot apply and offers W4/W5/W6 alternatives based on the sheet's structure.
- **"The target sheet does not have a time dimension on Columns."** The skill states plainly that W3 cannot project forward and offers W1/W5/W6 alternatives.
- **"The question is ambiguous (matches two or more rules)."** The skill asks exactly one clarifying question per `question-classification.md` and does not pick for you. Example: "Do you want a line at a specific value (W1), or the projected trend extended into the future (W3)?"
- **"I asked for a slider or user-selected value."** The skill routes to the Rule 7 parameter-only honest-limitation path with manual Desktop parameter steps and the agent-reliability caveat. A close-enough W1-W6 fallback (fixed value instead of adjustable) is offered.
- **"I asked for a Monte Carlo simulation."** The skill routes to the Rule 8 out-of-scope path. External modeling is recommended; a W6 midpoint single-point calc is offered as a partial answer.
- **"I asked for a prediction with confidence intervals."** The skill routes to the Rule 9 out-of-scope path. Tableau's Forecast feature on the Analytics pane is pointed to with exact steps (Right-click → Forecast → Show Forecast → Forecast Options). W3 trend extension is offered as a weaker fallback.
- **"The skill asked me to write the W6 calc itself."** It should refuse per HC-1 and convert to a formula template handoff. The calc goes through calc-writer (if installed) with the seed values, or you paste the formula into Tableau's calc editor manually.
- **"The file save failed."** The skill emits the full output inline anyway and names the save error with path. Copy from chat into your notes.
- **"The skill asked me to invent a hypothetical value."** It should refuse per HC-5. Three options are offered: state the value, use a `[VALUE]` placeholder you replace later, or declare baseline + shift for the skill to calculate the hypothetical.

## Support

File issues in the Tableau Agent Skills repo.
