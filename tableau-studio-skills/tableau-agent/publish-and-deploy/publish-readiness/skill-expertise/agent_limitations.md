# Tableau Studio Agent: Known Limitations

Comprehensive reference of confirmed platform constraints. Every item below was verified through live testing (July through August 2026), not assumed from documentation. This informs what this skill (and any Desktop skill) can and cannot do.

***

## Dashboard Assembly

| Limitation | Impact | Workaround |
|-----------|--------|------------|
| No zone-move/reparent command | Sheets can only be appended via default auto-tiling. No control over specific placement, columns, or rows. | Provide manual Desktop instructions with ASCII wireframes. |
| No view-fit command | Cannot set Standard / Fit Width / Fit Height / Entire View programmatically. | Give recommendations by chart type with exact menu paths (right-click sheet on dashboard > Fit > [value]). |
| No dashboard canvas-size command | Cannot set fixed width x height. | Manual instruction: Dashboard > Size > Fixed > [dimensions]. |
| No visual/screenshot capability | Agent cannot see a rendered chart or dashboard. Any spacing, clipping, or contrast judgment requires human confirmation. | Always ask the user to verify visual results. |
| Raw dashboard XML is not a safe workaround | Required tools (get-workbook-xml, apply-workbook, apply-dashboard-with-viewpoints) aren't exposed. Documented hard-crash risk can wipe the whole workbook. | Do not attempt XML-based assembly under any circumstances. |

**Result:** All dashboard assembly is instructions-only, with no exception for even simple "just place these existing sheets" requests.

***

## Object Lifecycle Gaps

| Limitation | Impact | Workaround |
|-----------|--------|------------|
| No delete-field / delete-calc command | Any diagnostic or scratch calc created is permanent unless the user deletes it manually. | State upfront before creating anything; get user approval. |
| No Filters-shelf placement via tools | `add-field` target only supports rows, cols, and encoding. Cannot place fields on Filters shelf. | Manual drag instruction. |
| No context-filter promotion command | Cannot promote a filter to Context via tools. | Manual right-click instruction. |
| Sets invisible to field-resolution and shelf-placement tools | `resolve-field` and `list-available-fields` don't surface sets regardless of how they were created. Unreliable for automated use. | Prefer calculated fields; manual set-creation instructions when sets are truly needed. |
| `author-parameter` deterministically broken on Windows | Crashes with `spawn ps ENOENT`. Never called. | All parameter creation is manual. Provide exact Desktop instructions. |
| `author-set` in top-n mode produces broken sets | Set can be broken even in the native Desktop UI, not just unverifiable. | Route to a RANK-based calc workaround instead. |
| No COUNT/COUNTD binding onto dimensions via chart templates | `bind-template` cannot produce COUNTD(Dimension). | Author a SUM(1) helper calc and use SUM instead. |
| Dual-axis merge not programmable | Requires one manual Desktop click even when everything else is automated. | Provide click instruction: right-click right axis > Synchronize Axis. |

***

## Reliability Gaps

| Limitation | Impact | Workaround |
|-----------|--------|------------|
| `get-worksheet-xml` 500s on dashboard-bound sheets | Repeatedly fails with 500/operation-failed errors on sheets placed on a dashboard with real data. Not a one-off. | Avoid calling on dashboard-bound sheets. Fall back to field-usage inference. Note "not checked" for affected sheets. |
| `build-and-apply-worksheet` causes calc corruption | Confirmed across 3 independent test runs on datasources with parameter-referencing calcs. Corruption is invisible to formula-text readback (formula reads back unchanged while live behavior is broken). | Hard-stop: never call worksheet-shelf-mutating tools on datasources with parameter-referencing calcs. |
| Whole-workbook preflight validation returns cached errors | Can produce a static error list unrelated to what's being built. A KPI bound to an unrelated datasource produced errors referencing fields from a different datasource. | Test against an unrelated datasource before concluding workbook corruption. Suspected validator bug. |
| `apply-worksheet` intermittently flaky | Can hang behind a blocked Desktop dialog, not just fail cleanly. | Use one-shot builds (`build-and-apply-worksheet`) as default; batch as fallback. Check for blocking modal if call hangs. |

***

## Interaction / Behavioral Testing

| Limitation | Impact | Workaround |
|-----------|--------|------------|
| No tool sets an existing parameter's value | Cannot empirically trigger or verify parameter-driven behavior. `author-parameter` is create-only and crashes on existing captions ("caption collision"). | Detect wiring structurally ("parameter referenced in calc on shelf"). Report "cannot verify, manual check required." |
| No tool simulates mark selection | Filter actions and set actions fire on mark selection, which cannot be programmatically triggered. | Detect that filter/set action sources and targets exist. Cannot verify they respond. Manual click instructions. |
| Dynamic zone visibility: detection-only | Can spot candidate boolean parameter/calc by name pattern. Cannot confirm zone binding or trigger toggle. | Report "candidate detected" with low confidence. Manual verification via Layout pane. |
| No action-configuration read | Cannot see which sheets a filter action targets or which fields are mapped. | Report symptoms ("Sheet X did not respond") not root cause. Append probable causes from known-patterns table. |

***

## Environment-Wide

| Limitation | Impact | Workaround |
|-----------|--------|------------|
| Blocking modal dialogs during operations | Tableau Studio shows modal popups during many agent operations (worksheet creation, field placement, calc authoring, template binding) that must be manually dismissed. Cosmetic only (not failures), but disruptive. Cannot be suppressed. | Skill instructions note that users should expect to dismiss popups. If a tool call hangs, ask user to check Desktop for a blocking dialog. |
| No REST API access | Anything requiring Server/Cloud site-wide operations is out of scope: governance scans, Pulse, published-datasource content search, permissions, refresh schedules. | Desktop-only scope. Post-publish items are reminder checklists, not tool-verified findings. |
| No document-conversion tool | Output files limited to `.txt` and `.md`. Cannot produce `.docx`, `.pdf`, or `.pptx`. | Write markdown/text output. User can convert if needed. |

***

## Implications for This Skill (Publish Readiness)

Given the above, this skill:

1. **Cannot verify any interactivity** (filter actions, parameter behavior, set actions, dynamic zones). These are user-verified reminder items only.
2. **Cannot see formatting** (colors, fonts, tooltips, borders, chart labels, axis visibility). Visual checks require human eyes.
3. **Cannot test performance empirically** (no timing, no Performance Recorder access). Performance checks detect known risk patterns from structure, not measured load times.
4. **Cannot inspect filter configuration** (scope, "Only Relevant Values", "Show Apply Button", context filter status). Filter checks are limited to field/count detection.
5. **Cannot read dashboard layout** (container structure, zone positions, sizing). Layout checks are not possible.
6. **Cannot verify export formatting** (PDF, PPT, Excel output). User must test manually.
7. **Cannot set post-publish configuration** (refresh schedules, permissions, RLS, descriptions). These are reminders only.
8. **Cannot delete anything it finds.** Every finding is a suggestion with a manual instruction, never an autonomous fix.

The skill's design accounts for all of this by clearly separating tool-verified findings from user-verified reminders, and by never claiming to have checked something it structurally cannot inspect.
