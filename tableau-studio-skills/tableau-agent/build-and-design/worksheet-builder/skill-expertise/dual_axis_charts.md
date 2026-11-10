# Dual-Axis Charts (Two Different Measures) — What's Programmatic and What Isn't

## Hard limitation: creating a true merged dual axis is NOT programmatic

Putting two different measures on the same shelf (e.g. Rows) via `+` and emitting the confirmed pane structure (see `tactics/viz/pane-structure.md` Test 2 — anchor pane + one named pane per measure with `y-axis-name`) produces the correct **multi-measure pane setup**, but this alone does NOT merge them into one overlaid dual-axis chart. Confirmed live (2026-08-03): building that exact pane structure via `apply-worksheet` left the chart stacked/merged incorrectly on Rows. The user had to perform the actual "Dual Axis" merge manually in Tableau Studio (right-click the second measure's axis → **Dual Axis**).

**Do not promise a user that dual-axis creation can be done purely via XML/API.** After the pane structure is correct, tell them the one remaining step is a single manual click in Desktop, and offer the discovery workflow below to capture whatever else they do next.

## The actual dual-axis merge marker (discovered by reading back a user-created dual axis)

After the user manually created the dual axis, `get-worksheet-xml` revealed the real signal — NOT in `<panes>`, but in the table-level `<style>`:

```xml
<style-rule element="axis">
  <encoding attr="space" class="0" field="[DS].[sum:Quantity:qk]" field-type="quantitative"
            fold="true" scope="rows" type="space"/>
</style-rule>
```

This `<encoding type="space" fold="true">` element (not the panes) is what actually tells Tableau to merge the stacked panes into one overlaid plot with two y-scales.

## Synchronize Axis — confirmed attribute

Toggling **Synchronize Axis** (right-click either axis in a dual-axis chart) adds `synchronized="true"` to that SAME `<encoding type="space">` element:

```xml
<encoding attr="space" class="0" field="[DS].[sum:Quantity:qk]" field-type="quantitative"
          fold="true" scope="rows" synchronized="true" type="space"/>
```

No new element — just the added attribute on the existing dual-axis marker. Confirmed live 2026-08-03.

**Unsyncing IS programmatic** (unlike creating the dual axis itself): read the worksheet XML, delete the `synchronized="true"` attribute from that same `<encoding type="space">` element (leave `fold="true"` and everything else intact — that's the dual-axis merge itself, not the sync), and re-apply. Confirmed live 2026-08-03 — no manual Desktop step needed for this direction, only for the initial dual-axis merge.

## When to advise FOR or AGAINST Synchronize Axis (judgment, not just mechanics)

**Advise AGAINST syncing** when the two measures are in different units or scales with no shared meaning (e.g. Sales in dollars vs. Quantity in units, tens of thousands vs. low thousands). Forcing both axes onto the same numeric range squeezes the smaller-scale measure into a flat sliver near zero — it destroys the exact readability benefit dual-axis was meant to provide. A "crossing point" between two differently-unit'd lines is meaningless, so there's no analytical upside, only a downside.

**Advise FOR syncing** when the two measures are comparable in meaning or unit — Actual vs. Target of the same metric, two measures already on similar scales, or any case where a crossing point or relative-magnitude comparison is meaningful. In those cases, synchronized scales make the comparison legible in a way independent scales would obscure.

When a user asks to add a second measure to an existing chart, proactively note this tradeoff before syncing blindly — don't sync just because the option exists.

## Recipe (as far as XML can take you)

1. Put both measures on the same shelf: `<rows>([DS].[sum:MeasureA:qk] + [DS].[sum:MeasureB:qk])</rows>`
2. Emit the confirmed pane structure — see `tactics/viz/pane-structure.md` Test 2 exactly (anchor pane with NO `id`, then `<pane id="1" y-axis-name="MeasureA">`, `<pane id="2" y-axis-name="MeasureB">`). Do not add a redundant third pane or `y-index` — that pattern is for the SAME field placed twice (line+circle overlay), not two different measures.
3. Apply and verify with `get-worksheet-xml` that the pane structure survived (id numbering, y-axis-name values).
4. Tell the user the pane setup is done and ask them to do the one remaining manual step (Dual Axis merge) in Desktop, OR if they've already done it, read back and confirm the `<encoding type="space">` marker is present.
5. Before offering Synchronize Axis, check whether the two measures share a comparable unit/scale — advise against it if they don't, per the judgment section above.
