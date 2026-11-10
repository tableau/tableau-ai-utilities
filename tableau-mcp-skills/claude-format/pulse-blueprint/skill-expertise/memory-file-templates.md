# Memory File Templates

Exact formats for the audit cache and delivered blueprints memory files.

**`pulse-blueprint-audit-cache.md`** -- stores last audit results:
```markdown
---
name: pulse-blueprint-audit-cache
description: Last Pulse audit scores and findings for delta comparison
type: project
---
## Last Audit: [date]
| Definition ID | Name | Score | Top Issues |
...
```

**`pulse-blueprint-delivered.md`** -- stores delivered blueprints:
```markdown
---
name: pulse-blueprint-delivered
description: Pulse metric blueprints previously delivered (avoid duplication)
type: project
---
## Delivered Blueprints
| Date | Metric Name | Datasource | Measure |
...
```
