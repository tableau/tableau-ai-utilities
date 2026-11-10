# Testability Scope

| Interaction Type | Testable? | Method |
|---|---|---|
| Dashboard filter actions (select mark on source → target filters) | **No (confirmed 2026-08-07)** | Filter actions fire on mark selection, not on a Filters-shelf filter. No tool can reach the Filters shelf (`add-field`'s `target` only supports `rows`/`cols`/`encoding`) and no tool simulates a mark click. Report "cannot verify, manual check required" rather than attempting the filter-on-source approximation described in the old method column. |
| Parameter changes → sheet response | **No (confirmed 2026-08-07)** | `author-parameter` only creates parameters — calling it again on an existing caption errors with "caption collision" rather than updating the value, and no tool sets an existing parameter's current value. Report "cannot verify, manual check required." |
| Set actions (mark selection → set membership → downstream calc/filter) | **No (confirmed 2026-08-07)** | Same mark-selection gap as filter actions — a Change Set Values action fires on Select, and nothing here can simulate that. Report "cannot verify, manual check required." |
| Highlight actions | Partial | Detect only if the target's mark count changes (which means it's also filtering, not just highlighting). Highlighting alone has no data signature — flag "visual-only, not empirically verifiable." |
| Tooltip interactions | Partial | Can confirm tooltip field is present on Detail shelf via summary data, but cannot verify visual rendering. Report: "Tooltip field [X] present on Detail — likely visible on hover, but visual confirmation requires manual check." |
| URL actions | No | No browser/web tool in Desktop. Report "cannot verify, manual check required." |
| Cross-datasource filter behavior | **No (confirmed 2026-08-07)** | Inherits the same filter-simulation gap as dashboard filter actions above — can still flag likely same-concept/different-name dimension pairs by inspection (that part doesn't need triggering anything), but cannot confirm active/inactive behavior. |
| Go-to-sheet actions | No | No navigation tool available. Report as untestable. |
| Dynamic zone visibility (parameter/field-driven zone show/hide) | **No** | Detection-only: can spot a candidate boolean parameter/calc by name from field inventory, but no tool reads dashboard-zone XML to confirm a zone's "Control visibility using" binding, and the same parameter-value-set gap blocks triggering the toggle. Report the candidate (if any) and require manual confirmation in Desktop's zone Layout pane. |

## Known Limitations

1. This skill detects symptoms (target didn't respond), never root cause
   (wrong field mapping, target excluded from the action, action disabled).
   Root cause needs action-config XML that no Desktop tool currently reads.
2. Highlight actions can't be empirically verified through data diffing alone.
3. Tooltip interactions are only verifiable at the field-presence level, not
   visual rendering.
4. URL and go-to-sheet actions are untestable in this environment.
5. Set detection depends entirely on whether sets surface in field inventory
   or calc formulas. If they don't, the user has to name the set.
6. Filter-action sweeps are O(source sheets x target sheets) — capped at 6
   source sheets per dashboard (user-overridable) to keep test time reasonable.
7. **Confirmed 2026-08-07 — none of the three primary interaction types (parameter, filter action, set action) can actually be empirically triggered in this environment**, superseding this file's earlier "Yes"/testable claims for all three:
   - No tool can update an existing parameter's current value. `author-parameter` is create-only; calling it again on an existing caption throws "caption collision" instead of setting the value, and no other tool sets it.
   - No tool can reach the Filters shelf to approximate a filter-action source selection. `add-field`'s `target` parameter only accepts `rows`/`cols`/`encoding` — this was previously known for filter promotion but applies equally here, since the skill's Phase 2 method (`"Apply a filter isolating one member of that dimension on the source sheet"`) requires exactly that shelf.
   - No tool simulates a mark click/selection, which is what both filter actions and Change Set Values actions actually fire on — applying a Filters-shelf filter is not equivalent to a selection event even where the shelf were reachable.
   - **Practical consequence:** Phases 1-3 as written cannot execute as designed. Report all three interaction types per-instance as "cannot verify, manual check required" rather than attempting the described diff method, and do not conclude dead wiring from a lack of tool-driven response.
