# Glance GenAd: Attention Friction & Ad Blindness demo

This demo is for InMobi/Glance. It takes live context (weather, time, user state, live events, phone skin) plus a user's behavioral profile and builds a hyper-contextual lock-screen ad layout in real time. It renders that layout side by side with the traditional static banner, and every simulation updates the predicted CTR, attention, eCPM, cost-per-engagement and opt-out numbers.

Workspace: `fe-sandbox-serverless-sandbox-8bg9w4` (CLI profile `fevm-biocon`). Bundle target: `fevm`.
App: https://glance-genad-7474647312316070.aws.databricksapps.com

## Execution evidence (text, from the running build)
See [`evidence/`](evidence/README.md), captured by `scripts/collect_evidence.py`:
- [SQL query results](evidence/01_query_results.md): medallion row counts, control-vs-variant KPIs, metric view queries, off-policy evaluation, learned weights, PII masks and row filters in effect
- [Job run logs](evidence/02_job_runs.md): datagen, training (metrics + policy table), context stream, refresh orchestration
- [Pipeline runs](evidence/03_pipeline_runs.md): updates, flow completions, data-quality expectation pass/fail counts
- [MLflow + UC model registry](evidence/04_mlflow_models.md): run metrics/params, model versions 1-7
- [Platform status](evidence/05_platform_status.md): Lakebase row counts (psql), Lakehouse Sync, synced table, Vector Search status + query result, App
- [Live app API responses](evidence/06_app_api_responses.md): real `/api/generate` output (scored leaderboard, VS match, guardrail rejections, LLM copy, timings)
- [Genie transcript](evidence/07_genie_transcript.md): questions, generated SQL, result rows

## Architecture

```
 mock streams ──► Lakebase Postgres (glance-genad) ── transactional / context DB + app backend
  (job 00)         glance_ops.user_profiles (20k users, PII)     glance_ops.context_signals (weather/match/transit)
                   glance_ops.creative_assets, brand_asset_components (registry + guardrails)
                   glance_ops.ad_decisions  ◄── every "Generate Ad Experience" from the app
                         │ Lakehouse Sync (CDC, Beta)                  ▲ Lakebase synced table (UC → PG)
                         ▼                                              │ glance_serving.model_coefficients
 ad-server logs ──► UC Volume raw.ad_logs ──► Lakeflow SDP pipeline (serverless)
  (job 01, 600k)        bronze: bronze_ad_impressions (Auto Loader) + lb_*_history (CDC)
                        silver: expectations, AUTO CDC SCD1, ROW FILTER by brand, PII column MASKs
                        gold:   fact_ad_impressions, agg_daily_performance, agg_theme_context_ctr,
                                format_lift_summary, live_context_latest, live_simulation_log
                         │
          ┌──────────────┼───────────────────────────┬─────────────────────────────┐
          ▼              ▼                           ▼                             ▼
  ML job 02: LR CTR, Ridge dwell,    Metric views (gold.mv_ad_effectiveness,   Vector Search
  LR opt-out → MLflow + UC model      gold.mv_live_simulations) ─► Genie agent   gold.brand_asset_registry_index
  glance_genad.ml.glance_engagement_model                                         (gte-large managed embeddings)
  + off-policy eval (gold.model_policy_evaluation)
                         └──────────── Databricks App (FastAPI + vanilla JS) ────────────┘
```

### What runs on each "Generate Ad Experience" (timings shown in the UI)
1. **Lakebase**: reads the user profile (segment, skin, behavior vector). The "Pull live context" button reads the latest signals for the user's city.
2. **Vector Search**: latent-space match between the live context text and the brand asset registry (filtered by brand). Unsafe components (e.g. a neon-pink swoosh recolor) are retrieved but **rejected by guardrails**, and the UI shows the rejection.
3. **Model scoring**: the trained CTR, dwell and opt-out models score **10 layout themes × 5 copy angles = 50 combos** for the state vector, in under 1 ms. The weights come from the Lakebase synced table. The objective is expected eCPM: pCTR·CPC + P(dwell≥2.5s)·CPE + CPM floor.
4. **Guardrails**: brand-blocked themes and angles (Nike: no `bold_neon`, no `discount`; Starbucks: no `energetic_sport`) are excluded. The UI shows the unconstrained winner when a guardrail changed the outcome.
5. **Copy**: Claude Haiku (FMAPI) writes copy constrained by the brand tone, banned phrases and the matched component's approved line. It is validated afterwards, with a template fallback.
6. **Compose**: a rule-based HTML/CSS template engine stitches pre-designed layers: theme background + weather FX + daypart lighting + live-score/transit widgets + skin accent.
7. **Decision log**: the decision is written to Lakebase, replicated to Delta by Lakehouse Sync, and flows through the pipeline into `gold.live_simulation_log` and `mv_live_simulations`, where Genie can see it.

### Metrics shown
* **Predicted Attention Score** (ad-blindness proxy, 0–100) = 70·(1−e^(−dwell/2.5)) + 30·min(1, pCTR/3%)
* **Ad Relevance Score** = 55% embedding similarity (context ↔ matched component, vs the generic baseline copy for static) + 45% learned theme/angle fit
* Predicted CTR lift, eCPM impact, average interaction duration (target > 2.5s), cost per engagement, opt-out reduction (target −15–20%), and a 30-day ROI projection with an impressions slider.

## Unity Catalog governance
* `governance.brand_row_filter` on silver/gold impressions: advertiser analysts only see their own brand (`governance.brand_entitlements`; `*` = platform team). The app SP and the demo owner are entitled to `*`.
* PII masks on `silver.silver_user_profiles` (`full_name`, `email`, `phone`, `device_ad_id` → pseudonymised hash). Only the account group `glance_pii_readers` sees raw values.
* Lineage end to end: Lakebase → bronze CDC → silver → gold → metric views / VS index / model.

## Runbook
```bash
P=fevm-biocon
databricks bundle deploy --profile $P
databricks bundle run glance_context_stream --params minutes=10 --profile $P   # live signals into Lakebase
databricks bundle run glance_refresh --profile $P                               # today's logs -> pipeline -> VS sync
databricks bundle run glance_ml_training --profile $P                           # retrain, new UC model version
databricks pipelines start-update a00ffbe2-89f3-4ea1-9778-3859f7d39415 --profile $P   # re-sync weights to Lakebase
# then POST /api/reload-models in the app (or restart it)
```
Rebuild from scratch: `scripts/lakebase_schema.sql` + `scripts/lakebase_seed.sql` (via `databricks psql --project glance-genad`), `src/sql/01_governance.sql`, jobs 01 → pipeline → 02, `src/sql/02_vector_registry.sql`, `03_metric_views.sql`, `04_app_grants.sql` (via `python3 scripts/run_sql.py <file> $P`), Lakehouse Sync (`databricks postgres create-cdf-config ... glance_genad bronze glance_ops`), Lakebase UC catalog `glance_genad_lakebase`, synced table, Genie space (`genie/genie_space.json`).

## Data honesty
All data is synthetic. Ad logs come from a hidden ground-truth response function (`src/jobs/generate_ad_logs.py`) in which only *context-fitting* generative layouts earn lift and mismatched ones hurt. The models are trained on those logs and recover that structure: the top weights are rain_atmos×heavy_rain, cozy_warm×cold, time_saving×just_missed_train, performance×working_out. Lift numbers are model predictions on synthetic data, not InMobi or Glance results.
