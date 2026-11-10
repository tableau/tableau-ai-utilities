# House-Style Catalog (Locked, 12 Rules)

Style rule authority for calc-linter. Never invent a new rule or reorder severity mid-run. Every violation delivery cites the specific rule ID plus severity.

Severity tiers:

- **error** — blocks house-style compliance; strongly rewritable.
- **warning** — reduces readability or maintainability; rewritable with care.
- **info** — style preference; report only, rewrite optional.

## Naming Rules (Severity: error)

### S-NAME-01 — Calc name is ≤20 characters

**Rule:** Calculated field names should be ≤20 characters, unless the name inherits a longer parent (e.g., `[Very Long Name] Fast` for a calc-optimizer output on a long-named original). A skill-added suffix (` Clean`, ` Fast`, ` Fixed`) doesn't count toward the 20.

**Rationale:** Long calc names crowd the Data pane and truncate in tooltips/legends. Short, meaningful names improve discoverability.

**Rewrite:** If safely rewritable, propose a shortened name that preserves meaning (e.g., `[Total Sales By Region Fixed Grand Total]` to `[Region Sales]`).

**Worked example:**
- Violation: `[Customer Order Frequency Per Month Rolling]` (43 chars)
- Rewrite: `[Cust Order Freq]` (17 chars)

### S-NAME-02 — Title Case, no whitespace issues

**Rule:** Calc names use Title Case with single spaces between words. No leading/trailing whitespace. No double spaces.

**Rationale:** Consistent capitalization improves scanability. Whitespace issues cause resolution errors.

**Rewrite:** Normalize to Title Case, strip whitespace anomalies.

**Worked example:**
- Violation: `  sales by  region  ` (leading/trailing spaces, lowercase, double space)
- Rewrite: `Sales By Region`

### S-NAME-03 — Not a reserved word or bare function name

**Rule:** Calc names must not shadow Tableau reserved words (`Number of Records`, `Measure Names`, `Measure Values`) or bare function names (`SUM`, `COUNT`, `AVG`).

**Rationale:** Shadowing produces formula-resolution ambiguity that Tableau resolves inconsistently across versions.

**Rewrite:** Suggest a qualified alternative (`Sales Sum` instead of `SUM`).

**Worked example:**
- Violation: `[COUNT]`
- Rewrite: `[Row Count]`

## Structure Rules (Severity: warning)

### S-STRUCT-01 — IF/ELSEIF chains ≤4 branches

**Rule:** Long IF/ELSEIF chains (>4 branches) are hard to read and maintain.

**Rationale:** Deep chains often indicate a missing lookup table or a case where CASE would be more appropriate.

**Rewrite:** Only rewrite to CASE if the original is genuinely equality-only (see Domain-Accuracy Assertions). Otherwise, flag as `severity: warning` without rewriting.

**Worked example:**
- Violation: IF/ELSEIF chain with 7 branches
- Rewrite suggestion: extract to a data-driven lookup or convert to CASE (only if equality-only)

### S-STRUCT-02 — Nested LODs documented

**Rule:** LODs nested deeper than depth 1 must have a leading comment explaining why the nesting is necessary.

**Rationale:** Nested LODs are performance-costly and rarely required. When they are, the intent should be self-documented so future editors don't naively flatten them.

**Rewrite:** Add a leading comment with rationale. Do not attempt to flatten (that's calc-optimizer's job).

**Worked example:**
- Violation: `{FIXED [Region] : AVG({FIXED [Order ID] : SUM([Sales])})}` with no comment
- Rewrite: prepend `// Nested for per-order average within region; flattening would change values (see calc-optimizer test 4)`

### S-STRUCT-03 — Table calcs document partitioning

**Rule:** Table calcs must have a leading comment explaining the partitioning/addressing (Compute Using scope).

**Rationale:** Table calc behavior depends entirely on view scope; without a comment, the calc is unreadable outside its original context.

