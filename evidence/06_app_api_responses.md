# Live app API responses (collected 2026-11-09 10:16 UTC from https://glance-genad-7474647312316070.aws.databricksapps.com)

## /api/health

```json
{
 "lakebase": "ok",
 "models": "ok (Lakebase synced table glance_serving.model_coefficients, v7)",
 "model_version": "7",
 "model_source": "Lakebase synced table glance_serving.model_coefficients"
}
```

## POST /api/generate - starbucks / heavy_rain / morning_rush / just_missed_train / none

```json
{
 "request": {
  "user_id": "U90002",
  "brand": "starbucks",
  "weather": "heavy_rain",
  "time_slot": "morning_rush",
  "user_state": "just_missed_train",
  "live_event": "none"
 },
 "decision_id": "dec-0ec4f75517a8",
 "model_version": "7",
 "model_source": "Lakebase synced table glance_serving.model_coefficients",
 "winner": {
  "theme": "urban_commute",
  "angle": "time_saving",
  "layers": [
   "theme-urban_commute",
   "fx-rain",
   "light-morning",
   "widget-transit",
   "skin-pastel_soft"
  ]
 },
 "copy": {
  "headline": "Missed your train? Coffee's ready.",
  "body": "Rain and rush hour? Pre-order on the app and skip the line.",
  "cta": "Tap to pre-order"
 },
 "copy_source": "llm",
 "matched_component": "sb_mobile_order",
 "rejected_by_guardrail": [],
 "blocked_combos": 5,
 "static": {
  "pctr": 0.0258,
  "pdwell_s": 0.9427,
  "poptout": 0.0108,
  "ecpm": 8.4523,
  "attention": 47.8,
  "relevance": 24.6
 },
 "generative": {
  "pctr": 0.0522,
  "pdwell_s": 3.6463,
  "poptout": 0.0065,
  "ecpm": 17.2854,
  "attention": 83.7,
  "relevance": 59.2
 },
 "lift": {
  "ctr": 1.0214,
  "ecpm": 1.0451,
  "dwell": 2.868,
  "optout_reduction": 0.3952,
  "attention_pts": 35.9,
  "cpe_static": 0.3271,
  "cpe_generative": 0.0237
 },
 "leaderboard_top5": [
  {
   "theme": "urban_commute",
   "angle": "time_saving",
   "pctr": 0.0522,
   "ecpm": 17.29,
   "blocked": null
  },
  {
   "theme": "cozy_warm",
   "angle": "comfort",
   "pctr": 0.0527,
   "ecpm": 17.24,
   "blocked": null
  },
  {
   "theme": "rain_atmos",
   "angle": "comfort",
   "pctr": 0.0509,
   "ecpm": 16.78,
   "blocked": null
  },
  {
   "theme": "energetic_sport",
   "angle": "time_saving",
   "pctr": 0.0472,
   "ecpm": 15.56,
   "blocked": "theme"
  },
  {
   "theme": "minimal_tech",
   "angle": "time_saving",
   "pctr": 0.0411,
   "ecpm": 13.75,
   "blocked": null
  }
 ],
 "why": [
  {
   "feature": "Urban Commute \u00d7 8 AM Rush Hour",
   "weight": 0.193
  },
  {
   "feature": "Time-saving \u00d7 8 AM Rush Hour",
   "weight": 0.093
  },
  {
   "feature": "Urban Commute \u00d7 Daily Commuter",
   "weight": 0.077
  },
  {
   "feature": "Time-saving \u00d7 Just missed a train",
   "weight": 0.074
  },
  {
   "feature": "Urban Commute \u00d7 Pastel Soft",
   "weight": 0.047
  },
  {
   "feature": "Time-saving \u00d7 Daily Commuter",
   "weight": 0.031
  }
 ],
 "timings_ms": {
  "score_ms": 1.68,
  "vector_search_ms": 553.7,
  "embedding_ms": 443.6,
  "copy_ms": 3120.5,
  "total_ms": 4119.7,
  "lakebase_profile_ms": 3.5,
  "lakebase_write_ms": 8.0
 }
}
```

## POST /api/generate - nike / sunny / morning_rush / working_out / none

