# Tableau Inheritance Triage

A read-only advisory skill that orients an author who just opened an unfamiliar Tableau workbook. Two modes. Orient mode produces a deliberately-shallow one-page summary (headline, primary dashboards, data sources, calc complexity tiers, sheet complexity top-10, where to start reading, known issues, optional handoffs). Complexity-score mode ranks every worksheet 1-10 against a locked 6-factor rubric (C1 mark count, C2 nesting, C3 table-calc, C4 LOD, C5 filter count, C6 cross-DS). Fills the gap between data-scribe (exhaustive metric dictionary), calc-documenter (exhaustive calc catalog), workbook-summary-onepager (stakeholder handoff), and workbook-auditor (change tracking) by owning the "shallow 5-minute orientation" problem none of them covers.

**Example:** "I just opened this workbook, orient me."

## What it does

Reads a live workbook via Studio tools (`list-dashboards`, `list-worksheets`, `list-available-fields`, `get-workbook-inventory`, `get-worksheet-xml` per sheet) and produces one of two outputs. **Orient mode** returns an 8-section summary capped at 500 words, meant to be read in 5 minutes. **Complexity-score mode** returns a per-worksheet ranking with C1-C6 breakdowns and a bucket count (Simple / Moderate / Complex).

The complexity ranking is a prioritization aid, not a quality judgment. A score-10 sheet is often the right design for its question; the score only tells the inheriting author "this one will take longer to read than the simple sheets."

Pairs with data-scribe (full metric dictionary), calc-documenter (full calc catalog), workbook-summary-onepager (stakeholder handoff), and workbook-auditor (change tracking) as optional downstream routes, each with a manual Desktop fallback.

## When to use it

- "I just opened this workbook and have no idea what it does."
- "I inherited this from a departed consultant."
- "Where do I start reading."
- "Give me a 5-minute summary before my review tomorrow."
- "Which of these 25 sheets are going to be the hardest to understand."
- "Rank these sheets by complexity so I know what to tackle last."

## When NOT to use it

- Not for a full metric dictionary (use data-scribe)
- Not for an exhaustive calc catalog (use calc-documenter)
- Not for a stakeholder-facing onepager (use workbook-summary-onepager)
- Not for ongoing change tracking (use workbook-auditor)
- Not for mutating the workbook (deleting flagged sheets, hiding orphans, cleaning up); this skill is read-only
- Not for authoring or editing anything in Desktop

## How to trigger it

Orient mode:

- "I inherited this"
- "orient me"
- "where do I start"
- "triage this workbook"
- "5-minute summary"
- "I just opened this workbook"
- "unfamiliar workbook"

Complexity-score mode:

- "rank these sheets by complexity"
- "which sheets are hardest"

## What you'll need

- Tableau Studio open with the agent connected
- A workbook with at least a few sheets. Workbooks under 5 sheets AND under 10 calcs trigger the HC-3 short-circuit (2-sentence summary) rather than the full 8-section orient.
- If the workbook has 100+ sheets, the skill will ask you to scope the scan before proceeding (full with top-20, scope to a dashboard, scope to sheets scoring 7+, or scope to a filename substring).
- `get-worksheet-xml` must succeed per sheet for a full C1-C6 score. Sheets whose XML fails to load are included in the ranked list with "unscored" and no fabricated score.

## The 6-factor complexity rubric (C1-C6)

Each worksheet scores 1-10 (sum of C-factor contributions, clamped).

- **C1 Mark count.** 0 if under 100 marks, 1 if 100-500, 2 if 500-5000, 3 if 5000+. If `get-summary-data` is unavailable, C1 defaults to 1 across all sheets with an "unverified mark counts" announcement at the top of the output.
- **C2 Calc nesting depth of fields used.** 0 if no calcs, 1 if one level of nesting, 2 if two or more levels (a calc that references another calc, which may itself reference another).
- **C3 Table-calc presence.** 0 or 1 point. Quick table calcs count (Running Total, Difference From, Percent Difference, etc.).
- **C4 LOD presence.** 0 if no LODs, 1 if INCLUDE or EXCLUDE, 2 if FIXED. FIXED weighs higher because it is the most powerful and most confusing to inherit.
- **C5 Filter count.** 0 if under 3 filters, 1 if 3-5, 2 if 6+.
- **C6 Cross-DS references.** 0 if all fields on the sheet reference the same data source, 2 if any field references a different data source than the primary one.

