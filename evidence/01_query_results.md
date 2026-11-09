# SQL query results (executed 2026-11-09 10:16 UTC on SQL warehouse e55438f8a8ce03e0)

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
| gold.agg_daily_performance | 360170 |
| bronze.bronze_ad_impressions | 602000 |
| bronze.lb_user_profiles_history (Lakehouse Sync) | 20006 |
| bronze.lb_context_signals_history (Lakehouse Sync) | 52 |
| bronze.lb_ad_decisions_history (Lakehouse Sync) | 42 |
| silver.silver_context_signals | 52 |
| gold.live_simulation_log | 18 |
| gold.brand_asset_registry (VS source) | 16 |
| ml.model_coefficients | 2020 |

## Historical control vs variant scorecard (gold.format_lift_summary)

```sql
SELECT brand, ad_format, impressions, round(ctr*100,3) ctr_pct, round(avg_dwell_s,2) avg_dwell_s, round(engaged_rate*100,1) engaged_pct, round(ecpm_usd,2) ecpm_usd, round(cost_per_engagement_usd,3) cpe_usd, round(opt_out_rate*100,3) opt_out_pct, round(ctr_lift_vs_static*100,1) ctr_lift_pct, round(ecpm_lift_vs_static*100,1) ecpm_lift_pct, round(opt_out_reduction_vs_static*100,1) opt_out_reduction_pct FROM glance_genad.gold.format_lift_summary ORDER BY brand, ad_format
```

| brand | ad_format | impressions | ctr_pct | avg_dwell_s | engaged_pct | ecpm_usd | cpe_usd | opt_out_pct | ctr_lift_pct | ecpm_lift_pct | opt_out_reduction_pct |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all | glance_generative | 270295 | 1.333 | 2.62 | 44.5 | 6.67 | 0.015 | 0.881 | 22.2 | 35.3 | 18.9 |
| all | standard_video | 120981 | 1.257 | 1.61 | 11.4 | 5.72 | 0.046 | 1.299 | 15.2 | 16.0 | -19.6 |
| all | static_banner | 210724 | 1.091 | 0.95 | 0.9 | 4.93 | 0.257 | 1.086 | 0.0 | 0.0 | 0.0 |
| nike | glance_generative | 134333 | 1.222 | 2.64 | 44.9 | 7.23 | 0.016 | 0.88 | 29.1 | 39.3 | 22.4 |
| nike | standard_video | 60239 | 1.107 | 1.61 | 11.4 | 6.08 | 0.05 | 1.268 | 17.0 | 17.1 | -11.9 |
| nike | static_banner | 105258 | 0.946 | 0.94 | 0.9 | 5.19 | 0.292 | 1.133 | 0.0 | 0.0 | 0.0 |
| starbucks | glance_generative | 135962 | 1.444 | 2.61 | 44.1 | 6.12 | 0.014 | 0.883 | 16.9 | 31.0 | 15.1 |
| starbucks | standard_video | 60742 | 1.406 | 1.61 | 11.5 | 5.37 | 0.043 | 1.33 | 13.8 | 14.7 | -28.0 |
| starbucks | static_banner | 105466 | 1.235 | 0.95 | 0.9 | 4.68 | 0.228 | 1.039 | 0.0 | 0.0 | 0.0 |

## Off-policy evaluation of the generative engine (gold.model_policy_evaluation, written by the training job)

```sql
SELECT policy, round(pred_ctr*100,2) pred_ctr_pct, round(pred_dwell_s,2) pred_dwell_s, round(pred_opt_out*100,3) pred_opt_out_pct, round(pred_ecpm_usd,2) pred_ecpm_usd, round(ctr_lift_vs_static*100,1) ctr_lift_pct, round(ecpm_lift_vs_static*100,1) ecpm_lift_pct, round(opt_out_reduction_vs_static*100,1) opt_out_reduction_pct, model_version, evaluated_at FROM glance_genad.gold.model_policy_evaluation
```

