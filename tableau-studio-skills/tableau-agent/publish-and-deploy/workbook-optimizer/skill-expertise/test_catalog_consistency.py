#!/usr/bin/env python3
"""Lock the workbook-optimizer skill to the Python catalog and SKILL.md procedure.

Catalog records live in wbo.py. SKILL.md owns walk, consent, journal, and
severity. These checks fail if the skill points at the research doc, if
corrected Tableau Help guidance regresses, or if the Python catalog drifts
from detectors / mechanical ids.
"""
from __future__ import annotations

import inspect
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL = SKILL_DIR / "SKILL.md"
EXPERTISE_DIR = Path(__file__).resolve().parent
DESIGN_DOC = SKILL_DIR.parents[2] / "docs" / "performance-best-practices.md"
PRIORITY_SECTION_RE = re.compile(
    r"##+\s*Priority mapping(.*?)(?=\n##\s|\Z)",
    re.DOTALL,
)
OUTPUT_FORMAT_RE = re.compile(
    r"##\s*Output Format \(Chat\)(.*?)(?=\n##\s|\Z)",
    re.DOTALL,
)
HR_LINE_RE = re.compile(r"^---\r?$", re.MULTILINE)
CHAT_PARTS = ("**Summary**", "**Issues found**", "**Actions**", "**Report**", "**Fix next step**")
SEVERITY_GROUPS = (
    "- WARNING: a significant load-time risk; address it.",
    "- NOTE: worth fixing, but a lower risk or a smaller payoff. Often optional cleanup.",
    "- INFO: minor or advisory. Low impact, usually housekeeping.",
)
RESULT_VALUES = ("pass", "fail", "n/a", "author-advice")
NON_PROGRAMMABLE_IDS = (
    "test-anchor-table",
    "publish-shared-sources",
    "materialize-calcs-in-extract",
    "reduce-mark-count",
    "performance-recorder",
    "fix-source-bottlenecks",
    "clean-structured-data",
)
ALLOWED_IMPACT = {
    "big",
    "medium",
    "small",
    "none",
    "indirect",
    "variable",
    "unknown",
}
FORMULA_IDS = ("consolidate-duplicate-calcs", "binary-string-branches")


def skill_text() -> str:
    return SKILL.read_text(encoding="utf-8")


def test_skill_does_not_reference_the_design_doc():
    text = skill_text()
    for ref in ("performance-best-practices", "docs/performance"):
        assert ref not in text, (
            f"SKILL.md must be self-contained; found reference to {ref!r}"
        )


def test_walk_id_duplication_is_gone():
    text = skill_text()
    assert "```walk-ids" not in text, (
        "the walk must not use a duplicated walk-ids block"
    )


def test_walk_is_defined_from_check_and_list():
    text = skill_text()
    assert "Catalog" in text, "SKILL.md needs a Catalog section heading"
    assert "list check" in text, "SKILL.md must tell the agent to run list check"
    assert "list fix" in text, "SKILL.md must tell the agent to run list fix"
    assert "check --format json" in text or "check <path> --format json" in text
    for value in RESULT_VALUES:
        assert value in text, f"walk must define the {value!r} result"
    assert re.search(r"only from `fail`|fail rows only|fail-row", text, re.I), (
        "recommendations must be derived only from fail rows"
    )
    assert "programmable: false" in text or "programmable:false" in text or (
        "`programmable`" in text and "false" in text
    )


def test_priority_comes_from_json():
    text = skill_text()
    m = PRIORITY_SECTION_RE.search(text)
    assert m, "SKILL.md must contain a Priority mapping section"
    assert "priority" in m.group(1).lower()
    assert "count-over-countd" in text
    assert "MEDIUM" in text
    assert "CLEANUP" in m.group(1)


