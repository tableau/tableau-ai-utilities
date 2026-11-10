# Format Drift Scanner

**Audit a workbook for format-string drift across measures, dates, and text.** Read-only. Every finding is a Desktop-fix instruction.

## When to Use

- You built dashboards with multiple measures and dates and want to catch inconsistencies before publish.
- You inherited a workbook and want a sanity check on formatting consistency.
- You're prepping for a stakeholder review and want to catch drift before someone else does.

## When Not to Use

- **Text-copy correctness.** Use `desktop-spellcheck` for spelling, capitalization, typography.
- **Localization fragility.** Use `i18n-scanner` for hard-coded currency, regional date collisions, region-specific vocabulary.
- **Color palette compliance.** Not supported (pixel-visibility gap).
- **Dashboard assembly hygiene.** Use `dashboard-preflight` for zone alignment, canvas size, container nesting.
- **Chart-type selection.** Use `chart-swap-advisor` for is-this-the-right-chart-type questions.
- **Applying format changes.** All fixes are Desktop-manual per HC#1.

## The 7-Drift Catalog

Every run evaluates the workbook against a locked catalog. Each finding cites a specific rule ID:

| ID | Drift Type | Baseline Severity |
|---|---|---|
| F-CURRENCY-01 | Currency-Symbol Mismatch | Warning |
| F-DECIMAL-02 | Decimal-Places Mismatch | Warning |
| F-DATE-03 | Date-Format Mismatch | Warning |
| F-SEPARATOR-04 | Thousands-Separator Mismatch | Warning |
| F-FONT-FAMILY-05 | Font-Family Drift | Info |
| F-FONT-SIZE-06 | Font-Size Drift | Info |
| F-NEGATIVE-07 | Negative-Number-Treatment Drift | Warning |

Cross-DS drift is Info-by-default per HC#12; multi-currency reporting is legitimate.

## What You Get

A compact chat summary with counts by severity, findings by drift type, and top 3 items. Optional full report file to Downloads. Handoff to publish-readiness, workbook-auditor, and i18n-scanner.

## Example Trigger Phrases

- "Format drift"
- "Check my formatting"
- "Audit format consistency"
- "Are my dates and numbers consistent?"
- "Check number formats"
- "Date format audit"
- "Font consistency check"

## Output Handoff

Emits `format_drift_report/1` per the locked schema. Consumed by publish-readiness (pre-publish summary), workbook-auditor (change enrichment), and i18n-scanner (candidate locale signals).

## Known Limitations

- One workbook per run. Batching is refused.
- `get-worksheet-xml` reliability on dashboard-bound populated sheets. Fallback to `list-available-fields` metadata.
- Cannot detect font drift on chart marks when the underlying mark type doesn't expose font attributes in XML.
- Cannot detect rendered visual differences that aren't encoded in the format string.

## Distribution

Ships with Tableau Studio. Also available on Skills Exchange for latest-version pulls between Studio releases.
