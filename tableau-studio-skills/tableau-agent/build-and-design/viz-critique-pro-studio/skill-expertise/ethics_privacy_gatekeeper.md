# Ethics and Privacy Gatekeeper (Locked, Non-Overridable)

Runs first, before any domain scoring. Overrides the overall-score ceiling. HC#11 makes this non-overridable under user pressure.

## Severity Tiers

- **Critical.** Cap overall score at 59/100. Report renders "Critical ethics violation" banner as the first section after the header.
- **Warning.** Cap overall score at 79/100. Report renders "Warning ethics observation" banner.
- **Info.** No cap. Noted in the report's ethics section as an observation.

Multiple violations: highest severity wins the cap. All violations render in the ethics section.

## Critical Triggers

### E-DECEPTIVE-SCALE

**Signal.** Y-axis or X-axis truncation that visually implies a magnitude the underlying data does not support. Common patterns: bar chart with y-axis starting well above zero producing apparent 300% growth on 8% real growth; dual-axis chart where one axis scale is compressed to make two series look correlated.

**Cap.** Critical → 59/100.

**Recommendation.** Start numeric axes at zero for bar charts, or add an explicit axis-break annotation. For dual-axis, either use single-axis with Measure Names color encoding, or note the scale difference in the caption.

### E-CHERRY-PICKED-COMPARISON

**Signal.** Comparison against a single hand-picked baseline that flatters the current period (e.g., "70% growth vs. worst month last year") without disclosing the selection.

**Cap.** Critical → 59/100.

**Recommendation.** Use year-over-year or period-over-period comparisons that are clearly documented, or use a rolling average rather than a single-point comparison.

### E-MISLEADING-TIME-WINDOW

**Signal.** Time-series chart with a truncated window that hides a countervailing trend visible in the fuller dataset (e.g., 3-month window showing growth on top of a 5-year decline that would flip the interpretation).

**Cap.** Critical → 59/100.

**Recommendation.** Show the fuller time window or annotate the window choice with rationale.

### E-MISSING-BASELINE-ON-RATE

**Signal.** Rate chart (conversion rate, retention rate, error rate) without a baseline or denominator disclosure that could mislead the reader about scale.

**Cap.** Critical → 59/100.

**Recommendation.** Add a baseline reference line or disclose the sample size.

### E-PII-PHI-VISIBLE

**Signal.** Personally identifiable information (names, email addresses, government ID numbers, medical record numbers, exact home addresses) visible on the rendered dashboard without redaction.

**Cap.** Critical → 59/100.

**Recommendation.** Redact via anonymization function, aggregation to a higher grain, or masking before publish. Route to `data-quality-review` for a data-side audit.

### E-PROPRIETARY-UNREDACTED

**Signal.** Proprietary data (customer names, contract values, competitive intelligence) visible without watermarks or classification indicators when the dashboard's audience includes External per stated intent.

**Cap.** Critical → 59/100.

**Recommendation.** Add classification banner or restrict audience.

## Warning Triggers

### E-HIDDEN-ASSUMPTION

**Signal.** A calc or filter that materially changes the interpretation is not disclosed on the dashboard (e.g., "excludes returns" applied silently to a Sales dashboard).

**Cap.** Warning → 79/100.

**Recommendation.** Add caption note or explicit filter card visible on the dashboard.

### E-COLOR-DECEPTION

**Signal.** Color choices that map bad-to-good in a way that misleads (e.g., red for "target met" and green for "target missed", or a divergent palette applied to a sequential measure).

**Cap.** Warning → 79/100.

**Recommendation.** Align color mapping with the shared portfolio catalog (blue/teal for positive, orange/magenta for alert, gray for neutral, plus mandatory shapes for accessibility).

### E-SELECTIVE-EMPHASIS

**Signal.** Formatting emphasis (bold, size, color highlight) applied to a subset of data in a way that flatters or damages a comparison without clear rationale.

