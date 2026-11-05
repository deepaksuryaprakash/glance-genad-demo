"""Train the Glance engagement models on historical ad-server logs (gold.fact_ad_impressions).

  ctr     : LogisticRegression  P(click | state, theme, angle)
  dwell   : Ridge on log(dwell_s) -> E[active interaction duration]
  opt_out : LogisticRegression  P(lock-screen opt-out or uninstall | ...)

Outputs
  * MLflow run + UC registered model  glance_genad.ml.glance_engagement_model  (pyfunc wrapping all three)
  * glance_genad.ml.model_coefficients   - sparse weights, served to the app for millisecond scoring
  * glance_genad.gold.model_policy_evaluation - off-policy estimate: logged policy vs optimized (argmax) policy
Params: <src dir> <catalog> <taxonomy.json>
"""
import json
import sys
from datetime import datetime, timezone

SRC, CATALOG, TAXONOMY = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, SRC)

import mlflow
import numpy as np
import pandas as pd
from pyspark.sql import SparkSession
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import log_loss, mean_absolute_error, roc_auc_score
from sklearn.model_selection import train_test_split

from common.features import build_features

spark = SparkSession.builder.getOrCreate()
tax = json.load(open(TAXONOMY))
COLS = ["ad_format", "brand", "segment", "weather", "time_slot", "user_state", "live_event", "phone_skin",
        "layout_theme", "copy_angle"]

df = spark.table(f"{CATALOG}.gold.fact_ad_impressions").selectExpr(*COLS, "clicked", "CAST(dwell_s AS DOUBLE) AS dwell_s", "opted_out").toPandas()
print("rows", len(df))


def feats(frame):
    return [{k: 1 for k in build_features(*r)} for r in frame[COLS].itertuples(index=False, name=None)]


tr, te = train_test_split(df, test_size=0.2, random_state=7, stratify=df["ad_format"])
vec = DictVectorizer(sparse=True)
Xtr = vec.fit_transform(feats(tr))
Xte = vec.transform(feats(te))
print("features", Xtr.shape[1])

mlflow.set_registry_uri("databricks-uc")
user = spark.sql("SELECT current_user()").first()[0]
mlflow.set_experiment(f"/Users/{user}/glance_genad_engagement_models")

