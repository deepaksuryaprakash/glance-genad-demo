-- Gold: analytics-ready impression fact (no PII), source for the metric view + Genie
CREATE OR REFRESH MATERIALIZED VIEW glance_genad.gold.fact_ad_impressions
COMMENT 'One row per ad impression with context, creative decision and outcomes. No PII. Row filter by brand.'
CLUSTER BY (event_date, brand)
TBLPROPERTIES ('quality' = 'gold')
WITH ROW FILTER glance_genad.governance.brand_row_filter ON (brand)
AS SELECT
  i.impression_id, i.event_ts, i.event_date, i.hour_of_day, i.is_weekend,
  i.user_id, i.city, i.segment, i.phone_skin, u.device_os, u.daily_unlocks,
  CASE WHEN u.daily_unlocks >= 120 THEN 'heavy (120+)' WHEN u.daily_unlocks >= 90 THEN 'medium (90-119)' ELSE 'light (<90)' END AS unlock_band,
  i.brand, i.ad_format,
  CASE WHEN i.ad_format = 'glance_generative' THEN 'Generative (variant)' ELSE 'Traditional (control)' END AS experience_group,
  i.placement, i.weather, i.temp_c, i.time_slot, i.user_state, i.live_event,
  i.layout_theme, i.copy_angle, i.component_id, i.campaign_id,
  i.clicked, i.dwell_ms, ROUND(i.dwell_ms / 1000.0, 3) AS dwell_s, i.engaged,
  i.opted_out,
  CASE WHEN i.opt_out_type = 'lockscreen_optout' THEN 1 ELSE 0 END AS lockscreen_optout,
  CASE WHEN i.opt_out_type = 'app_uninstall' THEN 1 ELSE 0 END AS app_uninstall,
  i.cpc_usd, i.revenue_usd,
  -- advertiser spend == platform revenue; cost per engagement is computed in the metric view
  i.revenue_usd AS advertiser_spend_usd
FROM silver_ad_impressions i
LEFT JOIN silver_user_profiles u ON i.user_id = u.user_id;
