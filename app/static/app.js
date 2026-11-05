const $ = (s) => document.querySelector(s);
const S = { brand: "starbucks", user_id: null, weather: "heavy_rain", time_slot: "morning_rush", user_state: "just_missed_train",
            live_event: "none", phone_skin: null };
let TAX = null, PERSONAS = [], LAST = null, GENIE_CONV = null;
const svgCache = {};
const pct = (x, d = 2) => (x * 100).toFixed(d) + "%";
const sgn = (x, d = 0) => (x >= 0 ? "+" : "") + (x * 100).toFixed(d) + "%";
const usd = (x, d = 2) => "$" + Number(x).toFixed(d);

async function api(path, body) {
  const r = await fetch(path, body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {});
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`);
  return r.json();
}

// ------------------------------------------------------------------ controls
function seg(el, options, key, labels) {
  const box = $(el); box.innerHTML = "";
  Object.entries(options).forEach(([k, v]) => {
    const b = document.createElement("button");
    b.textContent = labels ? labels(k, v) : v; b.dataset.k = k;
    if (S[key] === k) b.classList.add("on");
    b.onclick = () => { S[key] = k; box.querySelectorAll("button").forEach((x) => x.classList.toggle("on", x.dataset.k === k)); };
    box.appendChild(b);
  });
}
function renderControls() {
  seg("#brandSeg", Object.fromEntries(Object.entries(TAX.brands).map(([k, v]) => [k, v.display])), "brand");
  seg("#weatherSeg", TAX.weather, "weather", (k, v) => ({ sunny: "☀️ ", cloudy: "☁️ ", heavy_rain: "🌧️ ", cold: "🥶 ", hot_humid: "🥵 " }[k] + v));
  seg("#timeSeg", TAX.time_slot, "time_slot");
  seg("#stateSeg", TAX.user_state, "user_state");
  seg("#skinSeg", TAX.phone_skin, "phone_skin");
  $("#event").innerHTML = Object.entries(TAX.live_event).map(([k, v]) => `<option value="${k}">${v}</option>`).join("");
  $("#event").value = S.live_event;
  $("#event").onchange = (e) => (S.live_event = e.target.value);
  $("#persona").innerHTML = PERSONAS.map((p) => `<option value="${p.user_id}">${p.full_name} · ${TAX.segments[p.segment]} · ${p.city}</option>`).join("");
  $("#persona").onchange = (e) => selectPersona(e.target.value);
  selectPersona(PERSONAS.find((p) => p.segment === "daily_commuter")?.user_id || PERSONAS[0]?.user_id);
}
function selectPersona(id) {
  S.user_id = id; $("#persona").value = id;
  const p = PERSONAS.find((x) => x.user_id === id); if (!p) return;
  S.phone_skin = p.preferred_skin; seg("#skinSeg", TAX.phone_skin, "phone_skin");
  const v = typeof p.behavior_vector === "string" ? JSON.parse(p.behavior_vector) : p.behavior_vector;
  $("#personaCard").innerHTML = `<b>${p.full_name}</b> · ${p.device_os} · ${p.daily_unlocks} unlocks/day<br>${p.persona_blurb || ""}
    <div class="vec">${Object.values(v).map((x) => `<span style="height:${Math.max(6, x * 100)}%" title="${x}"></span>`).join("")}</div>
    <div class="vec-l">${Object.keys(v).map((k) => `<span>${k}</span>`).join("")}</div>`;
  $("#liveCity").textContent = p.city;
}
const PRESETS = {
  rain: { brand: "starbucks", weather: "heavy_rain", time_slot: "morning_rush", user_state: "just_missed_train", live_event: "none", persona: "daily_commuter" },
  sunny: { brand: "nike", weather: "sunny", time_slot: "morning_rush", user_state: "working_out", live_event: "none", persona: "fitness_enthusiast" },
  night: { brand: "nike", weather: "cloudy", time_slot: "late_night", user_state: "relaxing_at_home", live_event: "cricket_live", persona: "night_owl" },
};
function applyPreset(name) {
  const p = PRESETS[name];
  Object.assign(S, { brand: p.brand, weather: p.weather, time_slot: p.time_slot, user_state: p.user_state, live_event: p.live_event });
  const per = PERSONAS.find((x) => x.segment === p.persona); if (per) selectPersona(per.user_id);
  renderControls2(); generate();
}
function renderControls2() {
  ["brandSeg:brand", "weatherSeg:weather", "timeSeg:time_slot", "stateSeg:user_state", "skinSeg:phone_skin"].forEach((x) => {
    const [el, key] = x.split(":");
    document.querySelectorAll(`#${el} button`).forEach((b) => b.classList.toggle("on", b.dataset.k === S[key]));
  });
  $("#event").value = S.live_event;
}
async function pullLive() {
  const p = PERSONAS.find((x) => x.user_id === S.user_id);
  const r = await api(`/api/live-context?city=${encodeURIComponent(p.city)}`);
  Object.assign(S, r.suggested); renderControls2();
  $("#liveNote").innerHTML = `<b>Lakebase · ${r.lakebase_ms} ms</b> · ` + r.signals.map((s) => `${s.signal_type}: ${s.signal_value}`).join(" · ");
}

