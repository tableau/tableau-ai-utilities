# Fix Recipes

Each recipe corresponds to a check category in `checks.md` (row-level, sections 1-10) or `metadata_checks.md` (metadata, sections M1-M5). All fixes are **additive and reversible** -- they create new calculated fields or apply worksheet-level filters. Nothing deletes or mutates the original data.

Naming convention for all created objects: prefix with `DQ Fix:` so users can identify and remove them later.

***

## 1. Duplicate Rows

**Fix type:** Worksheet filter (LOD-based deduplication calc)

**Approach:** Create a calculated field that assigns a row number within each duplicate group, then filter to keep only row 1.

**Formula:**
```
// DQ Fix: Deduplicate Flag
IF { FIXED [all key fields] : COUNTD([Row ID or index field]) } > 1
THEN "Duplicate"
ELSE "Unique"
END
```

**Alternative (simpler):** If a reliable unique identifier exists, create a calc that flags the first occurrence:
```
// DQ Fix: Keep First Occurrence
{ FIXED [key fields] : MIN([unique_id_field]) } = [unique_id_field]
```

Then filter the worksheet to show only TRUE.

**User guidance:** "This creates a flag field. Add it to Filters and keep only 'Unique' (or TRUE). Your original data is unchanged — remove the filter and calc to revert."

**When even the "unique" identifier fields are duplicated (true full-row duplicates):** the two recipes above rely on a field (row ID, unique_id_field) that still distinguishes the two copies. If the duplicate rows share EVERY field including whatever you'd normally treat as a unique key (this happens — see the population-size-vs-sample-cap check in `checks.md`), there is no field left to break the tie safely. In that case:
- Do NOT auto-delete or auto-keep one copy — you cannot know which copy is the "real" one from the data alone, and picking wrong silently drops a legitimate record if the duplication wasn't a simple re-insert.
- Instead, create a review flag that marks every row belonging to an affected key, and let the user resolve it manually (or take it back to the source system):
```
// DQ Fix: Duplicate [Key Field] Flag
[Key Field] IN ("value1", "value2", ...)   // exact list of keys found duplicated
```
- Report the exact list of duplicated key values in the finding so the user can inspect them directly (e.g. filter the flag to TRUE and eyeball the pairs).
- If the user confirms after inspection that arbitrary de-duplication is safe (e.g. confirmed ETL re-run bug, both rows are byte-identical), THEN offer a table-calc-based tiebreaker as a follow-up, not as the default: `IF INDEX() = 1 THEN "Keep" ELSE "Duplicate" END` with "Compute Using" partitioned by the key field(s) — this requires the calc to be placed on a worksheet with the key field(s) present and the compute-using addressing set explicitly; confirm the partition/addressing before trusting the result.

***

## 2. Null Values

**Fix type:** Calculated field (IFNULL replacement)

**For dimensions (string fields):**
```
// DQ Fix: [Field Name] (Null Handled)
IFNULL([Original Field], "Unknown")
```

**For measures (numeric fields):**
```
// DQ Fix: [Field Name] (Null Handled)
ZN([Original Field])
```

**For date fields:**
```
// DQ Fix: [Field Name] (Null Handled)
IFNULL([Original Field], #1900-01-01#)
```

**User guidance:** "This creates a parallel field with nulls replaced. Use it instead of the original where null-safe aggregation is needed. The placeholder value ('Unknown', 0, or 1900-01-01) is visible in filters so downstream users know the data was imputed."

**Important:** Always ask the user what replacement value they prefer. The defaults above are starting suggestions.

***

## 3. Data Type Mismatches

**Fix type:** Calculated field (type conversion)

**Numeric stored as string:**
```
// DQ Fix: [Field Name] (As Number)
FLOAT([Original Field])
```

**Date stored as string (ISO format):**
```
// DQ Fix: [Field Name] (As Date)
DATEPARSE("yyyy-MM-dd", [Original Field])
```

