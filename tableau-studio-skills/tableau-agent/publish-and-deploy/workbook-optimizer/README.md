# Workbook Optimizer

Scans a Tableau workbook file (.twb or .twbx) for load-time performance issues, walks a locked catalog of 50+ known slowdowns, and applies safe mechanical fixes with your consent. By default it writes to a copy and leaves your original untouched.

**Example:** "Optimize this workbook" on a slow dashboard produces a prioritized list of Warnings, Notes, and Info items, plus an optional fix loop that swaps in cached dashboard sizing or hides unused fields without touching the original file.

---

## What it does

Runs three modes: `stats` (workbook tree, object counts and size warnings; it does not walk the catalog), `check` (full read-only performance audit against the catalog), and `fix` (mechanical fixes applied to a copy after you say yes, either one at a time or all auto-fixable issues together). Every finding cites a specific rule with a Tableau Help link where applicable, and every fix is validated before it counts as applied.

## When to use it

- "I need to know why this dashboard loads slowly"
- "I want a checklist of performance issues in my workbook"
- "I have a workbook heading to Server or Cloud and need to catch performance problems first"
- "I want to see which calcs, filters, or dashboard settings are dragging things down"
- "I have redundant calculated fields and want them flagged"

## When NOT to use it

- Not for rewriting a single calc for speed (use calc-optimizer)
- Not for slow extract refreshes or oversized extracts (use extract-optimizer)
- Not for pre-publish naming, titles, or hygiene checks (use publish-readiness)
- Not for data-correctness issues like nulls, duplicates, or outliers (use data-quality-review)
- Not for chart or dashboard design choices (use viz-planner)
- Not for tracking what changed in a workbook over time (use workbook-auditor)
- Not for building or editing workbooks in Tableau Studio directly (use the built-in Studio authoring skill, tableau-desktop-authoring)

## How to trigger it

- "optimize this workbook"
- "why is this workbook slow"
- "speed this up"
- "performance review"
- "check for redundant calcs"
- "show me stats on this workbook"
- "workbook optimizer"

## What you'll need

- Python 3.9 or later on PATH. The CLI lives in `skill-expertise/`: run `python wbo.py` (or `python3 wbo.py`) from that folder. The `./wbo.py` shebang path is Unix-only.
- A .twb or .twbx file on disk (path can be relative or absolute)
- For `fix` mode: write access to the folder where the skill saves its working copy and optimized copies

## Example walkthrough

**Input:** "optimize this workbook" pointed at `Sales_Q3.twbx`

**Output:**

```
Checking `/Users/you/Documents/Sales_Q3.twbx`

**Summary**

Two things mostly slow this workbook down: the Sales dashboard uses an automatic size, and seven filter cards each run a query.

**Issues found**

- WARNING: a significant load-time risk; address it.
  - Set a fixed dashboard size — Sales dashboard re-renders on every request (auto-fixable)
  - Reduce the number of shown filter cards — 7 filter cards on Sales dashboard
- NOTE: worth fixing, but a lower risk or a smaller payoff. Often optional cleanup.
  - Hide unused fields — 12 unused fields in the Orders data source (auto-fixable)
- INFO: minor or advisory. Low impact, usually housekeeping.
  - No issues found.

Issues not marked auto-fixable can only be fixed by you, manually in Tableau Studio.

Optimization Readiness Score: 2 Warnings, 1 Notes, 0 Info items. Recommend addressing Warnings, especially any COUNTD / live-connection combination.

**Actions**

- Set a fixed dashboard size — fixed-size dashboards can be cached (low effort)
- Reduce the number of shown filter cards — prefer actions on busy dashboards (high effort)
- Hide unused fields — hide them so extracts and queries drop them (low effort)

Analysis report saved to `<working-dir>/sales-q3-a1b2c3.html`

2 issues can be fixed automatically. Fix mode saves the changes to a copy of the workbook; your original file is not changed.

1. Run fix mode
2. Open the analysis report
Reply 1 or 2, or N to skip.
```

`<working-dir>` is a per-session folder, `.build/workbook-optimizer/<slug>-<token>/`, under the Tableau Agent skills folder. The skill writes a journal at `.wbo/perf-plan-sales-q3.md`, outside that folder.

