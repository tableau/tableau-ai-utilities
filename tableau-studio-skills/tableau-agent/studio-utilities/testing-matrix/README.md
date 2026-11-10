# Testing Matrix

Builds and guides a testing matrix for another Tableau Studio agent skill. Inspects the target skill's SKILL.md and references, derives 20-25 prompts across 5-8 sequences that exercise its triggers, hard constraints, error handling, and platform limitations, then walks you through each sequence step by step in Tableau Studio. On failure, proposes a specific fix, applies it to the target skill's files with your approval, and re-runs the failed prompt to confirm resolution.

**Example:** "Test my data-quality-review skill" produces `data-quality-review_testing_matrix.md` and an empty results file in your Downloads folder, walks you through 6 sequences (Trigger Precision, Domain Discipline, Error Handling, Composability, Platform-Gap Handling, Output-Format Discipline) with 22 exact-string prompts to paste into Desktop, logs pass/fail/N/A per row, proposes canonical fixes on failures, and hands off to skill-grader-desktop at the end so you can see the score movement.

***

## What it does

Turns a skill into an executable QA checklist. Skill-grader-desktop tells you what a skill claims about its own behavior; this skill tests whether the claims hold up when a human paste-tester runs real prompts inside Tableau Studio.

Every prompt in the matrix maps to something the target skill actually declares — a trigger phrase, a hard constraint, an error handling row, a platform limitation. If a prompt can't be traced back to a claim in the skill file, it gets cut. No fabricated tests.

When a test row fails, Testing Matrix matches the failure against `skill-expertise/fix_patterns.md`, shows you the specific before/after snippet, cites the file and line range, and waits for your explicit "yes" or "apply" per fix. Never batch-applies. Never applies silently. After the fix lands, the failed prompt gets re-run and the result logged.

Capped at 20-25 prompts across 5-8 sequences, 4-hour total tester budget. If the target skill has more surface area than fits, priority comes from the skill-grader-desktop report (lowest-scoring criteria first) or, if no grader ran, from the target skill's own hard-constraint ordering. Untested areas get named in a "Not Covered This Run" section.

## When to use it

- "Test my skill before I ship it"
- "Build a QA plan for this desktop skill"
- "I just graded this skill — verify the claims actually hold"
- "Walk me through validating this skill against a real workbook"
- "Regression-test this skill after my last edit"

## When NOT to use it

