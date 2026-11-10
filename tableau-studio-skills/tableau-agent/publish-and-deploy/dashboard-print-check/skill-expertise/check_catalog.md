# Check Catalog Reference
Locked reference file for dashboard-print-check's 8-check print catalog. Cited by HC#3 and V1. Every finding maps to exactly one primary check; multi-check findings tier by highest severity. Every check below includes detection criteria, evidence pattern, threshold defense (where applicable), edge cases, and worked examples.

## Check Precedence

**Severity tiering.** Warning-tier checks take precedence over Info-tier when multi-check tagging fires. Order among Warning-tier: check ID ascending (DPC-PAGEBREAK-01 before DPC-SIZE-02). Order among Info-tier: check ID ascending.

**Multi-check tagging.** A dashboard can trigger multiple checks simultaneously (common example: DPC-SIZE-02 range-size plus DPC-OVERFLOW-04 content overflow both fire on a range-sized dashboard with content beyond page-safe margins). Skill emits all triggered check IDs in `checks_triggered[]`; severity tier set by highest match.

**Fallback discipline.** When a check's detection depends on print-config XML that isn't set or is unreadable (a known platform gap), skill emits `"print-config-unset"` or `"unresolved"` sentinel for that specific check per HC#5. Rule is not treated as either true or false; user sees the sentinel and decides.

***

## DPC-PAGEBREAK-01: Page-Break Placement

**Severity:** Warning
**Signal source:** print_config
**Detection:** Print config XML declares a page-break policy (`<page-breaks>` element or equivalent) that falls mid-zone rather than at zone boundaries. Skill extracts declared break positions and cross-references against zone boundary coordinates from `get-dashboard-xml`.

**Evidence pattern:** `page_break_positions: [y=580, y=1160]; zone_boundaries: [{name: "Sales KPI", y_range: [540, 620]}]; break_falls_mid_zone: true`.

**Edge cases:**
- Print config declares no page breaks (single-page print). Does NOT fire; check clears.
- Break falls exactly at a zone boundary within a 5-pixel tolerance. Does NOT fire; considered clean.
- Zone boundaries unreadable via `get-dashboard-xml`. Emit `"unresolved"` sentinel per HC#5.

**Worked example:**
Dashboard `Q3 Regional Rollup` has a KPI zone spanning y=540-620 and print config declares a page break at y=580. Fires DPC-PAGEBREAK-01. Severity Warning. Desktop fix: "Adjust page break position in Print Preview or move zone boundary to align with break."

***

## DPC-SIZE-02: Fixed-Size vs Range-Size Sanity for Print

**Severity:** Warning
**Signal source:** dashboard XML
**Detection:** Dashboard `<size>` element declares `automatic` or `range` mode rather than `fixed`. Print rendering is unstable when the dashboard doesn't declare fixed pixel dimensions because page rendering scales unpredictably across page sizes.

**Evidence pattern:** `dashboard_size_mode: "range"; declared_dimensions: null; fires_regardless_of_print_config: true`.

**Edge cases:**
- Dashboard uses `fixed` size with explicit width/height. Does NOT fire; clears.
- Dashboard uses `range` size but user has explicitly acknowledged print instability in the workbook caption. Still fires (Info-tier reclassification not supported; user handles per-fix).
- Print config absent. Does NOT emit `"print-config-unset"` sentinel — this check is dashboard-XML-based, not print-config-based.

**Worked example:**
Dashboard `Executive Summary` uses range size (default in older workbooks). Fires DPC-SIZE-02. Severity Warning. Desktop fix: "Set fixed pixel size in Dashboard menu → Size → Fixed size → Set width/height explicitly."

***

## DPC-ORIENTATION-03: Orientation Fit

**Severity:** Warning
**Signal source:** print_config
**Detection:** Dashboard aspect ratio (width/height from dashboard XML) mismatches print config `<orientation>` declaration. Wide dashboards (aspect > 1.2) printed portrait get truncated; tall dashboards (aspect < 0.8) printed landscape get letterboxed.

**Evidence pattern:** `dashboard_aspect: 1.5 (wide); print_orientation: "portrait"; expected_orientation: "landscape"; mismatch: true`.

**Edge cases:**
- Aspect between 0.8 and 1.2 (roughly square). Does NOT fire; either orientation is acceptable.
- Print config unset. Emit `"print-config-unset"` sentinel per HC#5 (can't verify orientation without config).
- Dashboard size mode is `range` (so aspect is fluid). Emit `"unresolved"` sentinel; requires DPC-SIZE-02 to be addressed first.

