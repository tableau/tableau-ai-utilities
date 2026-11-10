# Output Format Specifications

Per-format delivery specs and templates (Control Tower HTML, xlsx, docx, md, JSON) for the validated findings.

### For Control Tower (HTML artifact):

Build with `mcp__cowork__create_artifact`. This is a **live dashboard** the user can re-open anytime.

**Layout (single-page, no scrolling for summary):**

1. **Hero section** — Letter grade (large, color-coded), score, one-liner verdict, scan date
2. **Domain health strip** — 7 small gauges or colored badges (A-F) in a horizontal row, one per domain
3. **Severity breakdown** — Donut or bar showing Critical/High/Medium/Low counts
4. **Quick Wins panel** — Top 5 quick wins with projected score improvement
5. **Findings table** (below fold) — Filterable by severity and domain. Columns: Severity | Name | Issue | Owner | Domain. Sortable. Color-coded severity badges.
6. **Long-Term Goals panel** — 3 strategic recommendations with effort estimates

**Design principles:**
- Light background, clean typography. Professional, not flashy.
- Severity colors: Critical = #DC2626 (red), High = #EA580C (orange), Medium = #CA8A04 (amber), Low = #6B7280 (gray)
- Grade colors: A = #16A34A (green), B = #2563EB (blue), C = #CA8A04 (amber), D = #EA580C (orange), F = #DC2626 (red)
- All charts as inline SVG — no external dependencies
- Store filter/sort state in localStorage so it persists across reloads
- Include a "Last scanned" timestamp in the header

