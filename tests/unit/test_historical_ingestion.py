import json
from datetime import date, datetime, timezone

import pandas as pd
import pytest

from market_data_platform.ingestion.historical import transform_yahoo_history


def make_history(
    timestamp: str,
    close: float = 100.0,
    timezone_name: str = "America/New_York",
) -> pd.DataFrame:
    """Create a timezone-aware Yahoo-style history DataFrame."""
    index = pd.DatetimeIndex([timestamp]).tz_localize(timezone_name)

    return pd.DataFrame(
        {
            "Open": [99.0],
            "High": [101.0],
            "Low": [98.0],
            "Close": [close],
            "Adj Close": [close],
            "Volume": [1000],
            "Dividends": [0.0],
            "Stock Splits": [0.0],
        },
        index=index,
    )


def transform(history: pd.DataFrame, run_id: str = "run-001"):
    return transform_yahoo_history(
        history,
        symbol="aapl",
        interval="1m",
        ingestion_run_id=run_id,
        ingested_at_utc=datetime(2026, 11, 13, 23, 0, tzinfo=timezone.utc),
    )


def test_preserves_est_timestamp_and_converts_to_utc():
    history = make_history("2026-11-13 09:30:00")

    record = transform(history)[0]

    assert record["provider_timestamp_local"] == "2026-11-13T09:30:00-05:00"
    assert record["provider_timezone"] == "America/New_York"
    assert record["provider_timestamp_utc"] == datetime(2026, 11, 13, 14, 30, tzinfo=timezone.utc)
    assert record["bar_date"] == date(2026, 11, 13)


def test_preserves_edt_offset_and_converts_to_utc():
    history = make_history("2026-07-15 09:30:00")

    record = transform(history)[0]

    assert record["provider_timestamp_local"] == "2026-07-15T09:30:00-04:00"
    assert record["provider_timestamp_utc"] == datetime(2026, 7, 15, 13, 30, tzinfo=timezone.utc)


def test_bar_date_uses_provider_local_date_not_utc_date():
    history = make_history(
        "2026-11-13 23:30:00",
        timezone_name="America/Los_Angeles",
    )

    record = transform(history)[0]

    assert record["bar_date"] == date(2026, 11, 13)
    assert record["provider_timestamp_utc"].date() == date(2026, 11, 14)


def test_normalizes_symbol_and_preserves_market_data_fields():
    history = make_history("2026-11-13 09:30:00")

    record = transform(history)[0]

    assert record["symbol"] == "AAPL"
    assert record["provider"] == "yahoo"
    assert record["provider_interval"] == "1m"
    assert record["open"] == 99.0
    assert record["high"] == 101.0
    assert record["low"] == 98.0
    assert record["close"] == 100.0
    assert record["adj_close"] == 100.0
    assert record["volume"] == 1000
    assert record["dividends"] == 0.0
    assert record["stock_splits"] == 0.0


def test_includes_ingestion_metadata():
    history = make_history("2026-11-13 09:30:00")

    record = transform(history, run_id="run-123")[0]

    assert record["ingestion_run_id"] == "run-123"
    assert record["ingested_at_utc"] == datetime(2026, 11, 13, 23, 0, tzinfo=timezone.utc)


def test_does_not_include_legacy_reconciliation_fields():
    history = make_history("2026-11-13 09:30:00")

    record = transform(history)[0]

    assert "observation_hash" not in record
    assert "is_current" not in record
    assert "first_seen_at_utc" not in record
    assert "last_seen_at_utc" not in record


def test_empty_history_returns_no_records():
    history = make_history("2026-11-13 09:30:00").iloc[0:0]

    assert transform(history) == []


def test_rejects_timezone_naive_index():
    history = make_history("2026-11-13 09:30:00")
    history.index = history.index.tz_localize(None)

    with pytest.raises(ValueError, match="timezone-aware"):
        transform(history)


def test_rejects_naive_ingestion_timestamp():
    history = make_history("2026-11-13 09:30:00")

    with pytest.raises(ValueError, match="ingested_at_utc must be timezone-aware"):
        transform_yahoo_history(
            history,
            symbol="AAPL",
            interval="1d",
            ingestion_run_id="run-001",
            ingested_at_utc=datetime(2026, 11, 13, 23, 0),
        )


def test_preserves_missing_market_values_as_none():
    history = make_history("2026-11-13 09:30:00")
    history.loc[:, "Open"] = float("nan")
    history["Volume"] = history["Volume"].astype("float64")
    history.loc[:, "Volume"] = float("nan")

    record = transform(history)[0]

    assert record["open"] is None
    assert record["volume"] is None


def test_preserves_infinite_price_value():
    history = make_history("2026-11-13 09:30:00")
    history.loc[:, "Open"] = float("inf")

    record = transform(history)[0]

    assert record["open"] == float("inf")
    assert json.loads(record["raw_record"])["Open"] == "Infinity"


def test_rejects_fractional_volume():
    history = make_history("2026-11-13 09:30:00")
    history["Volume"] = history["Volume"].astype("float64")
    history.loc[:, "Volume"] = 1000.5

    with pytest.raises(ValueError, match="Expected an integer"):
        transform(history)


def test_rejects_infinite_volume():
    history = make_history("2026-11-13 09:30:00")
    history["Volume"] = history["Volume"].astype("float64")
    history.loc[:, "Volume"] = float("inf")

    with pytest.raises(ValueError, match="Expected an integer"):
        transform(history)


def test_preserves_original_yahoo_record():
    history = make_history("2026-11-13 09:30:00")
    history["Extra Field"] = "provider-value"

    record = transform(history)[0]
    raw_record = json.loads(record["raw_record"])

    assert raw_record["Open"] == history.iloc[0]["Open"]
    assert raw_record["Adj Close"] == history.iloc[0]["Adj Close"]
    assert raw_record["Volume"] == history.iloc[0]["Volume"]
    assert raw_record["Extra Field"] == "provider-value"


def test_raw_record_preserves_missing_values_as_json_null():
    history = make_history("2026-11-13 09:30:00")
    history.loc[:, "Open"] = float("nan")

    record = transform(history)[0]
    raw_record = json.loads(record["raw_record"])

    assert raw_record["Open"] is None
    assert record["open"] is None
