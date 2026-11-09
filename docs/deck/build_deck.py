"""Build the 10-slide business deck for the Glance GenAd solution (Google Slides, Databricks 2024 template).

Usage: python3 build_deck.py <presentation_id>   (presentation = copy of the Databricks Corporate Slide Template 2024)
Requires the fe-google-tools gslides_builder module on PYTHONPATH (auth + batch_update helpers).
"""
import sys
import uuid

import gslides_builder as g

PID = sys.argv[1]
EMU = 914400
LAYOUT_TITLE = "g3a0039abd09_0_159"     # 3 Title Slide B - Light 2
LAYOUT_CONTENT = "g3a0039abd09_0_176"   # 8 Content A - Basic White 1 (TITLE, BODY1 kicker, BODY)


def hexrgb(h):
    h = h.lstrip("#")
    return {"red": int(h[0:2], 16) / 255, "green": int(h[2:4], 16) / 255, "blue": int(h[4:6], 16) / 255}


NAVY, LAVA, OAT, OAT2, GREEN, GRAY, BLUE, WHITE, YELLOW = (
    "#1B3139", "#FF3621", "#F9F7F4", "#EEEDE9", "#00A972", "#5A6F77", "#2272B4", "#FFFFFF", "#FFAB00")
FONT = "DM Sans"
REQ = []


def nid(prefix="e"):
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def tf(x, y):
    return {"scaleX": 1, "scaleY": 1, "translateX": int(x * EMU), "translateY": int(y * EMU), "unit": "EMU"}


def size(w, h):
    return {"width": {"magnitude": int(w * EMU), "unit": "EMU"}, "height": {"magnitude": int(h * EMU), "unit": "EMU"}}


def style_text(oid, runs_style, start=None, end=None):
    rng = {"type": "ALL"} if start is None else {"type": "FIXED_RANGE", "startIndex": start, "endIndex": end}
    fields = ",".join(runs_style.keys())
    REQ.append({"updateTextStyle": {"objectId": oid, "textRange": rng, "style": runs_style, "fields": fields}})


def box(page, x, y, w, h, text="", fill=None, outline=None, fs=12, color=NAVY, bold=False, align="START",
        valign="TOP", shape="RECTANGLE", rich=None, inset=0.08, line_spacing=None):
    """rich: list of (text, {style overrides}) segments - concatenated."""
    oid = nid("s")
    REQ.append({"createShape": {"objectId": oid, "shapeType": shape,
                                "elementProperties": {"pageObjectId": page, "size": size(w, h), "transform": tf(x, y)}}})
    props = {"contentAlignment": valign}
    fields = ["contentAlignment"]
    if fill:
        props["shapeBackgroundFill"] = {"solidFill": {"color": {"rgbColor": hexrgb(fill)}}}
        fields.append("shapeBackgroundFill.solidFill.color")
    else:
        props["shapeBackgroundFill"] = {"propertyState": "NOT_RENDERED"}
        fields.append("shapeBackgroundFill.propertyState")
    if outline:
        props["outline"] = {"outlineFill": {"solidFill": {"color": {"rgbColor": hexrgb(outline)}}},
                            "weight": {"magnitude": 1, "unit": "PT"}}
        fields += ["outline.outlineFill.solidFill.color", "outline.weight"]
    else:
        props["outline"] = {"propertyState": "NOT_RENDERED"}
        fields.append("outline.propertyState")
    REQ.append({"updateShapeProperties": {"objectId": oid, "shapeProperties": props, "fields": ",".join(fields)}})
    segs = rich or ([(text, {})] if text else [])
    full = "".join(s for s, _ in segs)
    if full:
        REQ.append({"insertText": {"objectId": oid, "text": full}})
        style_text(oid, {"fontFamily": FONT, "fontSize": {"magnitude": fs, "unit": "PT"},
                         "foregroundColor": {"opaqueColor": {"rgbColor": hexrgb(color)}}, "bold": bold})
        pos = 0
        for s, st in segs:
            if st and s:
                st2 = {}
                for k, v in st.items():
                    if k == "color":
                        st2["foregroundColor"] = {"opaqueColor": {"rgbColor": hexrgb(v)}}
                    elif k == "fs":
                        st2["fontSize"] = {"magnitude": v, "unit": "PT"}
                    else:
                        st2[k] = v
                style_text(oid, st2, pos, pos + len(s))
            pos += len(s)
        pstyle = {"alignment": align}
        pf = "alignment"
        if line_spacing:
            pstyle["lineSpacing"] = line_spacing
            pf += ",lineSpacing"
        REQ.append({"updateParagraphStyle": {"objectId": oid, "textRange": {"type": "ALL"}, "style": pstyle, "fields": pf}})
        ins = {"magnitude": int(inset * EMU), "unit": "EMU"}
    return oid


