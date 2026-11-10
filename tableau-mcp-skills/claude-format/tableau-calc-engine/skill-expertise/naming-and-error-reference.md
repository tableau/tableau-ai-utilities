# Naming Prefixes and Common Error Reference

Field naming pattern table, recommended prefixes, and the common error patterns and fixes table.

| Pattern | Example | Anti-Pattern |
|---|---|---|
| Descriptive noun | `Sales YTD` | `Calculation1` |
| Prefixed by type | `% Rev Growth` | `My Calc` |
| Abbreviated clearly | `Cust First Ord` | `CustomerFirstOrderDateForCohort` |
| Boolean as question | `Is Repeat?` | `RepeatCustomerFlag_v2_final` |

### Recommended Prefixing (for large workbooks)

- `Σ` or `m_` — Measures
- `Δ` or `d_` — Dimension calcs
- `◉` or `f_` — Boolean/filter calcs
- `₮` or `tc_` — Table calcs
- `_` or `z_` — Hidden helpers (sort to bottom)

| Error (wording varies by Tableau version) | Root Cause | Fix |
|---|---|---|
| Mixing aggregate and non-aggregate arguments | `SUM([A]) + [B]` where [B] not aggregated | Wrap: `SUM([A]) + MIN([B])` or use ATTR() |
| Aggregate calc used with a non-aggregated field | Dimension on measure-only shelf | Use LOD or ATTR() wrapper |
| Circular reference between calcs | Calc A → B → A | Break cycle: introduce third calc |
| NULL everywhere | Table calc dimension not in view | Add dimension or change Compute Using |
| LOD ignoring filter | FIXED computed before dimension filters | Add to Context, or use INCLUDE |
| Very large or slow LOD result | LOD creating huge intermediate | Add constraining dimensions |
| LOOKUP wrong value | Addressing direction wrong | Check Compute Using + sort order |
| % of Total = 100% | TOTAL() scope same as numerator | Adjust addressing |
