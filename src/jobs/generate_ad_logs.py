"""Synthetic ad-server impression logs for the Glance generative-ads demo.

Writes one parquet file per day into the raw landing volume; Auto Loader (Lakeflow pipeline)
ingests them incrementally into bronze.

Hidden ground truth (what the data-science models must *learn* from the logs):
  * Static banners / standard video ignore context -> low CTR, short dwell, higher opt-outs.
  * Generative lock-screen layouts earn lift only when the layout theme + copy angle fit the user's
    live context (weather, time, user state, live event, phone skin). Mismatched themes HURT.

Usage (job params):  <taxonomy.json path> <volume dir> <days> <impressions_per_day> [mode=backfill|today]
"""
import json
import sys
from datetime import date, datetime, timedelta, timezone

import numpy as np
import pandas as pd

TAXONOMY = sys.argv[1] if len(sys.argv) > 1 else "taxonomy.json"
OUT_DIR = sys.argv[2] if len(sys.argv) > 2 else "/Volumes/glance_genad/raw/ad_logs/impressions"
DAYS = int(sys.argv[3]) if len(sys.argv) > 3 else 60
PER_DAY = int(sys.argv[4]) if len(sys.argv) > 4 else 10000
MODE = sys.argv[5] if len(sys.argv) > 5 else "backfill"

tax = json.load(open(TAXONOMY))
SEGMENTS = ["fitness_enthusiast", "casual_gamer", "tech_professional", "daily_commuter", "night_owl"]
CITIES = tax["cities"]
SKINS = ["dark_minimal", "vibrant_neon", "pastel_soft", "nature_green"]
WEATHER = list(tax["weather"])
SLOTS = list(tax["time_slot"])
STATES = list(tax["user_state"])
EVENTS = list(tax["live_event"])
THEMES = list(tax["themes"])
ANGLES = list(tax["angles"])
BRANDS = list(tax["brands"])
CPE = tax["pricing"]["cpe_usd"]
ENGAGED_MS = tax["pricing"]["engaged_dwell_ms"]

