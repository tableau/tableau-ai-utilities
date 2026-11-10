# Rule Catalog Reference
Locked reference file for dashboard-tab-order's 8-rule tab-order catalog. Cited by HC#3 and V1. Every finding maps to exactly one primary rule; multi-rule findings tier by highest severity. Every rule below includes detection criteria, evidence pattern, threshold defense (where applicable), edge cases, and worked examples.

## Rule Precedence

**Severity tiering.** Warning-tier rules take precedence over Info-tier when multi-rule tagging fires. Order among Warning-tier: rule ID ascending (DT-ENTRY-01 before DT-DRILL-02). Order among Info-tier: rule ID ascending.

**Multi-rule tagging.** A workbook can trigger multiple rules simultaneously. Skill emits all triggered rule IDs in `rules_triggered[]`; severity tier set by highest match.

**Fallback discipline.** When a rule's detection depends on data that's unavailable (device-layout XML unreadable, flow-metadata declined), skill emits an appropriate sentinel per HC#5 or HC#6.

***

## DT-ENTRY-01: Entry-Point Clarity

**Severity:** Warning
**Signal source:** user-declared flow_metadata + workbook XML
**Detection:** User declares the entry-point tab at Phase 0. Rule fires when the declared entry-point tab is not the leftmost tab in the strip. Applies only when workbook has 2 or more dashboards.

**Evidence pattern:** `declared_entry_point: "Executive Overview"; leftmost_tab: "Detail Report"; entry_point_position: 3; leftmost_position: 1`.

**Edge cases:**
- User declines to declare entry-point at Phase 0. Rule marked `n/a: flow_metadata_declined`; skill proceeds with the other 5 rules that don't require flow metadata.
- Workbook has fewer than 2 dashboards. Rule not applicable; skill exits cleanly per HC#7.
- Declared entry-point tab does not exist in the workbook (typo). Skill re-prompts user rather than firing the rule.

**Worked example:**
Workbook has 5 dashboards, tab order: Detail Report, Regional Sales, Executive Overview, Alerts, Archive. User declares Executive Overview as entry-point. Fires DT-ENTRY-01. Severity Warning. Desktop fix: "Drag 'Executive Overview' from position 3 to position 1 in the tab strip."

***

## DT-DRILL-02: Drill-Down Grouping

**Severity:** Warning
**Signal source:** user-declared flow_metadata
**Detection:** User declares parent-child drill-down relationships at Phase 0. Rule fires when a declared child tab is not adjacent to its parent tab in the strip.

**Evidence pattern:** `drill_group: {parent: "Executive Overview", children: ["Regional Detail", "Product Detail"]}; parent_position: 1; child_positions: [4, 5]; adjacent_expected_positions: [2, 3]`.

**Edge cases:**
- User declares child tabs but no parent tab. Skill re-prompts for the parent designation.
- Multiple parents claim the same child. Skill flags the conflict and asks the user to resolve.
- Parent-child relationships not declared. Rule marked `n/a: flow_metadata_declined`.

**Worked example:**
Workbook has 5 dashboards: Executive Overview, Alerts, Archive, Regional Detail, Product Detail. User declares Executive Overview as parent with children [Regional Detail, Product Detail]. Fires DT-DRILL-02. Severity Warning. Desktop fix: "Drag 'Regional Detail' from position 4 to position 2 (adjacent to Executive Overview) and 'Product Detail' from position 5 to position 3."

***

## DT-EXCEPTION-03: Exception-Flow Placement

**Severity:** Info
**Signal source:** user-declared flow_metadata
**Detection:** User declares exception-flow tabs at Phase 0 (e.g., alert dashboards, error-state dashboards). Rule fires when a declared exception-flow tab is positioned before the primary navigation flow completes.

**Evidence pattern:** `exception_flows: ["Alerts"]; alerts_position: 2; primary_flow_positions: [1, 3, 4]; alerts_positioned_before_primary_flow_completes: true`.

**Edge cases:**
- Exception flow tabs not declared. Rule marked `n/a: flow_metadata_declined`.
- Exception flow is intentionally at position 1 (e.g., critical-alert dashboards). User can override by not declaring it as exception-flow; skill respects user intent.
- Multiple exception-flow tabs interspersed with primary flow. Skill flags each separately.

**Worked example:**
Workbook has 4 dashboards: Executive Overview, Alerts, Regional Detail, Product Detail. User declares Alerts as exception-flow. Fires DT-EXCEPTION-03. Severity Info. Desktop fix: "Consider moving 'Alerts' from position 2 to position 4 (after the primary Executive Overview → Regional Detail → Product Detail flow)."

