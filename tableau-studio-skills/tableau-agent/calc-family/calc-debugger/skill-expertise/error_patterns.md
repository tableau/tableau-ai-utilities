# Error-Pattern Catalog (Locked)

Nine locked error patterns. Every diagnosis cites the specific pattern ID. HC#2 discipline: never invent a pattern outside E-NULL through E-CIRC.

## E-NULL — Unexpected NULL Return

**Signature:** Calc returns NULL for rows where a non-NULL value was expected.

**Root causes:**
- NULL propagation through arithmetic (any op with a NULL operand returns NULL).
- Missing IFNULL/ZN wrappers on nullable fields.
- Filter or context mismatch (rows filtered out that the aggregation expected).
- Divide-by-zero returns NULL.
- LOD context with no matching dimension values.

**Fix approach:**
- Wrap nullable operands: `ZN([field])` for numeric zero fallback, `IFNULL([field], fallback)` for explicit fallback.
- Add explicit ISNULL fallback: `IF ISNULL([field]) THEN 'default' ELSE [field] END`.
- For divide-by-zero: `IF SUM([denom]) = 0 THEN NULL ELSE SUM([num]) / SUM([denom]) END`.

**Worked example:**
- Broken: `SUM([Profit]) / SUM([Sales])` (returns NULL for any Category with $0 Sales)
- Fixed: `IF SUM([Sales]) = 0 THEN NULL ELSE SUM([Profit]) / SUM([Sales]) END`

**V-gate rules that catch this:** R-NULL-01.

## E-SYNTAX — Author-calc Syntax Error

**Signature:** `author-calc` rejects the formula with a syntax error message.

**Root causes:**
- Malformed function call (missing paren, wrong arg count).
- Unmatched brackets, braces, or quotes.
- Wrong function name (e.g., `DATE_DIFF` instead of `DATEDIFF`).
- Missing colon in LOD (`{FIXED [dim] SUM(...)}` without `:`).
- Case-sensitivity error on function name.

