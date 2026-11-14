# MLflow runs + Unity Catalog model registry (collected 2026-11-14 15:38 UTC)

Experiment id: 733621986268813

## Run engagement-models-20261114-1508 (a39eafa1095e45789e776e8ccfcc5ea1) - FINISHED

metrics: `{"ctr_auc": 0.603, "ctr_calibration_ratio": 0.9652, "ctr_logloss": 0.0677, "dwell_log_sigma": 0.4508, "dwell_mae_s": 0.6553, "n_features": 670, "n_train": 480000, "optout_auc": 0.5508, "policy_ctr_lift": 0.7051, "policy_dwell_s": 3.1304, "policy_ecpm_lift": 0.7864, "policy_optout_reduction": 0.2649}`

params: `{"ctr_model": "LogisticRegression(C=0.15)", "ctr_saturation_A_s": "(1.7, 0.7)", "dwell_model": "Ridge(alpha=20) on log dwell", "dwell_saturation_A_s": "(0.6, 1.15)", "feature_crosses": "theme/angle x context, brand x context", "opt_out_saturation_A_s": "(0.4, 1.3)", "optout_model": "LogisticRegression(C=0.15)"}`

## UC registered model glance_genad.ml.glance_engagement_model

| version | status | created (UTC) | run_id |
|---|---|---|---|
| 1 | READY | 2026-11-14 15:09 | a39eafa1095e45789e776e8ccfcc5ea1 |