def arrow(page, x1, y1, x2, y2, color=GRAY, weight=1.5):
    oid = nid("ln")
    REQ.append({"createLine": {"objectId": oid, "lineCategory": "STRAIGHT", "elementProperties": {
        "pageObjectId": page, "size": size(max(abs(x2 - x1), 0.001), max(abs(y2 - y1), 0.001)),
        "transform": {"scaleX": 1 if x2 >= x1 else -1, "scaleY": 1 if y2 >= y1 else -1,
                      "translateX": int(x1 * EMU), "translateY": int(y1 * EMU), "unit": "EMU"}}}})
    REQ.append({"updateLineProperties": {"objectId": oid, "lineProperties": {
        "lineFill": {"solidFill": {"color": {"rgbColor": hexrgb(color)}}}, "weight": {"magnitude": weight, "unit": "PT"},
        "endArrow": "FILL_ARROW"}, "fields": "lineFill,weight,endArrow"}})


def table(page, x, y, w, h, data, col_w=None, header_fill=NAVY, fs=11, first_col_bold=True, highlight_col=None):
    oid = nid("tb")
    rows, cols = len(data), len(data[0])
    REQ.append({"createTable": {"objectId": oid, "rows": rows, "columns": cols,
                                "elementProperties": {"pageObjectId": page, "size": size(w, h), "transform": tf(x, y)}}})
    for r, row in enumerate(data):
        for c, val in enumerate(row):
            if val == "":
                continue
            REQ.append({"insertText": {"objectId": oid, "cellLocation": {"rowIndex": r, "columnIndex": c}, "text": val}})
            st = {"fontFamily": FONT, "fontSize": {"magnitude": fs, "unit": "PT"},
                  "foregroundColor": {"opaqueColor": {"rgbColor": hexrgb(WHITE if r == 0 else NAVY)}},
                  "bold": r == 0 or (c == 0 and first_col_bold) or (highlight_col is not None and c == highlight_col)}
            if r > 0 and highlight_col is not None and c == highlight_col:
                st["foregroundColor"] = {"opaqueColor": {"rgbColor": hexrgb(GREEN)}}
            REQ.append({"updateTextStyle": {"objectId": oid, "cellLocation": {"rowIndex": r, "columnIndex": c},
                                            "textRange": {"type": "ALL"}, "style": st,
                                            "fields": "fontFamily,fontSize,foregroundColor,bold"}})
    REQ.append({"updateTableCellProperties": {"objectId": oid, "tableRange": {"location": {"rowIndex": 0, "columnIndex": 0}, "rowSpan": 1, "columnSpan": cols},
                                              "tableCellProperties": {"tableCellBackgroundFill": {"solidFill": {"color": {"rgbColor": hexrgb(header_fill)}}}},
                                              "fields": "tableCellBackgroundFill.solidFill.color"}})
    for r in range(1, rows):
        REQ.append({"updateTableCellProperties": {"objectId": oid, "tableRange": {"location": {"rowIndex": r, "columnIndex": 0}, "rowSpan": 1, "columnSpan": cols},
                                                  "tableCellProperties": {"tableCellBackgroundFill": {"solidFill": {"color": {"rgbColor": hexrgb(OAT if r % 2 else WHITE)}}},
                                                                          "contentAlignment": "MIDDLE"},
                                                  "fields": "tableCellBackgroundFill.solidFill.color,contentAlignment"}})
    if col_w:
        for c, cw in enumerate(col_w):
            REQ.append({"updateTableColumnProperties": {"objectId": oid, "columnIndices": [c],
                                                        "tableColumnProperties": {"columnWidth": {"magnitude": int(cw * EMU), "unit": "EMU"}},
                                                        "fields": "columnWidth"}})
    return oid


