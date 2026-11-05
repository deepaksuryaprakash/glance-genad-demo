-- Gold: daily performance mart sliced by every business dimension analysts filter on
CREATE OR REFRESH MATERIALIZED VIEW glance_genad.gold.agg_daily_performance
COMMENT 'Daily impressions, clicks, dwell, engagement, opt-outs and revenue by format, brand, segment and context.'
TBLPROPERTIES ('quality' = 'gold')
WITH ROW FILTER glance_genad.governance.brand_row_filter ON (brand)
AS SELECT
  event_date, brand, ad_format, experience_group, segment, city, weather, time_slot, user_state, live_event,
  layout_theme, copy_angle,
  COUNT(*)                     AS impressions,
  SUM(clicked)                 AS clicks,
  SUM(dwell_ms)                AS total_dwell_ms,
  SUM(engaged)                 AS engaged_views,
  SUM(opted_out)               AS opt_outs,
  SUM(lockscreen_optout)       AS lockscreen_optouts,
  SUM(app_uninstall)           AS app_uninstalls,
  SUM(revenue_usd)             AS revenue_usd
FROM glance_genad.gold.fact_ad_impressions
GROUP BY ALL;
