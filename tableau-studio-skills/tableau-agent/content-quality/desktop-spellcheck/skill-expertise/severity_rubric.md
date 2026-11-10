# Severity Rubric

Locked thresholds. Do not deviate. If an issue does not fit a category cleanly, err toward lower severity, not higher. False positives at High severity destroy user trust faster than missed catches at Low.

## Critical

Real misspellings against the en-US dictionary, not in the allow-list, appearing in stakeholder-facing locations.

**Locations that qualify as stakeholder-facing:**
- Worksheet title
- Worksheet caption
- Dashboard title
- Dashboard text object
- Tooltip text visible on hover
- Annotation text visible on the sheet
- Parameter display name
- Field alias (the user-facing rename)

**Locations that do NOT qualify:**
- Calculated field name (internal-facing unless placed on a shelf title)
- Field name in schema (unless aliased and visible)

Example: "Cusomer Revenue" in a dashboard title.

## High

**Capitalization drift.** The same lowercase-normalized token appears in two or more capitalization variants across the workbook. Flag all variants except the most common one.

Example: "Order ID" appears 8 times, "Order Id" appears 3 times, "order id" appears 1 time. Flag the two variants that are not "Order ID."

**Also High:** proper-noun casing errors on known product names ("tableau" instead of "Tableau" outside the allow-list context).

## Medium

**Typography drift.** All of these tagged Medium:
- Any curly single quote (‘ or ’) found anywhere in scoped text — flag it directly at the point found. Do not require confirming a co-occurring straight quote elsewhere in the workbook first; curly quotes are rare enough in Tableau-authored captions that their mere presence is the signal (they indicate text pasted from Word/a document, which is inconsistent with everything else Tableau renders as straight quotes by default).
- Any curly double quote (“ or ”) found anywhere in scoped text — same rule, flag directly, no co-occurrence check required.
- Em-dash (—) and en-dash (–) used inconsistently
- Trailing whitespace on any user-facing text
- Double spaces inside any user-facing text
- Leading whitespace on any user-facing text

**Also Medium:** ambiguous abbreviations that could be typos ("YoY" is fine and allow-listed; "yoy" mid-sentence is not).

## Low

**Singular/plural inconsistency.** "Order" and "Orders" both used as column headers or titles in the same workbook when referring to the same underlying field. Include exact locations of each variant.

**Also Low:** repeated unknown tokens that appear 3+ times but did not trigger a dictionary suggestion (Levenshtein distance 3+). These are likely jargon the user should allow-list. Report but do not treat as an error.

Note: cross-term terminology consistency ("customer" vs "client", "sales" vs "revenue") is intentionally out of scope. That check produced too many false positives during design and undermined reproducibility. Users who need it should run a separate pass with a specific term-pair mapping file.

## Token-splitting rules

Before running the dictionary check, split text into tokens using these rules in order:

1. Split on whitespace.
2. Split on punctuation, except apostrophes inside a token (don't → one token).
3. Strip surrounding punctuation from each token.
4. Preserve internal capitalization (do not lowercase before dictionary lookup).
5. Skip tokens that are:
   - Numeric only (2026, 1.5, 3%)
   - Date-like (2026-Q3, Q1FY26, 08/25/2026)
   - Single characters (except common single-letter words: a, I)
   - Currency-formatted ($1.2M, €500)
6. Skip tokens that appear in the allow-list.
7. Skip a title/caption string entirely if it is character-for-character identical to the sheet's own internal name (this is Tableau's fallback when no custom title was ever set — a system-generated label, not authored copy). Do not run these through the dictionary check.
8. Before the dictionary check, split camelCase/PascalCase tokens on internal capital boundaries (`CustomerRank` → `Customer`, `Rank`) so real words inside a concatenated identifier are recognized rather than flagged whole.

## Close-match handling

For each token flagged by the dictionary as unknown, compute Levenshtein distance to the nearest dictionary word.

- Distance 1: high confidence misspelling. Include the suggestion in the finding.
- Distance 2: medium confidence. Include the suggestion but caveat as "did you mean?"
- Distance 3+: low confidence. Flag as unknown token without suggestion. May be a jargon term the user should allow-list.

If a token has distance 3+ AND appears 3 or more times in the workbook, include it prominently in the "Allow-list suggestions" section of the report.
