# Tableau Phone Layout Blueprint

A read-only advisory skill that designs or audits the phone layout for a Tableau dashboard, then hands you numbered Desktop steps to apply the fixes yourself. Catches the ship-broken auto-generated phone layouts most authors never asked for.

**Example:** "Audit my phone layout."

## What it does

Runs in three modes. Blueprint mode produces a phone-layout plan from an existing desktop dashboard: which sheets to include, which containers to swap vertical, which filters to collapse, which elements to hide on phone, and 44x44px tap-target targets for every clickable element. Audit mode runs a locked 15-rule catalog (P1 through P15) against an existing phone layout and returns severity-ranked findings. Preference-flag mode shows you how to disable auto-phone-layout generation on new dashboards if you never wanted one in the first place. Every finding and recommendation comes with numbered Desktop UI steps you execute manually.

## When to use it

- "I just published a dashboard and Tableau Mobile looks broken."
- "I need a phone layout for this dashboard but have no idea where to start."
- "Why does the auto-generated phone layout keep showing filters I never wanted on phone?"
- "I never wanted phone layouts. How do I turn off auto-generation?"
- "I want to review my phone layouts before shipping to Mobile users."

## When NOT to use it

- Not for designing the desktop dashboard from scratch (use viz-planner)
- Not for critiquing the desktop viz (use viz-critique-pro-studio)
- Not for pre-publish hygiene across the whole workbook (use publish-readiness)
- Not for dashboard assembly hygiene (use dashboard-preflight)
- Not for authoring or editing the phone layout in Desktop (this skill is read-only advisory)
- Not for tablet layouts
- Not for Tableau Cloud/Server mobile app config or MDM (out of scope)

## How to trigger it

- "phone layout blueprint"
- "mobile blueprint"
- "audit my phone layout"
- "why does my Tableau Mobile look broken"
- "phone-form-factor review"
- "recommend a phone layout"
- "tableau mobile blueprint"
- "make this dashboard mobile-friendly"
- "turn off phone layout auto-generation"
- "I never wanted a phone layout"

## What you'll need

- Tableau Studio open with the agent connected
- A workbook with at least one dashboard (for Blueprint or Audit modes)
- Your Tableau version if you have 3+ filters on the phone layout (needed to pick between the modern show/hide floating container mechanic and the pre-2020.4 fallback)

## Example walkthrough

**Input:** "audit my phone layout"

**Output:**

```
Audit mode output - Product dashboard phone layout

Verdict: Needs attention.

Findings ranked by severity:
- FAIL - P5 (hidden-on-phone flag). Dashboard title "Product Drilldown"
  is present and visible on the Phone device layout, not hidden.
  Fix: Device Preview → Phone → select the title zone → uncheck
  "Show title" (or delete the title zone from the phone layout only).
- NEEDS ATTENTION - P8 (tap-target 44x44px minimum). Region filter
  dropdown's rendered size is unconfirmed. Fix if under 44x44px:
  resize the filter zone in Phone layout until it measures at least
  44x44px in the preview ruler.
- NEEDS ATTENTION - P12 (color-only encoding). Profit Ratio legend
  carries primary meaning. Add a redundant encoding (shape, label,
  or annotation) if the color distinction is critical.
- PASS - P1 (fixed sizing), P2 (vertical stack), P4 (sheet count),
  P6 (filter count), P15 (container swap).
```

Then the skill asks what you want to do next: hand off to another skill, run Audit on more dashboards, or just stop here.

## What you get back

- A severity-ranked list of findings tied to the locked P1-P15 catalog
- Numbered Desktop UI steps for each fix, in the right sequence to apply them
- An honest "Ready for Mobile users" verdict when nothing is actually broken
- Preference-flag path if you never wanted the phone layout in the first place
- Handoff options to downstream skills (publish-readiness, dashboard-preflight, viz-critique-pro-studio) with manual fallbacks if those skills are not installed

## Limitations

- Read-only. The skill does not apply fixes for you. Every finding is a manual Desktop instruction.
- Tap-target sizing asks the author to report sizes from Device Preview.
- If you ask for a tablet audit, the skill delivers the subset of P-rules that transfer directly (P1 Fixed sizing, P8 Tap-target 44x44px, P11 Text size floor) and the subset that partially applies (P4, P6, P10, P15 with looser thresholds).
- Pre-2020.4 Tableau versions do not have the button-triggered show/hide floating container. The skill detects the version and degrades P7 recommendations to a filters-only worksheet fallback.
- One phone layout at a time. If you have multiple dashboards with phone layouts to audit, the skill runs them one at a time and asks before moving to the next.
- Preference-flag mode cannot flip the preference for you. It gives you the Desktop steps to flip it yourself.

## Troubleshooting

- **"No phone layout exists on this dashboard."** The skill offers Blueprint mode (design one from scratch) or Preference-flag mode (keep it that way) instead of refusing. Pick either.
- **"No workbook open."** The skill offers Preference-flag mode (no workbook required) or walks through the P-catalog summary as a reading reference so you know what the skill will check once you open a workbook.
- **"The skill asked me for tap-target sizes."** Known limitation. Read the sizes from Device Preview in Tableau Studio and reply with the numbers. P8 findings will be precise once reported.
- **"The skill asked for my Tableau version."** P7 (show/hide floating container) requires 2020.4+. If you are on an older version, the skill will degrade to the filters-only worksheet fallback once you confirm.
- **"I want you to fix it for me."** The skill cannot mutate the workbook. It will convert the request into Audit mode plus numbered Desktop steps in fix-sequence order so you have the exact path to apply the fixes yourself.
- **"The skill named a route to a skill I do not have installed."** Every route carries a manual fallback. The skill will not stall waiting for a handoff target that is not available.

## Support

File issues in the Tableau Agent Skills repo.
