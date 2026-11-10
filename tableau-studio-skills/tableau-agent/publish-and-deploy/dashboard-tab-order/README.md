# Dashboard Tab Order

Audit a Tableau workbook's dashboard tab order (left-to-right navigation) for logical flow against an 8-rule catalog. Read-only. Every finding is a manual Desktop-fix instruction.

**Example:** "Audit my dashboard tab order for logical flow."

***

## What it does

Runs 8 rules against one workbook (entry-point clarity, drill-down grouping, exception-flow placement, orphan tabs, name-consistency, tab-count sanity, hidden-tab presence, device-layout inheritance), tiers findings by severity, and produces manual reorder instructions. Refuses to fabricate flow relationships from tab names; you declare the entry-point and drill-down structure at Phase 0.

## When to use it

- "I want to make sure my tab strip reads left-to-right the way people actually navigate."
- "I inherited a workbook with 12 tabs and no obvious flow."
- "I want a pre-publish check for navigation hygiene."

## When NOT to use it

- Not for renaming tabs (rename tabs manually in Desktop).
- Not for applying reorders directly (the skill gives drag-to-fix steps instead).
- Not for dashboard-internal navigation like buttons or jump actions (route to interaction-validator).
- Not for tab-count reduction via worksheet removal (route to worksheet-cleanup).
- Not for scoring overall dashboard design (route to viz-critique-pro-studio).

## How to trigger it

- "audit dashboard tab order"
- "check tab flow"
- "is my navigation logical"
- "dashboard-tab-order"
- "tab strip audit"

## What you'll need

- Tableau Desktop 2024.3 or later with the MCP agent connected.
- The workbook open with 2 or more dashboards.
- A mental model of your intended flow (entry-point dashboard, drill-down parents/children, exception flows). The skill will ask.

## Example walkthrough

**Input:** Audit tab order for Superstore.

**Output:**

```
Phase 0 flow-metadata declaration:
  Entry-point dashboard: [ Executive Overview ]
  Drill-down groups:     Executive Overview -> [ Regional Detail, Product Detail ]
  Exception flows:       [ Alerts ]

Phase 2 evaluation (8 rules):
  DT-ENTRY-01 (Warning): "Executive Overview" declared as entry-point,
    but currently at tab position 3. Recommend moving to position 1.
    Desktop fix: right-click "Executive Overview" tab, choose "Move to first".
  DT-ORPHAN-04 (Warning): "Archive" not referenced in any flow declaration.
    Desktop fix: add to a flow, or intentionally leave at strip end.
  DT-DEVICE-08 (clear): No authored device-layout mismatches detected.
    Auto-generated Phone layouts correctly excluded per Bug 3 fix.

Top-5 Warning findings surfaced. Full report saved to Tier B on request.
```

## What you get back

- Per-finding severity tier, Desktop-fix instruction, and (for positional rules) a structured `reorder_action` handoff signal.
- A `tab_order_report/1` handoff for downstream consumers (dashboard-caption-audit, publish-readiness, workbook-auditor).
- Deterministic sort order so re-runs produce byte-identical output.

## Limitations

- Entry-point is user-declared, not auto-detected. If you decline to declare a flow, DT-ENTRY-01, DT-DRILL-02, DT-EXCEPTION-03, and DT-ORPHAN-04 mark as n/a.
- DT-DEVICE-08 fires only when a device layout is human-authored. Tableau's default Phone layouts (auto-generated on every dashboard) are correctly excluded.
- Hidden dashboards can only be hidden via Story membership in the current Tableau version (platform gap). Right-click dashboard hide is not directly available.
- Reorders are not applied automatically. Follow the drag-to-fix steps for each finding.

## Troubleshooting

- **"Skill won't proceed without a flow declaration."** Either declare your entry-point / drill-down / exception structure, or explicitly decline flow-metadata to skip the four flow-dependent rules.
- **"DT-DEVICE-08 fired on every dashboard."** Should not happen. If it does, the auto-generated-defaults filter may not be working; file a bug.
- **"Recommended reorder doesn't match my intent."** The rule is inferring from your declared flow. If your intent differs, restate the flow declaration or override the recommendation manually.

## Support

File issues in the Tableau Studio Agent Skills repo.
