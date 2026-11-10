# Geocoding Checks Catalog (Locked)

Six locked checks. Never invent a G7. Every finding cites its check ID.

## G1. Role Mismatch

**Signature.** Field has a geographic role assigned, but sample values don't match the expected format for that role.

**Detection.** Compare a sample of values (via `get-summary-data`) against expected patterns:
- City role: expects free-text names (e.g., "Boston").
- Zip Code role: expects 5-digit strings (US) or postal-code patterns.
- Country role: expects country names or ISO codes.
- State/Province role: expects state names or 2-letter codes.
- Latitude/Longitude role: expects numeric values in valid ranges.

**Severity.** Warning if the field is placed on any shelf. Info if the field is unused.

**Fix.** Right-click field → Geographic Role → choose correct role. If the correct role isn't in the list, consider a calc to reshape the values first.

## G2. High Unmatched Rate

**Signature.** More than 5% of the field's values return "Unknown" when Tableau attempts geocoding.

**Detection (estimated proxy — read this before running G2).** `get-summary-data` returns raw field values, not Tableau's actual geocoding-engine resolution status; there is no tool-accessible way to read the true Unknown count directly (same underlying gap as "cannot see rendered map output" in Known Limitations). Sample values via `get-summary-data` and flag a value as a likely-Unknown proxy when it matches any of: a non-Latin script outside the expected locale, an obvious typo/malformed pattern for the assigned role (see G1's expected-format list), or an empty/null value. Report the resulting rate as an **estimate**, explicitly labeled "estimated (proxy: format/script mismatch), not Tableau's actual resolution count." If the user can share the map's own "N unknown" indicator (visible in Desktop when the map is built), prefer that number and label it "verified from map."

**Severity.** Critical if >15%. Warning if 5-15%. Info if <5%. Applies to the estimated or verified rate, whichever is used.

**Fix.** Investigate the Unknowns (typos, alternate spellings, non-English names). Consider a cleanup calc or a manual mapping via Edit Locations dialog.

## G3. High Ambiguous Rate

**Signature.** More than 5% of the field's values resolve to multiple possible locations, requiring Tableau to guess.

**Detection (estimated proxy — read this before running G3).** Same underlying gap as G2: `get-summary-data` cannot read Tableau's actual Ambiguous-resolution status. Sample via `get-summary-data` and flag a value as a likely-Ambiguous proxy when it matches the locked ambiguous-city list (see G4) or another known multi-location name pattern, without an accompanying Country/State field to disambiguate. Report the resulting rate as an **estimate**, explicitly labeled "estimated (proxy: ambiguous-name list match without disambiguating field), not Tableau's actual resolution count." If the user can share the map's own "N ambiguous" indicator, prefer that number and label it "verified from map."

**Severity.** Critical if >15%. Warning if 5-15%. Info if <5%. Applies to the estimated or verified rate, whichever is used.

**Fix.** Add a Country or State field to disambiguate. Or use the Edit Locations dialog to lock resolutions.

## G4. Wrong Country Resolution

**Signature.** City values that could exist in multiple countries (Springfield, Cambridge, London, Athens) are resolving to a country other than the intended one because no Country context is present.

**Detection.** Sample values, cross-reference against the locked ambiguous-city list below, check whether a Country field is present alongside.

**Severity.** Warning if any known ambiguous city is present without Country context.

**Fix.** Add Country as a Detail encoding on the map, or as a disambiguating dimension.

### Ambiguous-City List (Locked)

20 canonical shared city names that resolve differently across countries.

| City Name | Common Country Resolutions |
|---|---|
| Springfield | US (multiple states), UK, Australia |
| Cambridge | UK, US (MA, MN, NY, OH), Canada, New Zealand |
| London | UK, Canada (ON), US (OH, KY) |
| Athens | Greece, US (GA, OH, TN, AL) |
| Rome | Italy, US (GA, NY) |
| Paris | France, US (TX, TN, KY, ME) |
| Vienna | Austria, US (VA, WV) |
| Moscow | Russia, US (ID, PA) |
| Alexandria | Egypt, US (VA, LA, MN) |
| Manchester | UK, US (NH, CT) |
| Portland | US (OR, ME), Australia, Jamaica |
| Columbus | US (OH, GA, IN, MS) |
| Georgetown | US (DC), Guyana, Cayman Islands, Malaysia |
| Salem | US (OR, MA, NH), India |
| Richmond | US (VA, CA, KY, IN), UK, Australia |
| Franklin | US (multiple states), New Zealand |
| Clinton | US (multiple states) |
| Newton | US (MA, KS, IA), UK |
| Fairfield | US (CT, CA, OH, NJ), Australia |
| Riverside | US (CA, MO, IL), UK |

**Detection cadence.** When any field value matches this list AND no Country field is present in the workbook's data source, G4 fires with Warning severity. If two or more list matches appear in the same field, escalate to Critical.

## G5. Missing Hierarchy

**Signature.** Country field is present but no State/Province or City field is available for drill-down.

**Detection.** Enumerate all geographic fields. If Country is present but no State or City exists at the same level, flag.

**Severity.** Note (users may not need drill in every map).

**Fix.** Consider adding a State or City field if drill is desired.

## G6. Role-vs-Datatype Conflict

**Signature.** Geographic role assigned to a field with an incompatible datatype (Geographic role on a Number field intended as a measure, or a String field with numeric zip codes).

**Detection.** Cross-check field's role against datatype.

**Severity.** Warning.

**Fix.** Either change the role or split the field (measure copy vs. dimension copy). Right-click → Convert to Dimension / Measure.

## Sampling Cadence

One `get-summary-data` sample per geographic field. Batch across all applicable checks. Do not re-sample per check.

## Refuse to Fabricate

If a symptom doesn't fit G1-G6, report "outside current check catalog; consult manual geocoding docs" and.
