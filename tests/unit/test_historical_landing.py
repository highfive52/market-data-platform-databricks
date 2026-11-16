from market_data_platform.ingestion.landing import write_yahoo_history_parquet


def test_empty_records_do_not_require_spark_or_write_files():
    result = write_yahoo_history_parquet(
        spark=None,
        records=[],
        output_path="/unused/path",
    )

    assert result == 0
