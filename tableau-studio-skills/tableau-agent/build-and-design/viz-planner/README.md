# Viz Planner

Plans a complete Tableau dashboard end-to-end. Given a datasource, business questions, and an audience, it produces the full design spec (chart selections, layout, filters, actions, color, KPIs), then orchestrates the build by delegating calcs to Calc Writer and worksheets to Worksheet Builder, and finally writes the exact Desktop click-path instructions for assembly.

**Example:** "Plan me a dashboard for regional sales, audience is the VP of Sales, checked Monday mornings" returns a full spec (5 charts, KPI zone, 2 filters, 1 filter action, color palette with hex codes), then offers to build it. On accept, delegates calcs and worksheets, then hands you the Desktop assembly steps.

***

## What it does

Bridges the gap between having data and knowing what to build. You describe the audience and the questions. Viz Planner picks the charts, lays out the zones, wires the filters and actions, chooses the colors, and decides which sheet goes where. Then it drives the build.

It designs, delegates, and instructs. It does not build calcs, worksheets, or dashboards directly. That separation is deliberate. Assembly is delivered as instructions because Tableau Studio's tool surface has no reliable way to place a sheet into a container, set view Fit, or set canvas size — so a "build the dashboard for you" step would be lying about what it can verify.

## When to use it

- "I have this datasource and no idea what to build with it"
- "I need an executive dashboard by Monday, plan the whole thing"
- "My CFO wants a Q3 summary, design it and build it"
- "Redesign this dashboard for a Manager audience instead of an Analyst"
- "Wireframe a KPI + regional breakdown + trend view for me"

## When NOT to use it

- Not for a single chart with no dashboard around it (use Worksheet Builder instead)
- Not for evaluating or critiquing an existing dashboard's design (use a dashboard critique skill or logic-explainer for the wiring story)
- Not for data quality profiling (use data-quality-review instead)
- Not for authoring one calculated field (use Calc Writer directly)

## How to trigger it

- "Plan a dashboard for [thing]"
- "Design a dashboard, audience is [role]"
- "Viz planner"
- "What should I build with this data"
- "Wireframe this"
- "Build me a full dashboard"

## What you'll need

- Tableau Studio with a datasource actively connected (Viz Planner reads its field inventory via `list-available-fields`)
- The MCP tools Viz Planner uses directly: `list-available-fields`, `resolve-field`, `get-workbook-inventory`, `list-dashboards`, `get-summary-data`
- **For the build step**, the Calc Writer and Worksheet Builder skills must both be available in the session. If either is missing, Viz Planner stops at the spec and says so — it never falls back to calling build tools directly.

## Example walkthrough

**Input:** "Plan me a dashboard for our sales datasource. Audience is the VP of Sales, checks it Monday mornings. Should answer: (1) are we on track for Q3, (2) which regions are underperforming, (3) which customers are at risk of churn."

**Output (excerpt from Full Spec mode):**

```
=====================================================
VIZ PLANNER - Dashboard Design Specification
=====================================================

PROJECT: Q3 Sales Health Monitor
AUDIENCE: VP of Sales (Executive) | TIME BUDGET: 30 sec
DIMENSIONS: 1400 x 900 | PAGES: 1

1. BUSINESS QUESTIONS -> CHART MAPPING

  Q1 [P1]: Are we on track for Q3?
  -> KPI BAN + Bullet chart | Fields: SUM(Sales), [Q3 Target]
  -> Position: KPI zone, top center

  Q2 [P1]: Which regions are underperforming?
  -> Horizontal bar, colored by variance | Fields: Region, SUM(Sales), [vs Target]
  -> Position: Primary viz zone, left 60%

  Q3 [P2]: Which customers are at risk of churn?
  -> Table with status indicator | Fields: Customer, LastOrder, [Risk Score]
  -> Position: Secondary zone, right 40%

3. LAYOUT WIREFRAME

  +---------------------------------------------------+
  | Q3 Sales Health Monitor | Rolling Q3 through 9/11 |
  +---------------------------------------------------+
  | $12.4M vs $13.5M target (91.8%)   | ^ 12% YoY    |
  +----------------------------+----------------------+
  | Regional Variance (bars)   | At-Risk Customers   |
  |                            | (table + status)     |
  +----------------------------+----------------------+

5. FILTER STRATEGY
  | Date Range | Relative | Dashboard-level | Rolling Q3 | All sheets |
  | Segment    | Dropdown | Dashboard-level | All        | All sheets |

  Actions: Region bar (click) -> filters At-Risk Customers table

6. COLOR SYSTEM
  Primary: #4E79A7    Alert: #F28E2B    Neutral: #9C9C9C
  (Non-status; blue/orange/gray, WCAG AA verified)

=====================================================

Ready to build? A) Build everything, B) One sheet at a time,
or C) Adjust the plan.
```