| policy | pred_ctr_pct | pred_dwell_s | pred_opt_out_pct | pred_ecpm_usd | ctr_lift_pct | ecpm_lift_pct | opt_out_reduction_pct | model_version | evaluated_at |
|---|---|---|---|---|---|---|---|---|---|
| static_banner (control) | 1.1 | 0.94 | 1.098 | 4.96 | 0.0 | 0.0 | 0.0 | 7 | 2026-11-05T15:40:28.446Z |
| generative - logged policy (rule + exploration) | 1.37 | 2.61 | 0.958 | 6.77 | 23.9 | 36.4 | 12.8 | 7 | 2026-11-05T15:40:28.446Z |
| generative - optimized (argmax of 50 layout x angle combos) | 1.96 | 3.1 | 0.885 | 9.1 | 77.5 | 83.5 | 19.4 | 7 | 2026-11-05T15:40:28.446Z |

## Metric view query: weekly KPIs, control vs variant (gold.mv_ad_effectiveness)

```sql
SELECT event_week, experience_group, MEASURE(impressions) impressions, round(MEASURE(ctr)*100,3) ctr_pct, round(MEASURE(avg_interaction_duration_s),2) dwell_s, round(MEASURE(ecpm_usd),2) ecpm_usd, round(MEASURE(opt_out_rate)*100,3) opt_out_pct FROM glance_genad.gold.mv_ad_effectiveness GROUP BY ALL ORDER BY event_week, experience_group
```

| event_week | experience_group | impressions | ctr_pct | dwell_s | ecpm_usd | opt_out_pct |
|---|---|---|---|---|---|---|
| 2026-08-31T00:00:00.000Z | Generative (variant) | 4484 | 1.271 | 2.57 | 6.49 | 0.959 |
| 2026-08-31T00:00:00.000Z | Traditional (control) | 5516 | 1.197 | 1.2 | 5.46 | 1.033 |
| 2026-09-07T00:00:00.000Z | Generative (variant) | 31616 | 1.496 | 2.62 | 7.23 | 0.857 |
| 2026-09-07T00:00:00.000Z | Traditional (control) | 38384 | 1.248 | 1.19 | 5.54 | 1.232 |
| 2026-09-14T00:00:00.000Z | Generative (variant) | 31542 | 1.236 | 2.63 | 6.28 | 0.885 |
| 2026-09-14T00:00:00.000Z | Traditional (control) | 38458 | 1.037 | 1.19 | 4.85 | 1.131 |
| 2026-09-21T00:00:00.000Z | Generative (variant) | 31304 | 1.291 | 2.62 | 6.56 | 0.907 |
| 2026-09-21T00:00:00.000Z | Traditional (control) | 38696 | 1.181 | 1.18 | 5.33 | 1.222 |
| 2026-09-28T00:00:00.000Z | Generative (variant) | 31364 | 1.46 | 2.64 | 7.19 | 0.867 |
| 2026-09-28T00:00:00.000Z | Traditional (control) | 38636 | 1.121 | 1.19 | 5.09 | 1.188 |
| 2026-10-05T00:00:00.000Z | Generative (variant) | 31527 | 1.269 | 2.63 | 6.44 | 0.936 |
| 2026-10-05T00:00:00.000Z | Traditional (control) | 38473 | 1.128 | 1.19 | 5.11 | 1.167 |
| 2026-10-12T00:00:00.000Z | Generative (variant) | 31430 | 1.336 | 2.66 | 6.7 | 0.827 |
| 2026-10-12T00:00:00.000Z | Traditional (control) | 38570 | 1.193 | 1.2 | 5.37 | 1.182 |
| 2026-10-19T00:00:00.000Z | Generative (variant) | 31395 | 1.303 | 2.63 | 6.57 | 0.917 |
| 2026-10-19T00:00:00.000Z | Traditional (control) | 38605 | 1.114 | 1.18 | 5.08 | 1.14 |
| 2026-10-26T00:00:00.000Z | Generative (variant) | 31244 | 1.258 | 2.58 | 6.33 | 0.883 |
| 2026-10-26T00:00:00.000Z | Traditional (control) | 38756 | 1.13 | 1.18 | 5.14 | 1.066 |
| 2026-11-02T00:00:00.000Z | Generative (variant) | 14389 | 1.39 | 2.61 | 6.94 | 0.792 |
| 2026-11-02T00:00:00.000Z | Traditional (control) | 17611 | 1.272 | 1.18 | 5.7 | 1.17 |

