-- Silver: every generative ad decision made by the app (written to Lakebase, replicated via Lakehouse Sync)
CREATE TEMPORARY VIEW ad_decision_changes AS
SELECT * EXCEPT (_pg_xid, _timestamp, _sort_by)
FROM STREAM(glance_genad.bronze.lb_ad_decisions_history)
WHERE _pg_change_type IN ('insert', 'update_postimage', 'delete');

CREATE OR REFRESH STREAMING TABLE silver_ad_decisions
COMMENT 'Real-time generative ad decisions (theme, angle, predicted CTR / dwell / opt-out / eCPM) logged by the Glance GenAd app.'
TBLPROPERTIES ('quality' = 'silver');

CREATE FLOW ad_decisions_cdc AS AUTO CDC INTO silver_ad_decisions
FROM STREAM(ad_decision_changes)
KEYS (decision_id)
APPLY AS DELETE WHEN _pg_change_type = 'delete'
SEQUENCE BY _pg_lsn
COLUMNS * EXCEPT (_pg_change_type)
STORED AS SCD TYPE 1;
