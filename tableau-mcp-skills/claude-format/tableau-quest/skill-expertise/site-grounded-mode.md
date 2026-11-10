# Site-Grounded Mode

Procedure and scenario-generation guidance for grounding Field Quest scenarios in the player's live Tableau site via MCP tools.

**Fallback (check first):** If no Tableau tools are available, a call errors, or results are empty, say once, out of game: "I can't read your site, so I'll use a realistic stand-in. Paste a real situation (50+ words) any time and I'll build the quest around it." Then proceed with fictional grounding and stay in character.

Call the connected Tableau MCP tools by name (`list-workbooks`, `get-workbook`, and so on), whatever server prefix they carry.

1. **Recent workbooks:** `list-workbooks` with `filter: updatedAt:gte:<30 days ago, ISO 8601>`, `limit: 10`. Extract workbook name, project name, updatedAt, and each workbook's id (the sheet count and id fields are unverified, so check the first response and skip any that are absent). Focus on the 3-5 most recent. If the list is empty, retry once without the date filter and use the staleness itself as a scenario hook.
2. **Workbook detail:** `get-workbook {workbookId}` for the views and `upstreamDatasources` (each carries a datasource LUID and whether it is queryable).
3. **Datasource fields:** `get-datasource-metadata {datasourceLuid}` (add `workbookLuid`, the workbook id from step 1, if the datasource is embedded). Extract field names, data types, field count. Note high-cardinality dimensions and complex-looking calculated fields.
4. **Popular and stale content:** `search-content` with `filter: {contentTypes: ["workbook","datasource","view"]}`, `orderBy: [{method: "hitsTotal", sortDirection: "DESC"}]`, `limit: 20`. Treat it as a ranked sample, not a complete inventory. Compare with step 1 for staleness patterns.
5. **Uncertified sources:** `list-datasources` with `filter: isCertified:eq:false`, `limit: 10`.

If a later step fails after earlier steps returned data, keep the real names and structure gathered so far, invent the rest, and say which parts are stand-in in the one-sentence notice. If step 1 fails or returns nothing even after the retry, fall back to fictional grounding for the whole scenario.

Use only what these calls return. Row counts, refresh schedules, users, groups and permissions are not available, so invent them as scenario details and never present them as facts about the player's site.

**Response parsing:** Extract only narrative-relevant details (names, counts, dates, project structure). Discard IDs, URLs and technical metadata once they have been used to make the next call. Never quote raw API responses. In dialogue, turn technical field names into natural language (field `Opp_Close_Dt` becomes "the opportunity close date field"); realistic business names for fields and datasources are fine.

**People:** Never use real owner names from the site. Invent fictional NPC names, and use ownership patterns (one owner for most content, orphaned projects) only to shape their roles and motives.

When the site is accessible:
1. Use real workbook and datasource names, field counts and content age
2. Reference real project structure and ownership patterns, with fictional people
3. Ground stakeholder roles in inferred org structure (content ownership, project hierarchy)
4. Introduce complications based on observed patterns (stale content, uncertified sources, high field counts, naming inconsistencies)
