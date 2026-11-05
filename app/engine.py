"""The Glance generative engine: state vector -> scored layouts -> brand-safe creative -> layout spec.

Pipeline per request (all timed and returned to the UI):
  1. context    : user profile + live context read from Lakebase
  2. retrieve   : Vector Search over the brand asset registry (latent-space match context <-> brand-safe components)
  3. score      : trained CTR / dwell / opt-out models score 10 layout themes x 5 copy angles (50 combos)
  4. guardrail  : brand guidelines block unsafe themes / angles / components
  5. copy       : LLM (FMAPI) writes on-brand copy constrained by the matched component; template fallback
  6. compose    : layered HTML/CSS layout spec (theme + weather + daypart + live widget + skin)
"""
import concurrent.futures as cf
import json
import math
import os
import re
import time
from pathlib import Path

from databricks.sdk import WorkspaceClient

from features import build_features

TAX = json.loads((Path(__file__).parent / "taxonomy.json").read_text())
VS_INDEX = os.getenv("VS_INDEX", "glance_genad.gold.brand_asset_registry_index")
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "databricks-claude-haiku-5-5")
EMBED_ENDPOINT = os.getenv("EMBED_ENDPOINT", "databricks-gte-large-en")
w = WorkspaceClient()
_pool = cf.ThreadPoolExecutor(max_workers=8)


# ------------------------------------------------------------------ model weights (synced from UC -> Lakebase)
class Models:
    def __init__(self):
        self.w = {"ctr": {}, "dwell": {}, "opt_out": {}}
        self.version = None
        self.source = None
        self.load_ms = None

    def load(self, rows, source, ms):
        w = {"ctr": {}, "dwell": {}, "opt_out": {}}
        for r in rows:
            w[r["model_name"]][r["feature"]] = float(r["weight"])
            self.version = r.get("model_version")
        self.w, self.source, self.load_ms = w, source, ms

    @property
    def ready(self):
        return bool(self.w["ctr"])

    def _lin(self, m, feats):
        """Linear score with a saturating creative-fit term (2nd-stage calibration fitted in training):
        z = intercept + sum(context weights) + s * A * tanh(sum(theme/angle weights) / A)"""
        ws = self.w[m]
        base = ws.get("__intercept__", 0.0) + sum(ws.get(f, 0.0) for f in feats if not f.startswith(("theme=", "angle=")))
        zc = sum(ws.get(f, 0.0) for f in feats if f.startswith(("theme=", "angle=")))
        A, sc = ws.get("__sat_A__"), ws.get("__sat_scale__", 1.0)
        return base + (sc * A * math.tanh(zc / A) if A else zc)

    def score(self, feats):
        z = self._lin("ctr", feats)
        pctr = 1 / (1 + math.exp(-z))
        sigma = self.w["dwell"].get("__sigma__", 0.45)
        mu = self._lin("dwell", feats)
        pdwell = math.exp(mu + sigma ** 2 / 2)
        thr = TAX["pricing"]["engaged_dwell_ms"] / 1000
        p_eng = 0.5 * math.erfc((math.log(thr) - mu) / (sigma * math.sqrt(2)))
        popt = 1 / (1 + math.exp(-self._lin("opt_out", feats)))
        return pctr, pdwell, p_eng, popt

    def contributions(self, feats, prefix=("theme=", "angle=")):
        ws = self.w["ctr"]
        out = [(f, ws.get(f, 0.0)) for f in feats if f.startswith(prefix)]
        return sorted(out, key=lambda x: -x[1])


MODELS = Models()


def ecpm(brand, pctr, p_eng):
    b = TAX["brands"][brand]
    return 1000 * (pctr * b["cpc_usd"] + p_eng * TAX["pricing"]["cpe_usd"]) + TAX["pricing"]["cpm_floor_usd"]


def attention_score(pdwell, pctr):
    """Predicted Attention Score (0-100): proxy for ad blindness. 70% from expected active dwell
    (saturating at ~2.5s scale), 30% from tap propensity (saturating at 3% CTR)."""
    return round(70 * (1 - math.exp(-pdwell / 2.5)) + 30 * min(1.0, pctr / 0.03), 1)


