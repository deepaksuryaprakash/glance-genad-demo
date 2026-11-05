-- Gold: decisions made live in the app, with predicted lift vs the static control
CREATE OR REFRESH MATERIALIZED VIEW glance_genad.gold.live_simulation_log
COMMENT 'Every Generate Ad Experience decision from the app: chosen theme/angle, guardrail blocks, predicted CTR/eCPM/attention lift.'
TBLPROPERTIES ('quality' = 'gold')
AS SELECT
  decision_id, created_at, CAST(created_at AS DATE) AS decision_date, requested_by, user_id, segment, brand, city,
  weather, time_slot, user_state, live_event, phone_skin, chosen_theme, chosen_angle, matched_component,
  relevance_score, headline, copy_source,
  pctr_static, pctr_generative, pctr_generative / NULLIF(pctr_static, 0) - 1 AS ctr_lift,
  pdwell_static_s, pdwell_generative_s,
  poptout_static, poptout_generative, 1 - poptout_generative / NULLIF(poptout_static, 0) AS opt_out_reduction,
  attention_static, attention_generative,
  ecpm_static, ecpm_generative, ecpm_generative / NULLIF(ecpm_static, 0) - 1 AS ecpm_lift,
  themes_scored, blocked_by_guardrail, latency_ms
FROM silver_ad_decisions;
