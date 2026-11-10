# Container Patterns

Exact nesting patterns, sizing modes, padding values, and distribution rules for Tableau dashboard container assembly.

***

## Build Technique: Outside-In with Placeholders

The single biggest cause of dashboard layout frustration is runaway nested containers. Tableau's default behavior when you drop a container inside another container is to fill the entire parent area, meaning the next container you add goes inside it rather than beside it. That creates "container inside container inside container" hierarchies that are painful to undo.

**The placeholder trick prevents this entirely:**

1. **Start with the outermost container.** Drag a vertical container onto the blank dashboard. It fills the entire canvas.
2. **Add placeholder objects (Blanks or Text) to reserve space.** Before dropping any child containers, drag 2-3 Blank objects into the outer container. Label them "Header", "Body", "Footer" (matching your zones). This forces Tableau to divide the parent into clear, separate slots.
3. **Replace placeholders with real containers.** Drag a horizontal container directly onto a placeholder. It replaces the placeholder and takes that slot. Repeat for each zone.
4. **Nest further using the same technique.** Inside any new container, add placeholders again before nesting deeper. This keeps every level of the hierarchy intentional.
5. **Check the Item hierarchy after every drop.** Open the Layout pane and verify each object landed where expected. If it didn't, undo immediately. Fixing hierarchy later is much harder.

**Naming convention:** Rename containers as you create them (right-click > Rename Item) so "Horizontal Container 4" becomes "KPI Row" in your hierarchy.

***

## Tiled vs. Floating

| Mode | Behavior | Use For |
|---|---|---|
| Tiled (default) | Snaps into structured grid, resizes predictably | Main dashboard structure (95% of layout) |
| Floating | Fixed pixel position, layers on top | Navigation buttons, info overlays, pop-up panels, annotations |

**Rule:** Build the main structure tiled. Use floating selectively for elements that layer on top. Hold Shift while dragging to make an item floating.

**Converting tiled to floating:** No direct conversion exists. Create a new floating container, drag content from tiled into it, then delete the empty tiled container.

***

## Container Types

| Container | Orientation | Use For |
|---|---|---|
| Horizontal | Arranges items left-to-right | Side-by-side charts, KPI rows, filter bars |
| Vertical | Arranges items top-to-bottom | Stacking sections, sidebars, full-page structure |

**Nesting rule:** Alternate orientations. Outer vertical holds horizontal rows. Each horizontal row holds vertical columns. This prevents layout collapse.

***

## Sizing Modes

### Dashboard-Level Sizing

| Mode | When to Use | Dimensions |
|---|---|---|
| Fixed | Known display context (embedded, kiosk, presentation) | Exact width x height in pixels |
| Range | Mixed devices but within known bounds | Min/max width x height |
| Automatic | Unknown display context (rare, avoid) | Fits to browser window |

**Default recommendation:** Fixed at 1400x900 unless spec says otherwise.

### Container-Level Sizing

| Sizing | Behavior | Use For |
|---|---|---|
| Fixed height/width | Stays at exact pixel value regardless of content | Headers (60-80px), KPI rows (60-80px), footers (30-40px), filter bars (40-50px) |
| Fill remaining | Expands to use whatever space is left | Body/chart containers (primary and secondary zones) |
| Fit | Sizes to content inside | Text objects, small annotations (use sparingly, unpredictable) |

**Rule:** Fix what must stay constant (headers, KPI height, footers). Fill what should grow (chart areas). Never "Fit" on chart containers.

***

## Standard Nesting Patterns

### Pattern 1: Executive (KPI + 2-zone body)

```
Dashboard (Fixed: 1400x900)
└── Outer Vertical Container (fill)
    ├── Header Horizontal (fixed: 70px)
    │   ├── Title text (left-aligned)
    │   └── Filter controls (right-aligned)
    ├── KPI Horizontal (fixed: 80px)
    │   ├── KPI Sheet 1 (distribute evenly)
    │   ├── KPI Sheet 2 (distribute evenly)
    │   └── KPI Sheet 3 (distribute evenly)
    ├── Body Horizontal (fill remaining)
    │   ├── Primary Vertical (60% width)
    │   │   └── Primary Chart Sheet (fill)
    │   └── Secondary Vertical (40% width)
    │       ├── Secondary Sheet 1 (50% height)
    │       └── Secondary Sheet 2 (50% height)
    └── Footer Horizontal (fixed: 30px)
        └── Source/context text
```

