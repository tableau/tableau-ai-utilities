# Report Template — Workbook Auditor

This file locks the output format for both Mode A and Mode B digests. Follow this structure exactly; do not improvise headers, bullet phrasing, or ordering.

***

## Mode A — Calc/Field Change Digest

### Header

```
## Field & Calc Changes: [Datasource Name]
Compared against snapshot from [snapshot date/time if available, otherwise "prior baseline"].
```

### Body (grouped by change type, in this order)

**Inferred Renames** (if any):
```
- [Inferred rename: "Old Name" → "New Name" — same formula/type, name changed]
```

**New Fields** (if any):
```
- New: "[Field Name]" ([dataType], [role]) — [calculated/native]
  - Formula (if calc): [formula text, first 120 chars; full if shorter]
```

**Removed Fields** (if any):
```
- Removed: "[Field Name]" ([dataType], [role]) — [calculated/native]
  - Prior formula (if calc): [formula text from snapshot]
```

**Formula Changes** (if any):
```
- Formula edit: "[Field Name]"
  - Was: [prior formula, first 120 chars]
  - Now: [current formula, first 120 chars]
  - (Textual diff only — behavioral equivalence not confirmed)
```

**Type/Role Changes** (if any):
```
- Type change: "[Field Name]" — [prior dataType/role] → [current dataType/role]
```

### Footer

```
[N] total changes ([breakdown by type]).
```

### Zero-Change Output

```
No field or calc changes detected since the last snapshot.
```

***

## Mode B — Workbook Change Digest

### Header

```
## Workbook Change Digest: [Workbook Name]
Compared against snapshot from [snapshot date/time if available, otherwise "prior baseline"].
```

### Summary Line (always present before detail)

```
Summary: [N] datasource(s) changed, [N] worksheet(s) changed, [N] dashboard(s) changed, [N] field/calc changes across all datasources.
```

### Body (grouped by dimension, in this severity order)

**Datasources** (highest signal):
```
- Datasource removed: "[Name]" — [connection type if known]. This may indicate an unintentional disconnect.
- Datasource added: "[Name]" — [connection type if known].
```

**Dashboards**:
```
- Dashboard added: "[Name]"
- Dashboard removed: "[Name]"
- Dashboard membership changed: "[Name]" — [sheets added/removed list]
```

**Worksheets**:
```
- Worksheet added: "[Name]"
- Worksheet removed: "[Name]"
- [Inferred rename: "Old Name" → "New Name" — same shelf contents, name changed]
```

**Fields & Calcs** (per datasource; see Formatting Rules below for the 50-99 / 100+ field-count bands):
```
[Datasource: "Name"] — [N] changes:
```
Then use the same bullet format as Mode A (Inferred Renames, New, Removed, Formula Changes, Type/Role Changes).

### Footer

```
[N] total changes across [N] dimensions.
```

### Zero-Change Output

```
No changes detected since the last snapshot.
```

***

## Formatting Rules

- Always bulleted list (never a table for the digest itself).
- Group headers in **bold**, not markdown heading level (avoid colliding with the top-level digest header).
- Omit any group that has zero items (don't render "**New Fields**: (none)").
- Formula text longer than 120 characters: show first 120 + "..." in the bullet, offer full formula on request.
- For 50-99 fields in a single datasource in Mode B: sub-group by change type with a datasource sub-header.
- For 100+ fields in a single datasource in Mode B: same sub-grouping, plus a one-line count-by-type summary before the detail bullets (e.g., "Orders: 12 new, 3 removed, 4 formula changes").
- For 5+ datasources in Mode B: present summary counts first, then expand only datasources with changes.
