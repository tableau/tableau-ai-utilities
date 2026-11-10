# Tableau Governance Scanner

A Claude skill that audits Tableau Cloud or Server sites for governance and hygiene issues. Built for [Claude Desktop](https://claude.ai/download) and the [Tableau MCP](https://github.com/tableau/tableau-mcp).

## How It Works

Say "scan CCI Platform" or "audit my site" and the skill pulls your content via the Tableau REST API, runs checks across 7 domains, and returns a letter-graded health report with prioritized actions.

```
CCI Platform – Governance Scan

D- – 61.5/100
"Significant issues. Trust and discoverability degraded."

Staleness: D  |  Usage: B  |  Certification: D  |  Naming: D
Structure: D  |  Performance: A  |  Metadata: C

Quick Wins (raise to ~74):
1. Add tags to all 14 views – 5 min
2. Add descriptions to 2 workbooks – 10 min
3. Archive 3 zero-view workbooks – 5 min

Long-Term Goals:
1. Certify primary datasource (8 observed downstream workbooks, sampled)
2. Fix stale pipeline (users on 99-day-old data)
3. Add co-owner (bus factor = 1)
```

## Audit Domains

| Domain | What It Catches |
|--------|-----------------|
| Staleness | Content not updated within threshold |
| Usage & Adoption | Ghost workbooks, zero-view content, dormant legacy dashboards |
| Certification & Trust | Uncertified datasources with high downstream impact |
| Naming | "Copy of", "Sheet 1", "(old)", test content in production |
| Structure | Default project clutter, owner concentration, sandbox sprawl |
| Performance | Over-sheeted workbooks, large files, live connections under load |
| Metadata | Missing descriptions, low tag adoption |

## Output Formats

| Format | Use Case |
|--------|----------|
| Control Tower | Interactive HTML dashboard with filters and severity gauges |
| Spreadsheet | Shareable .xlsx with one row per finding |
| Word | Formal .docx report for leadership |
| Markdown | Lightweight, good for wikis or chat |
| JSON | Programmatic consumption |

## Presets

| Preset | For |
|--------|-----|
| Light | First scan or small site. Flags only clear problems. |
| Standard | Balanced. The default. |
| Strict | Mature orgs with governance teams. |

## Key Features

- **Zero-config execution.** Infers scope, preset, and format from natural language.
- **Compare mode.** Side-by-side project comparison or delta tracking over time.
- **Memory-aware.** Remembers config per scope and preset, and shows score changes between comparable scans.
- **Graceful degradation.** Proceeds when datasource/project APIs return 401/403, grades skipped domains N/A, and labels the run Partial.
- **Validation phase.** Arithmetic, deduplication, and false-positive checks before output.
- **Scheduled monitoring.** Set it and forget it. Get alerted only when scores drop or new issues appear.

**Note on permissions:** Scheduled runs may prompt for tool approval the first time they access Tableau MCP endpoints. Run the task manually once ("Run now") to pre-approve the tools it needs. After that, future runs execute without interruption.

## Requirements

- Claude Desktop with the Tableau MCP connected
- Tableau Cloud or Server REST API access
- Minimum permissions: `list-views` + `list-workbooks` (datasource/project access optional)

## Installation

1. Save the whole `tableau-governance-scanner` folder (`SKILL.md` plus the `skill-expertise/` files) to your Claude skills directory. Installing `SKILL.md` alone leaves out the check catalog and output formats it reads.
2. Trigger with: "audit my site", "governance scan", "scan [project name]", or "what needs attention?"

## Companion Skills

| Skill | Handoff |
|-------|---------|
| VizCritique Pro | Evaluate visual design of flagged views |
| Tableau Scribe | Auto-generate docs for undocumented content |
| Data Quality Sentinel | Profile data in flagged datasources |
| Dashboard Architect | Plan redesigns for monolith workbooks |

## Limitations

- No permission auditing (not exposed by the Tableau MCP)
- No extract refresh schedules (uses `updatedAt` as proxy)
- Downstream workbook counts for datasources are sampled (up to 10 workbooks) and are a lower bound
- No render-time profiling (sheet count and size are proxy signals)
- `totalViewCount` is lifetime cumulative. Skill uses recency-adjusted logic to compensate.
