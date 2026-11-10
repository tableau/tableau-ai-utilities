# Test Prompts

Testing matrix for desktop-spellcheck. Run each prompt against a workbook with known seeded issues. Skill is production-ready when second-pass change rate falls below 20%.

## Coverage categories

1. Happy paths (basic activation, standard flow)
2. Scope confirmation flow
3. Allow-list interaction
4. Two-tier fallback
5. Edge cases and hard constraints
6. Error recovery
7. Scalability

***

## 1. Happy paths

| # | Prompt | Seed | Expected |
|---|---|---|---|
| 1 | "Spellcheck this workbook" | Workbook with 2 misspellings in titles, 1 in tooltip | Skill activates, confirms scope, produces report with 3 Critical findings |
| 2 | "Find typos in my dashboard" | Same as #1 | Same as #1 |
| 3 | "Proofread this before I publish" | Workbook with 1 misspelling, 1 double space | Report with 1 Critical, 1 Medium |
| 4 | "Copy consistency check" | Workbook with "Order Id" and "Order ID" both used | Report with 1 High (cap drift) |
| 5 | "Text review" | Clean workbook (no issues) | Report with all zero counts, "None" under each section |

## 2. Scope confirmation flow

| # | Prompt | Expected |
|---|---|---|
| 6 | "Spellcheck this" | Skill lists all 7 categories, asks user to confirm or trim |
| 7 | "Spellcheck just the dashboard text objects" | Skill scopes to dashboards only, skips others, notes scope in header |
| 8 | "Spellcheck everything except tooltips" | Skill excludes tooltips, notes scope in header |
| 9 | "Just check my field aliases" | Skill scopes to Datasource fields only |

## 3. Allow-list interaction

| # | Prompt | Setup | Expected |
|---|---|---|---|
| 10 | "Spellcheck this" | skill-expertise/allow-list.txt missing | Warns once, proceeds with the fallback seed list, says so in the header, suggests reinstalling or recreating the file |
| 11 | "Spellcheck this" | skill-expertise/allow-list.txt contains "Cusomer" (an intentional typo the user wants) | "Cusomer" not flagged. Other findings unaffected. |
| 12 | "Spellcheck this" | Same jargon term appears 5 times, not in allow-list | Term appears in Allow-list Suggestions section |
| 13 | "Spellcheck and ignore MuleSoft variations" | User adds MuleSoft to allow-list mid-flow (advisory only) | Skill notes it cannot modify allow-list, tells user to add manually |

## 4. Two-tier fallback

| # | Prompt | Setup | Expected |
|---|---|---|---|
| 14 | "Spellcheck this" | 3 dashboard-bound worksheets, get-worksheet-xml returns 500 on all | Skill detects failure, asks for .twb or .twbx path |
| 15 | "Spellcheck this" | Same as #14, user provides .twbx path | Skill unzips, parses .twb, includes those sheets in findings |
| 16 | "Spellcheck this" | Same as #14, user declines to provide path | Skill lists those sheets under Not Scanned, continues with what it has |
| 17 | "Spellcheck this" | User provides .twb path (not .twbx) | Skill parses directly, no unzip step, same output quality |

## 5. Edge cases and hard constraints

| # | Prompt | Expected |
|---|---|---|
| 18 | "Fix the typos in this workbook" | Skill activates but refuses to mutate. Produces report and explicit "fix these manually in Desktop" instruction. |
| 19 | "Rewrite the titles with better copy" | Skill declines. This is not a spellcheck task. Suggests user handle manually or use a writing skill. |
| 20 | "Spellcheck and change the misspellings" | Same as #18. Report only, no mutation. |
| 21 | "Spellcheck this workbook" (workbook has zero sheets) | Skill reports "No stakeholder-visible text found. Confirm you are pointed at the correct workbook." |
| 22 | "Spellcheck this workbook" (workbook has 200 sheets) | Skill scales, may take longer, produces complete report. If findings > 50, spot-checks 3. |
| 23 | Text contains "2026-Q3" | Not flagged (date-like) |
| 24 | Text contains "$1.2M" | Not flagged (currency) |
| 25 | Text contains "recieve" | Flagged Critical, suggestion "receive" |
| 26 | Text contains "revenue" and "Revenue" in same workbook | Flagged High (cap drift), most common form is the baseline |

## 6. Error recovery

| # | Prompt | Setup | Expected |
|---|---|---|---|
| 27 | "Spellcheck this" | Dictionary lookup fails entirely | Falls back to built-in word list, notes fallback in header |
| 28 | "Spellcheck this" | .twbx path provided is actually a .twb | Handles gracefully, parses as raw XML |
| 29 | "Spellcheck this" | .twb path is malformed XML | Reports parse failure, lists affected sheets under Not Scanned |
| 30 | "Spellcheck this" | Workbook has UTF-8 BOM | Handles encoding correctly, no garbled text in findings |

## 7. Scalability

| # | Prompt | Setup | Expected |
|---|---|---|---|
| 31 | "Spellcheck this" | 500+ findings | Report includes all, spot-check triggered, no truncation |
| 32 | "Spellcheck 3 workbooks" | User asks for batch | Skill runs sequentially, produces 3 separate reports, does not combine |

## Change-driven revisions

Track prompt-by-prompt whether output required correction. Target < 20% change rate on second pass. If a prompt drove a change, note the change here so it does not regress:

- (Populate during testing)

## Composability notes

This skill delegates to none of the other 8 skills. It does not receive delegated work either. It sits adjacent to Publish Readiness in the pipeline (both are read-only pre-publish passes) but they do not overlap in scope: Publish Readiness catches hygiene (naming, scratch sheets, performance patterns); this skill catches text errors.
