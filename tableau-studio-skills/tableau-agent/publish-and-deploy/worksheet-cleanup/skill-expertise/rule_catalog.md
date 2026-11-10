# Rule Catalog Reference
Locked reference file for worksheet-cleanup's 8-rule cleanup catalog. Cited by HC#13 and V1. Every candidate maps to exactly one primary rule; multi-rule candidates tier by highest severity. Every rule below includes detection criteria, evidence pattern, edge cases, and worked examples.

## Rule Precedence

**Severity tiering.** Warning-tier rules take precedence over Info-tier when multi-rule tagging fires. Order among Warning-tier: rule ID ascending (WC-ORPHAN-01 before WC-HIDDEN-02). Order among Info-tier: rule ID ascending.

**Multi-rule tagging.** A candidate can trigger multiple rules simultaneously (common for orphaned + hidden + empty combinations). Skill emits all triggered rule IDs in `rules_triggered[]`; severity tier set by highest match.

**Fallback discipline.** When a rule's detection depends on a platform tool that's unavailable or unreliable (a known platform gap), skill emits sentinel `"unable to determine"` for that rule per HC#5. Rule is not treated as either true or false; user sees the sentinel and decides.

***

## WC-ORPHAN-01: Orphaned Scratch Sheet

**Severity:** Warning
**Detection:** `get-workbook-inventory` returns worksheet with `dashboard_placements: []` (zero placements) AND worksheet is not `hidden: true`.

**Evidence pattern:** `worksheet_name: "..."; dashboard_placements: []; hidden: false`.

**Edge cases:**
- Worksheet on a dashboard that was recently deleted → fires WC-ORPHAN-01 (correct behavior; the worksheet is now genuinely orphaned).
- Worksheet used as a filter-action source but not visually placed → fires WC-ORPHAN-01 with action-config-warning tier if the action reference is unverifiable.
- Newly-created worksheet before user places it on a dashboard → fires WC-ORPHAN-01 (expected in early workbook state).

**Worked example:**

Superstore has a worksheet `Sales by Region-Draft`. It is not on any dashboard, not hidden. Fires WC-ORPHAN-01. Severity Warning. Recommended action: `remove`.

***

## WC-HIDDEN-02: Hidden Worksheet with No Dashboard Use

**Severity:** Warning
**Detection:** Worksheet has `hidden: true` in XML AND `dashboard_placements: []`.

**Evidence pattern:** `worksheet_name: "..."; hidden: true; dashboard_placements: []`.

**Edge cases:**
- Worksheet hidden because it is used as a data source for another worksheet via cross-sheet action → fires WC-HIDDEN-02 with action-config-warning tier per HC#3.
- Worksheet hidden by user for temporary staging → fires WC-HIDDEN-02 (correct behavior; if user meant to keep it, they respond "keep" in Phase 2).
- Worksheet hidden AND placed on a dashboard → does NOT fire WC-HIDDEN-02 (dashboard_placements non-empty).

**Worked example:**

Superstore has a worksheet `Old-Analysis-Q2` marked hidden, not on any dashboard. Fires WC-HIDDEN-02 AND WC-ORPHAN-01 (multi-rule tagging). Severity Warning. Recommended action: `remove`.

***

## WC-EMPTY-03: Empty Shelves

**Severity:** Warning
**Detection:** `get-worksheet-xml` returns worksheet with all mark-shelf placements empty: no fields on Rows, Columns, Text, Detail, Color, Size, Shape, Tooltip, Label, or Filter shelves. Parameter-only placements are excluded from the empty check.

**Evidence pattern:** `worksheet_name: "..."; shelves: {rows: [], columns: [], marks: {detail: [], color: [], ...}, filters: []}`.