def test_frontmatter_description_is_plain_single_quoted():
    text = skill_text()
    assert "description: >-" not in text, (
        "folded-block YAML description hides on some macOS Studio builds"
    )
    assert re.search(r"^description: '", text, re.MULTILINE), (
        "description must be a plain single-quoted scalar"
    )
    assert "Do NOT trigger for:" in text, "description must include a Do NOT trigger block"
    # Hosts pick a skill from the description alone, so the body's "stats when
    # asked by name" rule is unreachable unless the description triggers on it.
    description = re.search(r"^description: '(.*)'$", text, re.MULTILINE).group(1)
    triggers, _, not_triggers = description.partition("Do NOT trigger for:")
    assert '"show me stats on this workbook" (stats mode)' in triggers, (
        "description must trigger stats mode on an explicit workbook-stats request"
    )
    assert "never auto-selected" in description, "stats is still never the default"
    assert "stats about the data itself" in not_triggers, (
        "data stats (totals, counts) must not trigger the skill"
    )
    assert "python wbo.py check" in text, (
        "skill must tell the agent to run python wbo.py check"
    )
    assert "python wbo.py check <path>" in text, (
        "skill must show the instructional check <path> form, not only a catalog mention"
    )
    assert "do not invent" in text.lower() or "Do not invent" in text
    assert "--format json" in text, "agents must be told to use check --format json"
    assert "--format html" in text, "skill must document the customer HTML report"
    assert "--report-dir" in text, (
        "skill must document the one-shot check --report-dir report bundle"
    )
    assert "--format markdown" in text, "skill must document the customer markdown report"
    assert "--format human" in text, "skill must document the default human check format"


def test_frontmatter_has_name_and_bounded_description():
    text = skill_text()
    lines = text.splitlines()
    assert lines[0] == "---", "SKILL.md must open with frontmatter"
    close = next((i for i, l in enumerate(lines[1:], 1) if l == "---"), None)
    assert close is not None, "frontmatter must close with ---"
    front = lines[1:close]
    assert "name: workbook-optimizer" in front, "frontmatter needs name: workbook-optimizer"
    desc = next((l for l in front if l.startswith("description: ")), "")
    assert desc, "frontmatter needs a description"
    # A single apostrophe inside a single-quoted YAML scalar ends it early.
    inner = desc[len("description: '"):-1]
    assert "'" not in inner, "description must not contain an apostrophe"
    assert len(inner) < 2000, "keep the description under 2000 characters"


