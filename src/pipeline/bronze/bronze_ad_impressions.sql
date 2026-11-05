-- Bronze: raw ad-server impression logs, incrementally ingested from the landing volume with Auto Loader
CREATE OR REFRESH STREAMING TABLE glance_genad.bronze.bronze_ad_impressions
COMMENT 'Raw ad-server impression logs (static banner, standard video, Glance generative lock-screen). Auto Loader from /Volumes/glance_genad/raw/ad_logs.'
TBLPROPERTIES ('quality' = 'bronze')
AS SELECT
  *,
  _metadata.file_path AS _source_file,
  current_timestamp() AS _ingested_at
FROM STREAM read_files('/Volumes/glance_genad/raw/ad_logs/impressions/', format => 'parquet');
