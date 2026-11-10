# Report Template (Locked, Chat + Handoff)

Every `dashboard-preflight` delivery follows this shape. Chat summary first, then optional handoff schema. Never deviate from the section order; never rename headers.

## Two Output Modes

**Mode A: Compact chat summary (default).** Rendered every run. Lightweight; safe to scan in a Studio session.

**Mode B: Full report file (opt-in).** Written to Downloads folder only when user confirms. Uses the full section-by-section shape.

## Mode A: Compact Chat Summary Format

```markdown
**Dashboard Preflight: {dashboard_name}**
Workbook: {workbook_name} · Zones: {N} · Verdict: {Ready to publish | Ready with warnings | Blocking issues surface}

Findings: {N} Blocking · {N} Warning · {N} Info{ · {N} Unscanned if > 0}

Top items:
1. **[P-{RULE-ID}]** {finding_summary} → {short Desktop fix}
2. **[P-{RULE-ID}]** {finding_summary} → {short Desktop fix}
3. **[P-{RULE-ID}]** {finding_summary} → {short Desktop fix}

Next: {one-line next step}

Want the full report? I can save it to your Downloads folder as `.md` (default) or `.txt`. Say the word.
```

**Compact summary rules:**

- 8-line ceiling in chat before the offer line. Top 3 items only, ordered Blocking first, then Warning, then Info.
- If Blocking count is zero, render "None" and pick the top Warning + top Info.
- If total findings is zero, render "Findings: 0" and skip the Top items block. Verdict is "Ready to publish."
- Unscanned count appears in the counts line only when > 0.
- Never render Unscanned Checks details in the compact summary. Direct the user to the file for that.
- Offer line is exactly: `Want the full report? I can save it to your Downloads folder as `.md` (default) or `.txt`. Say the word.`

## Mode B: Full Report File Format

Used only when the user opts into a file write. Path: `{Downloads}/{workbook_name}_{dashboard_name}_preflight.md` (or `.txt`). Fresh-filename discipline: increment `_v2`, `_v3` on collision.

```markdown
# Dashboard Preflight: {dashboard_name}

**Workbook:** {workbook_name}
**Zone count:** {N}
**Verdict:** {Ready to publish | Ready with warnings | Blocking issues surface}
**Report generated:** {ISO-8601 timestamp}

## Findings by Severity

### Blocking ({N})
- **[P-{RULE-ID}]** {finding_summary}
  - **Zone:** {zone_reference or "Dashboard-level"}
  - **Fix in Desktop:** {desktop_fix_instruction}

### Warning ({N})
- **[P-{RULE-ID}]** {finding_summary}
  - **Zone:** {zone_reference or "Dashboard-level"}
  - **Fix in Desktop:** {desktop_fix_instruction}

### Info ({N})
- **[P-{RULE-ID}]** {finding_summary}
  - **Zone:** {zone_reference or "Dashboard-level"}
  - **Fix in Desktop:** {desktop_fix_instruction}

## Unscanned Checks ({N})
{Rendered only if any checks were skipped or failed to run. Otherwise omit this section.}

- **[P-{RULE-ID}]** {reason: tool_failure | user_skip | fallback_unavailable}
  - **Notes:** {short_string}

## Next Steps
{One or two-line pointer to publish-readiness or a specific fix priority. Never generic inspiration.}
```

## File-Write Confirmation Flow

1. Chat summary renders (Mode A).
2. Offer line appears at the end of the summary.
3. If the user opts in ("yes," "save it," "put it in Downloads," ".md," ".txt"):
   - Confirm format choice if not already stated (default `.md`).
   - Resolve the Downloads folder OS-agnostically. On Windows this is `%USERPROFILE%\Downloads\`; on macOS this is `$HOME/Downloads/`. Never hard-code a tilde-expanded path or a Windows drive letter in the confirmation line; render the fully-resolved absolute path returned by the tool environment.
   - Confirm the exact save path before writing. Example on macOS: "Saving to `/Users/{user}/Downloads/Regional_Sales_2026_Q4_Executive_Summary_preflight.md`. Confirm?" Example on Windows: "Saving to `C:\Users\{user}\Downloads\Regional_Sales_2026_Q4_Executive_Summary_preflight.md`. Confirm?"
   - Write the file per Mode B shape.
   - Report the path back in chat.
4. If the user declines or doesn't respond, no file is written. Handoff schema still emits to session context regardless.

**Never write a file silently.** HC#1 read-only discipline extends to Downloads-folder writes. Always confirm the path before saving.

**Fresh-filename discipline.** If the target path already exists, append `_v2` (then `_v3`, etc.) before the extension. Match the i18n-scanner CSV BOM overwrite lesson: never overwrite an existing report path without explicit user confirmation.

## Section Rendering Rules (Mode B, Full File Only)

**Header line.** Always `# Dashboard Preflight: {dashboard_name}`. Workbook and zone count on the two lines under the header. Verdict is exactly one of three strings. Report-generated timestamp on the fourth line.