def test_merge_grafts_are_present():
    text = skill_text()
    assert "## Hard Constraints" in text
    assert "## Severity framework" in text
    assert "Optimization Readiness Score" in text
    # The NOTE definition already says "Often optional cleanup"; the score
    # sits right under it, so it must not repeat that.
    assert "Notes are optional cleanup" not in text
    assert "## Common mistakes" in text
    assert re.search(r"^-\s+Scope:", text, re.MULTILINE), (
        "journal header must include a Scope field"
    )
    # Cleanup: plain words, real file names, no rename, only with 2+ copies.
    assert "1. Keep only the final copy, `<working-dir>/<name>_optimized_<token>_" in text
    assert "2. Keep all copies" in text
    assert "only when this session saved **more than one**" in text
    assert "Never rename a file" in text
    for stale in ("Keep the full chain", "ORIGINAL-optimized", "Clean up?", "-optimized-*"):
        assert stale not in text, f"stale cleanup wording: {stale!r}"
    assert "Scoping + object-count gate" in text
    assert "Size warning" in text
    assert "warnings[]" in text
    assert "large-file" in text
    assert "large-object-count" in text
    assert "200+" in text
    assert "500" in text
    assert "python3 wbo.py" in text, "skill must document a python3 fallback"
    # Auto-fixable issues are offered as a numbered menu (option 1 = fix all).
    assert "Fix all auto-fixable issues" in text, (
        "fix mode must offer a numbered menu whose option 1 fixes all auto-fixable issues"
    )
    # One author-facing term: "auto-fixable", never bare "fixable" (author-only
    # issues are fixable too, by the author).
    bare = re.findall(r"(?<!auto-)\bfixable\b", text, re.I)
    assert not bare, f"say 'auto-fixable', not bare 'fixable': {bare}"
    # Author-only issues are the menu's last option, not a list printed up front.
    assert "4. Fix issues manually\nReply with a number, or N to finish fixing." in text, (
        "the fix menu ends with a Fix issues manually option"
    )
    assert "do not print the\nmanual issues as a list up front" in text
    # Individual auto-fixes must read as auto-fixes, not as bare issue titles.
    assert (
        "Choose what to fix. Auto-fixes are saved to a new copy of the workbook; "
        "your original file is not changed.\n\n1. Fix all auto-fixable issues\n"
        "2. Auto-fix: <auto-fixable issue title>\n3. Auto-fix: <auto-fixable issue title>\n"
    ) in text, "the fix menu opens with a lead line and labels each auto-fix"
    assert "2. <auto-fixable issue title>" not in text, "unlabeled auto-fix menu entries"
    # No one-option menu: once auto-fixes run out, the manual list shows at once,
    # numbered so the user can pick one for step-by-step help.
    assert "do not show a menu with only \"Fix issues manually\"" in text
    assert "1. <issue title> — <what to change> (<effort>)" in text, (
        "each manual to-do item carries its effort tag, as in Actions"
    )
    assert "same `(low effort)` / `(medium effort)` / `(high effort)` tag" in text
    assert re.search(r"no\s+other\s+sentence\s+before\s+it", text), (
        "the manual list has a single lead sentence"
    )
    # A live run read "5" against the previous, longer list and gave the steps
    # for the wrong issue; it also cut the manual list short.
    assert re.search(
        r"A number always refers to the list in your\s+most recent reply, never an earlier one",
        text,
    ), "a reply number resolves against the latest list only"
    assert "`You picked <n>: <issue title>.`" in text, (
        "the step-by-step reply names the chosen issue first, so a wrong pick is visible"
    )
    assert re.search(
        r"no\s+`…and <k> more`,\s+no\s+\"abbreviated\"\s+note,\s+and\s+no\s+pointer\s+to\s+the\s+report",
        text,
    ), "the manual to-do list is never shortened"
    assert re.search(r"count\s+must\s+match\s+the\s+list", text), (
        "'<N> issues remain' must equal the items listed"
    )
    assert (
        "Reply with a number for step-by-step help in Tableau Studio, or N to finish fixing." in text
    )
    assert 'never say\n"author-only" in chat' in text
    # Picking a manual issue shows only its steps; the list comes back after the
    # user says done and the change is re-checked.
    assert "**one issue at a time.**" in text
    assert "Do **not**\n  show the list again in this reply." in text
    assert (
        "`Reply done when you've made the change and saved the workbook, or N to finish fixing.`" in text
    )
    assert "When the user replies **done**, check the change before moving on" in text
    assert "`python wbo.py check <that file> --format json`" in text
    assert "never claim it is fixed" in text
    assert "only the remaining issues, renumbered from 1" in text
    assert "then show the list\n  again (same format, same numbers)" not in text
    # N means done: straight to the wrap-up, which never offers more fixes and
    # has a fixed ending (the cleanup question, or "Fix mode is finished.").
    assert "**N always means finish fixing.**" in text
    assert "Never suggest or offer more fixes\nhere" in text
    assert "**Fixed ending.**" in text
    assert text.count("`Fix mode is finished.`") >= 2, (
        "both wrap-up endings (with and without cleanup) close with Fix mode is finished."
    )
    for stale in ("or N to stop.", "leave the rest for later"):
        assert stale not in text, f"stale fix-mode N wording: {stale!r}"
    assert "a reply never ends with two numbered prompts" in text
    # A live wrap-up re-listed every remaining issue twice; it is now one
    # short Summary with the applied fixes.
    wrap_up = (
        "**Summary**\n\nYou fixed <a> issues. <r> remain, <w> of them Warnings.\n\n"
        "- <issue title> (auto-fix)\n"
        "- <issue title> (fixed by you, confirmed by the re-check)\n\n"
        "The optimized copy is `<working-dir>/<name>_optimized_<token>_<N>.twbx`\n\n"
        "Fix mode is finished.\n"
    )
    assert wrap_up in text, "the wrap-up follows the short template"
    phase3 = text[text.index("## Phase 3"):text.index("## Common mistakes")]
    template = phase3[phase3.index("```markdown"):]
    template = template[:template.index("```", 3)]
    for gone in ("**Issues found**", "**Actions**", "Readiness Score", "Applied:"):
        assert gone not in template, f"wrap-up template must not contain {gone}"
    for rule in (
        "no **Issues found** or **Actions** section",
        "no Optimization Readiness Score",
        "do not list the remaining issues",
        "lists only what was applied",
        "no deferred or rejected lines",
        "`You didn't apply any fixes.",
        "no report line",
        "no estimate disclaimer",
        "`Fix mode is finished.` appears only once",
    ):
        assert rule in phase3, f"wrap-up rule missing: {rule}"
    assert "except the fix-mode wrap-up" in text, (
        "the three-section and Readiness Score rules must exempt the wrap-up"
    )
    assert "unfinished issues are listed as deferred in **Actions**" not in phase3
    assert "Author-only hits — a manual to-do list" not in text
    assert "When only **one** auto-fixable issue remains, skip" in text, (
        "a lone auto-fixable issue must not get a redundant Fix all option"
    )
    assert "always **\"Fix all" not in text
    assert "Reply with a number" in text, (
        "the auto-fixable menu must end with a numbered-reply prompt"
    )
    assert "`y` / `Y` / `yes`" in text, "consent must accept y/Y/yes, not only 'explicit yes'"
    assert "python wbo.py fix <path> <id> --json" in text
    assert "## Error handling" in text
    # Open-but-unsaved workbook: ask for a path, never export/save/copy it to
    # manufacture a file to analyze (reviewer feedback: check is read-only).
    assert "`no-path`" in text, (
        "error handling must cover an open workbook with no on-disk path"
    )
    assert "File > Save As" in text, (
        "no-path recovery must tell the user to Save As / share a saved path"
    )
    assert re.search(r"[Ee]xport.{0,40}open workbook|open workbook.{0,40}[Ee]xport", text), (
        "SKILL.md must forbid exporting/copying the open workbook to get a file"
    )
    # The workbook name in the agent's context may be an empty Desktop window's
    # default name ("Book1"), so never claim what is open; just name the file.
    assert "Say or imply which workbook is open in Tableau Studio" in text
    assert "``Open `<path>` in Tableau Studio.``" in text
    usage_row = next(
        line for line in text.splitlines() if line.startswith("| `usage`")
    )
    forbidden_row = next(
        line for line in text.splitlines() if line.startswith("| `forbidden-path`")
    )
    assert "`io`" in text and "`unknown-id`" in text
    assert "`not-programmable`" in text
    assert "--in-place" in usage_row, (
        "--out with --in-place is CLI usage, not forbidden-path"
    )
    assert "--in-place" not in forbidden_row
    assert "do not rewrite" in text.lower() or "not rewrite" in text.lower()
    assert "fixMethod" in text
    assert "--check-id" not in text, (
        "SKILL.md must not document --check-id as supported"
    )
    assert "journal older than workbook" in text
    assert "default is rewrite" in text.lower() or "default rewrite" in text.lower()
    assert "stale" in text.lower() or "no longer exists" in text.lower()
    assert "working dir" in text.lower() or "working directory" in text.lower()
    assert "ok: false" in text
    assert "**CLEANUP**" in text or "`CLEANUP`" in text
    assert "symlink" in text.lower()
    assert "Path.resolve" in text