**Fix approach:**
- Look up correct signature in `skill-expertise/INDEX.md` (HC#2).
- Refactor to match the locked signature.
- Add missing brackets/colons/parens.

**Worked example:**
- Broken: `DATE_DIFF('day', [Order Date], [Ship Date])` (wrong function name; rejected by author-calc)
- Fixed: `DATEDIFF('day', [Order Date], [Ship Date])`

**V-gate rules that catch this:** R-TYPE-01, R-LOD-01, R-TC-01.

## E-TYPE — Return Type Mismatch

**Signature:** Calc's return type doesn't match how the caller uses it. Example: calc returns String but is placed on a numeric axis; or calc returns Boolean but is aggregated with SUM without expected 1/0 cast.

**Root causes:**
- Missing explicit type conversion.
- Wrong function chosen (e.g., STR instead of INT).
- Boolean returned where Number expected downstream.

**Fix approach:**
- Explicit conversion: `INT(...)`, `STR(...)`, `FLOAT(...)`, `BOOL(...)`.
- For Boolean→Number: `IF [BoolCalc] THEN 1 ELSE 0 END`.

**Worked example:**
- Broken: `[Order ID] + 1` where `[Order ID]` is stored as String (fails or returns unexpected concatenation)
- Fixed: `INT([Order ID]) + 1` (or refuse if `[Order ID]` contains non-numeric characters — ask the user to confirm intent)

**V-gate rules that catch this:** R-TYPE-02, R-BOOL-01.

## E-AGG — Aggregation Wrapping Violation

**Signature:** Formula mixes aggregate and row-level references incorrectly. Example: `IF SUM([Sales]) > 100 THEN [Sales] END` (bare `[Sales]` in aggregate context).

**Root causes:**
- Bare row-level field inside an aggregate context (R-AGG-01).
- ATTR-based Boolean returning NULL on mixed groups (R-AGG-02).
- Missing SUM/AVG wrapper.

**Fix approach:**
- Wrap the bare field: `IF SUM([Sales]) > 100 THEN SUM([Sales]) END`.
- Rewrite ATTR to MIN/MAX: `MIN([Category]) = 'Furniture'` instead of `ATTR([Category]) = 'Furniture'`.

**Worked example:**
- Broken: `IF SUM([Sales]) > 100 THEN [Sales] END` (bare `[Sales]` inside an aggregate `IF`)
- Fixed: `IF SUM([Sales]) > 100 THEN SUM([Sales]) END`

**Locked ATTR-vs-MIN/MAX decision rule (R-AGG-02):** ATTR is acceptable ONLY when the diagnosis confirms both: (a) mixed-value groups genuinely exist in the data for the dimension in question, AND (b) the calc's intended semantics specifically require "same value across all rows in group, NULL otherwise" (i.e., a NULL on disagreement is the correct signal, not a bug). If either condition doesn't hold — including whenever a NULL from ATTR is the reported symptom being debugged — rewrite to MIN or MAX for stable-scalar semantics. Never leave ATTR in place solely because "it might matter later"; document the rationale in the handoff `notes` only when both conditions are confirmed true.

**V-gate rules that catch this:** R-AGG-01, R-AGG-02. **Self-healing:** auto-corrected by calc-writer/calc-debugger V-gate.

## E-LOD — LOD Returns Wrong Grain

**Signature:** LOD calc returns unexpected values because the dimension list, LOD type, or filter interaction is wrong.

**Root causes:**
- Missing dimension in the FIXED/INCLUDE/EXCLUDE list.
- Wrong LOD type (FIXED when INCLUDE was needed, or vice versa).
- Filter-order confusion: FIXED executes before dimension filters, so filter changes don't affect the LOD unless promoted to context.
- Nested LOD produces unexpected double-counting.

**Fix approach:**
- Adjust dimension list to match the intended grain.
- Switch LOD type per intent (FIXED for grain-independent; INCLUDE for finer grain than view; EXCLUDE for coarser).
- Promote a filter to context if a FIXED LOD needs to respect it.
- Flatten nested LODs if possible; document rationale if not (R-LOD-02).

**Worked example:**
- Broken: `{FIXED [Region] : SUM([Sales])}` on a view filtered by Category, expected to shrink per-Category but doesn't (FIXED ignores the non-context Category filter)
- Fixed: promote `[Category]` to a context filter, or rewrite as `{INCLUDE [Category] : SUM([Sales])}` if the intent was Category-aware grain

**V-gate rules that catch this:** R-LOD-01, R-LOD-02, R-LOD-03.

## E-FIELD — Reference to Nonexistent Field

**Signature:** Formula references a field that no longer exists in the data source (deleted, renamed, or from a different DS).

**Root causes:**
- Field deleted after calc was authored.
- Field renamed after calc was authored (broken reference by original name).
- User pasted a calc from a different data source.

**Fix approach:**
- Refuse silent substitution per HC#5.
- Ask user to confirm intended field name.
- If user names a similarly-named real field, propose that as the substitution — but only after explicit confirmation.

**Worked example:**
- Broken: `SUM([Gross Sales])` where the field was renamed to `[Sales]` — `list-available-fields` shows no `[Gross Sales]`
- Fixed: only after user confirms `[Sales]` is the intended replacement: `SUM([Sales])`

**V-gate rules that catch this:** field verification in Phase 1.

## E-PARAM — Reference to Nonexistent Parameter

**Signature:** Formula references a parameter that no longer exists.

**Root causes:**
- Parameter deleted after calc was authored.
- Parameter renamed.

**Fix approach:**
- Refuse re-authoring per HC#6 (calc-debugger cannot create parameters).
- Route to Desktop UI: "recreate the parameter manually in Desktop, then re-invoke."

**Worked example:**
- Broken: `IF [Selected Region] = 'West' THEN ...` where `[Selected Region]` parameter was deleted
- Fixed: no calc fix proposed; user is told to recreate the parameter, then re-invoke calc-debugger

**V-gate rules that catch this:** parameter verification in Phase 1.

## E-GRAIN — Wrong Values Due to Fanning or Grain Mismatch

**Signature:** Calc returns wrong (usually inflated or doubled) values because of many-to-many joins, wrong logical table, or missing FIXED LOD.

**Root causes:**
- Many-to-many join causes SUM to double-count (F1 fanning pattern from `join-and-relationship-advisor`).
- Calc placed on wrong logical table in a relationship model.
- Row-level calc where a FIXED LOD would preserve grain.

**Fix approach:**
- Diagnose grain issue.
- **If root cause is the model** (join type, cardinality, relationships), route to `join-and-relationship-advisor` per HC#10. Return here for the calc fix after the model is resolved.
- **If root cause is calc-side** (missing FIXED LOD, wrong table binding), propose the calc fix.

**Worked example:**
- Broken: `SUM([Sales])` on a view with Orders many-to-many joined to Returns via `[Order ID]`, sales inflated 3x
- Fixed (calc-side): `{FIXED [Order ID] : SUM([Sales])}` — but only after confirming the join itself is intentional; if not, route to `join-and-relationship-advisor` first per HC#10

**V-gate rules that catch this:** R-LOD-03 (filter-order + LOD context).

## E-CIRC — Circular Reference

**Signature:** Calc A references Calc B, which (directly or through a chain) references Calc A.

**Root causes:**
- User created a mutual reference intentionally, not realizing the cycle.
- Chain-of-refs eventually loops back.

**Fix approach:**
- Refuse re-authoring per HC#4 + HC#7 (no automatic fix; user must break the cycle).
- Report the specific cycle in the diagnosis.
- Ask user to identify which calc should be the "root" (non-referential); rewrite the others to reference the root.

**Worked example:**
- Broken: `[Calc A]` references `[Calc B]`, and `[Calc B]`'s formula references `[Calc A]`
- Fixed: no calc fix proposed; diagnosis reports "Calc A → Calc B → Calc A" and asks the user which should be the non-referential root

**V-gate rules that catch this:** reference graph check in Phase 1.

## Detection Order

Diagnose in this order to reduce false positives:

1. **E-CIRC** (block early; refuse re-authoring immediately).
2. **E-FIELD** (missing field means no diagnosis possible).
3. **E-PARAM** (same).
4. **E-SYNTAX** (`author-calc` rejects; can't verify).
5. **E-AGG** (self-healing; auto-correct).
6. **E-LOD** (grain issues; may cascade to E-GRAIN).
7. **E-GRAIN** (route to `join-and-relationship-advisor` if model is root).
8. **E-TYPE** (type conversion).
9. **E-NULL** (most common; often masks another root cause).

## Refuse to Fabricate

Never invent a new pattern ID. Ask user for the actual expected value vs. observed value to narrow diagnosis, per HC#4 one-clarifier.
