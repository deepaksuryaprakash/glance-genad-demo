"""Run a .sql file statement-by-statement via the Databricks CLI (no local deps).
Usage: python3 scripts/run_sql.py <file.sql> <profile> [KEY=VALUE substitutions...]"""
import os, re, subprocess, sys
WAREHOUSE = os.getenv("WAREHOUSE_ID", "e55438f8a8ce03e0")
path, profile, *subs = sys.argv[1:]
s = open(path).read()
for kv in subs:
    k, v = kv.split("=", 1); s = s.replace("${" + k + "}", v)
s = re.sub(r"--[^\n]*", "", s)
stmts, buf, q, i = [], "", None, 0
while i < len(s):  # split on ; outside quotes and $$ blocks
    if s.startswith("$$", i):
        q = None if q == "$$" else ("$$" if q is None else q); buf += "$$"; i += 2; continue
    c = s[i]
    if c == "'" and q in (None, "'"):
        q = None if q == "'" else "'"
    if c == ";" and q is None:
        if buf.strip(): stmts.append(buf.strip())
        buf = ""
    else:
        buf += c
    i += 1
if buf.strip(): stmts.append(buf.strip())
fails = 0
for st in stmts:
    import json as _j
    body = _j.dumps({"warehouse_id": WAREHOUSE, "statement": st, "wait_timeout": "50s"})
    r = subprocess.run(["databricks", "api", "post", "/api/2.0/sql/statements", "--json", body, "--profile", profile], capture_output=True, text=True)
    try:
        res = _j.loads(r.stdout); state = res["status"]["state"]
        ok = state == "SUCCEEDED"
        if not ok: r.stderr = _j.dumps(res["status"])
    except Exception:
        ok = False
    fails += not ok
    print(("ok   " if ok else "FAIL ") + " ".join(st.split())[:90])
    if not ok: print("   ", (r.stderr or r.stdout).strip()[-600:])
sys.exit(1 if fails else 0)
