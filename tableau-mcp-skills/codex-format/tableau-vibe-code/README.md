# Tableau Vibe Code

Tableau Vibe Code helps Codex build or safely restyle Tableau `.twb` and `.twbx` workbooks. It uses schema-aware XML changes, safe package extraction, deterministic repackaging, and explicit validation boundaries.

## When to use it

- Apply a deliberate visual restyle to an existing workbook.
- Add supported worksheets, dashboard zones, or KPI patterns from compatible evidence.
- Implement issues from a supplied dashboard critique.
- Produce a validated `.twb` or `.twbx` deliverable.
- Apply the same bounded change across a user-authorized workbook batch.

Use a calculation-specific skill for isolated calculated fields and a critique skill when no workbook output is requested.

## Requirements

- Codex with this skill installed or available.
- Python 3.10+ and `lxml` for local workbook helpers.
- A compatible Tableau runtime for opening, rendering, or optional publication-based checks.

Local XML validation does not by itself prove Tableau rendering compatibility.

## Installation

Install the entire `tableau-vibe-code` directory through your normal Codex skill or plugin workflow. Keep `SKILL.md`, `agents/`, and `skill-expertise/` together.

## Example prompts

```text
Use $tableau-vibe-code to convert this packaged workbook to the supplied dark palette while preserving every datasource and embedded asset.
```

```text
Apply these dashboard critique findings to my workbook and return a validated .twbx plus a concise changelog.
```

```text
Add a KPI row using the attached compatible workbook as the structural donor. Do not publish anything.
```

## Local helpers

Safely extract a packaged workbook into a new run directory:

```bash
python skill-expertise/workbook_tools.py extract input.twbx scratch/run-001
```

Validate a working `.twb`:

```bash
python skill-expertise/workbook_tools.py validate scratch/run-001/working.vibe.twb --json validation.json
```

Package the complete extracted tree after replacing its original workbook member:

```bash
python skill-expertise/workbook_tools.py package \
  scratch/run-001/extracted \
  scratch/run-001/working.vibe.twb \
  Workbook/book.twb \
  outputs/result.twbx
```

The helpers reject unsafe archives, do not force-delete conflicting output, and preserve unrelated package members.

## Safety model

- Source workbooks are never overwritten.
- Unknown XML structures require a compatible donor or verified schema evidence.
- Publication follows an explicit user request and available runtime capabilities; existing authorization is honored. Temporary render-check publication requires a cleanup route or an explicitly accepted retained artifact. Permanent publications are not cleaned up.
- Validation claims distinguish local XML checks from actual Tableau opening or rendering.

## Development

Run helper tests and the active Codex skill validator before release:

```bash
python -m unittest discover -s skill-expertise -v
```

## License

No license has been assigned by this package. Add one before public redistribution.
