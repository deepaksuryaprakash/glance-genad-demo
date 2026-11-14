# Lakeflow SDP pipeline evidence (collected 2026-11-14 15:38 UTC)

## Glance GenAd - Lakeflow medallion pipeline (fa3c7aff-097d-4a72-8df2-c97266f5dba0)

| update_id | state | full_refresh | created (UTC) |
|---|---|---|---|
| 3dc8a30e-fa8b-40fb-b51b-f9e3277747f3 | COMPLETED | False | 2026-11-14 15:30 |
| 104d1640-18ab-45cc-b19f-ba3f9b130c4b | COMPLETED | False | 2026-11-14 15:06 |

### Flow completions in the latest updates

```
2026-11-14T15:31:53.192Z Flow 'glance_genad.gold.agg_daily_performance' has COMPLETED.
2026-11-14T15:31:53.158Z Flow 'glance_genad.gold.agg_theme_context_ctr' has COMPLETED.
2026-11-14T15:31:52.440Z Flow 'glance_genad.gold.format_lift_summary' has COMPLETED.
2026-11-14T15:31:46.940Z Flow 'glance_genad.gold.fact_ad_impressions' has COMPLETED.
2026-11-14T15:31:37.352Z Flow 'glance_genad.silver.silver_ad_impressions' has COMPLETED.
2026-11-14T15:31:36.017Z Flow 'glance_genad.gold.live_simulation_log' has COMPLETED.
2026-11-14T15:31:35.038Z Flow 'glance_genad.gold.live_context_latest' has COMPLETED.
2026-11-14T15:31:27.844Z Flow 'glance_genad.silver.ad_decisions_cdc' has COMPLETED.
2026-11-14T15:31:26.266Z Flow 'glance_genad.bronze.bronze_ad_impressions' has COMPLETED.
2026-11-14T15:31:22.695Z Flow 'glance_genad.silver.silver_context_signals' has COMPLETED.
2026-11-14T15:31:18.294Z Flow 'glance_genad.silver.brand_components_cdc' has COMPLETED.
2026-11-14T15:31:18.270Z Flow 'glance_genad.silver.user_profiles_cdc' has COMPLETED.
2026-11-14T15:31:18.221Z Flow 'glance_genad.silver.creative_assets_cdc' has COMPLETED.
2026-11-14T15:07:25.463Z Flow 'glance_genad.gold.format_lift_summary' has COMPLETED.
2026-11-14T15:07:25.438Z Flow 'glance_genad.gold.agg_daily_performance' has COMPLETED.
2026-11-14T15:07:25.389Z Flow 'glance_genad.gold.agg_theme_context_ctr' has COMPLETED.
2026-11-14T15:07:21.576Z Flow 'glance_genad.gold.fact_ad_impressions' has COMPLETED.
2026-11-14T15:07:14.006Z Flow 'glance_genad.silver.silver_ad_impressions' has COMPLETED.
2026-11-14T15:07:13.195Z Flow 'glance_genad.gold.live_simulation_log' has COMPLETED.
2026-11-14T15:07:11.345Z Flow 'glance_genad.silver.user_profiles_cdc' has COMPLETED.
2026-11-14T15:07:11.309Z Flow 'glance_genad.silver.creative_assets_cdc' has COMPLETED.
2026-11-14T15:07:11.286Z Flow 'glance_genad.silver.brand_components_cdc' has COMPLETED.
2026-11-14T15:07:09.551Z Flow 'glance_genad.silver.ad_decisions_cdc' has COMPLETED.
2026-11-14T15:07:09.039Z Flow 'glance_genad.gold.live_context_latest' has COMPLETED.
2026-11-14T15:07:06.422Z Flow 'glance_genad.bronze.bronze_ad_impressions' has COMPLETED.
2026-11-14T15:07:02.587Z Flow 'glance_genad.silver.silver_context_signals' has COMPLETED.
```

### Data-quality expectation results (from event_log() SQL)

| timestamp | flow | dataset | expectation | passed_records | failed_records |
|---|---|---|---|---|---|
| 2026-11-14T15:31:37.337Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | generative_has_theme | 2000 | 0 |
| 2026-11-14T15:31:37.337Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | valid_brand | 2000 | 0 |
| 2026-11-14T15:31:37.337Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | valid_format | 2000 | 0 |
| 2026-11-14T15:31:37.337Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | non_negative_dwell | 2000 | 0 |
| 2026-11-14T15:31:37.337Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | valid_impression_id | 2000 | 0 |
| 2026-11-14T15:31:22.613Z | glance_genad.silver.silver_context_signals | glance_genad.silver.silver_context_signals | valid_signal_type | 42 | 0 |
| 2026-11-14T15:07:13.957Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | valid_format | 600000 | 0 |
| 2026-11-14T15:07:13.957Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | valid_brand | 600000 | 0 |
| 2026-11-14T15:07:13.957Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | generative_has_theme | 600000 | 0 |
| 2026-11-14T15:07:13.957Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | non_negative_dwell | 600000 | 0 |
| 2026-11-14T15:07:13.957Z | glance_genad.silver.silver_ad_impressions | glance_genad.silver.silver_ad_impressions | valid_impression_id | 600000 | 0 |
| 2026-11-14T15:07:02.395Z | glance_genad.silver.silver_context_signals | glance_genad.silver.silver_context_signals | valid_signal_type | 12 | 0 |