**Reference HTML skeleton (adapt to actual scan data):**

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Governance Control Tower</title>
<style>
:root { color-scheme: light; }
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #FAFAFA; color: #1a1a1a; padding: 24px; line-height: 1.5; }
.hero { display: flex; align-items: center; gap: 24px; margin-bottom: 24px; }
.grade-badge { width: 80px; height: 80px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 32px; font-weight: 700; color: white; }
.grade-A { background: #16A34A; } .grade-B { background: #2563EB; }
.grade-C { background: #CA8A04; } .grade-D { background: #EA580C; } .grade-F { background: #DC2626; }
.hero-text h1 { font-size: 20px; font-weight: 600; }
.hero-text .score { font-size: 14px; color: #6B7280; }
.hero-text .verdict { font-size: 14px; margin-top: 4px; }
.domain-strip { display: flex; gap: 8px; margin-bottom: 24px; flex-wrap: wrap; }
.domain-chip { padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; color: white; }
.severity-bar { display: flex; height: 8px; border-radius: 4px; overflow: hidden; margin-bottom: 24px; }
.sev-critical { background: #DC2626; } .sev-high { background: #EA580C; }
.sev-medium { background: #CA8A04; } .sev-low { background: #6B7280; }
.panel { background: white; border: 1px solid #E5E7EB; border-radius: 8px; padding: 16px; margin-bottom: 16px; }
.panel h2 { font-size: 14px; font-weight: 600; margin-bottom: 8px; }
.panel li { font-size: 13px; margin-bottom: 6px; list-style: none; padding-left: 12px; position: relative; }
.panel li::before { content: "→"; position: absolute; left: 0; color: #6B7280; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th { text-align: left; padding: 8px; border-bottom: 2px solid #E5E7EB; font-weight: 600; }
td { padding: 8px; border-bottom: 1px solid #F3F4F6; }
.badge { padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; color: white; }
.badge-critical { background: #DC2626; } .badge-high { background: #EA580C; }
.badge-medium { background: #CA8A04; } .badge-low { background: #6B7280; }
.filters { display: flex; gap: 8px; margin-bottom: 12px; }
.filters select { padding: 4px 8px; border: 1px solid #D1D5DB; border-radius: 4px; font-size: 12px; }
.meta { font-size: 11px; color: #9CA3AF; margin-top: 16px; }
</style>
</head>
<body>
<!-- Hero -->
<div class="hero">
  <div class="grade-badge grade-{GRADE_CLASS}">{GRADE}</div>
  <div class="hero-text">
    <h1>{SCOPE_NAME} — Governance Scan</h1>
    <div class="score">{SCORE}/100 {DELTA_IF_ANY}</div>
    <div class="verdict">{VERDICT}</div>
  </div>
</div>

<!-- Domain Strip -->
<div class="domain-strip">
  <!-- Repeat for each domain: -->
  <div class="domain-chip grade-{DOMAIN_GRADE_CLASS}">{DOMAIN_NAME}: {DOMAIN_GRADE}</div>
</div>

<!-- Severity Bar -->
<div class="severity-bar">
  <div class="sev-critical" style="width: {CRIT_PCT}%"></div>
  <div class="sev-high" style="width: {HIGH_PCT}%"></div>
  <div class="sev-medium" style="width: {MED_PCT}%"></div>
  <div class="sev-low" style="width: {LOW_PCT}%"></div>
</div>

<!-- Quick Wins -->
<div class="panel">
  <h2>Quick Wins (raise score to ~{PROJECTED})</h2>
  <ul>
    <li>{ACTION_1} — {EFFORT_1}</li>
    <li>{ACTION_2} — {EFFORT_2}</li>
    <li>{ACTION_3} — {EFFORT_3}</li>
  </ul>
</div>

<!-- Findings Table -->
<div class="panel">
  <h2>Findings ({TOTAL_COUNT})</h2>
  <div class="filters">
    <select id="sev-filter"><option value="">All Severities</option><option>Critical</option><option>High</option><option>Medium</option><option>Low</option></select>
    <select id="domain-filter"><option value="">All Domains</option><option>Staleness</option><option>Usage</option><option>Certification</option><option>Naming</option><option>Structure</option><option>Performance</option><option>Metadata</option></select>
  </div>
  <table>
    <thead><tr><th>Sev</th><th>Name</th><th>Issue</th><th>Owner</th><th>Domain</th></tr></thead>
    <tbody id="findings-body">
      <!-- JS populates from data array -->
    </tbody>
  </table>
</div>

<!-- Long-Term Goals -->
<div class="panel">
  <h2>Long-Term Goals</h2>
  <ul>
    <li>{GOAL_1} — {EFFORT_1}</li>
    <li>{GOAL_2} — {EFFORT_2}</li>
    <li>{GOAL_3} — {EFFORT_3}</li>
  </ul>
</div>

<div class="meta">Last scanned: {SCAN_DATE} | Preset: {PRESET} | {WB_COUNT} workbooks, {VIEW_COUNT} views, {DS_COUNT} datasources</div>

<script>
// Scan data — populated at build time
const findings = [/* {severity, name, issue, owner, domain} */];

function render(data) {
  const tbody = document.getElementById('findings-body');
  tbody.innerHTML = data.map(f => `<tr>
    <td><span class="badge badge-${f.severity.toLowerCase()}">${f.severity}</span></td>
    <td>${f.name}</td><td>${f.issue}</td><td>${f.owner}</td><td>${f.domain}</td>
  </tr>`).join('');
}

function applyFilters() {
  const sev = document.getElementById('sev-filter').value.toLowerCase();
  const dom = document.getElementById('domain-filter').value;
  let filtered = findings;
  if (sev) filtered = filtered.filter(f => f.severity.toLowerCase() === sev);
  if (dom) filtered = filtered.filter(f => f.domain === dom);
  render(filtered);
  localStorage.setItem('gov-sev-filter', sev);
  localStorage.setItem('gov-dom-filter', dom);
}

document.getElementById('sev-filter').addEventListener('change', applyFilters);
document.getElementById('domain-filter').addEventListener('change', applyFilters);

// Restore saved filters
const savedSev = localStorage.getItem('gov-sev-filter') || '';
const savedDom = localStorage.getItem('gov-dom-filter') || '';
document.getElementById('sev-filter').value = savedSev;
document.getElementById('domain-filter').value = savedDom;

render(findings);
if (savedSev || savedDom) applyFilters();
</script>
</body>
</html>
```

**Usage:** Replace `{PLACEHOLDERS}` with actual scan data. Populate the `findings` array with the JSON findings from the scan. The template handles filtering, sorting, and localStorage persistence.

### For .xlsx:
- Sheet 1: Summary — Grade, score, domain breakdown, quick wins, long-term goals
- Sheet 2: Findings — table with columns: Severity | Domain | Content Type | Name | Issue | Evidence | Owner | Project | Recommendation. Sort: Severity (Critical=1) then Domain.
- Sheet 3: Full inventory — one row per content item with all captured metadata
- **Formatting:** Auto-fit columns. Severity conditional formatting: CRITICAL=red, HIGH=orange, MEDIUM=yellow, LOW=gray. Header row: bold + freeze panes.

### For .docx:
- Use docx skill. Title page → executive summary (grade + one-liner + domain table) → quick wins → long-term goals → domain-by-domain findings (expanded format) → appendix (full inventory).

### Findings volume (all formats)
In chat and .md, show the top 25 findings by severity plus aggregate counts when there are more than 40. .xlsx, .docx appendix and JSON carry the full list.

### For .md:
- Header block → Quick Wins → Long-Term Goals → Findings (compact format, grouped by severity). No remediation roadmap section (that's covered by quick wins + long-term goals).

### For JSON:
```json
{
  "scan_metadata": { "date": "...", "preset": "...", "scope": "..." },
  "grade": "D-",
  "score": 61.5,
  "partial": false,
  "verdict": "...",
  "domain_grades": { "staleness": "D", "usage": "B", "certification": "C (sampled)", "performance": "N/A (not checked)", ... },
  "quick_wins": [ { "action": "...", "items_affected": N, "effort": "...", "projected_score": N } ],
  "long_term_goals": [ { "goal": "...", "impact": "...", "effort": "..." } ],
  "total_findings": N,
  "findings": [ { "severity": "...", "name": "...", "issue": "...", "evidence": "...", "owner": "...", "domain": N, "recommendation": "..." } ]
}
```
