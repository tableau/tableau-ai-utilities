---
name: data-scribe
description: "Use when the user says 'Document this data source', 'metric dictionary', 'what do these fields mean?', 'data dictionary'. Builds a field-level dictionary file: what each field is, how calcs work, sample values, and which sheets use it."
---

# Data Scribe

You are a documentation generator for a connected Tableau Studio datasource. Pure read-path plus one file write: inspect fields, read calc logic, sample values, map usage, and produce a shareable metric dictionary. One datasource per run.

**Why this shape:** opening someone elses workbook (or your own from months ago) and reverse-engineering every field by hand is tedious and error-prone. This skill automates the inspect-each-field loop and produces a durable artifact instead of a chat-only answer.

***

## When to use (full trigger detail)

Generate a field-level metric dictionary (markdown/text file) from a connected Tableau Studio datasource — what each field is, how calcs work, sample values, and which sheets use it. Trigger on document this datasource, metric dictionary, field dictionary, what do these fields mean, data dictionary, define these metrics, I inherited this workbook, whats in it, onboarding doc for this data, export field documentation. Do NOT trigger for. data quality issues like nulls/dupes/outliers (defer to data-quality-review), building or editing charts/dashboards/calcs (defer to a calc-authoring or dashboard-building skill if available), or describing what a worksheet visually SHOWS rather than what its fields ARE. Disambiguation from data-quality skills. those ask is this data clean?; this skill asks what does this data mean? — same fields, different question.

## Tools You Use

| Tool | Purpose |
|------|---------|
| `get-workbook-inventory` | Discover datasources, sheets, workbook file location (for output path). |
| `list-available-fields` (verbosity: full) | Full field list with type/role AND, for calcs, the actual `formula` text — this is the PRIMARY source for calc logic, not XML inspection. |
| `get-worksheet-xml` | Fallback only, if a calcs `formula` comes back missing/blank from `list-available-fields`. |
| `add-worksheet` | Create a scratch sheet for sampling, if no empty sheet is available. |
| `add-field` (target: encoding, encodingType: detail) | Stage fields on the scratch sheets Detail shelf for sampling, batched 5-6 at a time. |
| `get-summary-data` | Read sample values / min / max / avg for staged fields. |
| `delete-sheet` | Remove the scratch sheet after sampling — always, even on partial failure. |
| `resolve-field` | One-shot attempt to resolve a parameters current value/domain (see Phase 3). Never call `author-parameter` for this — it has a known deterministic crash on this platform. |
| Write | Produce the `.md`/`.txt` file on disk. |

***

## Hard Constraints

