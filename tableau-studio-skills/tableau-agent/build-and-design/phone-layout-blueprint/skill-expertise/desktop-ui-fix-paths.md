# Desktop UI Fix Paths (P1-P15)

Numbered Desktop UI instructions for each rule in the P-catalog. The skill's Audit output pulls the fix steps from here. Blueprint mode's numbered-steps section is composed from the same paths.

All paths are for Tableau Studio. Paths assume the workbook is open and the phone layout is selected in the Layout pane.

## P1. Fixed sizing on the phone layout

1. In the Dashboard pane on the left, click **Size**.
2. In the Size dropdown, select **Fixed size**.
3. If a size is not already chosen, pick a preset (typical phone: 375x812 or 414x896) or enter a custom width and height.
4. Save the workbook.

## P2. Vertical stack over horizontal containers

1. Open the Layout pane.
2. Click the top-level container in the phone layout.
3. If it is a horizontal container (indicated by side-by-side child arrangement), right-click and select **Change to Vertical Container**.
4. Repeat for any nested horizontal containers that span the full phone width.
5. Verify each nested chart still fits inside 375px wide after the swap.

## P3. KPI band at the top

1. Identify the KPI sheet on the desktop layout. If no KPI sheet exists, build one first on the desktop dashboard using a summary calculation (SUM, AVG, or similar single-value output).
2. In the phone layout, drag the KPI sheet to the top of the vertical container.
3. If the top 500px of the phone layout is currently occupied by a title, chart, or filter, hide those on phone (right-click → Hidden on phone) or move them below the KPI band.
4. Verify the KPI is visible without scrolling on a 375x812 preview.

## P4. Sheet count ceiling 4-5 sheets

1. Count sheets on the phone layout. If over 5, decide which to hide.
2. Priority to keep: KPI band, primary chart, one secondary chart, one detail table (if needed).
3. For each sheet to remove: right-click the sheet in the Layout pane → **Hidden on phone**.
4. Verify total sheet count on the phone layout is 4-5 or fewer.

## P5. Hidden-on-phone flag on titles, secondary KPIs, and duplicate legends

1. In the Layout pane, click the dashboard title text object.
2. Right-click → **Hidden on phone**.
3. Repeat for secondary KPI text objects.
4. For each color legend: check whether the mark color is already interpretable in context. If yes, right-click the legend → **Hidden on phone**.
5. Reload the phone layout preview to confirm the elements are hidden.

## P6. Filter count ceiling 2-3 visible

1. Count visible filter cards on the phone layout.
2. If over 3, decide which to keep visible: the 2-3 filters users interact with most.
3. Move the rest into a show/hide floating container per P7.

## P7. Show/hide floating container

### Tableau 2020.4 or later (preferred path)

1. In the Layout pane, add a **Floating** container to the phone layout.
2. Set the container size to a compact box (typical: 300x400 float).
3. Drag the excess filters into the floating container.
4. Add a **Button** object to the phone layout, positioned at the top-right (or wherever screen space allows).
5. Configure the button: right-click the button → **Edit Button** → set **Button Action** to **Set Container Visibility** → target the floating container.
6. Set the button icon to a filter icon (upload PNG or use built-in).
7. Set the floating container's initial state to hidden.
8. Test: tapping the button toggles the container visibility.

### Pre-2020.4 fallback (HC-9)

Show/hide floating containers with button-triggered visibility are not available in versions before 2020.4. Use this fallback path instead:

1. Build a separate worksheet named "Filters" that exposes the filter fields as a small control panel (drag filter cards onto a scratch sheet, size it compactly).
2. Add the Filters worksheet to the phone layout as its own vertical container, placed at the top or bottom of the stack.
3. On the desktop layout, right-click the Filters worksheet → **Hidden on phone**? No, reverse: on the phone layout keep it visible; on the desktop layout, right-click → **Hidden on desktop** if that variant exists in your version, otherwise leave the Filters worksheet visible on desktop too.
4. Set the Filters worksheet's container size so it does not dominate the KPI band.
5. Ask the user their Tableau version if you cannot determine which path applies. Never route them to the modern path without confirming the version supports it.

## P8. Tap-target size 44x44px minimum

1. For each interactive element (filter, button, parameter control, clickable mark):
   - Filters: click the filter card → drag the card border to at least 44px height and width.
   - Buttons: click the button → in the properties, set width and height to 44 or larger.
   - Parameter controls: click the parameter card → resize as with filters.
   - Clickable marks inside a chart: reduce the total number of marks in the view (through filtering or aggregation) so each mark is at least 44x44px at the chart's rendered size.
