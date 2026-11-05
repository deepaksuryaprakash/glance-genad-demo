-- Silver: current user profile store (SCD1 from Lakebase CDC via Lakehouse Sync). PII masked by UC column masks.
CREATE TEMPORARY VIEW user_profile_changes AS
SELECT * EXCEPT (_pg_xid, _timestamp, _sort_by)
FROM STREAM(glance_genad.bronze.lb_user_profiles_history)
WHERE _pg_change_type IN ('insert', 'update_postimage', 'delete');

CREATE OR REFRESH STREAMING TABLE silver_user_profiles (
  user_id         STRING NOT NULL,
  full_name       STRING MASK glance_genad.governance.mask_name,
  email           STRING MASK glance_genad.governance.mask_email,
  phone           STRING MASK glance_genad.governance.mask_phone,
  device_ad_id    STRING MASK glance_genad.governance.mask_ad_id,
  city            STRING,
  segment         STRING,
  preferred_skin  STRING,
  device_os       STRING,
  behavior_vector STRING COMMENT 'JSON affinity vector: sports, fitness, gaming, tech, coffee, commute, night',
  daily_unlocks   INT,
  is_demo_persona BOOLEAN,
  persona_blurb   STRING,
  updated_at      TIMESTAMP,
  _pg_lsn         BIGINT
)
COMMENT 'User Profile Store (behavioral vectors). Source of truth: Lakebase glance_ops.user_profiles. PII columns masked unless member of glance_pii_readers.'
TBLPROPERTIES ('quality' = 'silver');

CREATE FLOW user_profiles_cdc AS AUTO CDC INTO silver_user_profiles
FROM STREAM(user_profile_changes)
KEYS (user_id)
APPLY AS DELETE WHEN _pg_change_type = 'delete'
SEQUENCE BY _pg_lsn
COLUMNS * EXCEPT (_pg_change_type)
STORED AS SCD TYPE 1;
