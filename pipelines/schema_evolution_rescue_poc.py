from pyspark import pipelines as dp

SOURCE_PATH = "/Volumes/workspace/market_data/raw_market_data/schema_evolution_rescue/"


@dp.table(
    name="bronze_schema_evolution_rescue_poc",
    comment="Isolated Auto Loader schema evolution experiment.",
)
def bronze_schema_evolution_rescue_poc():
    return (
        spark.readStream.format("cloudFiles")  # noqa: F821
        .option("cloudFiles.format", "parquet")
        .option("cloudFiles.schemaEvolutionMode", "rescue")
        .load(SOURCE_PATH)
    )
