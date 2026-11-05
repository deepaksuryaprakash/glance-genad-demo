-- Silver: append-only stream of live context triggers (weather, live events, transit) from Lakebase
CREATE OR REFRESH STREAMING TABLE silver_context_signals (
  CONSTRAINT valid_signal_type EXPECT (signal_type IN ('weather', 'live_event', 'transit')) ON VIOLATION DROP ROW
)
COMMENT 'Live context triggers streamed into the Lakebase context DB and replicated by Lakehouse Sync.'
TBLPROPERTIES ('quality' = 'silver')
AS SELECT
  signal_id, city, signal_type, signal_key, signal_value,
  CAST(temp_c AS DOUBLE) AS temp_c, CAST(intensity AS DOUBLE) AS intensity,
  payload, observed_at, _pg_lsn
FROM STREAM(glance_genad.bronze.lb_context_signals_history)
WHERE _pg_change_type = 'insert';
