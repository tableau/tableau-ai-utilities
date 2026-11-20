# Workbook listing reference

Use with `tableau-workbook-inventory`. These examples match the Tableau MCP source at commit `15c18397c9f8317876e8e938abb567214419945f`. Confirm the connected tool's contract; older deployments may differ.

## Parameters and scope

`list-workbooks` accepts optional `filter`, `pageNumber` (positive integer, default 1), and `limit` (positive integer, at most 1000).

Examples, with project names supplied by the user:

```json
{"pageNumber": 1}
```

```json
{"filter": "projectName:eq:Finance", "pageNumber": 1}
```

```json
{"filter": "projectName:eq:Finance", "limit": 1}
```

The last example requests a count with minimal row output. Do not paste the example project into an unrelated request. Use the tool's documented filter encoding for literal values; if a value cannot be represented unambiguously, explain that rather than changing the scope. Do not invent `projectId` or a `contains` operator. Parent-project matching does not include descendants automatically.

## Fixed page boundaries: limit is a trim, not a page size

The checked implementation requests 1000 underlying records per page. Page 2 begins at offset 1000 regardless of `limit`. A call with `limit: 20` followed by page 2 skips the remainder of page 1.

- **Full inventory:** omit `limit`; request pages 1 through `ceil(totalAvailable / 1000)`, in order. This range determines the last page, not the post-filter row count. Keep the filter unchanged.
- **Preview N:** use full pages until the last needed page, then `limit` equal to the remaining requested number. For a preview of 1020, request page 1 without a trim, then page 2 with `limit: 20`. A trim happens before configuration filtering, so it can yield fewer than requested despite more allowed rows in that same page. When a preview comes back short, refetch that page untrimmed once and select locally; if still short, continue within the known page range until N unique rows or the last page. If continuing a previous trimmed preview, refetch that page untrimmed before advancing and deduplicate IDs; never treat the trim as the page size.
- **Count:** `limit: 1` returns at most one row while leaving `totalAvailable` independent of this caller trim. Do not count the one-row array as the total. If a count call is explicitly configuration-filtered and omits the total, retry page 1 once without `limit`. If no total is returned, report that the count is unavailable; do not infer zero or scan the entire site solely to recover a count.

Responses normally contain `{ data, totalAvailable }`. `data` holds workbook objects. Read structured results when available; otherwise interpret the actual returned content without assuming success when `isError` is true.

## Restrictions and inconsistencies

- `mcp.resultInfo.truncated: true` with `truncationReason: "admin-cap"` means the server restricts the reachable result range and caps `totalAvailable`. Report a restricted inventory/count; do not claim the cap is the real site total or request pages beyond it. You may offer a narrower user-selected scope, but do not change filters silently or claim that separate filtered queries form a complete inventory.
- Server configuration can filter rows after paging, so fewer rows than `totalAvailable` does not establish that more pages exist. Conversely, a short nonempty page does not prove the end: use the reported page range. An explicitly configuration-filtered empty response omits pagination metadata. If an earlier response established the page range, record this restriction and continue with the next page in that range; it does not mean later pages are empty. If the range is unknown, stop and report it as unresolved. A generic unexpected empty response before the known end remains a partial-result stopping condition.
- If totals change during traversal or IDs recur across pages, stop, preserve unique rows, identify the affected page, and label the inventory partial/inconsistent. The API does not provide a snapshot guarantee here. Do not claim exact coverage merely because counts happen to match.
- `totalAvailable` is computed before server-configuration row filtering. Without an admin cap, it is an upper bound on rows visible after that filtering; it is not a verified visible-row count. With an admin cap, it describes the capped pre-filter range and is not an upper bound on all workbooks on the site. Always label count mode as a tool-reported total, disclose these restrictions when known, and do not rule out configuration filtering merely because no warning appeared.

## Fields

Use `id`, `name`, and returned `project.name` / `project.id` for the core table. `owner` and `webpageUrl` may be absent. Owner fields can vary with metadata enrichment; present only actual values. Do not assume that filtering by `updatedAt` means the response includes that timestamp. `contentUrl` is an identifier/path value, not by itself a clickable URL.

Source: [list-workbooks](https://github.com/tableau/tableau-mcp/blob/15c18397c9f8317876e8e938abb567214419945f/src/tools/web/workbooks/listWorkbooks.ts), [pagination](https://github.com/tableau/tableau-mcp/blob/15c18397c9f8317876e8e938abb567214419945f/src/utils/paginate.ts), [workbook schema](https://github.com/tableau/tableau-mcp/blob/15c18397c9f8317876e8e938abb567214419945f/src/sdks/tableau/types/workbook.ts).
