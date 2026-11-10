# Injection Catalogs

Anomaly injection and data imperfection type catalogs, formats, and configuration used in Phases 4B and 4C.

## Phase 4B: Injection Types and Specification Format

**Supported injection types:**

| Injection Type | Description | Parameters |
|---|---|---|
| **Spike** | Sudden increase in a measure for a specific time window | field, magnitude (2x, 5x, etc.), start_date, duration |
| **Dip** | Sudden decrease in a measure | field, magnitude (0.5x, 0.2x), start_date, duration |
| **Outliers** | N extreme values scattered randomly | field, count, magnitude (how many σ above/below mean) |
| **Regime change** | Permanent shift in average at a point in time | field, shift_factor, change_date |
| **Event cluster** | Burst of activity on specific dates | date_field, event_dates[], volume_multiplier |
| **Flatline** | Zero/constant values for a period (system outage simulation) | field, constant_value, start_date, duration |

**Injection specification format (user provides):**

```
Inject:
- Spike: Sales × 3.0 during 2023-11-20 to 2023-11-27 (Black Friday)
- Outliers: 5 values in Profit at -4σ (scattered randomly)
- Dip: Quantity × 0.3 during 2023-01-01 to 2023-01-15 (supply shortage)
```

## Phase 4C: Imperfection Types and User Configuration

**Supported imperfection types:**

| Imperfection | Description | Default Rate | Applies To |
|---|---|---|---|
| **Inconsistent casing** | Mix of "New York", "new york", "NEW YORK", "new York" | 8% of string values | Categorical, Geographic |
| **Trailing/leading spaces** | " Sales " instead of "Sales" | 5% of string values | All string fields |
| **Typos** | Character transposition, omission, or substitution | 3% of string values | Names, Categories |
| **Near-duplicates** | Rows that are 90-95% identical (same person, slightly different spelling) | 2% of total rows | Full rows |
| **Format inconsistency** | Mixed date formats ("2023-01-15" vs "01/15/2023" vs "Jan 15, 2023") | 10% of date values | Date fields (string-formatted only) |
| **Unit inconsistency** | "$1,234.56" vs "1234.56" vs "$1234.56" | 5% of numeric values | Numeric fields (string-formatted only) |
| **Phantom categories** | Misspelled category values that create false cardinality ("Technolgy", "Techology") | 2-3 phantom values per categorical field | Categorical |
| **Encoding artifacts** | "Ã©" instead of "é", "â€"" instead of "—" | 1% of values with special chars | String fields |

**User configuration:**

```
Data Imperfection Mode: ON
Severity: [Light / Medium / Heavy]
- Light: 2-3% overall imperfection rate (subtle, realistic)
- Medium: 5-8% rate (clearly needs cleaning, good for demos)
- Heavy: 12-15% rate (stress-test cleaning logic)

Target fields: [all / specific fields]
Imperfection types: [all / specific types]
```
