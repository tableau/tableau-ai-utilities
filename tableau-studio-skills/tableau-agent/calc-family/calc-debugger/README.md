# Calc Debugger

Diagnoses one broken Tableau calculated field per run and proposes a corrected version. Every fix passes an 8-check Validation Gate before delivery. If you ask about several broken calcs in one message, it asks whether you'd like them one-at-a-time (default) or handled sequentially in this same run before starting.

**Example:** You paste a calc that's returning NULL for some rows. The skill reads the formula, classifies the failure against the error-pattern catalog (E-NULL), proposes a corrected version wrapped in `ZN([expression])` or `IFNULL([expression], fallback)`, re-authors as `[original name] Fixed`, runs the Validation Gate (R-NULL, R-TYPE, R-AGG all check out), verifies on a scratch worksheet, and hands you back the fix plus a `calc_debug_handoff/1` YAML payload for downstream peers.

## What it does

Takes a broken calc, reads its actual formula, classifies the failure against a locked 9-pattern error catalog (E-NULL through E-CIRC), proposes a corrected version, re-authors via `author-calc`, verifies via `get-summary-data`, and passes the same 8-check Validation Gate as calc-writer before delivery.

## When to use it

- "Debug this calc — it returns NULL for some customers."
- "Why is my profit margin calc showing negative values?"
- "This calc errors on `SUM([Sales]) / [Rows]` — fix it."
- "My LOD returns the wrong grain, help me fix it."
- "This calc had a syntax error after I edited it."

## When NOT to use it

- Write a brand-new calc → use `calc-writer`.
- Speed up a working calc → use `calc-optimizer`.
- Translate SQL, Excel, or DAX to Tableau → use `calc-translator`.
- Style/naming audit → use `calc-linter`.
- List or catalog existing calcs → use `calc-inventory`.
- Ambiguous calc question → use `calc-orchestrator`.
- Grain/join model issue where the calc is a symptom → use `join-and-relationship-advisor` first, then come back for the calc fix.

## What you get back

- The original broken formula.
- The diagnosed error pattern (E-NULL, E-SYNTAX, E-TYPE, E-AGG, E-LOD, E-FIELD, E-PARAM, E-GRAIN, or E-CIRC) with root cause.
- The proposed fix formula.
- The new calc's name (default: `[original name] Fixed`; opt in to overwrite).
- Verification result from a scratch worksheet (or a sample-size caveat if under 1,000 rows).
- Validation Gate summary (all 8 checks passed).
- `calc_debug_handoff/1` YAML for downstream calc-family peers.
