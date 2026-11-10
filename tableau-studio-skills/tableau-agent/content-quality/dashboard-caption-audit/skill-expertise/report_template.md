# Report Template (Locked, Chat + File)

Every `dashboard-caption-audit` delivery follows this shape. Compact Tier A chat + opt-in Tier B file. Never deviate from the section order; never rename headers.

## Tier A: Compact Chat Summary

```markdown
**Caption Audit: {workbook_name}**
Dashboards audited: {N} · Total findings: {N} Warnings, {N} Info

Per-dashboard TL;DR:
- {Dashboard A}: {n} missing captions, {n} missing titles{, N default names if any}
- {Dashboard B}: {n} missing captions, {n} missing titles

Top 3 recommendations:
1. {one-line teaser, no rationale}
2. {one-line teaser, no rationale}
3. {one-line teaser, no rationale}

Save the full findings and Desktop-fix instructions to Downloads? (.md default, .txt option, or skip)
```

**Compact summary rules.**

- Target under 25 lines total.
- One TL;DR line per dashboard. If workbook has 10+ dashboards, collapse remaining dashboards after the first 8 into `+ {N} more (see full report)`.
- Per-dashboard TL;DR ordering locked per HC#15: render in `list-dashboards` enumeration order. Never sort by finding count, severity mix, or judgment.
- Zero findings on a dashboard renders inline in its enumeration slot as `{Dashboard}: fully labeled`.
- Top 3 recommendations one-line only. No rationale, no rule ID, no XML citation in chat.
- Top-3 selection is locked per HC#14: sort by severity (Warning → Info), then dashboard enumeration order, then rule ID ascending; take the first 3. Never selected by subjective importance.
- Save-file offer is the last line.

**Never in Tier A.**

- Per-finding XML citations.
- Full recommendation list beyond top 3.
- Handoff schema payload.
- V-gate output.
- Desktop-fix step-by-step details.

## Tier B: Full Findings File

Path: `{Downloads}/{workbook_name}_caption-audit.md` (or `.txt`). Fresh-filename discipline: increment `_v2`, `_v3` on collision.

```markdown
# Caption Audit: {workbook_name}

**Report generated:** {ISO-8601 timestamp}
**Workbook:** {workbook_name}
**Dashboards audited:** {N}
**Total findings:** {N} Warnings, {N} Info
**UNSCANNED dashboards:** {list_or_none}

## Summary

{One paragraph summarizing the workbook's caption completeness state. Cite highest-severity findings first. Tone: neutral-constructive.}

## Per-Dashboard Findings

### Dashboard: {dashboard_name}

**Findings:** {N} Warnings, {N} Info

{For each finding on this dashboard:}

- **[{rule_id}] {rule_name}** ({severity})
  - **Element:** {element_name_and_type}
  - **XML evidence:** `{quoted_xml_snippet}`
  - **Desktop fix:** {step_by_step_instruction}

{Repeat per dashboard until all findings covered.}

## UNSCANNED Dashboards

{If any dashboard flagged UNSCANNED per HC#9, list here with reason.}

- **{dashboard_name}:** {reason} (e.g., "get-dashboard-xml returned partial results")

## Recommended Actions

{Prioritized action list across the workbook. Warnings first, then Info.}

1. **{action_title}.** {specific_desktop_fix_path}. Affects: {dashboard_or_worksheet_list}.
2. **{action_title}.** ...

## Handoff Payload

```yaml
schema: caption_audit_report/1
workbook_name: "{name}"
dashboards_audited: {N}
findings:
  - rule_id: "DC-TITLE-01"
    severity: "Warning"
    dashboard: "{name}"
    element: "{element_ref}"
    xml_evidence: "{snippet}"
    desktop_fix: "{instruction}"
  - {more findings same shape}
unscanned_dashboards: [{list_or_empty}]
routing:
  desktop_spellcheck: {true | false}
  format_drift_scanner: {true | false}
  viz_planner: {true | false}
  dashboard_preflight: {true | false}
```

## Next Steps

{One or two-line concrete pointer based on findings. Never generic.}

## Reference

- Completeness catalog: `completeness_catalog.md` in the skill directory.
- Handoff schema: `handoff_schema.md`.
```

## Section Rendering Rules (Tier B)

**Header block.** Always renders skill version, timestamp, workbook name, dashboards audited count, total finding counts, and UNSCANNED list.

**Summary section.** 1-2 paragraphs. Plain-language. Neutral-constructive tone regardless of finding count.

**Per-Dashboard Findings.** Every dashboard renders a section, even fully-labeled ones (renders `{N} Warnings, {N} Info` where N=0 and one line "Fully labeled."). Never omit a dashboard's section.

**UNSCANNED Dashboards.** Renders only if HC#9 fired on any dashboard. If empty, section is omitted.

**Handoff Payload.** Always rendered as a YAML block.

**Next Steps.** Concrete pointer per severity mix. Never generic.

## Overflow Handling

- **Many findings (30+).** No inline cap in Tier B; every finding renders. Group by dashboard preserves scan-ability.
- **10+ dashboards.** Tier A collapses remaining dashboards after the first 8 into `+ {N} more (see full report)`. Tier B renders every dashboard.
- **UNSCANNED dashboards.** Fire only when `get-dashboard-xml` returns partial results (HC#9). Report explains why the dashboard was skipped.

## File-Write Confirmation Flow

1. Tier A chat summary renders with save-file offer.
2. If user opts in:
   - Confirm format (.md default, .txt option).
   - Resolve Downloads folder OS-agnostically. Windows: `%USERPROFILE%\Downloads\`. macOS: `$HOME/Downloads/`.
   - Confirm the exact save path before writing.
   - Write per Tier B shape.
   - Report path back in chat.
3. If user declines, no file is written. Handoff schema still emits to session context.

Never write silently. HC#12 non-override.

Fresh-filename discipline: append `_v2`, `_v3` on collision.

## Refuse to Fabricate

Never render a finding without citing XML evidence. Never invent a rule beyond the 8-rule catalog. Never suppress a Warning to please the user. Never render the improvement plan in Tier A chat.