**Rewrite:** Add leading comment describing the intended Compute Using scope.

**Worked example:**
- Violation: `WINDOW_SUM(SUM([Sales]))` with no comment
- Rewrite: prepend `// Compute Using: Pane (Down); resets per year`

### S-STRUCT-04 — No unnecessary parentheses around single-token operands

**Rule:** Parentheses around single-token operands (bare fields, bare literals) are noise.

**Rationale:** Adds visual clutter without clarifying intent.

**Rewrite:** Strip unnecessary parens.

**Worked example:**
- Violation: `([Sales]) * (1.1)`
- Rewrite: `[Sales] * 1.1`

## Comment Rules (Severity: info)

### S-COMMENT-01 — Long calcs have a purpose comment

**Rule:** Calcs longer than 5 lines have a leading comment explaining purpose.

**Rationale:** Long calcs without a comment force future readers to reverse-engineer intent.

**Rewrite:** Prepend a purpose comment. Never rewrites formula body.

### S-COMMENT-02 — Magic numbers explained

**Rule:** Non-obvious literal values (business thresholds, magic numbers) have inline explanatory comments.

**Rationale:** A bare `500` in a threshold check is opaque; `500 // free-shipping threshold` is self-documenting.

**Rewrite:** Add inline comment. Never rewrites the value itself.

**Worked example:**
- Violation: `IF [Sales] > 500 THEN 'High' ELSE 'Low' END`
- Rewrite: `IF [Sales] > 500 // free-shipping threshold\nTHEN 'High' ELSE 'Low' END`

## Formatting Rules (Severity: info)

### S-FORMAT-01 — Consistent indentation

**Rule:** Indentation uses spaces (2 or 4), consistent within one calc. No tabs mixed with spaces.

**Rationale:** Mixed indentation renders unpredictably across editors and Tableau versions.

**Rewrite:** Normalize to the calc's dominant indentation style.

### S-FORMAT-02 — No trailing whitespace

**Rule:** No trailing whitespace on any line.

**Rationale:** Trailing whitespace triggers unnecessary diffs in workbook XML and can produce parse edge cases.

**Rewrite:** Strip trailing whitespace on every line.

### S-FORMAT-03 — At most one blank line between sections

**Rule:** No more than one blank line between logical sections within a calc.

**Rationale:** Excess blank lines waste vertical space in the calc editor without adding readability.

**Rewrite:** Collapse consecutive blank lines to one.

## Detection Order

Run rules in this order during Phase 2 for deterministic output:

1. S-NAME-01, S-NAME-02, S-NAME-03 (naming is user-visible first).
2. S-STRUCT-01, S-STRUCT-02, S-STRUCT-03, S-STRUCT-04 (structural clarity).
3. S-COMMENT-01, S-COMMENT-02 (documentation).
4. S-FORMAT-01, S-FORMAT-02, S-FORMAT-03 (formatting is lowest priority).

## Rewritable-vs-Report-Only

Every rule is reportable. Rewritability varies:

| Rule | Rewritable? | Rewrite touches formula body? |
|---|---|---|
| S-NAME-01, S-NAME-02, S-NAME-03 | Yes | No (name only) |
| S-STRUCT-01 | Rarely (only if equality-only IF chain) | Yes |
| S-STRUCT-02, S-STRUCT-03 | Yes | No (comment only) |
| S-STRUCT-04 | Yes | Yes (whitespace only) |
| S-COMMENT-01, S-COMMENT-02 | Yes | No (comment only) |
| S-FORMAT-01, S-FORMAT-02, S-FORMAT-03 | Yes | Yes (whitespace only) |

Rewrites that touch the formula body still require R-EQUIV-01 verification per HC#8. Rewrites that only add comments or rename the calc are still verified as a belt-and-braces defense against accidental formula corruption.

## Refuse to Fabricate

Never invent a new rule ID. Never mark a violation as more severe than its rule's assigned severity.
