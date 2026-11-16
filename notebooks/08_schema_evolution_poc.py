# Databricks notebook source
"""Create the initial dataset for the Auto Loader schema evolution POC."""

from uuid import uuid4

from pyspark.sql.types import (
    DoubleType,
    StringType,
    StructField,
    StructType,
)

SOURCE_PATH = "/Volumes/workspace/market_data/raw_market_data/schema_evolution/"

schema = StructType(
    [
        StructField("symbol", StringType(), nullable=False),
        StructField("close", DoubleType(), nullable=False),
    ]
)

records = [
    ("AAPL", 353.34),
    ("MSFT", 522.50),
]

df = spark.createDataFrame(records, schema=schema)

run_id = str(uuid4())
output_path = f"{SOURCE_PATH}run_id={run_id}"

df.write.format("parquet").save(output_path)

print(f"Run ID: {run_id}")
print(f"Output path: {output_path}")
print(f"Records written: {df.count()}")

# COMMAND ----------

from pyspark.sql.types import (
    DoubleType,
    StringType,
    StructField,
    StructType,
)

evolved_schema = StructType(
    [
        StructField("symbol", StringType(), nullable=False),
        StructField("close", DoubleType(), nullable=False),
        StructField("source_currency", StringType(), nullable=False),
    ]
)

evolved_records = [
    ("AAPL", 354.00, "USD"),
    ("MSFT", 524.00, "USD"),
]

evolved_df = spark.createDataFrame(
    evolved_records,
    schema=evolved_schema,
)

evolved_run_id = str(uuid4())
evolved_output_path = f"{SOURCE_PATH}run_id={evolved_run_id}"

evolved_df.write.format("parquet").save(evolved_output_path)

print(f"Run ID: {evolved_run_id}")
print(f"Output path: {evolved_output_path}")
print(f"Records written: {evolved_df.count()}")
