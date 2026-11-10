# Audit scoring contract

The helper accepts normalized JSON independent of any particular Tableau MCP response:

```json
{
  "methodology_version": "1.0",
  "definitions": [
    {"id": "def-1", "name": "Revenue", "status": "assessed"},
    {"id": "def-2", "name": "Restricted", "status": "failed"}
  ],
  "findings": [
    {
      "definition_id": "def-1",
      "rule_id": "format.currency_unspecified",
      "evidence_key": "representation.currency_code",
      "severity": "medium",
      "summary": "Currency format has no currency context",
      "observation": false
    }
  ]
}
```

Definition status is `assessed`, `partial`, or `failed`. Required finding keys are `definition_id`, `rule_id`, `evidence_key`, `severity`, and `summary`; `observation` is optional. Severity is `critical`, `high`, `medium`, or `low`.

The helper rejects unknown keys, duplicate definition IDs, findings against failed definitions, invalid types/enums, and methodology versions other than `1.0`. It deduplicates by definition, rule, and evidence key, keeping the highest severity. Observations never affect scores. Partial definitions are scored provisionally but excluded from the overall composite.


## Readiness is separate from the hygiene score

Output includes per-definition `readiness` and `overall_readiness`. Any scored critical finding makes readiness `not_ready`, even if the numeric grade is high. Incomplete/failed coverage produces `not_assessed` unless a known critical finding already makes the result not ready. Fully assessed results with no critical findings return `no_critical_findings`, not a guarantee of readiness. Present this status before scores and prioritize critical repairs.
