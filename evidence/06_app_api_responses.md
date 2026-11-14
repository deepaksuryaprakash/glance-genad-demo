# Live app API responses (collected 2026-11-14 15:38 UTC from https://glance-genad-7474659149187518.aws.databricksapps.com)

## /api/health

```json
{
 "lakebase": "ok",
 "models": "ok (Lakebase synced table glance_serving.model_coefficients, v1)",
 "model_version": "1",
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
 "decision_id": "dec-5b91a73914fe",
 "model_version": "1",
 "model_source": "Lakebase synced table glance_serving.model_coefficients",
 "winner": {
  "theme": "cozy_warm",
  "angle": "time_saving",
  "layers": [
   "theme-cozy_warm",
   "fx-rain",
   "light-morning",
   "widget-transit",
   "skin-pastel_soft"
  ]
 },
 "copy": {
  "headline": "Missed the train? Coffee's still warm.",
  "body": "Rainy rush hour, missed train? Pre-order now and skip the line.",
  "cta": "Order ahead"
 },
 "copy_source": "llm",
 "matched_component": "sb_mobile_order",
 "rejected_by_guardrail": [],
 "blocked_combos": 5,
 "static": {
  "pctr": 0.0263,
  "pdwell_s": 0.9475,
  "poptout": 0.0101,
  "ecpm": 8.5684,
  "attention": 48.3,
  "relevance": 24.6
 },
 "generative": {
  "pctr": 0.0532,
  "pdwell_s": 3.7495,
  "poptout": 0.006,
  "ecpm": 17.6095,
  "attention": 84.4,
  "relevance": 60.1
 },
 "lift": {
  "ctr": 1.0283,
  "ecpm": 1.0552,
  "dwell": 2.9571,
  "optout_reduction": 0.4096,
  "attention_pts": 36.1,
  "cpe_static": 0.3264,
  "cpe_generative": 0.0235
 },
 "leaderboard_top5": [
  {
   "theme": "cozy_warm",
   "angle": "time_saving",
   "pctr": 0.0532,
   "ecpm": 17.61,
   "blocked": null
  },
  {
   "theme": "energetic_sport",
   "angle": "time_saving",
   "pctr": 0.046,
   "ecpm": 15.25,
   "blocked": "theme"
  },
  {
   "theme": "urban_commute",
   "angle": "time_saving",
   "pctr": 0.0434,
   "ecpm": 14.87,
   "blocked": null
  },
  {
   "theme": "rain_atmos",
   "angle": "comfort",
   "pctr": 0.0434,
   "ecpm": 14.69,
   "blocked": null
  },
  {
   "theme": "sunrise_fresh",
   "angle": "time_saving",
   "pctr": 0.0409,
   "ecpm": 13.8,
   "blocked": null
  }
 ],
 "why": [
  {
   "feature": "Cozy / Warm \u00d7 Just missed a train",
   "weight": 0.101
  },
  {
   "feature": "Time-saving \u00d7 8 AM Rush Hour",
   "weight": 0.089
  },
  {
   "feature": "Time-saving \u00d7 Just missed a train",
   "weight": 0.088
  },
  {
   "feature": "Cozy / Warm \u00d7 Starbucks",
   "weight": 0.074
  },
  {
   "feature": "Cozy / Warm \u00d7 Daily Commuter",
   "weight": 0.074
  },
  {
   "feature": "Cozy / Warm \u00d7 Heavy Rain",
   "weight": 0.071
  }
 ],
 "timings_ms": {
  "score_ms": 1.7,
  "vector_search_ms": 1393.2,
  "embedding_ms": 1041.9,
  "copy_ms": 2480.1,
  "total_ms": 4917.1,
  "lakebase_profile_ms": 2.8,
  "lakebase_write_ms": 5.4
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
 "decision_id": "dec-2636e8cc1830",
 "model_version": "1",
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
  "headline": "Sunrise is your starting line.",
  "body": "Responsive Pegasus 41 energy for your sunlit morning run. Push the pace now.",
  "cta": "Start your run"
 },
 "copy_source": "llm",
 "matched_component": "nk_zoom_speed",
 "rejected_by_guardrail": [],
 "blocked_combos": 14,
 "static": {
  "pctr": 0.0236,
  "pdwell_s": 0.9461,
  "poptout": 0.0122,
  "ecpm": 11.1269,
  "attention": 45.6,
  "relevance": 23.3
 },
 "generative": {
  "pctr": 0.0608,
  "pdwell_s": 3.821,
  "poptout": 0.0075,
  "ecpm": 28.2756,
  "attention": 84.8,
  "relevance": 63.8
 },
 "lift": {
  "ctr": 1.5783,
  "ecpm": 1.5412,
  "dwell": 3.0389,
  "optout_reduction": 0.3805,
  "attention_pts": 39.2,
  "cpe_static": 0.4716,
  "cpe_generative": 0.0371
 },
 "leaderboard_top5": [
  {
   "theme": "sunrise_fresh",
   "angle": "performance",
   "pctr": 0.0608,
   "ecpm": 28.28,
   "blocked": null
  },
  {
   "theme": "energetic_sport",
   "angle": "performance",
   "pctr": 0.0558,
   "ecpm": 26.22,
   "blocked": null
  },
  {
   "theme": "urban_commute",
   "angle": "performance",
   "pctr": 0.0496,
   "ecpm": 23.33,
   "blocked": null
  },
  {
   "theme": "bold_neon",
   "angle": "performance",
   "pctr": 0.0445,
   "ecpm": 21.02,
   "blocked": "theme"
  },
  {
   "theme": "chill_lounge",
   "angle": "performance",
   "pctr": 0.0438,
   "ecpm": 20.79,
   "blocked": null
  }
 ],
 "why": [
  {
   "feature": "Sunrise Fresh \u00d7 Sunny",
   "weight": 0.2
  },
  {
   "feature": "Performance \u00d7 Working out",
   "weight": 0.187
  },
  {
   "feature": "Sunrise Fresh \u00d7 8 AM Rush Hour",
   "weight": 0.163
  },
  {
   "feature": "Sunrise Fresh \u00d7 Working out",
   "weight": 0.139
  },
  {
   "feature": "Performance \u00d7 Nike",
   "weight": 0.085
  },
  {
   "feature": "Performance \u00d7 Fitness Enthusiast",
   "weight": 0.067
  }
 ],
 "timings_ms": {
  "score_ms": 1.74,
  "vector_search_ms": 592.3,
  "embedding_ms": 617.7,
  "copy_ms": 4853.9,
  "total_ms": 6065.9,
  "lakebase_profile_ms": 3.0,
  "lakebase_write_ms": 7.1
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
 "decision_id": "dec-b1fa6f19e42e",
 "model_version": "1",
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
  "headline": "Bleed blue. Every ball. Tonight.",
  "body": "IND vs AUS is live. Pull on the jersey, feel the roar.",
  "cta": "Join the watch"
 },
 "copy_source": "llm",
 "matched_component": "nk_fan_jersey",
 "rejected_by_guardrail": [],
 "blocked_combos": 14,
 "static": {
  "pctr": 0.0084,
  "pdwell_s": 0.9569,
  "poptout": 0.0121,
  "ecpm": 4.7555,
  "attention": 30.7,
  "relevance": 17.9
 },
 "generative": {
  "pctr": 0.0136,
  "pdwell_s": 3.1484,
  "poptout": 0.0092,
  "ecpm": 8.158,
  "attention": 63.8,
  "relevance": 53.3
 },
 "lift": {
  "ctr": 0.6208,
  "ecpm": 0.7155,
  "dwell": 2.2902,
  "optout_reduction": 0.2396,
  "attention_pts": 33.1,
  "cpe_static": 0.5145,
  "cpe_generative": 0.0133
 },
 "leaderboard_top5": [
  {
   "theme": "chill_lounge",
   "angle": "social_fomo",
   "pctr": 0.0136,
   "ecpm": 8.16,
   "blocked": null
  },
  {
   "theme": "night_calm",
   "angle": "social_fomo",
   "pctr": 0.0125,
   "ecpm": 7.99,
   "blocked": null
  },
  {
   "theme": "bold_neon",
   "angle": "social_fomo",
   "pctr": 0.0109,
   "ecpm": 6.78,
   "blocked": "theme"
  },
  {
   "theme": "energetic_sport",
   "angle": "social_fomo",
   "pctr": 0.011,
   "ecpm": 6.64,
   "blocked": null
  },
  {
   "theme": "cozy_warm",
   "angle": "social_fomo",
   "pctr": 0.0101,
   "ecpm": 6.54,
   "blocked": null
  }
 ],
 "why": [
  {
   "feature": "Chill Lounge \u00d7 Relaxing at home",
   "weight": 0.212
  },
  {
   "feature": "Social / FOMO \u00d7 Live Cricket: IND vs AUS",
   "weight": 0.129
  },
  {
   "feature": "Chill Lounge \u00d7 11 PM Night",
   "weight": 0.063
  },
  {
   "feature": "Social / FOMO \u00d7 Night Owl Streamer",
   "weight": 0.061
  },
  {
   "feature": "Chill Lounge \u00d7 Nike",
   "weight": 0.04
  },
  {
   "feature": "Chill Lounge \u00d7 Cloudy",
   "weight": 0.026
  }
 ],
 "timings_ms": {
  "score_ms": 1.56,
  "vector_search_ms": 812.0,
  "embedding_ms": 874.9,
  "copy_ms": 4830.6,
  "total_ms": 6519.2,
  "lakebase_profile_ms": 2.9,
  "lakebase_write_ms": 5.2
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
 "decision_id": "dec-69f444b6e1bd",
 "model_version": "1",
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
  "headline": "Final's live. Your feet deserve rest.",
  "body": "Humid evening, BGMI final live. Recovery is training too. Slip into soft cushioning.",
  "cta": "Shop Calm Slides"
 },
 "copy_source": "llm",
 "matched_component": "nk_comfort_recovery",
 "rejected_by_guardrail": [
  "nk_neon_pink_recolor"
 ],
 "blocked_combos": 14,
 "static": {
  "pctr": 0.009,
  "pdwell_s": 0.921,
  "poptout": 0.0096,
  "ecpm": 4.993,
  "attention": 30.6,
  "relevance": 11.8
 },
 "generative": {
  "pctr": 0.0127,
  "pdwell_s": 3.4991,
  "poptout": 0.0071,
  "ecpm": 7.9221,
  "attention": 65.4,
  "relevance": 43.9
 },
 "lift": {
  "ctr": 0.4093,
  "ecpm": 0.5866,
  "dwell": 2.7993,
  "optout_reduction": 0.2631,
  "attention_pts": 34.8,
  "cpe_static": 0.555,
  "cpe_generative": 0.0113
 },
 "leaderboard_top5": [
  {
   "theme": "chill_lounge",
   "angle": "social_fomo",
   "pctr": 0.0127,
   "ecpm": 7.92,
   "blocked": null
  },
  {
   "theme": "night_calm",
   "angle": "social_fomo",
   "pctr": 0.0122,
   "ecpm": 7.41,
   "blocked": null
  },
  {
   "theme": "energetic_sport",
   "angle": "social_fomo",
   "pctr": 0.0117,
   "ecpm": 7.41,
   "blocked": null
  },
  {
   "theme": "bold_neon",
   "angle": "social_fomo",
   "pctr": 0.0109,
   "ecpm": 7.34,
   "blocked": "theme"
  },
  {
   "theme": "live_match_hype",
   "angle": "social_fomo",
   "pctr": 0.0099,
   "ecpm": 6.72,
   "blocked": null
  }
 ],
 "why": [
  {
   "feature": "Chill Lounge \u00d7 Relaxing at home",
   "weight": 0.212
  },
  {
   "feature": "Chill Lounge \u00d7 7 PM Evening",
   "weight": 0.096
  },
  {
   "feature": "Social / FOMO \u00d7 7 PM Evening",
   "weight": 0.094
  },
  {
   "feature": "Chill Lounge \u00d7 Nike",
   "weight": 0.04
  },
  {
   "feature": "Social / FOMO \u00d7 Esports Final (BGMI)",
   "weight": 0.032
  },
  {
   "feature": "Chill Lounge \u00d7 Vibrant Neon",
   "weight": 0.022
  }
 ],
 "timings_ms": {
  "score_ms": 1.73,
  "vector_search_ms": 255.8,
  "embedding_ms": 485.6,
  "copy_ms": 3722.7,
  "total_ms": 4466.1,
  "lakebase_profile_ms": 2.9,
  "lakebase_write_ms": 7.1
 }
}
```

