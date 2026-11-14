# SQL query results (executed 2026-11-14 15:38 UTC on SQL warehouse 2e3fc3596c58e22d)

## Row counts across the medallion (Lakebase CDC bronze -> silver -> gold)

```sql
SELECT 'bronze.bronze_ad_impressions' t, count(*) n FROM glance_genad.bronze.bronze_ad_impressions UNION ALL SELECT 'bronze.lb_user_profiles_history (Lakehouse Sync)', count(*) FROM glance_genad.bronze.lb_user_profiles_history UNION ALL SELECT 'bronze.lb_context_signals_history (Lakehouse Sync)', count(*) FROM glance_genad.bronze.lb_context_signals_history UNION ALL SELECT 'bronze.lb_ad_decisions_history (Lakehouse Sync)', count(*) FROM glance_genad.bronze.lb_ad_decisions_history UNION ALL SELECT 'silver.silver_ad_impressions', count(*) FROM glance_genad.silver.silver_ad_impressions UNION ALL SELECT 'silver.silver_user_profiles', count(*) FROM glance_genad.silver.silver_user_profiles UNION ALL SELECT 'silver.silver_brand_asset_components', count(*) FROM glance_genad.silver.silver_brand_asset_components UNION ALL SELECT 'silver.silver_context_signals', count(*) FROM glance_genad.silver.silver_context_signals UNION ALL SELECT 'gold.fact_ad_impressions', count(*) FROM glance_genad.gold.fact_ad_impressions UNION ALL SELECT 'gold.agg_daily_performance', count(*) FROM glance_genad.gold.agg_daily_performance UNION ALL SELECT 'gold.live_simulation_log', count(*) FROM glance_genad.gold.live_simulation_log UNION ALL SELECT 'gold.brand_asset_registry (VS source)', count(*) FROM glance_genad.gold.brand_asset_registry UNION ALL SELECT 'ml.model_coefficients', count(*) FROM glance_genad.ml.model_coefficients
```

| t | n |
|---|---|
| silver.silver_ad_impressions | 602000 |
| silver.silver_user_profiles | 20006 |
| silver.silver_brand_asset_components | 16 |
| gold.fact_ad_impressions | 602000 |
| gold.agg_daily_performance | 360101 |
| bronze.bronze_ad_impressions | 602000 |
| bronze.lb_user_profiles_history (Lakehouse Sync) | 20006 |
| bronze.lb_context_signals_history (Lakehouse Sync) | 54 |
| bronze.lb_ad_decisions_history (Lakehouse Sync) | 6 |
| silver.silver_context_signals | 54 |
| gold.live_simulation_log | 2 |
| gold.brand_asset_registry (VS source) | 16 |
| ml.model_coefficients | 2020 |

## Historical control vs variant scorecard (gold.format_lift_summary)

```sql
SELECT brand, ad_format, impressions, round(ctr*100,3) ctr_pct, round(avg_dwell_s,2) avg_dwell_s, round(engaged_rate*100,1) engaged_pct, round(ecpm_usd,2) ecpm_usd, round(cost_per_engagement_usd,3) cpe_usd, round(opt_out_rate*100,3) opt_out_pct, round(ctr_lift_vs_static*100,1) ctr_lift_pct, round(ecpm_lift_vs_static*100,1) ecpm_lift_pct, round(opt_out_reduction_vs_static*100,1) opt_out_reduction_pct FROM glance_genad.gold.format_lift_summary ORDER BY brand, ad_format
```

| brand | ad_format | impressions | ctr_pct | avg_dwell_s | engaged_pct | ecpm_usd | cpe_usd | opt_out_pct | ctr_lift_pct | ecpm_lift_pct | opt_out_reduction_pct |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all | glance_generative | 270311 | 1.329 | 2.62 | 44.5 | 6.66 | 0.015 | 0.882 | 21.7 | 34.7 | 18.8 |
| all | standard_video | 120980 | 1.263 | 1.61 | 11.4 | 5.74 | 0.046 | 1.302 | 15.6 | 16.2 | -19.8 |
| all | static_banner | 210709 | 1.093 | 0.95 | 0.9 | 4.94 | 0.258 | 1.086 | 0.0 | 0.0 | 0.0 |
| nike | glance_generative | 134341 | 1.216 | 2.64 | 44.9 | 7.2 | 0.016 | 0.88 | 27.7 | 38.1 | 22.0 |
| nike | standard_video | 60262 | 1.115 | 1.61 | 11.4 | 6.11 | 0.05 | 1.264 | 17.2 | 17.2 | -12.1 |
| nike | static_banner | 105282 | 0.952 | 0.94 | 0.9 | 5.21 | 0.292 | 1.128 | 0.0 | 0.0 | 0.0 |
| starbucks | glance_generative | 135970 | 1.441 | 2.61 | 44.1 | 6.12 | 0.014 | 0.885 | 16.9 | 31.0 | 15.3 |
| starbucks | standard_video | 60718 | 1.41 | 1.61 | 11.5 | 5.38 | 0.043 | 1.339 | 14.3 | 15.1 | -28.2 |
| starbucks | static_banner | 105427 | 1.233 | 0.95 | 0.9 | 4.67 | 0.228 | 1.044 | 0.0 | 0.0 | 0.0 |

