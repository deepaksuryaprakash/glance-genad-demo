"""MERGE the silver brand component registry into the VS source table and trigger an index sync."""
import sys
from pyspark.sql import SparkSession
from databricks.sdk import WorkspaceClient

sql_path, index = sys.argv[1], sys.argv[2]
spark = SparkSession.builder.getOrCreate()
import re
s = re.sub(r"--[^\n]*", "", open(sql_path).read())
for st in [x.strip() for x in s.split(";") if x.strip()]:
    spark.sql(st)
WorkspaceClient().vector_search_indexes.sync_index(index_name=index)
print("registry merged; index sync triggered")