def content_slide(title, kicker):
    page, t, k, b = nid("p"), nid("t"), nid("k"), nid("b")
    REQ.append({"createSlide": {"objectId": page, "slideLayoutReference": {"layoutId": LAYOUT_CONTENT},
                                "placeholderIdMappings": [
                                    {"layoutPlaceholder": {"type": "TITLE", "index": 0}, "objectId": t},
                                    {"layoutPlaceholder": {"type": "BODY", "index": 1}, "objectId": k},
                                    {"layoutPlaceholder": {"type": "BODY", "index": 0}, "objectId": b}]}})
    REQ.append({"insertText": {"objectId": t, "text": title}})
    style_text(t, {"fontSize": {"magnitude": 22, "unit": "PT"}, "bold": True})
    REQ.append({"insertText": {"objectId": k, "text": kicker}})
    style_text(k, {"fontSize": {"magnitude": 14, "unit": "PT"}, "foregroundColor": {"opaqueColor": {"rgbColor": hexrgb(GRAY)}}})
    REQ.append({"deleteObject": {"objectId": b}})
    return page


def footnote(page, text):
    box(page, 0.82, 6.8, 11.66, 0.26, text, fs=8.5, color=GRAY)


def kpi_tile(page, x, y, w, h, big, label, sub, accent=LAVA, target=None):
    box(page, x, y, w, h, fill=OAT, outline=OAT2)
    box(page, x, y, 0.08, h, fill=accent)
    box(page, x + 0.2, y + 0.12, w - 0.3, 0.75, big, fs=34, bold=True, color=accent)
    box(page, x + 0.2, y + 0.85, w - 0.3, 0.4, label, fs=13, bold=True)
    box(page, x + 0.2, y + 1.2, w - 0.3, 0.6, sub, fs=11, color=GRAY)
    if target:
        box(page, x + 0.2, y + h - 0.42, w - 0.3, 0.32, target, fs=10, bold=True, color=GREEN)


# =====================================================================================  SLIDES
# 1. Title
p1, t1, s1, s1b = nid("p"), nid("t"), nid("st"), nid("st")
REQ.append({"createSlide": {"objectId": p1, "slideLayoutReference": {"layoutId": LAYOUT_TITLE},
                            "placeholderIdMappings": [
                                {"layoutPlaceholder": {"type": "CENTERED_TITLE", "index": 0}, "objectId": t1},
                                {"layoutPlaceholder": {"type": "SUBTITLE", "index": 0}, "objectId": s1},
                                {"layoutPlaceholder": {"type": "SUBTITLE", "index": 1}, "objectId": s1b}]}})
REQ.append({"insertText": {"objectId": t1, "text": "Turning ad blindness into attention, and attention into yield"}})
style_text(t1, {"fontSize": {"magnitude": 40, "unit": "PT"}})
REQ.append({"insertText": {"objectId": s1, "text": "Real-time generative lock-screen ads for Glance, on the Databricks Data Intelligence Platform"}})
style_text(s1, {"fontSize": {"magnitude": 20, "unit": "PT"}})
REQ.append({"insertText": {"objectId": s1b, "text": "InMobi × Databricks  |  Solution review  |  November 2026"}})

# 2. Executive summary: lead with the outcome
p = content_slide("+83% eCPM from the same impressions, with fewer users opting out",
                  "Model-optimized generative lock-screen ads vs. today's static banner (off-policy evaluation, 600k impressions)")
W, X0, Y0, G = 2.78, 0.82, 2.0, 0.18
kpi_tile(p, X0 + 0 * (W + G), Y0, W, 2.25, "+83%", "eCPM (yield)", "$4.96 → $9.10 per 1,000 impressions", LAVA, "✓ target +50–75%")
kpi_tile(p, X0 + 1 * (W + G), Y0, W, 2.25, "+77%", "Click-through rate", "1.10% → 1.96% CTR", BLUE, "✓ significant CTR lift")
kpi_tile(p, X0 + 2 * (W + G), Y0, W, 2.25, "3.1 s", "Avg. active interaction", "0.94 s → 3.10 s per impression", GREEN, "✓ target > 2.5 s")
kpi_tile(p, X0 + 3 * (W + G), Y0, W, 2.25, "−19%", "Ad-related opt-outs", "1.10% → 0.89% opt-outs + uninstalls", YELLOW, "✓ target −15–20%")
box(p, 0.82, 4.45, 5.75, 2.05, fill=NAVY, rich=[
    ("Executive sponsor  ", {"bold": True, "color": YELLOW}), ("CEO · CRO · CFO\n", {"color": "#C5CED2"}),
    ("≈ $15M incremental annual earnings per 10M daily lock-screen impressions\n", {"bold": True, "fs": 15}),
    ("Higher yield from existing inventory (no new supply), lower churn risk on the lock-screen franchise, "
     "and a premium, differentiated ad product for brands.", {"fs": 12})], color=WHITE, fs=12, inset=0.2)
