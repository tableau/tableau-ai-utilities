# Drift Catalog (Locked, 7 Drift Types)

Every finding cites one of these rule IDs. No fabricated rules; no severity reassignment; no drift type outside this catalog.

## Severity Baselines

Every drift type has a locked severity baseline. Cross-DS drift is Info-by-default per HC#12; within-DS drift follows the tier assigned below.

| Rule ID | Drift Type | Baseline Severity |
|---|---|---|
| F-CURRENCY-01 | Currency-Symbol Mismatch | Warning |
| F-DECIMAL-02 | Decimal-Places Mismatch | Warning |
| F-DATE-03 | Date-Format Mismatch | Warning |
| F-SEPARATOR-04 | Thousands-Separator Mismatch | Warning |
| F-FONT-FAMILY-05 | Font-Family Drift | Info |
| F-FONT-SIZE-06 | Font-Size Drift | Info |
| F-NEGATIVE-07 | Negative-Number-Treatment Drift | Warning |

## F-CURRENCY-01 Currency-Symbol Mismatch

**Check:** every measure placement within the same data source that carries a currency-formatted format string uses the same currency symbol AND the same currency-format convention (Currency (Standard) vs Currency (Custom)).

**Signals evaluated:**

- Extract format string from worksheet XML `format="..."` attribute for the measure placement.
- Detect currency symbol at start or end of the format string (`$`, `€`, `£`, `¥`, `CHF`, `kr`, etc.).
- Compare against the baseline currency symbol for that measure within the DS (first-seen wins per HC#11).

**Fires when:** two or more placements of the same measure within the same DS use different currency symbols, OR one placement is currency-formatted and another is plain-number for the same measure.

**Cross-DS behavior:** different currency symbols across DS boundaries are Info-tier per HC#12. Multi-currency reporting is legitimate.

**Severity:** Warning within DS. Info cross-DS.

**Desktop fix:** right-click the field on the affected worksheet > Format > Numbers > Currency (Custom) > match the baseline symbol.

## F-DECIMAL-02 Decimal-Places Mismatch

**Check:** every measure placement within the same DS uses the same decimal-place count for the same measure.

**Signals evaluated:**

- Extract decimal-place count from the format string (e.g., `#,##0` = 0, `#,##0.00` = 2, `#,##0.0` = 1).
- Compare against the baseline decimal count for that measure within the DS.

**Fires when:** two or more placements of the same measure within the same DS use different decimal-place counts.

**Severity:** Warning within DS. Info cross-DS.

**Desktop fix:** right-click the field on the affected worksheet > Format > Numbers > adjust decimal places.

## F-DATE-03 Date-Format Mismatch

**Check:** every date-pill placement of the same date field uses the same date-format string.

**Signals evaluated:**

- Extract date-format string from worksheet XML for each date pill.
- Compare against the baseline date-format string for that date field within the DS.

**Fires when:** two or more date-pill placements of the same date field use different format strings (MM/DD/YYYY vs DD-MMM-YYYY vs YYYY-MM-DD).

**Severity:** Warning within DS. Info cross-DS (legitimate for multi-region reporting).

**Desktop fix:** right-click the date pill on the affected worksheet > Format > Dates > match the baseline pattern.

## F-SEPARATOR-04 Thousands-Separator Mismatch

**Check:** every measure placement within the same DS uses the same thousands-separator convention.

**Signals evaluated:**

- Extract separator character from the format string (`,` = 1,234, `.` = 1.234, space = 1 234, none = 1234).
- Compare against the baseline separator for that measure within the DS.

**Fires when:** two or more placements of the same measure within the same DS use different thousands separators, OR one placement uses a separator and another does not.

**Severity:** Warning within DS. Info cross-DS.

**Desktop fix:** right-click the field on the affected worksheet > Format > Numbers > Currency (Custom) > match the baseline separator convention.

## F-FONT-FAMILY-05 Font-Family Drift

**Check:** every text element within a workbook-scope element category (worksheet titles, axis labels, tooltip labels, dashboard text objects) uses the same font family.

**Signals evaluated:**

- Extract font-family declaration from worksheet or dashboard XML for each text element.
- Group text elements by category (title, axis, tooltip, dashboard-text).
- Compare within each category against the baseline font family (first-seen wins).

**Fires when:** two or more text elements within the same category use different font families.

**Severity:** Info by default (fonts are often intentional per design system). Upgrades to Warning when the drift is undocumented AND the workbook has a dashboard-caption reference to a design system that specifies one font.

**Desktop fix:** right-click the text element > Format > Font > select the baseline family.

## F-FONT-SIZE-06 Font-Size Drift

**Check:** every text element within a workbook-scope element category uses the same font size.

**Signals evaluated:**

- Extract font-size declaration from worksheet or dashboard XML.
- Group by category (title, axis, tooltip, dashboard-text).
- Compare within each category against the baseline size.

**Fires when:** two or more text elements within the same category use different font sizes.

**Severity:** Info by default. Upgrades to Warning when the drift is greater than 4 points (e.g., 9pt vs 14pt in tooltip labels) OR the drift affects axis labels specifically (axis-label size drift breaks visual hierarchy).

**Desktop fix:** right-click the text element > Format > Font > size > adjust to baseline.

## F-NEGATIVE-07 Negative-Number-Treatment Drift

**Check:** every measure placement of the same measure within the same DS uses the same negative-number treatment.

**Signals evaluated:**

- Extract negative-number treatment from the format string (parentheses `(1,234)`, minus-sign `-1,234`, red-color, minus + red).
- Compare against the baseline for that measure within the DS.

**Fires when:** two or more placements of the same measure within the same DS use different negative-number treatments.

**Severity:** Warning within DS. Info cross-DS.

**Desktop fix:** right-click the field > Format > Numbers > Currency (Custom) > negative-number panel > match baseline.

## Inherited vs. Explicit Format Strings

A placement with no explicit format override inherits the field's default format string. An inherited default is not a divergent value — do not compare it against an explicit override as if both were authored choices. Before firing any of F-CURRENCY-01, F-DECIMAL-02, F-DATE-03, F-SEPARATOR-04, or F-NEGATIVE-07 on a given pair of placements, confirm at least one of the differing values is an explicit override (present as a `format="..."` attribute on that specific pill/placement in the worksheet XML). If a placement has no explicit override, record it as `inherited_default` in the finding's `differing_format_strings` list rather than treating it as a competing baseline candidate, and do not let it win the first-seen baseline in HC#11 over a placement with an explicit override.

## Cross-DS Info-by-Default Rule (HC#12)

For F-CURRENCY-01, F-DECIMAL-02, F-DATE-03, F-SEPARATOR-04, and F-NEGATIVE-07: cross-DS drift is Info-tier by default. Multi-currency, multi-region, or multi-locale reporting produces legitimate cross-DS format differences. Downgrade the Info-tier finding to a not-flagged status if the workbook caption explicitly documents the reason. Upgrade to Warning-tier only if the workbook contains no rationale and the same-symbol convention could reasonably be enforced.

## Sentinel Discipline

If a check cannot run (e.g., `get-worksheet-xml` fails on a dashboard-bound sheet, or `search-workbook-fields` fails), record the affected placements as `"unscanned"` with a rationale in the notes field. Never silently omit a placement.

## Refuse to Fabricate

Every finding cites one of the 7 rule IDs. Never invent a rule. Never reassign severity. Never mark a check "passed" without evaluating its signals against the baseline. Never establish a synthetic baseline; use the first-seen format string per HC#11.
