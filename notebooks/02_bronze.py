# Databricks notebook source
"""Bronze ingestion notebook — Databricks execution experiments."""

print("Databricks notebook execution successful")
print(f"Spark version: {spark.version}")  # noqa: F821

print("\nSpark session:")
spark.sql("SELECT current_catalog(), current_schema()").show()  # noqa: F821

print("\nDatabricks runtime configuration:")
print(spark.conf.get("spark.sql.session.timeZone"))  # noqa: F821

# COMMAND ----------
print("\nTesting project package import:")

from market_data_platform.bronze.market_data import transform_yahoo_history

print(f"Imported: {transform_yahoo_history.__name__}")

# COMMAND ----------
print("\nPython import paths:")
for path in __import__("sys").path:
    print(path)

# COMMAND ----------
print("\nTesting yfinance connectivity:")

import yfinance as yf

try:
    history = yf.Ticker("AAPL").history(
        period="1d",
        interval="1d",
        auto_adjust=False,
    )

    print(f"Rows returned: {len(history)}")
    print(history.tail())

except Exception as exc:
    print(f"yfinance request failed: {type(exc).__name__}: {exc}")

# COMMAND ----------

print("Testing application package import:")

from market_data_platform.bronze.market_data import transform_yahoo_history

import inspect

print(f"Imported: {transform_yahoo_history.__name__}")
print(f"Signature: {inspect.signature(transform_yahoo_history)}")

# COMMAND ----------

from datetime import datetime, timezone
from uuid import uuid4

print("Testing Yahoo history transformation:")

records = transform_yahoo_history(
    history,
    symbol="AAPL",
    interval="1d",
    ingestion_run_id=str(uuid4()),
    ingested_at_utc=datetime.now(timezone.utc),
)

print(f"Records returned: {len(records)}")
print("\nFirst transformed record:")
print(records[0])
print("\nRecord fields:")
print(list(records[0].keys()))

# COMMAND ----------

table_name = "workspace.market_data.bronze_yahoo_market_bars"

print("Bronze table schema:")
spark.sql(f"DESCRIBE TABLE {table_name}").show(truncate=False)

print("\nCurrent Bronze table row count:")
spark.sql(f"SELECT COUNT(*) AS row_count FROM {table_name}").show()

# COMMAND ----------

from pyspark.sql.types import (
    BooleanType,
    DateType,
    DoubleType,
    LongType,
    StringType,
    StructField,
    StructType,
    TimestampNTZType,
)

bronze_schema = StructType(
    [
        StructField("symbol", StringType(), False),
        StructField("provider", StringType(), False),
        StructField("provider_interval", StringType(), False),
        StructField("provider_timestamp_local", TimestampNTZType(), False),
        StructField("provider_timezone", StringType(), False),
        StructField("provider_timestamp_utc", TimestampNTZType(), False),
        StructField("bar_date", DateType(), False),
        StructField("open", DoubleType(), True),
        StructField("high", DoubleType(), True),
        StructField("low", DoubleType(), True),
        StructField("close", DoubleType(), True),
        StructField("adj_close", DoubleType(), True),
        StructField("volume", LongType(), True),
        StructField("dividends", DoubleType(), True),
        StructField("stock_splits", DoubleType(), True),
        StructField("raw_record", StringType(), False),
        StructField("observation_hash", StringType(), False),
        StructField("is_current", BooleanType(), False),
        StructField("ingestion_run_id", StringType(), False),
        StructField("first_seen_at_utc", TimestampNTZType(), False),
        StructField("last_seen_at_utc", TimestampNTZType(), False),
    ]
)

bronze_df = spark.createDataFrame(records, schema=bronze_schema)

print("Spark DataFrame schema:")
bronze_df.printSchema()

print("\nTransformed Bronze record:")
bronze_df.show(truncate=False)

# COMMAND ----------

print(f"Writing {bronze_df.count()} records to {table_name}")

bronze_df.write.format("delta").mode("append").saveAsTable(table_name)

print("Bronze write completed.")

print("\nPersisted Bronze record:")
spark.sql(f"""
    SELECT
        symbol,
        provider,
        provider_interval,
        provider_timestamp_local,
        provider_timestamp_utc,
        observation_hash,
        ingestion_run_id
    FROM {table_name}
""").show(truncate=False)
