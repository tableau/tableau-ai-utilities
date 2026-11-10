---
name: workbook-auditor
description: "Use when the user says 'What changed in this workbook?', 'did anyone edit this calc?', 'take a snapshot of this workbook', 'save a baseline'. Saves a baseline file of fields, calcs, sheets, and dashboards (not a screenshot) and reports what changed since the last one."
---

# Workbook Auditor

You track change in a Tableau workbook over time. A single snapshot/diff mechanism serves two asks: a narrow one (did this calc change?) and a broad one (what changed since I last opened this?). Read-path plus one file write per run (the snapshot). No calc mutation, ever.

**Why this shape:** workbooks get handed between collaborators, or sit untouched for months, with no changelog. Reconstructing what changed by memory or by re-reading every calc is exactly the kind of tedious, error-prone loop this skill automates — the same rationale as `data-scribe`, applied to change instead of meaning.

**File structure:** SKILL.md (this file) + `skill-expertise/report_template.md` (locked output format for both modes) + `skill-expertise/snapshot_schema.md` (JSON schema for snapshot files, including cross-skill consumption guidance).

***

## When to use (full trigger detail)

Snapshot a workbooks fields, calcs, sheets, and dashboards, then diff the current state against a saved baseline to produce a plain-English what changed digest — new/removed/renamed fields, calc formula edits, new or removed sheets/dashboards. Two purposes, one snapshot/diff mechanism. (1) calc/field-level change tracking for governance, (2) whole-workbook change digest for handoffs between collaborators. Trigger on what changed in this workbook, did anyone edit this calc, compare to last version, change digest, audit changes, field/calc change history, diff this workbook, snapshot this workbook, whats different since I last opened this, track changes to this datasource. Do NOT trigger for. data quality issues like nulls/dupes/outliers (defer to data-quality-review), what a field MEANS rather than whether it changed (defer to data-scribe), building or editing charts/dashboards/calcs (defer to an authoring skill), or pre-publish hygiene checks like unused fields/default sheet names (defer to publish-readiness). Disambiguation from data-scribe. that skill documents meaning once; this skill tracks change over time via repeated snapshots.

## Tools You Use

| Tool | Purpose |
|------|---------|
| `get-workbook-inventory` | Sheets, dashboards, storyboards, workbook file location (for snapshot path). Does NOT enumerate datasources — use `list-workbook-datasources` for that. |
| `list-workbook-datasources` | The actual datasource list for the workbook (Mode B needs this to know how many datasources exist and their names before looping `list-available-fields` per one). Also the source for `connection_type`/`luid` where available — see Hard Constraint #9 on unverified fields. |
| `list-available-fields` (verbosity: full) | Full field list with type/role and calc `formula` text — the snapshots core content. |
| `get-worksheet-xml` | Fallback only, if a calcs `formula` comes back missing/blank from `list-available-fields`. Avoid on dashboard-bound sheets (known 500/`operation-failed` reliability gap). |
| `list-worksheets` / `list-dashboards` | Confirm current sheet/dashboard names for the digests structural-change section. |
| Read | Load the prior snapshot file for comparison. |
| Write | Save the new snapshot file after producing the digest. |

**Sequencing and batching:**
- Mode A: `list-available-fields` first (single call), then Read (snapshot file), then diff logic, then Write (if confirmed).
- Mode B: call `list-workbook-datasources` FIRST — this is the only tool that actually enumerates datasources; nothing else in this workflow can substitute for it. Its result is a prerequisite for the per-datasource `list-available-fields` loop below, so it cannot be batched with the other three. `get-workbook-inventory`, `list-worksheets`, `list-dashboards` are independent of each other and of `list-workbook-datasources` — issue those three together. Then `list-available-fields` per datasource, processed in the order returned by `list-workbook-datasources`. Each datasources field call is independent of the others.
- **`get-worksheet-xml` fallback cap:** limit to max 5 calcs per run. If more than 5 calcs have unreadable formulas from `list-available-fields`, report the extras as formula not extractable this run in bulk rather than hammering an unreliable tool.

***

## Hard Constraints

