# Export Reference

Hyper export code and type mapping used in Phase 6.

## Hyper Export Implementation Code and Type Mapping

```python
import pantab
import pandas as pd

# Convert generated data to DataFrame(s)
# pantab handles type mapping automatically
pantab.frame_to_hyper(df, "output.hyper", table="Extract")
# Verify against the installed pantab version: the function names and the table
# name/schema that Tableau treats as an extract (often Extract.Extract) have
# changed between releases. Read the file back and confirm it opens before delivering.

# For multi-table:
pantab.frames_to_hyper(
    {"Extract": df_orders, "Returns": df_returns},
    "output.hyper"
)
```

**Type mapping for .hyper:**
| Python/Generated Type | Hyper Type |
|---|---|
| string | TEXT |
| int | INTEGER / BIG_INT |
| float | DOUBLE |
| date | DATE |
| datetime | TIMESTAMP |
| bool | BOOLEAN |

Publishing: this MCP has no datasource publish tool. Tell the user to publish the .hyper from Tableau Desktop or the web (Publish Data Source / upload).