If you accept option A, Viz Planner delegates each calculated field to Calc Writer, waits for the Validation Gate to pass, delegates each worksheet spec (P1 first) to Worksheet Builder, verifies each with `get-summary-data`, and then writes the exact drag-and-drop container instructions for the dashboard itself — including the fixed canvas size, container nesting, filter placement, and action wiring.

## What you get back

- **Two output modes:** Full Spec (comprehensive design doc with shelf recipes, wireframe, and implementation notes) or Quick Plan (chart list, layout sketch, key decisions only). Viz Planner asks which you prefer on first use and remembers your choice.
- **Audience-calibrated design.** Chart count, filter count, chart complexity, and interaction model all locked to the audience profile (Executive, Manager, Analyst, Operations, External).
- **Priority tiering (P1-P4).** Every question is triaged so P3/P4 never crowds P1/P2 on Page 1.
- **Complete color system** with hex codes, WCAG AA contrast verified. Semantic status uses triple-encoding (shape + color + text), not red/yellow/green by default.
- **Filter and action strategy** with scope, defaults, and reset behavior specified. Every action's clearing set to "Show All Values" explicitly.
- **Optional HTML mockup file.** Saved to disk, opens in a browser. Static labeled boxes matching the wireframe. Not interactive, not inline in chat.
- **Precise Desktop assembly instructions** with fixed canvas size, container nesting steps, right-click sequences for filter scope and action wiring, and a follow-up ask so Viz Planner can verify with read-only tools after you build.

## Limitations

- **Read-only for assembly.** Tableau Studio's tool surface has no reliable way to place a sheet into a specific container, set a sheet's view Fit, or set the dashboard canvas size. Viz Planner produces instructions for these steps and asks you to confirm once done. It cannot verify visual layout, filter scope, or action wiring from tools alone.
- **Never builds calcs or worksheets directly.** Even if Worksheet Builder fails or is unavailable, Viz Planner will not fall back to `bind-template`, `author-calc`, or any build tool. If Worksheet Builder is missing from the session, it stops at the spec.
- **One datasource per plan.** If your questions span multiple datasources, Viz Planner designs against one primary and notes where blending or relationships are needed.
- **Chart count capped by audience.** An Executive dashboard maxes at 4-6 charts, no exceptions. If you have more questions than that, the extras go to Page 2, tooltips, or drill actions.
- **HTML mockup is static.** It's a saved file with labeled boxes showing proportions, not a working preview. You open it in a browser separately.
- **Depends on Calc Writer and Worksheet Builder for the build path.** If either is unavailable, the design spec is still complete and usable, but the build offer disappears.

## Troubleshooting

- **"It's asking me a bunch of questions before it starts."** Phase 1 needs three things: data schema, business questions, and audience. If any are missing, Viz Planner asks in one consolidated message. Answer the three and it proceeds.
- **"It gave me instructions instead of building the dashboard."** Working as designed. Desktop's tools can't place sheets in containers reliably, so assembly is always step-by-step instructions you follow in Desktop. For 2-4 simple charts it skips the full planning questions.
- **"It won't build the dashboard for me."** Correct behavior. Assembly is instructions-only because the tool surface can't verify layout, fit, or canvas size (see Limitations). Follow the instructions in Desktop and Viz Planner will verify with read-only tools when you confirm.
- **"A calc failed during the build."** Viz Planner diagnoses the syntax issue via Calc Writer and asks how you want to proceed. It does not silently continue past a calc failure because dependent worksheets would break.
- **"Worksheet Builder reports every build failing with the same error list."** Could be genuine workbook corruption OR a static/cached error list from a validator bug (confirmed case, 2026-08-05). Viz Planner runs a cross-datasource test before concluding corruption. Ask it to check both cases if you see this pattern.
- **"The assembly instructions didn't produce what I expected."** Tell Viz Planner what you actually see in Desktop and it will revise the instructions. It will not guess at what went wrong.

## Support

File issues in the same channel you use for other Tableau Studio skill feedback. Include the datasource shape (approximate field count and types), the audience, the business questions, and where the workflow went sideways.
