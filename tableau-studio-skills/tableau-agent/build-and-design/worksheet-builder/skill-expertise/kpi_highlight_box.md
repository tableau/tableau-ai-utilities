# KPI Highlight Box (Square Shape, Background-Matched)

A styling pattern for single-number KPI tiles: a Square mark maximized in size and colored to match the dashboard background, so the number appears to float on a full-bleed highlight card with no visible mark border. Text is centered both horizontally and vertically.

No `bind-template` template covers this — it is a manual worksheet-XML edit applied on top of an existing Text/KPI worksheet (e.g. the output of a `kpi-text` bind-template build).

## When to use

- User asks for a KPI "highlight box", "square background", "card-style" tile, or describes wanting the number to blend into the dashboard background.
- Single-value KPI, no status color needed (not the triple-encoding status tile — see KPI Tile (Status) above).

## Recipe

1. Build or locate the KPI worksheet (mark type already `Square` if built via `kpi-text`; otherwise change mark type first).
2. `get-worksheet-xml` to fetch the current cached file.
3. Confirm/add these elements inside `<pane>` (direct children, per the general encoding placement rules in `tactics/viz/marks-and-encodings.md`):

```xml
<pane ...>
  <view>...</view>
  <mark class="Square"></mark>
  <encodings>
    <text column="[DS].[sum:Measure:qk]"></text>
  </encodings>
  <mark-sizing mark-sizing-setting="marks-scaling-off"></mark-sizing>
  <style>
    <style-rule element="cell">
      <format attr="text-align" value="center"></format>
      <format attr="vertical-align" value="center"></format>
    </style-rule>
    <style-rule element="mark">
      <format attr="mark-labels-show" value="true"></format>
      <format attr="mark-labels-cull" value="true"></format>
      <format attr="mark-color" value="#ffffff"></format>
      <format attr="size" value="100"></format>
    </style-rule>
    <!-- Per-field font sizing: the general "axis label color" pattern in marks-and-encodings.md
         uses a field= attribute on <format> to target one field at table scope. This is UNCONFIRMED
         for element="datalabel" font-size — verify by reading the worksheet XML back after apply
         before trusting it; don't report success without checking. If field= is ignored here (applies
         one size to the whole mark), fall back to a two-sheet tile (see "Multi-size text" below). -->
    <style-rule element="datalabel">
      <format attr="font-size" field="[DS].[sum:Measure:qk]" value="36"></format>
      <format attr="font-size" field="[DS].[usr:YoYCalc:qk]" value="22"></format>
    </style-rule>
  </style>
</pane>
```

4. `apply-worksheet` with the modified file.

## Key facts

- **`mark-sizing-setting="marks-scaling-off"`** (sibling of `<style>`, direct child of `<pane>`) disables automatic size scaling so the manual size format takes effect.
- **`<format attr="size" value="100">`** inside `style-rule element="mark"` maximizes the square (higher = larger; `100` renders as full-bleed for a single KPI mark — the earlier documented small value of `"2"` in `marks-and-encodings.md` is for a *small* fixed size, not this maxed case).
- **`<format attr="mark-color" value="#ffffff">`** sets the square's fill — set this to the dashboard's actual background hex, not always white. Ask the user for their dashboard background color if it isn't white/default.
- **Centering** needs both `text-align` (horizontal) and `vertical-align` (vertical) on `style-rule element="cell"` — one alone leaves the number off-center.
- **Minimum font size: `font-size` ≥ `20`** on `style-rule element="datalabel"` (sibling of the `element="mark"` rule, per the general label-styling rule in `marks-and-encodings.md`) for the main KPI number. Below 20 the number reads as secondary detail text, not the headline metric — this is a hard floor for the primary value text encoding, not a suggestion.
- **Secondary/comparison text (YoY %, "vs. prior period", etc.) should render at ~60% of the main number's font size**, not the same size — a same-size stack reads as two equal headlines instead of one primary metric with supporting detail. E.g. main value 36-40pt → comparison text ~22-24pt.
- **This skill does not yet have a confirmed working XML pattern for two different font sizes within one mark's stacked text encodings** — see the "Multi-size text" caution below. Do not report a two-size result as verified without reading the applied worksheet XML back and confirming both `font-size` values actually differ per field; a single `style-rule element="datalabel"` may apply one size to the whole mark regardless of a `field=` filter.

### Multi-size text — CONFIRMED pattern (2026-08-06)