with mlflow.start_run(run_name=f"engagement-models-{datetime.now():%Y%m%d-%H%M}") as run:
    ctr = LogisticRegression(C=0.15, max_iter=500).fit(Xtr, tr["clicked"])
    p = ctr.predict_proba(Xte)[:, 1]
    dwell = Ridge(alpha=20.0).fit(Xtr, np.log(tr["dwell_s"].clip(lower=0.05)))
    resid = np.log(tr["dwell_s"].clip(lower=0.05)) - dwell.predict(Xtr)
    sigma = float(np.std(resid))
    d_hat = np.exp(dwell.predict(Xte) + sigma ** 2 / 2)
    opt = LogisticRegression(C=0.15, max_iter=500).fit(Xtr, tr["opted_out"])
    po = opt.predict_proba(Xte)[:, 1]
    # ---- second stage: creative relevance saturates. z = z_base + s * A * tanh(z_creative / A), fit on holdout
    names_ = vec.get_feature_names_out()
    cmask = np.array([n.startswith(("theme=", "angle=")) for n in names_])

    def split(X, coef, b):
        zc = X[:, cmask] @ coef[cmask]
        return X[:, ~cmask] @ coef[~cmask] + b, zc

    def sat(zb, zc, A, sc):
        return zb + sc * A * np.tanh(zc / A)

    grid = [(A, sc) for A in (0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.3, 1.7, 2.5, 5.0) for sc in (0.7, 0.85, 1.0, 1.15, 1.3)]
    zb, zc = split(Xte, ctr.coef_[0], ctr.intercept_[0])
    ctr_cap = min(grid, key=lambda g: log_loss(te["clicked"], 1 / (1 + np.exp(-sat(zb, zc, *g)))))
    zb_o, zc_o = split(Xte, opt.coef_[0], opt.intercept_[0])
    opt_cap = min(grid, key=lambda g: log_loss(te["opted_out"], 1 / (1 + np.exp(-sat(zb_o, zc_o, *g)))))
    zb_d, zc_d = split(Xte, dwell.coef_, dwell.intercept_)
    ylog = np.log(te["dwell_s"].clip(lower=0.05))
    dwell_cap = min(grid, key=lambda g: float(np.mean((ylog - sat(zb_d, zc_d, *g)) ** 2)))
    print("caps ctr", ctr_cap, "opt", opt_cap, "dwell", dwell_cap)
    CAPS = {"ctr": ctr_cap, "opt_out": opt_cap, "dwell": dwell_cap}

    def predict_all(X):
        a, c = split(X, ctr.coef_[0], ctr.intercept_[0]); pc = 1 / (1 + np.exp(-sat(a, c, *ctr_cap)))
        a, c = split(X, dwell.coef_, dwell.intercept_); pdw = np.exp(sat(a, c, *dwell_cap) + sigma ** 2 / 2)
        a, c = split(X, opt.coef_[0], opt.intercept_[0]); po_ = 1 / (1 + np.exp(-sat(a, c, *opt_cap)))
        return pc, pdw, po_

    p, d_hat, po = predict_all(Xte)
    metrics = {
        "ctr_auc": roc_auc_score(te["clicked"], p), "ctr_logloss": log_loss(te["clicked"], p),
        "ctr_calibration_ratio": float(p.mean() / te["clicked"].mean()),
        "dwell_mae_s": mean_absolute_error(te["dwell_s"], d_hat), "dwell_log_sigma": sigma,
        "optout_auc": roc_auc_score(te["opted_out"], po),
        "n_train": len(tr), "n_features": Xtr.shape[1],
    }
    mlflow.log_params({f"{k}_saturation_A_s": str(v) for k, v in CAPS.items()})
    mlflow.log_params({"ctr_model": "LogisticRegression(C=0.15)", "dwell_model": "Ridge(alpha=20) on log dwell",
                       "optout_model": "LogisticRegression(C=0.15)", "feature_crosses": "theme/angle x context, brand x context"})
    mlflow.log_metrics(metrics)
    print(json.dumps(metrics, indent=2))

    class GlanceEngagementModel(mlflow.pyfunc.PythonModel):
        """Scores a state vector + (theme, angle) -> pCTR, expected dwell (s), pOptOut."""

        def __init__(self, vec, ctr, dwell, opt, sigma, caps, cmask):
            self.vec, self.ctr, self.dwell, self.opt, self.sigma, self.caps, self.cmask = vec, ctr, dwell, opt, sigma, caps, cmask

        def _z(self, X, coef, b, cap):
            A, sc = cap
            return X[:, ~self.cmask] @ coef[~self.cmask] + b + sc * A * np.tanh((X[:, self.cmask] @ coef[self.cmask]) / A)

        def predict(self, context, model_input: pd.DataFrame):
            from common.features import build_features as bf
            X = self.vec.transform([{k: 1 for k in bf(*r)} for r in model_input[COLS].itertuples(index=False, name=None)])
            return pd.DataFrame({
                "pctr": 1 / (1 + np.exp(-self._z(X, self.ctr.coef_[0], self.ctr.intercept_[0], self.caps["ctr"]))),
                "pdwell_s": np.exp(self._z(X, self.dwell.coef_, self.dwell.intercept_, self.caps["dwell"]) + self.sigma ** 2 / 2),
                "poptout": 1 / (1 + np.exp(-self._z(X, self.opt.coef_[0], self.opt.intercept_[0], self.caps["opt_out"])))})

    example = te[COLS].head(5)
    model = GlanceEngagementModel(vec, ctr, dwell, opt, sigma, CAPS, cmask)
    info = mlflow.pyfunc.log_model(
        name="glance_engagement_model", python_model=model, code_paths=[f"{SRC}/common"],
        input_example=example, signature=mlflow.models.infer_signature(example, model.predict(None, example)),
        registered_model_name=f"{CATALOG}.ml.glance_engagement_model",
        pip_requirements=["scikit-learn", "pandas", "numpy"])
    version = info.registered_model_version
    print("registered version", version)

# ---------------------------------------------------------------- export sparse weights for online scoring
names = vec.get_feature_names_out()
now = datetime.now(timezone.utc)
rows = []
for mname, w, b in (("ctr", ctr.coef_[0], ctr.intercept_[0]), ("dwell", dwell.coef_, dwell.intercept_),
                    ("opt_out", opt.coef_[0], opt.intercept_[0])):
    rows += [(mname, str(n), float(x)) for n, x in zip(names, w) if abs(x) > 1e-6]
    rows.append((mname, "__intercept__", float(b)))
rows.append(("dwell", "__sigma__", sigma))
for mname, (A, sc) in CAPS.items():
    rows += [(mname, "__sat_A__", float(A)), (mname, "__sat_scale__", float(sc))]
coef = pd.DataFrame(rows, columns=["model_name", "feature", "weight"])
coef["model_version"] = str(version)
coef["trained_at"] = now
coef["feature_id"] = coef["model_name"] + ":" + coef["feature"]
# MERGE (not overwrite) so Change Data Feed carries row-level changes to the Lakebase synced table
coef_tbl = f"{CATALOG}.ml.model_coefficients"
spark.sql(f"""CREATE TABLE IF NOT EXISTS {coef_tbl} (model_name STRING, feature STRING, weight DOUBLE, model_version STRING,
              trained_at TIMESTAMP, feature_id STRING) TBLPROPERTIES (delta.enableChangeDataFeed = true)""")
