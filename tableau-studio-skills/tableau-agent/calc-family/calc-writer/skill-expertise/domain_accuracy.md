# Domain-Accuracy Assertions (Locked)

Moved from SKILL.md on 2026-11-03 to keep the always-loaded skill lean. Read this before authoring LOD, table-calc, ATTR, Boolean-aggregate, DATEPARSE, spatial, or REGEXP calcs.

Every function signature in the library cites `help.tableau.com` as source of truth. In addition, the following Tableau-specific behaviors are locked and correctly encoded in the reference files:

- **LOD order of operations** (R-LOD-03 and `lod.md`): FIXED executes before dimension filters; INCLUDE/EXCLUDE execute after dimension filters, before measure filters. Context filters promote a dimension filter to run before FIXED.
- **ATTR failure modes** (R-AGG-02 and `aggregate.md`): `NOT ATTR([BoolField])` returns NULL when values are mixed within the group (because ATTR returns NULL, and NOT NULL = NULL, not TRUE). `ISNULL(ATTR([DimField]))` returns TRUE both when the field is genuinely NULL and when values are mixed. MIN/MAX preferred where stable-scalar semantics hold.
- **INT vs. ROUND** (`type_conversion.md`): INT truncates, does not round. `INT(2.7) = 2`, not 3.
- **Boolean-as-Integer aggregation** (`aggregate.md`): SUM converts TRUE → 1 and FALSE → 0. This is Tableaus implicit numeric cast and is the correct pattern for counting Booleans.
- **COUNT vs. COUNTD NULL handling** (`aggregate.md`): COUNT and COUNTD both ignore NULL. If NULLs should count, wrap with IFNULL or use SUM over a Boolean.
- **DATEPARSE format strings** (`date.md`): follow Java SimpleDateFormat patterns, not Excel format masks. Test against a real value before committing.
- **Table-calc partitioning defaults** (R-TC-01 and `table_calc.md`): default partitioning is by every dimension in the view; explicit "compute using" / "along" required for reproducibility. calc-writer always documents intent in the handoff `notes` field.
- **Spatial function version gates** (`spatial.md`): MAKEPOINT 2019.2+, MAKELINE 2019.2+, DISTANCE 2019.2+, INTERSECTS 2019.2+, AREA 2020.4+, LENGTH 2020.4+, CENTROID 2022.4+, BUFFER 2024.1+.
- **USEREMAIL version gate** (`logical.md`): 2023.3+. USERNAME and ISUSERADMIN are available in all supported versions.
- **REGEXP escape handling** (`string.md`): Tableau REGEXP_MATCH uses ICU regex syntax. Double-escape special characters when passing via calc string literal.

Any calc that violates one of these assertions gets caught by the corresponding V-gate rule or a perf-advisory flag, never delivered.