## Metric view query: best generative theme per weather (historical evidence the model learns from)

```sql
SELECT weather, layout_theme, MEASURE(impressions) impressions, round(MEASURE(ctr)*100,3) ctr_pct, round(MEASURE(avg_interaction_duration_s),2) dwell_s FROM glance_genad.gold.mv_ad_effectiveness WHERE ad_format = 'glance_generative' GROUP BY ALL ORDER BY weather, ctr_pct DESC
```

| weather | layout_theme | impressions | ctr_pct | dwell_s |
|---|---|---|---|---|
| cloudy | chill_lounge | 2457 | 1.384 | 2.59 |
| cloudy | urban_commute | 2440 | 1.27 | 2.41 |
| cloudy | energetic_sport | 1233 | 1.217 | 2.67 |
| cloudy | minimal_tech | 29275 | 1.182 | 2.48 |
| cloudy | night_calm | 2481 | 1.048 | 2.41 |
| cloudy | sunrise_fresh | 2495 | 0.962 | 2.37 |
| cloudy | cozy_warm | 2460 | 0.935 | 2.57 |
| cloudy | live_match_hype | 2435 | 0.862 | 2.07 |
| cloudy | bold_neon | 1186 | 0.843 | 2.47 |
| cloudy | rain_atmos | 2512 | 0.836 | 2.47 |
| cold | cozy_warm | 15917 | 2.061 | 3.14 |
| cold | bold_neon | 662 | 1.662 | 2.41 |
| cold | minimal_tech | 1359 | 1.619 | 2.57 |
| cold | sunrise_fresh | 1337 | 1.571 | 2.49 |
| cold | urban_commute | 1335 | 1.498 | 2.53 |
| cold | rain_atmos | 1330 | 1.429 | 2.37 |
| cold | live_match_hype | 1315 | 1.369 | 2.15 |
| cold | night_calm | 1327 | 1.206 | 2.45 |
| cold | energetic_sport | 678 | 1.032 | 2.68 |
| cold | chill_lounge | 1318 | 0.986 | 2.5 |
| heavy_rain | cozy_warm | 3350 | 1.821 | 3.03 |
| heavy_rain | rain_atmos | 40710 | 1.609 | 3.12 |
| heavy_rain | chill_lounge | 3323 | 1.505 | 2.61 |
| heavy_rain | urban_commute | 3291 | 1.246 | 2.46 |
| heavy_rain | live_match_hype | 3382 | 1.242 | 2.26 |
| heavy_rain | energetic_sport | 1654 | 1.209 | 2.7 |
| heavy_rain | night_calm | 3396 | 1.207 | 2.45 |
| heavy_rain | minimal_tech | 3433 | 1.165 | 2.55 |
| heavy_rain | bold_neon | 1739 | 1.093 | 2.4 |
| heavy_rain | sunrise_fresh | 3284 | 0.944 | 2.18 |
| hot_humid | bold_neon | 1121 | 2.052 | 2.41 |
| hot_humid | energetic_sport | 1106 | 1.356 | 2.7 |
| hot_humid | night_calm | 2204 | 1.316 | 2.35 |
| hot_humid | urban_commute | 2262 | 1.149 | 2.44 |
| hot_humid | chill_lounge | 26976 | 1.049 | 2.47 |
| hot_humid | minimal_tech | 2355 | 0.977 | 2.48 |
| hot_humid | live_match_hype | 2208 | 0.861 | 2.1 |
| hot_humid | rain_atmos | 2215 | 0.813 | 2.04 |
| hot_humid | sunrise_fresh | 2144 | 0.653 | 2.37 |
| hot_humid | cozy_warm | 2277 | 0.571 | 2.13 |
| sunny | energetic_sport | 1998 | 1.702 | 2.86 |
| sunny | minimal_tech | 4246 | 1.484 | 2.48 |
| sunny | sunrise_fresh | 49454 | 1.478 | 2.7 |
| sunny | chill_lounge | 4147 | 1.278 | 2.51 |
| sunny | bold_neon | 2107 | 1.234 | 2.42 |
| sunny | cozy_warm | 4188 | 1.17 | 2.58 |
| sunny | urban_commute | 3942 | 1.167 | 2.4 |
| sunny | live_match_hype | 4044 | 1.088 | 2.09 |
| sunny | night_calm | 4101 | 0.951 | 2.23 |
| sunny | rain_atmos | 4086 | 0.734 | 1.81 |