box(p, 6.72, 4.45, 5.76, 2.05, fill=OAT, outline=OAT2, rich=[
    ("Domain owner  ", {"bold": True, "color": LAVA}), ("Head of Ad Products · Ad Ops · Data Science\n", {"color": GRAY}),
    ("Every brand asset becomes a context-matched, brand-safe creative in real time\n", {"bold": True, "fs": 15}),
    ("One governed platform for signals, models, GenAI and BI. Every decision is explainable, logged and "
     "measured in governed metric views your teams can query in plain English.", {"fs": 12})], fs=12, inset=0.2)
footnote(p, "Demo build on synthetic ad-server logs; figures are model predictions to be validated in a live A/B pilot. "
            "$15M = (9.10 − 4.96) × 10M / 1,000 × 365.")

# 3. Business problem
p = content_slide("Static ads are tuned out, and every ignored impression costs yield and users",
                  "Baseline from 60 days of ad-server logs (600k impressions): the lock screen is monetized like a banner")
cols = [
    ("Ad blindness", LAVA, "1.09%", "CTR on static banners",
     "Users see the same generic banner regardless of weather, time or what they are doing. Only 0.9% of "
     "impressions get ≥ 2.5 s of attention (avg. 0.95 s)."),
    ("Attention friction drives churn", YELLOW, "+19%", "more opt-outs with interruptive video",
     "Standard programmatic video lifts CTR only +15%, but raises lock-screen opt-outs and uninstalls "
     "from 1.09% to 1.30%: yield bought at the cost of the user base."),
    ("Relevance doesn't scale safely", BLUE, "1 → ∞", "creatives needed per moment",
     "Producing creatives per context is manual, and unguarded GenAI risks brand violations (e.g. a recolored "
     "logo), so brands keep defaulting to one-size-fits-all."),
]
for i, (h, acc, big, cap, body) in enumerate(cols):
    x = 0.82 + i * 3.94
    box(p, x, 2.0, 3.74, 3.75, fill=OAT, outline=OAT2)
    box(p, x, 2.0, 3.74, 0.07, fill=acc)
    box(p, x + 0.2, 2.2, 3.4, 0.45, h, fs=15, bold=True)
    box(p, x + 0.2, 2.7, 3.4, 0.8, big, fs=40, bold=True, color=acc)
    box(p, x + 0.2, 3.5, 3.4, 0.4, cap, fs=11, bold=True, color=GRAY)
    box(p, x + 0.2, 3.95, 3.4, 1.7, body, fs=12)
box(p, 0.82, 5.95, 11.66, 0.8, fill=NAVY, color=WHITE, fs=14, valign="MIDDLE", inset=0.2, rich=[
    ("Business impact: ", {"bold": True, "color": YELLOW}),
    ("eCPM is flat at ~$4.93 on a finite inventory. The phone's most-viewed surface (100+ unlocks a day) earns banner "
     "rates, and pushing harder with intrusive formats erodes the audience.", {})])
footnote(p, "Synthetic demo data modeled on industry-typical banner and video behavior.")

# 4. Objectives
p = content_slide("What success looks like: four KPIs the business already tracks",
                  "Targets agreed for the solution, plus the non-negotiables that make GenAI deployable for brands")
table(p, 0.82, 2.0, 7.6, 3.3, [
    ["Objective", "KPI", "Baseline (static)", "Target"],
    ["Performance & engagement", "Click-through rate (CTR)", "1.09%", "Significant lift"],
    ["Attention", "Avg. active interaction duration", "0.95 s", "> 2.5 s"],
    ["Yield", "eCPM (earnings per 1,000 impressions)", "$4.93", "+50–75%"],
    ["Retention / ad fatigue", "Ad-related opt-outs + uninstalls", "1.09%", "−15–20%"],
], col_w=[2.0, 2.65, 1.45, 1.5], fs=12, highlight_col=3)
box(p, 8.7, 2.0, 3.78, 3.3, fill=NAVY, color=WHITE, fs=12, inset=0.22, rich=[
    ("Non-negotiables\n\n", {"bold": True, "fs": 15, "color": YELLOW}),
    ("Brand safety by design: ", {"bold": True}), ("no creative violates brand guidelines\n\n", {}),
    ("Privacy & isolation: ", {"bold": True}), ("PII masked; advertisers see only their own data\n\n", {}),
    ("Real time & explainable: ", {"bold": True}), ("millisecond decisions, with the reason for each", {})])