### Behavioral Rules
1. **Never present an inferred description as fact.** Descriptions are guessed from field names, sample values, and usage context. Flag uncertain ones inline: `[Inferred: likely represents customer lifetime value. Verify with data owner.]`
2. **Scratch sheet cleanup is mandatory.** If you create one via `add-worksheet`, delete it with `delete-sheet` when sampling finishes — including on early exit or partial failure. The workbook must look the same before/after, minus the new file on disk.
3. **Scope is one datasource.** If the workbook has multiple, ask which one (or offer all of them as a multi-run option).
3b. **Sets and Hierarchies are out of scope for automated discovery.** No inventory tool reliably enumerates Sets or Hierarchies the way it does dimensions/measures/calcs. If the output templates Sets/Hierarchies sections would otherwise appear, state plainly in the Notes section: Sets/Hierarchies not scanned this run — no reliable discovery tool for this environment; check Desktops Data pane manually. Do not omit the caveat silently, and never fabricate a Set or Hierarchy entry from inference alone.
3a. **Never modify a calculated field.** This skill is documentation-only for calc logic — it reads `formula` from `list-available-fields`/`get-worksheet-xml`, it never calls `author-calc`, and it never edits an existing calcs definition, not even to fix something found broken during Phase 2 extraction. If a calc looks broken, report it in the output/Notes and defer any fix to the user or to a calc-authoring skill if one is available — do not touch it. This also applies transitively to Phase 4 sampling: the scratch-sheet build (whether via `add-field` or the `build-and-apply-worksheet` fallback) must only place fields on shelves/encodings — if a sampling step appears to have altered an existing calcs formula (confirmed a real occurrence once: a calc broke mid-run with no `author-calc` call in between), stop, do not attempt an in-skill fix, and tell the user exactly which calc and when in the sequence it was last known-good.
4. **Blocking modal awareness.** Tableau Studio has no command to dismiss an error dialog once one opens — it blocks the single UI thread, and every later tool call queues behind it instead of failing cleanly (it can look like a hang, a timeout, or a garbled/unexpected result). Prevention is the only lever:
   - Always validate a worksheet/dashboard name against a fresh `list-worksheets` call before navigating to it. Use `activate-sheet` (which validates internally).
   - If a tool call returns no response, times out, or comes back with a garbled/unexpected result right after a document-mutation call (`add-field`, `add-worksheet`, `author-calc`, etc.), stop issuing further calls immediately. Tell the user plainly: Desktop may have a blocked dialog open — please check and dismiss any error popup before I continue. Do not retry blind; retries queue behind the same blocked thread and wont recover the session on their own.

### Output Conventions
4. **Output file location:** write next to the open workbook. Get the path from `get-workbook-inventory`s `location` field (the `.twb`/`.twbx` path) and write the dictionary into that same folder. Default filename: `[datasource-name]_metric_dictionary.md`.
5. **Calc ordering:** output calculated fields in dependency order — leaf calcs first, compound calcs after the calcs they reference — so the file reads top-to-bottom without forward references.
6. **Overflow grouping (50+ calcs):** when the datasource has 50+ calculated fields, group them by type (LOD, Table Calc, Basic, String/Date, Conditional) with sub-headers rather than rendering one flat list.
7. **Multi-table / blended datasources:** render a unified field list (not grouped by source table). Add a **Source Table** property to each field entry so the reader knows where it originates. For fields that appear in multiple tables (e.g. a join key), list once with all source tables noted. If a relationship or blend introduces granularity ambiguity (fanout risk), add a one-line note under the field: `[Note: appears at [grain] in [table] — joins may duplicate rows at finer grain.]`

***

## Workflow

### Phase 0 — Orientation & Scope

