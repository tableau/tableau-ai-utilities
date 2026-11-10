# Project Discovery Reference

Detailed strategy table and search options (keyword, browse, sub-project, owner) for helping a user find the right Tableau project.

#### Step 1: Determine Discovery Strategy
 
| User signal | Strategy |
|---|---|
| User names a topic ("the finance project") | Search projects by keyword using `search-content` with `contentTypes: ['project']` |
| User asks to browse/list projects | Use `list-projects` to show available projects |
| User names a partial/fuzzy project name | Use `list-projects` with wildcard filter (`name:eq:[partial]*`) |
| User names an owner ("Sarah's project") | Use `list-projects` filtered by `ownerName:eq:[name]` |

#### Step 2: Search Projects
 
**Option A: Keyword-based discovery** (most common)
 
Use `search-content` with:
- `terms`: The user's topic or keyword
- `filter.contentTypes`: `['project']`
- `limit`: 11 (show 10; if 11 come back, say more than 10 matched)
 
This returns projects whose names or descriptions match the topic. It also returns `containerName` (parent project) which helps identify hierarchy.
 
**Option B: Browse all projects**
 
Use `list-projects` with:
- `limit`: 50 (or higher if needed)
- Optional filter: `name:eq:[pattern]*` for wildcard matching
- Optional filter: `topLevelProject:eq:true` to show only top-level projects (useful for initial orientation)
 
This returns full project metadata including descriptions, parent hierarchy, owner, and timestamps.
 
**Option C: Hierarchical / Sub-Project exploration**
 
Many Tableau sites organize content in nested project trees (e.g., "Finance Data Office" → "Total Bookings", "AI for Finance", "Renewals Forecast"). When the user:
- Says "what's inside [project]?" or "show me sub-projects of [X]"
- Picks a parent project and wants to go deeper
- Asks "drill into [project]" or "what sub-folders are there?"
 
Use `list-projects` with `parentProjectId:eq:[parent project id]` to list child projects.
 
**Hierarchical discovery flow:**
1. Find the parent project (by search or name match) to get its `id`
2. Call `list-projects` with `parentProjectId:eq:[id]`
3. Present sub-projects with their descriptions
4. Let the user pick a sub-project, or offer to search across all children
 
**Example:** User says "what's in the Finance Data Office project?"
1. Search: find "Finance Data Office" → id = `[parent project id]`
2. List children: `parentProjectId:eq:[parent project id]` → returns "Finance Wide", "AI for Finance", "Total Bookings", "ATR", "Renewals Forecast"
3. Present: "Finance Data Office has 5 sub-projects: [table]. Which one should I search, or want me to search across all of them?"
 
**Option D: Owner-based discovery**
 
If the user says "show me [person]'s projects" or "what does [team] own":
 
Use `list-projects` with `ownerName:eq:[name]` filter.
 
Useful for finding team-specific content when the user knows the owner but not the project name.