**Date stored as string (other formats):** Adjust the DATEPARSE format string to match the observed pattern. Common patterns:
- `"MM/dd/yyyy"`
- `"dd-MMM-yyyy"`
- `"yyyyMMdd"`

**Boolean stored as string with multiple variants** (e.g. a field mixing `"0"`/`"1"`, `"yes"`/`"no"`, `"true"`/`"True"`/`"false"`/`"FALSE"` for the same two logical states): normalize with a case-insensitive membership test rather than a straight cast, since `BOOLEAN()`/`FLOAT()` conversion functions won't reliably parse all the variants.
```
// DQ Fix: [Field Name] Normalized
IIF(LOWER(TRIM([Original Field])) IN ("1", "yes", "true"), TRUE, FALSE)
```
Build the `IN (...)` list from the actual distinct "true-like" values found during the check — don't guess a generic list. Confirm the field's real distinct-value set first (this is itself a Check #3 sub-step): pair the field with any measure via a bar-type template to enumerate every variant before writing the formula.

**User guidance:** "This creates a properly-typed version of the field. Verify a few values visually, then swap it into your worksheets. If any values fail to parse, they'll appear as Null in the new field — check the null count afterward."

***

## 4. Leading/Trailing Whitespace

**Fix type:** Calculated field (TRIM)

```
// DQ Fix: [Field Name] (Trimmed)
TRIM([Original Field])
```

**User guidance:** "This removes invisible leading and trailing spaces. Replace the original field with this version in your filters and dimensions to prevent false cardinality inflation."

***

## 5. Inconsistent Casing

**Fix type:** Calculated field (standardized casing)

**Option A — Title Case (recommended for names, categories):**

Tableau lacks a native PROPER() function. The simple formula below only capitalizes the first letter of the entire string, which works for single-word values but fails on multi-word strings ("new york" becomes "New york", not "New York").

For single-word fields only:
```
// DQ Fix: [Field Name] (Title Case - Single Word)
UPPER(LEFT([Original Field], 1)) + LOWER(MID([Original Field], 2))
```

For multi-word fields, use **Option D** (CASE mapping) instead. Build the CASE statement from the distinct values found during the check. This is the only reliable approach in Tableau for proper multi-word title casing.

**Option B — Upper Case (recommended for codes, IDs):**
```
// DQ Fix: [Field Name] (Uppercase)
UPPER([Original Field])
```

**Option C — Lower Case:**
```
// DQ Fix: [Field Name] (Lowercase)
LOWER([Original Field])
```

**Option D — Group/Alias (when specific mappings are needed):**
Create a group in Tableau that maps all variants to the canonical form. This is a UI action, not a calc. Describe the mapping to the user and let them create the group manually, or use `author-calc` with a CASE statement:
```
// DQ Fix: [Field Name] (Standardized)
CASE LOWER([Original Field])
  WHEN "new york" THEN "New York"
  WHEN "los angeles" THEN "Los Angeles"
  // ... extend as needed
  ELSE [Original Field]
END
```

**User guidance:** "Choose the casing rule that matches your house style. Option D gives you exact control but requires maintenance if new variants appear."

***

## 6. Outliers / Implausible Values

**Fix type:** Worksheet filter (exclusion calc) or a reference band

**Option A — Soft filter (hide but don't remove):**
```
// DQ Fix: [Field Name] Outlier Flag
IF [Original Field] < [Q1 - 3*IQR] OR [Original Field] > [Q3 + 3*IQR]
THEN "Outlier"
ELSE "Normal"
END
```
Add to Filters, exclude "Outlier". Easily toggled off.

**Option B — Capped field (winsorize):**
```
// DQ Fix: [Field Name] (Capped)
MIN(MAX([Original Field], [lower_bound]), [upper_bound])
```
Replace `[lower_bound]` and `[upper_bound]` with the computed thresholds.

**Option C — Negative value flag:**
```
// DQ Fix: [Field Name] Negative Flag
IF [Original Field] < 0 THEN "Negative" ELSE "Valid" END
```

**User guidance:** "Outliers may be real. This flag lets you toggle them on/off to see their impact without discarding data. Investigate before permanently filtering."

***

## 7. High Cardinality Dimensions

**Fix type:** Binning calc or top-N filter

**Option A — Bin/Group (for quasi-continuous fields):**
```
// DQ Fix: [Field Name] (Binned)
IF [Original Field] <= [threshold_1] THEN "Low"
ELSEIF [Original Field] <= [threshold_2] THEN "Medium"
ELSE "High"
END
```

**Option B — Top N + "Other" bucket:**
```
// DQ Fix: [Field Name] (Top N)
IF RANK(SUM([relevant_measure]), 'desc') <= 10
THEN [Original Field]
ELSE "Other"
END
```
`RANK()` is a table calc — its result depends on which fields are on the view and how "Compute Using" (addressing/partitioning) is set. Before trusting this fix, explicitly set "Compute Using" to address by `[Original Field]` (the dimension being ranked) with no other partitioning fields, and confirm on the worksheet that the rank order matches the top-10 you expect. If the calc is later moved to a worksheet with a different field layout, the addressing must be re-confirmed — it does not travel with the formula.

**Option C — Recommend removing from viz dimensions:**
If the field is a row-level ID (cardinality ratio > 0.9), the fix is simply: "Don't use this as a dimension. It's an identifier. Use it for detail lookups or as a filter, not on Rows/Columns/Color."

**User guidance:** "High cardinality isn't always a defect. If the field is meant to be granular (e.g., Transaction ID), the fix is to use it appropriately rather than to change it."

***

## 8. Date Field Issues

**Fix type:** Calculated field (bounds check or correction)

**Future dates beyond reasonable range:**
```
// DQ Fix: [Field Name] (Date Validated)
IF [Original Field] > TODAY() + 365 THEN NULL
ELSE [Original Field]
END
```

**Pre-floor dates:**
```
// DQ Fix: [Field Name] (Date Validated)
IF [Original Field] < #1900-01-01# THEN NULL
ELSE [Original Field]
END
```

**Truncation detection (info only):**
No automated fix. Report the pattern and let the user investigate upstream ETL. Suggest: "Your dates appear truncated to month-start. If daily grain is expected, check the source system's date formatting."

**User guidance:** "Implausible dates are nulled out in the fixed field. Check what's being lost — it might indicate a data-entry or ETL bug worth fixing at the source."

***

## 9. Constant / Zero-Variance Fields

**Fix type:** No calc needed. Recommendation only.

**Guidance to user:**
- "This field has only one value across all sampled rows. It provides no analytic differentiation."
- "Consider hiding it from the data pane (right-click > Hide) to reduce clutter."
- "If it's a measure that should vary, investigate the source — it may indicate a broken pipeline or filter applied too early."

**No object is created.** This is an advisory finding.

***

## 10. Sparse Fields

**Fix type:** Calculated field (placeholder cleanup) or advisory

**If sparseness is due to placeholder values:**
```
// DQ Fix: [Field Name] (Cleaned)
IF [Original Field] IN ("N/A", "n/a", "NA", "None", "Unknown", "TBD", "", "null")
THEN NULL
ELSE [Original Field]
END
```

This normalizes placeholders to true NULL so Tableau's null-handling (special values, ZN, etc.) works consistently.

**If sparseness is due to true nulls:**
Apply the Null Values fix (recipe #2) or advise the user that the field may not be reliable for analysis below a certain aggregation grain.

**User guidance:** "Sparse fields aren't necessarily broken — some fields only apply to certain record types. But if you're building a viz on this field, know that [X]% of your data will show as null/unknown."

***

## M1. Naming Violations (Rename Wrapper)

**Fix type:** Calculated field (alias wrapper)

**Approach:** Create a calculated field with a properly-named caption that simply references the original field. The consumer uses the clean name; the original stays untouched.

**Formula:**
```
// DQ Fix: [Proper Name]
[Original Poorly Named Field]
```

**Examples:**
- Original: `order_date__c` -> Fix caption: `DQ Fix: Order Date`, formula: `[order_date__c]`
- Original: `CUST_NM` -> Fix caption: `DQ Fix: Customer Name`, formula: `[CUST_NM]`

**User guidance:** "This creates a clean alias. Use the new field in your worksheets. The original remains for compatibility with existing calcs or extracts. Once all references are migrated, you can hide the original."

**Batch approach:** If >5 fields need renaming, present the full list and ask: "Want me to create rename wrappers for all [N], or just the ones you'll actively use?"

***

## M2. Type/Role Mismatches (from metadata)

**Fix type:** Calculated field (type cast or role correction)

**Numeric stored as string (detected from field name):**
```
// DQ Fix: [Field Name] (As Number)
FLOAT([Original Field])
```

**Date stored as string (detected from field name):**
```
// DQ Fix: [Field Name] (As Date)
DATEPARSE("yyyy-MM-dd", [Original Field])
```
Note: Format string must be confirmed during row-level check. If the metadata check fires but no row-level data has been read yet, propose the fix but flag: "Date format assumed as ISO. I'll confirm during the data scan."

**ID field misclassified as measure:**
```
// DQ Fix: [Field Name] (As Dimension)
STR([Original Field])
```
Converting to string forces dimension role. Alternative: advise user to right-click -> Convert to Dimension (no calc needed, but not reversible via this skill).

**User guidance:** "These fixes address fields whose names strongly suggest a different type than configured. After applying, verify a few values render correctly in the new type."

***

## M3. Schema Hygiene

**Fix type:** Advisory only (no calc).

**Excessive field count:**
- "This datasource has [N] fields. Consider hiding unused fields (right-click -> Hide) or splitting into focused datasources for different use cases."

**Excessive calc ratio:**
- "Over [X]% of fields are calculated. Consider moving stable calculations into the datasource (materialized columns or SQL views) to reduce viz-layer compute."

**Deeply nested calcs:**
- "Calc '[name]' has [N] nesting levels. Consider refactoring into intermediate calcs for readability and maintainability."
- Offer to show the formula for review.

**User guidance:** These are structural recommendations, not quick fixes. No objects are created.

***

## M4. Near-Duplicate / Redundant Fields

**Fix type:** Calculated field (unifier) or advisory

**Option A -- Unifier calc (when one variant should win):**
```
// DQ Fix: [Canonical Name]
IFNULL([Preferred Variant], [Fallback Variant])
```
Use when two near-duplicate fields exist across tables and the user wants a single unified version.

**Option B -- Advisory (when duplicates are cross-table join artifacts):**
- "Fields '[A]' and '[B]' have near-identical names across different tables. If they represent the same concept, consider hiding one and using the other consistently. If they differ semantically, rename one to clarify."

**User guidance:** "Near-duplicates aren't always wrong (same field from different tables in a multi-table datasource). But consumers shouldn't have to guess which 'Customer Name' to use."

***

## M5. Unused / Low-Signal Fields

**Fix type:** Advisory only (no calc).

**Generic auto-increment names (F1, Column1, Unnamed: 0):**
- "Fields [list] appear to be unnamed import artifacts. Consider: (1) re-importing with a proper header row, (2) renaming them if they contain useful data, or (3) hiding them if unused."

**Low-signal candidates:**
- "These fields have generic/system names, no descriptions, and aren't referenced by any calculation: [list]. Consider hiding them to reduce data pane clutter."

**User guidance:** "Hiding a field doesn't delete it. It remains available via 'Show Hidden Fields' and continues to work in existing calcs/worksheets."

***

## General Fix Application Rules

1. **Always ask before applying.** Present the fix, show the formula, and wait for approval.
2. **Name clearly.** Every created calc starts with `DQ Fix:` so it's identifiable.
3. **One calc per finding.** Don't bundle multiple fixes into a single calculated field.
4. **Preserve the original.** Never overwrite or hide the original field as part of a fix.
5. **Test after applying.** After creating a fix calc, briefly verify it produces the expected output by checking a few values via `get-summary-data`.