## Off-policy evaluation of the generative engine (gold.model_policy_evaluation, written by the training job)

```sql
SELECT policy, round(pred_ctr*100,2) pred_ctr_pct, round(pred_dwell_s,2) pred_dwell_s, round(pred_opt_out*100,3) pred_opt_out_pct, round(pred_ecpm_usd,2) pred_ecpm_usd, round(ctr_lift_vs_static*100,1) ctr_lift_pct, round(ecpm_lift_vs_static*100,1) ecpm_lift_pct, round(opt_out_reduction_vs_static*100,1) opt_out_reduction_pct, model_version, evaluated_at FROM glance_genad.gold.model_policy_evaluation
```

| policy | pred_ctr_pct | pred_dwell_s | pred_opt_out_pct | pred_ecpm_usd | ctr_lift_pct | ecpm_lift_pct | opt_out_reduction_pct | model_version | evaluated_at |
|---|---|---|---|---|---|---|---|---|---|
| static_banner (control) | 1.08 | 0.94 | 1.116 | 4.9 | 0.0 | 0.0 | 0.0 | 1 | 2026-11-14T15:09:04.216Z |
| generative - logged policy (rule + exploration) | 1.33 | 2.65 | 0.917 | 6.68 | 23.4 | 36.4 | 17.8 | 1 | 2026-11-14T15:09:04.216Z |
| generative - optimized (argmax of 50 layout x angle combos) | 1.84 | 3.13 | 0.82 | 8.75 | 70.5 | 78.6 | 26.5 | 1 | 2026-11-14T15:09:04.216Z |

## Metric view query: weekly KPIs, control vs variant (gold.mv_ad_effectiveness)

```sql
SELECT event_week, experience_group, MEASURE(impressions) impressions, round(MEASURE(ctr)*100,3) ctr_pct, round(MEASURE(avg_interaction_duration_s),2) dwell_s, round(MEASURE(ecpm_usd),2) ecpm_usd, round(MEASURE(opt_out_rate)*100,3) opt_out_pct FROM glance_genad.gold.mv_ad_effectiveness GROUP BY ALL ORDER BY event_week, experience_group
```

| event_week | experience_group | impressions | ctr_pct | dwell_s | ecpm_usd | opt_out_pct |
|---|---|---|---|---|---|---|
| 2026-09-14T00:00:00.000Z | Generative (variant) | 27096 | 1.461 | 2.59 | 7.1 | 0.882 |
| 2026-09-14T00:00:00.000Z | Traditional (control) | 32904 | 1.258 | 1.19 | 5.61 | 1.216 |
| 2026-09-21T00:00:00.000Z | Generative (variant) | 31570 | 1.277 | 2.64 | 6.43 | 0.871 |
| 2026-09-21T00:00:00.000Z | Traditional (control) | 38430 | 1.093 | 1.19 | 5.02 | 1.109 |
| 2026-09-28T00:00:00.000Z | Generative (variant) | 31302 | 1.319 | 2.64 | 6.66 | 0.901 |
| 2026-09-28T00:00:00.000Z | Traditional (control) | 38698 | 1.145 | 1.19 | 5.21 | 1.235 |
| 2026-10-05T00:00:00.000Z | Generative (variant) | 31335 | 1.391 | 2.61 | 6.88 | 0.894 |
| 2026-10-05T00:00:00.000Z | Traditional (control) | 38665 | 1.138 | 1.19 | 5.18 | 1.197 |
| 2026-10-12T00:00:00.000Z | Generative (variant) | 31560 | 1.258 | 2.62 | 6.45 | 0.884 |
| 2026-10-12T00:00:00.000Z | Traditional (control) | 38440 | 1.103 | 1.19 | 5.05 | 1.207 |
| 2026-10-19T00:00:00.000Z | Generative (variant) | 31454 | 1.361 | 2.67 | 6.8 | 0.868 |
| 2026-10-19T00:00:00.000Z | Traditional (control) | 38546 | 1.235 | 1.19 | 5.48 | 1.131 |
| 2026-10-26T00:00:00.000Z | Generative (variant) | 31449 | 1.342 | 2.65 | 6.66 | 0.89 |
| 2026-10-26T00:00:00.000Z | Traditional (control) | 38551 | 1.113 | 1.19 | 5.07 | 1.188 |
| 2026-11-02T00:00:00.000Z | Generative (variant) | 31251 | 1.238 | 2.58 | 6.28 | 0.88 |
| 2026-11-02T00:00:00.000Z | Traditional (control) | 38749 | 1.13 | 1.18 | 5.14 | 1.058 |
| 2026-11-09T00:00:00.000Z | Generative (variant) | 23294 | 1.335 | 2.61 | 6.74 | 0.867 |
| 2026-11-09T00:00:00.000Z | Traditional (control) | 28706 | 1.205 | 1.18 | 5.46 | 1.146 |