### Pattern 2: Manager (KPI + Grid body)

```
Dashboard (Fixed: 1400x900)
└── Outer Vertical Container (fill)
    ├── Header Horizontal (fixed: 60px)
    │   ├── Title text
    │   └── Filter controls (3-4 filters inline)
    ├── KPI Horizontal (fixed: 70px)
    │   ├── KPI Sheet 1
    │   ├── KPI Sheet 2
    │   ├── KPI Sheet 3
    │   └── KPI Sheet 4
    ├── Top Row Horizontal (fill: 50%)
    │   ├── Chart 1 Vertical (60%)
    │   └── Chart 2 Vertical (40%)
    └── Bottom Row Horizontal (fill: 50%)
        ├── Chart 3 Vertical (50%)
        └── Chart 4 Vertical (50%)
```

### Pattern 3: Analyst (Filter sidebar + body)

```
Dashboard (Fixed: 1600x900)
└── Outer Horizontal Container (fill)
    ├── Filter Sidebar Vertical (fixed: 220px)
    │   ├── Filter 1
    │   ├── Filter 2
    │   ├── Filter 3
    │   ├── Filter 4
    │   └── Reset button
    └── Body Vertical (fill remaining)
        ├── KPI Horizontal (fixed: 70px)
        │   ├── KPI 1
        │   ├── KPI 2
        │   └── KPI 3
        ├── Primary Chart (fill: 60%)
        └── Secondary Row Horizontal (fill: 40%)
            ├── Chart 2 (50%)
            └── Chart 3 (50%)
```

### Pattern 4: Operations (Vertical stack, no split)

```
Dashboard (Fixed: 1400x900)
└── Outer Vertical Container (fill)
    ├── Header Horizontal (fixed: 50px)
    │   ├── Title: "SYSTEM STATUS"
    │   └── Last updated timestamp
    ├── KPI Horizontal (fixed: 70px)
    │   ├── Status indicator
    │   ├── Uptime %
    │   ├── Active alerts count
    │   └── P95 response time
    ├── Alert List Sheet (fill: 40%)
    └── Trend Chart Sheet (fill: 60%)
```

### Pattern 5: Multi-Page (Navigation between dashboards)

```
Page 1: Overview Dashboard
└── Outer Vertical Container (fill)
    ├── Header Horizontal (fixed: 60px)
    │   ├── Title
    │   └── Navigation buttons (linked to Page 2, Page 3)
    ├── Summary content (fill)
    └── Footer (fixed: 30px)

Page 2: Detail Dashboard
└── Outer Vertical Container (fill)
    ├── Header Horizontal (fixed: 60px)
    │   ├── "< Back to Overview" button
    │   └── Detail-specific filters
    └── Detail content (fill)
```

***

## Padding & Spacing Rules

| Context | Inner Padding | Outer Padding | Gap Between |
|---|---|---|---|
| Dashboard border | N/A | 12px all sides | N/A |
| Container holding charts | 8px all sides | N/A | 8-12px between items |
| Container holding KPIs | 4px all sides | N/A | 0px (distribute evenly handles spacing) |
| Filter bar container | 8px top/bottom, 12px left/right | N/A | 12px between filters |
| Text objects | 8px all sides | N/A | N/A |

**Notes:**
- Padding is set on the container, not on individual objects inside it
- "Distribute Contents Evenly" on KPI containers eliminates the need for manual spacing
- If items look too crowded, add padding to the parent container (not individual elements)

***

## Distribute Contents Evenly

**What it does:** Divides the container's space equally among all child elements.

**When to use:**
- KPI rows (3-5 equal-width KPI tiles)
- Summary metric rows
- Equal-column grids

**When NOT to use:**
- Primary/secondary splits (you want 60/40, not 50/50)
- Containers with fixed-height elements mixed with fill elements
- Containers where one element is intentionally larger