def test_session_working_dir_and_naming():
    text = skill_text()
    # Working directory is per workbook per session, keyed by a random token.
    assert "Session token" in text, (
        "working dir must define a per-session random token"
    )
    assert "<slug>-<token>" in text, (
        "working dir folder must be <slug>-<token>, not bare <slug>"
    )
    assert "per session" in text, "working dir must be scoped per session"
    # New-session-mints-a-new-token rule (so reopening the agent → new folder).
    assert re.search(r"new conversation|earlier session", text), (
        "token rule must tie a new token to a new session"
    )
    # Copy and optimized output naming carry the token; optimized starts at _1.
    assert "_copy_<token>" in text, "working copy must be <name>_copy_<token>"
    assert "_optimized_<token>_<N>" in text, (
        "optimized output must be <name>_optimized_<token>_<N>"
    )
    assert re.search(r"first.{0,40}`_1`|`_1`.{0,40}first|starts at \*\*1\*\*", text), (
        "optimized numbering must start at _1 on the first optimize"
    )
    # Report files carry the token too (shared basename with the folder).
    assert "<slug>-<token>.json" in text, (
        "check reports must be named <slug>-<token>.json/html/md"
    )
    assert "--token" in text, "skill must pass the session token with --token"
    # Check mode announces the exact file it analyzed.
    assert "full path and filename" in text, (
        "check must open by stating the workbook's full path and filename"
    )


