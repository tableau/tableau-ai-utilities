# Fanning Patterns (Locked)

Six canonical fanning patterns with detection signature and recommended fix. Every fix routes to `calc-writer` for the LOD authoring step.

## F1. Additive-measure doubling on many-to-many

**Signature.** Two tables joined many-to-many (both sides "many" on the key). SUM of an additive measure on either side doubles or worse.

**Example.** Orders and Returns joined on Order ID. Orders has multiple rows per Order ID (line items). Returns has multiple rows per Order ID (partial returns). SUM([Sales]) from Orders doubles because each Orders row is repeated by the fanout.

**Fix pattern.** LOD: `{FIXED [Order ID] : SUM([Sales])}`. Routes to `calc-writer` with pattern name `F1-fixed-lod-dedupe`.

## F2. Denominator inflation

**Signature.** Ratio measure (`SUM(X) / SUM(Y)`) where numerator and denominator come from different table sides of a fanout join. Ratio deflates because denominator grows faster than numerator.

**Example.** Sales / Orders count where Sales comes from Orders line-items and Orders count comes from a joined orders-header table. Header count fans out by line-item count.

**Fix pattern.** Two `{FIXED}` LODs at the correct grain, then the ratio. Routes to `calc-writer` with pattern name `F2-ratio-lod`.

## F3. Distinct-count mismatch

**Signature.** `COUNTD([Customer])` disagrees with the count users expect (for example a row count or a pre-join figure) because a joined table repeats customer rows. COUNTD itself still dedupes; the mismatch comes from comparing it with row-level counts or a differently scoped figure.

**Example.** Customer joined to Orders one-to-many. COUNTD([Customer]) at the Orders grain still returns unique customers (COUNTD dedupes), but downstream users assume the number reflects the pre-join count and get confused when metadata references disagree.

**Fix pattern.** Either move COUNTD onto the correct table via a relationship, or use `{FIXED : COUNTD([Customer ID])}` explicit-grain LOD. Routes to `calc-writer` with pattern name `F3-countd-explicit-grain`.

## F4. Bridge-table double-fanout

**Signature.** Two dimensions joined through a bridge (Products ↔ ProductCategories via ProductCategoryLink). Joining directly instead of relating both edges causes double-fanout: each product-category assignment multiplies both sides.

**Fix pattern.** Relate Products to Link and Categories to Link (both edges). Never join across the bridge. If already joined, unwind and re-model. Routes to `calc-writer` only if calcs need updating for the new grain.

## F5. Temporal-range fanout

**Signature.** Fact table joined to a slowly-changing-dimension via a date range (Effective Start / Effective End). A join expands each fact row by the number of overlapping dimension versions.

**Variants covered:**

- **F5a Type 2 SCD point-in-time join.** Fact.event_date BETWEEN Dim.effective_start AND Dim.effective_end. Fixed at delivery time by joining once against the "current" version (Effective End IS NULL).
- **F5b Type 2 SCD historical join.** Same but preserving history. Filter to a specific as-of date via a parameter, or use a relationship with the range predicate.
- **F5c Effective-date-only variants (no end date).** Fact.event_date >= MAX(Dim.effective_start WHERE effective_start <= event_date). Requires window function in the source or a manual LOD fallback.

- Type 6 SCD (hybrid current-plus-history columns).
- Bi-temporal dimensions (system time plus valid time).

**Fix pattern.** Filter to the current effective version at query time, or use a relationship with a range predicate. Routes to `calc-writer` if a calc needs to restrict the fact to the correct version. Pattern slug for `calc-writer` routing: `F5-scd-range-filter`.

## F6. Self-join fanout

**Signature.** A single table joined to itself (hierarchical parent-child, employee-manager). Aggregate measures on the parent side inflate by the child count.

**Fix pattern.** Explicit `{FIXED [Parent ID] : SUM(measure)}` LOD. Routes to `calc-writer` with pattern name `F6-self-join-fixed`.

## Detection Cadence

The skill runs fanning detection only against measures placed on shelves anywhere in the workbook. Unplaced measures are not checked (reduces noise on wide fact tables).

## Refuse to Fabricate

If a fanning symptom doesn't match F1-F6, report "outside current pattern catalog; consult manual grain-analysis docs" rather than inventing a pattern.