**Edge cases:**
- Worksheet with a parameter dragged onto Filter shelf but no measures/dimensions → does NOT fire WC-EMPTY-03 (parameter-only placement).
- Worksheet with a hidden field on Detail → fires WC-EMPTY-03 (hidden fields don't count as active placements for this rule).
- `get-worksheet-xml` reliability gap on dashboard-bound sheets → skill emits `"unable to determine"` sentinel for WC-EMPTY-03 per HC#5. No false positive.

**Worked example:**

Superstore has a worksheet `Blank Test` created by dragging a chart type from the Show Me panel but then having every field removed. Fires WC-EMPTY-03. Severity Warning. Recommended action: `remove` (or `investigate` if the user recalls creating it for a specific purpose).

***

## WC-DUPE-04: Duplicate Near-Identical Worksheet

**Severity:** Info
**Detection:** Two or more worksheets with identical shelf configurations AND identical field references AND identical mark type. Skill treats all matching worksheets as duplicate candidates.

**Evidence pattern:** `duplicate_group: [worksheet_a, worksheet_b, ...]; identical_shelves: true; identical_fields: true; identical_mark_type: true`.

**Edge cases:**
- Two worksheets with same shelves but different filters → does NOT fire WC-DUPE-04 (filter difference means intent difference).
- Two worksheets with same shelves and fields but different names (`Sales by Region`, `Sales by Region v2`) → fires WC-DUPE-04. Naming variance is expected; content variance is what the rule checks.
- Exact-match only. Near-duplicates with minor formatting differences (e.g., different color palette applied) are NOT caught.

**Worked example:**

Superstore has `Region-Bar-A` and `Region-Bar-B`, both showing SUM(Sales) by Region on a bar chart with identical filters. Fires WC-DUPE-04 for both. Skill lists both as duplicate candidates. User picks which to keep. Severity Info.

***

## WC-DEAD-FIELD-05: Worksheet Bound to Deleted Fields

**Severity:** Warning
**Detection:** Worksheet has shelf placements referencing fields that `resolve-field` fails to locate on the active datasource. Sentinel `unresolved: <field_name>` populates.

**Evidence pattern:** `worksheet_name: "..."; broken_field_refs: ["<field_name>"]; resolve_status: unresolved`.

**Edge cases:**
- Calc referenced on a shelf was deleted → fires WC-DEAD-FIELD-05.
- Field renamed on datasource → fires WC-DEAD-FIELD-05 (Tableau's rename-detection isn't always propagated to shelf refs, so the shelf ref becomes broken).
- Field exists on a different datasource than the worksheet's active DS → fires WC-DEAD-FIELD-05 for the active DS scope. Skill notes `cross_datasource_reference: <source_ds>.<field>` if that's the case.
- `resolve-field` case-sensitivity concern: if the shelf ref uses a different case than the actual field name, WC-DEAD-FIELD-05 will fire incorrectly. Skill notes this in evidence and recommends manual verification before removal.

**Worked example:**

Superstore has a worksheet `Container Cost Analysis`. The referenced calc `[Container Cost]` was deleted from the Orders datasource. Fires WC-DEAD-FIELD-05. Severity Warning. Recommended action: `investigate` (worksheet may be salvageable if user recreates the calc; recommend `remove` only after user confirms the calc is genuinely gone).

***

## WC-DEFAULT-NAME-06: Default Name + No Shelf Content

**Severity:** Warning
**Detection:** Worksheet name matches default patterns AND WC-EMPTY-03 also fires. Both conditions required to reduce false positives on legitimate placeholder sheets.

**Default name patterns (locked, case-sensitive):**
- English: `Sheet 1`, `Sheet 2`, ..., `Sheet N` (numeric suffix)
- French: `Feuille 1`, `Feuille 2`, ..., `Feuille N`
- Spanish: `Hoja 1`, `Hoja 2`, ..., `Hoja N`
- German: `Blatt 1`, `Blatt 2`, ..., `Blatt N`

**Evidence pattern:** `worksheet_name: "Sheet 3"; matches_default_pattern: true; empty_shelves: true`.

**Edge cases:**
- Worksheet named `Sheet 1` with content on shelves → does NOT fire WC-DEFAULT-NAME-06 (WC-EMPTY-03 condition unmet). User may have kept the default name intentionally.
- Worksheet named `Sheet-Alpha` (custom, not matching pattern) with empty shelves → fires WC-EMPTY-03 only, not WC-DEFAULT-NAME-06.
- Locales beyond the four supported → skill emits `"unable to determine"` sentinel for the name check. Rule still fires on WC-EMPTY-03 alone if applicable.

**Worked example:**

Superstore has `Sheet 5` created by a Show Me click and then abandoned. Empty shelves. Fires WC-DEFAULT-NAME-06 AND WC-EMPTY-03. Severity Warning. Recommended action: `remove`.

***

## WC-FORMULA-ONLY-07: Formula-Only Worksheet (Unused Calc Placeholders)

**Severity:** Info
**Detection:** Every field on the worksheet is a calculated field, AND the worksheet is not on any dashboard, AND all calcs are also unused elsewhere in the workbook. All three conditions must be true. Weak signal by design.

**Evidence pattern:** `worksheet_name: "..."; fields_on_shelves: ["<calc_a>", "<calc_b>"]; all_calculated_fields: true; dashboard_placements: []; calcs_used_elsewhere: false`.

**Edge cases:**
- Worksheet with two calcs where one is used on another worksheet → does NOT fire WC-FORMULA-ONLY-07 (third condition unmet).
- Worksheet with one row-level calc and one native field → does NOT fire WC-FORMULA-ONLY-07 (second condition unmet: not all calculated).
- Calc-usage analysis requires calc-documenter's handoff. Without it, skill emits `"unable to determine"` sentinel per HC#5.

**Worked example:**

Superstore has a worksheet `Calc Sandbox` using only `[Profit Ratio Custom]` and `[Sales x1.5]`, not on any dashboard, and both calcs are unreferenced anywhere else. Fires WC-FORMULA-ONLY-07. Severity Info. Recommended action: `remove` (or `keep` if user wants the calcs preserved via the sandbox; user's call).

***

## WC-DZV-ONLY-08: Dynamic Zone Visibility Target Only

**Severity:** Info
**Detection:** Worksheet appears in a dashboard exclusively via a Dynamic Zone Visibility (DZV) parameter binding, with no direct dashboard placement (zone or floating). Requires successful parameter-binding traversal.

**Evidence pattern:** `worksheet_name: "..."; direct_placements: []; dzv_bindings: [{dashboard: "...", parameter: "...", condition: "..."}]; parameter_traversal_status: successful`.

**Edge cases:**
- Parameter unreadable (a known platform gap) → skill emits `"unable to determine"` sentinel for WC-DZV-ONLY-08 detection per HC#5. Rule does not fire when detection is unreliable. Prevents false positives on legitimately-placed worksheets.
- DZV binding references the worksheet as one option among several → fires WC-DZV-ONLY-08 with a note that removal breaks the DZV pattern's optionality.
- Worksheet has both direct placement AND DZV binding → does NOT fire WC-DZV-ONLY-08 (first condition unmet).
- Removal implication: user MUST acknowledge that removal breaks the DZV pattern. Skill flags this in the removal proposal per HC#4.

**Worked example:**

Superstore has a worksheet `Regional Detail-DZV`. It appears in the `Executive Overview` dashboard only when the `Show Detail` parameter is `true`. No direct zone placement. Parameter traversal succeeded. Fires WC-DZV-ONLY-08. Severity Info. Recommended action: `keep` (removal would break the DZV pattern; only `remove` if user is intentionally simplifying).

***

## Failure Modes This Reference Prevents

- **False-positive on parameter-only worksheets** (WC-EMPTY-03 excludes parameter-only placements).
- **False-positive on legitimate default-named placeholder** (WC-DEFAULT-NAME-06 requires both name-pattern AND empty-shelves).
- **False-positive on formula-only sandbox that's actually in use** (WC-FORMULA-ONLY-07 requires three conditions, most notably calcs-unused-elsewhere).
- **Silent WC-DZV-ONLY-08 removal that breaks DZV pattern** (rule flags DZV-break implication in removal proposal per HC#4).
- **Silent WC-DZV-ONLY-08 fire when parameter traversal is unreliable** (sentinel prevents false-positive when platform tools are unreadable).
- **Silent WC-DEAD-FIELD-05 fire on case-mismatch** (case-sensitivity concern flagged in evidence, recommends manual verification).
- **Silent WC-DUPE-04 fire on cosmetic-only duplicates** (requires exact-match on shelves + fields + mark type).
