# Interaction Validation Report Format

Render as plain markdown, bullet points instead of tables where the chat
surface doesn't render tables well (mirror data-quality-review's convention:
use bullets, not tables, in the actual chat response — the pipe tables below
are the internal design shape, not the literal render format).

## Overflow Rule

If any list in the report exceeds 8 items, group by pattern rather than
enumerating each item individually. For example:
- Instead of listing 12 non-responsive sheets one by one, write: "All 12 sheets in Zone 2 non-responsive to [parameter]"
- Instead of listing 9 responsive targets, write: "All sheets except [Sheet A, Sheet B] responded"

This keeps reports scannable even for large dashboards.

```
# Interaction Validation Report
## Dashboard: [name]
## Date: [today's date]

### Summary
- Parameters: X found — [tool-triggered: Y responsive, Z dead] OR [cannot verify: no tool sets an existing parameter's value, see 2026-08-07 note]
- Filter actions: X source sheets — [tool-triggered results] OR [cannot verify: no tool reaches Filters shelf or simulates a mark selection]
- Set actions: X — [tool-triggered results] OR [cannot verify: same mark-selection gap]
- Dynamic zone visibility: X candidate(s) found — manually confirmed [working / broken / not checked]
- Highlight actions: manually confirmed [working / broken / not checked] (visual-only — mark-count diff only if it's also filtering)
- Tooltip interactions: X field(s) confirmed present on Tooltip/Detail via data read
- Cross-DS filters: [active / inactive / not applicable] — if inactive, name-mismatch or missing-link (see Common Causes)

**As of 2026-08-07, most interaction types cannot be triggered by any tool in
this environment** (no command sets an existing parameter's value, reaches the
Filters shelf, or simulates a mark selection). Where that applies, this report
states "wiring present, cannot verify" rather than a false pass/fail, and asks
the user to manually click-test and report back. Treat user-reported manual
results as authoritative — log them as confirmed, not "unverified."

### Parameter Results
- **[Parameter name]** — [if tool-triggered: tested old->new value, responsive/non-responsive sheets] OR [cannot verify from here — ask user to manually toggle the control and report which sheets respond]

### Filter Action Results
- **[Source sheet] -> [target sheet(s)]** — dimension [field]. [If tool-triggered: coverage] OR [cannot verify from here — ask user to click a mark and report which targets filtered]

### Set Action Results
- **[Set name]** — source [sheet], target set [set]. [If tool-triggered: results] OR [cannot verify from here — ask user to click a mark and report set membership change]

### Dynamic Zone Visibility Results
- **[Zone]** controlled by **[parameter/field]** — [manually confirmed working/broken, per user report] OR [candidate found, not yet confirmed — ask user to toggle and report]

### Cross-Datasource Filter Results
- Shared dimension: [name]. Source DS: [...]. Target DS: [...]. Active: [yes/no, per user report]. If inactive: check both (1) exact name match and (2) field-linking (chain-link icon in Data pane) — matching names alone do not guarantee cross-DS propagation (user-confirmed 2026-08-07).

### Dead Wiring (Action Required)
[Confirmed-dead items — either from a tool-driven diff, or from user-reported manual testing. Include "Probable cause:" line from the Common Causes table for each item.]

### Not Connected (Likely Intentional)
[Non-responses where the target has no shared dimension — probably deliberate]

### Untestable Items

**When 3+ interaction types share the same blocking reason** (e.g., all require
mark selection or parameter-value-set), collapse them into a single grouped
block rather than repeating the limitation per item:

- **Blocked by: [shared reason, e.g. "no tool simulates mark selection"]**
  Affected: [Parameter sweep (X parameters), Filter actions (Y source sheets), Set actions (Z sets), Cross-DS filters]
  Manual test: [one consolidated instruction, e.g. "Click marks on each source sheet and confirm targets respond. Toggle each parameter control and confirm dependent sheets update."]

**When fewer than 3 items are untestable**, list individually:
- [Interaction type] — [specific reason]. Manual test: [specific instruction].

Always end with a count: "X of Y interaction types require manual verification."

### Recommendations
[1-3 concrete, actionable next steps based on the findings above]
```

Omit a section entirely if that phase found nothing to test (e.g. no
parameters exist in the workbook) — don't render an empty table/list with a
"none found" placeholder unless it's a meaningful negative (e.g. "Cross-DS
filters: not applicable, single datasource").
