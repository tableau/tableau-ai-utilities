# Report Template (Locked, Chat + File)

Every `format-drift-scanner` delivery follows this shape. Chat-first compact summary, then optional file write to Downloads. Never deviate from the section order; never rename headers.

## Two Output Modes

**Mode A: Compact chat summary (default).** Rendered every run. Lightweight; safe to scan in a Studio session.

**Mode B: Full report file (opt-in).** Written to Downloads folder only when user confirms. Uses the full section-by-section shape.

## Mode A: Compact Chat Summary Format

```markdown
**Format Drift Scanner: {workbook_name}**
Placements: {N} measures · {N} dates · {N} text objects · Verdict: {Ready with warnings | Ready to publish | Blocking issues surface}

Findings: {N} Blocking · {N} Warning · {N} Info{ · {N} Unscanned if > 0}

Top items:
1. **[F-{RULE-ID}]** {finding_summary} → {short Desktop fix}
2. **[F-{RULE-ID}]** {finding_summary} → {short Desktop fix}
3. **[F-{RULE-ID}]** {finding_summary} → {short Desktop fix}

Next: {one-line next step}

Want the full report? I can save it to your Downloads folder as `.md` (default) or `.txt`. Say the word.
```

**Compact summary rules.**

- 8-line ceiling in chat before the offer line.
- Verdict is exactly one of `Ready to publish`, `Ready with warnings`, `Blocking issues surface`.
- Top items ordered Blocking first, then Warning, then Info.
- If total findings is zero, render "Findings: 0 · Ready to publish" and skip the Top items block.
- Unscanned count appears in the counts line only when > 0.
- Offer line is exactly: `` Want the full report? I can save it to your Downloads folder as `.md` (default) or `.txt`. Say the word. ``

## Mode B: Full Report File Format

Used only when the user opts into a file write. Path: `{Downloads}/{workbook_name}_format-drift.md` (or `.txt`). Fresh-filename discipline: increment `_v2`, `_v3` on collision. Path resolves OS-appropriately: `%USERPROFILE%\Downloads\` on Windows, `$HOME/Downloads/` on macOS. Never hard-code a tilde-expanded path.

```markdown
# Format Drift Scanner: {workbook_name}

**Placements audited:** {N} measure placements · {N} date pills · {N} text objects
**Data sources:** {ds_names_list}
**Verdict:** {Ready to publish | Ready with warnings | Blocking issues surface}
**Report generated:** {ISO-8601 timestamp}

## Findings by Severity

### Blocking ({N})
- **[F-{RULE-ID}]** {finding_summary}
  - **Scope:** {within_ds ds_name | cross_ds | workbook}
  - **Element:** {field_name or element_category}
  - **Differing format strings:** {baseline} vs {alternates_list}
  - **Fix in Desktop:** {desktop_fix_instruction}

### Warning ({N})
{Same shape as Blocking. Empty section renders as _None._}

### Info ({N})
{Same shape. Empty renders as _None._}

## Findings by Drift Type

| Drift Type | Count |
|---|---|
| Currency (F-CURRENCY-01) | {N} |
| Decimal (F-DECIMAL-02) | {N} |
| Date (F-DATE-03) | {N} |
| Separator (F-SEPARATOR-04) | {N} |
| Font Family (F-FONT-FAMILY-05) | {N} |
| Font Size (F-FONT-SIZE-06) | {N} |
| Negative Treatment (F-NEGATIVE-07) | {N} |

## Baselines Per Drift Type Per DS

{Rendered as a list. Baselines are the first-seen format string per HC#11.}

- **{drift_type}** for **{field_name}** in **{ds_name}**: `{baseline_format_string}`

## Unscanned Placements ({N})

{Rendered only if count > 0. Otherwise omit this section.}

- **{element_type}** on **{worksheet_name}** — `reason: {tool_failure | user_skip | fallback_unavailable}`
  - **Notes:** {short_string}

## Next Steps

{One or two-line pointer. Never generic inspiration.}
```

## Section Rendering Rules (Mode B, Full File Only)

**Header line.** Always `# Format Drift Scanner: {workbook_name}`. Placements audited, data sources, verdict, and timestamp on the four lines under the header.

**Verdict logic:**

- `Blocking issues surface` if `blocking > 0`.
- `Ready with warnings` if `blocking == 0 AND (warning > 0 OR info > 0)`.
- `Ready to publish` if `blocking == 0 AND warning == 0 AND info == 0`.

**Severity sections.** Always render Blocking, Warning, Info in that order. Empty sections render as `_None._`. Never omit; empty is a signal of a clean check.

**Findings by Drift Type table.** Always renders. Zeros are legitimate values; do not omit rows.

**Baselines per Drift Type per DS.** Always renders. Includes baselines even when no drift finding fired for that drift type; downstream diff-mode reuse depends on the baseline being recorded.

**Unscanned Placements section.** Only renders when count > 0. Omit entirely when count is zero.

**Next Steps line.** Concrete pointer: "Publish-readiness handoff emitted" if clean, or "Fix Blocking Currency drift first, then re-run" if issues surface. Never generic advice.

## Overflow Handling

- **20+ findings.** Group Info findings under a `<details>` block after the first 5 per drift type. Blocking and Warning always fully rendered.
- **Multiple DSes.** Order findings by DS name alphabetically for stable diffs across runs.
- **Very wide workbook (100+ placements).** Add a per-worksheet appendix at the end of Mode B if any single worksheet has 10+ placements audited.

## File-Write Confirmation Flow

1. Mode A chat summary renders.
2. Offer line appears at the end.
3. If the user opts in ("yes," "save it," "put it in Downloads," ".md," ".txt"):
   - Confirm format choice if not already stated (default `.md`).
   - Resolve the Downloads folder OS-agnostically. On Windows: `%USERPROFILE%\Downloads\`. On macOS: `$HOME/Downloads/`. Never hard-code a tilde-expanded path or a drive letter; render the fully-resolved absolute path.
   - Confirm the exact save path before writing.
   - Write the file per Mode B shape.
   - Report the path back in chat.
4. If the user declines or doesn't respond, no file is written. Handoff schema still emits to session context regardless.

**Never write a file silently.** HC#1 read-only discipline extends to Downloads-folder writes. Always confirm the path before saving.

**Fresh-filename discipline.** If the target path already exists, append `_v2` (then `_v3`, etc.) before the extension.

**Naming convention.** The `_format-drift` suffix is reserved to this skill; never reuse it for other skills' exports.

## Refuse to Fabricate

Never render a finding without a rule-cited baseline and at least one differing format string. Never invent a drift rule ID. Never render a Blocking finding without confirming the drift is within a single DS (cross-DS is Info-by-default per HC#12). Empty sections are signals of a clean workbook, not gaps to paper over.