Tier boundaries. 1-3 Simple. 4-6 Moderate. 7-10 Complex.

Full rubric with per-factor evidence sources, scoring edge cases, and HC-8 reminder in `skill-expertise/complexity-rubric.md`.

## The 8-section Orient-mode output

Hard-capped at 500 words.

- **Section 1 Headline.** 1-2 sentences. What the workbook is, last-modified-date if available (or HC-6 absence-statement if not).
- **Section 2 Primary dashboards.** 3-5 bullets. Each: name, sheet count, structural "Answers X" phrase. Structural ("shows revenue by region"), not interpretive ("shows that revenue is strong").
- **Section 3 Data sources.** Count and names.
- **Section 4 Calc complexity tiers.** 3 lines: simple count, LOD-heavy count, nested count.
- **Section 5 Sheet complexity top-10.** Nested bulleted list (not a table): sheet name, score, tier.
- **Section 6 Where to start reading.** 1-2 sentences. Names a specific dashboard and a specific sheet or calc to read second.
- **Section 7 Known issues flag.** Only tool-visible issues: default sheet names, orphan sheets, hidden sheets, broken field references.
- **Section 8 Optional handoffs.** 4 lines, one per downstream skill, each with a manual fallback.

Full template with word budgets per section and trim discipline in `skill-expertise/triage-output-template.md`.

## Example walkthrough

**Input:** "orient me" (Sample Superstore workbook open: 6 dashboards, 21 worksheets, 14 named calcs, 3 datasources)

**Output (abridged, Orient mode):**

```
1. Headline. "Superstore" is a 6-dashboard, 21-worksheet
   sales/shipping/commission workbook spanning Sample - Superstore
   (primary), Sales Commission, and Sales Target datasources. Modified
   date not available in file metadata.

2. Primary dashboards.
   - Overview, answers "how is the business tracking overall" (4 sheets)
   - Product, answers "how is each product category performing" (2 sheets)
   - Customers, answers "who are our most and least valuable customers" (3 sheets)
   - Shipping, answers "are we shipping on time" (3 sheets)
   - Commission Model, answers "what would a rep's comp be under these
     assumptions" (4 sheets)

3. Data sources (3). Sample - Superstore (primary), Sales Commission.csv
   (secondary), Sales Target (small).

4. Calc complexity tiers. 14 total. 6 simple, 4 FIXED-LOD-based, 4 nested.

5. Sheet complexity top (C1 unverified, defaulted to 1 for all).
   - Product Detail Sheet, score 5, Moderate
   - ShipSummary, score 5, Moderate
   - Sales by Product, score 4, Moderate
   - Sales by Segment, score 4, Moderate
   - DaystoShip, score 4, Moderate
   (...5 more at or below Moderate)

6. Where to start. Start with Overview, then read Product Detail Sheet's
   Ship Status calc chain. It is the most nested logic feeding three
   Shipping-dashboard sheets.

7. Known issues. 4 sheets outside any dashboard's contained-sheet list
   (likely intentional standalone tabs). No default-named sheets.
   17 of 21 sheets hidden, expected for dashboard zone content.

8. Handoffs.
   - data-scribe: full metric dictionary. Fallback: read field
     descriptions from the Data pane.
   - calc-documenter: full per-calc dictionary. Fallback: inspect
     calcs individually from the Data pane.
   - workbook-summary-onepager: stakeholder handoff. Fallback: combine
     this orient summary with a 1-paragraph headline manually.
   - workbook-auditor: change tracking. Fallback: snapshot the
     workbook manually and diff against future versions.

File save: .md, .txt, or chat only?
```

Save goes to your Downloads folder by default.

## What you get back

