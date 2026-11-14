"""Collect text-readable execution evidence from the live workspace into evidence/.

Captures real outputs (not screenshots): job run logs, pipeline event logs, SQL query results,
MLflow metrics, model registry versions, Vector Search / Lakebase / synced-table status,
Genie conversation transcript and live app API responses.

Usage: python3 scripts/collect_evidence.py <profile> <app_url>
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

PROFILE, APP = sys.argv[1], sys.argv[2].rstrip("/")
OUT = os.path.join(os.path.dirname(__file__), "..", "evidence")
WAREHOUSE = os.getenv("WAREHOUSE_ID", "2e3fc3596c58e22d")
os.makedirs(OUT, exist_ok=True)
INDEX = []


def cli(*args, parse=True):
    r = subprocess.run(["databricks", *args, "--profile", PROFILE, "-o", "json"], capture_output=True, text=True)
    if r.returncode != 0:
        return {"error": (r.stderr or r.stdout).strip()[-800:]}
    return json.loads(r.stdout) if parse and r.stdout.strip() else r.stdout


def sql(stmt):
    body = json.dumps({"warehouse_id": WAREHOUSE, "statement": stmt, "wait_timeout": "50s"})
    r = subprocess.run(["databricks", "api", "post", "/api/2.0/sql/statements", "--json", body, "--profile", PROFILE],
                       capture_output=True, text=True)
    res = json.loads(r.stdout)
    if res["status"]["state"] != "SUCCEEDED":
        return [], [], res["status"]
    cols = [c["name"] for c in res["manifest"]["schema"]["columns"]]
    return cols, res.get("result", {}).get("data_array", []) or [], None


def md_table(cols, rows):
    if not cols:
        return "_no rows_\n"
    out = "| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n"
    for r in rows:
        out += "| " + " | ".join("" if v is None else str(v) for v in r) + " |\n"
    return out


def write(name, title, text):
    with open(os.path.join(OUT, name), "w") as f:
        f.write(text)
    INDEX.append((name, title))
    print("wrote", name)


def token():
    return cli("auth", "token")["access_token"]


def app(path, body=None):
    args = ["curl", "-s", "-H", f"Authorization: Bearer {token()}", f"{APP}{path}"]
    if body is not None:
        args[1:1] = ["-X", "POST", "-H", "Content-Type: application/json", "-d", json.dumps(body)]
    return json.loads(subprocess.run(args, capture_output=True, text=True).stdout)


now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

# ---------------------------------------------------------------- 1. SQL query results (medallion + KPIs + governance)
queries = [
    ("Row counts across the medallion (Lakebase CDC bronze -> silver -> gold)", """
      SELECT 'bronze.bronze_ad_impressions' t, count(*) n FROM glance_genad.bronze.bronze_ad_impressions UNION ALL
      SELECT 'bronze.lb_user_profiles_history (Lakehouse Sync)', count(*) FROM glance_genad.bronze.lb_user_profiles_history UNION ALL
      SELECT 'bronze.lb_context_signals_history (Lakehouse Sync)', count(*) FROM glance_genad.bronze.lb_context_signals_history UNION ALL
      SELECT 'bronze.lb_ad_decisions_history (Lakehouse Sync)', count(*) FROM glance_genad.bronze.lb_ad_decisions_history UNION ALL
      SELECT 'silver.silver_ad_impressions', count(*) FROM glance_genad.silver.silver_ad_impressions UNION ALL
      SELECT 'silver.silver_user_profiles', count(*) FROM glance_genad.silver.silver_user_profiles UNION ALL
      SELECT 'silver.silver_brand_asset_components', count(*) FROM glance_genad.silver.silver_brand_asset_components UNION ALL
      SELECT 'silver.silver_context_signals', count(*) FROM glance_genad.silver.silver_context_signals UNION ALL
      SELECT 'gold.fact_ad_impressions', count(*) FROM glance_genad.gold.fact_ad_impressions UNION ALL
      SELECT 'gold.agg_daily_performance', count(*) FROM glance_genad.gold.agg_daily_performance UNION ALL
      SELECT 'gold.live_simulation_log', count(*) FROM glance_genad.gold.live_simulation_log UNION ALL
      SELECT 'gold.brand_asset_registry (VS source)', count(*) FROM glance_genad.gold.brand_asset_registry UNION ALL
      SELECT 'ml.model_coefficients', count(*) FROM glance_genad.ml.model_coefficients"""),
    ("Historical control vs variant scorecard (gold.format_lift_summary)", """
      SELECT brand, ad_format, impressions, round(ctr*100,3) ctr_pct, round(avg_dwell_s,2) avg_dwell_s,
             round(engaged_rate*100,1) engaged_pct, round(ecpm_usd,2) ecpm_usd, round(cost_per_engagement_usd,3) cpe_usd,
             round(opt_out_rate*100,3) opt_out_pct, round(ctr_lift_vs_static*100,1) ctr_lift_pct,
             round(ecpm_lift_vs_static*100,1) ecpm_lift_pct, round(opt_out_reduction_vs_static*100,1) opt_out_reduction_pct
      FROM glance_genad.gold.format_lift_summary ORDER BY brand, ad_format"""),
    ("Off-policy evaluation of the generative engine (gold.model_policy_evaluation, written by the training job)", """
      SELECT policy, round(pred_ctr*100,2) pred_ctr_pct, round(pred_dwell_s,2) pred_dwell_s, round(pred_opt_out*100,3) pred_opt_out_pct,
             round(pred_ecpm_usd,2) pred_ecpm_usd, round(ctr_lift_vs_static*100,1) ctr_lift_pct, round(ecpm_lift_vs_static*100,1) ecpm_lift_pct,
             round(opt_out_reduction_vs_static*100,1) opt_out_reduction_pct, model_version, evaluated_at
      FROM glance_genad.gold.model_policy_evaluation"""),
    ("Metric view query: weekly KPIs, control vs variant (gold.mv_ad_effectiveness)", """
      SELECT event_week, experience_group, MEASURE(impressions) impressions, round(MEASURE(ctr)*100,3) ctr_pct,
             round(MEASURE(avg_interaction_duration_s),2) dwell_s, round(MEASURE(ecpm_usd),2) ecpm_usd,
             round(MEASURE(opt_out_rate)*100,3) opt_out_pct
      FROM glance_genad.gold.mv_ad_effectiveness GROUP BY ALL ORDER BY event_week, experience_group"""),
    ("Metric view query: best generative theme per weather (historical evidence the model learns from)", """
      SELECT weather, layout_theme, MEASURE(impressions) impressions, round(MEASURE(ctr)*100,3) ctr_pct,
             round(MEASURE(avg_interaction_duration_s),2) dwell_s
      FROM glance_genad.gold.mv_ad_effectiveness WHERE ad_format = 'glance_generative'
      GROUP BY ALL ORDER BY weather, ctr_pct DESC"""),
    ("Live app decisions flowing back through Lakebase -> Lakehouse Sync -> pipeline (gold.mv_live_simulations)", """
      SELECT brand, weather, user_state, chosen_theme, MEASURE(decisions) decisions,
             round(MEASURE(predicted_ctr_lift)*100,0) ctr_lift_pct, round(MEASURE(predicted_ecpm_lift)*100,0) ecpm_lift_pct,
             round(MEASURE(avg_predicted_dwell_s),2) dwell_s, round(MEASURE(avg_attention_score),1) attention
      FROM glance_genad.gold.mv_live_simulations GROUP BY ALL ORDER BY decisions DESC LIMIT 15"""),
    ("Top learned CTR weights (ml.model_coefficients) - model recovers context x creative interactions", """
      SELECT model_version, feature, round(weight,3) weight FROM glance_genad.ml.model_coefficients
      WHERE model_name = 'ctr' AND feature NOT LIKE '\\_\\_%' ORDER BY weight DESC LIMIT 15"""),
    ("Saturation calibration parameters exported with the model", """
      SELECT model_name, feature, weight FROM glance_genad.ml.model_coefficients WHERE feature LIKE '\\_\\_%' ORDER BY model_name, feature"""),
    ("UC column masks in effect (queried as a user NOT in glance_pii_readers)", """
      SELECT user_id, full_name, email, phone, device_ad_id, segment, city FROM glance_genad.silver.silver_user_profiles
      WHERE is_demo_persona ORDER BY user_id"""),
    ("UC row filter + masks attached to tables (information_schema)", """
      SELECT table_schema, table_name, 'row_filter' kind, filter_name AS fn, target_columns AS cols
      FROM glance_genad.information_schema.row_filters
      UNION ALL
      SELECT table_schema, table_name, 'column_mask', mask_name, column_name
      FROM glance_genad.information_schema.column_masks ORDER BY 1, 2"""),
    ("Brand entitlements driving the row filter", "SELECT principal, brand, granted_by FROM glance_genad.governance.brand_entitlements"),
    ("Live context in gold (from the Lakebase stream)", "SELECT * FROM glance_genad.gold.live_context_latest ORDER BY city, signal_type"),
]
txt = f"# SQL query results (executed {now} on SQL warehouse {WAREHOUSE})\n\n"
for title, q in queries:
    cols, rows, err = sql(q)
    txt += f"## {title}\n\n```sql\n{' '.join(q.split())}\n```\n\n" + (f"ERROR: {err}\n\n" if err else md_table(cols, rows) + "\n")
write("01_query_results.md", "SQL query results: medallion counts, KPIs, metric views, governance", txt)

# ---------------------------------------------------------------- 2. Job run logs
jobs = {j["settings"]["name"]: j["job_id"] for j in cli("jobs", "list") if "Glance GenAd" in j["settings"]["name"]}
txt = f"# Job run history and logged output (collected {now})\n\n"
for name, jid in sorted(jobs.items()):
    runs = cli("jobs", "list-runs", "--job-id", str(jid), "--limit", "5")
    txt += f"## {name} (job_id {jid})\n\n| run_id | start (UTC) | duration s | result |\n|---|---|---|---|\n"
    for r in runs if isinstance(runs, list) else []:
        st = datetime.fromtimestamp(r["start_time"] / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M")
        dur = round((r.get("end_time", r["start_time"]) - r["start_time"]) / 1000)
        txt += f"| {r['run_id']} | {st} | {dur} | {r['state'].get('result_state', r['state'].get('life_cycle_state'))} |\n"
    ok = next((r for r in (runs if isinstance(runs, list) else []) if r["state"].get("result_state") == "SUCCESS"), None)
    if ok:
        full = cli("jobs", "get-run", str(ok["run_id"]))
        for t in full.get("tasks", []):
            out = cli("jobs", "get-run-output", str(t["run_id"]))
            logs = (out.get("logs") or "").strip()
            if logs:
                lines = [l for l in logs.splitlines() if "threadpoolctl" not in l and "AttributeError: 'NoneType'" not in l]
                txt += f"\n**Task `{t['task_key']}` stdout (run {t['run_id']}, last 80 lines):**\n\n```\n" + "\n".join(lines[-80:]) + "\n```\n"
    txt += "\n"
write("02_job_runs.md", "Job runs + logged stdout (datagen, training, context stream, refresh)", txt)

# ---------------------------------------------------------------- 3. Pipeline updates + event log
pipes = [p for p in cli("pipelines", "list-pipelines") if "Glance GenAd" in p.get("name", "")]
txt = f"# Lakeflow SDP pipeline evidence (collected {now})\n\n"
for p in pipes:
    pid = p["pipeline_id"]
    ups = cli("pipelines", "list-updates", pid).get("updates", [])[:6]
    txt += f"## {p['name']} ({pid})\n\n| update_id | state | full_refresh | created (UTC) |\n|---|---|---|---|\n"
    for u in ups:
        c = datetime.fromtimestamp(u["creation_time"] / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M")
        txt += f"| {u['update_id']} | {u['state']} | {u.get('full_refresh', False)} | {c} |\n"
    ev = cli("pipelines", "list-pipeline-events", pid, "--max-results", "250")
    flows = [e for e in ev if e.get("event_type") == "flow_progress"]
    done = [e for e in flows if "COMPLETED" in e.get("message", "")]
    txt += "\n### Flow completions in the latest updates\n\n```\n" + "\n".join(f"{e['timestamp']} {e['message']}" for e in done[:40]) + "\n```\n"
    dq = []
    for e in flows:
        m = (e.get("details") or {}).get("flow_progress", {}).get("data_quality", {})
        if m.get("expectations"):
            for x in m["expectations"]:
                dq.append(f"{e['timestamp']} {x['dataset']}.{x['name']}: passed={x['passed_records']} failed={x['failed_records']}")
            if "dropped_records" in m:
                dq.append(f"    dropped_records={m['dropped_records']}")
    cols, rows, err = sql(f"""
      SELECT timestamp, origin.flow_name AS flow, e.dataset, e.name AS expectation, e.passed_records, e.failed_records
      FROM (SELECT timestamp, origin, explode(from_json(details:flow_progress.data_quality.expectations,
              'array<struct<name:string,dataset:string,passed_records:bigint,failed_records:bigint>>')) AS e
            FROM event_log('{pid}') WHERE event_type = 'flow_progress' AND details:flow_progress.data_quality IS NOT NULL)
      ORDER BY timestamp DESC LIMIT 30""")
    txt += "\n### Data-quality expectation results (from event_log() SQL)\n\n" + (f"ERROR {err}" if err else md_table(cols, rows)) + "\n"
write("03_pipeline_runs.md", "Lakeflow pipeline updates, flow completions, expectation results", txt)

# ---------------------------------------------------------------- 4. MLflow + UC model registry
exp = cli("experiments", "get-by-name", f"/Users/{cli('current-user', 'me')['userName']}/glance_genad_engagement_models")
eid = exp.get("experiment", {}).get("experiment_id")
runs = cli("experiments", "search-runs", "--json", json.dumps({"experiment_ids": [eid], "max_results": 8})) if eid else {}
txt = f"# MLflow runs + Unity Catalog model registry (collected {now})\n\nExperiment id: {eid}\n\n"
for r in (runs if isinstance(runs, list) else runs.get("runs", [])):
    m = {x["key"]: round(x["value"], 4) for x in r.get("data", {}).get("metrics", [])}
    pr = {x["key"]: x["value"] for x in r.get("data", {}).get("params", [])}
    txt += f"## Run {r['info']['run_name']} ({r['info']['run_id']}) - {r['info']['status']}\n\nmetrics: `{json.dumps(m)}`\n\nparams: `{json.dumps(pr)}`\n\n"
mv = cli("model-versions", "list", "glance_genad.ml.glance_engagement_model")
txt += "## UC registered model glance_genad.ml.glance_engagement_model\n\n| version | status | created (UTC) | run_id |\n|---|---|---|---|\n"
for v in (mv if isinstance(mv, list) else mv.get("model_versions", [])):
    c = datetime.fromtimestamp(v["created_at"] / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M")
    txt += f"| {v['version']} | {v.get('status')} | {c} | {v.get('run_id')} |\n"
write("04_mlflow_models.md", "MLflow run metrics/params + UC model versions", txt)

# ---------------------------------------------------------------- 5. Platform resource status
vs = cli("vector-search-indexes", "get-index", "glance_genad.gold.brand_asset_registry_index")
_vq = subprocess.run(["databricks", "api", "post", "/api/2.0/vector-search/indexes/glance_genad.gold.brand_asset_registry_index/query",
                     "--profile", PROFILE, "--json", json.dumps({
    "query_text": "Heavy Rain weather, 8 AM Rush Hour, the user has just missed a train. Daily Commuter audience.",
    "columns": ["component_id", "brand", "component_name", "brand_safe"], "num_results": 5})], capture_output=True, text=True)
vsq = json.loads(_vq.stdout) if _vq.stdout.strip() else {"error": _vq.stderr[-500:]}
syn = cli("postgres", "get-synced-table", "synced_tables/glance_genad_lakebase.glance_serving.model_coefficients")
cdf = cli("postgres", "list-cdf-configs", "projects/glance-genad/branches/production/databases/databricks-postgres")
appinfo = cli("apps", "get", "glance-genad")
pg = subprocess.run(["databricks", "psql", "--project", "glance-genad", "--profile", PROFILE, "--", "-c",
                     "SELECT 'user_profiles' t, count(*) FROM glance_ops.user_profiles UNION ALL "
                     "SELECT 'context_signals', count(*) FROM glance_ops.context_signals UNION ALL "
                     "SELECT 'brand_asset_components', count(*) FROM glance_ops.brand_asset_components UNION ALL "
                     "SELECT 'ad_decisions (written by app)', count(*) FROM glance_ops.ad_decisions UNION ALL "
                     "SELECT 'glance_serving.model_coefficients (synced from UC)', count(*) FROM glance_serving.model_coefficients"],
                    capture_output=True, text=True).stdout
txt = f"# Platform resource status (collected {now})\n\n"
txt += "## Lakebase Postgres (project glance-genad) - live row counts via psql\n\n```\n" + pg.strip() + "\n```\n\n"
txt += "## Lakehouse Sync (Lakebase -> UC CDC) config\n\n```json\n" + json.dumps(cdf, indent=1)[:1500] + "\n```\n\n"
txt += "## Lakebase synced table (UC -> Lakebase) status\n\n```json\n" + json.dumps(syn.get("status", syn), indent=1)[:1500] + "\n```\n\n"
txt += "## Vector Search index status\n\n```json\n" + json.dumps(vs.get("status", vs), indent=1) + "\n```\n\n"
txt += "## Vector Search query result (rain + missed train context)\n\n```json\n" + json.dumps(vsq.get("result", vsq), indent=1)[:2500] + "\n```\n\n"
txt += "## Databricks App\n\n```json\n" + json.dumps({k: appinfo.get(k) for k in ("name", "url", "app_status", "compute_status", "active_deployment", "service_principal_client_id")}, indent=1, default=str)[:2500] + "\n```\n"
write("05_platform_status.md", "Lakebase, Lakehouse Sync, synced table, Vector Search, App status", txt)

# ---------------------------------------------------------------- 6. Live app API responses + Genie transcript
txt = f"# Live app API responses (collected {now} from {APP})\n\n## /api/health\n\n```json\n{json.dumps(app('/api/health'), indent=1)}\n```\n\n"
scen = [
    {"user_id": "U90002", "brand": "starbucks", "weather": "heavy_rain", "time_slot": "morning_rush", "user_state": "just_missed_train", "live_event": "none"},
    {"user_id": "U90001", "brand": "nike", "weather": "sunny", "time_slot": "morning_rush", "user_state": "working_out", "live_event": "none"},
    {"user_id": "U90005", "brand": "nike", "weather": "cloudy", "time_slot": "late_night", "user_state": "relaxing_at_home", "live_event": "cricket_live"},
    {"user_id": "U90004", "brand": "nike", "weather": "hot_humid", "time_slot": "evening", "user_state": "relaxing_at_home", "live_event": "esports_final"},
]
for s in scen:
    r = app("/api/generate", s)
    summary = {
        "request": s, "decision_id": r.get("decision_id"), "model_version": r.get("model_version"), "model_source": r.get("model_source"),
        "winner": {"theme": r["generative"]["theme"], "angle": r["generative"]["angle"], "layers": r["generative"]["layers"]},
        "copy": r["generative"]["copy"], "copy_source": r["generative"]["copy_source"],
        "matched_component": (r.get("component") or {}).get("component_id"),
        "rejected_by_guardrail": [c["component_id"] for c in r.get("rejected_components", [])],
        "blocked_combos": r["guardrail"]["blocked_combos"],
        "static": {k: round(r["static"][k], 4) for k in ("pctr", "pdwell_s", "poptout", "ecpm", "attention", "relevance")},
        "generative": {k: round(r["generative"][k], 4) for k in ("pctr", "pdwell_s", "poptout", "ecpm", "attention", "relevance")},
        "lift": {k: round(v, 4) for k, v in r["lift"].items()},
        "leaderboard_top5": [{"theme": c["theme"], "angle": c["angle"], "pctr": round(c["pctr"], 4), "ecpm": round(c["ecpm"], 2), "blocked": c["blocked"]} for c in r["leaderboard"][:5]],
        "why": r["why"], "timings_ms": r["timings"],
    }
    txt += f"## POST /api/generate - {s['brand']} / {s['weather']} / {s['time_slot']} / {s['user_state']} / {s['live_event']}\n\n```json\n{json.dumps(summary, indent=1)}\n```\n\n"
write("06_app_api_responses.md", "Live app /api/generate responses (real model + VS + LLM output)", txt)

txt = f"# Genie agent transcript via the app (collected {now})\n\n"
conv = None
for q in ["What is the CTR lift of generative vs static banner by brand?",
          "Which layout theme has the highest CTR in heavy rain?",
          "Which user segment has the biggest reduction in opt-out rate with generative ads?"]:
    r = app("/api/genie", {"question": q, "conversation_id": conv})
    conv = r.get("conversation_id") or conv
    txt += f"## Q: {q}\n\n**Answer:** {r.get('text')}\n\n```sql\n{r.get('sql')}\n```\n\n" + md_table(r.get("columns", []), r.get("rows", [])[:15]) + "\n"
write("07_genie_transcript.md", "Genie agent Q&A with generated SQL and result rows", txt)

# ---------------------------------------------------------------- index
with open(os.path.join(OUT, "README.md"), "w") as f:
    f.write(f"# Execution evidence\n\nCollected {now} from workspace profile `{PROFILE}` by `scripts/collect_evidence.py`.\n"
            "Everything here is real command / query / API output captured as text from the running build.\n\n")
    for n, t in INDEX:
        f.write(f"- [{n}]({n}) - {t}\n")
print("done")