def label(f):
    parts = []
    for p in f.split("|"):
        k, v = p.split("=", 1)
        dims = {"theme": TAX["themes"].get(v, {}).get("label") if k == "theme" else None,
                "angle": TAX["angles"].get(v) if k == "angle" else None,
                "weather": TAX["weather"].get(v), "time_slot": TAX["time_slot"].get(v),
                "user_state": TAX["user_state"].get(v), "live_event": TAX["live_event"].get(v),
                "segment": TAX["segments"].get(v), "phone_skin": TAX["phone_skin"].get(v),
                "brand": TAX["brands"].get(v, {}).get("display") if k == "brand" else None}
        parts.append(dims.get(k) or v)
    return " × ".join(parts)


# ------------------------------------------------------------------ vector search + embeddings
def context_text(s):
    ev = "" if s["live_event"] == "none" else f", {TAX['live_event'][s['live_event']]} happening now"
    return (f"{TAX['weather'][s['weather']]} weather, {TAX['time_slot'][s['time_slot']]}, the user has "
            f"{TAX['user_state'][s['user_state']].lower()}{ev}. {TAX['segments'][s['segment']]} audience.")


def retrieve_components(s):
    """Latent-space matching: nearest brand components to the live context (brand filter, no safety filter
    so the UI can show what the guardrail rejected)."""
    res = w.vector_search_indexes.query_index(
        index_name=VS_INDEX, query_text=context_text(s), num_results=5,
        columns=["component_id", "component_name", "product", "creative_attributes", "approved_copy", "palette",
                 "brand_safe", "guardrail_note", "embedding_text"],
        filters_json=json.dumps({"brand": s["brand"]}))
    cols = [c.name for c in res.manifest.columns]
    return [dict(zip(cols, r)) for r in (res.result.data_array or [])]


def embed(texts):
    r = w.serving_endpoints.query(name=EMBED_ENDPOINT, input=texts)
    return [d.embedding for d in r.data]


def cos(a, b):
    na = math.sqrt(sum(x * x for x in a)); nb = math.sqrt(sum(x * x for x in b))
    return sum(x * y for x, y in zip(a, b)) / (na * nb)


# ------------------------------------------------------------------ copy generation
HOOKS = {
    "weather": {"heavy_rain": "Stuck in the rain?", "cold": "Chilly out there?", "sunny": "Sun's out.",
                "hot_humid": "Melting in the heat?", "cloudy": "Grey skies?"},
    "user_state": {"just_missed_train": "Just missed your train?", "working_out": "Mid-workout?",
                   "relaxing_at_home": "Couch mode on?", "at_office": "Back-to-back meetings?", "commuting": "On the move?"},
    "live_event": {"cricket_live": "Kohli's on 74*.", "football_live": "1-1 at 67'.", "city_marathon": "Race weekend.",
                   "esports_final": "Map 3 is live."},
}
CTAS = {"time_saving": "Tap to pre-order", "comfort": "Treat yourself", "performance": "Gear up",
        "social_fomo": "Join the moment", "discount": "Claim offer"}


def template_copy(s, comp, angle):
    hook = HOOKS["live_event"].get(s["live_event"]) or (
        HOOKS["user_state"][s["user_state"]] if s["user_state"] in ("just_missed_train", "working_out")
        else HOOKS["weather"][s["weather"]])
    if s["brand"] == "starbucks" and s["weather"] in ("heavy_rain", "cold") and s["user_state"] in ("just_missed_train", "commuting"):
        return {"headline": hook, "body": "Warm up with a hot Latte at the next station.", "cta": "Tap to pre-order"}
    return {"headline": hook, "body": comp["approved_copy"] if comp else TAX["brands"][s["brand"]]["baseline_copy"]["body"],
            "cta": CTAS.get(angle, "Learn more")}