- Not for grading a skill's effectiveness (use skill-grader-desktop first; Testing Matrix consumes its report as priority signal)
- Not for fixing a live Tableau workbook (use authoring skills; Testing Matrix treats your workbook as a read-only test fixture)
- Not for debugging a single failing skill run in isolation (that's ad-hoc troubleshooting, not matrix work)
- Not for testing multiple skills interleaved. One target skill per run.
- Not for building a custom test workbook. Testing Matrix uses Superstore or a workbook you already own; building fixtures is outside its capability.
- Not for skills below the size floor (fewer than 3 hard constraints, no error-handling table, fewer than 10 workflow lines). Testing that thin produces noise, not signal. Flesh out the skill first.

## How to trigger it

- "Build a testing matrix"
- "Test this skill"
- "QA plan for this desktop skill"
- "Testing matrix"
- "Test my skill"
- Automatically offered after skill-grader-desktop finishes

## What you'll need

- The target skill's SKILL.md accessible (either as a folder path or pasted directly)
- Tableau Studio with the agent active
- A workbook to test against — Superstore by default, or one you already own. Testing Matrix asks which before Phase 0 begins.
- The MCP tools Testing Matrix uses: `Read`, `Write`, `Edit`, and occasionally `get-workbook-inventory` / `list-worksheets` / `list-dashboards` for fixture-shape verification
- A Downloads folder (or a location you specify) writable for the two output files
- Ideally, a skill-grader-desktop report from earlier in the session. If present, Testing Matrix orders sequences by weighted-criteria score (lowest first) so the time budget hits the weakest surface.

## Example walkthrough

**Input:** "Test my data-scribe skill. I have a skill-grader-desktop report from earlier."

**Output (Phase 3, matrix file written):**

```
data-scribe_testing_matrix.md written to Downloads.

Setup
  Workbook: Superstore
  Estimated time: 100 minutes (~4.5 min per prompt including logging)
  Grader-informed priority: yes, based on report

Sequences (6 total, 22 prompts)
  1. Trigger Precision (4 prompts)
     Positive: "document this datasource", "metric dictionary",
     "I inherited this workbook, what's in it".
     Negative: "check data quality" (should route to
     data-quality-review, not data-scribe).

  2. Hard-Constraint Discipline (4 prompts)
     Tests: read-only for calcs (never author-calc), scratch-sheet
     cleanup, one-datasource-per-run, blocking-modal awareness.

  3. Error Handling (4 prompts)
     Tests: no workbook detected, list-available-fields empty,
     scratch-sheet deletion failure, output path unwritable.

  4. Platform-Gap Handling (3 prompts)
     Tests: hard-stop on parameter-referencing calc datasources,
     Sets/Hierarchies not scanned caveat, dashboard-bound sheet
     XML gap for calc formula fallback.

  5. Output-Format Discipline (4 prompts)
     Tests: .md vs .txt format ask (no silent default), calc
     dependency ordering, family-level summary trigger on 300+
     fields, Update vs Regenerate on existing dictionary.

  6. Composability (3 prompts)
     Tests: proactive offer after new datasource, handoff to
     data-quality-review for "clean" questions.

Not Covered This Run
  - Very-large-datasource (>1M rows) sampling behavior
  - Cloud connection timeout recovery
  - Multi-table blend vs relationship distinction

Ready to start Sequence 1?
```

Then walks you through each sequence: exact prompts, prep steps, pass criteria, on-fail hooks. Between sequences it offers a pause. On failure, it proposes a fix from `fix_patterns.md`, waits for your explicit yes/no, applies with `Edit`, re-runs, and logs.

## What you get back

- **Two files in your Downloads folder** (or wherever you specify): `{target-skill-name}_testing_matrix.md` (the plan) and `{target-skill-name}_testing_results.md` (a row-tracking table you fill in as you go).
- **5-8 sequences drawn from the universal library:** Trigger Precision, Domain Discipline, Error Handling, Composability are always in scope. Read-Only Mutation Refusal, Platform-Gap Handling, Output-Format Discipline, and Reproducibility are conditional on whether the target skill declares them.
- **20-25 exact-string prompts** you paste verbatim into Tableau Studio. Only `{sheet-name}` and `{dashboard-name}` placeholders when you need to substitute a real object from your workbook.
- **Prep instructions** immediately before every prompt that needs specific workbook state. When no prep is needed, it says "No prep. Paste the prompt" rather than implying prep silently.
- **Grader-informed priority ordering** when a skill-grader-desktop report exists in the session. Lowest-scoring criteria tested first, so your time budget hits the weakest surface.
- **Environment-dependent rows labeled up front.** Platform-reliability gaps, workbook-specific fixtures, and Tableau version behaviors that may not fire in every environment are marked "may not observe; N/A is a valid outcome" so you don't chase phantom fails.
- **On-fail flow** for every row: diagnose against `fix_patterns.md`, show the specific before/after snippet with file and line range, wait for explicit per-fix approval, apply, re-run, log.
- **Scoring rubric:** 90%+ pass = ready; 75-89% = solid, iterate; <75% = needs work. Any FAIL on release-blocking rows (mutation refusal, hard-constraint violation) blocks release regardless of overall pass rate.
- **Handoff back to skill-grader-desktop** at the end to confirm score movement from applied fixes.

## Limitations

- **One target skill per run.** Interleaving sequences from two target skills breaks the budget cap, the fix-pattern approval trail, and the pass/fail tally. Run each as its own complete cycle.
- **Never builds custom test workbooks.** Superstore or your own workbook. Always. Building fixtures is outside Testing Matrix's capability.
- **Never mutates your workbook.** Your workbook is a read-only test fixture. The only files Testing Matrix writes are the two matrix/results files and, on approval, the target skill's own SKILL.md/references.
- **Fixes only apply to files the target skill owns.** If a diagnosed fix would touch a file the target skill doesn't own, Testing Matrix refuses the auto-apply and hands off to you or the relevant authoring skill.
- **Every fix needs its own explicit approval.** Even if you approved a fix earlier in the session, each new fix requires a fresh yes. No batching.
- **Novel failures with no `fix_patterns.md` match are logged, not improvised.** Testing Matrix will diagnose plainly and log as "unresolved, no canonical fix pattern" — it won't invent a fix. Novel patterns should be added to `fix_patterns.md` deliberately.
- **Grader dependency is soft.** Testing Matrix works without a prior skill-grader-desktop report, but sequence prioritization is less targeted. The matrix header notes when it's running blind.
- **Size floor.** Skills below 3 hard constraints, with no error handling table, and fewer than 10 workflow lines get declined for full matrices. A minimal 2-sequence smoke test (Trigger Precision + Composability) is available if you still want to proceed.

## Troubleshooting

- **"A prompt returned nothing."** Retry once. If still nothing, log as N/A with a note. Testing Matrix does not assume failure without your confirmation.
- **"The fix from `fix_patterns.md` didn't resolve the failure."** Testing Matrix logs FAIL (fix insufficient), notes the new failure signature distinctly from the original, and flags the mismatch as a candidate for reviewing that pattern entry. It won't assume the pattern is simply "slow to take effect."
- **"I want to skip a sequence."** Say so; Testing Matrix moves to the next sequence and notes the skipped one under "Not Covered This Run" in the results file.
- **"I ran out of time mid-run."** Testing Matrix offers to pause and resume. The results file is saved mid-flight so nothing is lost.
- **"The tester asked for a custom workbook."** Declined. Testing Matrix suggests Superstore or a workbook you already own.
- **"A platform-gap row logged N/A. Is that a fail?"** No. Environment-dependent rows are labeled up front — N/A is a valid outcome by design.
- **"My workbook isn't open."** Testing Matrix restarts Phase 0 once the workbook is open. It won't run sequences against a disconnected fixture.
- **"The Downloads folder isn't writable."** Testing Matrix asks for an alternate save location rather than partial-writing.

## Support

File issues in the same channel you use for other Tableau Studio skill feedback. Include the target skill name, the sequence that surfaced the issue, the failing prompt, and the fix pattern (if any) Testing Matrix proposed.
