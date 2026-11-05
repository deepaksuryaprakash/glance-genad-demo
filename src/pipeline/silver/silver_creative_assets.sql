-- Silver: creative asset bucket index (files live in /Volumes/glance_genad/raw/creative_assets)
CREATE TEMPORARY VIEW creative_asset_changes AS
SELECT * EXCEPT (_pg_xid, _timestamp, _sort_by)
FROM STREAM(glance_genad.bronze.lb_creative_assets_history)
WHERE _pg_change_type IN ('insert', 'update_postimage', 'delete');

CREATE OR REFRESH STREAMING TABLE silver_creative_assets
COMMENT 'Core brand assets (raw product image, logo, baseline copy) registered in Lakebase.'
TBLPROPERTIES ('quality' = 'silver');

CREATE FLOW creative_assets_cdc AS AUTO CDC INTO silver_creative_assets
FROM STREAM(creative_asset_changes)
KEYS (asset_id)
APPLY AS DELETE WHEN _pg_change_type = 'delete'
SEQUENCE BY _pg_lsn
COLUMNS * EXCEPT (_pg_change_type)
STORED AS SCD TYPE 1;
