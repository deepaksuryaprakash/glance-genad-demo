-- Seed the Glance GenAd Lakebase context DB (idempotent)
SET search_path = glance_ops;

-- ---------- User Profile Store: 20,000 synthetic Glance users (formula mirrored in src/jobs/generate_ad_logs.py)
INSERT INTO user_profiles (user_id, full_name, email, phone, device_ad_id, city, segment, preferred_skin,
                           device_os, behavior_vector, daily_unlocks)
SELECT
  'U' || lpad(n::text, 5, '0'),
  (ARRAY['Aditi','Rahul','Ananya','Vikram','Isha','Arjun','Meera','Karan','Nisha','Siddharth','Putri','Budi'])[1 + (n % 12)]
    || ' ' ||
  (ARRAY['Sharma','Rao','Kapoor','Reddy','Das','Menon','Patel','Joshi','Kulkarni','Bose','Santoso','Wijaya'])[1 + ((n / 12) % 12)],
  'user' || n || '@example.com',
  '+91-9' || lpad(((n * 7919) % 1000000000)::text, 9, '0'),
  md5('gaid' || n)::uuid::text,
  (ARRAY['Bengaluru','Mumbai','Delhi','Hyderabad','Pune','Jakarta'])[1 + ((n / 5) % 6)],
  (ARRAY['fitness_enthusiast','casual_gamer','tech_professional','daily_commuter','night_owl'])[1 + (n % 5)],
  (ARRAY['dark_minimal','vibrant_neon','pastel_soft','nature_green'])[1 + ((n * 7) % 4)],
  CASE WHEN n % 7 = 0 THEN 'iOS' ELSE 'Android' END,
  jsonb_build_object(
    'sports',   round((CASE WHEN n % 5 = 0 THEN 0.8 ELSE 0.35 END + random() * 0.2)::numeric, 2),
    'fitness',  round((CASE WHEN n % 5 = 0 THEN 0.85 ELSE 0.25 END + random() * 0.15)::numeric, 2),
    'gaming',   round((CASE WHEN n % 5 = 1 THEN 0.9 WHEN n % 5 = 4 THEN 0.5 ELSE 0.15 END + random() * 0.1)::numeric, 2),
    'tech',     round((CASE WHEN n % 5 = 2 THEN 0.9 ELSE 0.3 END + random() * 0.1)::numeric, 2),
    'coffee',   round((CASE WHEN n % 5 IN (2, 3) THEN 0.75 ELSE 0.35 END + random() * 0.2)::numeric, 2),
    'commute',  round((CASE WHEN n % 5 = 3 THEN 0.95 ELSE 0.4 END + random() * 0.05)::numeric, 2),
    'night',    round((CASE WHEN n % 5 = 4 THEN 0.9 ELSE 0.3 END + random() * 0.1)::numeric, 2)),
  60 + (n * 37) % 90
FROM generate_series(1, 20000) AS n
ON CONFLICT (user_id) DO NOTHING;

