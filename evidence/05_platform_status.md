# Platform resource status (collected 2026-11-14 15:38 UTC)

## Lakebase Postgres (project glance-genad) - live row counts via psql

```
t                          | count 
----------------------------------------------------+-------
 user_profiles                                      | 20006
 context_signals                                    |    54
 brand_asset_components                             |    16
 ad_decisions (written by app)                      |     6
 glance_serving.model_coefficients (synced from UC) |  2020
(5 rows)
```

## Lakehouse Sync (Lakebase -> UC CDC) config

```json
[
 {
  "catalog": "glance_genad",
  "cdf_config_id": "glance_ops_to_bronze",
  "create_time": "2026-11-14T15:03:42.183Z",
  "name": "projects/glance-genad/branches/production/databases/databricks-postgres/cdf-configs/glance_ops_to_bronze",
  "postgres_schema": "glance_ops",
  "schema": "bronze"
 }
]
```

## Lakebase synced table (UC -> Lakebase) status

```json
{
 "detailed_state": "SYNCED_TABLE_ONLINE_NO_PENDING_UPDATE",
 "last_sync": {
  "delta_table_sync_info": {
   "delta_commit_time": "2026-11-14T15:09:15Z",
   "delta_commit_version": 2
  },
  "sync_end_time": "2026-11-14T15:11:04.946692Z",
  "sync_start_time": "2026-11-14T15:10:56.500613Z"
 },
 "message": "Synced table creation succeeded using Delta Live Tables: https://fe-sandbox-serverless-sandbox-5y8x8i.cloud.databricks.com#joblist/pipelines/b5520c6a-1d7a-422d-afb9-55ea3b57c312/updates/f2c82088-d2fc-4618-92bc-d115a9927273.",
 "pipeline_id": "b5520c6a-1d7a-422d-afb9-55ea3b57c312",
 "project": "projects/glance-genad",
 "unity_catalog_provisioning_state": "ACTIVE"
}
```

## Vector Search index status

```json
{
 "index_url": "fe-sandbox-serverless-sandbox-5y8x8i.cloud.databricks.com/api/2.0/vector-search/indexes/glance_genad.gold.brand_asset_registry_index",
 "indexed_row_count": 16,
 "message": "Index creation succeeded. Check latest status: https://fe-sandbox-serverless-sandbox-5y8x8i.cloud.databricks.com/explore/data/glance_genad/gold/brand_asset_registry_index",
 "ready": true
}
```

## Vector Search query result (rain + missed train context)

```json
{
 "row_count": 5,
 "data_array": [
  [
   "sb_mobile_order",
   "starbucks",
   "Mobile Order & Pay",
   true,
   0.5619686242344363
  ],
  [
   "sb_hot_latte",
   "starbucks",
   "Hot latte warm-up",
   true,
   0.4994762824265595
  ],
  [
   "nk_gtx_waterproof",
   "nike",
   "All-weather GORE-TEX",
   true,
   0.49281281312302916
  ],
  [
   "nk_zoom_speed",
   "nike",
   "Morning speed",
   true,
   0.4867687201126605
  ],
  [
   "sb_office_focus",
   "starbucks",
   "Desk-side focus",
   true,
   0.4861758486393331
  ]
 ]
}
```

## Databricks App

```json
{
 "name": "glance-genad",
 "url": "https://glance-genad-7474659149187518.aws.databricksapps.com",
 "app_status": {
  "message": "App has status: App is running",
  "state": "RUNNING"
 },
 "compute_status": {
  "message": "App compute is running.",
  "state": "ACTIVE"
 },
 "active_deployment": {
  "create_time": "2026-11-14T15:14:48Z",
  "creator": "deepak.suryaprakash@databricks.com",
  "deployment_artifacts": {
   "source_code_path": "/Workspace/Users/75e7265a-87ce-4285-bea1-3aa1a5036d48/src/01f1e03e220a1d449682a28d2d713911"
  },
  "deployment_id": "01f1e03e220a1d449682a28d2d713911",
  "mode": "SNAPSHOT",
  "source_code_path": "/Workspace/Users/deepak.suryaprakash@databricks.com/.bundle/glance_genad/files/app",
  "status": {
   "message": "App started successfully",
   "state": "SUCCEEDED"
  },
  "update_time": "2026-11-14T15:15:02Z"
 },
 "service_principal_client_id": "75e7265a-87ce-4285-bea1-3aa1a5036d48"
}
```
