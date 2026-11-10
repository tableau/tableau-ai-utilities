# Dashboard Print Check

Audit a Tableau dashboard for print-readiness against a locked 4-check catalog (aspect ratio + orientation, zone density per page, color-safe for black-and-white, text legibility at print scale).

**Example:** "Is this dashboard print-ready for Letter?"

***

## What it does

Runs 4 checks against one dashboard and a user-declared print target (Letter, A4, custom), tiers findings by severity, and produces manual Desktop-fix instructions per finding. Read-only. Zone-density threshold (100+ per page) and 2:1 aspect-ratio threshold are empirically defensible and documented in the reference file.

## When to use it

- "I'm handing this dashboard out at a meeting and want to make sure it prints well."
- "I need to know if my dashboard will look OK on Letter paper."
- "I want a pre-publish check before I export to PDF."

## When NOT to use it

- Not for PDF or PowerPoint export-format compatibility (not supported).
- Not for interactive-element behavior in print like filter states or tooltip visibility (out of scope).
- Not for non-print dashboard hygiene (route to dashboard-preflight).
- Not for chart-type appropriateness (route to chart-swap-advisor).
- Not for multi-dashboard batch runs (one dashboard per invocation).

## How to trigger it

- "audit this dashboard for print"
- "print check"
- "print layout audit"
- "is this dashboard print-ready"
- "dashboard-print-check"

## What you'll need

- Tableau Desktop 2024.3 or later with the MCP agent connected.
- The dashboard open in the workbook.
- A print target in mind (Letter, A4, or specific custom dimensions). The skill will ask.

## Example walkthrough

**Input:** Audit "Overview" for print-readiness on Letter.

**Output:**

```
Print target: Letter (8.5 x 11 in, portrait).
Dashboard: Overview. Aspect ratio: 1.4:1. Zones: 47.

Findings:
  1. DPC-SIZE-02 (Warning): Aspect ratio 1.4:1 close to Letter 1.29:1 ratio.
     Desktop fix: none needed; ratio within tolerance.
  2. DPC-DENSITY-04 (clear): 47 zones, under 100-zone threshold.
  3. DPC-COLORSAFE-05 (Info): Two chart colors (blue and orange) will differentiate
     under grayscale but with reduced contrast.
     Desktop fix: consider adding pattern encoding or direct labels.
  4. DPC-LEGIBILITY-06 (clear): Smallest text (10pt) legible at print scale.

Overall: print-ready with one minor Info-tier note.
```

## What you get back

- Per-check findings with severity tier and Desktop-fix instructions.
- A `print_check_report/1` handoff for downstream consumers (publish-readiness, workbook-auditor).
- Clear pass/fail signal against the declared print target.

## Limitations

- Print target must be user-declared. The skill will not auto-detect a target from workbook XML.
- Retired checks (page-break, header/footer, margins, standalone orientation) reflect platform gaps, not skill defects. Orientation is absorbed as a sub-check of DPC-SIZE-02 at the 2:1 threshold.
- Rendering fidelity (fonts, exact colors) is not verifiable via XML alone; findings flag likely issues but cannot preview the actual print output.
- One dashboard per invocation.

## Troubleshooting

- **"Skill won't proceed without a print target."** Declare Letter, A4, or custom dimensions when prompted. HC#6 refuses auto-detection.
- **"Zone-density check clear but the dashboard still feels crowded."** The 100-zone threshold is a heuristic. Consider running dashboard-preflight for a broader hygiene check.
- **"Findings look wrong for my custom paper size."** Provide exact width and height in inches; the skill will recompute against your dimensions.

## Support

File issues in the Tableau Studio Agent Skills repo.
