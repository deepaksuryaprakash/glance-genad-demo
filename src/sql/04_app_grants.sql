GRANT USE CATALOG ON CATALOG glance_genad TO `81f5cf7e-a15f-4710-8f01-03b28e0fe4ed`;
GRANT USE SCHEMA, SELECT ON SCHEMA glance_genad.gold TO `81f5cf7e-a15f-4710-8f01-03b28e0fe4ed`;
GRANT USE SCHEMA, SELECT ON SCHEMA glance_genad.ml TO `81f5cf7e-a15f-4710-8f01-03b28e0fe4ed`;
GRANT USE SCHEMA, READ VOLUME ON SCHEMA glance_genad.raw TO `81f5cf7e-a15f-4710-8f01-03b28e0fe4ed`;
GRANT USE SCHEMA, EXECUTE ON SCHEMA glance_genad.governance TO `81f5cf7e-a15f-4710-8f01-03b28e0fe4ed`;
GRANT SELECT ON TABLE glance_genad.governance.brand_entitlements TO `81f5cf7e-a15f-4710-8f01-03b28e0fe4ed`;
INSERT INTO glance_genad.governance.brand_entitlements VALUES ('81f5cf7e-a15f-4710-8f01-03b28e0fe4ed', '*', current_user(), current_timestamp());
