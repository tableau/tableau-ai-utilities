# Tableau Workbook Inventory

List or count published workbooks available through a connected Tableau MCP site, with explicit scope and completeness reporting.

## When to use

- “List the Tableau workbooks I can access.”
- “Inventory all workbooks in the Finance project.”
- “Show a preview of 20 workbooks in Finance.”
- “How many workbooks does the connected site report?”

This skill inventories workbook metadata. It does not recommend dashboards by topic, audit governance, render views, query business data, or modify Tableau content.

## Requirements

A client that can load Agent Skills and a Tableau MCP connection exposing `list-workbooks`, with permission to read the desired scope. Tool names may have a client/server prefix. No native rendering, local scripts, persistent memory, companion skills, or client-specific tools are required.

## Output and limitations

A plain Markdown table normally includes workbook name, project, and workbook ID. Count requests return a tool-reported total and relevant caveats. Preview requests remain previews. Full inventories traverse the reported page range and disclose restrictions, inconsistencies, or incomplete retrieval.

Results depend on account permissions, server configuration, and the connected tool version. This is not an administrator-certified census of every workbook on a site. “My workbooks” may require clarification about ownership.

## Files

- [SKILL.md](SKILL.md): agent instructions and scope.
- [skill-expertise/list-workbooks.md](skill-expertise/list-workbooks.md): filters, fixed page boundaries, response interpretation, and source contracts.

## Portability

This skill provides client-independent instructions for listing and counting published Tableau workbooks using the connected Tableau MCP server. It requires access to the `list-workbooks` tool. Follow your client's supported method for loading skills.
