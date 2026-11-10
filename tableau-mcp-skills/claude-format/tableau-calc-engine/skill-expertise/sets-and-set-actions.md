# Sets and Set Actions

Reference patterns for computed sets, combined sets, set actions and set-based calculations.

### Computed Sets

```tableau
// Top N customers by sales (computed set)
// Create: Right-click [Customer ID] → Create → Set
// Condition tab: By field: SUM([Sales]) >= [threshold]
// OR Top tab: Top N by SUM([Sales])

// Use in calc: IN/OUT test
IF [Top Customers Set] THEN "Top" ELSE "Other" END
// Name: "Cust Tier"
```

### Combined Sets

```tableau
// Customers in BOTH Set A and Set B (intersection)
// Create combined set: Set A ∩ Set B (shared members)
// Use for: customers who are high-value AND recently active

// Customers in Set A but NOT Set B (difference)
// Use for: high-value customers who have NOT purchased recently (churn risk)
```

### Set Actions (Requires Tableau 2018.3+)

Set actions let users click marks to add/remove members from a set — enabling advanced interactivity:

```
User clicks bars in "Category" chart
→ Set action adds clicked categories to [Selected Categories Set]
→ Other charts filter/color based on set membership
→ LOD calcs can reference the set: { FIXED : SUM(IF [Selected Categories Set] THEN [Sales] END) }
```

**Set action vs. filter action:**
- Filter action: removes non-selected marks entirely
- Set action: keeps all marks visible but distinguishes IN vs. OUT — better for comparison

### Set-Based Calculations

```tableau
// % of total from selected set members
SUM(IF [My Set] THEN [Sales] END) / SUM([Sales])
// Name: "% from Set"

// Aggregate only for set members
{ FIXED : SUM(IF [My Set] THEN [Sales] END) }
// Use for KPI BANs that respond to set selections

// Count of set members
{ FIXED : COUNTD(IF [My Set] THEN [Customer ID] END) }
// Name: "Set Count"
```
