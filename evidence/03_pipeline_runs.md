# Lakeflow SDP pipeline evidence (collected 2026-11-09 10:16 UTC)

## Glance GenAd - Lakeflow medallion pipeline (46247a0b-cc48-40e3-b73b-b0e1f1fbf93a)

| update_id | state | full_refresh | created (UTC) |
|---|---|---|---|
| 444859cb-e583-493c-86be-c5b249308485 | COMPLETED | False | 2026-11-05 15:42 |
| 412862be-2830-45fb-8552-1450d5058a98 | COMPLETED | True | 2026-11-05 15:37 |
| d15b4c9e-18c7-458d-bd3a-8dc877c177a9 | COMPLETED | True | 2026-11-05 15:21 |
| a5e362c0-b1ae-4ef0-bc86-9a5a901b8c5b | COMPLETED | True | 2026-11-05 13:41 |
| 75204693-595b-48bc-968e-47a87f1c8ba4 | COMPLETED | True | 2026-11-05 13:24 |
| 9669df9f-55a9-4057-a6ae-dd9d76fcd092 | COMPLETED | False | 2026-11-05 13:19 |

### Flow completions in the latest updates

```
2026-11-05T15:43:55.621Z Flow 'glance_genad.gold.agg_daily_performance' has COMPLETED.
2026-11-05T15:43:54.928Z Flow 'glance_genad.gold.agg_theme_context_ctr' has COMPLETED.
2026-11-05T15:43:54.902Z Flow 'glance_genad.gold.format_lift_summary' has COMPLETED.
2026-11-05T15:43:48.262Z Flow 'glance_genad.gold.fact_ad_impressions' has COMPLETED.
2026-11-05T15:43:36.487Z Flow 'glance_genad.silver.silver_ad_impressions' has COMPLETED.
2026-11-05T15:43:32.287Z Flow 'glance_genad.bronze.bronze_ad_impressions' has COMPLETED.
2026-11-05T15:43:29.913Z Flow 'glance_genad.gold.live_simulation_log' has COMPLETED.
2026-11-05T15:43:29.874Z Flow 'glance_genad.gold.live_context_latest' has COMPLETED.
2026-11-05T15:43:23.461Z Flow 'glance_genad.silver.ad_decisions_cdc' has COMPLETED.
2026-11-05T15:43:22.455Z Flow 'glance_genad.silver.silver_context_signals' has COMPLETED.
2026-11-05T15:43:22.446Z Flow 'glance_genad.silver.user_profiles_cdc' has COMPLETED.
2026-11-05T15:43:22.427Z Flow 'glance_genad.silver.brand_components_cdc' has COMPLETED.
2026-11-05T15:43:22.409Z Flow 'glance_genad.silver.creative_assets_cdc' has COMPLETED.
2026-11-05T15:39:01.404Z Flow 'glance_genad.gold.agg_daily_performance' has COMPLETED.
2026-11-05T15:39:00.581Z Flow 'glance_genad.gold.format_lift_summary' has COMPLETED.
2026-11-05T15:39:00.424Z Flow 'glance_genad.gold.agg_theme_context_ctr' has COMPLETED.
2026-11-05T15:38:56.086Z Flow 'glance_genad.gold.fact_ad_impressions' has COMPLETED.
2026-11-05T15:38:48.515Z Flow 'glance_genad.gold.live_simulation_log' has COMPLETED.
2026-11-05T15:38:48.187Z Flow 'glance_genad.silver.silver_ad_impressions' has COMPLETED.
2026-11-05T15:38:44.867Z Flow 'glance_genad.silver.user_profiles_cdc' has COMPLETED.
2026-11-05T15:38:44.768Z Flow 'glance_genad.silver.ad_decisions_cdc' has COMPLETED.
2026-11-05T15:38:44.735Z Flow 'glance_genad.silver.creative_assets_cdc' has COMPLETED.
2026-11-05T15:38:44.698Z Flow 'glance_genad.silver.brand_components_cdc' has COMPLETED.
2026-11-05T15:38:42.334Z Flow 'glance_genad.gold.live_context_latest' has COMPLETED.
2026-11-05T15:38:41.208Z Flow 'glance_genad.bronze.bronze_ad_impressions' has COMPLETED.
2026-11-05T15:38:34.596Z Flow 'glance_genad.silver.silver_context_signals' has COMPLETED.
2026-11-05T15:23:15.655Z Flow 'glance_genad.gold.agg_daily_performance' has COMPLETED.
2026-11-05T15:23:14.902Z Flow 'glance_genad.gold.format_lift_summary' has COMPLETED.
2026-11-05T15:23:14.852Z Flow 'glance_genad.gold.agg_theme_context_ctr' has COMPLETED.
2026-11-05T15:23:10.336Z Flow 'glance_genad.gold.fact_ad_impressions' has COMPLETED.
2026-11-05T15:23:01.989Z Flow 'glance_genad.gold.live_simulation_log' has COMPLETED.
2026-11-05T15:23:01.987Z Flow 'glance_genad.silver.silver_ad_impressions' has COMPLETED.
2026-11-05T15:22:58.294Z Flow 'glance_genad.silver.user_profiles_cdc' has COMPLETED.
2026-11-05T15:22:58.280Z Flow 'glance_genad.silver.creative_assets_cdc' has COMPLETED.
2026-11-05T15:22:58.238Z Flow 'glance_genad.silver.ad_decisions_cdc' has COMPLETED.
2026-11-05T15:22:58.201Z Flow 'glance_genad.silver.brand_components_cdc' has COMPLETED.
2026-11-05T15:22:55.663Z Flow 'glance_genad.gold.live_context_latest' has COMPLETED.
2026-11-05T15:22:54.751Z Flow 'glance_genad.bronze.bronze_ad_impressions' has COMPLETED.
2026-11-05T15:22:47.816Z Flow 'glance_genad.silver.silver_context_signals' has COMPLETED.
2026-11-05T13:43:07.626Z Flow 'glance_genad.gold.agg_daily_performance' has COMPLETED.
```