box(p, 0.82, 5.55, 11.66, 1.2, fill=OAT, outline=OAT2, fs=13, inset=0.2, valign="MIDDLE", rich=[
    ("Who owns what  ", {"bold": True, "color": LAVA}),
    ("Executive sponsor: yield (eCPM) and retention.   Domain owner: CTR, attention, brand safety and the operating "
     "model to run it every day.", {})])

# 5. Solution at a high level
p = content_slide("From one banner for everyone to a creative that fits the moment",
                  "A closed loop on one platform: sense the moment, decide what will work, generate it safely, learn from every impression")
steps = [("1  Sense", "Live context: weather, time, live sports, transit, phone skin, plus the user's behavioral profile"),
         ("2  Decide", "ML scores 10 layout themes × 5 message angles for expected yield (CTR, attention, opt-out risk)"),
         ("3  Generate", "Semantic search picks brand-approved assets; GenAI writes on-brand copy; layers compose the lock screen"),
         ("4  Learn", "Every decision and outcome flows back to the lakehouse to retrain the models")]
for i, (h, body) in enumerate(steps):
    x = 0.82 + i * 2.95
    box(p, x, 2.0, 2.8, 0.62, h, shape="HOME_PLATE" if i < 3 else "RECTANGLE", fill=[NAVY, BLUE, LAVA, GREEN][i],
        color=WHITE, fs=15, bold=True, valign="MIDDLE", inset=0.18)
    box(p, x, 2.72, 2.75, 1.25, body, fs=12)
box(p, 0.82, 4.15, 11.66, 2.65, fill=OAT, outline=OAT2)
box(p, 1.05, 4.3, 5.6, 0.4, "Example decision from the live demo", fs=13, bold=True, color=LAVA)
box(p, 1.05, 4.72, 5.4, 2.0, fs=12, rich=[
    ("Context: ", {"bold": True}), ("Starbucks · heavy rain · 8 AM rush hour · daily commuter who just missed a train\n\n", {}),
    ("Decision: ", {"bold": True}), ("Urban Commute layout + time-saving angle; Vector Search matched ‘Mobile Order & Pay’\n\n", {}),
    ("Copy (LLM): ", {"bold": True}), ("“Missed your train? Coffee's ready. Rain and rush hour? Pre-order on the app and skip the line.”", {"italic": True})])
for i, (v, l) in enumerate([("+102%", "predicted CTR"), ("+105%", "predicted eCPM"), ("3.6 s", "predicted interaction")]):
    x = 6.85 + i * 1.85
    box(p, x, 4.75, 1.7, 1.5, fill=WHITE, outline=OAT2)
    box(p, x, 4.9, 1.7, 0.6, v, fs=26, bold=True, color=[LAVA, LAVA, GREEN][i], align="CENTER")
    box(p, x, 5.55, 1.7, 0.5, l, fs=11, color=GRAY, align="CENTER")
box(p, 6.85, 6.35, 5.4, 0.35, "vs. the static ‘Buy Coffee Now. 10% off.’ banner shown to the same user", fs=10, color=GRAY)

# 6. Architecture
p = content_slide("Architecture: one governed platform from live signal to creative",
                  "Transactional, streaming, ML, GenAI and BI on the Databricks Data Intelligence Platform, all under Unity Catalog")
# sources
src = ["Live context streams\nweather · sports · transit", "Ad-server logs\nimpressions · clicks · dwell",
       "User profile store\nbehavioral vectors (PII)", "Creative asset bucket\nproduct shots · logos · copy"]
for i, s in enumerate(src):
    box(p, 0.82, 2.0 + i * 1.0, 2.1, 0.85, s, fill=OAT, outline=OAT2, fs=10, valign="MIDDLE", align="CENTER")
box(p, 0.82, 1.7, 2.1, 0.3, "SOURCES", fs=9, bold=True, color=GRAY)
# lakebase
box(p, 3.3, 1.7, 2.5, 0.3, "OPERATE", fs=9, bold=True, color=GRAY)
box(p, 3.3, 2.0, 2.5, 1.85, fill=BLUE, color=WHITE, fs=10, inset=0.14, rich=[
    ("Lakebase (Postgres)\n", {"bold": True, "fs": 13}),
    ("Context DB + app backend: profiles, live signals, asset registry, every ad decision; model weights served in ms", {})])
