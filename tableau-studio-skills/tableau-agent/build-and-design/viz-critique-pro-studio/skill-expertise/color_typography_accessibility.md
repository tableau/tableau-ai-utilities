# Domains 5 and 6: Color, Typography, and Accessibility (Locked)

Covers Domain 5 (Color and Typography) and Domain 6 (Accessibility). Both share the shared portfolio color and typography catalog.

## Shared Portfolio Color Catalog

Every dashboard evaluated against this catalog:

- **Good/positive.** Blue #4E79A7 or Teal #59A89C + upward triangle shape.
- **Alert/critical.** Orange #E87722 or Magenta #B07AA1 + downward triangle or X shape.
- **Neutral/caution.** Gray #9C9C9C + circle or dash shape.
- **Red/yellow/green retired for accessibility reasons.**
- **Triple encoding required** for every status indicator: color + shape + text label.

**Sequential palettes.** Single-hue gradients (blues: #c6dbef to #08519c) for continuous measures on maps and heatmaps.

**Categorical palettes.** Maximum 7 distinct colors. Use Tableau's built-in palettes or brand-anchored derivations. Never rainbow.

**Brand-anchored mode.** When the user provides brand hex codes, anchor the palette to those colors (primary = structural, secondary = accent) and derive additional tints/shades rather than adding unrelated colors.

## Domain 5: Color and Typography

**What it measures.** Color palette discipline and typographic execution.

**Score anchors:**

| Score | Description |
|---|---|
| 10 | Palette aligns with the shared catalog; triple encoding present on all status indicators; typography hierarchy clear and consistent. |
| 8-9 | Strong alignment with 1-2 minor drift issues (one status indicator missing a shape, one font-family variant). |
| 6-7 | Solid but with 3-4 drift issues or one significant palette mismatch. |
| 4-5 | Developing; rainbow palette OR retired red/yellow/green status colors OR typographic drift across 5+ elements. |
| 2-3 | Weak; color-only status encoding, multiple palette violations. |
| 1 | Fundamental color or typography failure (all-red alert dashboard, or mixed decorative fonts). |

**Color-specific downgrades:**

- Rainbow palette (more than 7 categorical colors).
- Red/yellow/green status without accessible alternatives (violates the retired-palette rule).
- Divergent palette on sequential data (implies bidirectionality that doesn't exist).
- Sequential palette on categorical data (implies ordinality that doesn't exist).
- Color-only status encoding (no shape, no text label; violates triple-encoding requirement).
- Brand palette applied inconsistently (primary color used on secondary elements).

**Typography-specific downgrades:**

- Multiple font families across similar element categories (title font drift, tooltip font drift).
- Font size drift larger than 4 points across similar elements.
- Font weight inconsistency (semibold title on one worksheet, bold on another).
- Decorative fonts on data visualization elements.
- Illegible sizes at the intended viewing distance (10pt on Executive dashboard is a downgrade).

## Domain 6: Accessibility

**What it measures.** Whether the dashboard is usable by readers with visual impairments, color-vision differences, or accessibility needs.

**Score anchors:**

| Score | Description |
|---|---|
| 10 | Passes WCAG AA contrast; triple encoding on all status; text alternatives present; keyboard-navigable structure implied by layout. |
| 8-9 | Strong with 1-2 accessibility gaps (one contrast issue, one missing shape). |
| 6-7 | Solid with 3-4 accessibility gaps or one significant WCAG failure. |
| 4-5 | Developing; color-only status encoding OR low contrast on 3+ elements. |
| 2-3 | Weak; multiple WCAG failures. |
| 1 | Inaccessible; dashboard cannot be read by common color-vision differences. |

**Accessibility-specific downgrades:**

- Contrast failure (WCAG AA text contrast below 4.5:1 for body text; below 3:1 for large text).
- Color-only status without shape or label.
- Missing text alternatives (chart labels, axis labels, tooltip labels).
- Illegible font sizes.
- Red/green combinations for good/bad status (common colorblindness pattern).
- Missing keyboard-navigability signals (no visible focus states in interactive elements).

## Calibration Examples

### Domain 5 Calibration

**Example 5.1 → Score 9.** Color palette aligned with shared portfolio catalog: blue (#4E79A7) for positive, orange (#E87722) for alert, gray (#9C9C9C) for neutral. Triple encoding on all three status indicators (color + upward triangle + text label). Typography consistent: Tableau Book for body, Tableau Bold for titles, no font-family drift, sizes at 10pt (tooltip), 12pt (axis), 14pt (title). Strong.

**Example 5.2 → Score 6.** Palette drifts on one chart from Tableau default (Blue-Orange) to a rainbow-adjacent categorical with 6 colors that includes yellow. Two font families visible (Arial on one worksheet, Tableau Book on the others). Signal: rainbow-adjacent flag + font drift. Solid but with three drift issues.

**Example 5.3 → Score 3.** Rainbow categorical palette with 9 colors (violates the max-7 rule). Retired red/yellow/green status without shape encoding. Font family drift across every worksheet. Two title fonts at 10pt (illegible for Executive audience). Weak.

### Domain 6 Calibration

**Example 6.1 → Score 9.** WCAG AA text contrast passes on all body text (>= 4.5:1). Triple encoding present on all status indicators. Text alternatives visible on axis labels and tooltips. Legend uses same encoding as marks. Passes accessibility audit.

**Example 6.2 → Score 6.** Contrast passes on primary body text but fails on secondary caption text (3.8:1, below 4.5:1). Status indicators use color only (no shape). Signal: two accessibility gaps.

**Example 6.3 → Score 3.** Red/green good/bad status without alternatives. Contrast fails on 3 elements. Illegible font sizes at 8pt on Executive dashboard. Multiple WCAG failures.

**Example 6.4 → Score 4.** Word cloud with green-to-gold sequential gradient for a secondary measure. Pale-end gradient labels (e.g., pale green artist names) render below 4.5:1 against a light background. Peak Position is encoded color-only with no redundant text or shape cue. Signal: A11y-TREEMAP-01-adjacent (word-cloud gradient contrast) fires + color-only encoding fires. Two accessibility gaps on the primary chart.

**Example 6.5 → Score 5.** Treemap with olive mark colors and olive labels inside cells (label-vs-mark contrast estimated near 3.0:1, below 4.5:1). Contrast passes on axis labels and legend text. Signal: A11y-TREEMAP-01 fires on treemap labels only.

## Signals Evaluated

**Contrast.**

- Text vs. background contrast ratio. Estimate from image; flag confidence when the estimate is close to the threshold.
- Chart-mark contrast against background.
- Axis label contrast.
- **Treemap and heatmap label contrast against mark color** (A11y-TREEMAP-01). Treemap cells and heatmap tiles color the background; labels sit inside that colored region. Estimate label-vs-mark contrast (not label-vs-canvas). Common failure: olive labels on olive treemap cells, dark-navy labels on medium-blue heatmap tiles, or gray labels on any pastel mark. Cite the specific cell and estimate the ratio.
- **Word cloud label contrast on gradient-colored text.** When word cloud labels use a color gradient (e.g., green-to-gold sequential palette), the pale-end labels frequently fall below 4.5:1 against a light canvas. Check the lightest gradient step against the canvas background.

**Palette discipline.**

- Count distinct colors used across the dashboard.
- Compare status colors against the shared portfolio catalog.
- Detect rainbow, retired-palette, or divergent-on-sequential misuse.

**Triple encoding.**

- Every status indicator has color + shape + text.
- Legend uses the same encoding as the marks.

**Typography.**

- Font family consistency across similar element categories.
- Font size consistency within a category (title = 14pt across all worksheets, tooltip = 10pt across all tooltips).
- Font weight consistency.
- Legibility at intended viewing distance.

## Common Downgrades

- Red/green good-vs-bad status (colorblind failure).
- Color-only KPI status indicators (no shape, no text).
- Rainbow categorical palette (more than 7 colors).
- Font-family drift across text objects.
- Font-size drift greater than 4 points in similar elements.
- Contrast failures on axis labels, tooltip labels, or secondary text.
- Sequential palette applied to a categorical dimension.
- Divergent palette applied to a sequential measure.

## Handoff Payload for Fixes

If Domain 5 or 6 scores below 7, the report handoff payload includes:

- Routing to `format-drift-scanner` for text-format drift (which owns font family, font size, and format-string consistency).
- Manual Desktop fixes for palette issues (right-click > Format > Color; right-click > Edit Colors).

## Refuse to Fabricate

Cite specific color values or contrast ratios (approximate from image) in the rationale. Flag confidence when estimating. Never invent a WCAG failure to lower the score. Never suppress a color-only status issue to raise the score.
