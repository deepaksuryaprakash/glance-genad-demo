# Genie agent transcript via the app (collected 2026-11-09 10:16 UTC)

## Q: What is the CTR lift of generative vs static banner by brand?

**Answer:** Generative ads have a higher CTR than **static banners** for both brands in the results. - **Nike:** static **0.95%**, generative **1.22%**, lift **29.10%**
- **Starbucks:** static **1.24%**, generative **1.44%**, lift **16.86%**

Across these 2 brands, **Nike** shows the larger CTR lift from generative ads.

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
  (try_divide(`g`.`ctr`,`s`.`ctr`) - 1) * 100 AS `ctr_lift_pct`
FROM `f` `g`
JOIN `f` `s`
  ON `g`.`brand` = `s`.`brand`
 AND `s`.`ad_format` = 'static_banner'
WHERE `g`.`ad_format` = 'glance_generative'
ORDER BY `g`.`brand`
```

| brand | static_ctr_pct | generative_ctr_pct | ctr_lift_pct |
|---|---|---|---|
| nike | 0.9462463660719376 | 1.2215911205735002 | 29.098632700125982 |
| starbucks | 1.2354692507537974 | 1.4437857636692606 | 16.861327207323274 |

## Q: Which layout theme has the highest CTR in heavy rain?

**Answer:** In **heavy rain**, the **cozy_warm** layout theme has the highest CTR among generative ads, with **CTR = 1.82%** based on **3,350 impressions**. The same **cozy_warm** theme also shows **average interaction duration = 3.03 seconds**, which is above the **2.5-second** engagement target.

Would you prefer to see the layout theme with the highest total clicks or the highest CTR weighted by impressions instead?

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
| cozy_warm | 3350 | 0.018208955223880597 | 3.0279426865671644 |

## Q: Which user segment has the biggest reduction in opt-out rate with generative ads?

**Answer:** The user segment with the biggest reduction in opt-out rate is **fitness_enthusiast**. For segment **fitness_enthusiast**, the static banner opt-out rate is **1.0947%**, the generative ad opt-out rate is **0.8406%**, and the reduction is **23.2164%**.

Would you prefer to see the user segment with the biggest absolute decrease in opt-out rate instead of the relative percentage reduction?

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
  (1 - try_divide(`g`.`opt_out_rate`, `s`.`opt_out_rate`)) * 100 AS `opt_out_rate_reduction_pct`
FROM `seg_rates` `g`
JOIN `seg_rates` `s`
  ON `g`.`segment` = `s`.`segment`
 AND `s`.`ad_format` = 'static_banner'
WHERE `g`.`ad_format` = 'glance_generative'
ORDER BY `opt_out_rate_reduction_pct` DESC
LIMIT 1
```

| segment | static_opt_out_rate_pct | generative_opt_out_rate_pct | opt_out_rate_reduction_pct |
|---|---|---|---|
| fitness_enthusiast | 1.0947438110325587 | 0.840583984663029 | 23.216374809171736 |