// ------------------------------------------------------------------ generate
const STEPS = ["Reading user profile + live context from Lakebase…", "Vector Search: matching context to brand-safe assets…",
  "Scoring 10 themes × 5 copy angles with CTR / dwell / opt-out models…", "Applying brand guardrails…", "Writing on-brand copy (LLM)…", "Stitching contextual layers…"];
async function generate() {
  $("#genBtn").disabled = true; $("#genOverlay").classList.add("on");
  let i = 0; $("#genStep").textContent = STEPS[0];
  const tick = setInterval(() => { i = Math.min(i + 1, STEPS.length - 1); $("#genStep").textContent = STEPS[i]; }, 450);
  try {
    const r = await api("/api/generate", { user_id: S.user_id, brand: S.brand, weather: S.weather, time_slot: S.time_slot,
      user_state: S.user_state, live_event: S.live_event, phone_skin: S.phone_skin });
    LAST = r;
    await render(r);
    refreshDecisions();
  } catch (e) { $("#trace").innerHTML = `<div class="err">${e.message}</div>`; }
  finally { clearInterval(tick); $("#genOverlay").classList.remove("on"); $("#genBtn").disabled = false; }
}
async function svg(brand, name) {
  const k = brand + name; if (!svgCache[k]) svgCache[k] = fetch(`/api/assets/${brand}/${name}`).then((r) => r.text());
  return svgCache[k];
}
const CLOCK = { morning_rush: ["08:02", "Wednesday, 5 November"], midday: ["13:07", "Wednesday, 5 November"],
                evening: ["19:24", "Wednesday, 5 November"], late_night: ["23:03", "Wednesday, 5 November"] };
const TEMP = { sunny: "31°", cloudy: "24°", heavy_rain: "21°", cold: "7°", hot_humid: "34°" };
const WICON = { sunny: "☀️", cloudy: "☁️", heavy_rain: "🌧️", cold: "🥶", hot_humid: "🥵" };