-- Named demo personas for the simulation dropdown
INSERT INTO user_profiles (user_id, full_name, email, phone, device_ad_id, city, segment, preferred_skin, device_os,
                           behavior_vector, daily_unlocks, is_demo_persona, persona_blurb) VALUES
 ('U90001','Aarav Mehta','aarav.mehta@example.com','+91-9811100001', md5('p1')::uuid::text,'Bengaluru','fitness_enthusiast','nature_green','Android',
  '{"sports":0.92,"fitness":0.97,"gaming":0.12,"tech":0.35,"coffee":0.40,"commute":0.45,"night":0.15}',84,true,'Marathon trainee, runs 5x a week at 6 AM, tracks every split'),
 ('U90002','Priya Nair','priya.nair@example.com','+91-9811100002', md5('p2')::uuid::text,'Mumbai','daily_commuter','pastel_soft','Android',
  '{"sports":0.30,"fitness":0.35,"gaming":0.10,"tech":0.40,"coffee":0.88,"commute":0.98,"night":0.20}',112,true,'Takes the 8:12 local to BKC every weekday; coffee is non-negotiable'),
 ('U90003','Rohan Gupta','rohan.gupta@example.com','+91-9811100003', md5('p3')::uuid::text,'Bengaluru','tech_professional','dark_minimal','iOS',
  '{"sports":0.45,"fitness":0.40,"gaming":0.35,"tech":0.97,"coffee":0.91,"commute":0.55,"night":0.50}',95,true,'Backend engineer at an ORR tech park; lives on cold brew and stand-ups'),
 ('U90004','Sneha Iyer','sneha.iyer@example.com','+91-9811100004', md5('p4')::uuid::text,'Hyderabad','casual_gamer','vibrant_neon','Android',
  '{"sports":0.40,"fitness":0.20,"gaming":0.96,"tech":0.60,"coffee":0.45,"commute":0.35,"night":0.70}',140,true,'BGMI between classes, 140 unlocks a day, follows esports finals'),
 ('U90005','Kabir Singh','kabir.singh@example.com','+91-9811100005', md5('p5')::uuid::text,'Delhi','night_owl','dark_minimal','Android',
  '{"sports":0.85,"fitness":0.30,"gaming":0.55,"tech":0.50,"coffee":0.50,"commute":0.25,"night":0.97}',101,true,'Watches cricket highlights after 11 PM; late-night snacker'),
 ('U90006','Dewi Lestari','dewi.lestari@example.com','+62-81100006', md5('p6')::uuid::text,'Jakarta','daily_commuter','nature_green','Android',
  '{"sports":0.35,"fitness":0.55,"gaming":0.15,"tech":0.45,"coffee":0.82,"commute":0.93,"night":0.20}',97,true,'KRL commuter from Bogor; grabs coffee between transfers')
ON CONFLICT (user_id) DO NOTHING;

-- ---------- Context Database: current live triggers per city (the stream job keeps appending)
INSERT INTO context_signals (city, signal_type, signal_key, signal_value, temp_c, intensity, payload)
SELECT * FROM (VALUES
 ('Bengaluru','weather','heavy_rain','Heavy rain, 21°C, waterlogging on ORR', 21.0, 0.85, '{"source":"imd_nowcast","humidity":94}'::jsonb),
 ('Mumbai','weather','heavy_rain','Monsoon downpour, 26°C, local trains delayed', 26.0, 0.92, '{"source":"imd_nowcast","humidity":97}'::jsonb),
 ('Delhi','weather','cold','Cold wave, 7°C, dense fog', 7.0, 0.60, '{"source":"imd_nowcast","aqi":312}'::jsonb),
 ('Hyderabad','weather','sunny','Clear skies, 31°C', 31.0, 0.20, '{"source":"imd_nowcast"}'::jsonb),
 ('Pune','weather','cloudy','Overcast, 24°C', 24.0, 0.30, '{"source":"imd_nowcast"}'::jsonb),
 ('Jakarta','weather','hot_humid','Hot and humid, 33°C', 33.0, 0.70, '{"source":"bmkg"}'::jsonb),
 ('Bengaluru','live_event','cricket_live','IND 182/4 (17.2 ov) vs AUS — Kohli 74*', NULL, 0.90, '{"match":"IND vs AUS T20I","venue":"Chinnaswamy"}'::jsonb),
 ('Mumbai','live_event','football_live','Mumbai City 1-1 Bengaluru FC (67'')', NULL, 0.75, '{"match":"ISL","venue":"Mumbai Football Arena"}'::jsonb),
 ('Delhi','live_event','city_marathon','Delhi Half Marathon this Sunday — 42k registered', NULL, 0.55, '{"event":"ADHM"}'::jsonb),
 ('Hyderabad','live_event','esports_final','BGMI Masters Grand Final — Map 3 live', NULL, 0.80, '{"event":"BGMI Masters"}'::jsonb),
 ('Mumbai','transit','train_delay','Western line locals running 18 min late', NULL, 0.70, '{"line":"WR Slow"}'::jsonb),
 ('Bengaluru','transit','train_delay','Purple line metro: 9 min headway', NULL, 0.40, '{"line":"Namma Metro Purple"}'::jsonb)
) AS v(city, signal_type, signal_key, signal_value, temp_c, intensity, payload)
WHERE NOT EXISTS (SELECT 1 FROM context_signals);

