---
name: phone-layout-blueprint
description: "Use when the user says 'Make this dashboard mobile-friendly', 'audit my phone layout', 'why does my Tableau Mobile look broken?' Plans a phone layout from a desktop dashboard, or audits an existing one against 15 rules, with manual fix steps. Read-only."
---

# Tableau Phone Layout Blueprint

Design or audit a Tableau Dashboard phone layout. Read-only advisory. Two modes: Blueprint (from a desktop dashboard) and Audit (against an existing phone layout). Rule catalog is first-party (P1-P15). Every finding is a numbered Desktop UI instruction the author applies manually.

## When to use (full trigger detail)

Design or audit a Tableau Dashboard phone layout. Two modes. Blueprint mode produces a phone-layout plan from an existing desktop dashboard (sheet inclusion, container swaps, filter-collapse, tap-target sizing, hidden-on-phone candidates). Audit mode runs a locked P1-P15 rule catalog against an existing phone layout and returns severity-ranked findings with manual Desktop fix steps. Read-only. Every finding is a manual instruction. Trigger on "phone layout blueprint", "mobile blueprint", "audit my phone layout", "why does my Tableau Mobile look broken", "phone-form-factor review", "make this dashboard mobile-friendly", "turn off phone layout auto-generation". Do NOT trigger for. desktop dashboard design (viz-planner), desktop viz critique (viz-critique-pro-studio), pre-publish hygiene (publish-readiness), dashboard assembly hygiene (dashboard-preflight), authoring in Desktop, tablet form factor, Server mobile app config.

## Reference files

Detail lives in `skill-expertise/`. Consult these when the summary in SKILL.md is not enough.

- **`skill-expertise/phone-rule-catalog.md`.** The locked P1-P15 catalog with severities, rationale, and evidence signals for each rule. Update this file when a rule is added, removed, or its severity changes.
- **`skill-expertise/desktop-ui-fix-paths.md`.** Numbered Desktop UI steps for every rule. The audit output cites the rule ID and pulls the fix steps from here.
- **`skill-expertise/preference-flag-steps.md`.** Numbered Desktop steps to disable auto-phone-layout generation on new dashboards, for authors who never wanted a phone layout.

Read the rule catalog first if you are running Audit mode. Read the fix paths first if you are running Blueprint mode. Read the preference-flag steps when the author signals they did not want a phone layout at all.

## When to use

Author has a desktop dashboard and needs a phone layout plan (Blueprint mode). Or the author has a phone layout (built or auto-generated) that ships broken and needs a fix list (Audit mode). Or the author never wanted a phone layout and wants the auto-generator turned off.

## Hard Constraints