def llm_copy(s, comp, theme, angle):
    b = TAX["brands"][s["brand"]]
    sys_prompt = (
        f"You write lock-screen ad copy for {b['display']} on Glance. Brand tone: {b['tone']} "
        f"Hard rules: {b['forbidden']} Never use these words: {', '.join(b['banned_phrases'])}. "
        "Output ONLY compact JSON: {\"headline\": <=6 words, \"body\": <=14 words, \"cta\": <=3 words}. "
        "Reference the user's live moment naturally, feature the given product benefit, no hashtags, no emojis.")
    user_prompt = (
        f"Live moment: {context_text(s)} Layout theme: {TAX['themes'][theme]['label']} ({TAX['themes'][theme]['desc']}). "
        f"Copy angle: {TAX['angles'][angle]}. Product: {comp['product']} - {comp['creative_attributes']}. "
        f"Approved brand line you may adapt: \"{comp['approved_copy']}\".")
    r = w.api_client.do("POST", f"/serving-endpoints/{LLM_ENDPOINT}/invocations", body={
        "max_tokens": 1000, "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}]})
    txt = r["choices"][0]["message"].get("content") or ""
    if isinstance(txt, str) and txt.lstrip().startswith("[{"):  # reasoning models return JSON-encoded content blocks
        try:
            txt = json.loads(txt)
        except ValueError:
            pass
    if isinstance(txt, list):  # keep only the text blocks (drop reasoning)
        txt = [p for p in txt if not isinstance(p, dict) or p.get("type") in (None, "text")]
        txt = "".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in txt)
    m = re.search(r"\{.*\}", txt, re.S)
    out = json.loads(m.group(0))
    return {k: str(out[k]).strip() for k in ("headline", "body", "cta")}


def brand_safe_copy(brand, c):
    text = " ".join(c.values()).lower()
    hits = [p for p in TAX["brands"][brand]["banned_phrases"] if p in text]
    return not hits and len(c["headline"]) <= 60 and len(c["body"]) <= 120, hits


# ------------------------------------------------------------------ layout composition
def layers_for(s, theme):
    layers = [f"theme-{theme}"]
    layers.append({"heavy_rain": "fx-rain", "cold": "fx-frost", "sunny": "fx-sunrays", "hot_humid": "fx-heat",
                   "cloudy": "fx-clouds"}[s["weather"]])
    layers.append({"morning_rush": "light-morning", "midday": "light-day", "evening": "light-evening",
                   "late_night": "light-night"}[s["time_slot"]])
    if s["live_event"] != "none":
        layers.append("widget-live")
    if s["user_state"] in ("just_missed_train", "commuting"):
        layers.append("widget-transit")
    layers.append(f"skin-{s['phone_skin']}")
    return layers


def generate(s, profile):
    """s: dict(brand, segment, weather, time_slot, user_state, live_event, phone_skin, user_id, city)"""
    t = {}
    t0 = time.perf_counter()
    brand = s["brand"]
    vs_future = _pool.submit(retrieve_components, s)

    # ---- score the static control
    f_static = build_features("static_banner", brand, s["segment"], s["weather"], s["time_slot"], s["user_state"],
                              s["live_event"], s["phone_skin"])
    sc, sd, se, so = MODELS.score(f_static)
    static = {"pctr": sc, "pdwell_s": sd, "p_engaged": se, "poptout": so, "ecpm": ecpm(brand, sc, se),
              "attention": attention_score(sd, sc)}

    # ---- score 10 themes x 5 angles with the trained models
    t1 = time.perf_counter()
    bcfg = TAX["brands"][brand]
    combos = []
    for theme in TAX["themes"]:
        for angle in TAX["angles"]:
            f = build_features("glance_generative", brand, s["segment"], s["weather"], s["time_slot"],
                               s["user_state"], s["live_event"], s["phone_skin"], theme, angle)
            pc, pdw, pe, po = MODELS.score(f)
            blocked = ("theme" if theme in bcfg["blocked_themes"] else "angle" if angle in bcfg["blocked_angles"] else None)
            combos.append({"theme": theme, "angle": angle, "pctr": pc, "pdwell_s": pdw, "p_engaged": pe, "poptout": po,
                           "ecpm": ecpm(brand, pc, pe), "blocked": blocked, "_f": f})
    t["score_ms"] = round((time.perf_counter() - t1) * 1000, 2)
    safe = [c for c in combos if not c["blocked"]]
    best = max(safe, key=lambda c: c["ecpm"])
    best_raw = max(combos, key=lambda c: c["ecpm"])
    leaderboard = []
    for theme in TAX["themes"]:
        cands = [c for c in combos if c["theme"] == theme]
        top = max([c for c in cands if not c["blocked"]] or cands, key=lambda c: c["ecpm"])
        leaderboard.append({k: v for k, v in top.items() if k != "_f"} | {
            "label": TAX["themes"][theme]["label"], "theme_blocked": theme in bcfg["blocked_themes"],
            "winner": top is best})
    leaderboard.sort(key=lambda c: -c["ecpm"])
    why = [{"feature": label(f), "weight": round(wt, 3)} for f, wt in MODELS.contributions(best["_f"])[:6] if wt > 0]
    against = [{"feature": label(f), "weight": round(wt, 3)} for f, wt in MODELS.contributions(best["_f"])[::-1][:3] if wt < 0]

    # ---- latent-space match (VS) + re-score with embeddings on one scale
    t2 = time.perf_counter()
    try:
        comps = vs_future.result(timeout=10)
        vs_error = None
    except Exception as e:  # noqa: BLE001
        comps, vs_error = [], str(e)[:200]
    t["vector_search_ms"] = round((time.perf_counter() - t2) * 1000, 1)
    safe_comps = [c for c in comps if str(c.get("brand_safe")).lower() in ("true", "1")]
    rejected = [c for c in comps if c not in safe_comps]
    comp = safe_comps[0] if safe_comps else None
    rel_gen, rel_static, sims = 0.0, 0.0, []
    t3 = time.perf_counter()
    try:
        texts = [context_text(s), " ".join(bcfg["baseline_copy"].values())] + [c["embedding_text"] for c in comps]
        e = embed(texts)
        sims = [round(cos(e[0], x), 3) for x in e[2:]]
        for c, sim in zip(comps, sims):
            c["similarity"] = sim
        base_sim = cos(e[0], e[1])
        top_sim = comp["similarity"] if comp else base_sim
        fit = sum(wt for _, wt in MODELS.contributions(best["_f"]))
        norm = lambda x: max(0.0, min(1.0, (x - 0.45) / 0.35))  # noqa: E731
        rel_gen = round(100 * (0.55 * norm(top_sim) + 0.45 / (1 + math.exp(-2.5 * fit))), 1)
        rel_static = round(100 * (0.55 * norm(base_sim) + 0.45 * 0.25), 1)
    except Exception as ex:  # noqa: BLE001
        vs_error = (vs_error or "") + f" embed: {str(ex)[:120]}"
    t["embedding_ms"] = round((time.perf_counter() - t3) * 1000, 1)

    # ---- copy (LLM, guardrailed) with template fallback
    t4 = time.perf_counter()
    copy, copy_source, copy_issue = None, "template", None
    if comp:
        try:
            copy = _pool.submit(llm_copy, s, comp, best["theme"], best["angle"]).result(timeout=9)
            ok, hits = brand_safe_copy(brand, copy)
            if ok:
                copy_source = "llm"
            else:
                copy_issue, copy = f"LLM copy rejected by guardrail ({', '.join(hits) or 'length'})", None
        except Exception as ex:  # noqa: BLE001
            copy_issue = f"LLM unavailable: {str(ex)[:100]}"
    if not copy:
        copy = template_copy(s, comp, best["angle"])
    t["copy_ms"] = round((time.perf_counter() - t4) * 1000, 1)

    gen = {k: best[k] for k in ("pctr", "pdwell_s", "p_engaged", "poptout", "ecpm")}
    gen["attention"] = attention_score(best["pdwell_s"], best["pctr"])
    t["total_ms"] = round((time.perf_counter() - t0) * 1000, 1)
    palette = (comp["palette"].split(",") if comp else bcfg["allowed_palette"][:3])
    return {
        "state": s, "context_text": context_text(s),
        "static": static | {"relevance": rel_static, "copy": bcfg["baseline_copy"]},
        "generative": gen | {"relevance": rel_gen, "theme": best["theme"], "theme_label": TAX["themes"][best["theme"]]["label"],
                             "angle": best["angle"], "angle_label": TAX["angles"][best["angle"]], "copy": copy,
                             "copy_source": copy_source, "copy_issue": copy_issue,
                             "layers": layers_for(s, best["theme"]), "palette": palette},
        "component": comp, "rejected_components": rejected, "candidates": comps, "vs_error": vs_error,
        "leaderboard": leaderboard, "why": why, "against": against,
        "guardrail": {"blocked_combos": sum(1 for c in combos if c["blocked"]),
                      "unconstrained_winner": None if best_raw is best else
                      {"theme": TAX["themes"][best_raw["theme"]]["label"], "angle": TAX["angles"][best_raw["angle"]],
                       "reason": bcfg["forbidden"]}},
        "lift": {"ctr": gen["pctr"] / static["pctr"] - 1, "ecpm": gen["ecpm"] / static["ecpm"] - 1,
                 "dwell": gen["pdwell_s"] / static["pdwell_s"] - 1, "optout_reduction": 1 - gen["poptout"] / static["poptout"],
                 "attention_pts": gen["attention"] - static["attention"],
                 "cpe_static": static["ecpm"] / 1000 / max(1e-9, max(static["pctr"], static["p_engaged"])),
                 "cpe_generative": gen["ecpm"] / 1000 / max(1e-9, max(gen["pctr"], gen["p_engaged"]))},
        "timings": t, "model_version": MODELS.version, "themes_scored": len(TAX["themes"]), "combos_scored": len(combos),
    }
