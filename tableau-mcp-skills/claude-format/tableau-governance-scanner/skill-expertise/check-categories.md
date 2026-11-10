# Check Categories Catalog

The full catalog of the seven governance check domains, with logic, patterns, and per-check severity.

### Domain 1: Staleness

**What:** Content that hasn't been updated within the threshold window.

**Logic:**
- Use `updatedAt` from views (and datasources if available)
- For workbooks without direct updatedAt, use MAX(updatedAt) from their views
- Flag content that exceeds the threshold. Do not flag content created within the last 7 days.
- **Base severity:** MEDIUM for views, workbooks and datasources. Datasources have no view counts, so escalate a stale datasource to HIGH only when its observed downstream WBs (sampled) meet the preset threshold; otherwise it stays MEDIUM.
- **Severity escalation:** stale AND totalViewCount > 50 AND updatedAt is recent-ish (within 1 year) = people actively relying on stale data = CRITICAL
- **Severity escalation:** stale AND totalViewCount > 50 AND updatedAt > 1 year = likely legacy-popular but dormant = HIGH
- **Severity reduction:** stale AND totalViewCount = 0 = just cluttering = LOW

**Recency nuance:** Since totalViewCount is cumulative, use updatedAt as a recency proxy. A view with 500 lifetime views but updatedAt 2 years ago is not "actively relied upon" — it's historically popular. Only escalate to CRITICAL when both totalViewCount is high AND updatedAt suggests the view was recently active (within 1 year) before going stale.

### Domain 2: Usage & Adoption

**What:** Content nobody is using, or content with suspicious engagement patterns.

**Checks:**
- **Zero-view views** — Views with totalViewCount = 0. Candidates for archival.
- **Ghost workbooks** — Workbooks where ALL views have totalViewCount = 0. Entire workbook is unused.
- **Low-traffic content** — Views with totalViewCount ≤ threshold (Standard/Strict) that were created >30 days ago.
- **Legacy-popular dormant** — Views with high totalViewCount (>100) but updatedAt >1 year ago. Still getting flagged by teams but likely abandoned.

**Severity:**
- Ghost workbooks in shared projects (not Sandbox/Testing): HIGH
- Ghost workbooks in Sandbox/Testing projects: LOW (expected)
- Zero-view views in otherwise active workbooks: MEDIUM
- Low-traffic content: LOW (informational)
- Legacy-popular dormant: MEDIUM (advisory — "verify if still needed")

**False positive prevention:**
- Do NOT flag views created in the last 7 days (use createdAt)
- Reduce severity for content in projects containing "Sandbox", "Test", "Dev", "Personal", "Staging"

### Domain 3: Certification & Trust

**What:** Datasources that are heavily used but lack certification or quality signals.

**Requires:** list-datasources to succeed. If it fails (401/403), grade this domain N/A (not checked) and note in output: "Datasource certification checks skipped — insufficient API permissions."

**Downstream count:** No tool returns it directly. Sample the 10 workbooks with the highest summed `totalViewCount` (`hitsTotal`), call `get-workbook` and read `upstreamDatasources`, and report "observed downstream WBs (sampled, lower bound)". If no sample was possible, say "downstream count not available, estimate only" and cap severity at HIGH.

**Checks:**
- **Uncertified high-use datasources** — Not certified (`isCertified:eq:false`) but observed in at least the preset's threshold of workbooks (Light ≥8, Standard ≥5, Strict ≥3; the sample cap is 10).
- **Missing descriptions on datasources** — No description field populated. (Owned by this domain; Domain 7 covers workbook descriptions only.)
- **Untagged content** — (Strict only) Workbooks or datasources with empty tags object.

**Severity:**
- Uncertified + observed downstream at or above the preset threshold: HIGH (CRITICAL only when combined per the escalation rules and the count is observed)
- Missing datasource description: MEDIUM
- Untagged: LOW

### Domain 4: Naming & Professionalism

**What:** Content with names that signal it's unfinished, duplicated, or unmaintained.

