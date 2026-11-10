# Completeness Catalog (Locked, 8 Rules)

Every finding cites one of these rule IDs. No fabricated rules; no severity reassignment; no rule outside this catalog.

## Severity Baselines

| Rule ID | Rule Name | Baseline Severity |
|---|---|---|
| DC-TITLE-01 | Dashboard-Title-Missing | Warning |
| DC-CAPTION-02 | Dashboard-Caption-Missing | Info |
| DC-WS-TITLE-03 | Worksheet-Title-Missing | Warning |
| DC-WS-CAPTION-04 | Worksheet-Caption-Missing | Info |
| DC-TEXT-EMPTY-05 | Text-Object-Empty | Warning |
| DC-DEFAULT-NAME-06 | Default-Name | Warning |
| DC-DEVICE-07 | Device-Layout-Inheritance-Duplicate | Warning |
| DC-TITLE-08 | Placeholder-Title-Text | Warning |

## DC-TITLE-01 Dashboard-Title-Missing

**Check.** Every dashboard has a visible, non-empty title.

**Signals evaluated.**

- Read `<dashboard>` element from `get-dashboard-xml`.
- Look for `<title>` child with non-empty text.
- Detect `<title style='hidden'>` or `<title show='false'>` attribute states.

**Fires when.** Dashboard has no `<title>` child, OR title is present but hidden (`style='hidden'`, `show='false'`), OR title text is empty string after whitespace trim.

**Severity.** Warning. Missing dashboard title is a visible defect that reaches the end user.

**Desktop fix.** Right-click the dashboard zone/canvas > toggle **Title** (checkmark = shown). Then click the title bar and edit the text to a descriptive name.

## DC-CAPTION-02 Dashboard-Caption-Missing

**Check.** Every dashboard has a caption (subtitle) text if the dashboard's design intent implies one.

**Signals evaluated.**

- Read `<dashboard>` element for `<caption>` child or dedicated caption text object.
- Empty caption text or missing element fires this rule.

**Fires when.** Dashboard has no caption text present.

**Severity.** Info. Captions are optional in most published workbooks; absence is a design choice more often than a defect.

**Desktop fix.** Add a text object below the title bar with a one-line context statement (e.g., "Q3 results, updated weekly").

## DC-WS-TITLE-03 Worksheet-Title-Missing

**Check.** Every worksheet placed on a dashboard has a visible, non-empty title.

**Signals evaluated.**

- Read `<worksheet>` element from `get-worksheet-xml` for each worksheet on a dashboard.
- Look for `<title>` child with non-empty text.
- Detect hidden-title states (`style='hidden'`, `show='false'`).

**Fires when.** Worksheet on the dashboard has no `<title>` child, OR title is hidden, OR title text is empty after whitespace trim.

**Severity.** Warning. Missing worksheet title on a dashboard is a visible defect.

**Desktop fix.** On the dashboard, right-click the worksheet's zone > toggle **Title** (checkmark = shown). Then edit the title bar text. (Confirmed live 2026-09-14: dashboard zone context menu exposes Title/Caption as single checkbox toggles, not a nested "Show Title" sub-item.)

## DC-WS-CAPTION-04 Worksheet-Caption-Missing

**Check.** Every worksheet on a dashboard has a caption if the design intent implies one.

**Signals evaluated.**

- Read `<worksheet>` element for `<caption>` child.
- Empty caption text or missing element fires this rule.

**Fires when.** Worksheet has no caption text.

**Severity.** Info. Captions are optional at the worksheet level.

**Desktop fix.** On the dashboard, right-click the worksheet's zone > toggle **Caption** (checkmark = shown). Edit the caption text.

## DC-TEXT-EMPTY-05 Text-Object-Empty

**Check.** Every dashboard text object (canvas text zone) has non-empty content.

**Signals evaluated.**

- Read `<zone type='text'>` or `<text-object>` elements from `get-dashboard-xml`.
- Look for `<formatted-text>` child with non-empty content.

**Fires when.** Text object zone exists but has no `<formatted-text>` content, OR content is empty string after whitespace trim.

**Severity.** Warning. Empty text zones render as blank rectangles on the dashboard.

**Desktop fix.** Double-click the empty text object and add content, OR delete the empty text object.

## DC-DEFAULT-NAME-06 Default-Name

**Check.** Dashboard or worksheet names do not match auto-generated patterns.

**Signals evaluated.**

- Read `name` attribute on `<dashboard>` and `<worksheet>` elements.
- Match against locale default-name regex patterns.

**Locale regex patterns.**

- English: `^Dashboard \d+$`, `^Sheet \d+$`.
- French: `^Tableau de bord \d+$`, `^Feuille \d+$`.
- Spanish: `^Panel \d+$`, `^Hoja \d+$`.
- German: `^Dashboard \d+$`, `^Blatt \d+$`.
- Case-sensitive to match Tableau's auto-generated names exactly.

**Fires when.** Name matches any locale default-name regex.

**Severity.** Warning. Default name signals the author never set an intentional title; audience reads `Dashboard 1` as unfinished work.