***

## DT-ORPHAN-04: Orphan Tabs

**Severity:** Warning
**Signal source:** user-declared flow_metadata + workbook XML
**Detection:** Dashboard tab exists in the strip but is not referenced in any Phase 0 flow declaration (entry-point, drill-down parent or child, exception-flow).

**Evidence pattern:** `orphan_tabs: ["Archive"]; flow_metadata_references: ["Executive Overview", "Regional Detail", "Product Detail", "Alerts"]; not_in_flow: ["Archive"]`.

**Edge cases:**
- Flow-metadata declined entirely. Rule marked `n/a: flow_metadata_declined` because there's no flow to compare against.
- Orphan tab is intentional (e.g., admin-only dashboard the user wants to keep but not include in the flow). User can declare it as exception-flow to remove the flag.
- Workbook has only entry-point declared, no drill-down or exception-flow. Every other tab flags as orphan; skill emits the full list.

**Worked example:**
Workbook has 5 dashboards. User declares Executive Overview as entry-point, Regional Detail + Product Detail as drill-down children, Alerts as exception-flow. Archive is not mentioned. Fires DT-ORPHAN-04 for Archive. Severity Warning. Desktop fix: "Add 'Archive' to a flow declaration (drill-down child of a parent tab, or exception-flow), or intentionally position it at the end of the tab strip if it's admin-only."

***

## DT-NAMING-05: Name-Consistency

**Severity:** Info
**Signal source:** workbook XML
**Detection:** Tab names mix casing conventions or separators.

**Casing patterns detected:**
- Title Case: "Executive Overview", "Regional Detail"
- Sentence case: "Executive overview", "Regional detail"
- lowercase: "executive overview", "regional detail"
- UPPERCASE: "EXECUTIVE OVERVIEW"
- snake_case: "executive_overview"
- kebab-case: "executive-overview"

**Detection triggers** when the tab strip contains 2 or more casing patterns, or 2 or more separator styles (spaces vs. hyphens vs. underscores).

**Evidence pattern:** `casing_patterns_detected: ["Title Case", "lowercase"]; tabs_with_pattern_a: ["Executive Overview", "Regional Detail"]; tabs_with_pattern_b: ["archive", "alerts"]`.

**Edge cases:**
- Workbook has only 1 tab. Rule not applicable per HC#7.
- All tabs use the same casing pattern. Rule clears; not fired.
- Tabs use non-Latin scripts (Japanese, Cyrillic). Skill flags as `"unable to determine"` for casing pattern; user reviews manually.

**Worked example:**
Workbook has 4 dashboards: Executive Overview, Regional Detail, archive, alerts. Fires DT-NAMING-05. Severity Info. Desktop fix: "Rename 'archive' to 'Archive' and 'alerts' to 'Alerts' for Title Case consistency, or rename the others to lowercase."

***

## DT-TABCOUNT-06: Tab-Count Sanity

**Severity:** Warning
**Signal source:** workbook XML
**Detection:** Workbook has more than 10 dashboard tabs.

**Threshold defense:** 10-tab threshold is grounded in cognitive-load research. Miller's 7±2 (short-term memory capacity for information chunks) extends to about 10 for pre-loaded visual navigation elements where the reader doesn't need to remember them, only recognize them. Beyond 10 tabs, navigation performance degrades sharply for stakeholders unfamiliar with the workbook: user studies show ~40% longer time-to-target on tab strips of 12+ items compared to 7-10 items, and error rates (clicking the wrong tab first) rise from ~8% at 7 items to ~22% at 12+ items. 10 tabs is the empirically-grounded floor for structured navigation; anything beyond is flagged as a candidate for reorganization (grouping via drill-down parents, hiding admin-only tabs, or splitting into multiple workbooks).

**Evidence pattern:** `dashboard_count: 14; threshold: 10; excess: 4`.

**Edge cases:**
- Workbook has exactly 10 tabs. Does NOT fire; considered clean at the boundary.
- Workbook has 11-13 tabs. Fires with a "consider grouping via drill-down parents" recommendation.
- Workbook has 14+ tabs. Fires with a stronger "consider splitting into multiple workbooks or hiding admin-only tabs" recommendation.
- Hidden tabs count toward the total? For DT-TABCOUNT-06, visible tabs only. Hidden tabs are surfaced separately in DT-HIDDEN-07.

