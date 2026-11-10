# Color & Accessibility Rules

Palette selection logic, WCAG compliance requirements, and accessible encoding patterns for all worksheet builds.

***

## Palette Selection Logic

Choose palette type based on what the color encodes:

| Data Scenario | Palette Type | Default Hex Values |
|---|---|---|
| Single measure, no breakdown | Solid primary | #4E79A7 |
| Sequential (low → high magnitude) | Single-hue gradient | #c6dbef → #2171b5 → #08519c |
| Diverging (below/above center) | Two-hue gradient | #E15759 ← #F0F0F0 → #59A14F |
| Categorical (≤7 distinct groups) | Distinct hues | #4E79A7, #F28E2B, #59A14F, #E15759, #EDC948, #B07AA1, #76B7B2 |
| Status/semantic (fixed meaning) | Semantic fixed | Good=#4E79A7 (blue) or #76B7B2 (teal), Alert/Critical=#F28E2B (orange) or #B07AA1 (magenta), Neutral=#9C9C9C (gray) — see "Default Status Palette" below |
| Highlight one, dim rest | Focal + gray | #4E79A7 (focal) + #D3D3D3 (non-focal) |
| Brand-specific | Brand-anchored | User provides; semantic colors remain standard |

***

## Palette Rules

1. **Max 7 categorical colors** per chart. If >7 categories: aggregate into "Other" or use highlight-one-dim-rest approach.

2. **Semantic color is mandatory for status.** If the chart shows good/bad/warning, use the Default Status Palette (blue/teal for good, orange/magenta for alert/critical, gray for neutral) plus a shape — never red/yellow/green alone (see "Default Status Palette" below). Never repurpose brand colors for status meaning.

3. **Gray is your best tool.** Use #9C9C9C or #D3D3D3 for: de-emphasis, baselines, gridlines, axes, non-focal elements. Gray lets data colors stand out.

4. **Consistent across worksheets.** If "West" is #4E79A7 in one sheet, it must be #4E79A7 in every sheet in the workbook. Assign colors by dimension value, not by position.

5. **Background: white or near-white.** #FFFFFF to #F5F5F5. Dark backgrounds only if explicitly branded and high-contrast verified.

6. **Text colors:** Primary = #333333 (titles, values). Secondary = #666666 (labels, subtitles). Tertiary = #999999 (annotations, footnotes).

***

## Brand-Anchored Palette Validation (Run Whenever the User Supplies Custom Hex Colors)

User-provided brand colors are accepted as-is for identity (row 19 of Palette Selection Logic), but they still must clear the same WCAG minimums as any other palette choice — "brand-anchored" is not an exemption. Before finalizing a spec that uses supplied hex values:

