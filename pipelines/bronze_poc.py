from pyspark import pipelines as dp

SOURCE_PATH = "/Volumes/workspace/market_data/raw_market_data/poc/yahoo/historical/"


@dp.table(
    name="bronze_poc_yahoo_market_bars",
    comment="POC Bronze table incrementally ingested from raw Yahoo Parquet files.",
)
def bronze_poc_yahoo_market_bars():
    return (
        spark.readStream.format("cloudFiles")  # noqa: F821
        .option("cloudFiles.format", "parquet")
        .load(SOURCE_PATH)
    )
