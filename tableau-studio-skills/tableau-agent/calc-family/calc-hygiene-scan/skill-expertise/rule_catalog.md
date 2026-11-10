# Rule Catalog Reference
Locked reference file for calc-hygiene-scan's 8-rule hygiene catalog. Cited by HC#3 and V1. Every calc maps against every rule; multi-rule findings tier by highest severity. Rules include detection criteria, evidence pattern, threshold defense where applicable, edge cases, and worked examples.

## Rule Precedence

**Severity tiering.** Warning-tier before Info-tier when multi-rule tagging fires on a single calc.

**Multi-rule tagging.** A calc can trigger multiple rules simultaneously. Skill emits all triggered rule IDs; severity tier set by highest match.

**Fallback discipline.** When rule detection depends on data that's unavailable per calc (formula unreadable, handoff stale for that calc), skill emits `"unable to determine"` sentinel for that rule on that specific calc per HC#5. Other rules on the same calc still evaluate.

***

## CH-NAMING-01: Naming Convention Drift

**Severity:** Info
**Signal source:** workbook XML (calc name list)
**Autofixable:** Yes (routes to calc-linter)
**Detection:** Workbook calc names mix casing conventions or separators. Fires when 2 or more casing patterns coexist across calcs, or 2 or more separator styles (spaces / hyphens / underscores).

**Casing patterns:** Title Case, Sentence case, lowercase, UPPERCASE, snake_case, kebab-case.

**Evidence pattern:** `casing_patterns_detected: ["Title Case", "lowercase"]; calcs_with_pattern_a: ["Profit Ratio", "Sales YoY"]; calcs_with_pattern_b: ["profit_by_region"]`.

**Edge cases:**
- All calcs use the same casing pattern. Rule clears.
- Workbook has 1 calc. Rule not applicable.
- Non-Latin script calc names. Skill emits `"unable to determine"` sentinel per HC#5 for those specific calcs.
- A cluster of 2+ calcs shares a common alternate casing pattern consistently (e.g., a deliberate `PascalCaseFamily` prefix convention). Treat that cluster as its own valid pattern, not drift — only fire on calc names that are true singletons within their pattern (no other calc shares that casing style). This avoids over-flagging intentional naming families while still catching real one-off drift.

**Worked example:**
Workbook has calcs `Profit Ratio`, `Sales YoY`, `profit_by_region`. Fires CH-NAMING-01 on `profit_by_region`. Severity Info. Desktop fix: "Rename `profit_by_region` to Title Case (`Profit by Region`) for consistency, or rename other calcs to match snake_case." Autofixable via calc-linter.

***

## CH-CAPTION-02: Missing Author Captions

**Severity:** Info
**Signal source:** workbook XML (calc caption attribute + in-formula `//` comments)
**Autofixable:** No (author intent required)
**Detection:** Calc has no author caption AND no in-formula `//` annotation. Both fields empty.

**Evidence pattern:** `calc_name: "Profit Ratio"; caption: ""; annotation: null; both_empty: true`.