def test_chat_reply_keeps_actions_section():
    # W-24599017: Actions was dropped once when the reply was shortened.
    m = OUTPUT_FORMAT_RE.search(skill_text())
    assert m, "SKILL.md must contain an Output Format (Chat) section"
    section = m.group(1)
    positions = []
    for part in CHAT_PARTS:
        bullet = f"\n- {part} —"
        assert bullet in section, f"chat reply must have a {part} part"
        positions.append(section.index(bullet))
    assert positions == sorted(positions), (
        f"chat parts must appear in order: {' → '.join(CHAT_PARTS)}"
    )
    assert "**Summary**, **Issues found**, and **Actions**, even when" in section, (
        "every reply has all three titled sections, even with no issues"
    )
    summary = section[positions[0]:positions[1]]
    assert "title line `**Summary**`" in summary, "Summary must print its title"
    issues = section[positions[1]:positions[2]]
    assert "grouped by severity" in issues, "Issues found must group hits by severity"
    assert "title line `**Issues found**`" in issues, "Issues found must print its title"
    assert "Always show all three groups" in issues and "`No issues found.`" in issues, (
        "an empty severity group must still be listed, saying no issues found"
    )
    group_positions = []
    for group in SEVERITY_GROUPS:
        assert group in issues, f"Issues found must show the severity group {group!r}"
        group_positions.append(issues.index(group))
    assert group_positions == sorted(group_positions), (
        "severity groups must appear in order: Warning, Note, Info"
    )
    assert not re.search(r"- \*\*(Warning|Note|Info)\*\*:", issues), (
        "severity group labels are capitals, not bold"
    )
    # Tag only the exception: most issues are Desktop fixes, so say that once.
    assert "(auto-fixable)" in issues
    assert "never tag an issue \"(fix in Tableau Studio)\"" in issues
    assert "> (fix in Tableau Studio)" not in issues and "detail> (fix in" not in issues, (
        "the Issues found shape must not tag Desktop fixes per line"
    )
    assert "\n  Issues not marked auto-fixable can only be fixed by you, manually in Tableau Studio.\n" in issues, (
        "the Desktop default is stated once, on its own line, after the groups"
    )
    assert "on a line of its own" in issues, "the Readiness Score is its own line"
    score = issues.find("\n  Optimization Readiness Score: ")
    assert score > group_positions[-1], (
        "Issues found ends with the Readiness Score line, after the severity groups"
    )
    actions = section[positions[2]:positions[3]]
    assert "title line `**Actions**`" in actions, "Actions must print its title"
    assert "bulleted list" in actions and "no numbers" in actions, (
        "Actions are bullets; the only numbers in the reply are the closing menu"
    )
    assert "numbered list" not in actions
    assert "`No actions needed.`" in actions, "an empty Actions section keeps its title"
    assert "suggestion" in actions and "effort" in actions, (
        "each Action must give the recommendation and its effort"
    )
    for tag in ("`(low effort)`", "`(medium effort)`", "`(high effort)`"):
        assert tag in actions, f"each Action ends with an effort tag such as {tag}"
    assert re.search(r"never\s+write\s+quick,\s+moderate,\s+or\s+author-effort", actions), (
        "the internal effort labels must not appear in chat"
    )
    assert re.search(r"applied, rejected,\s+or\s+deferred", actions), (
        "fix-mode Actions must say what was applied, rejected, or deferred"
    )
    report = section[positions[3]:positions[4]]
    assert "no title line" in report and "not bold" in report, (
        "Report must be a plain sentence, with no bold title"
    )
    assert "`Analysis report saved to" in report and "Analysis Report" not in report, (
        "the Report sentence must read 'Analysis report saved to', in sentence case"
    )
    assert "`Analysis report saved to `<working-dir>/<slug>-<token>.html`" in report, (
        "the Report sentence gives one path: the HTML report"
    )
    assert "— open" not in report, "do not repeat the folder path before the HTML path"
    assert "`Analysis report saved to `<working-dir>/<slug>-<token>.html` ``" in report, (
        "the Report sentence is just the HTML path"
    )
    assert not re.search(r"`Report saved|Open the report\b", skill_text()), (
        "say 'analysis report', not bare 'report', in the reply wording"
    )
    assert "same folder" not in report, "do not point the user at the .md / .json copies"
    assert "Optimization Readiness Score:" not in report, (
        "the Readiness Score summarizes Issues found, so it lives there, not in Report"
    )
    next_step = section[positions[4]:]
    for line in ("1. Run fix mode", "2. Open the analysis report", "Reply 1 or 2, or N to skip."):
        assert line in next_step, f"check mode must end with the next-step menu line {line!r}"
    assert "No issues can be fixed automatically. Fix mode walks you through" in next_step, (
        "with nothing auto-fixable, check mode still offers fix mode for the manual fixes"
    )
    assert "Open the analysis report? [Y/N]" not in skill_text(), (
        "Run fix mode is always offered; there is no open-report-only prompt"
    )
    assert "Fix mode saves the changes to a copy of the workbook; your original file is not changed." in next_step, (
        "check mode gives the auto-fixable count in one sentence before the menu"
    )
    # Templates the agent copies verbatim must use placeholders, not sample counts.
    assert "<N> issues can be fixed automatically." in next_step
    text = skill_text()
    assert "Fix mode saved <C> copies of the workbook" in text
    assert "Optimization Readiness Score: <n> Warnings, <n> Notes, <n> Info items." in issues
    for pattern in (r"\b\d+ issues? can be fixed", r"saved \d+ copies", r"Score: \d+ Warnings"):
        assert not re.search(pattern, text), f"hard-coded count in a template: {pattern!r}"
    assert "applied to a copy" not in next_step and "one per line" not in next_step, (
        "check mode does not re-list the auto-fixable issues"
    )
    assert "Run fix mode? [Y/N]" not in next_step, (
        "the two-option menu replaces the lone Run fix mode prompt"
    )


