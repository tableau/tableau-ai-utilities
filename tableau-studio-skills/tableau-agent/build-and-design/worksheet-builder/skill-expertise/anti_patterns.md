# Anti-Pattern Catalog

15 chart selection and design anti-patterns organized by severity. Check every worksheet spec against this list before finalizing.

***

## Critical (Always Block and Replace)

These are never correct. When detected, block the anti-pattern and build the correct alternative automatically. No exceptions.

### 1. 3D Charts of Any Kind
- **Problem:** Perspective distorts perception; elements in back appear smaller than they are
- **Detection:** User requests "3D bar", "3D pie", any mention of 3D effects
- **Response:** "3D distorts perception. I'll build the 2D version."
- **Fix:** Use 2D version of the same chart type

### 2. Pie Chart with >5 Slices
- **Problem:** Humans cannot accurately compare more than 5 angles
- **Detection:** Composition question + dimension has >5 values
- **Response:** "Pie charts fail beyond 5 slices. Switching to sorted bar."
- **Fix:** Horizontal bar chart, sorted high to low. Or treemap if hierarchy matters.

### 3. Dual Y-Axes Without Clear Justification
- **Problem:** Can be manipulated to show any relationship; scales mislead magnitude comparison
- **Detection:** User requests two measures on same chart with different scales
- **Response:** "Dual axes can mislead. I'll use two separate charts side by side."
- **Fix:** Two separate charts, or index both measures to a common baseline (% change from period 1)
- **Exception:** Only proceed if user explicitly insists AND both axes are clearly labeled AND the purpose is correlation (not magnitude comparison)

### 4. Misleading Y-Axis (Non-Zero Start Without Indication)
- **Problem:** Visual magnitude doesn't match data magnitude; bar starting at 950 instead of 0 makes 5% difference look like 500%
- **Detection:** Bar chart where the y-axis doesn't start at zero
- **Response:** "Bars must start at zero or the visual lengths mislead. Adding zero baseline."
- **Fix:** Start axis at 0 for bar charts (always). For line charts, non-zero is acceptable if the trend shape is the point.

### 5. Alphabetical Sort on Ranked Data
- **Problem:** Hides the ranking insight; user has to mentally re-sort
- **Detection:** Bar chart with categorical dimension sorted A-Z when the question is comparison or ranking
- **Response:** "Sorting by value for clearer ranking. Say 'keep alphabetical' to override."
- **Fix:** Sort descending by measure value (or ascending for "bottom N")
- **Exception:** When the dimension has inherent order (months, stages, age groups, A/B/C grades)

***

## High (Warn, Offer Alternative, Proceed if User Insists)

These are usually wrong but have rare valid use cases. Warn the user, present the better option, but build their request if they override.

### 6. Line Chart Connecting Non-Ordered Categories
- **Problem:** Lines imply continuity and order that doesn't exist between categories
- **Detection:** Line mark type with a nominal dimension (products, regions, names) on the axis
- **Response:** "Lines imply order between points. Switching to bar chart. Want me to keep the line?"
- **Fix:** Bar chart. Lines only connect ordered data (time, sequential stages).

### 7. Stacked Bars When Segment Comparison is the Goal
- **Problem:** Only the baseline segment is aligned; middle/top segments are impossible to compare accurately
- **Detection:** Stacked bar where the user's question emphasizes comparing individual segments (not totals)
- **Response:** "Stacked bars make segment comparison hard (only baseline is aligned). Suggest grouped bars or small multiples. Override?"
- **Fix:** Grouped bars, or separate charts per segment
- **When OK:** If total comparison is more important than segment comparison

### 8. Radar/Spider Charts
- **Problem:** Area distortion, hard to read values, rarely adds insight over simpler alternatives
- **Detection:** User requests "radar", "spider", "web chart"
- **Response:** "Radar charts distort area and are hard to read precisely. Suggest parallel bar charts or small multiples. Override?"
- **Fix:** Small multiples of horizontal bars, or parallel coordinates
- **Exception:** Extremely rare cases of cyclical data (clock hours, compass directions)

### 9. Spaghetti Lines (>6 Series)
- **Problem:** Too many overlapping lines create visual chaos; no single trend is readable
- **Detection:** Line chart with color dimension having >6 distinct values
- **Response:** "7+ lines create visual noise. I'll use small multiples (one sparkline per category) or highlight one line and gray the rest. Preference?"
- **Fix options:**
  - Small multiples (sparkline grid)
  - Highlight approach (one series colored, rest gray, interactive swap)
  - Filter to top N series