**Edge cases:**
- Calc has caption but no in-formula annotation → clears (author intent captured in caption).
- Calc has in-formula annotation but no caption → clears (annotation captures intent).
- Calc has whitespace-only caption → treated as empty; fires rule.
- Platform gap: `author_caption` XML path may not be settable via native Desktop UI. Separately, `list-available-fields` (this skill's primary read tool) does not surface the Desktop description/comment field at all — its `caption` attribute is the display-name alias, not the author description. When no in-formula `//` annotation is present, the skill cannot distinguish "no description" from "description exists but is unreadable by this tool." Emit `"unable to determine"` sentinel in this case rather than firing the rule — do not treat an empty in-formula-annotation check as proof the caption is empty.

**Worked example:**
Calc `Profit Ratio` = `SUM([Profit]) / SUM([Sales])` with no caption and no `//` comment. Fires CH-CAPTION-02. Severity Info. Desktop fix: "Add a caption to `Profit Ratio` explaining the intent (e.g., 'Total profit divided by total sales across all rows')." Not autofixable — author must supply intent.

***

## CH-UNUSED-03: Unused Calcs (Zero References)

**Severity:** Warning
**Signal source:** reference graph from `calc_documentation/1` handoff, or local-extract usage scan across worksheets and other calcs
**Autofixable:** No (removal is destructive; routes to calc-linter for delete workflow with user consent)
**Detection:** Calc has zero references anywhere in the workbook: not used on any worksheet shelf, not referenced in any other calc, not used in any dashboard filter/parameter binding.

**Evidence pattern:** `calc_name: "Legacy Discount Rate"; used_by_worksheets: []; used_by_calcs: []; used_by_dashboards: []; total_reference_count: 0`.

**Edge cases:**
- Calc used only as a parameter default → still fires (parameter usage doesn't count as "in-use" for this rule).
- Calc used on a hidden worksheet → does not fire (hidden ≠ unused).
- Handoff missing/stale for this calc → local-extract fallback scans worksheets manually.

**Worked example:**
Workbook has calc `Legacy Discount Rate` last used in Q2 2025, now on no worksheet, no other calc, no dashboard. Fires CH-UNUSED-03. Severity Warning. Desktop fix: "Verify `Legacy Discount Rate` is genuinely unused, then delete via right-click → Delete in the Data pane. Removal routes to calc-linter for delete workflow with user consent."

***

## CH-NESTING-04: Excessive Nesting Depth

**Severity:** Warning
**Signal source:** formula parse (count nested function calls)
**Autofixable:** No (rewrite is out of scope for this skill; routes to calc-optimizer)
**Detection:** Formula parse depth exceeds 5 levels of nested function calls. Threshold empirically grounded: Tableau's own performance documentation and community benchmarking (e.g., InterWorks, The Information Lab) cite 4-5 levels as the readability/performance boundary; beyond 5, calc becomes hard to debug and slow to render.

**Nesting depth definition:** count of unmatched-open-parenthesis at the deepest point of the formula, minus one for the outer function's own parenthesis. `IIF(SUM([X]) > 0, [Y], [Z])` has depth 2. `IIF(SUM(IIF([A], [B], [C])) > 0, [Y], [Z])` has depth 4.

**Evidence pattern:** `calc_name: "Complex Nested Logic"; nesting_depth: 7; threshold: 5; excess: 2`.

**Edge cases:**
- Depth exactly 5 → does not fire (at threshold, considered acceptable).
- LOD expressions counted as one level of nesting each. `{FIXED [X]: SUM({FIXED [Y]: SUM([Z])})}` has depth 2 at the LOD level plus 2 at the aggregate level.
- Formula unparseable (malformed). Emit `"unable to determine"` sentinel per HC#5.

**Worked example:**
Calc `Complex Nested Logic` = `IIF(SUM(IIF([A], IIF([B], [C], [D]), [E])) > IIF([F] > 0, [G], [H]), [I], [J])`. Depth 7. Fires CH-NESTING-04. Severity Warning. Desktop fix: "Refactor `Complex Nested Logic` into 2 or 3 intermediate calcs (e.g., `Inner Check`, `Outer Threshold`) to reduce nesting to at most 5 levels. Route to calc-optimizer for structured rewrite."

***

## CH-HARDCODED-05: Hardcoded Values That Should Be Parameters

**Severity:** Warning
**Signal source:** formula pattern-match against a locked hardcoded-value catalog
**Autofixable:** Yes (routes to calc-linter for parameter creation and formula replacement)
**Detection:** Formula contains hardcoded literal values that match one of the locked hardcoded-value patterns (numeric thresholds, date literals, category strings) AND the same literal value appears in 2 or more calcs in the workbook (indicating a shared threshold that should be a parameter).

**Locked hardcoded-value patterns:**
- Numeric threshold: any bare integer or decimal that appears in 2+ calcs (e.g., `> 1000`, `* 0.15`, `<= 90`).
- Date literal: `#YYYY-MM-DD#` or `MAKEDATE(YYYY, MM, DD)` that appears in 2+ calcs.
- Category string: any quoted string literal that appears in 2+ calcs (e.g., `= "Enterprise"`, `IN ("A", "B", "C")`).

**Evidence pattern:** `calc_name: "Discount Threshold Check"; hardcoded_value: 0.15; also_used_in: ["Volume Discount", "Enterprise Discount"]; shared_across: 3`.

**Edge cases:**
- Literal appears in only 1 calc → does not fire (not a shared threshold).
- Literal is a mathematical constant (0, 1, -1, 100 for percentage conversion) → does not fire (mathematical constants are legitimate hardcoded values).
- Literal appears in a calc name (e.g., `[Sales Q1 2025]`) rather than the formula → does not count against this rule (naming is CH-NAMING-01's concern).

**Worked example:**
Calcs `Discount Threshold Check`, `Volume Discount`, `Enterprise Discount` all use `0.15` as a hardcoded discount rate. Fires CH-HARDCODED-05 on all three. Severity Warning. Desktop fix: "Create a `Discount Rate` parameter set to 0.15, then replace the hardcoded `0.15` in all three calcs. Autofixable via calc-linter."

***

## CH-DEPRECATED-06: Deprecated Function Usage

**Severity:** Warning
**Signal source:** formula pattern-match against a locked deprecated-function list
**Autofixable:** Yes (routes to calc-linter for function replacement)
**Detection:** Formula contains a function from the locked deprecated-function list.

**Locked deprecated-function list (Tableau 2024.3+):**
- `SCRIPT_REAL`, `SCRIPT_INT`, `SCRIPT_STR`, `SCRIPT_BOOL` — R/Python integration functions deprecated in favor of Analytics Extensions. Not autofixable (external system dependency); flag only.
- `INDEX()` when used without partition specification → not deprecated but often misused; not fired by this rule (out of scope).
- Legacy date parsing patterns like `DATEPARSE("yyyy-MM-dd HH:mm:ss", ...)` when `DATETIME()` cast would work — flagged but not deprecated; out of scope.
- `WINDOW_SUM([Sales], -SIZE()+1, 0)` running-total pattern → superseded by `RUNNING_SUM([Sales])` since Tableau 10.5. Fires and autofixable.

**Evidence pattern:** `calc_name: "Legacy Running Total"; deprecated_function: "WINDOW_SUM([Sales], -SIZE()+1, 0)"; recommended_replacement: "RUNNING_SUM([Sales])"; deprecation_since: "Tableau 10.5"`.

**Edge cases:**
- Function used correctly and non-deprecated → clears.
- Function is deprecated but the specific usage is still supported (backward compatibility) → still fires (rule flags future risk, not present breakage).
- Deprecated-function list snapshot.

**Worked example:**
Calc `Legacy Running Total` = `WINDOW_SUM([Sales], -SIZE()+1, 0)`. Fires CH-DEPRECATED-06. Severity Warning. Desktop fix: "Replace `WINDOW_SUM([Sales], -SIZE()+1, 0)` with `RUNNING_SUM([Sales])`. Same behavior, clearer intent, no deprecation risk. Autofixable via calc-linter."

***

## CH-CROSSDS-07: Cross-DS Calcs Without Rationale

**Severity:** Info
**Signal source:** reference graph from `calc_documentation/1` handoff (`cross_datasource_reference` flag) or local-extract cross-DS scan
**Autofixable:** No (rationale is author intent; user acknowledges)
**Detection:** Calc references fields from a datasource other than the calc's home datasource, AND the calc has no author caption or in-formula annotation explaining the cross-DS relationship.

**Evidence pattern:** `calc_name: "Cross-DS Sales Ratio"; home_datasource: "Orders"; cross_datasource_reference: "Returns.Return Rate"; author_caption: null; annotation: null`.

**Edge cases:**
- Calc references cross-DS AND has an author caption explaining why → does NOT fire (rationale documented).
- Calc references cross-DS AND has an in-formula `//` annotation explaining why → does NOT fire.
- Cross-DS reference is via blend rather than relationship → flag as `"unable to determine"` sentinel because blend semantics are context-dependent.

**Worked example:**
Calc `Cross-DS Sales Ratio` on Orders references `[Returns].[Return Rate]` with no caption and no `//` comment. Fires CH-CROSSDS-07. Severity Info. Desktop fix: "Add a caption to `Cross-DS Sales Ratio` explaining why it references Returns from Orders (e.g., 'Orders is the primary DS; Returns is used via blend for return-rate normalization')."

***

## CH-LOD-OVERUSE-08: Over-Reliance on LOD When a Simpler Pattern Works

**Severity:** Info
**Signal source:** formula pattern-match against `skill-expertise/explanation_patterns.md` precedence rules
**Autofixable:** No (rewrite is out of scope for this skill; routes to calc-optimizer)
**Detection:** Formula uses LOD-fixed, LOD-include, or LOD-exclude when a simpler aggregate or table-calc pattern would produce the same result. Uses locked pattern-match rules from calc-explainer's `skill-expertise/explanation_patterns.md` (12-pattern catalog).

**Pattern matches that fire this rule:**
- `{FIXED : SUM([X])}` with no dimensions declared → equivalent to `SUM([X])` at row level; LOD adds no value.
- `{FIXED [D]: SUM([X])} / SUM([X])` computing percent-of-total on a single dimension → often achievable via table calc `SUM([X]) / TOTAL(SUM([X]))`.
- `{INCLUDE [D]: AVG([X])}` when the workbook only ever aggregates at `[D]` grain → LOD adds no value over row-level `[X]`.

**Evidence pattern:** `calc_name: "Total Sales"; formula: "{FIXED : SUM([Sales])}"; equivalent_pattern: "SUM([Sales])"; lod_adds_value: false`.

**Edge cases:**
- LOD adds real value (e.g., cross-partition aggregation in a table-calc context) → clears; not fired.
- Formula uses LOD nested inside another aggregate → skill defers to calc-explainer's precedence rules (Rule 1: LOD wins) and does not fire this rule.
- User declares LOD is intentional (via annotation) → skill respects; does not fire.

**Worked example:**
Calc `Total Sales` = `{FIXED : SUM([Sales])}` (no dimensions declared). Fires CH-LOD-OVERUSE-08. Severity Info. Desktop fix: "Replace `{FIXED : SUM([Sales])}` with `SUM([Sales])` — LOD adds no value at the row level. Route to calc-optimizer for structured rewrite."

***

## Failure Modes This Reference Prevents

- **False positive on CH-NAMING-01 in mixed-language workbooks.** Non-Latin script names get `"unable to determine"` sentinel rather than being force-classified.
- **False positive on CH-CAPTION-02 when annotation exists.** In-formula `//` comments count as author intent per HC#6.
- **Silent CH-UNUSED-03 rendering with stale handoff.** V5 formula-hash per-calc check per HC#13 forces local-extract fallback if handoff is stale for that specific calc.
- **Fabricated deprecation timelines.** CH-DEPRECATED-06 uses the locked list only; no inferred deprecation.
- **CH-HARDCODED-05 false positive on mathematical constants.** 0, 1, -1, 100 excluded.
- **CH-LOD-OVERUSE-08 fabrication.** Uses `skill-expertise/explanation_patterns.md` precedence rules; does not invent patterns.
- **Fuzzy case-matching on `resolve-field`.** Exact-case per HC#16.
- **Skipping a rule on a specific calc when unresolvable.** Sentinel per HC#5, not silent skip.
