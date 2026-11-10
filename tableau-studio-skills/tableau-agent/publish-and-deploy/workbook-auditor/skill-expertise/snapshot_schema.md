# Snapshot Schema — Workbook Auditor

This file defines the exact JSON structure that this skill writes and expects to read back. Other skills (e.g., publish-readiness, data-scribe) may consume these files to annotate "recently changed" items or detect drift.

***

## Mode A — Field/Calc Snapshot

Filename: `[datasource-name]_snapshot.json`

```json
{
  "schema_version": "1.0",
  "mode": "field_calc",
  "created_at": "2026-08-12T14:30:00Z",
  "workbook_name": "Sales Dashboard",
  "workbook_location": "C:\\Users\\<user>\\Documents\\Workbooks\\Sales Dashboard.twbx",
  "datasource_name": "Orders",
  "field_count": 47,
  "fields": [
    {
      "name": "Profit Ratio",
      "dataType": "REAL",
      "role": "measure",
      "is_calculated": true,
      "formula": "SUM([Profit]) / SUM([Sales])",
      "hidden": false
    },
    {
      "name": "Category",
      "dataType": "STRING",
      "role": "dimension",
      "is_calculated": false,
      "formula": null,
      "hidden": false
    }
  ]
}
```

### Field-level properties

| Property | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | Field name exactly as returned by `list-available-fields` |
| `dataType` | string | yes | One of: STRING, INTEGER, REAL, BOOLEAN, DATE, DATETIME |
| `role` | string | yes | One of: dimension, measure |
| `is_calculated` | boolean | yes | true if the field has a formula; false for native datasource fields |
| `formula` | string or null | yes | Full formula text if calculated; null otherwise. Stored as-is (no normalization). Normalization happens at diff time per Hard Constraint #4. |
| `hidden` | boolean or null | yes | Whether the field is hidden in the data pane. **Unconfirmed field** (see Hard Constraint #9 in SKILL.md) — use `null` if the source tool call doesn't return it, never guess. |

***

## Mode B — Workbook Snapshot

Filename: `[workbook-name]_workbook_snapshot.json`

```json
{
  "schema_version": "1.0",
  "mode": "workbook",
  "created_at": "2026-08-12T14:30:00Z",
  "workbook_name": "Sales Dashboard",
  "workbook_location": "C:\\Users\\<user>\\Documents\\Workbooks\\Sales Dashboard.twbx",
  "datasources": [
    {
      "name": "Orders",
      "connection_type": "hyper",
      "field_count": 47,
      "fields": [
        {
          "name": "Profit Ratio",
          "dataType": "REAL",
          "role": "measure",
          "is_calculated": true,
          "formula": "SUM([Profit]) / SUM([Sales])",
          "hidden": false
        }
      ]
    }
  ],
  "worksheets": [
    {
      "name": "Sales by Region",
      "datasource": "Orders"
    }
  ],
  "dashboards": [
    {
      "name": "Executive Summary",
      "member_sheets": ["Sales by Region", "Profit Trend", "Top Customers"]
    }
  ]
}
```

### Top-level properties

| Property | Type | Required | Description |
|---|---|---|---|
| `schema_version` | string | yes | Always "1.0" for now. Enables future-proofing if schema evolves. |
| `mode` | string | yes | "field_calc" or "workbook" |
| `created_at` | string (ISO 8601) | yes | Timestamp when snapshot was taken |
| `workbook_name` | string | yes | From `get-workbook-inventory` |
| `workbook_location` | string | yes | Full path from `get-workbook-inventory`'s `location` field |
| `datasources` | array | Mode B only | One entry per datasource in the workbook |
| `worksheets` | array | Mode B only | One entry per worksheet |
| `dashboards` | array | Mode B only | One entry per dashboard |

### Datasource entry

| Property | Type | Description |
|---|---|---|
| `name` | string | Datasource name |
| `connection_type` | string or null | "hyper" (extract), "live", or the connection class if detectable. **Unconfirmed field** (see Hard Constraint #9 in SKILL.md) — use `null` if `list-workbook-datasources` doesn't return it, never guess. |
| `field_count` | integer | Total fields in this datasource |
| `fields` | array | Same structure as Mode A fields |

### Worksheet entry

| Property | Type | Description |
|---|---|---|
| `name` | string | Worksheet name |
| `datasource` | string | Primary datasource name |

### Dashboard entry

| Property | Type | Description |
|---|---|---|
| `name` | string | Dashboard name |
| `member_sheets` | array of strings | Ordered list of worksheet names placed on this dashboard |

***

## Diff Logic Reference

When diffing current state against a loaded snapshot:

1. **Field matching:** by `name` within the same datasource. If name matches, compare `dataType`, `role`, `formula`, `hidden`.
2. **Rename detection:** a removed field + an added field with same `dataType`, `role`, and normalized formula (per Hard Constraint #4) = inferred rename.
3. **Worksheet matching:** by `name`. No shelf-content comparison unless rename detection is needed.
4. **Dashboard matching:** by `name`. Compare `member_sheets` arrays (order-sensitive).
5. **Datasource matching:** by `name`. A missing datasource in the current state = removal (high-signal).

***

## Cross-Skill Consumption

Other skills may read snapshot files for context:

- **publish-readiness:** could annotate "recently changed" calcs/fields in its report by checking whether the field appears as changed in the most recent snapshot diff.
- **data-scribe:** could flag fields whose formula changed since the last snapshot, prompting a documentation update.
- **calc-debugger:** could reference prior formula text when debugging a calc that "used to work."

To consume: parse the JSON, check `schema_version`, read the `fields` array. The schema is intentionally flat (no nesting beyond the field list) for easy parsing.
