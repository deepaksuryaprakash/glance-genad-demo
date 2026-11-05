"""Analytics (SQL warehouse over UC metric views) + Genie agent chat."""
import os
import time

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState

w = WorkspaceClient()
WAREHOUSE = os.getenv("DATABRICKS_WAREHOUSE_ID")
GENIE_SPACE = os.getenv("GENIE_SPACE_ID")
CATALOG = os.getenv("DEMO_CATALOG", "glance_genad")
_cache = {}


def sql(stmt, ttl=300):
    hit = _cache.get(stmt)
    if hit and time.time() - hit[0] < ttl:
        return hit[1]
    r = w.statement_execution.execute_statement(warehouse_id=WAREHOUSE, statement=stmt, wait_timeout="50s")
    while r.status.state in (StatementState.PENDING, StatementState.RUNNING):
        time.sleep(1)
        r = w.statement_execution.get_statement(r.statement_id)
    if r.status.state != StatementState.SUCCEEDED:
        raise RuntimeError(r.status.error.message if r.status.error else str(r.status.state))
    cols = [c.name for c in r.manifest.schema.columns]
    rows = [dict(zip(cols, row)) for row in (r.result.data_array or [])]
    _cache[stmt] = (time.time(), rows)
    return rows


def historical_scorecard():
    return sql(f"""
      SELECT ad_format,
             MEASURE(impressions) AS impressions, MEASURE(ctr) AS ctr,
             MEASURE(avg_interaction_duration_s) AS avg_dwell_s, MEASURE(ecpm_usd) AS ecpm,
             MEASURE(cost_per_engagement_usd) AS cpe, MEASURE(opt_out_rate) AS opt_out_rate,
             MEASURE(engaged_view_rate) AS engaged_rate
      FROM {CATALOG}.gold.mv_ad_effectiveness GROUP BY ad_format ORDER BY ad_format""")


def weekly_trend():
    return sql(f"""
      SELECT event_week, experience_group, MEASURE(ctr) AS ctr, MEASURE(ecpm_usd) AS ecpm,
             MEASURE(avg_interaction_duration_s) AS dwell, MEASURE(opt_out_rate) AS opt_out_rate
      FROM {CATALOG}.gold.mv_ad_effectiveness GROUP BY ALL ORDER BY event_week""")


def theme_by_weather(brand):
    return sql(f"""
      SELECT layout_theme, weather, MEASURE(ctr) AS ctr, MEASURE(impressions) AS impressions
      FROM {CATALOG}.gold.mv_ad_effectiveness
      WHERE ad_format = 'glance_generative' AND brand = '{brand}' GROUP BY ALL""")


def policy_eval():
    return sql(f"SELECT * FROM {CATALOG}.gold.model_policy_evaluation", ttl=600)


# ------------------------------------------------------------------ Genie
def genie_ask(question, conversation_id=None):
    if not GENIE_SPACE:
        return {"error": "GENIE_SPACE_ID not configured"}
    if conversation_id:
        msg = w.genie.create_message_and_wait(GENIE_SPACE, conversation_id, question)
    else:
        msg = w.genie.start_conversation_and_wait(GENIE_SPACE, question)
    out = {"conversation_id": msg.conversation_id, "message_id": msg.id, "status": str(msg.status), "text": None,
           "sql": None, "columns": [], "rows": [], "suggested": []}
    for a in msg.attachments or []:
        if a.text and a.text.content:
            out["text"] = (out["text"] + "\n\n" if out["text"] else "") + a.text.content
        if a.query:
            out["sql"] = a.query.query
            out["description"] = a.query.description
            try:
                qr = w.genie.get_message_attachment_query_result(GENIE_SPACE, msg.conversation_id, msg.id, a.attachment_id)
                sr = qr.statement_response
                out["columns"] = [c.name for c in sr.manifest.schema.columns]
                out["rows"] = (sr.result.data_array or [])[:50]
            except Exception as e:  # noqa: BLE001
                out["query_error"] = str(e)[:200]
        if getattr(a, "suggested_questions", None) and a.suggested_questions.questions:
            out["suggested"] = list(a.suggested_questions.questions)
    if msg.error:
        out["error"] = str(msg.error)
    return out