def test_chat_overview_is_capped_but_pick_lists_are_full():
    # W-24599017: a complex workbook made the reply too long to read.
    text = skill_text()
    m = OUTPUT_FORMAT_RE.search(text)
    assert m, "SKILL.md must contain an Output Format (Chat) section"
    section = m.group(1)
    issues = section[section.index("\n- **Issues found** —"):section.index("\n- **Actions** —")]
    assert "at most **5** issues per group" in issues, "each severity group shows at most 5"
    assert "`- …and <k> more in the analysis report`" in issues, (
        "hidden issues are counted, not a bare '...', and the count line says where they are"
    )
    assert "auto-fixable issues are always shown" in issues, (
        "every auto-fixable issue stays visible, so the fix menu has no surprises"
    )
    # The footer was four lines; the report pointer now rides on the count line
    # and the clear-checks count is left to the report.
    assert "Open the analysis report to see the full list" not in issues, (
        "no separate report-pointer line; the count line carries it"
    )
    assert "other checks" not in issues, "no clear-checks count line in the chat"
    assert "Do not count the checks that came back" in issues, (
        "the chat does not count the clear checks; the report lists them"
    )
    actions = section[section.index("\n- **Actions** —"):section.index("\n- **Report** —")]
    assert "the same issues" in actions, "Actions lists exactly the issues shown in Issues found"
    assert "`- …and <total> more in the analysis report`" in actions and "very end of the list" in actions, (
        "Actions is one flat list, so hidden issues are counted once, at the end"
    )
    assert "end that group's entries" not in actions, (
        "no per-group count lines in Actions; it has no group titles"
    )
    assert "applies in `fix` mode too" in issues, "the cap applies to the overview in both modes"
    assert re.search(r"Manual to-do list\.\*\*.{0,120}never\s+capped", text, re.S), (
        "the manual to-do list is complete; the user picks from it"
    )
    assert re.search(r"fix menu.{0,80}never\s+capped", text, re.S), (
        "the fix menu lists every auto-fixable issue"
    )


