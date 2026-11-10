# Custom Number Formatting — Known Gaps and Safe Path

**Status: weak spot.** There is no confirmed, field-tested XML pattern in this skill for setting a per-field custom number format (Format > Number > Custom in the Desktop UI, e.g. a semicolon-delimited positive;negative;zero pattern like `▲ 0.0%;▼ -0.0%;0.0%`). Do not guess at this live in a user's workbook — a wrong attribute name is silently stripped on round-trip with no error, which wastes an apply cycle and can look like success when it isn't (see Failed Attempts below).

## What NOT to do

- Do not invent a `<format attr="numeric-format" ...>` or similar style-rule and apply it hoping it round-trips. Confirmed **does NOT work** (stripped silently, 2026-08-03): a table-level `<style-rule element="cell"><format attr="numeric-format" field="[DS].[usr:Calc:qk]" value="...">` block. The whole style-rule was dropped on `apply-worksheet` round-trip — `get-worksheet-xml` readback showed no trace of it.
- Do not report a numeric-format edit as applied/successful based on the generic "readback clean" message from `apply-worksheet` alone — that message reflects structural validation, not that every element you wrote survived. Always grep the re-fetched worksheet XML for your specific attribute/value before claiming it worked (this generalizes the verification discipline already used for calcs — see `feedback_verify_calcs_against_real_data` project memory).

## Safe path: discovery-then-replicate

1. Ask the user to apply the custom format once manually in Tableau Studio: right-click the field → **Format...** → **Numbers** pane → **Custom** → enter the pattern.
2. Call `get-worksheet-xml` on that worksheet immediately after.
3. Inspect the cached XML for whatever new node or attribute appeared — this is the *actual* schema Tableau uses in this Desktop version, not a guess.
4. Record the confirmed pattern back into this file (replace this section) so future builds don't need to repeat the discovery step.

## Fallback if the user can't/won't apply it manually

Offer the underlying value pre-formatted as a display-only calculated field instead of fighting the number-format XML — e.g. a string calc like `IF [YoY %] >= 0 THEN "▲ " + STR(ROUND([YoY %]*100,1)) + "%" ELSE "▼ " + STR(ROUND([YoY %]*100,1)) + "%" END` placed on Text. This is authorable today via `author-calc` with confirmed syntax, at the cost of losing native numeric semantics (won't sort/aggregate as a number, tooltips show the string). State this tradeoff explicitly rather than silently substituting it as if it were the same as native number formatting.

## Currency + thousands-separator display calc (confirmed fallback recipe)

For a request like "show this total as currency with thousand separators" combined into a text label (e.g. a percent-and-total mark label: `"43.8% ($683,456)"`), two things to know before authoring:

1. **`REGEXP_REPLACE` can silently no-op on this datasource.** A formula like `REGEXP_REPLACE(STR(ROUND(SUM([Measure]),0)), "(\d)(?=(\d{3})+(?!\d))", "$1,")` applies with no error, but the output comes back unformatted (no commas inserted) — confirmed live 2026-08-03. Don't assume Tableau's `REGEXP_*` functions work here just because `apply` succeeds; verify the actual computed string via `get-summary-data`.
2. **Confirmed working fallback (no regex, manual thousands separator)** for values under ~7 digits:
   ```
   "$" + (IF LEN(STR(ROUND(SUM([Measure]),0))) > 3
          THEN LEFT(STR(ROUND(SUM([Measure]),0)), LEN(STR(ROUND(SUM([Measure]),0)))-3) + "," + RIGHT(STR(ROUND(SUM([Measure]),0)),3)
          ELSE STR(ROUND(SUM([Measure]),0))
          END)
   ```
   Extend the branching (nest another nested nested IF for a second comma) if values can exceed 999,999.
3. **If you re-author a calc under the SAME caption/name that already exists in the datasource, Tableau keeps the OLD formula** — editing a calc's XML copy embedded in a worksheet's `datasource-dependencies` is a no-op. Recreate under a distinct caption (e.g. append " v2") via `author-calc`, then rebind the encoding to the new calc, rather than patching the existing column def in place.

## Related

- `kpi_highlight_box.md` — the KPI tile pattern this formatting is usually requested for; also documents per-encoding font sizing.
