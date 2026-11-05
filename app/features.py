"""Shared feature builder for the CTR / dwell / opt-out models.

The SAME function runs in the training job (on historical logs) and inside the Databricks App
(on the live state vector), so online scoring is exactly consistent with training.

State vector = (ad_format, brand, segment, weather, time_slot, user_state, live_event, phone_skin)
Action       = (layout_theme, copy_angle)   -- only for glance_generative
Features are sparse one-hot crosses ("theme=rain_atmos|weather=heavy_rain" ...) so a linear model
learns context x creative interactions and every weight is explainable in the UI.
"""

CONTEXT_DIMS = ("segment", "weather", "time_slot", "user_state", "live_event", "phone_skin")


def build_features(ad_format, brand, segment, weather, time_slot, user_state, live_event, phone_skin,
                   layout_theme="none", copy_angle="none"):
    ctx = {"segment": segment, "weather": weather, "time_slot": time_slot, "user_state": user_state,
           "live_event": live_event, "phone_skin": phone_skin}
    f = [f"fmt={ad_format}", f"brand={brand}", f"fmt={ad_format}|brand={brand}"]
    for d, v in ctx.items():
        f.append(f"{d}={v}")
        f.append(f"brand={brand}|{d}={v}")
        f.append(f"fmt={ad_format}|{d}={v}")
    if ad_format == "glance_generative" and layout_theme != "none":
        f += [f"theme={layout_theme}", f"angle={copy_angle}", f"theme={layout_theme}|brand={brand}",
              f"angle={copy_angle}|brand={brand}", f"theme={layout_theme}|angle={copy_angle}"]
        for d, v in ctx.items():
            f.append(f"theme={layout_theme}|{d}={v}")
            if d != "phone_skin":
                f.append(f"angle={copy_angle}|{d}={v}")
    return f
