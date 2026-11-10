# Dynamic Zone Visibility and Parameter Patterns

Reference patterns for dynamic zone visibility calcs and for parameter-driven calculations.

### How It Works

1. Create a calc or parameter that evaluates to a Boolean
2. Dashboard → select container/sheet → Layout pane → "Control visibility using value"
3. Zone shows when TRUE, hides when FALSE

### Patterns

```tableau
// Toggle via parameter
// Requires: Parameter [Show Detail] = Boolean
[Show Detail]

// Show zone only after user clicks (parameter action sets value)
[Selected Customer] != ""

// Threshold-triggered alert panel
// Requires Tableau 2022.3+
{ FIXED : SUM([Sales]) } < [Target Parameter]

// Role-based visibility
// Requires Tableau 2022.3+
ISMEMBEROF("Executives")

// Date-range-dependent: TRUE (show YoY) only when the selected range is 12+ months
// Requires Tableau 2022.3+ and two date parameters
DATEDIFF('month', [Start Date Parameter], [End Date Parameter] + 1) >= 12
```

### Dynamic Zone + Parameter Actions (Interactive Pattern)

```
User clicks "Show Detail" button (sheet with parameter action)
→ Parameter [Show Detail] = TRUE → Detail zone appears
User clicks "Hide" button → Parameter = FALSE → Zone disappears
```

This replaces the old floating-sheet swap pattern.

### Dynamic Measure Swap

```tableau
CASE [Select Measure]
    WHEN "Sales" THEN SUM([Sales])
    WHEN "Profit" THEN SUM([Profit])
    WHEN "Quantity" THEN SUM([Quantity])
END
// Name: "Selected Metric"
```

### Dynamic Dimension Swap

```tableau
CASE [Group By]
    WHEN "Region" THEN [Region]
    WHEN "Category" THEN [Category]
    WHEN "Segment" THEN [Segment]
END
// Name: "Selected Dim"
```

### Dynamic TOP N

```tableau
// Parameter: [Top N] — Integer, range 3-20
RANK(SUM([Sales])) <= [Top N]
// Place on Filters → TRUE. Compute Using: the ranked dimension.
```

### Parameter Actions (Click-to-Set, requires 2019.2+)

```
User clicks bar → Parameter action sets [Selected Category] = "Technology"
→ Other charts filter: [Category] = [Selected Category]
→ KPI calcs reference: { FIXED : SUM(IF [Category] = [Selected Category] THEN [Sales] END) }
```

Preferred over filter actions when you need the selected value in calculations.
