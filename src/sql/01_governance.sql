-- Unity Catalog governance for the Glance GenAd demo
-- 1) Advertiser (brand) row-level security   2) PII column masks   3) tags

CREATE TABLE IF NOT EXISTS glance_genad.governance.brand_entitlements (
  principal  STRING COMMENT 'User email or service principal application id',
  brand      STRING COMMENT 'Brand the principal may see (* = all brands, platform team)',
  granted_by STRING,
  granted_at TIMESTAMP
) COMMENT 'Advertiser data-clean-room style entitlements: Nike analysts only see Nike rows, etc.';

MERGE INTO glance_genad.governance.brand_entitlements t
USING (SELECT current_user() AS principal, '*' AS brand) s
ON t.principal = s.principal AND t.brand = s.brand
WHEN NOT MATCHED THEN INSERT (principal, brand, granted_by, granted_at) VALUES (s.principal, s.brand, current_user(), current_timestamp());

-- Row filter: platform admins see everything, others only brands they're entitled to
CREATE OR REPLACE FUNCTION glance_genad.governance.brand_row_filter(row_brand STRING)
RETURNS BOOLEAN
COMMENT 'Row filter: advertiser analysts only see impressions for brands they are entitled to'
RETURN is_account_group_member('glance_platform_admins')
    OR EXISTS (SELECT 1 FROM glance_genad.governance.brand_entitlements e
               WHERE e.principal = current_user() AND (e.brand = '*' OR e.brand = row_brand));

-- PII column masks: only the privacy team (glance_pii_readers) sees raw values
CREATE OR REPLACE FUNCTION glance_genad.governance.mask_email(email STRING)
RETURNS STRING
RETURN CASE WHEN is_account_group_member('glance_pii_readers') THEN email
            ELSE concat(left(email, 2), '****@', split_part(email, '@', 2)) END;

CREATE OR REPLACE FUNCTION glance_genad.governance.mask_phone(phone STRING)
RETURNS STRING
RETURN CASE WHEN is_account_group_member('glance_pii_readers') THEN phone
            ELSE concat('+**-******', right(phone, 4)) END;

CREATE OR REPLACE FUNCTION glance_genad.governance.mask_name(full_name STRING)
RETURNS STRING
RETURN CASE WHEN is_account_group_member('glance_pii_readers') THEN full_name
            ELSE concat(left(full_name, 1), '***** ', left(split_part(full_name, ' ', 2), 1), '.') END;

-- Advertising ID is pseudonymised (stable hash) so joins still work without exposing the GAID/IDFA
CREATE OR REPLACE FUNCTION glance_genad.governance.mask_ad_id(device_ad_id STRING)
RETURNS STRING
RETURN CASE WHEN is_account_group_member('glance_pii_readers') THEN device_ad_id
            ELSE concat('hash:', left(sha2(device_ad_id, 256), 16)) END;
