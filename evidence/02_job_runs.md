# Job run history and logged output (collected 2026-11-09 10:16 UTC)

## Glance GenAd - 00 Mock live context stream -> Lakebase (job_id 84714594672098)

| run_id | start (UTC) | duration s | result |
|---|---|---|---|
| 488445459575586 | 2026-11-05 15:15 | 141 | SUCCESS |

**Task `stream_context` stdout (run 164284413911627, last 80 lines):**

```
15:16:54 +3 signals (total 3)
15:16:59 +3 signals (total 6)
15:17:04 +3 signals (total 9)
15:17:09 +3 signals (total 12)
15:17:14 +4 signals (total 16)
15:17:19 +3 signals (total 19)
15:17:24 +4 signals (total 23)
15:17:29 +4 signals (total 27)
15:17:34 +4 signals (total 31)
15:17:39 +3 signals (total 34)
15:17:44 +3 signals (total 37)
15:17:49 +3 signals (total 40)
done 40
```

## Glance GenAd - 01 Generate historical ad-server logs (job_id 539355431215852)

| run_id | start (UTC) | duration s | result |
|---|---|---|---|
| 979192536783096 | 2026-11-05 15:42 | 21 | SUCCESS |
| 523114282219893 | 2026-11-05 15:36 | 64 | SUCCESS |
| 723945290552828 | 2026-11-05 15:20 | 62 | SUCCESS |
| 634275329040047 | 2026-11-05 13:40 | 63 | SUCCESS |
| 146963217465541 | 2026-11-05 13:22 | 63 | SUCCESS |

**Task `generate_logs` stdout (run 359652104177794, last 80 lines):**

```
2026-11-05 2000 
                       ctr      dwell     opt     rev    ecpm
ad_format                                                   
glance_generative  0.0157  2715.3993  0.0067  0.0068  6.8443
standard_video     0.0177  1644.6354  0.0177  0.0082  8.1823
static_banner      0.0155   963.4459  0.0098  0.0061  6.1423
```

## Glance GenAd - 02 Train engagement models (CTR / dwell / opt-out) (job_id 312704288761067)

| run_id | start (UTC) | duration s | result |
|---|---|---|---|
| 588477521403727 | 2026-11-05 15:39 | 105 | SUCCESS |
| 675484286187073 | 2026-11-05 15:32 | 109 | SUCCESS |
| 976533841312271 | 2026-11-05 15:23 | 103 | SUCCESS |
| 872346716879605 | 2026-11-05 13:43 | 106 | SUCCESS |
| 598388420764712 | 2026-11-05 13:36 | 110 | SUCCESS |

**Task `train_models` stdout (run 621101834332783, last 80 lines):**

```
/databricks/python/lib/python3.12/site-packages/pydantic/_internal/_fields.py:161: UserWarning: Field "model_name" has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
/databricks/python/lib/python3.12/site-packages/pydantic/_internal/_fields.py:161: UserWarning: Field "model_api" has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
Exception ignored on calling ctypes callback function: <function _ThreadpoolInfo._find_modules_with_dl_iterate_phdr.<locals>.match_module_callback at 0xff72906f9800>
Traceback (most recent call last):
    self._make_module_from_path(filepath)
    module = module_class(filepath, prefix, user_api, internal_api)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    self.version = self.get_version()
                   ^^^^^^^^^^^^^^^^^^
    config = get_config().split()
             ^^^^^^^^^^^^^^^^^^


rows 600000
features 670


[1;38;5;208mIf you are using MLflow Tracing, you can migrate your traces to Unity Catalog for unlimited storage, fine-grained access controls, and queryability from notebooks, SQL, and dashboards. [94mLearn more: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/migrate-traces-to-uc[0m


caps ctr (0.6, 0.85) opt (0.3, 1.3) dwell (0.5, 1.15)
{
  "ctr_auc": 0.6111845365872409,
  "ctr_logloss": 0.06491811800290431,
  "ctr_calibration_ratio": 1.0229299435449206,
  "dwell_mae_s": 0.653370371406242,
  "dwell_log_sigma": 0.4506188182446385,
  "optout_auc": 0.528401672537899,
  "n_train": 480000,
  "n_features": 670
}


🔗 View Logged Model at: https://fe-sandbox-serverless-sandbox-8bg9w4.cloud.databricks.com/ml/experiments/3324159271457320/models/m-9f47e135882a40eab9b7814dba022e47?o=7474647312316070
2026/11/05 15:40:24 INFO mlflow.pyfunc: Validating input example against model signature
Registered model 'glance_genad.ml.glance_engagement_model' already exists. Creating a new version of this model...
🔗 Created version '7' of model 'glance_genad.ml.glance_engagement_model': https://fe-sandbox-serverless-sandbox-8bg9w4.cloud.databricks.com/explore/data/models/glance_genad/ml/glance_engagement_model/version/7?o=7474647312316070


registered version 7
🏃 View run engagement-models-20261105-1540 at: https://fe-sandbox-serverless-sandbox-8bg9w4.cloud.databricks.com/ml/experiments/3324159271457320/runs/3721cc600624445e850c33eb0f42bbaf
🧪 View experiment at: https://fe-sandbox-serverless-sandbox-8bg9w4.cloud.databricks.com/ml/experiments/3324159271457320
                                                        policy  pred_ctr  pred_dwell_s  pred_opt_out  pred_ecpm_usd  ctr_lift_vs_static  ecpm_lift_vs_static  dwell_lift_vs_static  opt_out_reduction_vs_static model_version                     evaluated_at
0                                      static_banner (control)  0.011028      0.944989      0.010981       4.961758            0.000000             0.000000              0.000000                     0.000000             7 2026-11-05 15:40:28.446752+00:00
1              generative - logged policy (rule + exploration)  0.013659      2.611668      0.009576       6.770274            0.238545             0.364491              1.763701                     0.127923             7 2026-11-05 15:40:28.446752+00:00
2  generative - optimized (argmax of 50 layout x angle combos)  0.019574      3.096095      0.008853       9.104457            0.774897             0.834926              2.276329                     0.193758             7 2026-11-05 15:40:28.446752+00:00
🏃 View run engagement-models-20261105-1540 at: https://fe-sandbox-serverless-sandbox-8bg9w4.cloud.databricks.com/ml/experiments/3324159271457320/runs/3721cc600624445e850c33eb0f42bbaf
🧪 View experiment at: https://fe-sandbox-serverless-sandbox-8bg9w4.cloud.databricks.com/ml/experiments/3324159271457320
```

## Glance GenAd - 03 Refresh: new ad logs -> pipeline -> VS registry (job_id 558331104149900)

| run_id | start (UTC) | duration s | result |
|---|---|---|---|
| 317224549257005 | 2026-11-05 15:42 | 151 | SUCCESS |

**Task `refresh_vector_registry` stdout (run 127779404026812, last 80 lines):**

```
registry merged; index sync triggered
```

