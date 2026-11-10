# Tableau Scribe

A Codex skill for producing evidence-grounded Tableau dashboard documentation and datasource dictionaries.

## What it provides

- concise or detailed dashboard help content;
- business-friendly metric and field dictionaries;
- documentation updates against accessible current Tableau state;
- runtime discovery of Tableau MCP capabilities and identifiers;
- explicit separation of observed, inferred, and unknown claims;
- opt-in, bounded sample-data enrichment;
- validated Markdown, DOCX, or XLSX deliverables.

## Example prompts

- `Document this Tableau dashboard for our sales managers.`
- `Create a brief help-page description for this view.`
- `Build a metric dictionary for measures and calculations in this datasource.`
- `Create an XLSX data dictionary for all accessible fields.`
- `Update this existing dashboard guide against the current Tableau view.`
- `Write these approved descriptions back to the specified Tableau fields if the runtime supports it.`

## Package layout

| Path | Purpose |
| --- | --- |
| `SKILL.md` | Core routing, workflows, evidence, and authority boundaries |
| `skill-expertise/tableau-evidence.md` | MCP discovery, target resolution, evidence limits, and failures |
| `skill-expertise/dashboard-documentation.md` | Brief and detailed dashboard structures |
| `skill-expertise/datasource-dictionary.md` | Field/calculation documentation guidance |
| `skill-expertise/evidence-contract.md` | Evidence-ledger schema |
| `skill-expertise/output-formats.md` | Markdown, DOCX, XLSX, and update validation |
| `skill-expertise/validate_evidence.py` | Deterministic evidence-ledger validator |
| `skill-expertise/test_validate_evidence.py` | Success, authorization, integrity, and portability tests |

## Local validation

```bash
python -m unittest discover -s skill-expertise -v
python -m py_compile skill-expertise/validate_evidence.py
```

Validate a ledger from any working directory using absolute paths:

```bash
python /absolute/path/to/tableau-scribe/skill-expertise/validate_evidence.py /absolute/path/to/ledger.json --pretty
```

The skill does not query sample values automatically. Value enrichment requires explicit authorization and remains bounded to the documented purpose.
