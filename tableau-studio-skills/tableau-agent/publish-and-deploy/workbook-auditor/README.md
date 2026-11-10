# Workbook Auditor

Snapshots a Tableau workbook's fields, calcs, sheets, and dashboards, then diffs the current state against a saved baseline to produce a plain-English "what changed" digest. Two modes on one snapshot mechanism: narrow calc/field change tracking for governance, and whole-workbook change digest for collaborator handoffs. Read-path plus one file write per run (the snapshot). Never mutates a calc, field, sheet, or dashboard.

**Example:** "What changed in this workbook since I last opened it?" produces a digest: 2 new calcs (with formulas), 1 removed field, 1 inferred rename (`Cust ID → Customer Key`, same formula and type after whitespace normalization), 3 formula edits (flagged as textual changes, not semantic — reformatting shows up too), 1 dashboard gained a member sheet. Then asks whether to save the current state as the new baseline.

***

## What it does

Turns "did anyone change this workbook" into a specific answer. Snapshot files are JSON, saved next to the workbook (same convention as data-scribe). Each run compares current state against exactly one baseline snapshot; the diff produces a digest grouped by change type.

Formula diffing is textual, not semantic. A calc that's been reformatted (whitespace, reordered branches) shows as "changed" — Workbook Auditor reports it plainly rather than editorializing about whether behavior actually changed.

Renames are inferred carefully. A rename looks identical to "field removed" + "field added" to the tools. Workbook Auditor infers a rename only when a removed field and an added field share the same `dataType`, `role`, and (for calcs) formula text that's identical after whitespace normalization (comments stripped, all whitespace runs collapsed to single spaces, comparison is case-sensitive). Otherwise, they're reported separately.

Compares against exactly one baseline. Multi-snapshot history ("show me changes across 5 snapshots") is out of scope. Each run diffs current vs. one prior baseline, then optionally overwrites that baseline with your explicit confirmation.

## When to use it

- "What changed in this workbook since I last opened it"
- "Did anyone edit this calc"
- "Compare this to last week's version"
- "Show me the change digest before I hand this off"
- "Establish a baseline so I can track changes going forward"
- "Track changes to this datasource across future edits"

## When NOT to use it

- Not for data quality issues in the underlying data (use data-quality-review)
- Not for what a field means, only whether it changed (use data-scribe)
- Not for pre-publish hygiene checks like unused fields, default sheet names (use publish-readiness)
- Not for building or editing charts, dashboards, or calcs (use an authoring skill)
- Not for multi-snapshot history spanning three or more baselines. One-to-one comparison only.
- Not for reading Tableau's own version history or prior save states. There is no tool for this. "What changed" always means "changed since the last snapshot this skill took."

## How to trigger it

- "What changed in this workbook"
- "Did anyone edit this calc"
- "Compare to last version"
- "Change digest"
- "Audit changes"
- "Field/calc change history"
- "Diff this workbook"
- "Snapshot this workbook"
- "What's different since I last opened this"
- "Track changes to this datasource"

## What you'll need