**Desktop fix.** Right-click the dashboard tab or worksheet tab > Rename Dashboard / Rename Sheet. Enter a descriptive name.

## DC-DEVICE-07 Device-Layout-Inheritance-Duplicate

**Check.** When a Desktop dashboard has phone or tablet device-layout variants, those variants must not silently propagate a missing title or missing caption from the Desktop parent to the phone/tablet audience.

**Signals evaluated.**

- Read `<dashboard>` element from `get-dashboard-xml` for a `<devicelayouts>` child element (confirmed live 2026-09-12 against Superstore's "Overview" dashboard; no `<device-layouts>` hyphenated form exists).
- For each device variant (`<devicelayout name='Phone'>`, `<devicelayout name='Tablet'>` — name, not type, is the discriminating attribute), a variant is **not independently customized** in either of two confirmed shapes, and both must be treated as "carries the parent's state, not an independent override":
  - **Shape A — auto-generated with duplicated content.** `auto-generated='true'` on the `<devicelayout>` element, with a full `<layout-options><title>` that mechanically copies the parent's exact title text and a full `<zones>` tree. Confirmed live on the "Phone" variant after Tableau auto-generated it.
  - **Shape B — bare untouched stub.** No `auto-generated` attribute at all, and no `<layout-options>`/`<title>`/`<zones>` children — only a `<size sizing-mode='automatic' />` (or similar) self-closing element. Confirmed live on the "Tablet" variant before it had ever been opened/generated. This is the *more* untouched state, not a customized one — do not treat the absence of `auto-generated='true'` as evidence of customization.
  - A variant counts as **independently customized** (and does not count toward this rule) only when it has its own `<layout-options><title>` whose text differs from the parent's, or an explicitly authored caption/text distinct from the parent.
- If parent dashboard already fires DC-TITLE-01 or DC-CAPTION-02, AND at least one device variant matches Shape A or Shape B (not independently customized), fire DC-DEVICE-07 as a compound finding.

**Fires when.** Desktop parent dashboard has a missing title or caption AND at least one phone/tablet `<devicelayout>` matches Shape A (auto-generated duplicate) or Shape B (bare stub with no title/zones) above. The parent finding already fires DC-TITLE-01 or DC-CAPTION-02; DC-DEVICE-07 adds the device-propagation observation.

**Severity.** Warning. Device variants ship to phone/tablet users with the same missing labels; the audience impact is the same as Desktop.

**Reporting discipline.** Report once on the Desktop parent dashboard. List the affected device variants in the same finding record as `affected_variants: [phone, tablet]`. Do not fire separate findings per variant. One Desktop-fix path (add the title/caption on the parent) resolves all non-customized variants, whether Shape A or Shape B.

**Desktop fix.** Right-click the Desktop dashboard zone/canvas > toggle **Title** (checkmark = shown), or add caption text. Non-customized device variants (both auto-generated duplicates and bare stubs) pick up the parent's title/caption text automatically once it exists — Shape B variants generate their own auto-layout the first time they're opened in Device Designer, and Shape A variants already mirror the parent directly. If a device variant needs a different label (e.g., shorter for phone viewports), open the Device Designer for that layout and edit its title/caption directly — this converts it to the independently-customized state and takes it out of scope for this rule.

## DC-TITLE-08 Placeholder-Title-Text

**Check.** Dashboard or worksheet title text is not Tableau's unedited literal boilerplate placeholder.

**Signals evaluated.**

- Read `<title><formatted-text>` runs from `get-dashboard-xml` (dashboard-level) or `get-worksheet-xml` (worksheet-level).
- Match the concatenated run text against known Tableau placeholder patterns: `<Sheet Name>`, `<Dashboard Name>`, and locale-equivalent bracketed boilerplate. Confirmed live 2026-09-14 against Superstore's "Order Details" dashboard: `<run>&lt;</run><run>Sheet Name</run><run>&gt;</run>` renders as literal `<Sheet Name>`.

**Fires when.** Title text, after concatenating all `<run>` children, exactly matches a known placeholder pattern. Does not fire on DC-TITLE-01/DC-WS-TITLE-03 (those require empty or hidden titles — this rule catches present-but-never-edited text, a distinct failure mode).

**Severity.** Warning. A never-edited placeholder title reaches the end user exactly like a missing one.

**Desktop fix.** Click the title bar (dashboard) or open the worksheet and click its title bar, then replace the placeholder text with a descriptive title.

## Detection Discipline

- **Trust XML evidence first.** Every rule fires on specific XML markers, not on impression.
- **Confidence flag on ambiguous signals.** If `get-dashboard-xml` returns partial results, flag UNSCANNED for that dashboard per HC#9.
- **Do not fabricate findings.** Every fire cites the specific XML element and attribute that triggered it.
- **Do not skip default-name detection.** HC#11 locks default names as Warning.

## Refuse to Fabricate

Every finding cites XML evidence. Never invent a finding to inflate rigor. Never suppress a genuine finding to please the user. If evidence is ambiguous, flag confidence and use UNSCANNED rather than a fake pass.
