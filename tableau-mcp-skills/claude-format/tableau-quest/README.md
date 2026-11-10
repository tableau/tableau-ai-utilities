# TableauQuest

**Judgment Through Consequences**

An interactive choose-your-own-adventure skill for [Cowork](https://claude.com/product/cowork) that teaches Tableau judgment through realistic organizational consequences. No tutorials. No hints. Just decisions, pressure, and outcomes.

Created by Adam Mico

---

## What Is This?

TableauQuest is a simulation. You're dropped into a realistic Tableau scenario (a dashboard is broken before a board meeting, two teams report conflicting numbers, a data incident triggers a compliance review) and you navigate it through numbered choices. Every decision has consequences that ripple through your organization: trust shifts, scars form, stakeholders remember.

The skill teaches judgment, not syntax. A technically perfect solution delivered without governance gets 1 sparkle. A pragmatic fix that preserves trust and follows process gets 3.

---

## Quick Start

### Prerequisites
- [Cowork](https://claude.com/product/cowork) desktop app with Claude
- (Optional) Tableau MCP connector for site-grounded scenarios

### Installation
1. Download the `tableau-quest` folder from this repo (`SKILL.md` plus the `skill-expertise/` files)
2. In Cowork, save it as a custom skill named `tableau-quest`, including the `skill-expertise/` files
3. Pasting only the SKILL.md content leaves out the scenario, menu and example files in `skill-expertise/`, so use the full folder

### Your First Game

Type any of these to start:
```
tableau quest
```
```
adventure mode
```
```
teach me tableau through a scenario
```

TableauQuest will greet you and walk through intake:
1. **Audience level** (executive / analyst / developer / mixed)
2. **Tableau experience** (beginner / intermediate / advanced / expert)
3. **Scenario focus** (category preference or your real situation)
4. **Genre** (Straightforward Reality, Corporate Thriller, Sci-Fi, Dark Fantasy, Noir, Prestige Drama, Office Comedy)
5. **Session depth** (Blitz 3-5 decisions, Quick 6-10, Standard 15-20, Deep 30+)
6. **Mode** (Single Scenario by default, Campaign, or Field Quest)

Skip anything you have already said, or answer "you choose" to take the defaults (mixed audience, intermediate, Straightforward Reality, Quick, Single Scenario).

Recommend starting with **Blitz** or **Quick** for your first run. You'll get the full experience in 5-10 minutes.

---

## Modes

### Single Scenario (Default)
One complete situation. Make decisions, face consequences, receive your Ending Screen with a Sparkle rating. After finishing, you can replay with the same settings, adjust, or end.

### Campaign
A multi-scenario campaign (7-10 scenarios total) across three arcs:
- **Proving Ground** (2-3 scenarios). Small-medium stakes. Build reputation.
- **Growing Scope** (3-4 scenarios). Cross-team visibility. Political dynamics. Callbacks to earlier decisions.
- **Strategic Impact** (2-3 scenarios). Executive stakes. Full organizational memory.

Consequences carry across scenario boundaries. Scars earned in Arc 1 constrain options in Arc 3. At Campaign completion, you receive a Judgment Trajectory showing how your profile evolved.

### Field Quest
Scenarios grounded in YOUR actual Tableau environment. If you have the Tableau MCP connector configured, TableauQuest queries your live site (recently updated workbooks, datasources and their fields, popular and uncertified content) and weaves real workbook names, field names and project structure into the narrative. Row counts, refresh schedules, users and permissions are not available, so those details are invented, and the people in the story are always fictional.

Without the MCP connector, you can still paste your real situation (>50 words) and play through it as a simulation.

---

## Genres

Genre changes tone only. Mechanics, consequences, and sparkle evaluation are identical regardless of genre.

| Genre | Tone |
|-------|------|
| Straightforward Reality | Default. Office as it is. |
| Corporate Political Thriller | Power plays, backchannels, leverage |
| Sci-Fi Megacorp | Same problems, neon lighting |
| Dark Fantasy Guilds | Arcane data councils, guild politics |
| Noir Investigation | Hard-boiled, cynical narration |
| Prestige Office Drama | Character-driven, slow burn |
| Office Comedy | Same stakes, funnier delivery |

---

## Sparkle Evaluation

Every scenario ends with a Sparkle Level:

| Level | Meaning |
|-------|---------|
| ✨ | Poor judgment. Governance bypassed, warnings ignored, trust lost. |
| ✨✨ | Mixed judgment. Some good calls balanced by shortcuts or missed signals. |
| ✨✨✨ | Strong judgment. Assumptions validated, trust preserved, long-term thinking demonstrated. |

Sparkle reflects judgment quality, not technical correctness. This README is the public description of how TableauQuest works; in-game, the skill keeps its internal instructions and detailed rubric private.

---

## Pixel Art

Every Ending Screen includes a bracketed pixel art scene description that visually represents your outcome. The sparkle level affects the scene's lighting, stability, and tone (intact vs. fractured systems, glow vs. flicker).

These descriptions are ready-made image generation prompts. Copy the bracketed text and paste it into an image generator like [Nano Banana](https://nanobanana.com) or ChatGPT to create your unique pixel art scene for each scenario you complete.

---

## Scenario Categories

TableauQuest generates scenarios from 10 archetype categories. It is not limited to fixed seeds; scenarios are generated dynamically based on your experience, profile, and (in Field Quest) actual site content.

- **A) Publishing and Governance Failures**
- **B) Metric Wars and Definition Conflicts**
- **C) Performance and Adoption Collapse**
- **D) Refresh and Reliability Incidents**
- **E) Security and Compliance Triggers**
- **F) UX and Trust Erosion**
- **G) Political and Organizational Conflict**
- **H) Migration and Platform Change**
- **I) Executive Demo Disasters**
- **J) Silent Decay and Long-Term Failure**