1. **Never mutate a calc, field, sheet, or dashboard.** This skill only reads and diffs. If a change looks like a mistake (a broken formula, an accidentally renamed field), report it — never fix it, and never offer to fix it as part of this skills own flow. Defer to a calc-authoring skill.
2. **A snapshot is the unit of comparison, not workbook history.** There is no tool that reads version history or prior save states. What changed always means changed since the last snapshot this skill took — say so explicitly the first time a user runs this skill against a workbook with no prior snapshot (nothing to diff against yet; this run just establishes the baseline).
3. **Formula-text diffing is textual, not semantic.** A formula thats been reformatted (whitespace, reordered `IF`/`ELSEIF` branches) but is logically identical will still show as changed. Report it as a **formula edit** without claiming to know whether behavior actually changed — dont editorialize past what the diff shows.
4. **Renames must be inferred carefully.** No tool reports a rename directly — a rename looks identical to field removed + field added. Only infer a rename when a removed field and an added field share the same `dataType` and `role`, and — for calcs — formula text that is identical after whitespace normalization (defined below). Otherwise report them as a separate removal and addition, not a guessed rename. State the inference plainly: `[Inferred rename: Old Name → New Name — same formula/type, name changed]`.
   **Whitespace normalization for formula comparison:** (1) Strip all comments (`// ...` to end-of-line and `/* ... */` blocks). (2) Trim leading/trailing whitespace from the full string. (3) Split on any whitespace (spaces, tabs, newlines) and rejoin with a single space — this collapses all runs and treats line breaks as equivalent to a space. (4) Compare the resulting strings directly (case-sensitive — do not lowercase, since Tableau string literals are case-sensitive). This is safe because Tableau calc syntax has no semantically load-bearing whitespace. If the normalized formulas match, the formulas are considered identical for rename-inference purposes. Reordered branches, changed logic, or altered string literals are NOT whitespace differences and will correctly fail this check.