# ---------------------------------------------------------------- ground truth (hidden)
THEME_FX = {
    "cozy_warm":       {"cold": .6, "heavy_rain": .45, "morning_rush": .2, "late_night": .15, "relaxing_at_home": .3, "starbucks": .35, "hot_humid": -.5, "pastel_soft": .15},
    "rain_atmos":      {"heavy_rain": .85, "cloudy": .2, "sunny": -.6, "hot_humid": -.3, "just_missed_train": .3, "commuting": .2, "dark_minimal": .15},
    "sunrise_fresh":   {"morning_rush": .45, "sunny": .4, "late_night": -.6, "working_out": .25, "heavy_rain": -.3, "pastel_soft": .15, "nature_green": .15},
    "energetic_sport": {"working_out": .6, "fitness_enthusiast": .5, "city_marathon": .6, "sunny": .25, "nike": .35, "late_night": -.3, "relaxing_at_home": -.2, "nature_green": .15},
    "live_match_hype": {"cricket_live": .9, "football_live": .8, "esports_final": .3, "none": -.5, "evening": .2, "relaxing_at_home": .25, "vibrant_neon": .15},
    "urban_commute":   {"just_missed_train": .6, "commuting": .5, "morning_rush": .35, "daily_commuter": .35, "relaxing_at_home": -.4},
    "minimal_tech":    {"tech_professional": .5, "at_office": .4, "dark_minimal": .25, "midday": .15},
    "night_calm":      {"late_night": .7, "night_owl": .35, "relaxing_at_home": .25, "morning_rush": -.4, "sunny": -.2, "dark_minimal": .15},
    "chill_lounge":    {"relaxing_at_home": .55, "evening": .3, "cloudy": .15, "pastel_soft": .2, "just_missed_train": -.3},
    "bold_neon":       {"casual_gamer": .55, "esports_final": .6, "vibrant_neon": .35, "late_night": .2, "tech_professional": -.15},
}
ANGLE_FX = {
    "time_saving": {"just_missed_train": .6, "commuting": .3, "morning_rush": .25, "at_office": .2, "relaxing_at_home": -.3},
    "comfort":     {"relaxing_at_home": .35, "heavy_rain": .3, "cold": .3, "late_night": .2},
    "performance": {"working_out": .5, "fitness_enthusiast": .35, "city_marathon": .4, "nike": .2, "relaxing_at_home": -.2},
    "social_fomo": {"cricket_live": .4, "football_live": .4, "esports_final": .4, "evening": .2, "none": -.15},
    "discount":    {"_base": .1, "casual_gamer": .2, "nike": -.3},
}
BRAND_FX = {  # baseline demand: applies to every format
    "starbucks": {"cold": .35, "heavy_rain": .3, "morning_rush": .4, "hot_humid": .1, "at_office": .2, "just_missed_train": .25,
                  "working_out": -.3, "tech_professional": .3, "daily_commuter": .3, "night_owl": .1},
    "nike":      {"sunny": .25, "city_marathon": .5, "working_out": .45, "fitness_enthusiast": .5, "heavy_rain": -.15,
                  "late_night": -.2, "casual_gamer": -.1},
}
BASE_CTR_LOGIT = {"static_banner": -4.9, "standard_video": -4.75, "glance_generative": -5.1}
BASE_DWELL_S = {"static_banner": 0.85, "standard_video": 1.45, "glance_generative": 1.9}
BASE_OPTOUT_LOGIT = {"static_banner": -4.55, "standard_video": -4.4, "glance_generative": -4.6}
# layout component used for each theme (per brand) -> ties logs to the brand asset registry
THEME_COMPONENT = {
    "nike": {"cozy_warm": "nk_comfort_recovery", "rain_atmos": "nk_gtx_waterproof", "sunrise_fresh": "nk_zoom_speed",
             "energetic_sport": "nk_zoom_speed", "live_match_hype": "nk_fan_jersey", "urban_commute": "nk_gtx_waterproof",
             "minimal_tech": "nk_zoom_speed", "night_calm": "nk_reflective_night", "chill_lounge": "nk_comfort_recovery",
             "bold_neon": "nk_neon_pink_recolor"},
    "starbucks": {"cozy_warm": "sb_hot_latte", "rain_atmos": "sb_hot_latte", "sunrise_fresh": "sb_rewards_morning",
                  "energetic_sport": "sb_energy_shot", "live_match_hype": "sb_match_share", "urban_commute": "sb_mobile_order",
                  "minimal_tech": "sb_office_focus", "night_calm": "sb_night_decaf", "chill_lounge": "sb_cold_brew",
                  "bold_neon": "sb_cold_brew"},
}


FIT_SCALE = 0.7    # strength of creative-context fit
FIT_CAP = 1.4      # creative relevance saturates: effect = FIT_SCALE * FIT_CAP * tanh(raw / FIT_CAP)
CPM_FLOOR_USD = 0.0012  # CPM-sold floor per viewable impression ($1.20 CPM)


def fx(table, keys):
    return sum(table.get(k, 0.0) for k in keys) + table.get("_base", 0.0)


# ---------------------------------------------------------------- context sampling
CITY_WEATHER = {  # climate mix per city
    "Bengaluru": [.25, .30, .30, .05, .10], "Mumbai": [.20, .20, .40, .0, .20], "Delhi": [.30, .15, .10, .40, .05],
    "Hyderabad": [.45, .20, .15, .05, .15], "Pune": [.30, .30, .25, .10, .05], "Jakarta": [.20, .15, .30, .0, .35],
}
SLOT_P = [.30, .25, .27, .18]
SLOT_HOURS = {"morning_rush": [7, 8, 9], "midday": [12, 13, 14, 15], "evening": [18, 19, 20, 21], "late_night": [22, 23, 0]}
STATE_P = {  # P(state | slot): just_missed_train, relaxing_at_home, commuting, working_out, at_office
    "morning_rush": [.15, .15, .45, .15, .10], "midday": [.05, .20, .10, .10, .55],
    "evening": [.05, .35, .30, .20, .10], "late_night": [.04, .82, .08, .05, .01],
}


