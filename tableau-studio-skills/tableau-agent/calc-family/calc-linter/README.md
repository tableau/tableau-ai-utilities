# Calc Linter

Lints one existing Tableau calculated field per run against a locked 12-rule house-style catalog. Reports violations with severity plus rationale by default. Rewrites only on explicit user opt-in, and every rewrite passes an 8-check Validation Gate plus a mandatory R-EQUIV-01 runtime equivalence check before delivery. Style-only scope. Value-preserving.

**Example:** You have a calc named `  sales by  region  ` (leading/trailing whitespace, double spaces, lowercase). The skill flags S-NAME-02 (Title Case + whitespace violation) as `severity: error`, proposes `Sales By Region`, and on your opt-in authors `[Sales By Region] Clean`, verifies the rewrite returns identical values on a scratch worksheet, and hands you back the linted calc plus a `calc_lint_handoff/1` YAML with the full violations list, trade-offs, and equivalence confirmation.

## What it does

Consumes a `calc_write_handoff/1` / `calc_debug_handoff/1` / `calc_optimize_handoff/1` payload from any upstream calc-family peer, or fires standalone on a lint ask. Reads the original formula, runs it against the locked 12-rule catalog, groups violations by severity (error / warning / info), and delivers a report-only verdict by default. On explicit user opt-in, generates rewrite candidates, filters them through the V-gate, authors the consolidated rewrite via `author-calc`, verifies runtime equivalence, and emits `calc_lint_handoff/1`.

## When to use it

Fires on "lint this calc," "check this calc's style," "rewrite for readability," "does this calc follow our house style," "check my calc naming," "style-check this calc," or when an upstream handoff arrives and the user says "now lint it."

Do NOT invoke for writing new calcs (`calc-writer`), fixing broken/wrong-value calcs (`calc-debugger`), performance rewrites (`calc-optimizer`), cataloging calcs across a data source (`calc-inventory`), dashboard-level style tuning (`workbook-auditor`), or model/relationship naming (`join-and-relationship-advisor`).

## What makes this skill distinctive

- **Locked 12-rule catalog with severity tiers.** Every violation cites a stable rule ID (S-NAME-01 through S-FORMAT-03) plus severity (error / warning / info). Two lint runs on the same calc produce the same violation list in the same order.
- **Report-mode default.** "Lint this calc" alone triggers report-only. Rewriting requires an explicit opt-in phrase ("rewrite it to match" or "fix the style"). Never silently modifies a user's calc.
- **Mandatory R-EQUIV-01 on every rewrite** — even for cosmetic edits like whitespace, indentation, or comments. Belt-and-braces defense against accidental formula corruption. Same fail-open pattern as calc-optimizer.
- **Value-semantics traps documented explicitly.** IF-to-CASE conversion, branch reordering, AND/OR reordering, ZN/IFNULL stripping, and boolean simplification are all listed as things linter must NEVER do without R-EQUIV-01, since they can silently change NULL propagation or short-circuit evaluation.
- **Clean verdict is a real deliverable.** When no violations surface, the skill delivers an explicit "clean" verdict with the full catalog scope documented. Same contract shape as calc-optimizer's "already optimal."
- **Runtime-resolved derivation prefixes.** Uses the calc's actual AGG-flag via `list-available-fields`/`resolve-field`. Never string-matches the formula.

## Handoff contract

Emits `calc_lint_handoff/1` unprompted after every delivery, including clean verdicts and report-only runs. Required non-blank fields: `violations` (list; may be empty), `rewritten` (true/false), `verified_equivalent` (or `not_applicable`), `overwrites_original`, `clean_verdict`.

Downstream consumers: calc-inventory (catalog-wide style scorecard), workbook-auditor (dashboard-level style rollup).

## Hard constraints in force

- HC#1: single-calc-per-run default; multi-calc requires opt-in clarifier.
- HC#2: value-preserving; every rewrite verified at runtime via R-EQUIV-01.
- HC#3: locked 12-rule catalog is the rule authority.
- HC#5: no field, parameter, set, or hierarchy fabrication.
- HC#8: 8-check V-gate plus R-EQUIV-01 with fail-open on double failure.
- HC#10: style-only; correctness routes to calc-debugger, perf routes to calc-optimizer.
- HC#11: report-mode default; rewrite requires explicit opt-in.
- HC#12: overwrite discipline; default is new calc `[original name] Clean`, overwrite requires explicit opt-in that user pressure never waives.

Full spec in `SKILL.md`. House-Style Catalog in `skill-expertise/style_catalog.md`. Validation Gate in `skill-expertise/validation_gate.md`. Handoff schema in `skill-expertise/handoff_schema.md`. Function library in `skill-expertise/` (`INDEX.md` plus one file per function category).
