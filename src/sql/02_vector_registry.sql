-- Brand asset registry for Vector Search (Delta Sync index with managed gte-large embeddings).
-- Source of truth = Lakebase glance_ops.brand_asset_components -> Lakehouse Sync -> silver (SDP) -> here.
CREATE TABLE IF NOT EXISTS glance_genad.gold.brand_asset_registry (
  component_id        STRING NOT NULL,
  brand               STRING,
  component_name      STRING,
  product             STRING,
  creative_attributes STRING,
  description         STRING,
  approved_copy       STRING,
  palette             STRING,
  brand_safe          BOOLEAN,
  guardrail_note      STRING,
  embedding_text      STRING COMMENT 'Text embedded by Vector Search (databricks-gte-large-en)',
  updated_at          TIMESTAMP
)
COMMENT 'Brand-safe creative component registry embedded into Vector Search for latent-space matching of live context to brand assets.'
TBLPROPERTIES (delta.enableChangeDataFeed = true);

MERGE INTO glance_genad.gold.brand_asset_registry t
USING (
  SELECT component_id, brand, component_name, product, creative_attributes, description, approved_copy, palette,
         brand_safe, guardrail_note,
         concat(component_name, '. ', product, '. Attributes: ', creative_attributes, '. ', description) AS embedding_text,
         CAST(updated_at AS TIMESTAMP) AS updated_at
  FROM glance_genad.silver.silver_brand_asset_components
) s ON t.component_id = s.component_id
WHEN MATCHED AND (t.embedding_text <> s.embedding_text OR t.brand_safe <> s.brand_safe OR t.approved_copy <> s.approved_copy) THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
WHEN NOT MATCHED BY SOURCE THEN DELETE;