def gen_day(rng, d: date, n: int) -> pd.DataFrame:
    users = rng.integers(1, 20001, n)
    seg = np.array(SEGMENTS)[users % 5]
    city = np.array(CITIES)[(users // 5) % 6]
    skin = np.array(SKINS)[(users * 7) % 4]
    slot = rng.choice(SLOTS, n, p=SLOT_P).astype(object)
    hour = np.array([rng.choice(SLOT_HOURS[s]) for s in slot])
    # one weather draw per city per day (+ a 20% chance the evening turns rainy)
    day_weather = {c: rng.choice(WEATHER, p=CITY_WEATHER[c]) for c in CITIES}
    weather = np.array([day_weather[c] for c in city], dtype=object)
    flip = (slot == "evening") & (rng.random(n) < .2) & (weather != "cold")
    weather[flip] = "heavy_rain"
    state = np.empty(n, dtype=object)
    for s in SLOTS:
        m = slot == s
        p = np.array(STATE_P[s])
        state[m] = rng.choice(STATES, m.sum(), p=p)
    # segment skews: commuters miss trains more, fitness folks work out more
    bump = (seg == "daily_commuter") & (slot == "morning_rush") & (rng.random(n) < .2)
    state[bump] = "just_missed_train"
    bump = (seg == "fitness_enthusiast") & (rng.random(n) < .2) & (slot != "late_night")
    state[bump] = "working_out"
    # live events: matches in evening/late-night, marathon on weekend mornings, esports finals
    ev = np.full(n, "none", dtype=object)
    r = rng.random(n)
    weekend = d.weekday() >= 5
    match_day = (d.toordinal() % 3 == 0)
    ev[(np.isin(slot, ["evening", "late_night"])) & match_day & (r < .45)] = "cricket_live"
    ev[(np.isin(slot, ["evening", "late_night"])) & (not match_day) & (r < .2)] = "football_live"
    ev[(slot == "morning_rush") & weekend & np.isin(city, ["Delhi", "Mumbai", "Bengaluru"]) & (r < .5)] = "city_marathon"
    ev[(np.isin(slot, ["evening", "late_night", "midday"])) & (d.toordinal() % 7 == 2) & (r > .85)] = "esports_final"

    brand = rng.choice(BRANDS, n)
    fmt = rng.choice(["static_banner", "standard_video", "glance_generative"], n, p=[.35, .20, .45])
    theme = np.full(n, "none", dtype=object)
    angle = np.full(n, "none", dtype=object)
    comp = np.full(n, None, dtype=object)
    rule_theme = {"heavy_rain": "rain_atmos", "cold": "cozy_warm", "sunny": "sunrise_fresh", "hot_humid": "chill_lounge", "cloudy": "minimal_tech"}
    for i in np.where(fmt == "glance_generative")[0]:
        b = brand[i]
        allowed_t = [t for t in THEMES if t not in tax["brands"][b]["blocked_themes"]]
        allowed_a = [a for a in ANGLES if a not in tax["brands"][b]["blocked_angles"]]
        # historical serving policy: 55% weather rule, 45% exploration (uniform)
        t = rule_theme[weather[i]] if rng.random() < .55 else rng.choice(allowed_t)
        if t not in allowed_t:
            t = rng.choice(allowed_t)
        theme[i] = t
        angle[i] = rng.choice(allowed_a)
        comp[i] = THEME_COMPONENT[b][t]

    # ------------------------------------------------------------ outcomes
    user_fx = rng.normal(0, .3, 20001)[users]
    logit = np.empty(n)
    fit = np.zeros(n)
    for i in range(n):
        keys = (seg[i], weather[i], slot[i], state[i], ev[i], skin[i], brand[i])
        l = BASE_CTR_LOGIT[fmt[i]] + fx(BRAND_FX[brand[i]], keys)
        if fmt[i] == "glance_generative":
            raw = fx(THEME_FX[theme[i]], keys) + fx(ANGLE_FX[angle[i]], keys)
            f = FIT_SCALE * FIT_CAP * np.tanh(raw / FIT_CAP)
            fit[i] = f
            l += f
        logit[i] = l
    logit += user_fx
    p_click = 1 / (1 + np.exp(-logit))
    clicked = (rng.random(n) < p_click).astype(int)

    is_gen = fmt == "glance_generative"
    base_dw = np.array([BASE_DWELL_S[f] for f in fmt])
    dwell_s = np.exp(np.log(base_dw) + .6 * fit + .25 * clicked + rng.normal(0, .45, n))
    dwell_ms = np.round(dwell_s * 1000).astype(int)

    o_logit = np.array([BASE_OPTOUT_LOGIT[f] for f in fmt]) - .55 * fit
    o_logit += np.where((~is_gen) & (slot == "late_night"), .25, 0)       # intrusive at night
    o_logit += np.where(fmt == "standard_video", .1 * (state == "just_missed_train"), 0)
    o_logit += np.where(is_gen & (fit < 0), .2, 0)                          # badly matched generative hurts
    p_opt = 1 / (1 + np.exp(-o_logit))
    opted = (rng.random(n) < p_opt).astype(int)
    opt_type = np.where(opted == 1, np.where(rng.random(n) < .7, "lockscreen_optout", "app_uninstall"), None)

    cpc = np.array([tax["brands"][b]["cpc_usd"] for b in brand])
    engaged = (dwell_ms >= ENGAGED_MS).astype(int)
    revenue = clicked * cpc + engaged * CPE + CPM_FLOOR_USD  # + CPM floor on every viewable impression

    placement = np.where(fmt == "static_banner", "in_app_banner",
                np.where(fmt == "standard_video", "interstitial_video",
                np.where(rng.random(n) < .6, "lockscreen_widget", "lockscreen_background")))
    temp = {"sunny": 31, "cloudy": 25, "heavy_rain": 23, "cold": 8, "hot_humid": 34}
    secs = rng.integers(0, 3600, n)
    ts = [datetime(d.year, d.month, d.day, int(h), tzinfo=timezone.utc) + timedelta(seconds=int(s)) for h, s in zip(hour, secs)]
    return pd.DataFrame({
        "impression_id": [f"imp-{d.strftime('%Y%m%d')}-{i:06d}-{rng.integers(1e9)}" for i in range(n)],
        "event_ts": ts, "user_id": [f"U{u:05d}" for u in users], "city": city, "segment": seg,
        "phone_skin": skin, "brand": brand, "ad_format": fmt, "placement": placement,
        "weather": weather, "temp_c": [temp[w] + float(rng.normal(0, 2)) for w in weather],
        "time_slot": slot, "user_state": state.astype(str), "live_event": ev.astype(str),
        "layout_theme": theme.astype(str), "copy_angle": angle.astype(str), "component_id": comp,
        "campaign_id": [f"{b}-q4-{'gen' if f == 'glance_generative' else 'std'}" for b, f in zip(brand, fmt)],
        "device_os": np.where(users % 7 == 0, "iOS", "Android"),
        "clicked": clicked, "dwell_ms": dwell_ms, "engaged": engaged,
        "opted_out": opted, "opt_out_type": opt_type, "cpc_usd": cpc, "revenue_usd": np.round(revenue, 6),
        "ad_server": "glance-adserver-v3",
    })


def main():
    rng = np.random.default_rng(20261105 if MODE == "backfill" else int(datetime.now().timestamp()))
    today = date.today()
    days = [today - timedelta(days=k) for k in range(DAYS, 0, -1)] if MODE == "backfill" else [today]
    import os
    for d in days:
        df = gen_day(rng, d, PER_DAY)
        p = f"{OUT_DIR}/dt={d.isoformat()}"
        os.makedirs(p, exist_ok=True)
        suffix = "backfill" if MODE == "backfill" else datetime.now().strftime("%H%M%S")
        df.to_parquet(f"{p}/impressions-{suffix}.parquet", index=False, coerce_timestamps="us", allow_truncated_timestamps=True)
        g = df.groupby("ad_format").agg(ctr=("clicked", "mean"), dwell=("dwell_ms", "mean"), opt=("opted_out", "mean"), rev=("revenue_usd", "mean"))
        print(d, len(df), "\n", (g.assign(ecpm=g.rev * 1000)).round(4).to_string())


main()
