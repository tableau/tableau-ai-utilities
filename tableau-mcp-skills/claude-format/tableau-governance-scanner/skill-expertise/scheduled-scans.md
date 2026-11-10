# Scheduled Scans Detail

Schedule configuration questions and the scheduled-task prompt template used when the user accepts recurring scans.

### Schedule Configuration

When the user accepts, ask:
1. **Cadence:** Daily, weekly (default), biweekly, monthly
2. **Alert threshold:** Only notify on score drops of 5+ points (default), notify on any change, or full report every time
3. **Scope:** Same as this scan (default), or a different scope

### Scheduled Task Prompt Template

Use the scheduled-tasks create tool (`create_scheduled_task`) with this prompt:

```
You are running a scheduled Tableau Governance Scanner audit. This is an automated run with no user present.

STEP 1 — LOAD METHODOLOGY:
Read the skill file at this path to understand the full scan methodology, then read the files in the skill-expertise folder next to it (check-categories.md, output-formats.md, api-field-availability.md, calibration-notes.md, compare-mode.md, scheduled-scans.md):
[full path to the installed tableau-governance-scanner folder]\SKILL.md

STEP 2 — LOAD PRIOR STATE:
Read memory files for prior scan results (look for the governance-scan-[scope-slug]-[preset] file that matches this task's scope and preset in the memory directory).

STEP 3 — EXECUTE:
Run a full governance scan following the methodology in the SKILL.md and its skill-expertise files:
- Preset: [Standard/Light/Strict from user config]
- Scope: [scope from user config]
- Format: Alert-style (only report score changes and new findings)

STEP 4 — COMPARE:
Compare results to prior scan in memory. Only surface:
- Score changes of [threshold]+ points
- New CRITICAL or HIGH findings not present in prior scan
- Findings that were resolved since last scan

STEP 5 — SAVE TO MEMORY:
Write updated scan results to memory (governance-scan-[scope-slug]-[preset], including the findings list) so the next scheduled run has a baseline.

STEP 6 — REPORT:
If nothing changed, all scores are stable, AND no domain was N/A: "Governance Scanner: All clear. Score [X]/100, no changes since [last scan date]."
If any domain was N/A: never say "All clear". Say "Governance Scanner: Partial. Score [X]/100 (not checked: [domains])."
If there is no comparable prior scan: report the score and say no baseline existed.
If issues found: list them with severity, content name, and recommended action.
```
