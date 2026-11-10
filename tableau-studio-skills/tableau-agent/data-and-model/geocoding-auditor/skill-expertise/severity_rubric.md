# Severity Rubric (Locked)

Deterministic severity assignment. Never re-interpret; look up the rule.

## Rate-Based Checks (G2, G3)

| Rate | Severity |
|---|---|
| >15% Unknown or Ambiguous | Critical |
| 5% - 15% | Warning |
| <5% | Info |

## Role-Assignment Checks (G1, G6)

| Condition | Severity |
|---|---|
| Role mismatch and field is placed on a shelf | Warning |
| Role mismatch and field is unused | Info |
| Datatype conflict (G6) | Warning |

## Structural Checks (G4, G5)

| Condition | Severity |
|---|---|
| Wrong-country resolution risk (G4) present | Warning |
| Missing hierarchy (G5), Country present without drill fields | Note |

## Sort Order in Report

1. Critical (top).
2. Warning.
3. Note.
4. Info (bottom).

Within each severity band, sort alphabetically by field name for determinism.

## Refuse to Interpret

Every finding must map cleanly to a row above. If a finding doesn't (e.g., "borderline ambiguous at exactly 5.0%"), pick the higher severity (Warning in that case) rather than inventing a middle band.