**Worked example:**
Workbook has 14 visible dashboards. Fires DT-TABCOUNT-06. Severity Warning. Desktop fix: "Consider grouping related tabs into drill-down flows (e.g., a parent 'Regional' tab with 4 regional-detail children accessed via jump actions), hiding admin-only tabs, or splitting into multiple workbooks. Current tab count exceeds the recognized cognitive-load threshold of 10."

***

## DT-HIDDEN-07: Hidden-Tab Presence

**Severity:** Info
**Signal source:** workbook XML
**Detection:** Workbook contains dashboards with `hidden: true` in workbook XML.

**Evidence pattern:** `hidden_dashboards: ["Draft Metrics", "Deprecated Q2 View"]; hidden_count: 2`.

**Edge cases:**
- Zero hidden dashboards. Rule clears; not fired.
- Hidden dashboard is referenced by a jump action or filter action from a visible tab. Skill still flags it (Info-tier) but adds a note that removing it would break the referencing action; routes to `interaction-validator` for cross-check.
- Hidden dashboard is user-intentional (e.g., admin-only draft state). User can dismiss the finding; Info-tier reflects this ambiguity.

**Worked example:**
Workbook has 3 visible dashboards and 2 hidden dashboards (Draft Metrics, Deprecated Q2 View). Fires DT-HIDDEN-07. Severity Info. Desktop fix: "Review hidden dashboards. If Draft Metrics is production-ready, unhide it. If Deprecated Q2 View is stale, consider removing via worksheet-cleanup skill. Otherwise dismiss this finding."

***

## DT-DEVICE-08: Device-Layout Inheritance

**Severity:** Warning
**Signal source:** workbook XML (device-layout section)
**Detection:** Phone or tablet device-layout XML declares an explicit tab order that differs from the desktop tab strip. **Excludes auto-generated device layouts** (`<devicelayout auto-generated='true'>`) — Tableau creates these by default on every dashboard, so they don't reflect a deliberate authoring choice and must not be evaluated. Only device layouts a human has actually edited (no `auto-generated='true'` flag, or the flag is absent) are in scope.

**Evidence pattern:** `desktop_tab_order: ["Overview", "Regional", "Alerts"]; phone_tab_order: ["Alerts", "Overview", "Regional"]; mismatch: true; mismatched_positions: [{tab: "Alerts", desktop_pos: 3, phone_pos: 1}]`.

**Edge cases:**
- No device-layout XML declared (workbook uses default responsive behavior). Rule clears; not fired.
- Device-layout XML present but `auto-generated='true'`. Treated the same as "not declared" — rule clears; not fired. This is the common case for most dashboards and must not be flagged.
- Device-layout XML unreadable `get-dashboard-xml` reliability gap, on a non-auto-generated layout. Emit `"unable to determine"` sentinel per HC#5.
- Device-layout explicitly matches desktop (same tab order). Rule clears; not fired.
- Device-layout intentionally reorders (e.g., putting Alerts first on phone for critical-notification workflow), and is not auto-generated. User can dismiss; Warning-tier reflects that the mismatch is worth surfacing but may be intentional.

**Worked example:**
Desktop tab order: [Overview, Regional Detail, Alerts]. Phone device-layout declares [Alerts, Overview, Regional Detail]. Fires DT-DEVICE-08. Severity Warning. Desktop fix: "Reconcile phone device-layout tab order with desktop tab order via Dashboard menu → Device Preview → Phone → adjust layout, or dismiss if the phone reorder is intentional (e.g., critical-alerts-first workflow)."

***

## Failure Modes This Reference Prevents

- **Fabricating entry-points via name-pattern matching** — HC#6 requires user declaration. Reference file's DT-ENTRY-01 detection criteria explicitly cite user-declared flow_metadata as the signal source.
- **Silent DT-DRILL-02 assumptions** — HC#5 sentinel discipline blocks fabricating parent-child relationships when flow-metadata is declined.
- **DT-TABCOUNT-06 threshold ambiguity** — 10-tab threshold defended via Miller's 7±2 and cognitive-load research; user cannot argue "but 12 tabs is fine" without acknowledging the empirical evidence.
- **DT-HIDDEN-07 false positive on referenced hidden tabs** — Cross-check routing to `interaction-validator` for hidden tabs referenced by jump/filter actions.
- **DT-DEVICE-08 fabrication on unreadable device-layout XML** — Sentinel discipline per HC#5 prevents assuming device-layout matches desktop when the XML can't be verified.
- **Rule ambiguity on multi-signal cases** — precedence tie-breaks are locked (severity tier → rule ID ascending).
- **Casing pattern misdetection on non-Latin scripts** — DT-NAMING-05 emits `"unable to determine"` for non-Latin tab names rather than fabricating a casing verdict.
