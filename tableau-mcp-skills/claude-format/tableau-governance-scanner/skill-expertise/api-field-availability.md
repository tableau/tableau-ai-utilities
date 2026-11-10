# API Field Availability Reference

Which fields each Tableau MCP tool returns, plus the caveats that shape which checks are possible.

The MCP tools return different fields depending on the content type. Know what's available before designing checks:

### list-workbooks returns:
`id`, `name`, `description`, `webpageUrl`, `contentUrl`, `project` (id + name), `owner` (id only), `showTabs`, `defaultViewId`, `tags`

**Not confirmed in the list-workbooks response body:** `updatedAt`, `createdAt`, `size`, `sheetCount`, `favoritesTotal`. These ARE filterable server-side (see "Filterable fields" below), so use filters instead of workarounds.

### list-views returns:
`id`, `name`, `contentUrl`, `viewUrlName`, `createdAt`, `updatedAt`, `workbook` (id + name), `owner` (id + name), `project` (id + name), `tags`, `totalViewCount`

**This is the richest data source.** Views have timestamps AND usage counts.

**Critical note on totalViewCount:** This is a **cumulative lifetime counter**, NOT a windowed metric. A view created 3 years ago with 500 total views may have had zero views in the last 6 months. To approximate recency, combine totalViewCount with updatedAt: a view with high totalViewCount but updatedAt >180 days ago is likely legacy-popular but no longer actively used.

### list-datasources returns:
`id`, `name`, `updatedAt`, `isCertified`, `owner`, `description`, `hasExtracts`, `contentUrl`, `favoritesTotal`, `type`

**Note:** May return 401 if the user's token scope doesn't include datasource listing. If this happens, proceed with workbook + view data only.

### list-projects returns:
`id`, `name`, `parentProjectId`, `owner`, `description`, `contentPermissions`, `createdAt`, `updatedAt`

**Note:** May also 401. If so, infer project info from workbook/view metadata.

### get-workbook (individual call) returns:
Detail including the workbook's views and `upstreamDatasources` (confirmed). `size` and `sheetCount` are **unverified** here: check the first response before relying on them. **Use sparingly** — only call for workbooks already flagged by other checks. Cap at 10 per scan.

### search-content (limited use)
Filter supports only `contentTypes`, `ownerIds` and `modifiedTime`. It **cannot scope by project** and returns a **ranked top-N** (`limit` max 2000), not an exhaustive list. `orderBy` methods include `hitsTotal` and the windowed `hitsSmallSpanTotal` (last month), `hitsMediumSpanTotal` (3 months), `hitsLargeSpanTotal` (year). Use it only for spot checks (e.g. most-used content), never as the inventory. Fields such as `connectedWorkbooksCount`, `viewCountLastMonth` and `extractRefreshedAt` are **unverified**; do not build checks on them.

### Filterable fields (server-side, `filter: "field:operator:value"`)
Operators: `eq`, `gt`, `gte`, `lt`, `lte`, `in` (per field). Comma = AND. Dates are ISO 8601. `limit` max 1000, use `pageNumber`; read `totalAvailable`.

| Tool | Filterable fields useful for governance |
|------|-----------------------------------------|
| list-workbooks | `updatedAt`, `createdAt`, `size` (units unconfirmed), `sheetCount`, `favoritesTotal`, `hasExtracts`, `hasAlerts`, `projectName`, `ownerName`, `tags`, `name` |
| list-views | `hitsTotal` (lifetime views), `sheetType`, `updatedAt`, `createdAt`, `projectName`, `ownerName`, `workbookName`, `tags`, `name` |
| list-datasources | `isCertified`, `hasExtracts`, `updatedAt`, `ownerName`, `description`, `projectName`, `tags`, `name` |
| list-projects | `name`, `parentProjectId`, `topLevelProject`, `ownerName`, `createdAt`, `updatedAt` |

Examples: `updatedAt:lt:2026-08-01T00:00:00Z` (stale), `sheetCount:gt:15` (over-sheeted), `hitsTotal:lte:5` (low usage), `isCertified:eq:false`, `hasExtracts:eq:false`.
