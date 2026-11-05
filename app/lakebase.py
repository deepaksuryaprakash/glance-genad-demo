"""Lakebase (Postgres) = the app's transactional backend and real-time context DB.

  glance_ops.user_profiles          - User Profile Store (behavioral vectors)
  glance_ops.context_signals        - live context stream (weather / live events / transit)
  glance_ops.creative_assets        - creative asset bucket index
  glance_ops.brand_asset_components - brand registry (mirrors what Vector Search indexes)
  glance_ops.ad_decisions           - every generated ad decision (-> Lakehouse Sync -> Delta)
  glance_serving.model_coefficients - model weights synced FROM Unity Catalog (Lakebase synced table)

Connection vars (PGHOST, PGPORT, PGDATABASE, PGUSER) come from the app's `postgres` resource;
LAKEBASE_ENDPOINT is used to mint the 1-hour OAuth password, refreshed here.
"""
import json
import os
import threading
import time

import psycopg
from databricks.sdk import WorkspaceClient
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

OPS = "glance_ops"
SERVING = os.getenv("LAKEBASE_SERVING_SCHEMA", "glance_serving")
_TOKEN_TTL_S = 40 * 60

_w = WorkspaceClient()
_token = {"value": None, "at": 0.0}
_lock = threading.Lock()


def _endpoint():
    ep = os.getenv("LAKEBASE_ENDPOINT", "")
    if "/endpoints/" not in ep:  # resource may resolve to the branch path
        ep = f"{ep.rstrip('/')}/endpoints/primary" if ep else "projects/glance-genad/branches/production/endpoints/primary"
    return ep


def _db_token():
    with _lock:
        if not _token["value"] or time.time() - _token["at"] > _TOKEN_TTL_S:
            _token["value"] = _w.postgres.generate_database_credential(endpoint=_endpoint()).token
            _token["at"] = time.time()
        return _token["value"]


class _TokenConnection(psycopg.Connection):
    @classmethod
    def connect(cls, conninfo="", **kwargs):
        kwargs["password"] = _db_token()
        return super().connect(conninfo, **kwargs)


def _user():
    return os.getenv("PGUSER") or _w.current_user.me().user_name


pool = ConnectionPool(
    conninfo=(f"host={os.getenv('PGHOST', '')} port={os.getenv('PGPORT', '5432')} "
              f"dbname={os.getenv('PGDATABASE', 'databricks_postgres')} user={_user()} sslmode=require"),
    connection_class=_TokenConnection,
    kwargs={"row_factory": dict_row, "autocommit": True},
    min_size=1, max_size=8, max_lifetime=_TOKEN_TTL_S, open=False,
)


def init():
    pool.open(wait=True, timeout=60)


def query(sql, params=None):
    t0 = time.perf_counter()
    with pool.connection() as c:
        cur = c.execute(sql, params or {})
        rows = cur.fetchall() if cur.description else []
    return rows, round((time.perf_counter() - t0) * 1000, 1)


def personas():
    rows, _ = query(f"""SELECT user_id, full_name, city, segment, preferred_skin, device_os, behavior_vector,
                               daily_unlocks, persona_blurb
                        FROM {OPS}.user_profiles WHERE is_demo_persona ORDER BY user_id""")
    return rows


def user_profile(user_id):
    rows, ms = query(f"""SELECT user_id, city, segment, preferred_skin, device_os, behavior_vector, daily_unlocks
                         FROM {OPS}.user_profiles WHERE user_id = %(u)s""", {"u": user_id})
    return (rows[0] if rows else None), ms


def live_context(city=None):
    rows, ms = query(f"""SELECT DISTINCT ON (city, signal_type) signal_id, city, signal_type, signal_key, signal_value,
                                temp_c, intensity, observed_at
                         FROM {OPS}.context_signals
                         {"WHERE city = %(c)s" if city else ""}
                         ORDER BY city, signal_type, observed_at DESC, signal_id DESC""", {"c": city})
    return rows, ms


def recent_signals(limit=12):
    rows, _ = query(f"""SELECT signal_id, city, signal_type, signal_key, signal_value, observed_at
                        FROM {OPS}.context_signals ORDER BY signal_id DESC LIMIT %(n)s""", {"n": limit})
    return rows


def coefficients():
    rows, ms = query(f"SELECT model_name, feature, weight, model_version FROM {SERVING}.model_coefficients")
    return rows, ms


def insert_decision(d):
    cols = list(d)
    query(f"INSERT INTO {OPS}.ad_decisions ({', '.join(cols)}) VALUES ({', '.join('%(' + c + ')s' for c in cols)})",
          {k: (json.dumps(v) if isinstance(v, (dict, list)) else v) for k, v in d.items()})


def recent_decisions(limit=10):
    rows, _ = query(f"""SELECT decision_id, created_at, brand, segment, weather, time_slot, user_state, live_event,
                               chosen_theme, chosen_angle, headline, pctr_static, pctr_generative,
                               ecpm_static, ecpm_generative, attention_generative, latency_ms
                        FROM {OPS}.ad_decisions ORDER BY created_at DESC LIMIT %(n)s""", {"n": limit})
    return rows


def decision_stats():
    rows, _ = query(f"""SELECT count(*) AS n,
                               avg(pctr_generative / NULLIF(pctr_static, 0) - 1) AS avg_ctr_lift,
                               avg(ecpm_generative / NULLIF(ecpm_static, 0) - 1) AS avg_ecpm_lift,
                               avg(pdwell_generative_s) AS avg_dwell,
                               avg(1 - poptout_generative / NULLIF(poptout_static, 0)) AS avg_optout_red,
                               avg(latency_ms) AS avg_latency
                        FROM {OPS}.ad_decisions""")
    return rows[0] if rows else {}
