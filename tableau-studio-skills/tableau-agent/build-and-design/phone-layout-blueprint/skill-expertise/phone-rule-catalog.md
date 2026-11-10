# Phone Layout Rule Catalog (P1-P15)

Locked, first-party rule catalog for phone-layout-blueprint. Every Audit finding and Blueprint recommendation cites a rule ID from this file. Do not invent rules mid-run.

Severity legend:

- **FAIL.** Ships broken on a real phone. Fix before Mobile users see it.
- **NEEDS ATTENTION.** Works but degrades UX or accessibility. Fix in next revision.
- **PASS.** Meets the rule. No action.

## Layout structure

### P1. Fixed sizing on the phone layout

**Severity ceiling:** FAIL if auto-sizing is on.

**Rule.** Phone layouts must use Fixed sizing. Automatic sizing forces the dashboard to re-render on every session, which is slow on mobile networks and produces layout jitter as containers reflow.

**Evidence signal.** Dashboard pane → Size → check for "Fixed" vs "Automatic" or "Range."

**Rationale.** Fixed-size dashboards can be cached by the mobile client and render on open without a reflow pass. Auto-sizing negates that benefit and adds a visible reflow on every open.

### P2. Vertical stack over horizontal containers

**Severity ceiling:** FAIL if any top-level horizontal container spans more than 375px on the phone canvas.

**Rule.** Phone dashboards read top-to-bottom. Horizontal containers force horizontal scrolling on narrow viewports, which users do not expect on phone.

**Evidence signal.** Layout pane → check the top-level container. Horizontal = FAIL. Vertical = PASS.

**Rationale.** Phone viewports are 375-430px wide typically. Any horizontal container wider than that either scrolls horizontally (bad UX) or shrinks marks below legibility.

### P3. KPI band at the top, visible without scrolling

**Severity ceiling:** NEEDS ATTENTION if the top 500px of the phone layout does not contain a summary KPI.

**Rule.** The first thing a Mobile user sees should be the headline number. Anything else buries the point.

**Evidence signal.** Read the top-most sheet on the phone layout. Is it a KPI (single number, delta indicator, or small comparison bar)? If not, flag.

**Rationale.** Mobile users open the dashboard for a check-in, not a deep dive. If the KPI is below the fold, they will not scroll to find it.

### P4. Sheet count ceiling 4-5 sheets

**Severity ceiling:** FAIL at 7+ sheets. NEEDS ATTENTION at 6.

**Rule.** More than 5 sheets on the phone layout forces long scrolls and slow initial render. Every sheet must query and layout before the dashboard displays.

**Evidence signal.** Count sheets visible on the phone layout. Auto-generated phone layouts often include every desktop sheet by default and blow past this ceiling.

**Rationale.** Each sheet adds render time. Users on phone want a summary view, not a full recreation of the desktop dashboard.

### P5. Hidden-on-phone flag on dashboard title, secondary KPIs, and legends where mark encoding carries the meaning

**Severity ceiling:** NEEDS ATTENTION if any of the flagged categories are visible on phone without a design reason.

**Rule.** Dashboard titles eat vertical real estate above the fold. Secondary KPIs dilute the primary KPI band. Legends duplicate information already carried by mark color, shape, or size.

**Evidence signal.** Layout pane → for each of the above categories, check the "Hidden on phone" flag. If unset and the element is visible on phone, flag.

**Rationale.** Every hidden-on-phone element buys back scroll length and render time without losing information.

## Filter and interaction strategy

### P6. Filter count ceiling 2-3 visible

**Severity ceiling:** FAIL at 5+ visible filters. NEEDS ATTENTION at 4.

**Rule.** More than 3 always-visible filters on a phone layout crowds the KPI and forces users into unnecessary control-plane management before they see data.

**Evidence signal.** Count filter cards visible on the phone canvas. Filters inside a show/hide floating container do not count against this ceiling (see P7).

**Rationale.** Phone users want to see the answer, then filter if needed. Filters as the first thing they see reverses that.

### P7. Show/hide floating container when 3+ filters are needed

**Severity ceiling:** NEEDS ATTENTION if 3+ filters are required by the analysis and none are in a show/hide floating container.

**Rule.** When the analysis genuinely needs 3 or more filters, put them in a show/hide floating container triggered by a filter icon.

**Evidence signal.** Layout pane → floating container with show/hide state and a button object bound to its visibility.

**Rationale.** Show/hide floating containers reveal filters on demand without permanently occupying viewport space.

**Version requirement (HC-9).** Show/hide floating containers with button-triggered visibility require Tableau 2020.4 or later. If the user is on a pre-2020.4 version, degrade to the fallback: build a separate filters-only worksheet on the phone layout that lives at the top or bottom of the vertical stack, and hide it on desktop. The rule still fires as NEEDS ATTENTION, but the fix path in desktop-ui-fix-paths.md P7 offers both the modern and fallback approaches. Ask the version if it is not obvious from context.

### P8. Tap-target size 44x44px minimum

**Severity ceiling:** FAIL on any clickable element under 44x44px.