def test_open_report_runs_the_os_opener():
    text = skill_text()
    assert "**Open the analysis report.**" in text, (
        "SKILL.md must define what Open the analysis report does"
    )
    assert '`open "<html>"`' in text, "macOS opens the HTML report with open"
    assert (
        '`powershell -NoProfile -Command "Invoke-Item -LiteralPath \'<html>\'"`' in text
    ), "Windows opens the HTML report with Invoke-Item"
    assert '`cmd /c start "" "<html>"`' not in text, (
        "Git Bash rewrites /c to C:/, so cmd /c start never runs"
    )
    assert "`reports.html`" in text, "only the HTML path from the reports index is opened"


def test_paths_in_chat_are_inline_code():
    # The chat renderer strips file:// links (react-markdown 6 uriTransformer),
    # so a path rendered as a link looks clickable but does nothing. Outside a
    # code span, Markdown eats the backslash in `\.` (C:\...\skills\.build).
    text = skill_text()
    assert "**Paths in chat**" in text, "SKILL.md must define one inline-code path rule"
    assert "as inline code" in text and "never as a markdown link" in text
    assert not re.search(r"path\w* as plain text", text), (
        "plain-text paths lose Windows backslashes before punctuation"
    )
    for line in re.findall(r"^.*<working-dir>/<name>_optimized_.*$", text, re.M):
        if not line.startswith("`--out"):
            assert "`<working-dir>/" in line, f"path in chat template not in backticks: {line}"
    assert "file://" not in text, "do not tell the agent to build file:// links"
    assert not re.search(r"clickable", text, re.I), "paths are not clickable; do not say so"
    assert not re.search(r"\]\((?:/|~)", text), "no markdown link wrapped around a path"


def test_no_body_level_horizontal_rules():
    text = skill_text()
    lines = text.splitlines()
    fence = False
    hr_after_frontmatter = []
    dash_count = 0
    for i, line in enumerate(lines, start=1):
        if line.startswith("```"):
            fence = not fence
            continue
        if line == "---":
            dash_count += 1
            if dash_count > 2 and not fence:
                hr_after_frontmatter.append(i)
    assert dash_count >= 2, "YAML frontmatter must open and close with ---"
    assert not hr_after_frontmatter, (
        f"body-level --- dividers hide sections on macOS Studio: "
        f"lines {hr_after_frontmatter}"
    )


def test_mac_safe_hr_lines_in_every_skill_file():
    # The Mac Studio YAML parser trips on any line that is exactly "---" other
    # than the frontmatter pair, including lines inside code fences, and the
    # same check applies to every file shipped next to SKILL.md.
    skill_hits = HR_LINE_RE.findall(skill_text())
    assert len(skill_hits) == 2, (
        f"SKILL.md must contain exactly 2 '---' lines, found {len(skill_hits)}"
    )
    offenders = []
    for path in sorted(EXPERTISE_DIR.rglob("*")):
        if path.suffix.lower() not in {".py", ".md", ".txt", ".json"} or not path.is_file():
            continue
        if "_parts" in path.parts:
            continue
        found = HR_LINE_RE.findall(path.read_text(encoding="utf-8", errors="replace"))
        if found:
            offenders.append(f"{path.name}: {len(found)}")
    assert not offenders, f"'---' lines found outside SKILL.md frontmatter: {offenders}"


def test_tableau_guidance_stays_corrected():
    text = skill_text()
    assert "no longer help improve query performance" in text, (
        "SKILL.md must carry Tableau's current context-filter guidance"
    )
    assert "2–4" not in text, "sheets-per-dashboard must follow Tableau Help (2–3), not 2–4"
    assert re.search(r"2–3|two or three", text), (
        "sheets-per-dashboard must cite Tableau's 2–3 views guideline"
    )
    assert not re.search(r"`MEDIUM`.{0,80}trimming\s+quick filters", text, re.I), (
        "do not tag quick filters as MEDIUM cleanup"
    )


def test_design_doc_is_marked_non_normative():
    if not DESIGN_DOC.exists():
        return
    text = DESIGN_DOC.read_text()
    assert "non-normative" in text.lower(), (
        "design doc must state it is non-normative background"
    )
    assert "SKILL.md" in text, "design doc must point at SKILL.md as the normative source"


