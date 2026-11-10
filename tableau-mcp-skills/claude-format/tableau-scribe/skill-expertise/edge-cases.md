# Edge Cases

How to handle unusual requests and metadata mismatches.

**"Document this dashboard" + no view identifiable:**
→ Search and present options.

**"Document this datasource" (uses "document" but targets datasource):**
→ Route to Metric Builder. "Datasource" keyword takes priority.

**Datasource has 100+ fields:**
→ In Brief: measures + calcs only, one-line each. In Detailed: group by category, full primary measures, abbreviated secondary.

**User asks for both modes at once:**
→ Run both. Single document: Part 1 = Auto-Doc, Part 2 = Metric Dictionary.

**User already has documentation and wants it updated:**
→ Ask for existing doc. Compare against live state. Produce gap report or updated version.

**User wants to switch depth after receiving output:**
→ "Want the brief/detailed version too?" Detailed to Brief reuses what you already fetched. Brief to Detailed needs data a Brief run skips (view data, sample queries, design health inputs), so fetch it now, following Safe Querying, before writing the Detailed version.

**Stale metadata detection:**
→ When datasource metadata references fields not visible in the rendered view (or vice versa), this may indicate the extract and metadata are from different versions (e.g., fields added/removed between refreshes). Flag in a bottom note: "Some metadata fields do not appear in the current render — the datasource schema may have changed since the last extract refresh. Verify field availability with the data owner." Do not silently omit mismatched fields; document them with a "(not currently visible)" marker.
