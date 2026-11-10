# Error Recovery Playbook

Error causes and recovery actions for this skill.

## Error Recovery Table

| Error | Cause | Recovery |
|-------|-------|----------|
| 403 on get-datasource-metadata | No permission (do not retry) | Search for same-name datasource in other projects; offer description-based fallback |
| 403 or auth error on query-datasource | No permission to query (do not retry) | Skip profiling for that datasource; offer description-based generation from the schema in the metadata |
| Empty field list from metadata | Datasource type not supported | Explain limitation; offer description-based generation |
| Profiling query returns 0 rows | Empty datasource or query error | Retry once; if still empty, ask user for expected row count and use domain defaults, labeled "unprofiled defaults" in the proposal and validation summary |
| Profiling query timeout | Large datasource | Reduce profiling scope (top 20 instead of 50); skip low-priority fields |
| Calibration fails after 3 attempts | Distribution shape incompatible | Trigger escape hatch: present variance to user with options (accept, simplify distribution, adjust range) |
| Unique constraint impossible | Cardinality space < row count | Trigger the "Constraint Conflict Resolution" section in SKILL.md |
| Geographic validation failure | City/State mismatch in generated data | Use fallback: substitute state capital or largest city for that state; regenerate postal code to match |
| Calculated field division by zero | Base field = 0 in denominator | Set calculated field to NULL for that row; note in validation summary |
| Parameter-dependent profiling seems incomplete | RLS or parameter filtering | Note in schema proposal; ask user if results look reasonable for their access level |
| pantab/hyper API not available | Package not installed | Attempt pip install; if fails, offer CSV with conversion instructions |
| Correlation profiling inconclusive | Insufficient data or no clear pattern | Default to independent generation; note in schema proposal |
| Temporal pattern detection fails | Date range too short or irregular | Default to flat/uniform generation; note limitation |
