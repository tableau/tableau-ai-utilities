# Calibration Notes

Scope limits, compound-finding consolidation example, and large-site optimization steps for the scanner.

### What This Skill Does NOT Do

- **Data quality profiling** — Doesn't query field values. That's Data Quality Sentinel.
- **Visual design evaluation** — Doesn't render views. That's VizCritique Pro.
- **Permission auditing** — Not exposed by this MCP.
- **Changing anything** — Read-only. Never move, publish, delete, certify, or retag content.
- **Extract refresh schedules** — Not exposed. Uses `updatedAt` as proxy.
- **Performance profiling** — No render times. Sheet count and size are proxies only.

### Compound Findings

When the same content triggers multiple checks, consolidate into a single compound finding with escalated severity. Example:

```
[CRITICAL] "Sales_Data_v2_COPY" — Uncertified + stale + no description + naming violation
  14 observed downstream WBs (sampled) on undocumented, stale, duplicate-named data | Fix: Audit vs. original, certify or deprecate
```

### Large Site Optimization

For sites with `totalAvailable` > 2000 workbooks:
1. Pass scope filters at the API level; paginate with `limit:1000` and `pageNumber`
2. Focus get-workbook enrichment on top 10 flagged items only
3. Report systemic findings as aggregates
4. Offer project-scoped deep-dives after the initial overview
