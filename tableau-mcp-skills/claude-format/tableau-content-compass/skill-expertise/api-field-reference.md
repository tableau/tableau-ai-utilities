# API Field Availability Reference

Fields returned by each Tableau tool used in the search and what each tool is best for.

### list-projects returns:
`id`, `name`, `description`, `parentProjectId`, `owner` (id), `contentPermissions`, `createdAt`, `updatedAt`. Verify the exact response shape on the first call.
 
**Best for:** Project discovery. Supports wildcard filters on `name` (e.g., `name:eq:Finance*`), filtering by `ownerName`, `parentProjectId`, and `topLevelProject:eq:true`. Descriptions are especially valuable for identifying project purpose. The owner is an id only; show the owner name only if you have one (for example from `search-content` `ownerName`), and resolve the parent name from another project's `id`, or show "not shown".
 
### search-content returns:
`name`, `description`, `type` (view/workbook/datasource/project/etc.), `projectName`/`containerName`, `ownerName`, `tags`, usage (`hitsTotal`), `isCertified`, `hasExtracts`, `updatedAt`, `createdAt`
 
**Best for:** Broad term matching across all content types including projects. Supports `orderBy` (`hitsTotal` and the hitsSmall/Medium/LargeSpanTotal methods) and `limit` up to 2000. Filter takes only `contentTypes`, `ownerIds`, `modifiedTime`. Field names in results are unverified: check what comes back. When used with `contentTypes: ['project']`, returns projects whose names or descriptions match search terms. Returns `containerName` as the parent project name.
 
### list-views returns:
`id`, `name`, `contentUrl`, `viewUrlName`, `createdAt`, `updatedAt`, `workbook` (id + name), `owner` (id + name), `project` (id + name), `tags`, usage (`hitsTotal` if returned)
 
**Best for:** Project-scoped discovery. Has timestamps and usage counts. Server-side filter fields include `projectName`, `name`, `title`, `tags`, `workbookName`, `workbookDescription`, `fields`, `hitsTotal`, `sheetType`, `updatedAt`.
 
### list-datasources returns:
`id`, `name`, `updatedAt`, `isCertified`, `owner`, `description`, `hasExtracts`, `contentUrl`, `favoritesTotal`, `type`
 
**Note:** May return 403 or 401 if the token scope is limited. If so, infer datasource info from `upstreamDatasources` in `get-workbook`. Server-side filters: `projectName`, `name`, `description`, `tags`, `isCertified`, `hasExtracts`, `updatedAt`.
 
### get-datasource-metadata returns:
Full field list with `name`, `dataType`, `description`, `dataCategory`, `role` (dimension/measure).
 
**Best for:** Deep matching — confirms whether a datasource can actually answer the question based on available fields.
 
### get-view returns:
View detail including workbook info, project, owner, tags, usage, and a **`url`** if returned (direct link to the view, e.g., `https://[pod].online.tableau.com/#/site/[site]/views/[workbook]/[view]`). Do not assume it returns upstream datasources; use `get-workbook` for those.
 
**Best for:** Enrichment after initial matches. Provides the link for output when a `url` is returned.

### get-workbook returns:
The workbook's views and `upstreamDatasources` (with queryability). 

**Best for:** Companion views and the datasources behind a workbook.
 
### list-all-pulse-metric-definitions returns:
Metric definition names, descriptions, datasource references, measure fields, time dimensions, allowed dimensions.
 
**Best for:** Finding pre-defined metrics that track what the user is asking about.