**Cap.** Warning → 79/100.

**Recommendation.** Apply consistent emphasis rules or remove selective formatting.

### E-UNDISCLOSED-SAMPLING

**Signal.** Sample-based data rendered as if population-level, without disclosure.

**Cap.** Warning → 79/100.

**Recommendation.** Add caption note stating the sample basis.

## Info Observations

### E-CLASSIFICATION-BANNER-ABSENT

**Signal.** Dashboard likely handles sensitive data but has no classification banner. Not a Critical or Warning unless PII/PHI or proprietary content is visible.

**Recommendation.** Add classification banner as a best practice.

### E-SOURCE-CITATION-ABSENT

**Signal.** No data-source citation on the dashboard footer.

**Recommendation.** Add data-source and last-updated timestamp to the footer.

### E-INTENT-AMBIGUOUS

**Signal.** Purpose of the dashboard is unclear from title and design; ambiguous intent could enable multiple interpretations, some of which lean toward misleading.

**Recommendation.** Sharpen title, add a decision-oriented subtitle.

## Calibration Examples

**Example E.1 → E-DECEPTIVE-SCALE Critical fires.** Bar chart on the dashboard has y-axis starting at 250 with bars extending to 280 for Sales-Rep A and 260 for Sales-Rep B. Visual reading suggests Rep A has 2-3x higher sales than Rep B; actual values are 280 vs. 260 (7% difference). Signal: axis truncation greater than 10% of the value range on a bar chart. Cap at 59/100.

**Example E.2 → E-COLOR-DECEPTION Warning fires.** KPI tile uses red for "target met" and green for "target missed." Signal: color polarity inverted from convention; readers will misread status at a glance. Cap at 79/100.

**Example E.3 → E-PII-PHI-VISIBLE Critical fires.** Detail table on the dashboard shows employee names, email addresses, and manager assignments unredacted. Signal: PII visible on a dashboard without a classification banner or aggregation. Cap at 59/100.

**Example E.4 → No violation.** Bar chart with y-axis starting at zero. All measures clearly labeled. Colors align with shared portfolio catalog. No PII visible. Rate chart shows the denominator (n=1,247) in the caption. Signal: no ethics triggers fire. Overall score computed normally.

**Example E.5 → E-INTENT-AMBIGUOUS Info observation.** Dashboard title reads "Data" with no subtitle. Multiple charts with no clear primary metric. Signal: ambiguous intent could enable multiple interpretations, but no specific manipulation is evident. Info-tier note in the ethics section; no cap.

## Detection Discipline

- **Trust image evidence first.** Ethics triggers cite specific visual signals from the image.
- **Confidence flag on ambiguous ethics signals.** If an axis truncation looks marginal, flag confidence in the report and use the lower severity if confidence is low.
- **Do not fabricate ethics violations.** Every triggered violation cites the specific image evidence.
- **Do not skip the gatekeeper.** Runs first, every run. HC#11 non-override.

## Cap Enforcement

When any Critical or Warning ethics trigger fires:

1. Compute per-domain scores normally (each domain gets its 1-10 score).
2. Compute overall weighted score normally.
3. Apply the cap: `overall = min(overall, cap_ceiling)`.
4. Note the raw pre-cap score in the ethics section for transparency.
5. Render the appropriate banner ("Critical ethics violation" or "Warning ethics observation") as the first section after the report header.

## User-Pressure Refusal

Under any request to override, downgrade, or skip the ethics cap:

- "I understand you'd prefer a higher score. The ethics cap stands because [specific violation]. The cap protects the audience from a design that could mislead. If you address the violation, re-run the critique and the cap lifts automatically."

Never sarcastic. Never dismissive. Direct and specific.

## Refuse to Fabricate

Every ethics violation cites specific image evidence. Never invent a violation to inflate rigor. Never suppress a genuine violation to please the user. If a violation is ambiguous, flag confidence and use the lower severity.