### 10. Gauges for Everything
- **Problem:** Uses enormous space for a single number; inefficient when multiple KPIs needed
- **Detection:** User requests multiple gauges, or gauge for a metric without natural min/max
- **Response:** "Gauges use a lot of space for one number. KPI tiles (number + sparkline + status) are more compact. Want tiles instead?"
- **Fix:** KPI tile with number + trend + comparison
- **When OK:** Metric naturally has bounded range (0-100%, temperature, utilization) AND only 1-2 gauges total

### 16. Signed Measure on Size
- **Problem:** Size can only show bigger or smaller. It cannot show a sign and has no zero point, so a loss renders as a small mark, indistinguishable from a small gain. Readers misread losses as "low but positive."
- **Detection:** A measure placed on Size (or as the bubble-size variable) whose name contains "Profit," "Margin," "Variance," "Change," "Diff," "Delta," "Growth," "Net," "Balance," or "%", OR whose `get-summary-data` values include any number below 0.
- **Response:** "[Measure] can be negative, and Size can't show negatives, so losses would look like small profits. I'll put it on Color with a diverging palette instead and use [non-negative measure] for Size. Override?"
- **Fix:** Move the signed measure to Color (diverging, centered at 0) or Label. Use a never-negative measure for Size (Sales, Quantity, a count). If the user insists on Size, use ABS() only with the sign shown on Color, and say so.

***

## Medium (Note and Proceed)

These are context-dependent. Note the concern, proceed with the build, but mention the alternative.

### 11. Tables When Pattern Matters
- **Problem:** Numbers in rows/columns hide the visual pattern that a chart reveals instantly
- **Detection:** User asks for a table but the underlying question is about trends, comparisons, or rankings
- **Response:** Build the chart. Note: "I went with a chart to show the pattern. If you also need a detail table for exact values, I can build one alongside."
- **When OK:** User needs exact values for copy/paste, reference lookup, or export

### 12. Pie Chart for Time Series
- **Problem:** Pie charts cannot show change over time; no temporal axis
- **Detection:** Part-to-whole question + time-based breakdown
- **Response:** "Pie can't show change over time. Using stacked area (or line) instead."
- **Fix:** Stacked area chart or multi-line chart

### 13. Bar Chart for Continuous Distribution
- **Problem:** Equal-width bars with gaps misrepresent the distribution shape
- **Detection:** User asks about distribution/spread but requests a bar chart
- **Response:** "For distribution, a histogram (no gaps, binned) shows the shape better. Building histogram."
- **Fix:** Histogram with appropriate bin size

### 14. Multiple Pies for Comparison
- **Problem:** Angle comparison across separate pies is nearly impossible for humans
- **Detection:** User wants to compare composition across categories using multiple pie charts
- **Response:** "Comparing across pies is unreliable (angle perception). Using stacked bar for clear comparison."
- **Fix:** Stacked bar chart with categories on rows and segments as color

### 15. Donut Chart
- **Problem:** Same readability issues as pie, with worse space efficiency (center hole wastes area)
- **Detection:** User requests "donut chart"
- **Response:** "Donuts have the same limitations as pie charts with less space efficiency. Building as stacked bar (or pie if 2-3 slices). Override?"
- **Fix:** Stacked bar, or pie (if criteria met), or single-number KPI with ring indicator

***

## Quick Anti-Pattern Check Sequence

Before presenting any worksheet spec, run through:

1. Is this a 3D chart? → BLOCK
2. Is this a pie with >5 slices? → BLOCK
3. Are there dual y-axes without explicit user request + justification? → BLOCK
4. Do bars start at non-zero? → BLOCK (for bars; ok for lines)
5. Are bars sorted alphabetically when ranking/comparison is the question? → FIX (sort by value)
6. Are lines connecting non-ordered categories? → WARN
7. Are there >6 line series? → WARN
8. Is a gauge being used when a KPI tile would work? → WARN
9. Is a table being used when a pattern/trend question was asked? → NOTE
10. Is a signed measure (can be negative) on Size? → WARN (move to diverging Color; see #16)

If all pass, proceed with build.
