from pyspark import pipelines as dp

SOURCE_PATH = "/Volumes/workspace/market_data/raw_market_data/yahoo/historical/"


@dp.table(
    name="bronze_yahoo_historical_recreation",
    comment="Recreation POC: rebuild Bronze from existing Yahoo historical Parquet files.",
)
def bronze_yahoo_historical_recreation():
    return (
        spark.readStream.format("cloudFiles")  # noqa: F821
        .option("cloudFiles.format", "parquet")
        .load(SOURCE_PATH)
    )
