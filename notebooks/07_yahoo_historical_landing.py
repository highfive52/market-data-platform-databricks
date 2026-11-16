# Databricks notebook source
"""Extract Yahoo historical market data and land it as Parquet files."""

from datetime import datetime, timezone
from uuid import uuid4

import yfinance as yf

from market_data_platform.ingestion.historical import transform_yahoo_history
from market_data_platform.ingestion.landing import write_yahoo_history_parquet

# COMMAND ----------

# Use UTC consistently for Spark timestamps.
spark.conf.set("spark.sql.session.timeZone", "UTC")

# Keep the initial extraction small and reproducible.
symbols = ["AAPL", "MSFT"]
start_date = "2026-11-13"
end_date = "2026-11-17"  # yfinance treats end as exclusive.
interval = "1d"

# Give every extraction a unique identity.
ingestion_run_id = str(uuid4())
ingested_at_utc = datetime.now(timezone.utc)

output_path = (
    f"/Volumes/workspace/market_data/raw_market_data/yahoo/historical/run_id={ingestion_run_id}"
)

print(f"Ingestion run ID: {ingestion_run_id}")
print(f"Symbols: {symbols}")
print(f"Date range: {start_date} through {end_date} (end exclusive)")
print(f"Interval: {interval}")
print(f"Output path: {output_path}")
print(f"Ingested at UTC: {ingested_at_utc.isoformat()}")

# COMMAND ----------

# Extract and normalize each symbol independently.
records = []

for symbol in symbols:
    print(f"Fetching {symbol}...")

    history = yf.Ticker(symbol).history(
        start=start_date,
        end=end_date,
        interval=interval,
        auto_adjust=False,
        actions=True,
    )

    print(f"  Rows returned: {len(history)}")

    symbol_records = transform_yahoo_history(
        history,
        symbol=symbol,
        interval=interval,
        ingestion_run_id=ingestion_run_id,
        ingested_at_utc=ingested_at_utc,
    )

    print(f"  Records normalized: {len(symbol_records)}")
    records.extend(symbol_records)

print(f"Total normalized records: {len(records)}")

# COMMAND ----------

# Inspect the normalized records before writing.
if records:
    normalized_df = spark.createDataFrame(records)
    display(normalized_df)
else:
    print("No records returned. No Parquet files will be written.")

# COMMAND ----------

# Land the extraction as Parquet files in the Unity Catalog Volume.
records_written = write_yahoo_history_parquet(
    spark,
    records,
    output_path=output_path,
)

print(f"Records written: {records_written}")

if records_written:
    print(f"Files written under: {output_path}")
    display(dbutils.fs.ls(output_path))