## Metric view query: best generative theme per weather (historical evidence the model learns from)

```sql
SELECT weather, layout_theme, MEASURE(impressions) impressions, round(MEASURE(ctr)*100,3) ctr_pct, round(MEASURE(avg_interaction_duration_s),2) dwell_s FROM glance_genad.gold.mv_ad_effectiveness WHERE ad_format = 'glance_generative' GROUP BY ALL ORDER BY weather, ctr_pct DESC
```

| weather | layout_theme | impressions | ctr_pct | dwell_s |
|---|---|---|---|---|
| cloudy | chill_lounge | 2461 | 1.382 | 2.59 |
| cloudy | urban_commute | 2437 | 1.313 | 2.41 |
| cloudy | energetic_sport | 1238 | 1.292 | 2.67 |
| cloudy | minimal_tech | 29278 | 1.165 | 2.48 |
| cloudy | night_calm | 2484 | 1.006 | 2.41 |
| cloudy | sunrise_fresh | 2494 | 0.962 | 2.36 |
| cloudy | cozy_warm | 2459 | 0.935 | 2.57 |
| cloudy | live_match_hype | 2435 | 0.862 | 2.07 |
| cloudy | bold_neon | 1185 | 0.844 | 2.47 |
| cloudy | rain_atmos | 2513 | 0.836 | 2.47 |
| cold | cozy_warm | 15835 | 2.052 | 3.14 |
| cold | bold_neon | 657 | 1.674 | 2.41 |
| cold | minimal_tech | 1357 | 1.548 | 2.57 |
| cold | sunrise_fresh | 1331 | 1.503 | 2.49 |
| cold | urban_commute | 1337 | 1.496 | 2.53 |
| cold | rain_atmos | 1315 | 1.445 | 2.37 |
| cold | live_match_hype | 1299 | 1.386 | 2.15 |
| cold | night_calm | 1314 | 1.218 | 2.45 |
| cold | energetic_sport | 675 | 1.185 | 2.68 |
| cold | chill_lounge | 1311 | 0.992 | 2.49 |
| heavy_rain | cozy_warm | 3346 | 1.823 | 3.02 |
| heavy_rain | rain_atmos | 40724 | 1.603 | 3.12 |
| heavy_rain | chill_lounge | 3321 | 1.506 | 2.61 |
| heavy_rain | urban_commute | 3303 | 1.241 | 2.46 |
| heavy_rain | live_match_hype | 3388 | 1.24 | 2.25 |
| heavy_rain | night_calm | 3395 | 1.208 | 2.45 |
| heavy_rain | energetic_sport | 1661 | 1.204 | 2.7 |
| heavy_rain | minimal_tech | 3433 | 1.136 | 2.55 |
| heavy_rain | bold_neon | 1739 | 1.093 | 2.4 |
| heavy_rain | sunrise_fresh | 3290 | 0.942 | 2.18 |
| hot_humid | bold_neon | 1120 | 1.964 | 2.43 |
| hot_humid | night_calm | 2199 | 1.273 | 2.36 |
| hot_humid | energetic_sport | 1106 | 1.266 | 2.7 |
| hot_humid | urban_commute | 2269 | 1.146 | 2.44 |
| hot_humid | chill_lounge | 26966 | 1.068 | 2.47 |
| hot_humid | minimal_tech | 2354 | 0.935 | 2.48 |
| hot_humid | live_match_hype | 2205 | 0.862 | 2.11 |
| hot_humid | rain_atmos | 2215 | 0.813 | 2.05 |
| hot_humid | sunrise_fresh | 2143 | 0.653 | 2.37 |
| hot_humid | cozy_warm | 2268 | 0.573 | 2.13 |
| sunny | energetic_sport | 2000 | 1.8 | 2.87 |
| sunny | sunrise_fresh | 49534 | 1.474 | 2.7 |
| sunny | minimal_tech | 4252 | 1.458 | 2.48 |
| sunny | chill_lounge | 4164 | 1.273 | 2.51 |
| sunny | bold_neon | 2109 | 1.233 | 2.42 |
| sunny | urban_commute | 3950 | 1.19 | 2.4 |
| sunny | cozy_warm | 4197 | 1.168 | 2.58 |
| sunny | live_match_hype | 4048 | 1.062 | 2.08 |
| sunny | night_calm | 4104 | 0.926 | 2.23 |
| sunny | rain_atmos | 4093 | 0.733 | 1.81 |

