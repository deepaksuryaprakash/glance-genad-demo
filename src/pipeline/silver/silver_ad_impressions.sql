-- Silver: validated, conformed impressions. Advertiser row-level security via UC row filter.
CREATE OR REFRESH STREAMING TABLE silver_ad_impressions (
  CONSTRAINT valid_impression_id EXPECT (impression_id IS NOT NULL) ON VIOLATION DROP ROW,
  CONSTRAINT valid_format EXPECT (ad_format IN ('static_banner', 'standard_video', 'glance_generative')) ON VIOLATION DROP ROW,
  CONSTRAINT non_negative_dwell EXPECT (dwell_ms >= 0 AND dwell_ms < 600000) ON VIOLATION DROP ROW,
  CONSTRAINT valid_brand EXPECT (brand IN ('nike', 'starbucks')) ON VIOLATION DROP ROW,
  CONSTRAINT generative_has_theme EXPECT (ad_format <> 'glance_generative' OR layout_theme <> 'none')
)
COMMENT 'Cleaned ad impressions with engagement outcomes. Row filter: advertisers only see their own brand.'
CLUSTER BY (event_date, brand)
TBLPROPERTIES ('quality' = 'silver')
WITH ROW FILTER glance_genad.governance.brand_row_filter ON (brand)
AS SELECT
  impression_id,
  CAST(event_ts AS TIMESTAMP)              AS event_ts,
  CAST(event_ts AS DATE)                   AS event_date,
  hour(event_ts)                           AS hour_of_day,
  dayofweek(event_ts) IN (1, 7)            AS is_weekend,
  user_id, city, segment, phone_skin, brand, ad_format, placement,
  weather, CAST(round(temp_c, 1) AS DOUBLE) AS temp_c, time_slot, user_state, live_event,
  layout_theme, copy_angle, component_id, campaign_id, device_os,
  CAST(clicked AS INT)                     AS clicked,
  CAST(dwell_ms AS INT)                    AS dwell_ms,
  CAST(engaged AS INT)                     AS engaged,
  CAST(opted_out AS INT)                   AS opted_out,
  opt_out_type,
  CAST(cpc_usd AS DOUBLE)                  AS cpc_usd,
  CAST(revenue_usd AS DOUBLE)              AS revenue_usd,
  ad_server, _source_file, _ingested_at
FROM STREAM(glance_genad.bronze.bronze_ad_impressions);