spark.createDataFrame(coef).createOrReplaceTempView("new_coef")
spark.sql(f"""MERGE INTO {coef_tbl} t USING new_coef s ON t.feature_id = s.feature_id
              WHEN MATCHED THEN UPDATE SET *
              WHEN NOT MATCHED THEN INSERT *
              WHEN NOT MATCHED BY SOURCE THEN DELETE""")
spark.sql(f"COMMENT ON TABLE {CATALOG}.ml.model_coefficients IS 'Sparse weights of the registered glance_engagement_model (v{version}). Synced to Lakebase for millisecond in-app scoring.'")

# ---------------------------------------------------------------- off-policy evaluation: optimized argmax vs logged
gen = te[te.ad_format == "glance_generative"].sample(6000, random_state=1)
themes, angles = list(tax["themes"]), list(tax["angles"])
cand = []
for i, r in enumerate(gen.itertuples(index=False)):
    bt, ba = tax["brands"][r.brand]["blocked_themes"], tax["brands"][r.brand]["blocked_angles"]
    for t in themes:
        if t in bt:
            continue
        for a in angles:
            if a in ba:
                continue
            cand.append((i, r.brand, r.segment, r.weather, r.time_slot, r.user_state, r.live_event, r.phone_skin, t, a))
cand = pd.DataFrame(cand, columns=["i", "brand", "segment", "weather", "time_slot", "user_state", "live_event", "phone_skin", "layout_theme", "copy_angle"])
cand["ad_format"] = "glance_generative"
Xc = vec.transform(feats(cand))
cand["pctr"], cand["pdwell"], cand["popt"] = predict_all(Xc)
best = cand.loc[cand.groupby("i")["pctr"].idxmax()].set_index("i")

g = gen.reset_index(drop=True)
Xl = vec.transform(feats(g))
static = g.assign(ad_format="static_banner", layout_theme="none", copy_angle="none")
Xs = vec.transform(feats(static))
cpc = g["brand"].map({b: v["cpc_usd"] for b, v in tax["brands"].items()}).values
cpe, eng_ms = tax["pricing"]["cpe_usd"], tax["pricing"]["engaged_dwell_ms"] / 1000


def p_engaged(mean_dwell):  # lognormal tail P(dwell >= 2.5s)
    from scipy.stats import norm
    mu = np.log(mean_dwell) - sigma ** 2 / 2
    return 1 - norm.cdf((np.log(eng_ms) - mu) / sigma)


def summarize(name, pctr, pdw, popt):
    ecpm = 1000 * (pctr * cpc + p_engaged(pdw) * cpe + tax['pricing']['cpm_floor_usd'] / 1000)
    return {"policy": name, "pred_ctr": float(np.mean(pctr)), "pred_dwell_s": float(np.mean(pdw)),
            "pred_opt_out": float(np.mean(popt)), "pred_ecpm_usd": float(np.mean(ecpm))}


res = pd.DataFrame([
    summarize("static_banner (control)", *predict_all(Xs)),
    summarize("generative - logged policy (rule + exploration)", *predict_all(Xl)),
    summarize("generative - optimized (argmax of 50 layout x angle combos)", best["pctr"].values, best["pdwell"].values, best["popt"].values),
])
base = res.iloc[0]
for k, out in (("pred_ctr", "ctr_lift_vs_static"), ("pred_ecpm_usd", "ecpm_lift_vs_static"), ("pred_dwell_s", "dwell_lift_vs_static")):
    res[out] = res[k] / base[k] - 1
res["opt_out_reduction_vs_static"] = 1 - res["pred_opt_out"] / base["pred_opt_out"]
res["model_version"] = str(version)
res["evaluated_at"] = now
print(res.to_string())
with mlflow.start_run(run_id=run.info.run_id):
    opt_row = res.iloc[2]
    mlflow.log_metrics({"policy_ctr_lift": opt_row.ctr_lift_vs_static, "policy_ecpm_lift": opt_row.ecpm_lift_vs_static,
                        "policy_dwell_s": opt_row.pred_dwell_s, "policy_optout_reduction": opt_row.opt_out_reduction_vs_static})
spark.createDataFrame(res).write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOG}.gold.model_policy_evaluation")
spark.sql(f"COMMENT ON TABLE {CATALOG}.gold.model_policy_evaluation IS 'Off-policy evaluation of the generative engine: static control vs logged generative policy vs model-optimized policy (predicted CTR, dwell, opt-out, eCPM).'")