async function render(r) {
  const st = r.state, g = r.generative, b = TAX.brands[st.brand];
  $("#ctxText").textContent = r.context_text;
  // ---- control banner
  const productFile = st.brand === "nike" ? "product_shoe.svg" : "product_cup.svg";
  $("#banner").innerHTML = `<span class="ad">Ad</span><img src="/api/assets/${st.brand}/${productFile}"/>
    <div><div class="t">${r.static.copy.headline}</div><div class="b">${r.static.copy.body}</div></div><div class="cta">${r.static.copy.cta}</div>`;
  $("#blindBadge").innerHTML = `Same banner for every user, every moment. Predicted attention <b>${r.static.attention}</b>/100 · banner blindness risk high`;
  $("#blindBadge").classList.add("on");
  // ---- generative lock screen: stitch layers
  $("#lsLayers").innerHTML = g.layers.map((l) => `<div class="${l}"></div>`).join("");
  const [clk, date] = CLOCK[st.time_slot];
  $("#lsClock").textContent = clk; $("#lsDate").textContent = date;
  $("#lsTop").innerHTML = `<span>${st.city} · ${WICON[st.weather]} ${TEMP[st.weather]}</span><span>5G ▮▮▮ 82%</span>`;
  const w = [];
  if (st.live_event !== "none") w.push(`<div class="wdg"><span class="live">LIVE</span>${TAX.live_event[st.live_event]}${st.live_event === "cricket_live" ? " · IND 182/4 (17.2)" : st.live_event === "football_live" ? " · 1-1 (67')" : ""}</div>`);
  if (st.user_state === "just_missed_train") w.push(`<div class="wdg">🚆 Next train in 9 min · ${b.display} 2 min from exit</div>`);
  else if (st.user_state === "commuting") w.push(`<div class="wdg">🚇 On the move · store at next station</div>`);
  if (st.user_state === "working_out") w.push(`<div class="wdg">💓 142 bpm · 5.2 km · 28:41</div>`);
  $("#lsWidgets").innerHTML = w.join("");
  $("#lsProduct").src = `/api/assets/${st.brand}/${productFile}`;
  const accent = g.palette.find((c) => c.trim().toUpperCase() !== "#FFFFFF" && c.trim().toUpperCase() !== "#111111") || b.accent;
  const logo = await svg(st.brand, "logo.svg");
  $("#lsCard").innerHTML = `<div class="logo">${logo}</div><div class="h">${g.copy.headline}</div><div class="bd">${g.copy.body}</div>
    <span class="cta" style="background:${accent}">${g.copy.cta} →</span><span class="src">${g.copy_source === "llm" ? "copy: LLM ✓ guardrails" : "copy: template"}</span>`;
  $("#variantSub").textContent = `${g.theme_label} · ${g.angle_label} angle`;
  // ---- trace
  const t = r.timings;
  const steps = [["Lakebase profile", t.lakebase_profile_ms, "user store"], ["Vector Search", t.vector_search_ms, "brand registry"],
    ["Embedding re-score", t.embedding_ms, "gte-large"], ["Model scoring", t.score_ms, `${r.combos_scored} combos`],
    ["LLM copy", t.copy_ms, g.copy_source], ["Lakebase write", t.lakebase_write_ms ?? "–", "decision log"], ["Total", t.total_ms, "end-to-end"]];
  $("#trace").innerHTML = steps.map(([n, ms, i]) => `<div class="step">${n}<b>${ms} ms</b><i>${i}</i></div>`).join("");
  $("#modelSrc").textContent = `model v${r.model_version} · weights from ${r.model_source?.includes("Lakebase") ? "Lakebase" : "UC"}`;
  renderLeaderboard(r); renderMatches(r); renderKpis(r); renderRoi();
}