**Verdict logic:**

- `Blocking issues surface` if `findings_count_by_severity.blocking > 0`.
- `Ready with warnings` if `blocking == 0 AND (warning > 0 OR info > 0)`.
- `Ready to publish` if `blocking == 0 AND warning == 0 AND info == 0`.

**Severity sections.** Always render all three (Blocking, Warning, Info) even when count is zero. Empty sections render as `### Blocking (0)\n_None._` (or Warning/Info equivalent). Never omit a severity section. Empty-count sections signal that the check ran and found nothing.

**Rule ID prefix.** Every bullet starts with `**[P-{RULE-ID}]**`. Rule IDs are drawn from the locked 8-check catalog: P-ZONE-01, P-SHEET-02, P-FILTER-03, P-PARAM-04, P-TITLE-05, P-CANVAS-06, P-FIT-07, P-CONTAINER-08.

**Zone reference.** Either a specific zone name or the literal string `Dashboard-level` for dashboard-scope findings (P-CANVAS-06, dashboard-title P-TITLE-05, dashboard-level P-FILTER-03).

**Desktop fix instruction.** Concrete UI steps. Never blank. Never abstract ("consider fixing this"). Format: verb + Desktop location + action. Example: "Right-click zone > Remove, or rebind to a live sheet via Sheets pane."

**Unscanned Checks section.** Only rendered when at least one check was skipped or failed. Omit the section header entirely when `unscanned_checks: []`. Never render an empty `## Unscanned Checks (0)` section.

**Next Steps line.** Points to the next action: `publish-readiness` if verdict is Ready, or "Fix Blocking issues first, then re-run" if Blocking. Never end with generic advice.

## Overflow Handling

- **20+ findings.** Group Info-severity findings under a `<details>` collapsible block after the first 5, or ask the user if they want the full expanded list. Warning and Blocking always fully rendered.
- **Multi-page dashboards.** Preflight one page per run per HC#2. If the user asks about pages 2-N, ask which one to preflight.
- **Duplicate findings across zones.** Do not deduplicate at report time. Every zone with a P-FIT-07 finding gets its own bullet, even if the finding text is identical. Deduplication would obscure zone-level triage.

## Handoff Emission

After the chat summary, emit `dashboard_preflight_report/1` per `skill-expertise/handoff_schema.md`. The handoff is the machine-readable version of the chat summary. Both must agree; if they disagree, V3 (handoff-completeness) fails and delivery is blocked.

Handoff includes findings that don't render in chat (e.g., zone-level clean evaluations). Chat renders only findings with severity assigned; the handoff includes the full evaluation record for downstream skills.

## Example Rendered Report

```markdown
# Dashboard Preflight: Sales Overview

**Workbook:** Regional_Sales_2026.twbx
**Zone count:** 7
**Verdict:** Ready with warnings

## Findings by Severity

### Blocking (0)
_None._

### Warning (2)
- **[P-FIT-07]** Zone 'Trend by Month' uses Standard view fit; recommended for time-series line is Fit Width.
  - **Zone:** Trend by Month
  - **Fix in Desktop:** Right-click zone > Fit > Fit Width.
- **[P-CANVAS-06]** Canvas is 1600x950; not a known device class and no rationale in dashboard caption.
  - **Zone:** Dashboard-level
  - **Fix in Desktop:** Dashboard pane > Size > select a preset, or add rationale to dashboard caption.

### Info (1)
- **[P-PARAM-04]** Parameter 'Rolling Window' referenced only in tooltip on Zone 'Regional Breakdown'.
  - **Zone:** Regional Breakdown
  - **Fix in Desktop:** No action needed if tooltip-only is intentional. Otherwise, wire into a calc or filter.

## Next Steps

Two Warnings surface; neither is release-blocking. Address if you have time, then run publish-readiness for whole-workbook hygiene.
```

## Refuse to Fabricate

Never render a finding without a rule ID. Never invent severity ("Critical" or "High" would be catalog violations; use Blocking/Warning/Info only). Never render a section with fabricated finding content to fill space. Empty sections are signals of a healthy dashboard, not gaps to paper over.