- **HC-1 Read-only, but deliver the exact steps.** Never mutate the workbook. If the author asks the skill to apply fixes, do not just decline. Convert the request into Audit mode (or continue the existing Blueprint), then deliver the numbered Desktop steps in the fix sequence order documented in `skill-expertise/desktop-ui-fix-paths.md`. Say plainly: "I can't apply these for you, but here is every step in the order to run them." The author gets an actionable output, not a refusal.
- **HC-2 Locked rule catalog.** All Audit findings cite a rule ID from the locked P1-P15 catalog. Blueprint recommendations reference the same catalog. No ad-hoc "best practices" invented mid-run.
- **HC-3 Phone-only, but transfer what applies.** Do not run the full P-catalog against a tablet layout. **P4 sheet count, P6 filter count, P10 scroll length, P15 container swap** partially apply but with looser thresholds on tablet (author's judgment). Everything else (P2 vertical stack, P3 KPI band, P5 hidden-on-phone flag, P7 show/hide, P9 parameter actions, P12 color encoding, P13-P14 auto-generator behavior) is phone-specific and deferred. Never present the transferred rules as a complete tablet audit.
- **HC-4 Honest "already good" verdict.** If the phone layout passes the audit catalog, say so. Do not manufacture findings.
- **HC-5 Preference-flag as recommendation only.** Never claim to flip the auto-generation preference. Ship numbered steps for the author.
- **HC-6 No pasted URLs to community resources.** State names, let the user search.
- **HC-7 Standalone routing.** Downstream skills (`viz-planner`, `viz-critique-pro-studio`, `publish-readiness`, `dashboard-preflight`) may not be installed, and skill names can vary across portfolios. Frame every handoff as "if you have `<skill>` installed, hand this off. Otherwise, here is the specific manual path." Every route in the verdict carries a self-contained fallback. Never claim a specific named skill is the only option.
- **HC-8 Tap-target minimums cited numerically.** 44x44px minimum on every filter, button, or clickable mark. Do not hand-wave.
- **HC-9 Old-version safety.** Show/hide floating containers with button-triggered visibility require Tableau 2020.4 or later. If the user is on a pre-2020.4 version (or the version cannot be determined and the user says the fix "does not exist" in their Desktop), P7 recommendations degrade automatically: replace the show/hide floating container with a separate filters-only worksheet on the phone layout. Never route the user to a fix path their version cannot execute. When in doubt, ask the version.

## Modes

### Blueprint mode

Trigger: author has a desktop dashboard and asks for a phone-layout plan.

**Tools used.** `list-workbook-datasources` (to confirm the workbook is open and readable), `list-dashboards` (to enumerate dashboards), `list-worksheets` (to inspect the sheets on the source dashboard), `list-available-fields` (to identify KPI vs chart candidates), `get-dashboard-xml` (to read the desktop dashboard's container tree and filter cards so Blueprint recommendations for P2/P6/P7/P15 cite real evidence rather than asking the author to describe their own layout), `get-workbook-inventory` (to check for an existing summary/KPI calc before recommending the author build a new one for P3). Read-only. No mutation tools invoked.

Steps:

1. Call `list-dashboards` to enumerate available dashboards. Confirm which desktop dashboard is the source. If only one exists, use it. If unclear, ask. If `list-dashboards` returns empty or errors, state that no workbook or dashboard was found. Do not proceed on an assumed dashboard, but do not stop at a bare refusal either: offer Preference-flag mode (which does not require a workbook), and offer to walk through the P-catalog summary as a reading reference so the author knows what the skill will check once they open a workbook. Ask which of those helps.
2. Call `get-dashboard-xml` on the source dashboard to read the container tree, filter cards, and title/legend zones. Call `list-worksheets` scoped to the source dashboard, plus `list-available-fields` if KPI candidates need to be identified. Note KPI sheets, chart sheets, any legends or titles, and container orientation. If `get-dashboard-xml` is unavailable or `list-worksheets` returns empty for a dashboard `list-dashboards` confirmed exists, treat this as a tool-read failure (not "no sheets") and say so plainly rather than emitting an empty plan or asking the author to describe their own desktop structure from scratch.
3. Call `get-workbook-inventory` once to check for an existing summary/KPI calc (SUM, AVG, or single-value aggregation already built) before recommending the author build a new one for P3. Point to the existing calc if one is found; only propose building a new KPI calc if none exists.
4. Run each of P1-P15 as a design decision, not an audit. For each, produce a recommendation:
   - **P4 Sheet count.** Propose which sheets to include and which to hide-on-phone. Ceiling 4-5 sheets.
   - **P15 Container swap.** Name each horizontal container and recommend vertical.
   - **P6 Filter count.** Cap visible filters at 2-3. Anything beyond that goes into a show/hide floating container per P7.
   - **P8 Tap-target sizing.** For each clickable element, note the current size (or ask the author) and target size 44x44px.
   - **P5 Hidden-on-phone candidates.** Dashboard title (usually), secondary KPIs, legends where the mark encoding carries the meaning.
5. Emit the plan as the Blueprint mode output template below.

**Portfolio scale (4+ dashboards).** If the workbook has more than a handful of dashboards and the author wants Blueprint plans for several, run one dashboard at a time rather than batching all plans into a single pass. Each plan depends on that dashboard's own sheet/container/filter inventory, and batching risks cross-contaminating recommendations between dashboards. Confirm with the author which dashboard to start with, deliver that plan, then ask whether to continue to the next.

### Audit mode

Trigger: author has an existing phone layout and asks for a review.

**Tools used.** `list-dashboards` (to enumerate dashboards and detect phone-layout presence), `get-dashboard-xml` (load-bearing read: the only tool that exposes the phone-layout zone tree, container orientation, filter cards, title zone, color legends, and fixed-sizing attributes used by P1-P2-P5-P6-P7-P8-P12-P15), `list-worksheets` (to inspect the sheets referenced by phone-layout zones), `list-available-fields` (to confirm color-encoded field references for P12). Read-only. No mutation tools invoked. If `get-dashboard-xml` is unavailable or returns empty for a dashboard `list-dashboards` confirmed has a phone layout, degrade gracefully: deliver only the P-rules that can be answered from `list-worksheets` and author-reported evidence (P4 sheet count, P8 author-reported sizes), and state plainly which rules were skipped for lack of structural read.

Steps:

1. Call `list-dashboards`. Confirm which dashboard's phone layout is under audit. If no phone layout is present on the target dashboard, offer Blueprint mode or Preference-flag mode instead (see Trigger conditions). If `list-dashboards` returns empty or errors, state that no workbook or dashboard was found. Do not proceed on an assumed dashboard, but do not stop at a bare refusal either: offer Preference-flag mode (which does not require a workbook), and offer to walk through the P-catalog summary as a reading reference so the author knows what the skill will check once they open a workbook. Ask which of those helps.
2. Call `get-dashboard-xml` on the target dashboard to read the phone-layout zone tree (container orientation, filter cards, title zone, color legends, fixed-sizing attributes). Call `list-worksheets` to resolve zone-to-sheet mappings. If author-reported sizes are needed (tap-target, viewport), ask once and cite what they gave. If `get-dashboard-xml` is unavailable or `list-worksheets` returns empty for a phone layout `list-dashboards` confirmed exists, treat this as a tool-read failure, state so plainly, and run only the P-rules answerable from the data you did get (never report a clean audit on a read failure).
3. Run each P-rule against the phone layout. For each rule, record PASS, NEEDS ATTENTION, or FAIL with the evidence.
4. Rank findings by severity (see phone-rule-catalog.md for severity per rule).
5. Emit the audit as the Audit mode output template below.

**Portfolio scale (4+ dashboards).** If the author wants Audit mode run across many dashboards' phone layouts in one request, run and report one dashboard at a time rather than batching. Each audit's findings must trace to that dashboard's own evidence. Confirm the order with the author before starting the second dashboard.

### Preference-flag mode

Trigger: author explicitly says they never wanted a phone layout, or asks to turn off auto-generation.

**Tools used.** `list-dashboards` (only if the author wants an inventory of existing phone layouts to clean up). Otherwise no workbook read is required for this mode.

Steps:

1. Confirm the intent: "You want to stop Tableau from auto-generating a phone layout on new dashboards. Not delete an existing one."
2. Emit the numbered Desktop steps from `skill-expertise/preference-flag-steps.md`. Do not attempt to flip the preference.
3. Offer to run Audit mode on any existing phone layouts if the author wants those cleaned up too. If yes, call `list-dashboards` to enumerate.

## Rule catalog summary (full catalog in phone-rule-catalog.md)

The P-catalog is first-party. All 15 rules ship as the skill's own guidance.

**Layout structure.** P1 fixed sizing on the phone layout. P2 vertical stack over horizontal containers. P3 KPI band at the top visible without scrolling. P4 sheet count ceiling 4-5. P5 hidden-on-phone flag on dashboard title, secondary KPIs, and legends where mark encoding carries the meaning.

**Filter and interaction strategy.** P6 filter count ceiling 2-3 visible. P7 show/hide floating container when 3+ filters are needed. P8 tap-target size 44x44px minimum. P9 parameter actions preferred over quick filters for anything requiring two taps on desktop.

**Content and hierarchy.** P10 vertical scroll length under 3 phone-screens-tall. P11 text size floor 12pt body, 14pt headers. P12 color-only encoding accessibility (critical needs a second encoding).

**Author intent.** P13 preference-flag check (does the author actually want a phone layout?). P14 sheet-inclusion audit (any desktop sheet auto-included that should be hidden-on-phone?). P15 container-swap audit (any horizontal container from desktop that should be vertical on phone?).

## Severity levels

- **FAIL.** Ships broken. Fix before Mobile users see it.
- **NEEDS ATTENTION.** Works but degrades UX. Fix in the next revision.
- **PASS.** Meets the rule. No action.

Full severity mapping per rule lives in phone-rule-catalog.md.

## Output format

### Blueprint mode output (chat, no file)

1. **Source dashboard.** Named. Sheet count, container count, filter count in one sentence.
2. **Sheet inclusion plan.** One line per sheet. Keep or hide-on-phone with reason.
3. **Container swap plan.** Named containers with orientation change.
4. **Filter-collapse strategy.** Which filters stay visible, which move to show/hide, which become parameter actions.
5. **Tap-target sizing table.** Element, current size (author-reported), target 44x44px.
6. **Hidden-on-phone candidates.** Bulleted list with reason per item.
7. **Numbered Desktop UI steps.** In sequence for the author to execute.

### Audit mode output (chat, no file)

1. **One-line verdict.** "Ships broken," "Needs attention," or "Ready for Mobile users."
2. **Findings ranked by severity.** Each finding cites the P-rule ID, severity, evidence, and Desktop fix path.
3. **Preference-flag recommendation.** Only if the author signaled they never wanted a phone layout (P13 trigger).
4. **Handoff options.** Named skills for downstream work with manual fallbacks per HC-7.

### Preference-flag mode output (chat, no file)

1. **Confirmed intent.** One line.
2. **Numbered Desktop steps.** Verbatim from preference-flag-steps.md.
3. **Optional Audit offer.** If existing phone layouts are worth cleaning up first.

## Composability

Every downstream target below is optional. Users may have installed only this skill or a subset of the fixers.

Wording pattern for each route in the verdict:

> "If you have `<skill-name>` installed, hand this off to it. If not, do this: `<manual fallback>`."

| Situation | Route target (if installed) | Manual fallback (if not) |
|---|---|---|
| Author needs a full desktop redesign before the phone layout makes sense | `viz-planner` | (1) Simplify the desktop dashboard first. (2) Cut sheets to 4-5 core views. (3) Come back for the phone Blueprint once the desktop is clean. |
| Audit finds design issues that also affect the desktop layout | `viz-critique-pro-studio` | (1) Note the desktop-affecting findings separately. (2) Author reviews the desktop layout manually against the 7-domain framework or against their team's design standard. |
| Author is running pre-publish hygiene | `publish-readiness` | (1) Author runs a pre-publish check manually: unused fields hidden, sheet names not defaulted, dashboard titles present, extract configured. |
| Author needs assembly-hygiene review | `dashboard-preflight` | (1) Author checks manually: zone alignment, sheet-to-zone mapping, filter-action wiring, parameter linkage, canvas size sanity. |

Emit `phone_layout_audit/1` in the verdict when handing off (source dashboard, findings summary, target skill, seed values). The receiving skills can accept the handoff or run standalone. When no downstream skill is available, the verdict still ships: the manual fallback lives beside every route.

## Validation Gate (run before delivering the output)

Before returning Blueprint or Audit output, confirm each of these. If any fail, revise or state the limitation instead of shipping.

- **V1.** The workbook was read and the source or target dashboard is named explicitly.
- **V2.** Every finding or recommendation cites a P-rule ID from the locked catalog (HC-2).
- **V3.** Tap-target sizes cite 44x44px minimum numerically (HC-8).
- **V4.** No community-resource URLs pasted (HC-6).
- **V5.** No tablet-layout advice given (HC-3).
- **V6.** No mutation attempted. Every finding is a manual Desktop instruction (HC-1).
- **V7.** If the layout passes all rules, the verdict says "Ready for Mobile users" and does not manufacture findings (HC-4).
- **V8.** Every route in the output carries a manual fallback path the user can follow without the target skill installed (HC-7).
- **V9.** Preference-flag recommendation is delivered as numbered steps, not as an action the skill claims to take (HC-5).
- **V10.** If P7 (show/hide floating container) is recommended, the user's Tableau version was confirmed to be 2020.4 or later, or a degraded fallback (separate filters-only worksheet) was offered (HC-9).

## Anti-patterns (auto-fail if any of these happen)

- Mutating the workbook to fix a finding. Every fix is manual.
- Inventing a rule mid-run instead of citing a P-catalog ID.
- Hand-waving tap-target sizing without the 44x44px number.
- Running rules against a tablet layout.
- Manufacturing findings when the phone layout is actually clean.
- Claiming to have flipped the auto-phone-layout preference flag.
- Pasting a URL to any community resource.
- Naming a downstream skill in the output without a manual fallback beside it.
- Refusing to complete the diagnosis because a downstream target skill is missing.
- Recommending P7 (show/hide floating container) to a user on Tableau pre-2020.4 without offering the degraded fallback (HC-9).

## Trigger conditions

**Positive triggers (Blueprint mode):**

- "phone layout blueprint"
- "mobile blueprint"
- "recommend a phone layout"
- "make this dashboard mobile-friendly"
- "tableau mobile blueprint"

**Positive triggers (Audit mode):**

- "audit my phone layout"
- "why does my Tableau Mobile look broken"
- "phone-form-factor review"
- "review my phone layout"
- "check my mobile layout"

**Positive triggers (Preference-flag mode):**

- "turn off phone layout auto-generation"
- "stop auto-generating phone layouts"
- "I never wanted a phone layout"
- "disable phone layout"

**Negative triggers (route elsewhere per Composability table):**

- Full desktop design from scratch
- Desktop-form-factor viz critique
- Pre-publish hygiene across the workbook
- Dashboard assembly hygiene
- Actually building or editing the phone layout in Desktop
- Tablet form factor
- Tableau Cloud/Server mobile app config or MDM

## Out-of-scope requests: name what IS in scope

When a request lands outside this skill's boundaries, do not stop at "out of scope." Name what IS in scope and offer the closest useful thing.

- **MDM or Server-side mobile app configuration.** Say plainly this skill cannot configure MDM or Server admin settings. Then name what IS in scope: the per-workbook Desktop phone-layout settings, the Preference-flag mode for turning off auto-phone-layout generation on new dashboards, and Audit mode against existing phone layouts. Ask whether any of those solves the underlying need. If the underlying need is "disable auto-phone-layout across the org," clarify that the fix ships per-workbook via Preference-flag mode, not via Server admin.
- **Tableau Cloud/Server publishing or permissions.** Out of scope. In-scope alternative: run Audit before the author publishes so the phone layout is not broken on Mobile users' first open. Offer to route to `publish-readiness` (or its manual fallback per HC-7) for the broader pre-publish check.
- **Desktop version upgrade advice.** Out of scope. In-scope alternative: HC-9 degrades P7 automatically if the author is pre-2020.4, so the user gets a working recommendation regardless. If the user is considering an upgrade, note that P7 needs Tableau 2020.4 or later.

The pattern: refuse-only outputs are a design failure. Every refusal should carry the in-scope alternative that gets the user closer to their goal.

## Standalone use

If the user has only this skill installed, drop the "if installed" clause from routes and lead with the manual fallback. Never refuse to complete a Blueprint or Audit because a downstream target is missing. The output is fully usable on its own via the manual paths in the Composability table and the numbered Desktop steps in `skill-expertise/desktop-ui-fix-paths.md`.

## Graceful Degradation

These rules apply whenever something this skill needs is missing or fails. More specific rules elsewhere in this file take precedence.

- **Nothing to work on.** If no workbook is open, there is no data source, or the named calc, sheet, dashboard, or data source isn't found, stop before any other step. Say what you found (list the real names, if any) and ask the user to open the workbook or pick one. Never work on a guessed or closest-match target.
- **Tool call fails, times out, or returns empty.** Retry once, then stop retrying. Mark everything that depended on that call as not checked, continue with what you still can, and say which step failed. If the failed call was a write, stop and report the workbook's current state instead of continuing.
- **Partial results.** If any check, sheet, field, or data source wasn't evaluated, the summary says so (Partial: N of M checked; not checked: [list]). Never give a clean, ready, or PASS verdict on a partial run.
- **Reference file won't open.** Use the rules summarized in this file, say [file] unavailable; using the built-in summary, and never make up thresholds, rule IDs, or Desktop menu steps from memory.
- **Peer skill not installed.** If this skill would hand off to another skill that isn't available, say so and give the manual Desktop step instead. A handoff is never the only next step.
- **Platform gap.** If no tool can do something, say so plainly and give the manual Desktop path.
- **Failure messages.** Tell the user in plain language what was done, what wasn't, and the next step. No raw errors, stack traces, or JSON.
- **No fabrication.** Never invent fields, values, findings, or results to fill a gap left by a failed read.
