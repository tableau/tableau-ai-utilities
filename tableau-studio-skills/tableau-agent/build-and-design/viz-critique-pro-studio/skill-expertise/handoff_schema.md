# Handoff Schema for `viz_critique_report/1` (Locked)

Every successful `viz-critique-pro-studio` invocation emits this schema. Downstream skills (`viz-planner`, `worksheet-builder`, `chart-swap-advisor`, `dashboard-preflight`, `workbook-auditor`) may consume it. Schema is versioned; unknown versions refused by downstream per HC#8.

## Full Schema

```yaml
schema_version: viz_critique_report/1
mode: {workbook_scan | image_only}
mode_source: {workbook_open | workbook_closed | user_override}
image_only_disclaimers: [{disclaimer_string}, ...]
workbook_name: {name_or_null}
dashboard_name: {name_or_null}
dashboard_id: {luid_or_null}
image_metadata:
  provided: {true | false}
  aspect_ratio: {width_to_height_ratio}
  long_form_detected: {true | false}
  sections_covered: {full | top | middle | bottom | partial}
  workbook_open_at_time_of_evaluation: {true | false}
  xml_context_used: {true | false}
audience:
  stated: {true | false}
  audience_type: {Executive | Manager | Analyst | Operations | External | null}
  inference_confidence: {High | Medium | Low | null}
ethics_violations:
  - trigger_id: {E-DECEPTIVE-SCALE | E-CHERRY-PICKED-COMPARISON | ... | E-INTENT-AMBIGUOUS}
    severity: {Critical | Warning | Info}
    rationale: {short_string}
    fix_recommendation: {short_string}
ethics_cap_applied:
  triggered: {true | false}
  cap_ceiling: {59 | 79 | null}
  raw_overall_score: {N_or_null}
domains:
  - domain_id: {1 | 2 | 3 | 4 | 5 | 6 | 7}
    domain_name: {Audience Adaptation | Message Alignment | Chart Usage | Layout and Hierarchy | Color and Typography | Accessibility | Interactive-Design Signals}
    score: {N.N | "unscanned"}
    anchor_matched: {Example X.Y | null}
    confidence: {High | Medium | Low | null}
    rationale: {short_string}
    signals_evaluated: [{signal_string}, ...]
    recommendations: [{recommendation_string}, ...]
overall_score: {N}
raw_overall_score: {N}
tier: {Showcase-Ready | Vizzy Good | On the Right Track | Work in Progress | Needs a Rework | Back to the Drawing Board}
top_strengths:
  - {strength_string}
top_recommendations:
  - {recommendation_string}
rebuild_handoff_payload:
  route_to_viz_planner: {true | false}
  route_to_worksheet_builder_per_chart: [{worksheet_name}, ...]
  route_to_chart_swap_advisor_per_chart: [{worksheet_name}, ...]
  route_to_dashboard_preflight: {true | false}
  route_to_format_drift_scanner: {true | false}
  route_to_interaction_validator: {true | false}
  rationale: {short_string}
delivery:
  tier_a_rendered: {true | false}
  tier_b_saved: {true | false}
  tier_b_file_path: {absolute_path_or_null}
  tier_b_format: {md | txt | null}
drift_sample:
  detection_method: {hash_match | user_declared | not_applicable}
  image_hash: {hash_string_or_null}
  prior_run_scores: {[7-element_score_array]_or_null}
  new_run_scores: {[7-element_score_array]_or_null}
  per_domain_delta: {[7-element_delta_array]_or_null}
  drift_detected: {true | false | not_applicable}
  drifted_domains: [{domain_id}, ...]
  drift_banner_text: {string_or_null}
run_metadata:
  timestamp: {ISO-8601}
  diff_mode: {true | false}
  prior_report_hash: {string_or_null}
  session_score_cache_key: {string_or_null}
  tool_failures: [{tool_name}, ...]
notes: {optional_free_text}
```

## Field-by-Field