box(p, 3.3, 4.05, 2.5, 1.75, fill=OAT, outline=BLUE, fs=10, inset=0.14, rich=[
    ("Lakehouse Sync (CDC)\n", {"bold": True, "fs": 12}), ("Lakebase → Delta, continuously\n\n", {}),
    ("Synced tables\n", {"bold": True, "fs": 12}), ("Delta → Lakebase (model weights)", {})])
# lakeflow medallion
box(p, 6.2, 1.7, 3.2, 0.3, "ENGINEER & LEARN", fs=9, bold=True, color=GRAY)
box(p, 6.2, 2.0, 3.2, 1.35, fill=NAVY, color=WHITE, fs=10, inset=0.14, rich=[
    ("Lakeflow Declarative Pipelines\n", {"bold": True, "fs": 12}), ("Bronze → Silver → Gold Delta tables · Auto Loader · "
                                                                    "AUTO CDC · data-quality expectations", {})])
box(p, 6.2, 3.5, 1.55, 1.15, fill=OAT, outline=OAT2, fs=10, inset=0.1, rich=[("MLflow + UC models\n", {"bold": True}), ("CTR · dwell · opt-out", {})])
box(p, 7.85, 3.5, 1.55, 1.15, fill=OAT, outline=OAT2, fs=10, inset=0.1, rich=[("Vector Search\n", {"bold": True}), ("brand-safe asset registry", {})])
box(p, 6.2, 4.8, 1.55, 1.0, fill=OAT, outline=OAT2, fs=10, inset=0.1, rich=[("Metric views\n", {"bold": True}), ("governed KPIs", {})])
box(p, 7.85, 4.8, 1.55, 1.0, fill=OAT, outline=OAT2, fs=10, inset=0.1, rich=[("Foundation models\n", {"bold": True}), ("LLM copy · embeddings", {})])
# experience
box(p, 9.8, 1.7, 2.68, 0.3, "EXPERIENCE", fs=9, bold=True, color=GRAY)
box(p, 9.8, 2.0, 2.68, 2.1, fill=LAVA, color=WHITE, fs=10, inset=0.14, rich=[
    ("Databricks App\n", {"bold": True, "fs": 13}), ("Simulation controls · generative engine (static vs. generative) · "
                                                    "live effectiveness dashboard", {})])
box(p, 9.8, 4.25, 2.68, 1.55, fill=OAT, outline=LAVA, fs=10, inset=0.14, rich=[
    ("Genie agent\n", {"bold": True, "fs": 12}), ("Plain-English questions over the metric views, inside the app", {})])
# governance band
box(p, 0.82, 6.0, 11.66, 0.75, fill=NAVY, color=WHITE, fs=11, valign="MIDDLE", align="CENTER", rich=[
    ("Unity Catalog  ", {"bold": True, "color": YELLOW, "fs": 13}),
    ("advertiser row-level security · PII column masks · end-to-end lineage · model registry · access control", {})])
for ax in (2.96, 5.84, 9.44):
    box(p, ax, 3.55, 0.32, 0.5, shape="RIGHT_ARROW", fill=GRAY)
box(p, 4.33, 3.87, 0.44, 0.17, shape="DOWN_ARROW", fill=GRAY)
footnote(p, "Built and running end to end in a Databricks workspace; code and execution evidence: github.com/deepaksuryaprakash/glance-genad-demo")

# 7. Solution in detail: inside one decision
p = content_slide("Inside one decision: from context to brand-safe creative in a single request",
                  "What the generative engine does each time a user unlocks the phone (timings measured in the live demo)")
det = [("Read profile + live context", "Lakebase", "~4 ms"),
       ("Match brand-safe assets", "Vector Search", "~0.3–0.5 s"),
       ("Score 50 layouts", "CTR · dwell · opt-out models", "< 2 ms"),
       ("Enforce guardrails", "Brand rules + safety flags", "inline"),
       ("Write on-brand copy", "Foundation model (LLM)", "~3 s*"),
       ("Compose + log decision", "Layered layout → Lakebase → Delta", "~8 ms")]