**Worked example:**
Dashboard `Sales Trend by Region` is 1600x800 (aspect 2.0, wide) but print config declares portrait. Fires DPC-ORIENTATION-03. Severity Warning. Desktop fix: "Change print orientation to landscape in File → Page Setup, or reshape dashboard to portrait aspect."

***

## DPC-OVERFLOW-04: Container Overflow at Print DPI

**Severity:** Warning
**Signal source:** dashboard XML + print_config
**Detection:** Zone or container boundaries at print DPI (96 dpi baseline, or 300 dpi if print config declares high-DPI mode) exceed page-safe margins (page width minus 2× declared margin, page height minus 2× declared margin). XML-signal-based only; does not render print preview per HC#12.

**Evidence pattern:** `page_safe_area: [7.5in × 10in]; overflowing_zones: [{name: "Detail Grid", overflow_axis: "width", overflow_amount: "0.4in"}]; routing_offered.dashboard_preflight: true`.

**Edge cases:**
- Print config unset. Emit `"print-config-unset"` sentinel per HC#5 (can't compute page-safe area without margin declarations).
- Overflow amount below 0.1" (approximate pixel-DPI rounding tolerance). Does NOT fire; considered clean.
- Container-nesting soundness is out of scope for this check. Routes to `dashboard-preflight` via HC#11 for deeper analysis.

**Worked example:**
Dashboard `Detail Report` has a zone spanning x=0 to x=1700 pixels; at 96 dpi with letter-size portrait paper and 0.5" margins, page-safe width is 7.5" = 720 pixels. Fires DPC-OVERFLOW-04. Severity Warning. `routing_offered.dashboard_preflight: true`. Desktop fix: "Reduce zone width to fit within 720 pixels at 96 dpi, or route to dashboard-preflight for container-nesting analysis."

***

## DPC-COLORSAFE-05: Color-Safe Check for Black-and-White Printing

**Severity:** Info
**Signal source:** worksheet XML
**Detection (numbered checklist for reproducibility per HC#7):**

1. Enumerate worksheets referenced on the dashboard via `get-dashboard-xml` zone list.
2. For each worksheet, read shelf composition via `get-worksheet-xml`.
3. Check if `Color` shelf has any pill placement (measure or dimension).
4. Check if `Shape`, `Size`, and `Label` shelves are all empty (no redundant encoding).
5. If both conditions hold (Color populated AND all redundancy shelves empty), the worksheet fires DPC-COLORSAFE-05 for that dashboard.
6. Dashboard-level result: fires if any worksheet on the dashboard triggers steps 3-5.

**Evidence pattern:** `worksheets_with_color_sole_encoding: [{name: "Category Breakdown", color_field: "Category", shape_empty: true, size_empty: true, label_empty: true}]`.

**Edge cases:**
- Worksheet uses accessibility-safe palette (e.g., ColorBrewer schemes designed for grayscale distinguishability). Still fires; skill doesn't distinguish accessibility-safe palettes. User acknowledges per-fix.
- Worksheet XML is unreadable on some dashboard-bound sheets (a known platform gap). Emit `"unresolved"` sentinel per HC#5.
- Worksheet has Color plus Label populated (redundant encoding present). Does NOT fire; clears.

**Worked example:**
Dashboard `Regional Detail` has worksheet `Category Breakdown` with SUM(Sales) on Rows, Category on Color, and Shape/Size/Label all empty. Fires DPC-COLORSAFE-05. Severity Info. Desktop fix: "Add Category to Label or Shape shelf on Category Breakdown worksheet for redundant encoding."

***

## DPC-HEADFOOT-06: Header/Footer Presence

**Severity:** Info
**Signal source:** print_config
**Detection:** Print config declares no `<header>` or `<footer>` content (empty string, absent element, or explicit "none" value).

**Evidence pattern:** `print_header_content: null; print_footer_content: null; both_absent: true`.

**Edge cases:**
- Header set, footer empty (or vice versa). Fires Info-tier for the absent one only, not both.
- Print config unset entirely. Emit `"print-config-unset"` sentinel per HC#5.
- Header/footer contain only whitespace. Treats as absent; fires.

**Worked example:**
Dashboard `Q3 Executive Summary` has print config with `<header>` and `<footer>` both empty. Fires DPC-HEADFOOT-06. Severity Info. Desktop fix: "In File → Page Setup, add header (e.g., report title) and footer (e.g., page number, date) via the header/footer text fields."

***

## DPC-MARGINS-07: Margin Sanity

**Severity:** Info
**Signal source:** print_config
**Detection:** Print config declares margins outside the range 0.25 inches to 1.0 inches on any side (top, bottom, left, right).

**Threshold defense:** Tableau's default margin is 0.5 inches. Margins below 0.25 inches risk edge clipping on many consumer and office printers (typical unprintable margin is 0.15-0.20 inches per HP, Canon, and Epson printer specifications). Margins above 1.0 inches waste more than 20 percent of an 8.5"×11" page's horizontal space, which is typically considered excessive for dashboard content. Range 0.25 to 1.0 inches represents the ISO/ANSI-common defensible authoring range; anything outside is flagged as a candidate for review, not an outright error.

**Evidence pattern:** `margins: {top: "0.15in", bottom: "0.5in", left: "0.5in", right: "0.5in"}; violating_sides: ["top"]; violation_type: "below_minimum"`.

**Edge cases:**
- All four margins within range. Does NOT fire; clears.
- Print config unset. Emit `"print-config-unset"` sentinel per HC#5.
- Margins declared in different unit (mm, cm). Skill normalizes to inches before threshold comparison.
- One side violates, three sides clear. Fires with `violating_sides` listing only the violation.

**Worked example:**
Dashboard `Detail Grid` has print config declaring 0.1" top margin (rest at 0.5"). Fires DPC-MARGINS-07. Severity Info. Desktop fix: "Increase top margin to at least 0.25" in File → Page Setup → Margins."