## Live app decisions flowing back through Lakebase -> Lakehouse Sync -> pipeline (gold.mv_live_simulations)

```sql
SELECT brand, weather, user_state, chosen_theme, MEASURE(decisions) decisions, round(MEASURE(predicted_ctr_lift)*100,0) ctr_lift_pct, round(MEASURE(predicted_ecpm_lift)*100,0) ecpm_lift_pct, round(MEASURE(avg_predicted_dwell_s),2) dwell_s, round(MEASURE(avg_attention_score),1) attention FROM glance_genad.gold.mv_live_simulations GROUP BY ALL ORDER BY decisions DESC LIMIT 15
```

| brand | weather | user_state | chosen_theme | decisions | ctr_lift_pct | ecpm_lift_pct | dwell_s | attention |
|---|---|---|---|---|---|---|---|---|
| starbucks | heavy_rain | just_missed_train | cozy_warm | 2 | 103.0 | 106.0 | 3.75 | 84.4 |

## Top learned CTR weights (ml.model_coefficients) - model recovers context x creative interactions

```sql
SELECT model_version, feature, round(weight,3) weight FROM glance_genad.ml.model_coefficients WHERE model_name = 'ctr' AND feature NOT LIKE '\_\_%' ORDER BY weight DESC LIMIT 15
```

| model_version | feature | weight |
|---|---|---|
| 1 | brand=nike|user_state=working_out | 0.343 |
| 1 | theme=chill_lounge|user_state=relaxing_at_home | 0.212 |
| 1 | theme=cozy_warm|weather=cold | 0.202 |
| 1 | theme=sunrise_fresh|weather=sunny | 0.2 |
| 1 | brand=nike|segment=fitness_enthusiast | 0.199 |
| 1 | angle=performance|user_state=working_out | 0.187 |
| 1 | theme=rain_atmos|weather=heavy_rain | 0.177 |
| 1 | theme=sunrise_fresh|time_slot=morning_rush | 0.163 |
| 1 | angle=comfort|user_state=relaxing_at_home | 0.148 |
| 1 | brand=starbucks|user_state=just_missed_train | 0.145 |
| 1 | theme=minimal_tech|user_state=at_office | 0.142 |
| 1 | theme=sunrise_fresh|user_state=working_out | 0.139 |
| 1 | angle=social_fomo|live_event=cricket_live | 0.129 |
| 1 | angle=comfort|weather=heavy_rain | 0.127 |
| 1 | theme=urban_commute|time_slot=morning_rush | 0.127 |

## Saturation calibration parameters exported with the model

```sql
SELECT model_name, feature, weight FROM glance_genad.ml.model_coefficients WHERE feature LIKE '\_\_%' ORDER BY model_name, feature
```

| model_name | feature | weight |
|---|---|---|
| ctr | __intercept__ | -1.031933006013565 |
| ctr | __sat_A__ | 1.7 |
| ctr | __sat_scale__ | 0.7 |
| dwell | __intercept__ | 0.3067604082961464 |
| dwell | __sat_A__ | 0.6 |
| dwell | __sat_scale__ | 1.15 |
| dwell | __sigma__ | 0.45078969556816867 |
| opt_out | __intercept__ | -1.0593417183858653 |
| opt_out | __sat_A__ | 0.4 |
| opt_out | __sat_scale__ | 1.3 |

## UC column masks in effect (queried as a user NOT in glance_pii_readers)

```sql
SELECT user_id, full_name, email, phone, device_ad_id, segment, city FROM glance_genad.silver.silver_user_profiles WHERE is_demo_persona ORDER BY user_id
```