5. **Snapshot file location:** write next to the workbook, same convention as `data-scribe` — get the path from `get-workbook-inventory`s `location` field. Default filename: `[datasource-name]_snapshot.json` for field/calc snapshots, `[workbook-name]_workbook_snapshot.json` for whole-workbook snapshots.
   **Temp-path detection (locked substring check):** check the resolved `location` path (case-insensitive) for any of these substrings: `\Temp\`, `/Temp/`, `AppData\Local\Temp`, `TableauTemp`, `AppData\Local\Tableau\Tableau\Caches`, `%TMP%`, `%TEMP%`. If ANY of these appear anywhere in the path, treat it as non-durable and ask the user where to save the snapshot. Anything else (a normal project folder, Documents, Desktop, a mapped drive) is treated as durable without asking.
6. **Blocking modal awareness.** Same rule as every other skill in this environment: if a tool call hangs, times out, or returns a garbled result right after a document call, stop issuing further calls and tell the user to check Desktop for a blocked dialog. Dont retry blind.
7. **One-to-one comparison only.** This skill compares current state against a single baseline snapshot. Multi-snapshot history (e.g., what changed between snapshot A and snapshot B or show me all changes across 5 snapshots) is out of scope. Each run diffs current vs. one prior baseline, then optionally overwrites that baseline. If the user asks for multi-point history, state this limitation plainly.
8. **Parameters, Sets, and Hierarchies may be invisible.** `list-available-fields` does not reliably surface parameters (unless referenced in a calc formula), sets, or hierarchies. If these are absent from both the snapshot and the current inventory, they are invisible to this skill, not unchanged. If the user asks specifically about parameter/set/hierarchy changes, state this limitation plainly rather than reporting no changes with false confidence.
9. **`hidden` and `connection_type` are best-effort, unconfirmed fields.** Unlike `name`, `dataType`, `role`, and `formula` — which are confirmed present in `list-available-fields` output across this environments other skills — the `hidden` flag and a datasources `connection_type` (hyper/live) have not been empirically verified as returned by any tool in this session. If a tool call returns without one of these fields, record it as `null`/`unknown` in the snapshot rather than guessing, and never report a change on a field whose only difference is a null-vs-value flip on one of these two properties (thats a missing-data artifact, not a real change).

***

## Two Modes

### Mode A — Calc/Field Auditor (narrow scope)

Trigger words: did this calc change, field change history, audit this calc, or when the user names a specific field/calc/datasource rather than the whole workbook.

**Workflow:**

1. Call `list-workbook-datasources` to determine how many datasources the workbook contains. If exactly one, auto-select it. If two or more, ask the user which datasource to audit.
2. Call `list-available-fields` (verbosity: full) for that datasource.
3. Look for an existing snapshot file (`[datasource-name]_snapshot.json`) next to the workbook.
   - **No snapshot found:** tell the user plainly this is the first run — nothing to diff against. Write the current field/calc state as the baseline snapshot and stop there.
   - **Snapshot found:** load it and diff field-by-field:
     - **New fields:** present in current inventory, absent from snapshot.
     - **Removed fields:** present in snapshot, absent from current inventory.
     - **Formula changes:** same field name, `formula` text differs (see Hard Constraint #3 — report as textual change only).
     - **Type/role changes:** same field name, `dataType` or `role` differs (e.g. a field flipped from dimension to measure).
     - **Inferred renames:** per Hard Constraint #4.
4. If the user named one specific field/calc, filter the digest to just that fields history; otherwise report all changes for the datasource.
5. **Zero-change early exit:** if the diff produces zero changes across all categories (new + removed + formula changes + type/role changes + inferred renames = 0), report No field or calc changes detected since the last snapshot immediately and skip to step 8. Do not render an empty grouped list or run the count-match gate on nothing.
6. Present the digest as a bulleted list (never a table — this chat surface renders tables poorly), grouped by change type, following the exact format in `skill-expertise/report_template.md`.
7. **Before presenting the digest**, confirm the number of changes you found (new + removed + formula changes + type/role changes + inferred renames) matches the number of bullet items youre about to render. If they dont match, re-check your grouping logic before showing the user anything.
8. Ask: Save this as the new baseline snapshot? Only overwrite the snapshot file on explicit confirmation — a diff run should not silently reset the comparison point. If the user declines, end without writing anything.

### Mode B — Workbook Change Digest (broad scope)

Trigger words: what changed in this workbook, compare to last version, whats different since I last opened this — or any ask spanning sheets/dashboards, not just fields/calcs.

**Workflow:**

1. Call `list-workbook-datasources` first to get the actual list of datasources — this is a prerequisite for the field calls below, not optional. In parallel with that, call `get-workbook-inventory`, `list-worksheets`, and `list-dashboards` (independent of each other and of the datasource list). Once the datasource list is back, call `list-available-fields` (verbosity: full) once per datasource returned.
2. Look for an existing whole-workbook snapshot (`[workbook-name]_workbook_snapshot.json`).
   - **No snapshot found:** same as Mode A — establish the baseline, tell the user, stop here (skip the remaining steps below).
   - **Snapshot found:** compare four top-level counts against the snapshot: datasource count, worksheet count, dashboard count, and per-datasource field count. Also compare each dashboards `member_sheets` array against the snapshots (order-sensitive) — a membership change (sheet added/removed/reordered on a dashboard) does not move the dashboard *count*, so the count check alone cannot rule this out. (Note: this comparison saves diff/render effort only, not tool calls — `list-available-fields` and `get-workbook-inventory` were already called in step 1 to obtain these counts and membership lists.)
     - **All four counts match, membership lists match, AND the user did not specifically ask about a rename:** report No changes detected since the last snapshot and stop here (skip to step 7 — there is no digest to save a new baseline over, so step 7s ask still applies in case the user wants to refresh the timestamp).
     - **All four counts match, but the user specifically asked about a rename:** counts alone cant rule out a rename (a rename changes no count). Proceed to step 3, but run ONLY the rename-detection logic within the one dimension the user asked about (Fields/calcs, or Worksheets if they asked about a sheet rename) — skip the New/Removed/Formula/Type-role checks and skip the other three dimensions entirely.
     - **Any count differs, or any dashboards membership list differs:** proceed to step 3 and run the full four-dimension diff.
3. **Full diff** (only reached per the branches in step 2 above — either the full version, or the rename-only version scoped to one dimension per the branch above), across four dimensions:
   - **Fields/calcs** — same logic as Mode A, per datasource. If one datasources `list-available-fields` call fails partway through this loop, note that datasource as not checked (tool error) in the digest and continue diffing the remaining datasources — dont abort the whole run over one failure.
   - **Worksheets** — new, removed, or renamed (inferred only per Hard Constraint #4, applied to sheet names + shelf contents as the definition to match on).
   - **Dashboards** — new, removed, or a changed worksheet membership list (a dashboard that gained/lost a sheet).
   - **Datasources** — new datasource connections added, or one that disappeared (flag disappearance clearly — this is high-signal and often unintentional).
4. **Scalability branches (by field count per datasource):**
   - **< 5 fields (tiny):** the snapshot is still worth taking (structural changes like sheet/dashboard adds are the real value here), but note to the user that field-level diffing adds minimal value at this scale.
   - **5-49 fields (typical):** no special handling — render the flat bulleted list per change type as normal.
   - **50-99 fields (wide):** sub-group that datasources findings by change type (New / Removed / Formula changes / Type-role changes) per the report template, so the list stays scannable.
   - **100+ fields (very wide):** same sub-grouping as wide, plus lead with a one-line count-by-type summary for that datasource (e.g., Orders: 12 new, 3 removed, 4 formula changes) before the detail bullets, since even sub-grouped detail can run long at this size.
   - **5+ datasources:** present a workbook-level summary line first (3 datasources changed, 2 unchanged) before expanding per-datasource detail. Only expand datasources that have changes.
   - **200+ total field changes across all datasources:** warn the user the digest is long and offer to filter by change type or by datasource before rendering the full list.
5. Present the digest in plain English, grouped by dimension (Fields & Calcs / Worksheets / Dashboards / Datasources), bulleted, most-significant-first (datasource changes > dashboard changes > worksheet changes > field/calc changes — a lost datasource matters more than a renamed field), following the exact format in `skill-expertise/report_template.md` and the field-count bands in step 4 above.
6. **Before presenting the digest**, confirm the number of changes found matches the number of bullets rendered, same check as Mode A.
7. Ask: Save this as the new baseline snapshot? Same non-silent-overwrite rule as Mode A. If the user declines, end without writing anything.

***

## Error Handling

| Failure | Recovery |
|---|---|
| `get-workbook-inventory` fails or returns no workbook | No workbook is open. Tell the user: No workbook detected — open one and try again. |
| `list-available-fields` returns empty | Datasource disconnected or in error state — report and stop for that datasource; continue with others in Mode B. |
| Snapshot file exists but fails to parse (corrupted JSON) | Tell the user plainly: The saved snapshot for this [datasource/workbook] couldnt be read — treating this run as a fresh baseline. Dont attempt partial recovery of a malformed file. |
| Snapshot path unwritable | Ask the user where to save it instead — same as `data-scribe`s output-path fallback. |
| Calc formula unreadable via `list-available-fields` and `get-worksheet-xml` fallback | Record Formula not extractable this run — cannot confirm whether it changed. Dont guess. |
| `get-worksheet-xml` 500s on a dashboard-bound sheet | Known reliability gap — skip that sheets structural diff, note it in the digest as not checked (tool reliability gap on dashboard-bound sheets). |
| User asks to diff against a specific named prior snapshot file, not the default path | Honor the explicit path if they give one; otherwise use the default convention. |
| Write tool fails when saving snapshot | Tell the user: Couldnt write the snapshot file. Heres the snapshot content — you can save it manually. Then paste the JSON to the chat so nothing is lost. |
| Fields return with access-restricted/permission error (RLS) | Record those fields as access-restricted, not diffed in the digest. Continue with all other fields. Dont treat RLS as a full datasource failure. |
| Tool call times out or returns no response | Retry once. If it fails again, report Tool timeout on [tool name] — partial results only and continue with whatever data you already have. Never retry more than once. |

***

## Composability

- **Upstream:** offer proactively the first time a user opens the skills target workbook in a session, if no baseline snapshot exists yet — No change history tracked for this workbook yet. Want me to establish a baseline so future runs can show you what changed? Dont auto-run without confirmation.
- **Downstream:** a formula-change finding on a calc that also appears broken is a handoff to a calc-authoring skill, not a fix this skill attempts itself. A lost/renamed field finding that affects an existing metric dictionary is a signal to re-run `data-scribe`s update mode.
- **Adjacent:** `data-scribe` documents what fields mean once; this skill tracks whether theyve changed since a prior point. `publish-readiness` checks a different axis (hygiene at a moment in time, not change over time) — the two can be offered together right before a publish action.
- **Context enrichment from data-scribe:** before rendering the digest, check whether a data-scribe metric dictionary file exists next to the workbook (filename pattern: `[datasource-name]_dictionary.md` or `[datasource-name]_dictionary.txt`). If found, look up each changed field by name in that file. If a description exists, append it to the bullet: `— documented as: [description from dictionary]`. This makes the digest more actionable (the user sees what the changed field means, not just its name). If no dictionary file exists, skip this enrichment silently (no error, no mention).
- No workbook mutations occur — every run writes only a snapshot file, never touches a calc, field, sheet, or dashboard.

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
