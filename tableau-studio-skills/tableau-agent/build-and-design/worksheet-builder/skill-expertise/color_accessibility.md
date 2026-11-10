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
| Status/semantic (fixed meaning) | Semantic fixed | Green=#59A14F, Yellow=#F28E2B, Red=#E15759 |
| Highlight one, dim rest | Focal + gray | #4E79A7 (focal) + #D3D3D3 (non-focal) |
| Brand-specific | Brand-anchored | User provides; semantic colors remain standard |

***

## Palette Rules

1. **Max 7 categorical colors** per chart. If >7 categories: aggregate into "Other" or use highlight-one-dim-rest approach.

2. **Semantic color is mandatory for status.** If the chart shows good/bad/warning, use green/yellow/red (or accessible equivalent). Never repurpose brand colors for status meaning.

3. **Gray is your best tool.** Use #9C9C9C or #D3D3D3 for: de-emphasis, baselines, gridlines, axes, non-focal elements. Gray lets data colors stand out.

4. **Consistent across worksheets.** If "West" is #4E79A7 in one sheet, it must be #4E79A7 in every sheet in the workbook. Assign colors by dimension value, not by position.

5. **Background: white or near-white.** #FFFFFF to #F5F5F5. Dark backgrounds only if explicitly branded and high-contrast verified.

6. **Text colors:** Primary = #333333 (titles, values). Secondary = #666666 (labels, subtitles). Tertiary = #999999 (annotations, footnotes).

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

1. **Never use red-green as the only distinction.** 8% of males have red-green color blindness.
   - Bad: red bar vs. green bar with no other differentiation
   - Good: red bar vs. green bar WITH text labels ("Above Target" / "Below Target")

2. **Safe color pairs for status:**
   - Blue (#4E79A7) + Orange (#F28E2B) — universally distinguishable
   - Dark blue + light blue (value intensity) — safe for all types
   - Green + Red — OK only if triple-encoded (see below)

3. **Avoid rainbow scales entirely.** Not intuitive for magnitude AND problematic for color-blind users. Use single-hue sequential instead.

4. **Test mentally:** "If I printed this in grayscale, could I still read it?" If no, add a non-color encoding.

***

## Triple Encoding Rule (Status Indicators)

**Status MUST be encoded three ways. Never color alone.**

### Required Triple Encoding:

```
✅ ACCESSIBLE:
  Color     + Icon     + Text
  Green     + ✓        + "On Track"
  Yellow    + ⚠        + "Caution"  
  Red       + ✗        + "Alert"
```

```
❌ INACCESSIBLE:
  Green / Yellow / Red  (color only — excludes 8% of males)
```

### Implementation in Tableau:

- Use a calculated field for status classification
- Shape mark for icon (custom shapes: checkmark, warning triangle, X)
- Text mark or label for the word
- Color mark for the background or shape fill
- All three appear together in the view

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
  - OR: Status encoding | Green=#59A14F, Yellow=#F28E2B, Red=#E15759 | Triple-encoded with [shape field] + [label field]
```

Always note when the color assignment requires custom configuration beyond Tableau's default palette assignment.
