# Section Catalog Reference
Locked reference file for workbook-summary-onepager's 5-section catalog. Cited by HC#3 and V1. Every section renders content or an empty-state prose fallback; no section is silently omitted. Each section below documents its signal source, detection criteria, evidence pattern, edge cases, and worked examples.

## Section Precedence

**Fixed ordering.** Sections render in locked order 1→5 per HC#7. No reordering across runs.

**Signal source preference.** Each section prefers a fresh upstream handoff when available; falls back to local-extract from workbook XML when the handoff is missing or stale (fingerprint mismatch per HC#13); falls back to empty-state prose when even local extract yields no data.

**Fingerprint staleness.** Each handoff consumed is verified against the current workbook fingerprint per portfolio-wide HC#15. Fingerprint mismatch forces local-extract fallback for that section.

***

## Section 1: What This Workbook Shows

**Purpose:** Plain-language description of the workbook's overall subject. Answers "what would I tell a colleague this workbook is about?"

**Signal source (preferred):** Workbook-level author caption from `get-workbook-inventory` if present.

**Signal source (fallback):** Aggregated dashboard titles from `get-dashboard-xml` across all dashboards; skill composes a 2-3 sentence summary connecting the dashboard themes.

**Empty-state prose:** "No workbook-level description available. This workbook contains N dashboards covering [list first 3 dashboard titles]."

**Evidence pattern:** `workbook_caption: "Q3 sales performance across regions, products, and customer segments" | null; dashboard_titles: ["Executive Overview", "Regional Sales", "Product Detail"]`.

**Edge cases:**
- Workbook caption is present but empty (whitespace only). Treated as null; fall back to dashboard-title aggregation.
- Workbook has 0 dashboards (data-source-only workbook). Empty-state: "This workbook has no dashboards; it contains only data sources and worksheets."
- Workbook caption is longer than 200 characters. Preserved verbatim (HC#6); Tier A may truncate for display but full text lands in Tier B.

**Worked example:**

Workbook has an author caption "Q3 sales performance across regions, products, and customer segments — for exec review 2026-09." Fires **Section 1: What this workbook shows.** Content: verbatim author caption. `signal_source: handoff` (workbook caption is a workbook-level signal, not from an upstream skill). Desktop fix (Tier A): none; this section is descriptive, not diagnostic.

***

## Section 2: Key Metrics Defined

**Purpose:** Top 5 most-referenced calculated fields, giving the reader a sense of the workbook's key metrics.

**Signal source (preferred):** `calc_documentation/1` handoff → extract top 5 calcs by `used_by_count` from the reference graph.

**Signal source (fallback):** Local-extract via `list-available-fields` on the primary datasource; rank by name-recency (weaker signal). Explicit label: "ranked by naming order; run calc-documenter for reference-graph-based ranking."

**Empty-state prose:** "No calculated fields defined in this workbook."

**Evidence pattern:** `top_metrics: [{name: "Profit Ratio", used_by_count: 8, aggregation: "aggregate"}, {name: "Sales YoY", used_by_count: 6, aggregation: "table-calc"}, ...]`.

**Edge cases:**
- Fewer than 5 calcs exist. Render all available calcs; empty-state prose amends the count ("This workbook defines 3 calculated fields, listed below.").
- Handoff is stale (fingerprint mismatch). Skill falls back to local-extract per HC#13 and labels: "Handoff was stale; used local extract."
- Two or more calcs tied on `used_by_count`. Deterministic tiebreak: name ascending.
- Calc names contain multiple datasources' calcs of the same name. Skill prefixes with datasource: `Orders.Profit Ratio` vs `Returns.Profit Ratio`.

**Worked example:**

Workbook has a fresh `calc_documentation/1` handoff with 25 calcs. Top 5 by `used_by_count`: Profit Ratio (8), Sales YoY (6), Regional Sales (4), Order Profitable? (3), Customer Segment (3). Fires **Section 2: Key metrics defined.** `signal_source: handoff`. Tier A output lists all 5 with their aggregation types.

***

## Section 3: Data Sources Used

**Purpose:** Per-datasource summary with row count and relationship shape.

**Signal source (preferred):** `data_model_documentation/1` handoff → extract per-DS summary with row_count and relationship_shape.

**Signal source (fallback):** Local-extract from `get-workbook-inventory` datasource enumeration; `row_count: unknown` sentinel per HC#4 (skill does not query the data itself, out of scope per read-only-structural rule).

**Empty-state prose:** "This workbook has no data sources loaded." (rare, only fires on empty workbooks)

**Evidence pattern:** `datasources: [{name: "Orders", row_count: 9994, relationship_shape: "flat"}, {name: "Returns", row_count: 296, relationship_shape: "one-to-many-with-Orders"}]`.

**Edge cases:**
- Handoff is stale. Fallback to local-extract with `row_count: unknown` sentinel per HC#4.
- Datasource is a live connection. `row_count: live` sentinel (not `unknown`; distinguishes from staleness).
- Datasource is a published data source. `source_type: published` field populated.
- Cross-datasource relationships defined. `relationship_shape` describes the join or blend cardinality.

**Worked example:**

Workbook has fresh `data_model_documentation/1` handoff. Two datasources: Orders (9994 rows, flat), Returns (296 rows, one-to-many with Orders). Fires **Section 3: Data sources used.** `signal_source: handoff`. Tier A output lists both with row counts and the join shape.

***

## Section 4: Dashboards Included

**Purpose:** Dashboard names with title/caption presence flags. Reader can tell which dashboards ship with clear titles and which need review before handoff.

**Signal source (preferred):** `caption_audit_report/1` handoff → extract dashboard names with `title_present` and `caption_present` flags.

**Signal source (fallback):** Local-extract from `get-workbook-inventory` dashboard enumeration; `title_present: unknown` sentinel when `get-dashboard-xml` is unreadable per HC#5 (reliability gap on dashboard-bound sheets).

**Empty-state prose:** "This workbook has no dashboards; it contains only worksheets and data sources."

**Evidence pattern:** `dashboards: [{name: "Executive Overview", title_present: true, caption_present: true}, {name: "Regional Detail", title_present: true, caption_present: false}]`.

**Edge cases:**
- Handoff is stale. Fallback to local-extract with `title_present: unknown` sentinels.
- Dashboard is hidden. `hidden: true` flag populated; still listed in Section 4 (hidden dashboards are part of the workbook, worth surfacing for handoff).
- Dashboard has 10+ zones (per HC#15). No truncation at section level; wide-workbook handling kicks in only if dashboard count exceeds 10.
- Dashboard is in a story. Story membership is metadata, not a filter; still listed in Section 4.

**Worked example:**

Workbook has fresh `caption_audit_report/1` handoff. 3 dashboards: Executive Overview (title yes, caption yes), Regional Detail (title yes, caption no), Product Detail (title no, caption no). Fires **Section 4: Dashboards included.** `signal_source: handoff`. Tier A output lists all 3 with flags; also flags Product Detail as "review before handoff" (both title and caption missing).

***

## Section 5: Known Limitations

**Purpose:** Author-declared limitations of the workbook. Answers "what won't work here?" or "what caveats does the reader need?"

**Signal source (preferred):** Workbook-level author caption's "Known limitations:" or "Limitations:" section (if declared).

**Signal source (fallback):** Empty-state prose. Skill does not infer limitations; only surfaces what the author explicitly declared.

**Empty-state prose:** "No known limitations documented in workbook caption. Reader should confirm scope with the workbook author before basing decisions on this content."

**Evidence pattern:** `author_declared: true; limitations_text: "Q3 data only; Q4 not yet loaded. Regional Sales dashboard uses estimated Sept figures pending month-end close." | null`.

**Edge cases:**
- Workbook caption has no "Known limitations" section. Empty-state prose per HC#11.
- Workbook caption has a "Caveats:" or "Notes:" section (variant heading). Skill accepts variant headings: "Known limitations", "Limitations", "Caveats", "Notes", "Warnings" (case-insensitive).
- Limitations text is longer than 500 characters. Preserved verbatim per HC#6; Tier A may truncate for display but full text lands in Tier B.

**Worked example:**

Workbook has an author caption containing "Known limitations: Q3 data only; Q4 not yet loaded." Fires **Section 5: Known limitations.** `signal_source: handoff` (workbook caption). `author_declared: true`. Content: verbatim limitations text.

**Contrasting worked example (empty-state):**

Workbook has no author caption at all. Fires **Section 5: Known limitations** with empty-state prose: "No known limitations documented in workbook caption. Reader should confirm scope with the workbook author before basing decisions on this content." `signal_source: empty_state`. `author_declared: false`.

***

## Failure Modes This Reference Prevents

- **Silent section omission.** HC#3 requires all 5 sections; reference file's empty-state prose per section prevents skipping when signal is missing.
- **Fabricated row counts / metric values.** Section 3 uses `unknown` sentinel per HC#4 when handoff is stale or absent; never guesses.
- **Rewriting author caption.** Section 1 and Section 5 both preserve author caption verbatim per HC#6; skill never paraphrases.
- **Silent staleness rendering.** HC#13 fingerprint verification blocks silent stale-data output; falls back to local-extract with clear labeling.
- **Auto-invoking upstream skills.** HC#9 opportunistic-only consumption; skill never chains-calls calc-documenter / data-model-documenter / dashboard-caption-audit on behalf of the user.
- **Section-count drift.** Locked 5-section catalog per HC#3; no fabricated sections, no reordering across runs.