1. Call `get-workbook-inventory` to list datasources, sheets, and the workbook file path (needed later for output location).
2. **Tool-health check:** before investing effort in Phases 1-3, make one cheap probe call (e.g. `get-summary-data` on any sheet named in the inventory) to confirm document/mark-level tools are actually responding. If it fails with a server/operation error (not just empty sheet), the environment has a systemic tool outage — tell the user plainly (Desktops document tools arent responding right now — field inventory and calc extraction may still work, but sample values and usage mapping wont. Want me to proceed with a partial run, or wait?) before continuing, rather than discovering the outage mid-Phase-4.
3. **Unsaved/temp workbook path:** if `location` from `get-workbook-inventory` resolves inside a temp directory (e.g. contains `Temp\TableauTemp`, `AppData\Local\Temp`, or similar OS temp patterns), dont assume its writable/durable. Proactively ask the user where to save the dictionary instead of defaulting to that folder.
4. If multiple datasources exist, ask which to document.
4a. **Blend vs. relationship distinction (setup confusion is real and common):** before treating any datasource as blended, confirm its genuinely a separate datasource object in the workbook, not a Tableau relationship producing a single combined federated datasource (which often shows a caption suffixed with `+`, e.g. `X+`, and surfaces every related tables fields under one `datasource` entry in `list-available-fields`). A true blend means two independent datasource entries exist, and the blend link only becomes visible/active when a worksheet combines fields from both. If a user describes something as blended but `list-workbook-datasources` shows only one combined entry, say so plainly before proceeding — dont silently document it as a blend when its actually a relationship model (see Multi-table rule #7 for that case instead).
5. If the user names a subset (just the calcs, only measures), scope accordingly and note which phases to skip:
   - just calcs → run Phases 1-2-3 only, skip Phases 4-5. Assemble output with Calc and Parameter sections only.
   - only measures → run Phases 1-4-5, skip Phase 2-3 calc extraction for non-measure calcs.
6. If a dictionary file with the target filename already exists in that folder, ask: Update the existing dictionary with new/changed fields, or regenerate from scratch? If the user chooses **Update**: match fields by name between the existing file and the new inventory. Preserve any non-empty Description that differs from a purely inferred one (the user likely edited it manually). Append newly discovered fields at the end of their respective section. Flag fields present in the old dictionary but absent from the current inventory as `[Removed — no longer in datasource as of this run]` rather than silently deleting them. Recalculate the summary header counts to reflect the current state.
7. **Output format:** ask the user which file format they want — plain text (`.txt`) or Markdown (`.md`). Do not default silently to `.md`. (Word/`.docx` is not currently supported in this environment — no document-conversion tool is installed — so dont offer it unless that changes.)

### Phase 1 — Field Inventory

1. Call `list-available-fields` (verbosity: full) on the target datasource.
2. **Early exit:** If the call returns empty or errors, the datasource is likely disconnected or in an error state. Report: No fields returned — verify the datasource is connected and refresh the extract if applicable. Stop.
3. **Fast-path for small datasources:** If ≤15 fields total, skip any document all or subset? question — document everything without asking.
4. Classify every field: Dimensions, Measures, Date/Time fields, Calculated fields (anything with a non-empty `formula` and `derivation: User`), Groups/Bins (formula is a bare field reference with a `(group)`/`(bin)`-style caption), Hierarchies (if present in the inventory).
5. Note field counts per category for the summary header.
6. **100+ fields:** dont sample all of them. Ask: This datasource has [N] fields — document all, or just [calcs / measures / a named subset]? If proceeding with all, sample measures (min/max/avg) and high-cardinality dimensions only; give low-cardinality dimensions (<20 members) full member lists. Process in batches of ~20.
7. **300+ fields:** default to documenting only measures and high-cardinality dimensions unless the user explicitly opts into full coverage. Warn: This datasource has [N] fields — full sampling will take significant time. Documenting measures and key dimensions by default. Say all if you want everything.
8. **300+ fields, user says all (family-level summary rule):** treat all as a request for full field *coverage* in the output, not a literal instruction to individually sample every field regardless of cost. If multiple fields share a detected naming pattern (e.g. a numbered suffix like `Cost M01`...`Cost M24`, `Score 001`...`Score 100`) or get flagged as near-duplicates by the tooling during sampling (a warning like dataset has near-duplicate columns X/Y/Z... from `build-and-apply-worksheet`), group them into a single field-family entry in the output rather than sampling and writing up every member individually:
   - List every field name in the family so none are dropped from coverage.
   - Sample 2-3 representative members (first, middle, last) for real values instead of all of them.
   - Disclose explicitly, per family, that a representative-sampling approach was used and why (e.g. 24 near-duplicate monthly columns, 2 sampled).
   - This applies per-family — a 300+ field datasource without repetitive naming patterns should still get full individual documentation as normal; only apply this shortcut where genuine repetition is detected.

### Phase 2 — Calculated Field Extraction

For each calc found in Phase 1:

1. **Primary path:** use the `formula` field already returned by `list-available-fields` — no extra tool call needed. This covers the common case (verified: e.g. `SUM([Profit])/SUM([Sales])`, `IF [Parameters].[...] = "Sales" THEN ... END`).
2. **Fallback only** if `formula` is missing/blank for a calc: call `get-worksheet-xml` on a sheet that uses it and extract the calc definition from there. If still unreadable, record: Formula not extractable via current tools — flagged for manual inspection.
3. From the formula text, identify: referenced fields/calcs (dependencies), calc type (basic / LOD FIXED-INCLUDE-EXCLUDE / table calc / string / date / conditional), and any `[Parameters].` references.
4. Write a one-sentence plain-English explanation, avoiding jargon where possible.
5. Build the dependency chain: which other calcs reference this one (scan all calc formulas for this calcs name/caption).
6. **Circular reference check:** if calc A references calc B and calc B (directly or transitively) references calc A, do not attempt to resolve a linear ordering. Flag both calcs explicitly: Circular reference detected between [A] and [B] — dependency order not determinable. List them together at the end of the Calculated Fields section rather than silently picking an arbitrary order or dropping either one.

### Phase 3 — Parameter Documentation

**Parameters are not directly enumerable by any inventory tool.** Discover them only by scanning the formula text collected in Phase 2 for `[Parameters].[...]` references.

For each parameter found this way:

1. Record its name as it appears in the formula.
2. Make **one attempt** to resolve current value/domain via `resolve-field` on the parameter name. Never call `author-parameter` to probe it — it has a known deterministic crash on this platform (Windows ENOENT on reopen).
3. If that one attempt doesnt yield a usable value/domain, stop trying and record: Allowable values: unknown — check parameter definition in Desktop. Do not retry or dig into XML for this.
4. Write a one-sentence purpose statement inferred from how the calc uses it (e.g. toggles which measure is displayed).
5. List which calcs reference it.

If no `[Parameters].` reference turns up in any calc formula, state plainly that no parameters were found via calc scanning — this does not guarantee none exist, only that none are wired into visible calc logic.

### Phase 4 — Sample Value Enrichment

**Skip this phase entirely if the user scoped to just calcs.**

For dimensions, date fields, and string measures (skip for calcs already fully described by their formula):

1. Find or create a scratch worksheet. Prefer an existing empty sheet; otherwise call `add-worksheet` and read the new sheet's name from `get-workbook-inventory`.
2. Batch up to 5-6 fields at a time onto the scratch sheets Detail encoding via `add-field`.
3. Call `get-summary-data` once per batch to pull real values.
4. Record 3-5 representative values per field (for high-cardinality fields: min/max/sample instead of a full list). **Cardinality thresholds (locked):** Low = fewer than 10 distinct values (record full member list), Medium = 10-50 (record full member list unless it makes the entry unreadably long, in which case sample the top 10 by row count plus a total count), High = more than 50 (record 3-5 sample values plus the count only, never attempt a full list).
5. For date fields: record earliest/latest.
6. For measures: record min, max, avg from the summary data.
7. If a field returns no data (all NULL, disconnected), record No data available and continue — dont fail the whole run.
8. **When sampling is done, delete the scratch sheet** via `delete-sheet` (skip this if you reused an existing sheet — restore it to its prior field state instead by removing the fields you added).

**Fallback if `add-field`/`get-worksheet-xml` fail:** if `add-field` returns a server/operation error rather than a normal failure, dont retry it repeatedly — that risks stacking calls behind a stuck dialog per Blocking Modal Awareness above. See the hard stop below before reaching for `build-and-apply-worksheet` as a substitute — it is not a safe fallback for a datasource with parameter-referencing calcs.

**Hard stop: no worksheet-mutation sampling when parameter-referencing calcs exist (confirmed, unresolved corruption risk).** Across three separate test runs, a `build-and-apply-worksheet` call during Phase 4 sampling coincided with an unrelated parameter-referencing calc becoming corrupted in Tableau Studios engine, with no `author-calc` call from this skill in between. Formula-text comparison via `list-available-fields` does **not** reliably detect this — the corrupted calcs formula text can read back character-identical to its healthy state while still being broken in Desktop. Because there is no reliable way to detect or prevent this with the tools available to this skill:
- If the datasource being documented contains **any** calc referencing a parameter (`[Parameters].[...]` in its formula), do not call `build-and-apply-worksheet`, `add-field`, or any other worksheet-shelf-mutating tool during Phase 4 for that datasource, full stop — no exceptions, no just this one field fallback.
- In that case, Phase 4 for measures/dimensions becomes formula/name-only: document what the field is from its formula and metadata, and state plainly in the output that sample values were not gathered because worksheet-based sampling is unsafe on this datasource until the underlying corruption is understood. Do not attempt a workaround.
- If the datasource has **no** parameter-referencing calcs at all, the `add-field` → `build-and-apply-worksheet` fallback path above may still be used, since the corruption has only ever been observed on datasources with parameter-referencing calcs.

**Live vs. extract note:** On live connections, `get-summary-data` latency scales with datasource size. For very large live connections (300+ fields or known-slow queries), consider sampling only the first 100 rows (`maxRows: 100`) to keep response time reasonable. For cloud-hosted connections (Snowflake, BigQuery, Databricks, Redshift), expect higher per-query latency than local extracts; if a sampling call times out or returns a credential-refresh error, treat it as the cloud connection dropping rather than a tool outage. Record Cloud connection timeout — retry after re-authenticating in Desktop for affected fields and continue.

**Sampling depth floor:** for measures, always capture at minimum a grand-total `SUM` (one cheap call per measure) rather than skipping a subset silently. If full row-level min/max/avg isnt feasible within a reasonable tool-call budget, say so explicitly in the outputs Notes section — dont let partial coverage look like complete coverage.

**Blended (not related) datasources — a real tool limitation:** `build-and-apply-worksheet` refuses to bind fields from two different datasources onto one template (errors with `[cross-datasource-binding]`) — it supports single-datasource templates and Tableau relationships, but has no path for classic worksheet-level data blending. If sampling a blends cross-datasource behavior (e.g. confirming which field is the active blend link), this skill cannot construct that verification worksheet itself: ask the user to build the minimal blend worksheet manually in Desktop, then read it back via `get-summary-data` only. Sampling each blended datasources own fields independently (not the cross-datasource interaction) is unaffected and can proceed normally.

### Phase 5 — Usage Mapping

**Skip this phase entirely if the user scoped to just calcs.**

1. From `get-workbook-inventory`s sheet list, check each sheets shelves/encodings to see which fields are placed.
2. Build Field → [sheets using it].
3. Flag fields used on 0 sheets (defined but never placed) and fields used on 5+ sheets (core metrics).

### Phase 6 — Assembly & Output

1. Assemble findings into the template at `skill-expertise/output_template.md`.
2. **Pre-write validation:** Compare the count of fields documented in the assembled output against the total field count from Phase 1. If theres a mismatch (fields were dropped during processing), identify the missing fields and re-process them before writing. Do not write an incomplete dictionary.
3. **Dependency order check:** Scan the Calculated Fields section to confirm no calc references another calc that appears later in the document. If a forward-reference exists, reorder to fix it.
4. **Sets/Hierarchies omission check:** if the Sets or Hierarchies sections are empty, confirm this reflects a genuine absence (no Set/Hierarchy fields turned up in Phase 1s inventory) rather than a silent skip — if genuinely absent, omit the section per the templates rule; if its unclear whether any exist (no reliable discovery tool, per Hard Constraint #3b), include the explicit not scanned this run caveat instead of a bare omission.
5. Write the file to the workbooks folder (from Phase 0) as `[datasource-name]_metric_dictionary.md` (or `.txt` if requested).
6. Report the file path to the user, plus a one-line summary (field counts by category, any flagged/uncertain items).

***

## Error Handling

| Failure | Recovery |
|---|---|
| `get-workbook-inventory` fails or returns no workbook | No workbook is open. Tell the user: No workbook detected — open a workbook with a connected datasource and try again. |
| `list-available-fields` returns empty | No datasource connected or datasource in error state — report and stop (see Phase 1 early exit). |
| Calc formula missing from inventory AND from XML fallback | Report the calc exists but formula is not extractable via current tools. Flag for manual inspection. Continue with other fields. |
| Sample data returns empty for a field | Record No data available. Continue with the rest. |
| Scratch sheet creation fails | Use an existing empty sheet instead. If none exists, tell the user: Cannot sample values without a scratch sheet — create an empty worksheet and Ill retry. |
| Scratch sheet deletion fails | Warn the user: A temporary worksheet named [X] could not be deleted automatically. Please remove it manually to keep the workbook clean. Continue with file output — dont block the dictionary on cleanup failure. |
| A document-mutation call (`add-field`, `add-worksheet`, `author-calc`, etc.) times out, hangs, or returns a garbled/unexpected result | A blocking Desktop dialog may be open (see Blocking Modal Awareness). Stop issuing further calls immediately — do not retry. Tell the user: Desktop may have a blocked error dialog open — please check and dismiss any popup before I continue. Wait for confirmation before resuming. |
| Parameter value/domain not resolvable after one attempt | Record Allowable values: unknown — check parameter definition in Desktop. Dont retry further. |
| Output path unwritable (e.g. workbook not yet saved, no folder path) | Ask the user where to save the file instead. |
| A fields sample query returns an access-denied/permission error (row-level security) | Record Access restricted — cannot sample (row-level security or permission denial). Continue with other fields; dont treat this as a systemic outage. |
| `get-summary-data` returns fewer rows than the requested `maxRows` | Treat the returned rows as the full available sample for that field/query — dont retry assuming an error, and dont pad the output with fabricated additional values. |

***

## Composability

- **Upstream:** offer proactively right after a new datasource connects — Want me to generate a metric dictionary for this? Also offer after schema changes or datasource refreshes when an existing dictionary is detected — Your datasource schema may have changed since the last dictionary. Want me to diff and update it?
- **Downstream:** the dictionary can inform viz-planning skills (core metrics vs. supporting fields), calc-authoring skills (existing calc inventory before writing new ones), and data-quality skills (field context for what clean means per field).
- **Adjacent:** data-quality skills cover the same fields but ask a different question (clean? vs. what does it mean?).
- No workbook mutations survive this skills run except a temporary scratch sheet, always cleaned up.

## Graceful Degradation

These rules apply whenever something this skill needs is missing or fails. More specific rules elsewhere in this file take precedence.

- **Nothing to work on.** If no workbook is open, there is no data source, or the named calc, sheet, dashboard, or data source isn't found, stop before any other step. Say what you found (list the real names, if any) and ask the user to open the workbook or pick one. Never work on a guessed or closest-match target.
- **Tool call fails, times out, or returns empty.** Retry once, then stop retrying. Mark everything that depended on that call as not checked, continue with what you still can, and say which step failed. If the failed call was a write, stop and report the workbook's current state instead of continuing.
- **Partial results.** If any check, sheet, field, or data source wasn't evaluated, the summary says so (Partial: N of M checked; not checked: [list]). Never give a clean, ready, or PASS verdict on a partial run.
- **Reference file won't open.** Use the rules summarized in this file, say [file] unavailable; using the built-in summary, and never make up thresholds, rule IDs, or Desktop menu steps from memory.
- **Peer skill not installed.** If this skill would hand off to another skill that isn't available, say so and give the manual Desktop step instead. A handoff is never the only next step.
- **Platform gap.** If no tool can do something, say so plainly and give the manual Desktop path.
- **Failure messages.** Tell the user in plain language what was done, what wasn't, and the next step. No raw errors, stack traces, or JSON.
- **No fabrication.** Never invent fields, values, findings, or results to fill a gap left by a failed read.
