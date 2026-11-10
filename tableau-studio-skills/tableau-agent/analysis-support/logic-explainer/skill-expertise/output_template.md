# Logic Explainer — Long-Form Template

Used only when the user asks for the full breakdown (chat or file). Order
sections by reading priority: what you see first on the view, then what
shapes it, then what drives it, then how it connects to other sheets.

```
# [Sheet or Dashboard Name] — Construction Logic

## Summary
One paragraph: what this is built to show/do and the overall approach.

## What You See
Mark type, Rows/Cols fields, key encodings (color/size/text) and why each
was chosen for this view.

## What Shapes the Scope
Filters and parameters that narrow or reshape the data before it's
visualized. For each: what it filters, whether it is **Visible** (quick
filter card, dashboard action target, parameter control, legend-based
filter) or **Hidden** (context filter, data source filter, extract filter,
hardcoded True/False gate), and why (e.g. "Date filter fixed to trailing
12 months — keeps the trend chart from diluting with multi-year history").
**A dedicated Hidden Filters subsection is mandatory**, listing each
hidden filter with what it excludes, or stating "No hidden filters" when
none exist. Silence on hidden filters is not permitted.

## What Drives the Metric
Calculated fields, LODs, table calcs, sets — in dependency order (leaf
calcs first). For each: the formula, a plain-English translation, and the
WHY (what problem it solves for this view specifically).
Tag any non-trivial inference with `[Confidence: High]` (name + idiom + formula agree), `[Confidence: Medium]` (one signal), or `[Confidence: Low]` (no signals — closer to a mechanical description than a true inference).

## How It Connects (dashboard only)
Actions: source -> target, trigger (select/hover/menu), effect, and why
that wiring likely exists. Dynamic zone visibility rules and their
trigger parameter/condition.

## Notable or Fragile Points
Anything unusual, circular, undocumented, or that looks like it could break
easily (e.g. a filter referencing a field that no longer exists, a calc with
no clear consumer). Flag, don't fix.

## Not Covered This Run
Anything skipped due to scope, tool limitation, or unreadable formula —
state plainly rather than omitting silently.
```