2. If a mark cannot be sized to 44x44px because of density, replace the interaction with a parameter action or list of button objects (P9).

## P9. Parameter actions preferred over quick filters

1. For each quick filter that is a candidate: identify the field and the values users select.
2. Create a parameter with the same data type and the same allowable values.
3. Build a control worksheet: drag the field to Rows or Columns to expose the values, then set up a parameter action (**Worksheet menu** → **Actions** → **Add Action** → **Change Parameter**).
4. Configure the action: source is the control sheet, target is the parameter, run on **Select**.
5. In the phone layout, replace the quick filter with the control worksheet.
6. Update the sheets that used the filter to reference the parameter instead (via a filter calc: `[Field] = [Parameter]` on the Filters shelf).
7. Test: tapping a value on the control sheet updates the target sheets in one tap.

## P10. Vertical scroll length under 3 phone-screens-tall

1. Check the phone layout's current fixed height in the Dashboard pane.
2. If the height exceeds roughly 2000-2400px (3 phone-screens):
   - Hide additional sheets per P4.
   - Reduce sheet heights (drag the sheet's container border shorter).
   - Move detail views to a show/hide floating container per P7.
3. Verify total height is under 2400px.

## P11. Text size floor: 12pt body, 14pt headers

1. For each text object on the phone layout: click the text → **Edit Text** → set font size to 12pt or larger.
2. For headers: 14pt or larger.
3. For chart tooltips: right-click each sheet → **Tooltip** → set font size to 12pt or larger.
4. For axis labels: right-click axis → **Format** → set font size to 12pt or larger.
5. Preview on the phone canvas to verify legibility.

## P12. Color-only encoding accessibility

1. For each color-encoded distinction: identify the field driving color.
2. Add a redundant encoding:
   - **Icon prefix in the label.** Edit the mark label → add a text calc like `IF [KPI Status] = "On Track" THEN "✓" ELSE "✗" END + " " + [Label]`.
   - **Shape variation.** Change the mark type to Shape and map the same field to Shape.
   - **Arrow prefix.** For delta indicators: `IF [Change] > 0 THEN "▲" ELSE "▼" END`.
3. Preview to confirm the distinction is legible without relying on color.

## P13. Preference-flag check

Runs Preference-flag mode. See `preference-flag-steps.md` for the numbered path.

## P14. Sheet-inclusion audit (specific sheets to hide)

For each sheet flagged as hidden-on-phone in the Audit:

1. In the Layout pane, expand the phone layout's container tree.
2. Right-click the target sheet → **Hidden on phone**.
3. Confirm the sheet is grayed out in the phone canvas.

Combine with P4 to verify total sheet count is at 4-5 or fewer after the hides.

## P15. Container-swap audit (specific containers to swap)

For each horizontal container flagged for swap:

1. In the Layout pane, click the container.
2. Right-click → **Change to Vertical Container**.
3. If the container had specific child sizing (fixed widths), reset the children to responsive sizing after the swap.
4. Verify the swap did not break the layout: reload the phone canvas preview.

## Fix sequencing recommendation

When applying multiple fixes at once, sequence in this order to avoid rework:

1. **P1 Fixed sizing.** Do this first; every downstream fix assumes fixed sizing.
2. **P13 Preference-flag check.** If the author never wanted the layout, this is the whole answer.
3. **P4 + P14 Sheet inclusion.** Reduce sheet count before adjusting layout.
4. **P15 Container swap.** Swap containers before sizing tap targets.
5. **P2 Vertical stack top-level.** Confirms top-level after any container swap.
6. **P3 KPI at top.** Once containers are vertical, place the KPI.
7. **P5 Hidden-on-phone flags.** Hide titles, secondary KPIs, legends.
8. **P6 + P7 Filter strategy.** Collapse filters into show/hide.
9. **P8 Tap-target sizing.** Size all remaining interactive elements to 44x44px.
10. **P9 Parameter actions.** Replace two-tap quick filters where beneficial.
11. **P10 Scroll length.** Verify total height under 2400px after all reductions.
12. **P11 Text sizing.** Set text and font sizes.
13. **P12 Color encoding.** Add redundant encodings last.

## Version-specific notes

- **Tableau 2020.4+.** Show/hide floating containers with button-triggered visibility available. If the author is on an older version, P7 is not implementable and the workaround is a separate filters-only worksheet in the phone layout.
- **Tableau 2021.2+.** Improved phone-layout preview mode. Author can preview the layout without switching devices.
- **Tableau 2022.3+.** Custom fonts on Cloud/Server are consistent. Older versions may substitute fonts on mobile devices; P11 legibility is more critical then.