for i, (h, tech, ms) in enumerate(det):
    x = 0.82 + i * 1.96
    box(p, x + 0.61, 1.95, 0.6, 0.6, str(i + 1), shape="ELLIPSE", fill=[NAVY, BLUE, LAVA, YELLOW, GREEN, NAVY][i], color=WHITE,
        fs=14, bold=True, align="CENTER", valign="MIDDLE")
    box(p, x, 2.6, 1.82, 0.62, h, fs=12, bold=True, align="CENTER")
    box(p, x, 3.2, 1.82, 0.5, tech, fs=10, color=GRAY, align="CENTER")
    box(p, x, 3.68, 1.82, 0.38, ms, fs=12, bold=True, color=LAVA, align="CENTER")
trust = [("Explainable", "Each choice shows the learned signals behind it, e.g. ‘Time-saving × Just missed a train’ and "
                          "‘Urban Commute × 8 AM rush hour’, so ad ops can see why a layout won."),
         ("Brand-safe by design", "Unsafe assets are retrieved but rejected (e.g. an AI neon-pink Nike recolor). "
                                  "Blocked themes and angles are excluded before scoring; generated copy is checked against banned phrases."),
         ("Measured, end to end", "Every decision is written to Lakebase, synced to Delta and surfaced in metric views, "
                                  "so lift is tracked live and Genie can answer questions about it.")]
for i, (h, body) in enumerate(trust):
    x = 0.82 + i * 3.94
    box(p, x, 4.35, 3.74, 2.3, fill=OAT, outline=OAT2)
    box(p, x + 0.2, 4.5, 3.4, 0.4, h, fs=14, bold=True, color=[BLUE, LAVA, GREEN][i])
    box(p, x + 0.2, 4.92, 3.4, 1.7, body, fs=11.5)
footnote(p, "* Copy generation dominates latency in the demo. In production, copy variants are pre-generated per context cell "
            "so serving is model scoring + lookup (milliseconds).")

# 8. Mapping to objectives
p = content_slide("How the solution maps to each objective",
                  "Optimized engine vs. static control: all four KPI targets met, with brand safety enforced on every creative")
table(p, 0.82, 2.0, 11.66, 3.65, [
    ["Objective", "Target", "Result", "How the solution delivers it"],
    ["CTR lift", "Significant lift", "+77%  (1.10% → 1.96%)", "Context × creative model picks the highest-yield of 50 layout/message combinations for each moment"],
    ["Avg. interaction", "> 2.5 s", "3.10 s  (from 0.94 s)", "Immersive lock-screen widget that fits the moment (rain, commute, live match) instead of a banner"],
    ["eCPM", "+50–75%", "+83%  ($4.96 → $9.10)", "Optimizes expected yield directly: CTR × CPC + engaged views × CPE + CPM floor"],
    ["Opt-outs / uninstalls", "−15–20%", "−19.4%", "Relevance replaces interruption; the model avoids mismatched creatives, which raise opt-outs"],
    ["Brand safety", "No violations", "Every served creative passes", "Brand registry with safety flags in Vector Search, blocked themes/angles, copy validation"],
], col_w=[1.9, 1.5, 2.25, 6.01], fs=11, highlight_col=2)
box(p, 0.82, 5.85, 11.66, 0.9, fill=NAVY, color=WHITE, fs=13, valign="MIDDLE", inset=0.2, rich=[
    ("Why the data science matters: ", {"bold": True, "color": YELLOW}),
    ("‘generative’ alone is not enough. Naive generative layouts (rules + random) deliver +36% eCPM and −13% opt-outs; "
     "model-driven optimization is what clears the targets.", {})])
footnote(p, "Off-policy evaluation on 6,000 held-out contexts, model v7 (MLflow / Unity Catalog). Synthetic data; validate in live A/B.")

# 9. Value framing
p = content_slide("The value case for the executive sponsor and the domain owner",
                  "Same platform, two lenses: financial outcome at the top, operating leverage for the team that runs it")
box(p, 0.82, 2.0, 5.75, 4.75, fill=NAVY)
box(p, 1.05, 2.15, 5.3, 0.45, "Executive sponsor · CEO / CRO / CFO", fs=15, bold=True, color=YELLOW)
table(p, 1.05, 2.7, 5.3, 1.45, [
    ["Per 10M daily impressions", "Static", "Generative"],
    ["Earnings per day", "$49.6K", "$91.0K"],
    ["Earnings per year", "$18.1M", "$33.2M"],
], col_w=[2.5, 1.4, 1.4], header_fill=LAVA, fs=11, highlight_col=2)
box(p, 1.05, 4.3, 5.3, 2.4, color=WHITE, fs=12, rich=[
    ("+$15.1M a year incremental from existing inventory\n", {"bold": True, "fs": 14}),
    ("• Yield up without adding supply or ad load\n• −19% opt-outs protects the lock-screen audience and future revenue\n"
     "• Premium, differentiated ‘contextual moments’ product to sell to brands\n• One platform, lower total cost than stitching point tools", {})])
