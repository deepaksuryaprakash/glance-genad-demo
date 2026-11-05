-- Gold: latest live trigger per city and signal type (what the generative engine sees right now)
CREATE OR REFRESH MATERIALIZED VIEW glance_genad.gold.live_context_latest
COMMENT 'Latest weather / live event / transit signal per city from the Lakebase context stream.'
TBLPROPERTIES ('quality' = 'gold')
AS SELECT city, signal_type, signal_key, signal_value, temp_c, intensity, observed_at
FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY city, signal_type ORDER BY observed_at DESC, signal_id DESC) AS rn
  FROM silver_context_signals
) WHERE rn = 1;