function renderLeaderboard(r) {
  const max = Math.max(...r.leaderboard.map((c) => c.ecpm));
  $("#leaderboard").innerHTML = `<div class="lb-row muted" style="font-size:10px"><span>Theme (best angle)</span><span>expected eCPM</span><span class="v">pCTR · eCPM</span></div>` +
    r.leaderboard.map((c) => `<div class="lb-row ${c.winner ? "win" : ""} ${c.theme_blocked ? "blocked" : ""}">
      <span>${c.label}${c.winner ? '<span class="tag win">WINNER</span>' : ""}${c.theme_blocked ? '<span class="tag block">BLOCKED</span>' : ""}</span>
      <span class="bar"><span style="width:${(c.ecpm / max) * 100}%"></span></span>
      <span class="v">${pct(c.pctr)} · ${usd(c.ecpm)}</span></div>`).join("");
  $("#why").innerHTML = `<b>Why this layout wins</b> (top learned weights for the winning combo):<br>` +
    r.why.map((x) => `<span class="f pos">${x.feature} <b>+${x.weight}</b></span>`).join("") +
    (r.against.length ? `<br>Holding it back: ` + r.against.map((x) => `<span class="f neg">${x.feature} <b>${x.weight}</b></span>`).join("") : "");
}
function renderMatches(r) {
  if (r.vs_error && !r.candidates.length) { $("#matches").innerHTML = `<div class="err">Vector Search: ${r.vs_error}</div>`; return; }
  const topId = r.component?.component_id;
  $("#matches").innerHTML = `<div class="muted" style="font-size:10.5px;margin-bottom:6px">Query: "${r.context_text}"</div>` +
    r.candidates.slice(0, 4).map((c) => {
      const safe = String(c.brand_safe).toLowerCase() === "true";
      return `<div class="match ${c.component_id === topId ? "top" : ""} ${safe ? "" : "rej"}">
        <b>${c.component_name}</b> · ${c.product}${c.component_id === topId ? ' <span class="tag win">USED</span>' : ""}${safe ? "" : ' <span class="tag block">GUARDRAIL</span>'}
        <span class="sim">cos ${c.similarity ?? "–"}</span>
        <div class="attrs">${c.creative_attributes}</div>${safe ? "" : `<div class="guard">⛔ ${c.guardrail_note}</div>`}</div>`;
    }).join("");
  const gr = r.guardrail;
  $("#guard").innerHTML = `🛡️ ${gr.blocked_combos} theme/angle combos blocked by ${TAX.brands[r.state.brand].display} guidelines` +
    (gr.unconstrained_winner ? `<br>Unconstrained model would have picked <b>${gr.unconstrained_winner.theme} / ${gr.unconstrained_winner.angle}</b>: blocked.` : "") +
    (r.generative.copy_issue ? `<br>${r.generative.copy_issue}` : "");
}

