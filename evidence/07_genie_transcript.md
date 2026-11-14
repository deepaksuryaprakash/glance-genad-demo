# Genie agent transcript via the app (collected 2026-11-14 15:38 UTC)

## Q: What is the CTR lift of generative vs static banner by brand?

**Answer:** CTR lift is **27.72%** for **Nike** and **16.90%** for **Starbucks** when comparing generative ads to static banners. In both brands shown, generative ads have higher CTR than static banners: **Nike** rose from **0.95%** to **1.22%**, and **Starbucks** rose from **1.23%** to **1.44%**; **Nike** shows the larger lift.

```sql
WITH `f` AS (
  SELECT
    `brand`,
    `ad_format`,
    MEASURE(`ctr`) AS `ctr`
  FROM `glance_genad`.`gold`.`mv_ad_effectiveness`
  WHERE `brand` IS NOT NULL
    AND `ad_format` IS NOT NULL
  GROUP BY ALL
)
SELECT
  `g`.`brand`,
  `s`.`ctr` * 100 AS `static_ctr_pct`,
  `g`.`ctr` * 100 AS `generative_ctr_pct`,
  100 * (try_divide(`g`.`ctr`,`s`.`ctr`) - 1) AS `ctr_lift_pct`
FROM `f` AS `g`
JOIN `f` AS `s`
  ON `g`.`brand` = `s`.`brand`
 AND `s`.`ad_format` = 'static_banner'
WHERE `g`.`ad_format` = 'glance_generative'
ORDER BY `g`.`brand`
```

| brand | static_ctr_pct | generative_ctr_pct | ctr_lift_pct |
|---|---|---|---|
| nike | 0.9517296403943695 | 1.2155633797574827 | 27.721500746135042 |
| starbucks | 1.2330807098750796 | 1.4414944473045526 | 16.901873150751577 |

## Q: Which layout theme has the highest CTR in heavy rain?

**Answer:** In **heavy rain**, the layout theme with the highest CTR is **cozy_warm**, with **CTR 1.82%**, **3,346 impressions**, and **average interaction duration 3.02 seconds**. In this result, **cozy_warm** is the top-performing heavy-rain generative theme and its **3.02-second** interaction duration is above the **2.5-second** engagement target.

```sql
SELECT `layout_theme`, MEASURE(`impressions`) AS `impressions`, MEASURE(`ctr`) AS `ctr`, MEASURE(`avg_interaction_duration_s`) AS `avg_dwell_s`
FROM `glance_genad`.`gold`.`mv_ad_effectiveness`
WHERE `ad_format` = 'glance_generative'
  AND `weather` = 'heavy_rain'
  AND `layout_theme` IS NOT NULL
GROUP BY ALL
ORDER BY `ctr` DESC
LIMIT 1
```

| layout_theme | impressions | ctr | avg_dwell_s |
|---|---|---|---|
| cozy_warm | 3346 | 0.018230723251643755 | 3.020122833233712 |

## Q: Which user segment has the biggest reduction in opt-out rate with generative ads?

**Answer:** The user segment with the **biggest reduction** in opt-out rate is **fitness_enthusiast**. For **fitness_enthusiast**, the static banner opt-out rate is **1.09%**, the generative ad opt-out rate is **0.84%**, and the opt-out reduction is **22.58%**.

```sql
WITH `seg_rates` AS (
  SELECT
    `segment`,
    `ad_format`,
    MEASURE(`opt_out_rate`) AS `opt_out_rate`
  FROM `glance_genad`.`gold`.`mv_ad_effectiveness`
  WHERE `segment` IS NOT NULL
    AND `ad_format` IS NOT NULL
  GROUP BY ALL
)
SELECT
  `g`.`segment`,
  `s`.`opt_out_rate` * 100 AS `static_opt_out_rate_pct`,
  `g`.`opt_out_rate` * 100 AS `generative_opt_out_rate_pct`,
  100 * try_divide((`s`.`opt_out_rate` - `g`.`opt_out_rate`), `s`.`opt_out_rate`) AS `opt_out_reduction_pct`
FROM `seg_rates` AS `g`
JOIN `seg_rates` AS `s`
  ON `g`.`segment` = `s`.`segment`
 AND `s`.`ad_format` = 'static_banner'
WHERE `g`.`ad_format` = 'glance_generative'
ORDER BY `opt_out_reduction_pct` DESC, `g`.`segment` ASC
LIMIT 1
```

| segment | static_opt_out_rate_pct | generative_opt_out_rate_pct | opt_out_reduction_pct |
|---|---|---|---|
| fitness_enthusiast | 1.0902726864224392 | 0.8440684838097343 | 22.581892188878534 |