## Live app decisions flowing back through Lakebase -> Lakehouse Sync -> pipeline (gold.mv_live_simulations)

```sql
SELECT brand, weather, user_state, chosen_theme, MEASURE(decisions) decisions, round(MEASURE(predicted_ctr_lift)*100,0) ctr_lift_pct, round(MEASURE(predicted_ecpm_lift)*100,0) ecpm_lift_pct, round(MEASURE(avg_predicted_dwell_s),2) dwell_s, round(MEASURE(avg_attention_score),1) attention FROM glance_genad.gold.mv_live_simulations GROUP BY ALL ORDER BY decisions DESC LIMIT 15
```

| brand | weather | user_state | chosen_theme | decisions | ctr_lift_pct | ecpm_lift_pct | dwell_s | attention |
|---|---|---|---|---|---|---|---|---|
| starbucks | heavy_rain | just_missed_train | cozy_warm | 6 | 129.0 | 126.0 | 3.42 | 82.1 |
| nike | cloudy | relaxing_at_home | chill_lounge | 5 | 102.0 | 98.0 | 2.89 | 63.3 |
| nike | sunny | working_out | sunrise_fresh | 2 | 308.0 | 289.0 | 4.3 | 87.5 |
| nike | heavy_rain | working_out | sunrise_fresh | 2 | 198.0 | 185.0 | 3.42 | 82.2 |
| nike | hot_humid | at_office | minimal_tech | 2 | 47.0 | 65.0 | 3.42 | 63.0 |
| starbucks | hot_humid | at_office | minimal_tech | 1 | 32.0 | 51.0 | 2.99 | 61.1 |

## Top learned CTR weights (ml.model_coefficients) - model recovers context x creative interactions

```sql
SELECT model_version, feature, round(weight,3) weight FROM glance_genad.ml.model_coefficients WHERE model_name = 'ctr' AND feature NOT LIKE '\_\_%' ORDER BY weight DESC LIMIT 15
```

| model_version | feature | weight |
|---|---|---|
| 7 | brand=nike|user_state=working_out | 0.298 |
| 7 | theme=chill_lounge|user_state=relaxing_at_home | 0.27 |
| 7 | theme=rain_atmos|weather=heavy_rain | 0.222 |
| 7 | angle=performance|user_state=working_out | 0.209 |
| 7 | theme=sunrise_fresh|weather=sunny | 0.206 |
| 7 | theme=cozy_warm|weather=cold | 0.204 |
| 7 | theme=urban_commute|time_slot=morning_rush | 0.193 |
| 7 | brand=starbucks|user_state=just_missed_train | 0.184 |
| 7 | theme=sunrise_fresh|time_slot=morning_rush | 0.173 |
| 7 | theme=minimal_tech|user_state=at_office | 0.17 |
| 7 | brand=nike|segment=fitness_enthusiast | 0.16 |
| 7 | angle=comfort|user_state=relaxing_at_home | 0.159 |
| 7 | theme=sunrise_fresh|segment=tech_professional | 0.15 |
| 7 | theme=sunrise_fresh|user_state=working_out | 0.146 |
| 7 | angle=comfort|weather=heavy_rain | 0.135 |