def test_severity_table_matches_wbo():
    """The SKILL.md severity table and wbo.SEVERITY_TABLE must be identical."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import wbo  # noqa: WPS433

    text = skill_text()
    rows = {}
    for line in text.splitlines():
        m = re.match(r"^\| (CRITICAL|HIGH|MEDIUM|CLEANUP) \| (\w+) \| (\w+) \| (\w+) \|$", line)
        if m:
            rows[m.group(1)] = tuple(m.group(2, 3, 4))
    assert rows == wbo.SEVERITY_TABLE, (rows, wbo.SEVERITY_TABLE)
    assert "puts a `severity` field on every" in text


def test_python_catalog_is_complete():
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import wbo  # noqa: WPS433

    ids = [r["id"] for r in wbo.CATALOG]
    assert len(ids) == len(set(ids)), "duplicate catalog ids"
    assert set(NON_PROGRAMMABLE_IDS) <= set(ids)
    programmable = [r for r in wbo.CATALOG if r["programmable"]]
    not_prog = [r for r in wbo.CATALOG if not r["programmable"]]
    assert [r["id"] for r in programmable] == list(wbo.CHECK_IDS)
    assert set(wbo.DETECTORS) == set(wbo.CHECK_IDS)
    extra_detectors = set(wbo.DETECTORS) - set(wbo.CHECK_IDS)
    missing_detectors = set(wbo.CHECK_IDS) - set(wbo.DETECTORS)
    assert not extra_detectors and not missing_detectors, (
        extra_detectors,
        missing_detectors,
    )
    for rec in not_prog:
        assert rec["id"] not in wbo.DETECTORS, rec["id"]
        assert rec["fixMethod"] == "author-only", rec["id"]
    assert tuple(wbo.MECHANICAL_FIX_IDS) == (
        "hide-unused-fields",
        "fixed-dashboard-size",
    )
    for rec in wbo.CATALOG:
        assert rec["impact"] in ALLOWED_IMPACT, (rec["id"], rec["impact"])
        assert rec["priority"] in {"CRITICAL", "HIGH", "MEDIUM", "CLEANUP"}, rec["id"]
        assert rec["fixMethod"] in {"mechanical", "author-only"}, rec["id"]
        assert rec["detectability"] in {"S", "P", "R", "S/R", "P/R"}, rec["id"]
        assert rec["title"], rec["id"]
        assert rec["title"] != rec["id"], (
            f"{rec['id']}: title must be human-readable, not the raw id"
        )
        assert rec["summary"]
        assert rec["detail"]
        assert isinstance(rec["sources"], list)
    assert wbo.CATALOG_BY_ID["count-over-countd"]["priority"] == "MEDIUM"
    assert wbo.CATALOG_BY_ID["hide-unused-fields"]["priority"] == "CLEANUP"
    assert wbo.CATALOG_BY_ID["reduce-mark-count"]["priority"] == "HIGH"
    for cid in (
        "hide-unused-fields",
        "default-field-properties",
        "prefer-tiled-over-floating",
        "keep-tooltips-simple",
        "minimize-image-sizes",
        "prefer-transparent-pngs",
        "upgrade-tableau-version",
    ):
        assert wbo.CATALOG_BY_ID[cid]["priority"] == "CLEANUP", cid
    for cid in FORMULA_IDS:
        assert wbo.CATALOG_BY_ID[cid]["fixMethod"] == "author-only"
        assert wbo.CATALOG_BY_ID[cid]["programmable"] is True
    known_labels = set(wbo.TABLEAU_LINKS) | set(wbo.PLAIN_SOURCES)
    for rec in wbo.CATALOG:
        for lab in rec["source_keys"]:
            assert lab in known_labels, (rec["id"], lab)
        if rec["source_keys"] and set(rec["source_keys"]).issubset(wbo.PLAIN_SOURCES):
            assert "help.tableau.com" not in wbo._source_links(rec["id"]), rec["id"]
    assert wbo.SCHEMA_VERSION == 3


def main() -> int:
    """Run every test_* function in this file (discovered, not hand-listed)."""
    tests = [
        fn
        for name, fn in list(globals().items())
        if name.startswith("test_") and inspect.isfunction(fn)
    ]
    failed = 0
    for test in tests:
        try:
            test()
            print(f"PASS  {test.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL  {test.__name__}: {exc}")
        except Exception as exc:
            failed += 1
            print(f"ERROR {test.__name__}: {type(exc).__name__}: {exc}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
