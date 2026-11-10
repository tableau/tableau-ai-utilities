# Report Template (Locked, Chat + File)

Every `chart-swap-advisor` delivery follows this shape. Chat-first compact summary, then optional file write to Downloads. Never deviate from the section order; never rename headers.

## Two Output Modes

**Mode A: Compact chat summary (default).** Rendered every run. Lightweight; safe to scan in a Studio session.

**Mode B: Full report file (opt-in).** Written to Downloads folder only when user confirms. Uses the full section-by-section shape.

## Mode A: Compact Chat Summary Format

```markdown
**Chart Swap Advisor: {worksheet_name}**
Workbook: {workbook_name} · Current: {current_mark_type} · Verdict: {Keep | Swap Recommended | Anti-Pattern Block}

Classification: {question_type} ({confidence} confidence · signals: {short_signal_list})
{Verdict line explaining the recommendation in one sentence.}

{If Swap Recommended or Anti-Pattern Block, next 3 lines:}
Recommended: {recommended_chart_type}
Rationale: {short_reason}
Rebuild path: hand off to worksheet-builder with the payload, or apply manually in Desktop.

{If Keep, one line:}
Rationale: {short_reason_current_chart_fits}

{If anti-patterns fired, one line per pattern:}
Anti-pattern: {AB-X or W-X} · {short rationale}

Want the full report? I can save it to your Downloads folder as `.md` (default) or `.txt`. Say the word.
```

**Compact summary rules.**

- 8-line ceiling in chat before the offer line.
- Classification confidence always shown.
- Verdict is exactly one of `Keep`, `Swap Recommended`, `Anti-Pattern Block`.
- Anti-pattern lines only render when at least one fired.
- If verdict is Keep, do not show a "Recommended" line.
- Offer line is exactly: `` Want the full report? I can save it to your Downloads folder as `.md` (default) or `.txt`. Say the word. ``

## Mode B: Full Report File Format

Used only when the user opts into a file write. Path: `{Downloads}/{workbook_name}_{worksheet_name}_chart-swap.md` (or `.txt`). Fresh-filename discipline: increment `_v2`, `_v3` on collision. Path resolves OS-appropriately: `%USERPROFILE%\Downloads\` on Windows, `$HOME/Downloads/` on macOS. Never hard-code a tilde-expanded path.

```markdown
# Chart Swap Advisor: {worksheet_name}

**Workbook:** {workbook_name}
**Current chart:** {mark_type} + {shelf_placement_summary}
**View fit:** {view_fit}
**Verdict:** {Keep | Swap Recommended | Anti-Pattern Block}
**Report generated:** {ISO-8601 timestamp}

## Classification

**Question type:** {type}
**Confidence:** {High | Medium | Low}
**Supporting signals:**
- {signal_1}
- {signal_2}
- ...
{If confidence is Low, add:}
**Classification notes:** {explanation_of_weak_signal}

## Audience

**Stated:** {Yes / No}
{If Yes:}
**Audience type:** {Executive | Manager | Analyst | Operations | External}
**Anti-pattern impact:** {audience_override_note_or_none}

## Anti-Patterns Matched

{Rendered as a list. Empty list renders as "_None._" Never omit this section.}

- **[{Anti-Pattern-ID}]** {rationale}
  - **Severity:** {Auto-Block | Warning | Info}

## Recommendation

{If Keep:}
**Verdict:** Keep. The current chart is a right fit for the classified question type.
**Rationale:** {reason_why_current_chart_fits}

{If Swap Recommended or Anti-Pattern Block:}
**Recommended chart type:** {recommended_chart_type}
**Rationale:** {detailed_reason}

### Rebuild Handoff to Worksheet Builder

- **Recommended mark type:** {mark_type}
- **Recommended shelf placements:**
  - Rows: {list_or_none}
  - Columns: {list_or_none}
  - Marks: {list_or_none}
  - Filters: {list_or_none}
  - Detail: {list_or_none}
- **Preserve fields:** {list_or_none}
- **Fields to drop:** {list_or_none}
- **Rebuild instructions summary:** {short_string}

Ask to have this chart rebuilt and this payload carries over automatically, or apply the shelf placements manually in Desktop.

## Next Steps

{One or two-line pointer. Never generic inspiration.}
```

## Section Rendering Rules (Mode B, Full File Only)

**Header line.** Always `# Chart Swap Advisor: {worksheet_name}`. Workbook, current chart, view fit, verdict, and timestamp on the five lines under the header.

**Classification section.** Question type and confidence always shown. Supporting signals rendered as a bullet list. Classification notes only rendered when confidence is Low.

**Audience section.** Always rendered. "Stated: No" is a legitimate value, not a gap. Audience type and anti-pattern impact only rendered when stated is Yes.

**Anti-Patterns Matched section.** Always rendered. Empty list renders as `_None._`. Never omit this section; empty is a signal, not a gap.

**Recommendation section.** Content varies by verdict:

- Keep: two-line rationale.
- Swap Recommended / Anti-Pattern Block: full rebuild handoff payload rendered as a nested sub-section.

**Rebuild Handoff sub-section.** Only rendered when verdict is Swap Recommended or Anti-Pattern Block. Every payload field rendered with a bullet.

**Next Steps line.** Concrete pointer: "Ask to have this rebuilt" if Swap/Block, or "No further action needed" if Keep. Never generic advice.

## Overflow Handling

- **10+ supporting signals.** Group under a `<details>` collapsible block after the first 5 in Mode B; not applicable in Mode A (Mode A caps at signal list length).
- **Multiple anti-patterns fired.** All rendered; do not deduplicate. Order by severity: Auto-Block first, then Warning, then Info.
- **Multi-mark worksheet (dual-axis, MARKS card multi-mark).** Render one Recommendation sub-section per mark, each with its own classification and anti-pattern list. Verdict is the union: if any mark is Anti-Pattern Block, overall is Anti-Pattern Block.

## File-Write Confirmation Flow

1. Mode A chat summary renders.
2. Offer line appears at the end.
3. If the user opts in ("yes," "save it," "put it in Downloads," ".md," ".txt"):
   - Confirm format choice if not already stated (default `.md`).
   - Resolve the Downloads folder OS-agnostically. On Windows: `%USERPROFILE%\Downloads\`. On macOS: `$HOME/Downloads/`. Never hard-code a tilde-expanded path or a drive letter; render the fully-resolved absolute path returned by the tool environment.
   - Confirm the exact save path before writing. Example on macOS: "Saving to `/Users/{user}/Downloads/Regional_Sales_Trend_chart-swap.md`. Confirm?" Example on Windows: "Saving to `C:\Users\{user}\Downloads\Regional_Sales_Trend_chart-swap.md`. Confirm?"
   - Write the file per Mode B shape.
   - Report the path back in chat.
4. If the user declines or doesn't respond, no file is written. Handoff schema still emits to session context regardless.

**Never write a file silently.** HC#1 read-only discipline extends to Downloads-folder writes. Always confirm the path before saving.

**Fresh-filename discipline.** If the target path already exists, append `_v2` (then `_v3`, etc.) before the extension. Match the i18n-scanner CSV BOM overwrite lesson: never overwrite an existing report path without explicit user confirmation.

**Naming convention.** The `_chart-swap` suffix is reserved to this skill; never reuse it for other skills' exports.

## Refuse to Fabricate

Never render a recommendation without a rule-cited rationale. Never invent an anti-pattern ID. Never render a Keep verdict with a fabricated "matches best practice" rationale; the rationale must cite the specific taxonomy match. Empty Anti-Patterns Matched sections are signals of a clean chart, not gaps to paper over.