- Tableau Studio with the workbook open and the datasource connected
- The MCP tools Workbook Auditor uses: `get-workbook-inventory`, `list-workbook-datasources`, `list-available-fields` (verbosity: full), `list-worksheets`, `list-dashboards`, `get-worksheet-xml` (fallback for missing formulas, capped at 5 calcs per run), `Read`, `Write`
- A saved workbook so the snapshot writes next to it. If the workbook path resolves inside a temp directory (matched against a locked list of temp-path substrings: `\Temp\`, `/Temp/`, `AppData\Local\Temp`, `TableauTemp`, `AppData\Local\Tableau\Tableau\Caches`, `%TMP%`, `%TEMP%`), Workbook Auditor asks where to save instead.
- On the first run against a workbook, no prior snapshot exists. Workbook Auditor tells you plainly, writes the baseline, and stops there. Future runs diff against it.

## Example walkthrough

**Input:** "What changed in this workbook since I last opened it?"

**Output (Mode B, whole-workbook digest):**

```
Workbook: Q3 Sales Health.twbx
Comparing current state to snapshot from 2026-08-28.

Datasources
  No datasource changes.

Dashboards
  Executive Summary gained 1 member sheet:
    + "Segment Health Bar" (worksheet exists in both snapshots;
      dashboard membership is new).

Worksheets
  New: "Segment Health Bar" (created since baseline).

Fields & Calcs
  Sales_Clean datasource (12 changes total):

  New (3):
    + [Segment Health Score] = IF SUM([Sales]) > [Target] THEN
      "On Track" ELSE "At Risk" END
      -- documented as: "Binary status flag for KPI cards"
    + [Target Delta %] = (SUM([Sales]) - [Target]) / [Target]
    + [Rolling 4-Week Avg]  (formula extracted from list-available-
      fields at full verbosity)

  Removed (1):
    - [Legacy Region Code]
      -- documented as: "Deprecated 2024 regional bucket, safe to drop"

  Inferred renames (1):
    ~ [Cust ID] -> [Customer Key]
      Same formula (whitespace-normalized), same dataType (string),
      same role (dimension). Reported as inferred rename per Hard
      Constraint #4.

  Formula edits (4):
    ~ [Adjusted Margin]: formula text changed. Reformatting or logic
      edit -- diff is textual, not semantic. Compare in Desktop's calc
      editor to confirm intent.
    ~ [Q3 Cutoff Date]: formula text changed.
    ~ [Metric Selector Result]: formula text changed.
    ~ [Growth Threshold Check]: formula text changed.

  Type/role changes (3):
    ~ [Order Date]: dataType changed from string to date.
    ~ [Discount Bucket]: role changed from dimension to measure.
    ~ [Segment Tier]: role changed from measure to dimension.

Summary
  0 datasource changes, 1 dashboard change, 1 new worksheet, 12 field/
  calc changes on 1 datasource.

Save this as the new baseline snapshot?
```

The `-- documented as: "..."` lines come from the context enrichment step: Workbook Auditor checks whether a `data-scribe` metric dictionary exists next to the workbook and appends each changed field's documented description if found. Silently skipped if no dictionary exists.

## What you get back

- **Two modes on one snapshot mechanism.** Mode A (narrow) tracks a specific field, calc, or datasource. Mode B (broad) audits the whole workbook across four dimensions: Fields/Calcs, Worksheets, Dashboards, Datasources.
- **Snapshot file** (JSON, per `skill-expertise/snapshot_schema.md`) saved next to the workbook. Default filename `[datasource-name]_snapshot.json` for Mode A, `[workbook-name]_workbook_snapshot.json` for Mode B.
- **Plain-English digest** grouped by change type, bulleted (never a table — chat rendering of tables is unreliable). Most significant first: datasources → dashboards → worksheets → fields/calcs.
- **Inferred rename detection** with the specific criteria stated inline (same dataType, role, whitespace-normalized formula). Called out explicitly rather than presented as certainty.
- **Textual formula diffs**, not semantic. Reformatting shows as "changed" and Workbook Auditor says so plainly. It does not editorialize about whether behavior actually changed.
- **Field-count scalability bands.** <5 fields: flat list, note that field-level diffing adds minimal value. 5-49: normal flat list. 50-99: sub-grouped by change type. 100+: one-line count-by-type summary before detail. 200+ total field changes across all datasources: warn and offer to filter by change type or datasource before rendering.
- **Multi-datasource summary line** ("3 datasources changed, 2 unchanged") when 5+ datasources exist. Only expands datasources with actual changes.
- **Context enrichment from data-scribe.** If a metric dictionary file exists next to the workbook, each changed field gets its documented description appended to the digest bullet. Silently skipped if no dictionary exists.
- **Non-silent baseline overwrite.** Workbook Auditor asks "Save this as the new baseline snapshot?" after every diff. Declining ends the run without writing anything.

## Limitations

- **One baseline per snapshot.** No multi-point history. Each run diffs current vs. one prior baseline, then optionally overwrites that baseline. If you need change history across three or more baselines, save named copies of snapshot files manually between runs.
- **Formula diffing is textual, not semantic.** A reformatted calc with identical logic shows as "changed." Workbook Auditor never claims a formula edit changed behavior; it reports the diff.
- **Renames are inferred, never confirmed.** A rename looks identical to "removed + added" to the tools. Workbook Auditor states rename inferences plainly and reports separately if the criteria don't match.
- **Parameters, Sets, and Hierarchies may be invisible.** `list-available-fields` doesn't reliably surface parameters (unless referenced in a calc formula), sets, or hierarchies. Workbook Auditor states this rather than reporting "no changes" with false confidence when the user asks about them specifically.
- **`hidden` flag and `connection_type` are best-effort.** Not empirically verified as returned by any tool in this session. Recorded as `null`/`"unknown"` if missing, and never reported as a change on a null-vs-value flip alone.
- **Whole-workbook mode compares four top-level counts plus per-dashboard membership lists.** If all counts match and all membership lists match, Workbook Auditor reports "No changes detected" and stops (unless you specifically asked about a rename — counts alone can't rule out a rename, so rename-detection runs even on unchanged counts).
- **`get-worksheet-xml` 500s on dashboard-bound sheets.** Known platform gap. Workbook Auditor caps its use of `get-worksheet-xml` at 5 calcs per run and reports the excess as "formula not extractable this run."
- **No workbook mutations.** Every run writes only a snapshot file. Never touches a calc, field, sheet, or dashboard.

## Troubleshooting

- **"It said this is the first run but I know I ran it before."** Snapshot files live next to the workbook. If the workbook was moved or renamed, or if the snapshot was written into a temp directory, the baseline is elsewhere. Point Workbook Auditor at the snapshot path explicitly if you know where it went.
- **"It flagged a formula change but I didn't touch the logic."** Textual diff. Whitespace, reordered branches, or reformatting all show as "changed." Compare in Desktop's calc editor to confirm intent — Workbook Auditor doesn't claim behavior changed.
- **"It missed a rename."** The rename inference requires same `dataType`, `role`, AND whitespace-normalized formula text match. If any of those differ, Workbook Auditor reports separate removal and addition rather than guessing. Rename a field AND change its type or logic and Workbook Auditor can't distinguish that from a coincidental drop + create.
- **"A dashboard-bound worksheet is missing from the diff."** `get-worksheet-xml` returned an error (documented reliability gap on dashboard-bound sheets). Workbook Auditor notes "not checked (tool reliability gap)" for those sheets rather than assuming they're unchanged.
- **"Snapshot file failed to parse."** Corrupted JSON. Workbook Auditor treats the run as a fresh baseline and tells you plainly rather than attempting partial recovery.
- **"It won't write to my chosen location."** Path unwritable. Workbook Auditor asks for an alternate. If the path resolved inside a temp folder, that's the temp-path guard — Workbook Auditor asks proactively rather than defaulting to a temp write.
- **"I want history across three snapshots."** Out of scope. Save named copies of snapshot files between runs (`snapshot_2026-09-01.json`, `snapshot_2026-09-08.json`) and diff them manually or with a separate tool. Workbook Auditor's mechanism is current-vs-one-baseline only.

## Support

File issues in the same channel you use for other Tableau Studio skill feedback. Include the workbook name, the snapshot date, whether the change you expected appeared in the digest, and what Workbook Auditor reported instead.