-- ---------- Creative Asset Bucket (files in /Volumes/glance_genad/raw/creative_assets)
INSERT INTO creative_assets (asset_id, brand, asset_type, name, volume_path, baseline_copy) VALUES
 ('nike_product_pegasus_trail','nike','product_image','Pegasus Trail 5 GORE-TEX (raw product shot)','/Volumes/glance_genad/raw/creative_assets/nike/product_shoe.svg',NULL),
 ('nike_logo','nike','logo','Nike wordmark (approved lockup)','/Volumes/glance_genad/raw/creative_assets/nike/logo.svg',NULL),
 ('nike_baseline_copy','nike','baseline_copy','Baseline programmatic copy',NULL,'Shop Nike Running Shoes. New season styles. 10% off. Buy Now.'),
 ('starbucks_product_latte','starbucks','product_image','Caffe Latte (raw product shot)','/Volumes/glance_genad/raw/creative_assets/starbucks/product_cup.svg',NULL),
 ('starbucks_logo','starbucks','logo','Starbucks wordmark (approved lockup)','/Volumes/glance_genad/raw/creative_assets/starbucks/logo.svg',NULL),
 ('starbucks_baseline_copy','starbucks','baseline_copy','Baseline programmatic copy',NULL,'Buy Coffee Now. 10% off your next order. Order.')
ON CONFLICT (asset_id) DO NOTHING;