Choosing **Run fix mode** starts fix mode. After one yes to create a working copy (`Sales_Q3_copy_a1b2c3.twbx`), the skill offers a numbered menu: **Fix all auto-fixable issues** (when two or more remain), then each auto-fixable issue, then **Fix issues manually**. Each applied fix is saved as `<working-dir>/Sales_Q3_optimized_a1b2c3_<N>.twbx`, numbered from `_1`. `Sales_Q3.twbx` itself is not changed.

## What you get back

- Issues grouped by severity (Warning, Note, Info), most severe priority first (CRITICAL, HIGH, MEDIUM, CLEANUP), plus a recommended action for each
- A journal file (`.wbo/perf-plan-<slug>.md`) with the full catalog walk, recommendations, and status
- An Optimization Readiness Score summary line ("N Warnings, N Notes, N Info items")
- An analysis report (HTML, with markdown and JSON copies) saved in the working folder, which you can send to a stakeholder
- For `fix` mode: one `<name>_optimized_<token>_<N>.twbx` copy per applied fix, with the original untouched

## Limitations

- Findings are signals, not measurements. Recommend Performance Recorder if you need to confirm real query or render latency.
- Formula comparison is textual (whitespace-normalized). Two calcs with the same effective logic but different variable names will not match.
- Some rules (mark count, source bottlenecks) cannot be checked from the file and appear as advice rather than mechanical fixes. The Tableau version check only reports the workbook's version.
- When fix mode saves two or more optimized copies, the agent asks whether to keep only the final copy or keep all (reply 1 or 2). It deletes nothing without your reply and never renames or deletes your original. The `_optimized_<token>_<N>.twbx` names and this cleanup question belong to the agent. If you run `wbo.py fix` yourself without `--out`, it writes `<name>-optimized.twbx` next to the workbook, and nothing is cleaned up for you.
- Automatic fixes edit the workbook XML with text patterns. If a fix would produce XML that is not well-formed, `wbo.py` writes nothing and reports `invalid-output`. Fields whose names contain `&` or `'` may be skipped by the hide-unused-fields fix.
- The PC + Tableau Studio combined workflow is not yet verified.

## Troubleshooting

- **"I asked to fix a duplicate calc and nothing changed"** then that is expected: `consolidate-duplicate-calcs` is reported as skipped (`author-only`) because formula rewrites are out of scope. Consolidate the calcs in Tableau Studio, or use calc-optimizer for a single calc. An `unknown-id` error means the id is not in the catalog.
- **"malformed XML" or "bad ZIP"** then the .twb or .twbx file is corrupt. Save a fresh copy from Tableau Studio and re-run.
- **"the fix landed next to a symlink, not the real file"** then update to v1.1; `Path.resolve` now runs before computing the sibling path.
- **"I want to fix everything at once"** then choose **Fix all auto-fixable issues** in fix mode (shown when two or more remain). The CLI equivalent is `wbo.py fix <path> --all`. A bare `wbo.py fix <path>` with no id and no `--all` changes nothing and returns a usage error.
- **"the fix was skipped: invalid-output"** then the automatic edit would have produced broken XML, so nothing was written and your workbook is unchanged. Make that change manually in Tableau Studio.
- **"the workbook lives under training-data/"** then `check` and `stats` read it in place, but `fix` refuses to write there; copy it to a working directory first.

## Version / changelog

- 2026-10-29: the Python CLI and its tests moved from `scripts/` to `skill-expertise/`; run `wbo.py` from there.
- 2026-10-28: fixed `hide-unused-fields` corrupting the workbook XML when a column attribute contains `>`; added the `invalid-output` error, which blocks any fix that would write malformed XML.
- v1.1 (2026-09-11) then post-blocker fix: symlink resolution in `default_out_path`, catalog moved to `wbo.py` (`list check` command), matrix rows corrected for consolidate-duplicate-calcs and count-over-countd severity.
- v1.0 (2026-09-08) then initial release. Three-mode CLI, 50+ rule catalog, journal-based workflow, consent before any fix.

## Support

Owner: Greeshma Vijayakumar (Tableau Studio agent skills team). Developer: Hung Dang. File issues or questions with Greeshma.
