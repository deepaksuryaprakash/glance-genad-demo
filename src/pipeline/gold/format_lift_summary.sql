-- Gold: control (static banner) vs variant (generative) scorecard per brand - the headline business KPIs
CREATE OR REFRESH MATERIALIZED VIEW glance_genad.gold.format_lift_summary
COMMENT 'Static banner / standard video vs Glance generative: CTR, avg interaction duration, eCPM, cost per engagement, opt-out rate and lift %.'
TBLPROPERTIES ('quality' = 'gold')
AS WITH f AS (
  SELECT brand, ad_format,
         COUNT(*) AS impressions, AVG(clicked) AS ctr, AVG(dwell_ms) / 1000.0 AS avg_dwell_s,
         AVG(engaged) AS engaged_rate, 1000 * AVG(revenue_usd) AS ecpm_usd,
         SUM(revenue_usd) / NULLIF(SUM(GREATEST(clicked, engaged)), 0) AS cost_per_engagement_usd,
         AVG(opted_out) AS opt_out_rate
  FROM glance_genad.gold.fact_ad_impressions
  GROUP BY GROUPING SETS ((brand, ad_format), (ad_format))
)
SELECT COALESCE(f.brand, 'all') AS brand, f.ad_format, f.impressions, f.ctr, f.avg_dwell_s, f.engaged_rate,
       f.ecpm_usd, f.cost_per_engagement_usd, f.opt_out_rate,
       f.ctr / s.ctr - 1                 AS ctr_lift_vs_static,
       f.ecpm_usd / s.ecpm_usd - 1       AS ecpm_lift_vs_static,
       1 - f.opt_out_rate / s.opt_out_rate AS opt_out_reduction_vs_static,
       f.cost_per_engagement_usd / s.cost_per_engagement_usd - 1 AS cpe_change_vs_static
FROM f JOIN f s ON s.ad_format = 'static_banner' AND COALESCE(s.brand, 'all') = COALESCE(f.brand, 'all');
