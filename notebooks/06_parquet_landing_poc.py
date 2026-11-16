# Databricks notebook source
"""Controlled Parquet landing POC."""

from datetime import datetime, timezone
from uuid import uuid4

from pyspark.sql.types import (
    DoubleType,
    LongType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

# Use UTC consistently for this experiment.
spark.conf.set("spark.sql.session.timeZone", "UTC")

# Give this extraction a unique identity so rerunning the notebook
# never overwrites previously landed files.
ingestion_run_id = str(uuid4())
ingested_at_utc = datetime.now(timezone.utc)

# Explicit schema: don't rely on Spark inferring types.
schema = StructType(
    [
        StructField("symbol", StringType(), nullable=False),
        StructField("provider", StringType(), nullable=False),
        StructField("interval", StringType(), nullable=False),
        StructField("provider_timestamp_utc", TimestampType(), nullable=False),
        StructField("open", DoubleType(), nullable=True),
        StructField("high", DoubleType(), nullable=True),
        StructField("low", DoubleType(), nullable=True),
        StructField("close", DoubleType(), nullable=True),
        StructField("volume", LongType(), nullable=True),
        StructField("ingestion_run_id", StringType(), nullable=False),
        StructField("ingested_at_utc", TimestampType(), nullable=False),
    ]
)

# # Small, controlled dataset: two symbols, two daily observations each.
# observations = [
#     ("AAPL", "2026-11-12 21:00:00", 275.00, 278.00, 274.00, 277.00, 41000000),
#     ("AAPL", "2026-11-13 21:00:00", 277.00, 280.00, 276.00, 279.00, 39000000),
#     ("MSFT", "2026-11-12 21:00:00", 508.00, 512.00, 507.00, 511.00, 22000000),
#     ("MSFT", "2026-11-13 21:00:00", 511.00, 515.00, 510.00, 514.00, 20500000),
# ]

# Second batch: two new daily observations per symbol.
observations = [
    ("AAPL", "2026-11-16 21:00:00", 280.00, 283.00, 279.00, 282.00, 42000000),
    ("MSFT", "2026-11-16 21:00:00", 514.00, 518.00, 513.00, 517.00, 21500000),
]

records = [
    (
        symbol,
        "yahoo",
        "1d",
        datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc),
        open_price,
        high,
        low,
        close,
        volume,
        ingestion_run_id,
        ingested_at_utc,
    )
    for (
        symbol,
        timestamp,
        open_price,
        high,
        low,
        close,
        volume,
    ) in observations
]

df = spark.createDataFrame(records, schema=schema)

print("Dataset schema:")
df.printSchema()

print(f"Records created: {df.count()}")
display(df)

# Write to a unique extraction directory in the Volume.
output_path = (
    f"/Volumes/workspace/market_data/raw_market_data/poc/yahoo/historical/run_id={ingestion_run_id}"
)

df.write.format("parquet").save(output_path)

print(f"Parquet dataset written to: {output_path}")
print("Files created:")
display(dbutils.fs.ls(output_path))