```json
{
 "request": {
  "user_id": "U90001",
  "brand": "nike",
  "weather": "sunny",
  "time_slot": "morning_rush",
  "user_state": "working_out",
  "live_event": "none"
 },
 "decision_id": "dec-d39133298224",
 "model_version": "7",
 "model_source": "Lakebase synced table glance_serving.model_coefficients",
 "winner": {
  "theme": "sunrise_fresh",
  "angle": "performance",
  "layers": [
   "theme-sunrise_fresh",
   "fx-sunrays",
   "light-morning",
   "skin-nature_green"
  ]
 },
 "copy": {
  "headline": "Own the morning. Own the run.",
  "body": "Sunny skies, 8 AM, and Pegasus 41 responsive energy for every stride.",
  "cta": "Shop Pegasus 41"
 },
 "copy_source": "llm",
 "matched_component": "nk_zoom_speed",
 "rejected_by_guardrail": [],
 "blocked_combos": 14,
 "static": {
  "pctr": 0.0228,
  "pdwell_s": 0.95,
  "poptout": 0.0115,
  "ecpm": 10.8114,
  "attention": 45.0,
  "relevance": 23.3
 },
 "generative": {
  "pctr": 0.0535,
  "pdwell_s": 3.6268,
  "poptout": 0.007,
  "ecpm": 25.1351,
  "attention": 83.6,
  "relevance": 64.6
 },
 "lift": {
  "ctr": 1.3436,
  "ecpm": 1.3249,
  "dwell": 2.8175,
  "optout_reduction": 0.3919,
  "attention_pts": 38.6,
  "cpe_static": 0.4733,
  "cpe_generative": 0.0346
 },
 "leaderboard_top5": [
  {
   "theme": "sunrise_fresh",
   "angle": "performance",
   "pctr": 0.0535,
   "ecpm": 25.14,
   "blocked": null
  },
  {
   "theme": "energetic_sport",
   "angle": "performance",
   "pctr": 0.05,
   "ecpm": 23.71,
   "blocked": null
  },
  {
   "theme": "urban_commute",
   "angle": "performance",
   "pctr": 0.048,
   "ecpm": 22.6,
   "blocked": null
  },
  {
   "theme": "chill_lounge",
   "angle": "performance",
   "pctr": 0.0437,
   "ecpm": 20.7,
   "blocked": null
  },
  {
   "theme": "bold_neon",
   "angle": "performance",
   "pctr": 0.0428,
   "ecpm": 20.3,
   "blocked": "theme"
  }
 ],
 "why": [
  {
   "feature": "Performance \u00d7 Working out",
   "weight": 0.209
  },
  {
   "feature": "Sunrise Fresh \u00d7 Sunny",
   "weight": 0.206
  },
  {
   "feature": "Sunrise Fresh \u00d7 8 AM Rush Hour",
   "weight": 0.173
  },
  {
   "feature": "Sunrise Fresh \u00d7 Working out",
   "weight": 0.146
  },
  {
   "feature": "Sunrise Fresh \u00d7 Fitness Enthusiast",
   "weight": 0.13
  },
  {
   "feature": "Performance \u00d7 Nike",
   "weight": 0.123
  }
 ],
 "timings_ms": {
  "score_ms": 1.57,
  "vector_search_ms": 382.1,
  "embedding_ms": 526.7,
  "copy_ms": 2983.6,
  "total_ms": 3894.1,
  "lakebase_profile_ms": 3.4,
  "lakebase_write_ms": 9.8
 }
}
```

## POST /api/generate - nike / cloudy / late_night / relaxing_at_home / cricket_live

```json
{
 "request": {
  "user_id": "U90005",
  "brand": "nike",
  "weather": "cloudy",
  "time_slot": "late_night",
  "user_state": "relaxing_at_home",
  "live_event": "cricket_live"
 },
 "decision_id": "dec-ccc6885235d8",
 "model_version": "7",
 "model_source": "Lakebase synced table glance_serving.model_coefficients",
 "winner": {
  "theme": "chill_lounge",
  "angle": "social_fomo",
  "layers": [
   "theme-chill_lounge",
   "fx-clouds",
   "light-night",
   "widget-live",
   "skin-dark_minimal"
  ]
 },
 "copy": {
  "headline": "The whole country's watching",
  "body": "IND vs AUS is live. Wear the jersey. Feel the stadium from your couch.",
  "cta": "Bleed blue now"
 },
 "copy_source": "llm",
 "matched_component": "nk_fan_jersey",
 "rejected_by_guardrail": [],
 "blocked_combos": 14,
 "static": {
  "pctr": 0.0085,
  "pdwell_s": 0.9565,
  "poptout": 0.0126,
  "ecpm": 4.7806,
  "attention": 30.7,
  "relevance": 17.9
 },
 "generative": {
  "pctr": 0.0142,
  "pdwell_s": 3.0447,
  "poptout": 0.0094,
  "ecpm": 8.3322,
  "attention": 63.5,
  "relevance": 56.2
 },
 "lift": {
  "ctr": 0.6743,
  "ecpm": 0.7429,
  "dwell": 2.1831,
  "optout_reduction": 0.2561,
  "attention_pts": 32.8,
  "cpe_static": 0.5196,
  "cpe_generative": 0.0143
 },
 "leaderboard_top5": [
  {
   "theme": "chill_lounge",
   "angle": "social_fomo",
   "pctr": 0.0142,
   "ecpm": 8.33,
   "blocked": null
  },
  {
   "theme": "night_calm",
   "angle": "social_fomo",
   "pctr": 0.0129,
   "ecpm": 8.08,
   "blocked": null
  },
  {
   "theme": "live_match_hype",
   "angle": "social_fomo",
   "pctr": 0.0102,
   "ecpm": 6.75,
   "blocked": null
  },
  {
   "theme": "bold_neon",
   "angle": "social_fomo",
   "pctr": 0.0101,
   "ecpm": 6.48,
   "blocked": "theme"
  },
  {
   "theme": "minimal_tech",
   "angle": "social_fomo",
   "pctr": 0.01,
   "ecpm": 6.36,
   "blocked": null
  }
 ],
 "why": [
  {
   "feature": "Chill Lounge \u00d7 Relaxing at home",
   "weight": 0.27
  },
  {
   "feature": "Social / FOMO \u00d7 Night Owl Streamer",
   "weight": 0.115
  },
  {
   "feature": "Social / FOMO \u00d7 Live Cricket: IND vs AUS",
   "weight": 0.078
  },
  {
   "feature": "Chill Lounge \u00d7 Night Owl Streamer",
   "weight": 0.06
  },
  {
   "feature": "Chill Lounge \u00d7 Nike",
   "weight": 0.048
  },
  {
   "feature": "Chill Lounge \u00d7 11 PM Night",
   "weight": 0.043
  }
 ],
 "timings_ms": {
  "score_ms": 1.55,
  "vector_search_ms": 492.6,
  "embedding_ms": 970.6,
  "copy_ms": 3411.5,
  "total_ms": 4876.5,
  "lakebase_profile_ms": 3.3,
  "lakebase_write_ms": 5.7
 }
}
```