- **schema_version.** Always exactly `viz_critique_report/1`.
- **mode.** `workbook_scan` when the run used workbook XML alongside the image. `image_only` when the run used the image alone. Always populated.
- **mode_source.** `workbook_open` (default Workbook Scan mode fired), `workbook_closed` (fallback Image Only mode fired), or `user_override` (user opted to Image Only with workbook open).
- **image_only_disclaimers.** Populated only when mode is `image_only`. Contains the reduced-accuracy disclaimers for Domain 4 and Domain 7. Empty `[]` when mode is `workbook_scan`.
- **workbook_name / dashboard_name / dashboard_id.** Present when workbook was open. `null` when Image Only mode ran with workbook closed.
- **image_metadata.** Records image state at evaluation time. `long_form_detected: true` when aspect_ratio > 2:1. `sections_covered` reflects HC#12 partial-coverage state.
- **audience.** `stated: true` when user explicitly named the audience. `inference_confidence` populated when stated is false.
- **ethics_violations.** Every triggered violation with severity, rationale, and fix recommendation. Empty list `[]` when none fired.
- **ethics_cap_applied.** Records whether the cap was applied and the raw pre-cap score.
- **domains.** All 7 domains with scores, rationales, and cited signals. `score: "unscanned"` acceptable per HC#12 for Domains 4 and 7 on long-form partial reports.
- **overall_score.** Final score after ethics cap. Range 0-100.
- **raw_overall_score.** Pre-cap score for transparency. Equal to overall_score when no cap applied.
- **tier.** Matches the overall_score range per `scoring_tiers_and_tone.md`.
- **top_strengths / top_recommendations.** Cited in the chat summary and the longform report.
- **rebuild_handoff_payload.** Boolean routing flags plus per-chart lists. Downstream skills consume based on which flag is true.
- **run_metadata.** Operational metadata. `diff_mode: true` when the critique was reused from a prior report on an unchanged dashboard.
- **notes.** Optional free-text for edge cases.

## Downstream Consumer Expectations

- **`viz-planner`.** Consumes when `route_to_viz_planner: true` (typically Back to the Drawing Board tier). Uses the critique as input for a redesign session.
- **`worksheet-builder`.** Consumes per-chart rebuild payloads from `route_to_worksheet_builder_per_chart`.
- **`chart-swap-advisor`.** Consumes per-chart swap advisory from `route_to_chart_swap_advisor_per_chart`.
- **`dashboard-preflight`.** Consumes when `route_to_dashboard_preflight: true` (typically Layout-driven recommendations).
- **`format-drift-scanner`.** Consumes when `route_to_format_drift_scanner: true` (typically Color/Typography-driven recommendations).
- **`interaction-validator`.** Consumes when `route_to_interaction_validator: true` (Domain 7 runtime-behavior verification).
- **`workbook-auditor`.** Consumes critique deltas across runs for change digest enrichment.

## Verdict Contracts

**"Clean critique" (no ethics violations, all domains scored, no rebuild handoff):**

- `ethics_violations: []`.
- `ethics_cap_applied.triggered: false`.
- All 7 domains scored (no UNSCANNED).
- `rebuild_handoff_payload` fields all `false` / empty.
- `overall_score == raw_overall_score`.

**"Ethics-capped critique":**

- `ethics_violations` contains at least one Critical or Warning entry.
- `ethics_cap_applied.triggered: true` with cap_ceiling and raw_overall_score populated.
- `overall_score <= cap_ceiling`.
- Tier reflects the capped score.
- Banner text renders in the compact chat summary and the longform report.

**"Long-form partial critique":**

- `image_metadata.long_form_detected: true`.
- `image_metadata.sections_covered` is not `full`.
- Domains 4 and 7 may be `"unscanned"` with rationale.
- `overall_score` reflects partial coverage; tier caveat rendered in report.

**"Back to the Drawing Board critique" (overall < 50):**

- `tier: Back to the Drawing Board`.
- `rebuild_handoff_payload.route_to_viz_planner: true`.
- `top_recommendations` includes the highest-impact 1-2 items plus the routing recommendation.

## Refuse to Guess

If any required field cannot be populated, refuse delivery per HC#8. Never fake a domain score. Never assign a High confidence when signals don't support it. Never bypass the ethics cap.
