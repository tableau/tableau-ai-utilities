# Calc Hygiene Scan

Audit every calculated field in a Tableau workbook against a locked 8-rule hygiene catalog. Read-only. Every finding is a manual Desktop-fix instruction plus (for autofixable rules) a handoff signal to calc-linter.

**Example:** "Audit my calcs for hygiene drift."

***

## What it does

Runs 8 rules against every calc: naming convention drift, missing author captions, unused calcs, excessive nesting depth, hardcoded values that should be parameters, deprecated function usage, cross-DS calcs without rationale, and over-reliance on LOD when a simpler pattern works. Tiers findings by severity, emits per-rule routing to calc-linter (autofix) or calc-optimizer (rewrite), and never mutates the workbook.

## When to use it

- "I want a workbook-wide calc hygiene sweep before publish."
- "I need to find unused calcs, hardcoded literals, and deprecated functions."
- "I want to route autofixable issues to calc-linter and rewrite candidates to calc-optimizer."

## When NOT to use it

- Not for explaining a single calc in plain language (route to calc-explainer).
- Not for documenting every calc in detail (route to calc-documenter for the full dictionary).
- Not for calc performance rewrites (route to calc-optimizer).
- Not for applying naming or hygiene fixes (route to calc-linter).
- Not for authoring new calcs from scratch (route to calc-writer).
- Not for diagnosing NULL returns (route to calc-debugger).
- Not for migrating a calc between datasources (route to calc-migrator).

## How to trigger it

- "calc hygiene scan"
- "audit my calcs"
- "check calc quality"
- "calc-hygiene-scan"
- "review my calcs"
- "calc quality audit"
- "find calc issues"

## What you'll need

- Tableau Desktop 2024.3 or later with the MCP agent connected.
- The workbook open with at least one calculated field.
- Optionally: a fresh `calc_documentation/1` handoff from calc-documenter for richer usage data. Without it, the skill falls back to local-extract cleanly.

## Example walkthrough

**Input:** Audit calcs in the currently open Superstore workbook.

**Output:**

```
Calc Hygiene Scan: Superstore
Calcs evaluated: 30 (across 3 datasources)
Findings: 17 Warning, 7 Info, 31 sentinel ("unable to determine")
Autofixable findings routing to calc-linter: 4
Handoff consumed: yes. Stale: no.

Top-5 Warning findings:
  1. [HygieneDeprecated] CH-DEPRECATED-06: uses WINDOW_SUM(SUM([Sales]), -SIZE()+1, 0),
     superseded by RUNNING_SUM() since Tableau 10.5. Desktop fix: replace with
     RUNNING_SUM([Sales]). Autofixable via calc-linter.
  2. [HygieneHardcodedA] CH-HARDCODED-05: literal 0.15 shared with HygieneHardcodedB.
     Desktop fix: create a Discount Rate parameter, replace both literals.
  3. [HygieneNested] CH-NESTING-04: nesting depth 6, exceeds 5-level threshold.
     Route to calc-optimizer for structured rewrite.
  ...

Routing offered: calc-linter (4 autofixable), calc-optimizer (2 rewrites).
Save full report to file? (.md or .txt)
```

## What you get back

- Tier A: compact chat summary with counts, top-5 Warning findings, and routing offers.
- Tier B (opt-in): full report with per-calc detail saved as `.md` or `.txt`.
- A `calc_hygiene_report/1` handoff for downstream consumers (calc-linter, calc-optimizer, workbook-auditor).

## Limitations

- CH-CAPTION-02 emits `"unable to determine"` sentinel on most calcs because `list-available-fields` doesn't expose the Desktop Description field (platform gap). Only in-formula `//` annotations reliably clear the rule.
- CH-NAMING-01 respects cohesive naming families. A cluster of 2 or more calcs sharing a deliberate alt-casing convention (e.g., a PascalCase family) is treated as a valid pattern, not drift.
- CH-DEPRECATED-06 list is a snapshot.
- CH-LOD-OVERUSE-08 detection is heuristic and uses calc-explainer's `explanation_patterns.md` precedence rules.
- `resolve-field` is case-sensitive (platform gap). The skill uses handoff data preferentially to avoid the gap.

## Troubleshooting

- **"Sentinel on 29 of 30 calcs for CH-CAPTION-02."** Expected. The tool can't see Desktop Description text; only in-formula `//` annotations clear the rule. Not a defect.
- **"CH-NAMING-01 fired on my Hygiene* fixtures."** Expected if you have a mixed casing convention across the workbook. Cohesive naming families with 2+ calcs are treated as valid; single-calc outliers fire the rule.
- **"Skill flagged a deprecated function but I know it still works."** The rule flags future risk, not present breakage. Deprecated functions still run today; the fix is planning for a future release.

## Support

File issues in the Tableau Studio Agent Skills repo.
