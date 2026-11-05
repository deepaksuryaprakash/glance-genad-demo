-- Silver: brand-safe creative component registry (SCD1 from Lakebase). Feeds the Vector Search index.
CREATE TEMPORARY VIEW brand_component_changes AS
SELECT * EXCEPT (_pg_xid, _timestamp, _sort_by)
FROM STREAM(glance_genad.bronze.lb_brand_asset_components_history)
WHERE _pg_change_type IN ('insert', 'update_postimage', 'delete');

CREATE OR REFRESH STREAMING TABLE silver_brand_asset_components
COMMENT 'Brand asset component registry: approved creative attributes, palettes and guardrails per brand.'
TBLPROPERTIES ('quality' = 'silver');

CREATE FLOW brand_components_cdc AS AUTO CDC INTO silver_brand_asset_components
FROM STREAM(brand_component_changes)
KEYS (component_id)
APPLY AS DELETE WHEN _pg_change_type = 'delete'
SEQUENCE BY _pg_lsn
COLUMNS * EXCEPT (_pg_change_type)
STORED AS SCD TYPE 1;