## Saturation calibration parameters exported with the model

```sql
SELECT model_name, feature, weight FROM glance_genad.ml.model_coefficients WHERE feature LIKE '\_\_%' ORDER BY model_name, feature
```

| model_name | feature | weight |
|---|---|---|
| ctr | __intercept__ | -1.0628105873570006 |
| ctr | __sat_A__ | 0.6 |
| ctr | __sat_scale__ | 0.85 |
| dwell | __intercept__ | 0.30559412651717016 |
| dwell | __sat_A__ | 0.5 |
| dwell | __sat_scale__ | 1.15 |
| dwell | __sigma__ | 0.4506188182446385 |
| opt_out | __intercept__ | -1.0568461863986431 |
| opt_out | __sat_A__ | 0.3 |
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
| silver | silver_user_profiles | column_mask | glance_genad.governance.mask_email | email |
| silver | silver_user_profiles | column_mask | glance_genad.governance.mask_name | full_name |
| silver | silver_user_profiles | column_mask | glance_genad.governance.mask_ad_id | device_ad_id |

## Brand entitlements driving the row filter

```sql
SELECT principal, brand, granted_by FROM glance_genad.governance.brand_entitlements
```

| principal | brand | granted_by |
|---|---|---|
| 81f5cf7e-a15f-4710-8f01-03b28e0fe4ed | * | deepak.suryaprakash@databricks.com |
| deepak.suryaprakash@databricks.com | * | deepak.suryaprakash@databricks.com |

## Live context in gold (from the Lakebase stream)

```sql
SELECT * FROM glance_genad.gold.live_context_latest ORDER BY city, signal_type
```

| city | signal_type | signal_key | signal_value | temp_c | intensity | observed_at |
|---|---|---|---|---|---|---|
| Bengaluru | live_event | cricket_live | IND 195/5 (19.2 ov) vs AUS |  | 0.9 | 2026-11-05T15:17:49.953Z |
| Bengaluru | transit | train_delay | Purple line metro: 9 min headway |  | 0.4 | 2026-11-05T13:08:23.552Z |
| Bengaluru | weather | cloudy | Cloudy, 23°C | 23.0 | 0.47 | 2026-11-05T15:17:19.901Z |
| Delhi | live_event | city_marathon | Delhi Half Marathon this Sunday — 42k registered |  | 0.55 | 2026-11-05T13:08:23.552Z |
| Delhi | weather | cloudy | Cloudy, 25°C | 24.0 | 0.23 | 2026-11-05T15:17:14.892Z |
| Hyderabad | live_event | esports_final | BGMI Masters Grand Final — Map 3 live |  | 0.8 | 2026-11-05T13:08:23.552Z |
| Hyderabad | weather | cloudy | Cloudy, 24°C | 26.0 | 0.66 | 2026-11-05T15:17:39.936Z |
| Jakarta | weather | cold | Cold, 6°C | 10.0 | 0.62 | 2026-11-05T15:16:54.847Z |
| Mumbai | live_event | football_live | Mumbai City 2-2 Bengaluru FC (79') |  | 0.75 | 2026-11-05T15:17:49.953Z |
| Mumbai | transit | train_delay | Western line locals running 20 min late |  | 0.8 | 2026-11-05T15:17:34.928Z |
| Mumbai | weather | heavy_rain | Heavy Rain, 24°C | 26.0 | 0.54 | 2026-11-05T15:17:49.953Z |
| Pune | weather | sunny | Sunny, 31°C | 32.0 | 0.5 | 2026-11-05T15:17:44.945Z |

