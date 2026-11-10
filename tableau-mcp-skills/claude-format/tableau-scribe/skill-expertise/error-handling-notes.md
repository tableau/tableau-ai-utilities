# Error Handling and Degradation Notes

Bottom-note pattern, MCP failure matrix, and graceful degradation priority.

### Bottom-Note Pattern

When MCP calls fail or data is unavailable, do NOT clutter the documentation body with error explanations. Instead, place a **bottom note** at the very end of the output:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NOTE: [Brief explanation of what was unavailable and why]
[What sections are affected]
[What the user can do to resolve, if applicable]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Examples:**

```
NOTE: View image could not be retrieved (the render timed
out). Visual layout analysis and Design Health Summary are
based on metadata architecture only. Try again later or
open the view in Tableau to confirm it renders.
```

```
NOTE: Sample data query timed out. "Typical range" values
are not included in metric definitions. Data owner can
provide these manually.
```

### When to use a bottom note vs. inline mention:
- **Bottom note:** Any MCP failure, missing data source, permission issue, or degradation that affects what sections contain
- **Inline (within the section):** Only when a specific metric/field definition can't be completed — mark it "(inferred)" or "confirm with data owner" inline, and add the systemic explanation to the bottom note

### MCP Failure Matrix

| Failure | Fallback | Bottom Note |
|---------|----------|-------------|
| 401 Unauthorized (do not retry) | Stop. Later calls will fail too. Tell the user the session expired and to reconnect | "Your Tableau session expired, so no documentation was produced. Reconnect and try again." |
| 403 on datasource in Auto-Doc (do not retry) | Image + view metadata only | "Datasource access restricted. Metric definitions inferred from visual analysis only." |
| 403 or 404 on the datasource in Metric Builder (do not retry) | Stop; ask the user to confirm access or pick another datasource. Document nothing from it | "You don't have access to this datasource (or it wasn't found), so no dictionary was produced." |
| 403 on the view or workbook (do not retry) | Stop; ask the user to confirm access or pick another item. Document nothing from that item | "You don't have access to this view/workbook, so no documentation was produced." |
| 404 Not Found (do not retry) | Search alternatives with `search-content` or a name filter; list real names and ask. Never pick a closest match | "View/workbook not found. May have been renamed or deleted." |
| Datasource returns zero fields (do not retry) | Stop the dictionary; for Auto-Doc continue with image and view metadata | "The datasource returned no fields, so no field-level definitions were produced." |
| Datasource not queryable (`isQueryable` false) | Skip sample enrichment | "Datasource can't be queried, so typical ranges are not included." |
| View renders blank | Metadata-only documentation | "View rendered blank (extract may need refresh). Documentation based on metadata only." |
| Timeout on data query | Skip sample enrichment | "Sample data unavailable. Typical ranges not included." |
| Formula, parameter, filter-default, or refresh data requested | Write "Not available via MCP; confirm with the owner" (Type/Inputs: "confirm with data owner") | "Formulas, parameter values, filter defaults, and refresh schedules aren't available through the Tableau MCP and are marked for confirmation." |
| Partial metadata | Use what's available, flag gaps | "Some fields lack descriptions. Definitions marked (inferred) require validation." |

### Graceful Degradation Priority

Always produce something useful. Priority order:

1. **Full run** — Image + metadata + sample data + all sections
2. **Image + metadata** — Skip sample data enrichment
3. **Metadata only** — No visual analysis
4. **Image only** — No field-level data
5. **Search results only** — Can't access content; help user find the right target

At each level, generate what you can and explain gaps in the bottom note. The bottom note must list every failed or skipped call and which sections it affects.
