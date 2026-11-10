# Parameters — Known Gaps and Safe Path

**Status: weak spot on this environment.** `author-parameter` has a confirmed reliability problem on this machine: it stages the new parameter into a side file (`param-stage-N.twb`) but the automatic reopen step fails (`Failed to inspect Tableau Studio process: spawn ps ENOENT` — the harness shells out to a `ps` binary that doesn't exist on Windows). The parameter never merges into the live workbook, and a subsequent `resolve-field`/caption lookup on it returns not-found even though the tool reported success.

## What NOT to do

- Do not blindly retry `author-parameter` after a failure on this machine. Each retry stages another orphaned `param-stage-N.twb` file under `.../My Tableau Repository/Workbooks/` without fixing the underlying reopen bug — it just accumulates junk files and burns turns.
- Do not report the parameter as created because the tool call "succeeded" — the reopen step is a separate, silent failure point. Verify with `resolve-field` (or `list-available-fields`) after the call before telling the user it's ready to use.

## Safe path

1. Call `author-parameter` once.
2. Verify it actually landed: `resolve-field` for the parameter's caption, or check `list-available-fields`.
3. If it's not found, stop — do not retry. Tell the user plainly: "Parameter creation didn't merge into the live workbook. Can you check that Tableau Studio is open and responsive, or apply it manually via the Parameters pane (right-click → Create Parameter)?" Wait for their confirmation before continuing.
4. Once the user confirms Desktop is responsive (or has applied it manually), proceed with referencing the parameter in calcs as normal.

## Manual fallback (Desktop UI)

If `author-parameter` is unreliable in this session, the fastest unblock is the native UI path: Data pane → dropdown arrow → **Create Parameter...** → set name/type/default/allowable values → OK. Then reference `[Parameter Name]` in any calc via `author-calc` as usual — parameter *consumption* in formulas is unaffected by this bug, only parameter *creation* through the tool is.

## Confirmed recurrence

Reproduced again 2026-08-03 on a plain string-type parameter (`Measure Selector`, values Sales/Profit, intended to drive a toggle between two measures on a bar chart) — same `param-stage-N.twb` + `spawn ps ENOENT` signature as the original report. This is a stable, repeatable environment bug, not a one-off — treat the Safe Path above as the default flow for ANY parameter-creation ask on this machine, not just a fallback for occasional failures. When it fails, stop after step 2's verification and offer the user a choice: check Desktop's responsiveness, or apply the parameter manually and continue once confirmed. Don't attempt workarounds (e.g. faking the toggle with a different mechanism) without asking first — the user may prefer to just create it manually since that path works fine.

## Related

- Project memory: `project_author_parameter_reopen_broken` — the specific error signature and machine context.
- `number_formatting.md` — a similar "don't guess, verify, escalate to manual" discipline applies there for a different weak spot.
