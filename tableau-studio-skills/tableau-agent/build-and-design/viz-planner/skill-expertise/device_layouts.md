# Device Layouts

Responsive dashboard design for tablet and phone breakpoints. Desktop-first assembly with progressive reduction for smaller screens.

***

## Strategy: Desktop-First, Then Subtract

The instruction sequence to give the user is:
1. Finish the full desktop dashboard first (this is always the primary deliverable)
2. If device layouts are requested, instruct creating tablet and phone layouts by HIDING elements, not by rebuilding
3. Keep KPIs and the primary chart on all breakpoints
4. Lower-priority elements get hidden on smaller screens

**Do NOT design mobile-first.** The desktop version is always the master layout.

***

## Breakpoints

| Device | Typical Size | Tableau Layout Setting |
|---|---|---|
| Desktop | 1400x900 (or per spec) | Default dashboard size |
| Tablet (landscape) | 1024x768 | Add device layout: Tablet |
| Tablet (portrait) | 768x1024 | Optional, rarely needed |
| Phone (portrait) | 375x667 | Add device layout: Phone |

**When to create device layouts:**
- User explicitly requests tablet/phone versions
- DASHBOARD REQUEST spec mentions "responsive" or "multi-device"
- Dashboard will be consumed via Tableau Mobile

**When to skip device layouts:**
- Desktop-only consumption (embedded in portal, presentation mode)
- No mention of mobile in the spec
- Dashboard is too complex for meaningful mobile reduction (analyst dashboards with 8+ charts)

***

## Element Survival Rules

### Always Survives (All Breakpoints)

- KPI BAN tiles (the headline numbers)
- Primary chart (the single most important visualization)
- Date context (the user must know the time frame)
- At least one interactive filter (date or primary dimension)

### Survives to Tablet, Hidden on Phone

- Secondary charts (supporting context)
- Filter bar with multiple controls (condense to 1-2 on phone)
- Legend (if separate from chart)
- Footer/source text

### Desktop Only (Hidden on Tablet and Phone)

- Tertiary/exploratory charts
- Detail tables with many columns
- Multi-filter sidebars
- Annotations and lengthy text objects
- Navigation menus with many options (simplify to one "back" button)

***

## Tablet Layout Adjustments

| Desktop Pattern | Tablet Adaptation |
|---|---|
| 60/40 horizontal split | Stack vertically (primary on top, secondary below) |
| 3-column grid | 2-column grid (third element moves to next row) |
| Sidebar filters | Move filters to horizontal bar above content |
| 4 KPIs in a row | Keep 4 in a row (still fits at 1024px) |
| Wide table (many columns) | Hide lowest-priority columns or use horizontal scroll |

**Tablet sizing:** 1024x768 (landscape). The vertical space is constrained, so:
- Reduce header height from 70px to 50px
- Reduce KPI row from 80px to 60px
- Remove footer if non-critical

***

## Phone Layout Adjustments

| Desktop Pattern | Phone Adaptation |
|---|---|
| Multi-chart dashboard | Single chart (primary only) + KPIs |
| Horizontal KPI row | Stack KPIs vertically (one per row, 50px each) |
| Any horizontal split | Convert to vertical stack |
| Filter bar | Single dropdown filter above content |
| Legend | Hide (rely on tooltip or inline labels) |
| Title + subtitle | Title only (shorten if needed) |
| Navigation buttons | Single "back" link |

**Phone sizing:** 375x667. Extremely constrained. Rules:
- Maximum 2-3 elements visible without scrolling
- KPIs should show the 2 most important values only (not all 4)
- Primary chart fills available width
- No side-by-side layouts (everything stacks vertically)
- Font sizes may need to increase for touch readability

***

## Instructions for Hiding Elements on Device Layouts

Dashboard Assembler is advisory-only — give the user these exact Desktop steps rather than attempting to perform them:

1. "Dashboard menu → Device Layouts → Add Layout → [Tablet or Phone]."
2. "Elements from the desktop layout appear automatically on the new device layout."
3. "For each element that shouldn't survive to this breakpoint (see Element Survival Rules above): select it, then click the X or 'Remove from layout' — this only hides it on this device layout, the desktop version is untouched."
4. "Rearrange remaining elements for the new dimensions by dragging within the device layout view."

**What "hiding" means (relay this to the user):**
- The element still exists on the desktop dashboard
- It simply doesn't appear on the device-specific layout
- No data is lost; users can access the desktop version for full details
- Filters that are hidden still apply if they have defaults set

**What "hiding" means:**
- The element still exists on the desktop dashboard
- It simply doesn't appear on the device-specific layout
- No data is lost; users can access the desktop version for full details
- Filters that are hidden still apply if they have defaults set

***

## Device-Specific Interaction Considerations

### Tablet

- Hover actions don't work on touch (no "mouse hover" on tablets)
- Convert hover highlights to tap highlights
- Filter actions on Select still work (tap = select)
- Increase tap target size: marks should be at least 44x44px touchable area
- Tooltips appear on long-press, not hover

### Phone

- Even more constrained than tablet for interaction
- Prefer pre-filtered states over interactive filtering
- One filter maximum (usually date or primary dimension)
- Actions between sheets are less useful (only 1-2 sheets visible)
- Focus on "glanceable" KPI values

***

## Implementation Checklist (When Device Layouts Requested)

- [ ] Desktop layout complete and verified first
- [ ] Tablet layout created with appropriate elements hidden
- [ ] Phone layout created with maximum reduction
- [ ] KPIs survive all breakpoints
- [ ] Primary chart survives all breakpoints
- [ ] Date context visible on all breakpoints
- [ ] At least one filter accessible on tablet
- [ ] Hover-based interactions have tap alternatives on touch layouts
- [ ] Font sizes readable at each device's DPI
- [ ] No horizontal scrolling required on any breakpoint

***

## When NOT to Build Device Layouts

State this clearly to the user/upstream skill:
- "This analyst dashboard has 8 charts with cross-filtering. A phone layout would lose so much context that it wouldn't serve the analysis purpose. Recommend desktop-only with a note that Tableau Mobile users see a simplified auto-layout."
- "The operations dashboard relies on real-time table scanning. Mobile consumption should use Tableau Mobile's native summary view instead of a custom phone layout."

Not every dashboard benefits from device layouts. Simple KPI-only dashboards scale well. Complex analytical dashboards do not.