- An 8-section Orient summary at or under 500 words, or a full per-worksheet complexity ranking with C1-C6 breakdowns, depending on which mode fires
- Honest short-circuit for small workbooks (fewer than 5 sheets AND fewer than 10 calcs): 2 sentences, not 8 sections
- An honest "Modified date not available in file metadata" statement when `get-workbook-inventory` returns no timestamp
- A ranked complexity list with hidden sheets sorted to the bottom as a block and visible sheets ordered by score (with within-tie tie-breakers: named-field-count descending, then alphabetical)
- Optional `.md` or `.txt` save to the Downloads folder

## Limitations

- Read-only. The skill does not modify the workbook. All output is text summary.
- Deliberately shallow. Orient mode is capped at 500 words. If you need an exhaustive output, use data-scribe (metrics), calc-documenter (calcs), or workbook-summary-onepager (stakeholder handoff).
- Mark count (C1) depends on `get-summary-data`, which may not be available in every session. In that case C1 defaults to 1 point across all sheets and the output announces this at the top. You can also self-report mark counts for a rescored C1.
- Complexity scoring is per-worksheet, not per-dashboard,.
- Cross-session persistence is not supported. The reference artifact is the opt-in Downloads-folder save; re-read that file in a future session instead of expecting the skill to remember.
- Complex sheets are not "bad" sheets. The output never renders a quality judgment on a complex sheet per HC-8. Interpretive-judgment requests ("is this workbook good or bad") are refused and converted to structural output.
- The skill does not guess at business purpose beyond what the shelf composition shows. "Answers X" phrases are structural, not interpretive. If you want business context folded into the headline, provide it and the skill will re-emit.
- 100+ sheet workbooks require you to pick a scope before scanning. The skill does not scan 100+ sheets silently.
- `get-worksheet-xml` failures on individual sheets degrade gracefully: the failed sheet appears in the ranked list with "unscored (XML did not load)" and no fabricated score; the top-of-output announces "[N] of [M] sheets scored."

## Troubleshooting

- **"No workbook open."** The skill does not refuse. It offers to walk through `complexity-rubric.md` and `triage-output-template.md` as reading reference until a workbook is open.
- **"My workbook has 0 worksheets."** The skill short-circuits with a 1-sentence message and offers to walk through the output template format in advance.
- **"My workbook is small (fewer than 5 sheets, fewer than 10 calcs)."** The HC-3 short-circuit fires: 2-sentence summary, no full 8-section orient. This is correct behavior for a trivial workbook; it is not a bug or a "clean" verdict.
- **"The modified date is missing from the headline."** HC-6 held: `get-workbook-inventory` returned no timestamp (common for local .twb files that have never been published to Server). The absence is stated plainly rather than fabricated.
- **"The complexity top-10 does not match my gut sense of complex."** The rubric is structural (fields, nesting, LODs, filters, cross-DS, marks), not interpretive. If a sheet feels complex to read but scores low, that is often because the complexity is in the dashboard composition or in the author's naming, not in the shelf structure. Run data-scribe or calc-documenter for the deeper layer.
- Say "complexity for Overview" and the skill emits the top-3 scoring sheets contained in that dashboard.
- **"The skill refused to say whether a complex sheet is bad."** HC-8 held: complexity is prioritization, not quality judgment. A score-10 sheet is often the right design for its question. The skill will not render evaluative framing on any sheet.
- **"The skill refused to delete the orphan sheets you flagged."** HC-1 held: this skill is read-only. If `worksheet-cleanup` is installed, hand off there with the orphan flags from Section 7. Otherwise clean up manually in Desktop (right-click each in the Tabs strip, Delete, after confirming the sheet is genuinely unused).
- **"The file save failed."** The skill emits the full orient or complexity output inline anyway and names the save error. Copy from chat into your notes.
- **"The hidden sheets in Complexity-score mode are sorted after the visible sheets even though some score higher."** This is intentional per the rubric's edge case rule. Hidden sheets sort to the bottom as a block regardless of score, with each hidden sheet flagged inline. Visible sheets lead the ranked list.

## Support

File issues in the Tableau Agent Skills repo.
