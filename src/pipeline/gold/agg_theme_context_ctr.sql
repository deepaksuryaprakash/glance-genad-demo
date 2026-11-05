-- Gold: empirical evidence per (layout theme x context) - the historical reward table behind the bandit
CREATE OR REFRESH MATERIALIZED VIEW glance_genad.gold.agg_theme_context_ctr
COMMENT 'Historical CTR / dwell / opt-out per generative layout theme and context cell, with Bayesian-smoothed CTR (Beta prior from the theme-level mean).'
TBLPROPERTIES ('quality' = 'gold')
AS WITH cell AS (
  SELECT brand, layout_theme, weather, time_slot, user_state,
         COUNT(*) AS impressions, SUM(clicked) AS clicks, AVG(dwell_ms) / 1000.0 AS avg_dwell_s,
         AVG(opted_out) AS opt_out_rate
  FROM glance_genad.gold.fact_ad_impressions
  WHERE ad_format = 'glance_generative'
  GROUP BY ALL
), prior AS (
  SELECT brand, layout_theme, SUM(clicks) / SUM(impressions) AS prior_ctr
  FROM cell GROUP BY ALL
)
SELECT c.*, p.prior_ctr,
       (c.clicks + 200 * p.prior_ctr) / (c.impressions + 200) AS smoothed_ctr
FROM cell c JOIN prior p USING (brand, layout_theme);
