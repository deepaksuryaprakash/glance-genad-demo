# Platform resource status (collected 2026-11-09 10:16 UTC)

## Lakebase Postgres (project glance-genad) - live row counts via psql

```
t                          | count 
----------------------------------------------------+-------
 user_profiles                                      | 20006
 context_signals                                    |    52
 brand_asset_components                             |    16
 ad_decisions (written by app)                      |    42
 glance_serving.model_coefficients (synced from UC) |  2020
(5 rows)
```

## Lakehouse Sync (Lakebase -> UC CDC) config

```json
[
 {
  "catalog": "glance_genad",
  "cdf_config_id": "glance_ops_to_bronze",
  "create_time": "2026-11-05T13:09:16.442Z",
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
   "delta_commit_time": "2026-11-05T15:43:15Z",
   "delta_commit_version": 21
  },
  "sync_end_time": "2026-11-05T15:43:56.465613Z",
  "sync_start_time": "2026-11-05T15:43:53.800692Z"
 },
 "message": "Synced table creation succeeded using Delta Live Tables: https://fe-sandbox-serverless-sandbox-8bg9w4.cloud.databricks.com#joblist/pipelines/a00ffbe2-89f3-4ea1-9778-3859f7d39415/updates/5908556e-69c1-4091-a670-181b88daa1a9.",
 "pipeline_id": "a00ffbe2-89f3-4ea1-9778-3859f7d39415",
 "project": "projects/glance-genad",
 "unity_catalog_provisioning_state": "ACTIVE"
}
```

## Vector Search index status

```json
{
 "index_url": "fe-sandbox-serverless-sandbox-8bg9w4.cloud.databricks.com/api/2.0/vector-search/indexes/glance_genad.gold.brand_asset_registry_index",
 "indexed_row_count": 16,
 "message": "Index creation succeeded. Check latest status: https://fe-sandbox-serverless-sandbox-8bg9w4.cloud.databricks.com/explore/data/glance_genad/gold/brand_asset_registry_index",
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
   0.5619147218636665
  ],
  [
   "sb_hot_latte",
   "starbucks",
   "Hot latte warm-up",
   true,
   0.4994692014966167
  ],
  [
   "nk_gtx_waterproof",
   "nike",
   "All-weather GORE-TEX",
   true,
   0.49277287725658375
  ],
  [
   "nk_zoom_speed",
   "nike",
   "Morning speed",
   true,
   0.4867271448963051
  ],
  [
   "sb_office_focus",
   "starbucks",
   "Desk-side focus",
   true,
   0.48612317512194453
  ]
 ]
}
```

## Databricks App

```json
{
 "name": "glance-genad",
 "url": "https://glance-genad-7474647312316070.aws.databricksapps.com",
 "app_status": {
  "message": "App has status: App is running",
  "state": "RUNNING"
 },
 "compute_status": {
  "message": "App compute is running.",
  "state": "ACTIVE"
 },
 "active_deployment": {
  "create_time": "2026-11-09T09:58:49Z",
  "creator": "deepak.suryaprakash@databricks.com",
  "deployment_artifacts": {
   "source_code_path": "/Workspace/Users/81f5cf7e-a15f-4710-8f01-03b28e0fe4ed/src/01f1dc24298e1d86afe67ea3948f1e81"
  },
  "deployment_id": "01f1dc24298e1d86afe67ea3948f1e81",
  "mode": "SNAPSHOT",
  "source_code_path": "/Workspace/Users/deepak.suryaprakash@databricks.com/.bundle/glance_genad/files/app",
  "status": {
   "message": "App started successfully",
   "state": "SUCCEEDED"
  },
  "update_time": "2026-11-09T09:58:58Z"
 },
 "service_principal_client_id": "81f5cf7e-a15f-4710-8f01-03b28e0fe4ed"
}
```
