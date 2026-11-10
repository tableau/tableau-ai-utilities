# Scenario Archetypes (Scenario DNA)

The ten incident archetype categories (A-J) used to seed scenarios, the tables for combining them by session depth and experience, and the catalog of consequence types.

**A) Publishing and Governance Failures** -- Wrong project, lost certification, orphaned content, split truth, permission inheritance breaks, ownership conflicts.

**B) Metric Wars and Definition Conflicts** -- Two dashboards report different numbers, rolling vs. calendar time, filter changes KPI meaning, upstream schema shift, executive disagreement on "official" source.

**C) Performance and Adoption Collapse** -- Executive demo times out, volume spike slows everything, extract refresh doubles, mobile unusable, load time exceeds patience, dashboard abandoned.

**D) Refresh and Reliability Incidents** -- Credential rotation breaks refresh, incremental logic misfires, pipeline changes column meaning, schedules collide, data arrives late after decisions already made, weekend outage.

**E) Security and Compliance Triggers** -- RLS misconfigured, partner gains unintended access, PII visible in tooltip, audit demands lineage proof, unapproved data source used, legal requests takedown.

**F) UX and Trust Erosion** -- Dashboard overwhelms executives, filter behavior surprises users, tooltip contradicts KPI, color misleads urgency, dense views reduce adoption, simplification death spiral.

**G) Political and Organizational Conflict** -- New leader rejects existing work, team rivalry over definitions, budget cuts threaten platform, governance blocks release, competing BI tool challenge, ownership erupts.

**H) Migration and Platform Change** -- Desktop-to-Cloud breaks assumptions, legacy logic behaves differently, feature parity assumption fails, permission model shifts, "it worked before" meltdown.

**I) Executive Demo Disasters** -- Live demo fails to load, KPI wrong in board meeting, CEO challenges definition publicly, CFO demands reconciliation on the spot, meeting derailed by technical issue.

**J) Silent Decay and Long-Term Failure** -- Dashboard slowly loses users, reorg breaks ownership chain, documentation missing, no monitoring, metric drifts unnoticed, "why does nobody use this anymore?"

## Scenario Construction Tables

**Combine categories by session depth:**
- Blitz: 1 category, immediate impact (C, F, I preferred)
- Quick: 1-2 categories, related domains (C+F, B+F, A+G)
- Standard: 2-3 categories, cross-domain compounding (C+G+F, D+A+B)
- Deep: 3-5 categories cascading (D->A->G->E, C->F->B->G)

**Adapt by experience level:**
- Beginner: Prefer F, C, A. Clear signals. 1-2 stakeholders.
- Intermediate: Any single category. Mix technical + organizational. 2-4 stakeholders.
- Advanced: Any combination. Ambiguous signals. Political dynamics active. 3-6 stakeholders.
- Expert: Complex cascades. Minimal hand-holding. Full stakeholder ecosystem. 6-10 stakeholders.

## Consequence Catalog

**Soft Failures (recoverable with effort):**
Stakeholder questions approach, performance degrades but usable, minor permission friction, governance warning, timeline extension, repairable trust damage.

**Escalations (increased stakes and visibility):**
Director/VP meeting pulled, formal review initiated, competing solution emerges, budget scrutiny triggered, timeline pressure intensifies, scope threatened.

**Hard Failures (significant lasting impact):**
Dashboard pulled from production, data incident formally reported, project canceled or reassigned, key relationship severely damaged, reputation scar earned, career implications visible.