-- ---------- Brand asset component registry (the "safe" creative building blocks)
INSERT INTO brand_asset_components (component_id, brand, component_name, product, creative_attributes, description, approved_copy, palette, brand_safe, guardrail_note) VALUES
 ('nk_gtx_waterproof','nike','All-weather GORE-TEX','Pegasus Trail 5 GORE-TEX','waterproof, durable, grip, wet roads, all-weather',
  'Waterproof GORE-TEX upper and sticky rubber grip keep feet dry and stable on rain-soaked roads, puddles and monsoon commutes. Durable, built for heavy rain.',
  'Rain or shine, keep moving.','#111111,#1E3A8A,#FFFFFF',true,NULL),
 ('nk_zoom_speed','nike','Morning speed','Air Zoom Pegasus 41','responsive, speed, energy, sunrise run, morning training',
  'Responsive Air Zoom cushioning for fast sunrise runs and morning training sessions in bright sunny weather. Energy return for tempo days.',
  'Own the morning.','#FA5400,#FFFFFF,#111111',true,NULL),
 ('nk_drifit_heat','nike','Dri-FIT heat management','Dri-FIT Miler Tee','sweat-wicking, breathable, cooling, hot humid, heat',
  'Dri-FIT fabric wicks sweat and breathes in hot, humid afternoons so you stay cool through tough sessions in the heat.',
  'Stay cool. Go further.','#FFFFFF,#6E6E6E,#FA5400',true,NULL),
 ('nk_marathon_community','nike','Race-day community','Nike Run Club','marathon, race day, community, training plan, finish line',
  'Join thousands of runners on race weekend with Nike Run Club guided runs and a marathon training plan that gets you to the finish line.',
  'Your finish line is waiting.','#111111,#FA5400,#FFFFFF',true,NULL),
 ('nk_reflective_night','nike','Night visibility','Pegasus Shield Reflective','reflective, visibility, night run, safety, late evening',
  '360-degree reflective details for visibility and safety on late-night and early-dark runs through the city.',
  'Be seen. Run on.','#111111,#6E6E6E,#FFFFFF',true,NULL),
 ('nk_fan_jersey','nike','Match-day fan kit','India Cricket Fan Jersey','fan, live match, jersey, team pride, stadium',
  'Official fan jersey for live match nights. Wear your team pride in the stadium or on the couch while the score climbs.',
  'Bleed blue. Every ball.','#1E3A8A,#FA5400,#FFFFFF',true,NULL),
 ('nk_comfort_recovery','nike','Recovery comfort','Nike Calm Slide','comfort, recovery, relaxing, home, soft cushioning',
  'Soft foam slides for recovery days and relaxing at home after training. Plush comfort for downtime.',
  'Recovery is training too.','#6E6E6E,#FFFFFF,#111111',true,NULL),
 ('nk_neon_pink_recolor','nike','Neon pink swoosh recolor','Pegasus Trail 5 (AI recolor)','neon, fluorescent pink, rgb glow, gamer, bold color',
  'AI-generated fluorescent neon pink recolor of the shoe and swoosh with RGB gamer glow for esports and nightlife audiences.',
  'Glow up your game.','#FF00C8,#00FFF0',false,'Violates Nike brand guidelines: swoosh/product may not be recolored.'),
 ('sb_hot_latte','starbucks','Hot latte warm-up','Caffe Latte','hot, warm, cozy, rain, cold weather, comfort, steam',
  'A steaming hot Caffe Latte to warm up on cold, rainy, drizzly days. Cozy comfort in a cup when the weather turns.',
  'Warm up with a hot latte.','#00704A,#CBA258,#FFFFFF',true,NULL),
 ('sb_mobile_order','starbucks','Mobile Order & Pay','Mobile Order & Pay','pre-order, skip the queue, time-saving, commute, on the go, train station',
  'Order ahead in the app and pick up at the store near your next station. Skip the queue when you are running late or just missed your train.',
  'Tap to pre-order. Skip the line.','#00704A,#1E3932,#FFFFFF',true,NULL),
 ('sb_cold_brew','starbucks','Iced cold brew refresh','Cold Brew','iced, cold brew, refreshing, hot humid, heat, afternoon',
  'Slow-steeped iced Cold Brew to cool down on hot, humid afternoons. Smooth and refreshing.',
  'Beat the heat. Sip cold brew.','#1E3932,#D4E9E2,#FFFFFF',true,NULL),
 ('sb_office_focus','starbucks','Desk-side focus','Americano + Work Hours','office, focus, productivity, meeting, work break',
  'A bold Americano delivered to your desk to power through back-to-back meetings and focused work blocks at the office.',
  'Fuel the next meeting.','#00704A,#FFFFFF,#1E3932',true,NULL),
 ('sb_match_share','starbucks','Match-night share pack','Frappuccino Share Pack','share, friends, live match, watch party, celebration',
  'A Frappuccino share pack for live match watch parties with friends. Celebrate every boundary together.',
  'Watch party, sorted.','#00704A,#CBA258,#FFFFFF',true,NULL),
 ('sb_night_decaf','starbucks','Late-night wind-down','Chamomile Tea & Decaf','calm, late night, wind down, decaf, relaxing, home',
  'Caffeine-free chamomile tea and decaf for quiet late-night wind-downs at home.',
  'Slow down. Sip something calm.','#1E3932,#D4E9E2,#CBA258',true,NULL),
 ('sb_rewards_morning','starbucks','Morning rewards','Starbucks Rewards','rewards, stars, morning ritual, breakfast, sunrise',
  'Earn double Stars on your morning ritual coffee and breakfast before 10 AM.',
  'Double Stars before 10.','#00704A,#CBA258,#FFFFFF',true,NULL),
 ('sb_energy_shot','starbucks','Extreme energy shot','Espresso Triple Shot','extreme energy, workout fuel, pre-gym, high intensity',
  'Triple espresso positioned as an extreme pre-workout energy shot for high-intensity gym sessions.',
  'Max energy. Crush the gym.','#00704A,#000000',false,'Violates Starbucks guidelines: no health/energy-drink claims or high-intensity sports framing.')
ON CONFLICT (component_id) DO NOTHING;