box(p, 6.72, 2.0, 5.76, 4.75, fill=OAT, outline=OAT2)
box(p, 6.95, 2.15, 5.3, 0.45, "Domain owner · Ad Products & Ad Ops", fs=15, bold=True, color=LAVA)
box(p, 6.95, 2.7, 5.3, 4.0, fs=12, rich=[
    ("Ship relevance at scale\n", {"bold": True}), ("Any brand asset becomes context-matched creatives without manual production.\n\n", {}),
    ("Say yes to GenAI with brands\n", {"bold": True}), ("Guardrails, safety flags and copy validation are built into the decision path.\n\n", {}),
    ("Trust and iterate fast\n", {"bold": True}), ("Explainable decisions; retrain → new weights flow to serving automatically.\n\n", {}),
    ("Self-serve answers\n", {"bold": True}), ("Governed metric views + Genie let sales and ad ops ask ‘which theme wins in rain?’ directly.\n\n", {}),
    ("Governed by default\n", {"bold": True}), ("Advertiser data isolation, PII masking and lineage in Unity Catalog.", {})])
footnote(p, "Earnings = eCPM × impressions / 1,000. eCPM $4.96 (static) vs $9.10 (optimized generative), model v7. Illustrative, synthetic data.")

# 10. Conclusion + next steps
p = content_slide("Conclusion: relevance is the new reach",
                  "Generative, context-aware lock-screen ads turn ignored impressions into attention, and attention into yield")
for i, (h, body, acc) in enumerate([
        ("Proven in a working build", "End to end on Databricks: live context in Lakebase, medallion pipelines, three trained models, "
                                      "Vector Search guardrails, LLM copy, an app and Genie, all governed in Unity Catalog.", BLUE),
        ("Hits every target KPI", "+77% CTR · 3.1 s interaction · +83% eCPM · −19% opt-outs vs. the static banner, with "
                                  "brand safety enforced on every creative.", LAVA),
        ("Worth ≈ $15M a year per 10M daily impressions", "Higher yield from the inventory Glance already has, while protecting the "
                                                          "audience that makes it valuable.", GREEN)]):
    x = 0.82 + i * 3.94
    box(p, x, 2.0, 3.74, 2.25, fill=OAT, outline=OAT2)
    box(p, x, 2.0, 3.74, 0.07, fill=acc)
    box(p, x + 0.2, 2.2, 3.4, 0.7, h, fs=14, bold=True, color=acc)
    box(p, x + 0.2, 2.9, 3.4, 1.3, body, fs=11.5)
box(p, 0.82, 4.45, 11.66, 2.3, fill=NAVY)
box(p, 1.05, 4.6, 6, 0.4, "Recommended next steps", fs=15, bold=True, color=YELLOW)
for i, (h, body) in enumerate([
        ("Weeks 1–2 · Connect", "Real weather/sports/transit feeds, ad-server logs and the creative DAM into the same pipelines"),
        ("Weeks 3–6 · Pilot", "A/B test on 5% of lock-screen inventory with 2 brands; success = the four KPI targets"),
        ("Weeks 7+ · Scale", "Pre-generated copy for ms serving, drift monitoring, rollout across brands and markets")]):
    x = 1.05 + i * 3.8
    box(p, x, 5.1, 3.6, 0.4, h, fs=13, bold=True, color=WHITE)
    box(p, x, 5.5, 3.6, 1.1, body, fs=11.5, color="#C5CED2")

# ===================================================================================== apply
old = g.get_slide_ids(PID)
for i in range(0, len(REQ), 400):
    r = g.batch_update(PID, REQ[i:i + 400])
    if "error" in r:
        print("ERROR", r["error"]["message"][:500])
        sys.exit(1)
g.batch_update(PID, [{"deleteObject": {"objectId": s}} for s in old])
print("slides:", len(g.get_slide_ids(PID)))
print(f"https://docs.google.com/presentation/d/{PID}/edit")
