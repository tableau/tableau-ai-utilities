# Chart Recommendation Catalog (Locked)

Maps every question type from the taxonomy to a recommended chart type plus permissible alternatives. Duplicates Worksheet Builder's `decision_framework.md` recommendations intentionally so both skills stay in sync.

## Recommendation Table

| Question Type | Recommended Chart | Alternatives (Info-tier acceptable) | Anti-Pattern Matches |
|---|---|---|---|
| Temporal | Line | Area (composition-over-time), Vertical bar (period-over-period), Sparkline (compact multi-metric) | AB-1 (3D area), AB-5 (radar for time) |
| Categorical | Sorted horizontal bar | Vertical bar (short labels), Dot plot (many categories), Lollipop (small-count high-emphasis) | AB-2 (pie >5), W-3 (text table), W-4 (discrete-date bar mislabeled) |
| Composition | Stacked bar | Treemap (high-cardinality), 100% stacked (share comparison) | AB-1 (3D), AB-2 (pie >5) |
| Distribution | Histogram | Box plot (outlier emphasis), Density plot (continuous) | AB-2 (pie for spread), W-3 (text for distribution), W-7 (histogram when outlier/per-category emphasis is the real question) |
| Correlation | Scatter | Scatter with trend line (regression), Connected scatter (correlation over time) | W-2 (Executive audience), W-3 (text for correlation) |
| Ranking | Sorted horizontal bar + Top N | Bump chart (rank-over-time), Dot plot (compact ranking) | AB-2 (pie for top-N), I-2 (sort order missing) |
| Geographic | Filled map (choropleth) | Point map (lat/long), Density map (high-cardinality points), Symbol map (measure-scaled points) | W-5 (choropleth with count) |
| Status/KPI | KPI tile (BAN + delta) or bullet chart | Sparkline with target line | AB-6 (gauge), W-6 (multi-measure KPI in one sheet) |
| Sequential | Funnel (sorted bar with stages) | Sankey (multi-source, limited native support), Stage-transition matrix | AB-2 (pie for funnel), W-1 (line chart for sequential) |

## Recommendation Confidence

Every recommendation carries a confidence tag matching the classification's confidence:

- **High-confidence classification + Anti-pattern gate clean.** Recommendation is a direct swap to the recommended default. Confidence: High.
- **High-confidence classification + Anti-pattern fires.** Recommendation is the anti-pattern's escape route. Confidence: High (the anti-pattern is a locked catalog entry).
- **Medium-confidence classification.** Recommendation is the type-default but with an explicit "consider re-running with a stated question or audience" note. Confidence: Medium.
- **Low-confidence classification.** No recommendation. Route to `worksheet-builder` for a fresh chart design per HC#4.
- **Low-confidence classification + anti-pattern gate clean (locked default verdict).** When no anti-pattern fires and the classification can't confidently endorse or reject the current chart, the verdict is `Keep` — but `recommendation.recommended_chart_type` is `null` (not the current mark type) and the rationale must state plainly that this is a low-confidence non-endorsement, not a best-fit match. Never render this case as a confident Keep. Suggest re-running with a stated question or audience.

## Recommendation Rationale Template

Every recommendation includes a rationale following this shape:

```
Verdict: {Keep | Swap Recommended | Anti-Pattern Block}
Current chart: {mark_type} + {shelf_placement_summary}
Recommended chart: {recommended_type}
Rationale:
- Question type: {type} ({confidence} confidence, signals: {list})
- Current chart fit: {reason_for_mismatch_or_match}
- Recommendation rationale: {why_the_recommended_type_answers_the_question_better}
- Anti-patterns matched: {list_or_none}
Desktop rebuild path (if Swap Recommended or Anti-Pattern Block):
- {specific_worksheet_builder_handoff_or_manual_instruction}
```

## Rebuild Handoff Payload (to worksheet-builder)

When verdict is Swap Recommended or Anti-Pattern Block, the handoff includes:

- **recommended_mark_type.** Specific Tableau mark type (Line, Bar, Circle, Filled Map, etc.).
- **recommended_shelf_placements.** Rows / Columns / Marks card assignments matching Worksheet Builder's `build_patterns.md` conventions.
- **rationale.** Copied from the recommendation report.
- **preserve_fields.** List of fields from the current worksheet that should carry into the rebuild.
- **fields_to_drop.** List of fields not needed in the new chart (rare; usually zero).

Worksheet Builder consumes this payload, presents its own build plan to the user for approval, and only then invokes `bind-template` or `build-and-apply-worksheet`.

## Locked Alternatives (Not Substitutes)

The "Alternatives" column lists Info-tier acceptable variants. Do not substitute an alternative for the recommended default without a stated reason:

- If the user cites a specific decision that maps to an alternative (e.g., "I need period-over-period comparison" for Temporal → recommend Bar instead of Line), the alternative is the recommendation.
- If no specific reason is cited, recommend the default. The user can request an alternative in Desktop.

## Refuse to Fabricate

Never recommend a chart type outside this catalog. Every recommendation must map to a row above.
