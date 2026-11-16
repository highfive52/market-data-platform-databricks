"""Write normalized historical market data to a Parquet landing location."""

from typing import Any


def write_yahoo_history_parquet(
    spark: Any,
    records: list[dict[str, Any]],
    *,
    output_path: str,
) -> int:
    """Write normalized Yahoo historical records to a Parquet directory.

    Returns the number of records written. An empty extraction writes no files.
    """
    if not records:
        return 0

    from pyspark.sql.types import (
        DateType,
        DoubleType,
        LongType,
        StringType,
        StructField,
        StructType,
        TimestampType,
    )

    schema = StructType(
        [
            StructField("symbol", StringType(), nullable=False),
            StructField("provider", StringType(), nullable=False),
            StructField("provider_interval", StringType(), nullable=False),
            StructField("bar_date", DateType(), nullable=False),
            StructField("open", DoubleType(), nullable=True),
            StructField("high", DoubleType(), nullable=True),
            StructField("low", DoubleType(), nullable=True),
            StructField("close", DoubleType(), nullable=True),
            StructField("adj_close", DoubleType(), nullable=True),
            StructField("volume", LongType(), nullable=True),
            StructField("dividends", DoubleType(), nullable=True),
            StructField("stock_splits", DoubleType(), nullable=True),
            StructField("provider_timestamp_local", StringType(), nullable=False),
            StructField("provider_timezone", StringType(), nullable=False),
            StructField("provider_timestamp_utc", TimestampType(), nullable=False),
            StructField("ingestion_run_id", StringType(), nullable=False),
            StructField("ingested_at_utc", TimestampType(), nullable=False),
            StructField("raw_record", StringType(), nullable=False),
        ]
    )

    dataframe = spark.createDataFrame(records, schema=schema)
    dataframe.write.format("parquet").save(output_path)

    return len(records)
