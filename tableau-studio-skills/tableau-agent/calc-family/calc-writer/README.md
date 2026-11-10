# Calc Writer

Authors one new Tableau calculated field per run from a natural-language ask. Every authored calc passes an 8-check Validation Gate before delivery. If you ask for several calcs in one message, it asks whether you'd like them one-at-a-time (default) or handled sequentially in this same run before starting.

**Example:** You ask "write me a calc that flags orders above $500." The skill classifies the ask as a Boolean row-level calc, looks up the comparison operator in the function library, authors `[Sales] > 500`, runs the Validation Gate (R-TYPE, R-AGG, R-BOOL all check out), verifies on a scratch worksheet, and hands you back the calc name plus a `calc_write_handoff/1` YAML payload for downstream peers.

## What it does

Takes a natural-language ask, classifies the calc type (row-level, aggregate, LOD, table calc), looks up function signatures from a locked reference library (never guessed), authors via `author-calc`, verifies via `get-summary-data`, and passes an 8-check Validation Gate before delivery.

## When to use it

- "Write me a calc for revenue by customer."
- "Author a Boolean flag for orders over $500."
- "I need a calc that computes profit margin."
- "Create a rolling 90-day average sales calc."
- "Make a calc for days between order and ship date."

## When NOT to use it

- Debug a broken calc → use `calc-debugger`.
- Speed up a slow calc → use `calc-optimizer`.
- Translate SQL, Excel, or DAX to Tableau → use `calc-translator`.
- Style/naming audit → use `calc-linter`.
- List or catalog existing calcs → use `calc-inventory`.
- Ambiguous calc question → use `calc-orchestrator`.
- Create a parameter, set, or hierarchy → Desktop UI (out of scope).
- Build a dashboard or worksheet → `worksheet-builder` or `viz-planner`.

## What you get back

- The authored calc's name and formula.
- Classification (row-level, aggregate, LOD FIXED/INCLUDE/EXCLUDE, table calc).
- Verification result from a scratch worksheet (or a sample-size caveat if under 1,000 rows).
- Validation Gate summary (all 8 checks passed).
- `calc_write_handoff/1` YAML for downstream calc-family peers.
