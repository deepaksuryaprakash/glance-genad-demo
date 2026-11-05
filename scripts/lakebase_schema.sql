-- Glance GenAd: Lakebase (Postgres) transactional / context database
-- Run: databricks psql --project glance-genad --profile <p> -- -f scripts/lakebase_schema.sql
CREATE SCHEMA IF NOT EXISTS glance_ops;
SET search_path = glance_ops;

-- 1) User Profile Store: behavioral vectors + PII (masked downstream in Unity Catalog)
CREATE TABLE IF NOT EXISTS user_profiles (
  user_id            TEXT PRIMARY KEY,
  full_name          TEXT NOT NULL,
  email              TEXT NOT NULL,
  phone              TEXT NOT NULL,
  device_ad_id       TEXT NOT NULL,
  city               TEXT NOT NULL,
  segment            TEXT NOT NULL,
  preferred_skin     TEXT NOT NULL,
  device_os          TEXT NOT NULL,
  behavior_vector    JSONB NOT NULL,   -- affinity scores 0..1 per interest axis
  daily_unlocks      INT NOT NULL,
  is_demo_persona    BOOLEAN NOT NULL DEFAULT false,
  persona_blurb      TEXT,
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2) Context Database: live triggers (weather, live events, phone skin trends) streamed in
CREATE TABLE IF NOT EXISTS context_signals (
  signal_id          BIGSERIAL PRIMARY KEY,
  city               TEXT NOT NULL,
  signal_type        TEXT NOT NULL CHECK (signal_type IN ('weather', 'live_event', 'transit')),
  signal_key         TEXT NOT NULL,      -- e.g. heavy_rain / cricket_live / train_delay
  signal_value       TEXT,               -- human readable: "IND 182/4 (17.2 ov)"
  temp_c             NUMERIC(4,1),
  intensity          NUMERIC(4,2),       -- 0..1 (rain intensity, match excitement, delay severity)
  payload            JSONB,
  observed_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS context_signals_city_ts ON context_signals (city, signal_type, observed_at DESC);

-- 3) Creative Asset Bucket index: core brand assets (files live in the UC Volume)
CREATE TABLE IF NOT EXISTS creative_assets (
  asset_id           TEXT PRIMARY KEY,
  brand              TEXT NOT NULL,
  asset_type         TEXT NOT NULL CHECK (asset_type IN ('product_image', 'logo', 'baseline_copy')),
  name               TEXT NOT NULL,
  volume_path        TEXT,
  baseline_copy      TEXT,
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 4) Brand asset component registry: brand-safe creative attributes (embedded into Vector Search)
CREATE TABLE IF NOT EXISTS brand_asset_components (
  component_id       TEXT PRIMARY KEY,
  brand              TEXT NOT NULL,
  component_name     TEXT NOT NULL,
  product            TEXT NOT NULL,
  creative_attributes TEXT NOT NULL,     -- e.g. "waterproof, durable, grip"
  description        TEXT NOT NULL,      -- rich text that gets embedded
  approved_copy      TEXT NOT NULL,
  palette            TEXT NOT NULL,
  brand_safe         BOOLEAN NOT NULL,
  guardrail_note     TEXT,
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 5) Decision log written by the app on every "Generate Ad Experience"
CREATE TABLE IF NOT EXISTS ad_decisions (
  decision_id        TEXT PRIMARY KEY,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  requested_by       TEXT,
  user_id            TEXT NOT NULL,
  segment            TEXT NOT NULL,
  brand              TEXT NOT NULL,
  city               TEXT,
  weather            TEXT NOT NULL,
  time_slot          TEXT NOT NULL,
  user_state         TEXT NOT NULL,
  live_event         TEXT NOT NULL,
  phone_skin         TEXT NOT NULL,
  chosen_theme       TEXT NOT NULL,
  chosen_angle       TEXT NOT NULL,
  matched_component  TEXT,
  relevance_score    DOUBLE PRECISION,
  headline           TEXT,
  body               TEXT,
  cta                TEXT,
  copy_source        TEXT,               -- llm | template
  pctr_static        DOUBLE PRECISION,
  pctr_generative    DOUBLE PRECISION,
  pdwell_static_s    DOUBLE PRECISION,
  pdwell_generative_s DOUBLE PRECISION,
  poptout_static     DOUBLE PRECISION,
  poptout_generative DOUBLE PRECISION,
  attention_static   DOUBLE PRECISION,
  attention_generative DOUBLE PRECISION,
  ecpm_static        DOUBLE PRECISION,
  ecpm_generative    DOUBLE PRECISION,
  themes_scored      INT,
  blocked_by_guardrail INT,
  latency_ms         INT,
  scoring_detail     JSONB
);
CREATE INDEX IF NOT EXISTS ad_decisions_ts ON ad_decisions (created_at DESC);

-- Lakehouse Sync (CDC -> Unity Catalog) requires full replica identity
ALTER TABLE user_profiles          REPLICA IDENTITY FULL;
ALTER TABLE context_signals        REPLICA IDENTITY FULL;
ALTER TABLE creative_assets        REPLICA IDENTITY FULL;
ALTER TABLE brand_asset_components REPLICA IDENTITY FULL;
ALTER TABLE ad_decisions           REPLICA IDENTITY FULL;
