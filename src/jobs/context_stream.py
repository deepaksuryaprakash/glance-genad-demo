"""Mock real-time context stream -> Lakebase glance_ops.context_signals.

Simulates IMD/BMKG weather nowcasts, live cricket/football score ticks and transit delays.
Lakehouse Sync replicates every insert to glance_genad.bronze.lb_context_signals_history (CDC),
the Lakeflow pipeline lands it in silver/gold. Params: <minutes> <interval_seconds>
"""
import json
import random
import sys
import time

import psycopg
from databricks.sdk import WorkspaceClient

MINUTES = float(sys.argv[1]) if len(sys.argv) > 1 else 5
INTERVAL = float(sys.argv[2]) if len(sys.argv) > 2 else 5
EP = "projects/glance-genad/branches/production/endpoints/primary"

w = WorkspaceClient()
host = w.postgres.get_endpoint(name=EP).status.hosts.host
user = w.current_user.me().user_name
conn = psycopg.connect(host=host, dbname="databricks_postgres", user=user, sslmode="require",
                       password=w.postgres.generate_database_credential(endpoint=EP).token, autocommit=True)

CITIES = ["Bengaluru", "Mumbai", "Delhi", "Hyderabad", "Pune", "Jakarta"]
WEATHER = {"sunny": (29, 34), "cloudy": (22, 27), "heavy_rain": (20, 26), "cold": (5, 11), "hot_humid": (32, 36)}
state = {c: random.choice(list(WEATHER)) for c in CITIES}
runs, wkts, overs = 182, 4, 17.2
goals = [1, 1]; minute = 67
t_end = time.time() + MINUTES * 60
n = 0
while time.time() < t_end:
    rows = []
    c = random.choice(CITIES)
    if random.random() < 0.3:
        state[c] = random.choice(list(WEATHER))
    wk = state[c]; lo, hi = WEATHER[wk]
    rows.append((c, "weather", wk, f"{wk.replace('_', ' ').title()}, {random.randint(lo, hi)}°C", random.randint(lo, hi),
                 round(random.random(), 2), json.dumps({"source": "mock_nowcast"})))
    # live cricket ticks in Bengaluru
    runs += random.choice([0, 1, 1, 2, 4, 6]); overs = round(overs + 0.1 if (overs * 10) % 10 < 5 else int(overs) + 1, 1)
    if random.random() < 0.08:
        wkts += 1
    rows.append(("Bengaluru", "live_event", "cricket_live", f"IND {runs}/{wkts} ({overs} ov) vs AUS", None, 0.9,
                 json.dumps({"match": "IND vs AUS T20I"})))
    minute = min(90, minute + 1)
    if random.random() < 0.05:
        goals[random.randint(0, 1)] += 1
    rows.append(("Mumbai", "live_event", "football_live", f"Mumbai City {goals[0]}-{goals[1]} Bengaluru FC ({minute}')", None, 0.75,
                 json.dumps({"match": "ISL"})))
    if random.random() < 0.4:
        delay = random.randint(0, 25)
        rows.append(("Mumbai", "transit", "train_delay", f"Western line locals running {delay} min late", None,
                     round(min(1, delay / 25), 2), json.dumps({"line": "WR Slow"})))
    with conn.cursor() as cur:
        cur.executemany("""INSERT INTO glance_ops.context_signals
                           (city, signal_type, signal_key, signal_value, temp_c, intensity, payload)
                           VALUES (%s, %s, %s, %s, %s, %s, %s)""", rows)
    n += len(rows)
    print(f"{time.strftime('%H:%M:%S')} +{len(rows)} signals (total {n})", flush=True)
    time.sleep(INTERVAL)
print("done", n)
