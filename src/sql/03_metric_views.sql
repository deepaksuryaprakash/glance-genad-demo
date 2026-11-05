-- Governed KPI layer for dashboards, the app and the Genie agent

CREATE OR REPLACE VIEW glance_genad.gold.mv_ad_effectiveness
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
source: glance_genad.gold.fact_ad_impressions
comment: "Ad effectiveness KPIs for Glance lock-screen generative ads vs traditional static banners and programmatic video. One row per impression in the source."
dimensions:
  - name: event_date
    expr: event_date
    display_name: Date
  - name: event_week
    expr: DATE_TRUNC('WEEK', event_date)
    display_name: Week
  - name: brand
    expr: brand
    synonyms: [advertiser, client]
  - name: ad_format
    expr: ad_format
    comment: "static_banner = traditional control banner, standard_video = programmatic video, glance_generative = generative contextual lock-screen layout"
    synonyms: [format, creative type, ad type]
  - name: experience_group
    expr: experience_group
    comment: "Traditional (control) vs Generative (variant)"
    synonyms: [test group, control vs variant, ab group]
  - name: placement
    expr: placement
  - name: segment
    expr: segment
    synonyms: [audience, user segment, persona, behavioral segment]
  - name: city
    expr: city
  - name: weather
    expr: weather
  - name: time_slot
    expr: time_slot
    synonyms: [daypart, time of day]
  - name: user_state
    expr: user_state
    synonyms: [user context, moment]
  - name: live_event
    expr: live_event
    synonyms: [sports event, match]
  - name: phone_skin
    expr: phone_skin
    synonyms: [theme skin, wallpaper theme]
  - name: layout_theme
    expr: layout_theme
    comment: "Generative layout theme chosen by the engine (none for traditional formats)"
    synonyms: [creative theme, layout]
  - name: copy_angle
    expr: copy_angle
    synonyms: [message angle, copy strategy]
  - name: unlock_band
    expr: unlock_band
  - name: device_os
    expr: device_os
measures:
  - name: impressions
    expr: COUNT(1)
    synonyms: [impression count, views, ad views]
  - name: clicks
    expr: SUM(clicked)
    synonyms: [taps]
  - name: ctr
    expr: SUM(clicked) / COUNT(1)
    comment: "Click-through rate = clicks / impressions"
    display_name: CTR
    synonyms: [click through rate, click rate]
  - name: avg_interaction_duration_s
    expr: AVG(dwell_ms) / 1000.0
    comment: "Average active interaction duration (dwell) in seconds. Target > 2.5s."
    display_name: Avg interaction duration (s)
    synonyms: [dwell time, attention time, interaction time, engagement duration]
  - name: engaged_view_rate
    expr: AVG(engaged)
    comment: "Share of impressions with >= 2.5s of active interaction"
    synonyms: [engagement rate, attention rate]
  - name: revenue_usd
    expr: SUM(revenue_usd)
    synonyms: [earnings, ad revenue, spend, advertiser spend]
  - name: ecpm_usd
    expr: 1000 * SUM(revenue_usd) / COUNT(1)
    comment: "Effective cost per mille = revenue per 1,000 impressions"
    display_name: eCPM (USD)
    synonyms: [ecpm, effective cpm, earnings per thousand impressions, yield]
  - name: engagements
    expr: SUM(GREATEST(clicked, engaged))
    comment: "Impressions that were clicked or had >= 2.5s active interaction"
  - name: cost_per_engagement_usd
    expr: SUM(revenue_usd) / NULLIF(SUM(GREATEST(clicked, engaged)), 0)
    comment: "Advertiser spend divided by engagements (click or >= 2.5s interaction)"
    display_name: Cost per engagement (USD)
    synonyms: [cpe, cost per engagement]
  - name: opt_out_rate
    expr: AVG(opted_out)
    comment: "Ad-related lock-screen opt-outs + app uninstalls per impression (ad fatigue / churn)"
    synonyms: [churn rate, ad fatigue, opt out rate, uninstall rate]
  - name: lockscreen_optouts
    expr: SUM(lockscreen_optout)
  - name: app_uninstalls
    expr: SUM(app_uninstall)
    synonyms: [uninstalls]
$$;

CREATE OR REPLACE VIEW glance_genad.gold.mv_live_simulations
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
source: glance_genad.gold.live_simulation_log
comment: "Real-time decisions made by the Glance generative engine in the demo app, with model-predicted lift vs the static control."
dimensions:
  - name: decision_date
    expr: decision_date
  - name: brand
    expr: brand
  - name: segment
    expr: segment
  - name: weather
    expr: weather
  - name: time_slot
    expr: time_slot
  - name: user_state
    expr: user_state
  - name: live_event
    expr: live_event
  - name: chosen_theme
    expr: chosen_theme
    synonyms: [winning theme, selected layout]
  - name: chosen_angle
    expr: chosen_angle
  - name: matched_component
    expr: matched_component
    synonyms: [brand asset, creative component]
  - name: copy_source
    expr: copy_source
measures:
  - name: decisions
    expr: COUNT(1)
    synonyms: [simulations, generations]
  - name: avg_predicted_ctr_generative
    expr: AVG(pctr_generative)
  - name: avg_predicted_ctr_static
    expr: AVG(pctr_static)
  - name: predicted_ctr_lift
    expr: AVG(pctr_generative) / AVG(pctr_static) - 1
    synonyms: [ctr lift, uplift]
  - name: predicted_ecpm_lift
    expr: AVG(ecpm_generative) / AVG(ecpm_static) - 1
    synonyms: [ecpm lift, yield lift]
  - name: avg_predicted_dwell_s
    expr: AVG(pdwell_generative_s)
  - name: predicted_opt_out_reduction
    expr: 1 - AVG(poptout_generative) / AVG(poptout_static)
  - name: avg_attention_score
    expr: AVG(attention_generative)
  - name: avg_relevance_score
    expr: AVG(relevance_score)
  - name: guardrail_blocks
    expr: SUM(blocked_by_guardrail)
  - name: avg_latency_ms
    expr: AVG(latency_ms)
$$;
