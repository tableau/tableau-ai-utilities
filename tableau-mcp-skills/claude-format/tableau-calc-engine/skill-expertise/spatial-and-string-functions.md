# Spatial and String Function Reference

Reference examples for spatial and mapping functions and for string functions, including SQL equivalences.

### Core Spatial Functions

```tableau
// Create point from lat/long
MAKEPOINT([Latitude], [Longitude])

// Line between two points (flight paths, routes)
MAKELINE(MAKEPOINT([Origin Lat], [Origin Long]), MAKEPOINT([Dest Lat], [Dest Long]))

// Distance (km or mi)
DISTANCE(MAKEPOINT([Store Lat], [Store Long]), MAKEPOINT([Customer Lat], [Customer Long]), 'km')

// Buffer — circle around a point (requires 2024.1+)
BUFFER(MAKEPOINT([Lat], [Long]), 5, 'km')

// Area of polygon
AREA([Geometry], 'km')

// Length of a line
LENGTH(MAKELINE(MAKEPOINT([A_Lat],[A_Long]), MAKEPOINT([B_Lat],[B_Long])), 'km')
```

### Practical Spatial Patterns

```tableau
// Delivery feasibility (within 30-mile radius)
DISTANCE(MAKEPOINT([Warehouse Lat],[Warehouse Long]), MAKEPOINT([Delivery Lat],[Delivery Long]), 'mi') <= 30

// Drive-time proxy (straight-line × 1.4 correction)
DISTANCE(MAKEPOINT([A_Lat],[A_Long]), MAKEPOINT([B_Lat],[B_Long]), 'mi') * 1.4

// Hex bin for density (reduces overplotting)
HEXBINX([Longitude] * 3, [Latitude] * 3)  // Scale factor 2-5 depending on zoom
HEXBINY([Longitude] * 3, [Latitude] * 3)
```

### Core String Functions

```tableau
// Extract with regex (SQL: REGEXP_SUBSTR)
REGEXP_EXTRACT([Email], '(.+)@')  // Returns username portion

// Replace with regex
REGEXP_REPLACE([Phone], '[^0-9]', '')  // Strip non-numeric chars

// Check regex match (returns boolean)
REGEXP_MATCH([Field], '^\d{5}$')  // Is it a 5-digit zip?

// Split on delimiter (token numbers are 1-based; negative counts from the end)
SPLIT([Full Name], ' ', 1)  // First token (first name)
SPLIT([Full Name], ' ', -1) // Last name (negative = from end)

// Substring (MID equivalent)
MID([String], start, length)
LEFT([String], n)
RIGHT([String], n)

// Trim whitespace
TRIM([Field])           // Both sides
LTRIM([Field])          // Left only
RTRIM([Field])          // Right only

// Find position (SQL: CHARINDEX / POSITION)
FIND([String], 'search')        // Returns position (1-based) or 0
FIND([String], 'search', start) // Start searching from position

// Contains (simpler than FIND for boolean)
CONTAINS([Field], 'text')  // Returns TRUE/FALSE

// Replace (non-regex)
REPLACE([Field], 'old', 'new')

// Case conversion
UPPER([Field])
LOWER([Field])
PROPER([Field])  // Title Case
```

### SQL → Tableau String Equivalences

| SQL | Tableau | Notes |
|-----|---------|-------|
| `CONCAT(a, b)` | `[a] + [b]` | Use `STR()` to convert non-strings first |
| `SUBSTRING(s, start, len)` | `MID([s], start, len)` | Tableau is 1-based |
| `CHARINDEX('x', s)` | `FIND([s], 'x')` | Returns 0 (not NULL) if not found |
| `LEN(s)` | `LEN([s])` | Same |
| `REGEXP_SUBSTR(s, pat)` | `REGEXP_EXTRACT([s], pat)` | Use capture group `()` in pattern |
| `ISNULL(s, default)` | `IFNULL([s], default)` or `ZN([s])` | ZN only for numeric (returns 0) |
| `CAST(x AS VARCHAR)` | `STR([x])` | Also: `STR(DATEPART(...))` for date parts |