***

## DPC-TEXTLEGIBLE-08: Text-Object Legibility at Print DPI

**Severity:** Warning
**Signal source:** worksheet XML + dashboard XML
**Detection:** Any dashboard text object or worksheet title/caption declares font size below 8 points.

**Threshold defense:** 8-point font at 300 dpi print rendering is commonly cited in print-typography guidance as roughly the readable floor for standard body text (e.g., Wheildon's Type & Layout work and Ars Typographica both treat sub-8pt body/callout text as a legibility risk, though exact effort-penalty figures vary by source and aren't independently verified here). Below 8pt, print quality also degrades on consumer printers due to ink bleed and pixel-quantization effects on font hinting. 8pt is treated as the defensible authoring floor; anything smaller is flagged as a print-legibility risk, not an absolute defect.

**Evidence pattern:** `sub_legible_text_objects: [{location: "worksheet:Sales Detail:caption", declared_size: "6pt", threshold: "8pt"}]`.

**Edge cases:**
- Text object declares size in a non-point unit (px, em). Skill normalizes to points (1pt ≈ 1.33px at 96 dpi) before threshold comparison.
- Text object is hidden or has `display: none` equivalent. Does NOT fire; skill only evaluates visible text.
- Font size inherited from workbook default (not explicitly declared). Emit `"unresolved"` sentinel per HC#5 unless inherited value can be resolved via workbook XML.
- Dashboard-level text object (in a zone, not a worksheet). Same rule applies; skill checks dashboard XML text-object declarations.

**Worked example:**
Dashboard `Sales Detail` has a worksheet caption declared at 6pt font. Fires DPC-TEXTLEGIBLE-08. Severity Warning. Desktop fix: "Increase caption font size to at least 8pt in worksheet caption editor."

***

## Failure Modes This Reference Prevents

- **Fabricating print-config defaults** — every print-config-dependent check has an explicit `"print-config-unset"` sentinel per HC#5. No assumed Tableau defaults.
- **Silent DPC-OVERFLOW-04 without routing** — HC#11 requires `routing_offered.dashboard_preflight: true` on this specific check.
- **DPC-COLORSAFE-05 false positive on redundant encoding** — 3-step check (Color populated AND all redundancy shelves empty) prevents flagging worksheets that use Color plus Label/Shape/Size.
- **DPC-MARGINS-07 without threshold defense** — the 0.25"-1.0" range is empirically grounded in consumer-printer unprintable-margin specs and defensible-authoring range norms.
- **DPC-TEXTLEGIBLE-08 without threshold defense** — the 8pt floor is grounded in print typography research (Wheildon, Ars Typographica).
- **Rule ambiguity on multi-signal cases** — precedence tie-breaks are locked (severity tier → check ID ascending).
- **Pixel-visibility gap fabrication** — DPC-OVERFLOW-04 and DPC-TEXTLEGIBLE-08 are XML-signal-based per HC#12; findings tier as Info where XML doesn't cover the visual concern fully.