| user_id | full_name | email | phone | device_ad_id | segment | city |
|---|---|---|---|---|---|---|
| U90001 | A***** M. | aa****@example.com | +**-******0001 | hash:ee4c3f5ab0b7f868 | fitness_enthusiast | Bengaluru |
| U90002 | P***** N. | pr****@example.com | +**-******0002 | hash:8646d5095bbd5a82 | daily_commuter | Mumbai |
| U90003 | R***** G. | ro****@example.com | +**-******0003 | hash:51324faeb90c0db9 | tech_professional | Bengaluru |
| U90004 | S***** I. | sn****@example.com | +**-******0004 | hash:1e38631dacfe2349 | casual_gamer | Hyderabad |
| U90005 | K***** S. | ka****@example.com | +**-******0005 | hash:390889cf32c95d63 | night_owl | Delhi |
| U90006 | D***** L. | de****@example.com | +**-******0006 | hash:13a91efaba62b082 | daily_commuter | Jakarta |

## UC row filter + masks attached to tables (information_schema)

```sql
SELECT table_schema, table_name, 'row_filter' kind, filter_name AS fn, target_columns AS cols FROM glance_genad.information_schema.row_filters UNION ALL SELECT table_schema, table_name, 'column_mask', mask_name, column_name FROM glance_genad.information_schema.column_masks ORDER BY 1, 2
```

| table_schema | table_name | kind | fn | cols |
|---|---|---|---|---|
| gold | agg_daily_performance | row_filter | glance_genad.governance.brand_row_filter | brand |
| gold | fact_ad_impressions | row_filter | glance_genad.governance.brand_row_filter | brand |
| silver | silver_ad_impressions | row_filter | glance_genad.governance.brand_row_filter | brand |
| silver | silver_user_profiles | column_mask | glance_genad.governance.mask_phone | phone |
| silver | silver_user_profiles | column_mask | glance_genad.governance.mask_name | full_name |
| silver | silver_user_profiles | column_mask | glance_genad.governance.mask_ad_id | device_ad_id |
| silver | silver_user_profiles | column_mask | glance_genad.governance.mask_email | email |

## Brand entitlements driving the row filter

```sql
SELECT principal, brand, granted_by FROM glance_genad.governance.brand_entitlements
```

| principal | brand | granted_by |
|---|---|---|
| 75e7265a-87ce-4285-bea1-3aa1a5036d48 | * | deepak.suryaprakash@databricks.com |
| deepak.suryaprakash@databricks.com | * | deepak.suryaprakash@databricks.com |

## Live context in gold (from the Lakebase stream)

```sql
SELECT * FROM glance_genad.gold.live_context_latest ORDER BY city, signal_type
```

| city | signal_type | signal_key | signal_value | temp_c | intensity | observed_at |
|---|---|---|---|---|---|---|
| Bengaluru | live_event | cricket_live | IND 220/4 (19.2 ov) vs AUS |  | 0.9 | 2026-11-14T15:29:55.603Z |
| Bengaluru | transit | train_delay | Purple line metro: 9 min headway |  | 0.4 | 2026-11-14T15:03:33.264Z |
| Bengaluru | weather | sunny | Sunny, 29°C | 31.0 | 0.54 | 2026-11-14T15:29:50.595Z |
| Delhi | live_event | city_marathon | Delhi Half Marathon this Sunday — 42k registered |  | 0.55 | 2026-11-14T15:03:33.264Z |
| Delhi | weather | cold | Cold, 7°C | 11.0 | 0.39 | 2026-11-14T15:29:25.562Z |
| Hyderabad | live_event | esports_final | BGMI Masters Grand Final — Map 3 live |  | 0.8 | 2026-11-14T15:03:33.264Z |
| Hyderabad | weather | cold | Cold, 5°C | 11.0 | 0.09 | 2026-11-14T15:29:55.603Z |
| Jakarta | weather | sunny | Sunny, 34°C | 31.0 | 0.02 | 2026-11-14T15:29:40.581Z |
| Mumbai | live_event | football_live | Mumbai City 1-1 Bengaluru FC (79') |  | 0.75 | 2026-11-14T15:29:55.603Z |
| Mumbai | transit | train_delay | Western line locals running 8 min late |  | 0.32 | 2026-11-14T15:29:55.603Z |
| Mumbai | weather | hot_humid | Hot Humid, 33°C | 33.0 | 0.14 | 2026-11-14T15:29:35.575Z |
| Pune | weather | cloudy | Overcast, 24°C | 24.0 | 0.3 | 2026-11-14T15:03:33.264Z |