// ------------------------------------------------------------------ dashboard
function gauge(el, v, color) {
  const a = Math.PI * (1 - v / 100), R = 52, cx = 64, cy = 64;
  const x = cx + R * Math.cos(a), y = cy - R * Math.sin(a);
  $(el).innerHTML = `<svg viewBox="0 0 128 76" width="128"><path d="M12 64 A52 52 0 0 1 116 64" stroke="#262b38" stroke-width="11" fill="none" stroke-linecap="round"/>
    <path d="M12 64 A52 52 0 0 1 ${x.toFixed(1)} ${y.toFixed(1)}" stroke="${color}" stroke-width="11" fill="none" stroke-linecap="round"/>
    <text x="64" y="62" text-anchor="middle" fill="#fff" font-size="24" font-weight="800">${Math.round(v)}</text></svg>`;
}
function kpi(k, gen, stat, lift, tgt, met) {
  return `<div class="kpi"><div class="k">${k}</div><div class="vals"><span class="g">${gen}</span><span class="s">static ${stat}</span></div>
    <div class="lift ${lift.startsWith("-") ? "down" : "up"}">${lift}</div>${tgt ? `<div class="tgt ${met ? "met" : ""}">${met ? "✓ " : ""}${tgt}</div>` : ""}</div>`;
}
function renderKpis(r) {
  const g = r.generative, s = r.static, L = r.lift;
  gauge("#gStatic", s.attention, "#8a92a6"); gauge("#gGen", g.attention, "#ff3e6c");
  const cpeChange = L.cpe_generative / L.cpe_static - 1;
  $("#kpis").innerHTML =
    kpi("Predicted CTR", pct(g.pctr), pct(s.pctr), `${sgn(L.ctr)} CTR lift`) +
    kpi("Ad relevance score", g.relevance.toFixed(0), s.relevance.toFixed(0), `+${(g.relevance - s.relevance).toFixed(0)} pts`) +
    kpi("eCPM impact", usd(g.ecpm), usd(s.ecpm), `${sgn(L.ecpm)} eCPM`, "target +50–75%", L.ecpm >= 0.5) +
    kpi("Avg interaction", g.pdwell_s.toFixed(2) + "s", s.pdwell_s.toFixed(2) + "s", `${sgn(L.dwell)} dwell`, "target > 2.5s", g.pdwell_s > 2.5) +
    kpi("Cost per engagement", usd(L.cpe_generative, 3), usd(L.cpe_static, 3), `${sgn(cpeChange)} CPE`) +
    kpi("Ad fatigue / opt-out risk", pct(g.poptout, 2), pct(s.poptout, 2), `-${(L.optout_reduction * 100).toFixed(0)}% opt-outs`, "target -15–20%", L.optout_reduction >= 0.15);
}
function renderRoi() {
  if (!LAST) return;
  const M = +$("#impr").value; $("#imprVal").textContent = M + "M";
  const s = LAST.static.ecpm, g = LAST.generative.ecpm, days = 30, W = 360, H = 130, P = 26;
  const cum = (e) => Array.from({ length: days + 1 }, (_, d) => (e * M * 1000 * d)); // eCPM * (M*1e6/1000) per day
  const cs = cum(s), cg = cum(g), max = cg[days] || 1;
  const pts = (a) => a.map((v, i) => `${P + (i / days) * (W - P - 6)},${H - 18 - (v / max) * (H - 30)}`).join(" ");
  const fmt = (v) => v >= 1e6 ? "$" + (v / 1e6).toFixed(2) + "M" : "$" + (v / 1e3).toFixed(0) + "K";
  $("#roiChart").innerHTML = `<svg viewBox="0 0 ${W} ${H}" width="100%">
    <line x1="${P}" y1="${H - 18}" x2="${W - 6}" y2="${H - 18}" stroke="#262b38"/>
    <polygon points="${P},${H - 18} ${pts(cg)} ${W - 6},${H - 18}" fill="#ff3e6c22"/>
    <polyline points="${pts(cg)}" fill="none" stroke="#ff3e6c" stroke-width="2.5"/>
    <polyline points="${pts(cs)}" fill="none" stroke="#8a92a6" stroke-width="2" stroke-dasharray="4 3"/>
    <text x="${W - 8}" y="${H - 22 - (H - 30)}" text-anchor="end" fill="#ff3e6c" font-size="10" font-weight="700">Generative ${fmt(cg[days])}</text>
    <text x="${W - 8}" y="${H - 22 - (cs[days] / max) * (H - 30)}" text-anchor="end" fill="#8a92a6" font-size="10">Static ${fmt(cs[days])}</text>
    <text x="${P}" y="${H - 4}" fill="#8a92a6" font-size="9">day 0</text><text x="${W - 6}" y="${H - 4}" text-anchor="end" fill="#8a92a6" font-size="9">day 30</text></svg>`;
  $("#roiSum").innerHTML = `<span>Incremental 30-day earnings</span><b style="color:#2fd08a">+${fmt(cg[days] - cs[days])}</b>`;
}
async function loadAnalytics() {
  try {
    const a = await api(`/api/analytics?brand=${S.brand}`);
    if (a.scorecard) {
      const lbl = { static_banner: "Static banner", standard_video: "Std video", glance_generative: "Generative" };
      $("#hist").innerHTML = `<div class="hist-row h"><span>Format</span><span>CTR</span><span>Dwell</span><span>eCPM</span><span>Opt-out</span></div>` +
        a.scorecard.map((r) => `<div class="hist-row"><span class="${r.ad_format === "glance_generative" ? "gen" : ""}">${lbl[r.ad_format]}</span>
          <span>${pct(+r.ctr)}</span><span>${(+r.avg_dwell_s).toFixed(2)}s</span><span>${usd(r.ecpm)}</span><span>${pct(+r.opt_out_rate)}</span></div>`).join("");
    } else $("#hist").innerHTML = `<div class="err">${a.scorecard_error || ""}</div>`;
    if (a.policy) {
      const o = a.policy.find((p) => p.policy.startsWith("generative - optimized")), l = a.policy.find((p) => p.policy.startsWith("generative - logged"));
      $("#policy").innerHTML = `Off-policy evaluation (model v${o.model_version}, 6,000 held-out contexts): naive generative <b>${sgn(+l.ecpm_lift_vs_static)}</b> eCPM →
        optimized engine <b style="color:#2fd08a">${sgn(+o.ecpm_lift_vs_static)}</b> eCPM, ${(+o.pred_dwell_s).toFixed(2)}s dwell, <b>-${(o.opt_out_reduction_vs_static * 100).toFixed(0)}%</b> opt-outs vs static.`;
    }
  } catch (e) { $("#hist").innerHTML = `<div class="err">${e.message}</div>`; }
}
async function refreshDecisions() {
  try {
    const d = await api("/api/decisions"), s = d.stats;
    $("#decisions").innerHTML = `<div class="dec-stats"><b>${s.n}</b> decisions · avg CTR lift <b>${sgn(+s.avg_ctr_lift || 0)}</b> · avg eCPM lift <b>${sgn(+s.avg_ecpm_lift || 0)}</b> · avg ${Math.round(s.avg_latency || 0)} ms</div>` +
      d.recent.map((r) => `<div class="dec-row"><span class="t">${new Date(r.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
        <span>${TAX.brands[r.brand].display} · ${TAX.weather[r.weather]} · ${TAX.user_state[r.user_state]} → <b>${TAX.themes[r.chosen_theme].label}</b></span>
        <span class="l">${sgn(r.ecpm_generative / r.ecpm_static - 1)}</span></div>`).join("");
  } catch (e) { $("#decisions").innerHTML = `<div class="err">${e.message}</div>`; }
}

