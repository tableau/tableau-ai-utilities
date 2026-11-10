# Domain 4: Layout and Hierarchy (Locked)

Evaluates dashboard layout structure, visual hierarchy, scan path, container use, and canvas discipline.

## Score Anchors

| Score | Description |
|---|---|
| 10 | Clear F-pattern or Z-pattern scan path; primary metric anchors the layout; container structure is sound; no orphan zones. |
| 8-9 | Strong hierarchy with one minor issue (e.g., one competing element, one alignment gap). |
| 6-7 | Solid layout with 2-3 hierarchy or alignment gaps. |
| 4-5 | Developing; scan path unclear or hierarchy inverted (secondary metric visually dominates the primary). |
| 2-3 | Weak layout; readers must hunt for the primary information. |
| 1 | No discernible hierarchy; layout reads as tiled random content. |

## Signals Evaluated

**Scan path.**

- Does the layout support a clear scan path (F-pattern for text-heavy; Z-pattern for chart-heavy; center-out for KPI-focused)?
- Is the primary metric in the top-left (Latin left-to-right reading) or top-center (for chart-heavy layouts)?

**Visual hierarchy.**

- Is the most important information visually dominant (size, position, color contrast, whitespace around)?
- Do secondary elements defer to primary elements without competing?

**Container structure.**

- Are zones aligned to a grid? Fractional-pixel offsets read as sloppy.
- Are containers nested no deeper than 4 levels? Deeper nesting increases edit-in-Desktop friction and often signals design overrun.
- Are there orphan floating zones inside tiled containers?

**Canvas discipline.**

- Is the canvas size appropriate for the audience? Executive dashboard on a 4K canvas is a mismatch.
- Are empty zones minimized? Excess whitespace suggests incomplete design or missing content.
- Are decorative elements (logos, banners) proportional to their information value?

**Zone density.**

- Compact dashboards should not exceed 8 zones. Wide dashboards should have clear zone grouping (headers, filters, primary, secondary).
- Do filter zones cluster together (left rail, top strip) rather than scatter across the canvas?

## Common Downgrades

- Primary KPI positioned below or to the right of secondary charts.
- Filter zones scattered across the canvas rather than clustered.
- Container depth greater than 4 levels visible in layout (crowded, over-nested feel).
- Empty white zones larger than the primary KPI.
- Decorative elements (logos, banners) larger than the primary KPI or centrally placed.
- Charts of similar visual weight competing for the reader's first attention.
- No visible zone grouping (headers vs. filters vs. body vs. footer).
- Alignment drift: zones off-grid by more than a few pixels visibly.

## Calibration Examples

**Example 4.1 → Score 9.** F-pattern scan path clearly established. Primary KPI (Revenue) in top-left, secondary KPIs below, supporting charts in a grid below the KPI row. Filter zone clustered on the left rail. No orphan floating zones, no zero-dimension containers, container nesting 3 levels deep. Empty zones minimized. Signal: hierarchy inverted-pyramid, alignment on grid, one minor gap (footer whitespace slightly larger than needed).

**Example 4.2 → Score 6.** Primary KPI positioned in the middle of the canvas, not top-left. Filter zone split across top strip and right rail. Two zones with visible fractional-pixel offsets. Signal: hierarchy weak but present; filter placement fights the scan path; alignment drift on two zones. Solid but with clear gaps.

**Example 4.3 → Score 3.** Company logo occupies the top 20% of the canvas. Primary KPI is the same size as three supporting charts. Filter zones scattered across every edge (top, left, right, bottom). Container nesting 6 levels deep with a floating zone inside a tiled container. Signal: decorative element dominates, no clear primary metric, filter chaos, over-nested containers. Weak; scan path is a hunt.

## Long-Form Dashboards (HC#12)

If image aspect ratio is taller than 2:1, Domain 4 scoring depends on seeing the full canvas. Do not score Domain 4 on a partial image; flag UNSCANNED with `reason: layout_requires_full_canvas`. Offer per-section re-runs and combine on the last invocation.

## XML Context Sharpening

When workbook is open and `get-dashboard-xml` is available:

- Cross-reference visible zones against XML zone declarations for count and ordering.
- Detect container nesting depth from XML for the depth-4 check.
- Detect floating zones that may not be visible in the image but affect layout.

Cite XML-derived signals in the rationale ("XML confirms 6-level container nesting under the filter panel").

## Handoff Payload for Layout Fixes

If Domain 4 scores below 7, the report handoff payload includes:

- Routing to `dashboard-preflight` for per-zone alignment and canvas-size audits (P-ZONE-01, P-CANVAS-06, P-CONTAINER-08).
- User opts in per HC#6.

## Refuse to Fabricate

Cite specific zone references in the rationale. Never invent a hierarchy issue to lower the score. If a zone's role is ambiguous from the image, flag confidence and use the lower anchor.
