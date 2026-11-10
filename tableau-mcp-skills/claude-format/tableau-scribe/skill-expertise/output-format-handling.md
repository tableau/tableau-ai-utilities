# Output Format Handling

How to produce documentation as .docx, on-screen text, .md, or .xlsx.

### .docx (Word document)

Generate a formatted Word document using the docx skill's approach:
- Professional formatting with proper heading hierarchy
- Table of contents (Detailed mode only)
- Tables for structured information (filters, metrics in Metric Builder)
- Clean typography: Calibri/Arial, appropriate sizing
- Headers, page numbers, and generation timestamp in footer

### On screen (text in conversation)

Present documentation inline using the matching template in `auto-doc-structures.md` or `metric-dictionary-structures.md`. Use markdown formatting for readability.

### .md (Markdown file)

Generate a standalone Markdown file with:
- Proper heading hierarchy (# ## ###)
- Tables in Markdown format
- Saved to outputs folder and linked for download

### .xlsx (Excel) — Metric Builder only, offer when appropriate

If the user is in Metric Builder mode and .xlsx seems more useful (large field count, they mention "spreadsheet"), offer it:
- One row per field
- Columns: Field Name, Category, Definition, Business Context, Directionality, Aggregation, Data Type, Typical Range, Caveats
- Formatted as a proper table with filters