---

## Judgment Profile (Hidden)

TableauQuest silently tracks your decision patterns across 5 traits:

- **Risk Bias** (reckless / impatient / cautious / balanced)
- **Governance Tolerance** (low / medium / high)
- **Stakeholder Empathy** (low / medium / high)
- **Evidence Discipline** (weak / moderate / strong)
- **Repair Behavior** (avoids / partial / consistent)

Your profile shapes how the world responds. Reckless players face earlier scrutiny. Cautious players face funding questions. The profile is never shown during gameplay (only surfaced in Campaign Debrief after completing a full Campaign).

---

## Persistent State

TableauQuest saves your state between sessions:
- Judgment profile and your intake settings carry forward (so "same settings" replays work)
- Scars persist (and can heal with 3-5 good decisions)
- Campaign progress is preserved
- Abandoned scenarios are remembered (and carry consequences)

Say "new identity", "start fresh", or "reset profile" to wipe your slate.

---

## Skill Handoffs

After a scenario, if the content maps naturally to real practice, TableauQuest offers bridges to other Cowork skills:

- Calculation-heavy scenarios -> **Tableau Calc Engine**
- Governance/site health scenarios -> **Tableau Governance Scanner**
- Dashboard sprawl/discovery scenarios -> **Tableau Content Compass**

---

## File Structure

```
tableau-quest/
  README.md       <- You are here
  SKILL.md        <- The skill's rules and game engine (install this in Cowork with skill-expertise/)
  skill-expertise/                  <- Reference material loaded by SKILL.md when needed
    blitz-example-turns.md          <- Full Blitz example sequence
    narrative-arc-templates.md      <- Beat templates per session depth
    player-facing-scripts.md        <- Lite offer, menus, debrief, handoff text
    scenario-archetypes.md          <- Incident archetypes A-J, category combos, consequence catalog
    site-grounded-mode.md           <- Field Quest MCP site grounding
```

---

## FAQ

**Can I play without the Tableau MCP connector?**
Yes. Field Quest's site-grounded mode requires it, but Single Scenario and Campaign work without any external connections.

**Is this the same as the TableauQuest GPT?**
Same core design, enhanced for Cowork. Key differences: persistent state across sessions (the GPT has no memory), MCP integration for live site grounding (impossible in ChatGPT), and skill handoffs to other Tableau tools.

**Can I modify the skill?**
Yes. Fork the repo, edit SKILL.md, and install your version. The skill is a folder: SKILL.md plus the reference files in skill-expertise/.

**How long does a session take?**
Blitz: 5-10 minutes. Quick: 15-25 minutes. Standard: 45-60 minutes. Deep: 90+ minutes.

---

## Credits

Designed and built by Adam Mico