**How to apply:** Set on the parent container. Overrides any fixed width/height on child elements.

***

## Percentage-Based Splits

When the spec says "60/40 split" or "50/25/25":

**For horizontal splits (side-by-side):**
- Set the Body Horizontal container to "fill remaining" height
- Set each child vertical container's width as a proportion
- 60/40: left child = 60% of parent width, right child = 40%
- Percentages should total exactly 100%

**For vertical splits (stacked):**
- Set each child's height as a proportion of the parent container's height
- 50/50: each child = 50% of parent height
- Common vertical splits: 60/40 (primary/secondary), 70/30 (chart/table), 50/25/25 (three rows)

**Fallback:** If percentage control isn't precise enough, use fixed pixel values calculated from the dashboard dimensions. For a 1400x900 dashboard with 60/40 split after an 80px header: body height = 900 - 80 = 820px. Left container = 840px wide (60% of 1400), right = 560px.

***

## Container Ordering

**Build from outside in:**

1. Create the outermost container (usually Vertical)
2. Add the fixed-height children first (header, KPI row, footer)
3. Add the fill container(s) for the body
4. Inside the body, add horizontal or vertical containers for splits
5. Inside each split container, place the worksheets

**Do NOT:**
- Start by placing worksheets and then try to wrap them in containers (order matters)
- Use floating containers for structural layout (floating is for overlays only)
- Nest more than 4 levels deep (Header > Body > Split > Column > Sheet is the max typical depth)
- Put a tiled element inside a floating container or vice versa

***

## Common Container Failures

| Problem | Cause | Fix |
|---|---|---|
| Container collapses to 0 height | No child has "fill" sizing | Set at least one child to fill |
| Elements overflow/clip | Total fixed heights exceed dashboard height | Reduce fixed heights or use range sizing |
| Uneven KPI tiles | Not using "Distribute Contents Evenly" | Apply distribute on KPI parent |
| Chart squished in one direction | Wrong container orientation | Verify horizontal vs. vertical matches layout intent |
| Blank space at bottom | Footer has "fill" instead of fixed | Set footer to fixed height |
| Filter bar displaces chart area | Filter bar sized too tall | Fix filter bar height at 40-50px |
| Runaway nesting (container inside container inside...) | Dropped containers without placeholders first | Undo, add Blank placeholders, then re-drop containers beside them |
| New object lands inside instead of beside | Tableau default "fill parent" behavior | Use placeholder trick; check Item hierarchy after every drop |

***

## Assembly Best Practices

- **Use Blanks for spacing, not extra containers.** Need a gap between two charts? Add a Blank object and resize it. Don't nest another container just to create whitespace.
- **Adjust padding before adding containers.** The Layout pane lets you set inner and outer padding on any object. Most spacing problems are solved with padding rather than additional structure.
- **Colour containers temporarily while building.** Give each container a different background color during assembly. It makes the structure visible at a glance and confirms where new objects will land. Remove the colors once the layout is locked in.
- **Pin sizes for fixed elements.** Headers, navigation rows, and filter panels want fixed pixel heights or widths. Set these explicitly in the Layout pane so they don't resize at different dashboard sizes.
- **Use thin text objects as separator lines.** A clean way to add dividing lines between sections without needing images.
- **Copy and paste container structures.** Since Tableau 2021.4, you can copy and paste entire container structures via the right-click menu. For repeating tile patterns (KPI cards), build the template once and duplicate.
- **Deleting a container without losing content.** Select the container in the Item hierarchy, click the dropdown arrow, and choose "Remove Container." This removes only the wrapper; worksheets inside stay intact on the dashboard.

***

## Reference Links

- [Organize Dashboard Objects with Layout Containers](https://help.tableau.com/current/pro/desktop/en-us/dashboards_organize_floatingandtiled.htm)
- [Dashboard Best Practices](https://help.tableau.com/current/pro/desktop/en-us/dashboards_best_practices.htm)
- [Create Dashboards](https://help.tableau.com/current/pro/desktop/en-us/dashboards_create.htm)
