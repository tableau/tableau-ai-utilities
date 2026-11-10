# Filter Shelf, Context Filter & Set Verification: Known Gaps

Confirmed gap (2026-08-04): there is no tool-only path to place a field on the Filters shelf, promote an existing filter to context, or reliably read back either state afterward. A related, separately confirmed gap: sets are not visible to any field-inspection tool at all, regardless of how they were created or how their membership is configured.

***

## No Filters-shelf target on `add-field`

`add-field`'s `target` parameter only accepts `rows`, `cols`, or `encoding` (color/size/lod/detail/text/tooltip/path/angle). There is no `filters` target. This means a field cannot be placed on the Filters shelf via `add-field` at all — not just context promotion, the basic filter-shelf placement itself has no tool path.

## No context-promotion command

No MCP tool adds a filter to context or promotes an existing filter.

## No reliable read-back of filter/context state

- `get-worksheet-xml` has been observed failing with a 500/`operation-failed` error on at least one real, populated, dashboard-referenced worksheet ("Product Detail Sheet") — consistent with the known reliability gap for dashboard-bound sheets.
- `get-summary-data` cannot substitute: it only returns fields already placed on the view (Rows/Columns/Marks), not what's on the Filters shelf, and it has no concept of "is this filter in context."

## What this means for this skill

**Do not attempt to add a filter or promote it to context via any tool.** There is no `add-field`/`apply-worksheet` chain that reaches the Filters shelf, and no tool that reaches context promotion. Give the user the manual Desktop steps instead:

1. "Drag [field] onto the Filters shelf for [worksheet]."
2. "Right-click the filter card (on the shelf or in the worksheet view) → **Add to Context**."

**Do not claim the filter or context promotion was applied** — there is no way to verify it from here. If the user reports they made the change, take their word for it; don't attempt a verification read that this environment can't actually perform.

**If asked why a FIXED LOD isn't responding to a dimension filter the way expected:** this is the likely reason the filter isn't in context yet — walk the user through the two manual steps above rather than trying to fix it via calc-level tricks.

***

## Sets are not resolvable or inspectable via any available tool

**Confirmed 2026-08-04.** `author-set` (mode `empty`) reports success and returns a `setName`, but the resulting set:
- Does **not** appear in `list-available-fields`' output (checked full verbosity — dimensions and measures both, across all datasources in the workbook).
- Is **not** resolvable via `resolve-field` — it returns `not_found` with a message asserting the field "genuinely does not exist," even immediately after a fresh live refresh.
- **Cannot be placed on a shelf** via `build-and-apply-worksheet` — the field gets silently dropped with "All requested fields were dropped."

**This holds true regardless of set membership state.** Confirmed by testing at two different points: immediately after creation (empty, `mode: "empty"`, no members assigned) and again after the user manually populated it in Desktop via Create Set → Condition → Custom Value List, adding "California" as an explicit IN member. The set was equally unresolvable both times — this is not a timing/staleness issue or a membership-state issue, it's a category-level exclusion: **sets as a field type are not surfaced by `list-available-fields`, `resolve-field`, or shelf-placement tools in this environment**, independent of how they were created (via `author-set` or natively in Desktop) or how they're configured (empty, fixed member list, condition-based, wildcard).

**What this means:**
- **Cannot verify a set was created correctly, has the expected membership, or is usable on a shelf** — not through any read tool available here.
- **Cannot place a set on Color/Filter/Detail via `add-field`** either, for the same resolution reason — the set has no `column_ref` that any tool can produce.
- **Never claim a set exists, has specific membership, or is usable** based on `author-set`'s success response alone — that response only confirms the internal call didn't error, not that the object is inspectable or correct.

### Default behavior: give instructions, don't call `author-set`, for any set that needs to actually work

Since `author-set`'s output is unusable and unverifiable regardless of outcome, calling it adds no real value when the user needs a working set — it just produces an object that looks created but can't be placed on a shelf or confirmed by either of us. **Default to giving the user manual build instructions instead of calling `author-set`:**

1. "Right-click **[dimension]** in the Data pane → **Create → Set...**"
2. For a simple explicit list: "In the **General** tab, check the member(s) you want IN the set (e.g. California), then name it and click OK."
3. For a pattern match instead of listing members: "Switch to the **Condition** tab → By formula → enter a wildcard/condition (e.g. `[State/Province] = "California"`), then click OK."
4. "Drag the new set from the Data pane onto Color, Filter, or Detail to use it — it'll show as two values, **In** and **Out**."

State plainly, before giving these steps, that you can't build or verify the set yourself in this environment — this isn't a "try the manual route as backup," it's the actual recommended path since the tool path produces nothing usable.

**Only call `author-set` when the user explicitly wants a placeholder/staged object despite knowing it won't be usable via tools** (e.g. they're fine configuring it further themselves in Desktop and just want the object to exist as a starting point) — and say so explicitly when you do: "I've created a set object, but I can't verify it or use it on a shelf from here — you'll need to configure and confirm it in Desktop."

**Prefer a calculated field over a Set whenever the split is a simple IN/OUT that doesn't need native Set semantics** (`IF [field] = "X" THEN "X" ELSE "Other" END`) — it behaves identically for filtering/coloring and is fully verifiable via `list-available-fields`, `resolve-field`, and every shelf-placement tool, unlike a Set. Reserve an actual Set recommendation for when the user specifically needs set actions, "Show/Hide members in Set," or set-combination operations that a calc can't replicate.

### `author-set` mode `top-n` with `orderBy` is not just unverifiable — it can produce a genuinely broken set

**User-confirmed, 2026-08-07** (`skills/Bug report/bug-report-agent-set-creation.md`): calling `author-set` with `mode: "top-n"` and an `orderBy` measure (e.g. Top 10 customers by Sales) created a set that showed a red `!` invalid-field indicator **in the Desktop Data pane itself** — this is a step worse than the general tool-invisibility above, because it fails natively in Tableau's own UI, not just in agent-side tooling. The set could not be dragged to any shelf (failed or produced no marks). Opening **Edit Set → Top tab** showed the correct-looking field (`Sales` / `Sum`) in the dropdown, but the underlying reference didn't resolve. Deleting the set and re-calling `author-set` with identical arguments reproduced the same broken state — this is consistent, not a one-off flake.

**Do not use `author-set` mode `top-n` at all when the set needs to actually work.** Instead:
- **Preferred:** author a `RANK(SUM([measure]), 'desc')` table calc, place it on the Filters shelf, filter to `<= N`, and set "Compute Using" to the target dimension. This reliably replaces a Top-N set and is fully agent-buildable.
- **If the user specifically needs Set semantics** (set actions, Show/Hide members): give manual instructions — Data pane → right-click dimension → **Create → Set... → Top tab → By field** — and warn explicitly that this exact configuration is known to produce a broken set even when built manually by some accounts, so verify in Desktop that the Data pane shows no red `!` before relying on it.
- Condition-based and General-tab (fixed member list) sets are not implicated by this bug report — the tool-invisibility limitation above still applies to them, but they have not been reported as natively broken in Desktop.