**Rule.** Every filter, button, parameter control, or clickable mark on the phone layout must be at least 44x44px. This is the platform convention for reliable finger-tap accuracy.

**Evidence signal.** Ask the author to report the size of each interactive element, or read the container's fixed size in the workbook XML. Marks inside a chart are sized by the mark type and data density; check that the smallest clickable mark is 44x44px minimum.

**Rationale.** Below 44x44px, tap accuracy drops and users mis-fire filters or hit adjacent controls.

### P9. Parameter actions preferred over quick filters for anything requiring two taps on desktop

**Severity ceiling:** NEEDS ATTENTION if quick filters are used where a parameter action would be one tap.

**Rule.** On phone, a quick filter often requires open-the-filter, tap-a-value, dismiss-the-filter (3 taps). A parameter action on a mark or button is 1 tap.

**Evidence signal.** For each quick filter on the phone layout, ask: could a parameter action do the same job with fewer taps?

**Rationale.** Phone interaction budget is small. Every extra tap costs a percentage of users who give up before they see the result.

## Content and hierarchy

### P10. Vertical scroll length under 3 phone-screens-tall

**Severity ceiling:** FAIL at 5+ screens tall. NEEDS ATTENTION at 4.

**Rule.** A phone layout longer than 3 phone screens (roughly 2000px on a modern phone) buries content Mobile users will never scroll to.

**Evidence signal.** Read the phone layout's fixed height. Compare to 3x viewport height (roughly 2000-2400px depending on phone).

**Rationale.** Empirically, Mobile users scroll 1-2 screens on a check-in view. Anything below that is dead space that adds render time.

### P11. Text size floor: 12pt body, 14pt headers

**Severity ceiling:** FAIL on any body text under 10pt or headers under 12pt.

**Rule.** Body text on phone layouts must be 12pt or larger. Headers 14pt or larger. Smaller reads as broken on a 375px viewport.

**Evidence signal.** Check text object font sizes on the phone layout. Chart tooltips and axis labels also count.

**Rationale.** Desktop text sizes (9-10pt) do not translate to phone. What reads clearly on a 27-inch monitor is unreadable on a 6-inch phone.

### P12. Color-only encoding accessibility

**Severity ceiling:** NEEDS ATTENTION if a critical distinction is carried by color alone.

**Rule.** Anything critical on the phone layout (positive vs negative, above vs below target, on-track vs off-track) needs a second encoding besides color. Icon, prefix, or shape.

**Evidence signal.** For each color-encoded distinction, check if there is a redundant encoding (icon in the mark label, arrow prefix, shape variation).

**Rationale.** Phone screens vary in color rendering (OLED vs LCD, brightness settings, outdoor sunlight). Color-only encoding fails on some devices and for color-blind users.

## Author intent

### P13. Preference-flag check

**Severity ceiling:** NEEDS ATTENTION if the author signals they did not want a phone layout.

**Rule.** If the author says "I never wanted a phone layout" or similar, surface the Desktop preference to disable auto-generation on new dashboards. This rule triggers Preference-flag mode.

**Evidence signal.** Author message contains any of: "I did not want," "auto-generated," "why is there a phone layout," "delete the phone layout," "turn off phone layouts."

**Rationale.** Many authors publish workbooks without realizing the phone layout was auto-generated and pushed. Fixing this at the source is more valuable than auditing individual layouts.

### P14. Sheet-inclusion audit

**Severity ceiling:** NEEDS ATTENTION per sheet that should be hidden-on-phone but is not.

**Rule.** Auto-generated phone layouts include every desktop sheet by default. Any sheet that duplicates data shown elsewhere, adds detail Mobile users will not consume, or is design-only (spacers, dividers) should be flagged as hidden-on-phone.

**Evidence signal.** Compare desktop sheets vs phone-included sheets. For each phone-included sheet, ask: is this a summary view a Mobile user wants?

**Rationale.** The auto-generator has no judgment about what belongs on phone. It includes everything. The author's judgment must be applied.

### P15. Container-swap audit

**Severity ceiling:** NEEDS ATTENTION per horizontal container that should be vertical.

**Rule.** Every horizontal container in the desktop layout should be reconsidered for phone. Default recommendation is vertical.

**Evidence signal.** Layout pane on the phone layout. Count horizontal containers. Each is a candidate for swap unless the content genuinely reads left-to-right (rare on phone).

**Rationale.** Desktop dashboards use horizontal containers for side-by-side comparison. Phone users compare vertically by scrolling.

## Rule interactions

**P4 + P14 together.** Sheet count ceiling and hidden-on-phone audit are two sides of the same coin. If P4 fails, run P14 to identify which specific sheets to hide.

**P6 + P7 together.** Filter count ceiling and show/hide container are paired. If P6 fails, P7 is the remedy.

**P2 + P15 together.** Vertical stack rule and container-swap audit are paired. P2 flags the current state; P15 names the specific containers to swap.

**P13 short-circuits everything else.** If P13 triggers (author never wanted the layout), Preference-flag mode runs and the P1-P12 audit is offered as optional cleanup for any existing phone layouts.