// ------------------------------------------------------------------ genie
function addMsg(cls, html) { const d = document.createElement("div"); d.className = "msg " + cls; d.innerHTML = html; $("#genieBody").appendChild(d); $("#genieBody").scrollTop = 1e9; return d; }
async function askGenie(q) {
  addMsg("u", q); const pending = addMsg("a", "Genie is thinking… (writing SQL over the metric views)");
  try {
    const r = await api("/api/genie", { question: q, conversation_id: GENIE_CONV });
    if (r.conversation_id) GENIE_CONV = r.conversation_id;
    let html = r.error ? `<span class="err">${r.error}</span>` : (r.text || r.description || "");
    if (r.columns?.length) html += `<table><tr>${r.columns.map((c) => `<th>${c}</th>`).join("")}</tr>` +
      r.rows.slice(0, 15).map((row) => `<tr>${row.map((v) => `<td>${v !== null && !isNaN(v) && String(v).includes(".") ? (+v).toFixed(4) : v ?? ""}</td>`).join("")}</tr>`).join("") + "</table>";
    if (r.sql) html += `<details><summary>SQL</summary><pre>${r.sql.replace(/</g, "&lt;")}</pre></details>`;
    pending.innerHTML = html || "(no answer)";
  } catch (e) { pending.innerHTML = `<span class="err">${e.message}</span>`; }
}

// ------------------------------------------------------------------ boot
async function boot() {
  const b = await api("/api/bootstrap");
  TAX = b.taxonomy; PERSONAS = b.personas;
  const st = b.status;
  $("#status").innerHTML = `Lakebase <span class="${st.lakebase === "ok" ? "ok" : "bad"}">${st.lakebase === "ok" ? "●" : "✕"}</span> · models <span class="${String(st.models).startsWith("ok") ? "ok" : "bad"}">${st.model_version ? "v" + st.model_version : "✕"}</span> · Genie <span class="${b.genie_enabled ? "ok" : "bad"}">${b.genie_enabled ? "●" : "off"}</span>`;
  renderControls();
  $("#genBtn").onclick = generate; $("#liveBtn").onclick = pullLive;
  document.querySelectorAll("[data-preset]").forEach((a) => (a.onclick = () => applyPreset(a.dataset.preset)));
  $("#impr").oninput = renderRoi;
  $("#genieFab").onclick = () => $("#genie").classList.toggle("on"); $("#genieClose").onclick = () => $("#genie").classList.remove("on");
  document.querySelectorAll(".genie-hint a").forEach((a) => (a.onclick = () => askGenie(a.textContent)));
  $("#genieForm").onsubmit = (e) => { e.preventDefault(); const q = $("#genieQ").value.trim(); if (q) { $("#genieQ").value = ""; askGenie(q); } };
  loadAnalytics(); refreshDecisions();
  generate();
}
boot().catch((e) => ($("#status").innerHTML = `<span class="bad">${e.message}</span>`));