## POST /api/generate - nike / hot_humid / evening / relaxing_at_home / esports_final

```json
{
 "request": {
  "user_id": "U90004",
  "brand": "nike",
  "weather": "hot_humid",
  "time_slot": "evening",
  "user_state": "relaxing_at_home",
  "live_event": "esports_final"
 },
 "decision_id": "dec-3a2ade3c1b74",
 "model_version": "7",
 "model_source": "Lakebase synced table glance_serving.model_coefficients",
 "winner": {
  "theme": "chill_lounge",
  "angle": "social_fomo",
  "layers": [
   "theme-chill_lounge",
   "fx-heat",
   "light-evening",
   "widget-live",
   "skin-vibrant_neon"
  ]
 },
 "copy": {
  "headline": "Final's live. Slip into comfort.",
  "body": "Humid night, BGMI final live. Sink into soft cushioning. Recovery is training too.",
  "cta": "Shop Calm Slides"
 },
 "copy_source": "llm",
 "matched_component": "nk_comfort_recovery",
 "rejected_by_guardrail": [
  "nk_neon_pink_recolor"
 ],
 "blocked_combos": 14,
 "static": {
  "pctr": 0.007,
  "pdwell_s": 0.9204,
  "poptout": 0.0094,
  "ecpm": 4.1642,
  "attention": 28.6,
  "relevance": 11.8
 },
 "generative": {
  "pctr": 0.0105,
  "pdwell_s": 3.2729,
  "poptout": 0.0088,
  "ecpm": 6.9013,
  "attention": 61.6,
  "relevance": 49.6
 },
 "lift": {
  "ctr": 0.4954,
  "ecpm": 0.6573,
  "dwell": 2.5558,
  "optout_reduction": 0.0641,
  "attention_pts": 33.0,
  "cpe_static": 0.5713,
  "cpe_generative": 0.0107
 },
 "leaderboard_top5": [
  {
   "theme": "chill_lounge",
   "angle": "social_fomo",
   "pctr": 0.0105,
   "ecpm": 6.9,
   "blocked": null
  },
  {
   "theme": "bold_neon",
   "angle": "performance",
   "pctr": 0.0085,
   "ecpm": 5.93,
   "blocked": "theme"
  },
  {
   "theme": "night_calm",
   "angle": "social_fomo",
   "pctr": 0.0091,
   "ecpm": 5.93,
   "blocked": null
  },
  {
   "theme": "live_match_hype",
   "angle": "social_fomo",
   "pctr": 0.0077,
   "ecpm": 5.7,
   "blocked": null
  },
  {
   "theme": "energetic_sport",
   "angle": "social_fomo",
   "pctr": 0.0079,
   "ecpm": 5.65,
   "blocked": null
  }
 ],
 "why": [
  {
   "feature": "Chill Lounge \u00d7 Relaxing at home",
   "weight": 0.27
  },
  {
   "feature": "Chill Lounge \u00d7 7 PM Evening",
   "weight": 0.088
  },
  {
   "feature": "Social / FOMO \u00d7 7 PM Evening",
   "weight": 0.077
  },
  {
   "feature": "Chill Lounge \u00d7 Vibrant Neon",
   "weight": 0.054
  },
  {
   "feature": "Chill Lounge \u00d7 Nike",
   "weight": 0.048
  },
  {
   "feature": "Chill Lounge \u00d7 Social / FOMO",
   "weight": 0.036
  }
 ],
 "timings_ms": {
  "score_ms": 2.3,
  "vector_search_ms": 993.7,
  "embedding_ms": 421.3,
  "copy_ms": 3474.1,
  "total_ms": 4891.8,
  "lakebase_profile_ms": 5.4,
  "lakebase_write_ms": 15.0
 }
}
```