### Data-quality expectation results (from event_log() SQL)

| timestamp | flow | dataset | expectation | passed_records | failed_records |
|---|---|---|---|---|---|
| 2026-11-05T15:43:36.468Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | non_negative_dwell | 2000 | 0 |
| 2026-11-05T15:43:36.468Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | generative_has_theme | 2000 | 0 |
| 2026-11-05T15:43:36.468Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | valid_format | 2000 | 0 |
| 2026-11-05T15:43:36.468Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | valid_brand | 2000 | 0 |
| 2026-11-05T15:43:36.468Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | valid_impression_id | 2000 | 0 |
| 2026-11-05T15:38:48.170Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | valid_impression_id | 600000 | 0 |
| 2026-11-05T15:38:48.170Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | valid_format | 600000 | 0 |
| 2026-11-05T15:38:48.170Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | valid_brand | 600000 | 0 |
| 2026-11-05T15:38:48.170Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | non_negative_dwell | 600000 | 0 |
| 2026-11-05T15:38:48.170Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | generative_has_theme | 600000 | 0 |
| 2026-11-05T15:38:34.483Z | glance_genad.silver.silver_context_signals | glance_genad.silver.silver_context_signals | valid_signal_type | 52 | 0 |
| 2026-11-05T15:23:01.965Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | generative_has_theme | 600000 | 0 |
| 2026-11-05T15:23:01.965Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | non_negative_dwell | 600000 | 0 |
| 2026-11-05T15:23:01.965Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | valid_brand | 600000 | 0 |
| 2026-11-05T15:23:01.965Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | valid_impression_id | 600000 | 0 |
| 2026-11-05T15:23:01.965Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | valid_format | 600000 | 0 |
| 2026-11-05T15:22:47.726Z | glance_genad.silver.silver_context_signals | glance_genad.silver.silver_context_signals | valid_signal_type | 52 | 0 |
| 2026-11-05T13:42:54.681Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | generative_has_theme | 600000 | 0 |
| 2026-11-05T13:42:54.681Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | non_negative_dwell | 600000 | 0 |
| 2026-11-05T13:42:54.681Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | valid_impression_id | 600000 | 0 |
| 2026-11-05T13:42:54.681Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | valid_brand | 600000 | 0 |
| 2026-11-05T13:42:54.681Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | valid_format | 600000 | 0 |
| 2026-11-05T13:42:41.994Z | glance_genad.silver.silver_context_signals | glance_genad.silver.silver_context_signals | valid_signal_type | 12 | 0 |
| 2026-11-05T13:25:09.721Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | generative_has_theme | 600000 | 0 |
| 2026-11-05T13:25:09.721Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | valid_format | 600000 | 0 |
| 2026-11-05T13:25:09.721Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | valid_impression_id | 600000 | 0 |
| 2026-11-05T13:25:09.721Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | valid_brand | 600000 | 0 |
| 2026-11-05T13:25:09.721Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | non_negative_dwell | 600000 | 0 |
| 2026-11-05T13:24:55.909Z | glance_genad.silver.silver_context_signals | glance_genad.silver.silver_context_signals | valid_signal_type | 12 | 0 |
| 2026-11-05T13:20:44.161Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | valid_brand | 600000 | 0 |

