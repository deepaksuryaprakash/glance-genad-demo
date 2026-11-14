# Job run history and logged output (collected 2026-11-14 15:38 UTC)

## Glance GenAd - 00 Mock live context stream -> Lakebase (job_id 580174488712551)

| run_id | start (UTC) | duration s | result |
|---|---|---|---|
| 386801325476006 | 2026-11-14 15:28 | 97 | SUCCESS |

**Task `stream_context` stdout (run 440558142740485, last 80 lines):**

```
15:29:00 +3 signals (total 3)
15:29:05 +4 signals (total 7)
15:29:10 +4 signals (total 11)
15:29:15 +4 signals (total 15)
15:29:20 +3 signals (total 18)
15:29:25 +3 signals (total 21)
15:29:30 +3 signals (total 24)
15:29:35 +3 signals (total 27)
15:29:40 +3 signals (total 30)
15:29:45 +4 signals (total 34)
15:29:50 +4 signals (total 38)
15:29:55 +4 signals (total 42)
done 42
```

## Glance GenAd - 01 Generate historical ad-server logs (job_id 483217132247433)

| run_id | start (UTC) | duration s | result |
|---|---|---|---|
| 808806891821918 | 2026-11-14 15:30 | 21 | SUCCESS |
| 252225057186477 | 2026-11-14 15:04 | 54 | SUCCESS |

**Task `generate_logs` stdout (run 978626811247787, last 80 lines):**

```
2026-11-14 2000 
                       ctr      dwell     opt     rev    ecpm
ad_format                                                   
glance_generative  0.0143  2733.1044  0.0132  0.0072  7.2396
standard_video     0.0127  1592.1294  0.0254  0.0053  5.3320
static_banner      0.0144   974.5991  0.0101  0.0062  6.2489
```

## Glance GenAd - 02 Train engagement models (CTR / dwell / opt-out) (job_id 247669204246282)

| run_id | start (UTC) | duration s | result |
|---|---|---|---|
| 71184997808484 | 2026-11-14 15:07 | 127 | SUCCESS |

**Task `train_models` stdout (run 183523635925152, last 80 lines):**

```
/databricks/python/lib/python3.12/site-packages/pydantic/_internal/_fields.py:161: UserWarning: Field "model_name" has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
/databricks/python/lib/python3.12/site-packages/pydantic/_internal/_fields.py:161: UserWarning: Field "model_api" has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
Exception ignored on calling ctypes callback function: <function _ThreadpoolInfo._find_modules_with_dl_iterate_phdr.<locals>.match_module_callback at 0xff914053b060>
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


2026/11/14 15:08:51 INFO mlflow.tracking.fluent: Experiment with name '/Users/deepak.suryaprakash@databricks.com/glance_genad_engagement_models' does not exist. Creating a new experiment.
[1;38;5;208mIf you are using MLflow Tracing, consider storing your traces in Unity Catalog for unlimited storage (no 100,000 trace limit), fine-grained access controls, and queryability from notebooks, SQL, and dashboards. [94mLearn more: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/trace-unity-catalog[0m


caps ctr (1.7, 0.7) opt (0.4, 1.3) dwell (0.6, 1.15)
{
  "ctr_auc": 0.6030340698049207,
  "ctr_logloss": 0.06771040379197767,
  "ctr_calibration_ratio": 0.9652200766111846,
  "dwell_mae_s": 0.6552885670800196,
  "dwell_log_sigma": 0.45078969556816867,
  "optout_auc": 0.5508005416471755,
  "n_train": 480000,
  "n_features": 670
}


🔗 View Logged Model at: https://fe-sandbox-serverless-sandbox-5y8x8i.cloud.databricks.com/ml/experiments/733621986268813/models/m-c73de827f1954bbcabe2c5c33afb5b84?o=7474659149187518
2026/11/14 15:09:00 INFO mlflow.pyfunc: Validating input example against model signature
Successfully registered model 'glance_genad.ml.glance_engagement_model'.
🔗 Created version '1' of model 'glance_genad.ml.glance_engagement_model': https://fe-sandbox-serverless-sandbox-5y8x8i.cloud.databricks.com/explore/data/models/glance_genad/ml/glance_engagement_model/version/1?o=7474659149187518


registered version 1
🏃 View run engagement-models-20261114-1508 at: https://fe-sandbox-serverless-sandbox-5y8x8i.cloud.databricks.com/ml/experiments/733621986268813/runs/a39eafa1095e45789e776e8ccfcc5ea1
🧪 View experiment at: https://fe-sandbox-serverless-sandbox-5y8x8i.cloud.databricks.com/ml/experiments/733621986268813
                                                        policy  pred_ctr  pred_dwell_s  pred_opt_out  pred_ecpm_usd  ctr_lift_vs_static  ecpm_lift_vs_static  dwell_lift_vs_static  opt_out_reduction_vs_static model_version                     evaluated_at
0                                      static_banner (control)  0.010802      0.944849      0.011157       4.898195            0.000000             0.000000              0.000000                     0.000000             1 2026-11-14 15:09:04.216169+00:00
1              generative - logged policy (rule + exploration)  0.013334      2.649164      0.009169       6.681986            0.234433             0.364173              1.803797                     0.178148             1 2026-11-14 15:09:04.216169+00:00
2  generative - optimized (argmax of 50 layout x angle combos)  0.018418      3.130400      0.008202       8.750325            0.705076             0.786439              2.313122                     0.264867             1 2026-11-14 15:09:04.216169+00:00
🏃 View run engagement-models-20261114-1508 at: https://fe-sandbox-serverless-sandbox-5y8x8i.cloud.databricks.com/ml/experiments/733621986268813/runs/a39eafa1095e45789e776e8ccfcc5ea1
🧪 View experiment at: https://fe-sandbox-serverless-sandbox-5y8x8i.cloud.databricks.com/ml/experiments/733621986268813
```

## Glance GenAd - 03 Refresh: new ad logs -> pipeline -> VS registry (job_id 819982569419071)

| run_id | start (UTC) | duration s | result |
|---|---|---|---|
| 968324252588966 | 2026-11-14 15:30 | 435 | SUCCESS |

**Task `refresh_vector_registry` stdout (run 270280570735822, last 80 lines):**

```
registry merged; index sync triggered
```