**Naming violation patterns (case-insensitive regex):**

| Pattern | Regex | Interpretation | Severity | From preset |
|---------|-------|---------------|----------|-------------|
| Default sheet names | `^Sheet\s*\d+$` | Tab never renamed | MEDIUM | Light |
| Copy prefix | `^Copy\s+of\s+` | Unresolved duplicate | MEDIUM | Standard |
| Test content | `\btest\b` (standalone word) | Test content in production | HIGH | Light |
| Default workbook | `^(New Workbook\|Book\d+\|Untitled)$` | Never personalized | MEDIUM | Light |
| Duplicate suffix | `\(\d+\)\s*$` | Upload collision | MEDIUM | Strict |
| Temp names | `\b(tmp\|temp\|draft)\b` | Temporary left behind | MEDIUM | Strict |
| Deferred cleanup | `\b(DELETE\|ARCHIVE\|OLD\|DEPRECATED)\b` | Tagged for removal, not removed | HIGH | Light |

Run only the patterns whose "From preset" tier is at or below the chosen preset (Light runs the Light rows; Standard adds Standard rows; Strict runs all).

**Apply to:** Workbook names, view names (from viewUrlName or name field), datasource names.

**False positive handling:**
- "Test" in a project called "Testing" or "QA" → reduce to LOW
- "Draft" in a personal/sandbox project → reduce to LOW
- "Dashboard 1" is NOT a violation (valid Tableau default for dashboard tabs)

**Systemic aggregation:** When >50 items match the same pattern, report as one systemic finding: "[Pattern]: [count] items ([list top 5 names]...)" rather than listing individually.

### Domain 5: Structure & Organization

**What:** Architectural issues with how content is organized.

**Checks:**
- **Content in Default project** — Anything in a project named "default" (case-insensitive) hasn't been organized.
- **Sandbox sprawl** — Projects with "Sandbox" in the name containing >100 workbooks (flag threshold = severity threshold).
- **Owner concentration** — One person owns >30% of scanned content. Bus factor risk.
- **Project proliferation** — If project count > workbook count ÷ 3, over-organization or abandoned shells.

**Severity:**
- Content in Default: MEDIUM
- Sandbox sprawl >100 items: MEDIUM (systemic)
- Owner concentration >50%: HIGH
- Owner concentration 30-50%: MEDIUM (Strict only)
- Project proliferation: LOW (informational)

### Domain 6: Performance Signals

**What:** Content with structural characteristics that suggest performance problems.

**Checks (require get-workbook enrichment for full accuracy):**
- **Over-sheeted workbooks** — Use `list-workbooks` filter `sheetCount:gt:[threshold]`; confirm the top candidates with get-workbook (values unverified).
- **Large workbooks** — Use `list-workbooks` filter `size:gt:[N]` (units unconfirmed; check a result first), confirm top candidates with get-workbook.
- **Live connections on high-traffic workbooks** — `list-workbooks`/`list-datasources` filter `hasExtracts:eq:false` + the workbook's views have high `totalViewCount`. Workbook-to-datasource linkage only comes from sampled get-workbook `upstreamDatasources`; without it, report as "linkage not checked".

**Severity:**
- Over-sheeted + high usage: HIGH
- Large workbook + high usage: HIGH
- Over-sheeted + low usage: MEDIUM
- Live connection + high traffic: MEDIUM (advisory)

### Domain 7: Metadata Completeness

**What:** Content missing the metadata that makes a Tableau site navigable and self-service.

**Checks:**
- **Workbooks without descriptions** — `description` field is empty string. (Owned by this domain; datasource descriptions are checked in Domain 3.)
- **Tag adoption rate** — Percentage of workbooks with non-empty tags. If <10%, flag as systemic.

**Severity:**
- Site-wide tagging <10%: MEDIUM (systemic finding, report as one item with count)
- Site-wide descriptions <20%: MEDIUM (systemic)
- Individual items: LOW (unless combined with other issues)