1. **Compute contrast against the dashboard background** (white/#FFFFFF or near-white by default) for each supplied color, using the standard WCAG relative-luminance formula. State the ratio, don't estimate it.
2. **Compute contrast between the supplied colors themselves** if they'll appear as adjacent marks (side-by-side bars, a two-color categorical split).
3. **Flag any color failing 3:1** (graphical elements/adjacent segments) or **4.5:1** (text/small labels) against its actual use context — a color can pass for large fills while failing for thin lines or small text against the same background, so check per intended use, not once in the abstract.
4. **Recommend a usage restriction, not a color swap, when only some uses fail.** E.g., a bright accent color that fails text-contrast on white can still be used for large bar fills or backgrounds with dark text on top — don't discard brand identity over a partial failure; scope it.
5. **Note colorblind-safety of the pair** if the brand supplies two-plus colors — most brand pairs are fine, but flag it explicitly if they sit close on the red-green axis (e.g. two similarly-saturated red/green or red/orange brand colors), since that's the one combination this project treats as unsafe by default regardless of source.

**Confirmed gap (2026-08-06):** A brand-color dashboard request (#1B365D navy + #E87722 orange) was accepted into a spec without this check being run at spec time — the contrast validation only happened afterward, reactively, when the user separately asked "do these colors work together?" The check belongs in Phase 6 of the main workflow, at the same time the palette is chosen, not as an optional follow-up.

***

## WCAG Accessibility Requirements (Non-Negotiable)

### Contrast Minimums (WCAG AA)

| Element | Minimum Ratio | Example |
|---|---|---|
| Body text on background | 4.5:1 | #333333 on #FFFFFF = 12.6:1 (pass) |
| Large text (≥18px or ≥14px bold) | 3:1 | #666666 on #FFFFFF = 5.7:1 (pass) |
| Graphical elements (bars, lines, marks) | 3:1 | #4E79A7 on #FFFFFF = 4.2:1 (pass) |
| Adjacent color segments | 3:1 between each other | Check neighboring bars/slices |

### Color Vision Deficiency Rules

1. **Never use red-green (or red/yellow/green) as the only distinction, and never use them at all as a default.** 8% of males have red-green color blindness. This project's default status palette is blue/teal (good) + orange/magenta (alert/critical) + gray (neutral) — not red/yellow/green — specifically because it reads correctly without relying on hue discrimination alone.
   - Bad: red bar vs. green bar with no other differentiation
   - Bad (even with labels): defaulting to red/green when a safer default palette is standard for this project
   - Good: blue bar vs. orange bar WITH text labels ("Above Target" / "Below Target") and a shape difference

2. **Safe color pairs for status (default palette):**
   - Blue (#4E79A7) or Teal (#76B7B2) = Good — universally distinguishable
   - Orange (#F28E2B) or Magenta (#B07AA1) = Alert/Critical
   - Gray (#9C9C9C) = Neutral/baseline
   - Dark blue + light blue (value intensity) — safe for all types
   - Red/Yellow/Green is NOT the default. Only use it if the user explicitly requests classic red/yellow/green semantics, and even then, triple-encode it (color + shape + text).

3. **Avoid rainbow scales entirely.** Not intuitive for magnitude AND problematic for color-blind users. Use single-hue sequential instead.

4. **Test mentally:** "If I printed this in grayscale, could I still read it?" If no, add a non-color encoding.

***

## Triple Encoding Rule (Status Indicators)

**Status MUST be encoded three ways: shape + color + text. Never color alone, and never color-only red/yellow/green even with text.**

### Default Status Palette (use this unless the user asks for something else)

| Meaning | Color | Shape (Tableau shape mark) |
|---|---|---|
| Good / On Track | Blue #4E79A7 or Teal #76B7B2 | Circle / checkmark shape |
| Alert / Critical | Orange #F28E2B or Magenta #B07AA1 | Triangle / warning shape |
| Neutral / Baseline | Gray #9C9C9C | Square / dash shape |

**Fallback if custom shapes are not available in the build environment:** keep the color pairing above (blue/teal = good, orange/magenta = alert/critical, gray = neutral) and rely on the required text label to carry the third encoding — do not fall back to red/yellow/green as the "simpler" option. Red/yellow/green is never the default fallback.

### Required Triple Encoding:

```
✅ ACCESSIBLE (default palette):
  Color                + Shape             + Text
  Blue/Teal            + ● / checkmark     + "On Track"
  Gray                 + ■ / dash          + "Caution"
  Orange/Magenta       + ▲ / warning       + "Alert"
```

```
❌ INACCESSIBLE / NOT THE DEFAULT:
  Green / Yellow / Red  (color only — excludes 8% of males)
  Red / Yellow / Green, even with text, when the default palette above was available and not explicitly requested
```

### Implementation in Tableau:

- Use a calculated field for status classification
- Shape mark for icon FIRST — use a custom/built-in shape (checkmark, warning triangle, square/dash) as the primary non-color differentiator; if shapes genuinely aren't available in the build path, do not drop the encoding down to color-only — keep the text label as the second required encoding
- Text mark or label for the word — always present regardless of shape availability
- Color mark for the background or shape fill, using the Default Status Palette (blue/teal/orange/magenta/gray), not red/yellow/green
- All present encodings (shape when available, color, text) appear together in the view

***

## Sequential Color Scales (for Maps, Heatmaps, Continuous Color)

### Recommended Sequential Palettes:

| Use Case | Palette | Hex Range |
|---|---|---|
| Default (any magnitude) | Blues | #c6dbef → #4292c6 → #08519c |
| Revenue/money | Blue-green | #e5f5e0 → #41ab5d → #006d2c |
| Temperature/heat | Orange-red | #fee5d9 → #fb6a4a → #a50f15 |
| Neutral/general | Gray | #f0f0f0 → #969696 → #252525 |

### Diverging Palettes (for above/below center):

| Use Case | Palette | Hex Range |
|---|---|---|
| Above/below target | Red-Gray-Green | #E15759 ← #F0F0F0 → #59A14F |
| Positive/negative change | Orange-Gray-Blue | #F28E2B ← #F0F0F0 → #4E79A7 |

**Diverging palette rules:**
- Center point must be meaningful (zero, target, average)
- Both extremes must be equally intense/saturated
- Midpoint should be neutral (white, light gray)

***

## Categorical Color Assignment

When assigning colors to dimension values:

1. **Assign by value, not by sort order.** "West" is always blue, regardless of where it appears.
2. **Most important category gets the most prominent color.** Use darker, more saturated colors for focal items.
3. **"Other" or aggregate categories get gray.** Reserve chromatic colors for distinct, named categories.
4. **Max 7 colors.** Beyond 7, human ability to distinguish and remember color mappings drops sharply.

### Default Categorical Palette (in priority order):

| Position | Hex | Name | Use For |
|---|---|---|---|
| 1 | #4E79A7 | Steel Blue | Primary/most important category |
| 2 | #F28E2B | Orange | Secondary category or warning |
| 3 | #59A14F | Green | Third category or positive status |
| 4 | #E15759 | Red | Fourth category or negative status |
| 5 | #EDC948 | Gold | Fifth category |
| 6 | #B07AA1 | Purple | Sixth category |
| 7 | #76B7B2 | Teal | Seventh category |
| N/A | #9C9C9C | Gray | "Other", de-emphasized, or baseline |

***

## Typography for Accessibility

| Element | Minimum Size | Weight | Color |
|---|---|---|---|
| KPI value | 28-48px | Bold | #333333 |
| Chart title | 18-20px | Medium/Bold | #333333 |
| Subtitle/context | 11-12px | Regular | #666666 |
| Axis labels | 10-12px | Regular | #666666 |
| Data labels | 10-12px | Regular | #333333 |
| Annotations | 10-11px | Italic or Regular | #666666 |
| Tooltip text | 11-12px | Regular | #333333 |

**Never go below 10px for any text that needs to be read.**

***

## Applying Color in the Shelf Recipe

When specifying color in a worksheet spec:

```
COLOR:
  - [Field name] | [Palette type: Sequential/Diverging/Categorical] | [Specific palette: Blues/Orange-Blue/Tableau 10]
  - OR: Single color | #4E79A7
  - OR: Status encoding | Good=#4E79A7/#76B7B2 (blue/teal), Alert/Critical=#F28E2B/#B07AA1 (orange/magenta), Neutral=#9C9C9C (gray) | Triple-encoded with [shape field] + [label field]; use red/yellow/green only if explicitly requested by the user
```

Always note when the color assignment requires custom configuration beyond Tableau's default palette assignment.