Two different font sizes within one mark's stacked text **does work**, but not via a `field=`-scoped `style-rule element="datalabel"` format — it uses a `<customized-label>` block with per-run `fontsize` attributes instead. Confirmed by reading back applied worksheet XML after a manual Desktop edit (KPI: current-period value at 20pt, comparison % at 12pt, both center/middle aligned):

```xml
<pane ...>
  <mark class="Automatic"></mark>
  <encodings>
    <text column="[DS].[usr:CurrentValueCalc:qk]"></text>
    <text column="[DS].[usr:ComparisonPctCalc:qk]"></text>
  </encodings>
  <customized-label>
    <formatted-text>
      <run fontsize="20">&lt;[DS].[usr:CurrentValueCalc:qk]&gt;</run>
      <run>&#10;</run>
      <run fontsize="12">&lt;[DS].[usr:ComparisonPctCalc:qk]&gt;</run>
    </formatted-text>
  </customized-label>
  <style>
    <style-rule element="cell">
      <format attr="text-align" value="center"></format>
      <format attr="vertical-align" value="center"></format>
    </style-rule>
    <style-rule element="mark">
      <format attr="mark-labels-show" value="true"></format>
      <format attr="mark-labels-cull" value="true"></format>
    </style-rule>
  </style>
</pane>
```

- Each stacked field still needs its own `<text>` encoding — the `<customized-label>` block only controls the *rendering* (size, line breaks) of the already-encoded fields; it doesn't add fields on its own.
- The `<run>&#10;</run>` empty run is the line break between the two text lines — without it both values render on one line.
- Field tokens inside `<run>` use the bracketed placeholder form `&lt;[DS].[column-instance]&gt;`, matching the exact column-instance name used in `<encodings>`.
- Set the comparison calc's percent format on the calc column itself (`default-format="p0.0%"` or similar), not in the label markup — number formatting and font-size are separate concerns.
- This was reached via a *manual Desktop edit*, not a live `add-field`/`apply-worksheet` chain — `apply-worksheet` failed repeatedly (6 consecutive failures) when trying to stack a second/third text encoding onto an existing `kpi-text`-built sheet in this environment (see `feedback_top_n_sort_blocked_on_calc_fields`-adjacent apply flakiness). If the automated add-field path fails after 2 attempts, hand the user this exact XML recipe as manual Desktop steps rather than retrying.
- `mark-labels-show`/`mark-labels-cull` must stay `true` or the text encoding won't render at all (see general label rule in `marks-and-encodings.md`).
- **A YoY/comparison ask needs its own encoding, not just the base measure.** A "KPI with YoY comparison" request needs a *second* `<text>` encoding (or a second sheet) carrying the YoY calc (e.g. `[Current - Prior] / ABS(Prior)`, see `calc_templates.md`) — binding only `SUM(Measure)` satisfies the KPI half but silently drops the comparison the user actually asked for. Check for an existing YoY calc via `list-available-fields` before authoring a new one.
- **Check whether the comparison calc is already aggregated before binding it to the shelf.** A YoY %/ratio calc built as `(SUM(IF...) - SUM(IF...)) / ABS(SUM(IF...))` is already a fully-aggregated (AGG) expression — bind it with the **`usr:`** column-instance form (`derivation="User"`, e.g. `[usr:CalcName:qk]`), never `sum:` (`derivation="Sum"`). Binding an AGG calc with `sum:`/`derivation="Sum"` re-aggregates an already-aggregated value and silently produces a wrong number with no error — this matches the general `[AGG]` bare-reference rule in the system prompt, but it applies to shelf/encoding column-instances too, not just formula bodies. Verify by reading the calc's own formula (`grep` the workbook XML for the calc name, or `resolve-field`) before choosing the CI prefix, and confirm the bound value with `get-summary-data` (its column name will read `AGG(...)` for a correctly-bound AGG calc, `SUM(...)` if wrongly double-aggregated).

## Common mistakes

- Forgetting `mark-sizing-setting="marks-scaling-off"` — the size format is ignored without it, and the square stays at default auto-scaled size.
- Only setting `text-align` and skipping `vertical-align` — text ends up horizontally centered but vertically pinned to one edge of the cell.
- Hardcoding `mark-color` to white without checking the dashboard's real background — defeats the "blends into background" goal on a non-white dashboard.
- Applying this to a status KPI (up/down, on-track/alert) — this pattern is value-only; status tiles still need the triple color+icon+text encoding.
- Leaving the datalabel at default font size — always set `font-size` to at least `20` for the primary KPI value.
- Binding a "KPI with YoY/comparison" ask to only the base measure and treating the KPI as done — verify a comparison field (YoY %, prior period, etc.) actually landed as a second encoding before calling the build complete.
