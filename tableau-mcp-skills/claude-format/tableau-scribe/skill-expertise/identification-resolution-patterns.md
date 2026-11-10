# Identification and Resolution Patterns

Patterns for parsing Tableau URLs and resolving views, workbooks, and datasources.

### Parsing Tableau URLs

Tableau URLs vary by environment. Common patterns:

- Cloud: `https://[pod].online.tableau.com/#/site/[site]/views/[workbook]/[view]`
- Server: `https://[server]/t/[site]/views/[workbook]/[view]`
- Workbook page: `.../#/site/[site]/workbooks/[numericId]`

**The numeric ID in URLs is NOT the LUID needed for API calls.** Always resolve by name or URL slug: `list-views` with `viewUrlname:eq:<view>` or `list-workbooks` with `contentUrl:eq:<workbook>`, with a `limit`.

### When Multiple Views Exist in a Workbook

- Ask which view to document, or offer to document the primary (first) view and wait for the user to confirm
- Offer: "This workbook has [N] views: [list names]. Want me to document all of them, or a specific one?"
- If all: produce a single document with each view as a chapter/section

### When Datasource Has No Descriptions

- Use field names and types to infer purpose
- Use sample data to understand values
- Be explicit about inferences: mark with "(inferred)"
- Flag in bottom note: "This datasource has no field descriptions configured."
