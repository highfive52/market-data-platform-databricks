import json
from datetime import datetime, timezone

import pandas as pd
import pytest

from market_data_platform.bronze.market_data import transform_yahoo_history


def make_history(timestamp: str, close: float = 100.0) -> pd.DataFrame:
    """Create a timezone-aware Yahoo-style history DataFrame."""
    index = pd.DatetimeIndex([timestamp]).tz_localize("America/New_York")

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


def test_converts_est_timestamp_to_utc():
    history = make_history("2026-11-13 09:30:00")

    record = transform(history)[0]

    assert record["provider_timestamp_local"] == datetime(2026, 11, 13, 9, 30)
    assert record["provider_timezone"] == "America/New_York"
    assert record["provider_timestamp_utc"] == datetime(2026, 11, 13, 14, 30)
    assert record["bar_date"].isoformat() == "2026-11-13"


def test_converts_edt_timestamp_to_utc():
    history = make_history("2026-07-15 09:30:00")

    record = transform(history)[0]

    assert record["provider_timestamp_local"] == datetime(2026, 7, 15, 9, 30)
    assert record["provider_timestamp_utc"] == datetime(2026, 7, 15, 13, 30)


def test_preserves_yahoo_market_data_fields():
    history = make_history("2026-11-13 09:30:00")

    record = transform(history)[0]

    assert record["open"] == 99.0
    assert record["high"] == 101.0
    assert record["low"] == 98.0
    assert record["close"] == 100.0
    assert record["adj_close"] == 100.0
    assert record["volume"] == 1000
    assert record["dividends"] == 0.0
    assert record["stock_splits"] == 0.0


def test_hash_is_stable_across_ingestion_runs():
    history = make_history("2026-11-13 09:30:00")

    first = transform(history, run_id="run-001")[0]
    second = transform(history, run_id="run-002")[0]

    assert first["observation_hash"] == second["observation_hash"]


def test_hash_changes_when_market_data_changes():
    timestamp = "2026-11-13 09:30:00"

    original = transform(make_history(timestamp, close=100.0))[0]
    revised = transform(make_history(timestamp, close=100.5))[0]

    assert original["observation_hash"] != revised["observation_hash"]


def test_rejects_timezone_naive_index():
    history = make_history("2026-11-13 09:30:00")
    history.index = history.index.tz_localize(None)

    with pytest.raises(ValueError, match="timezone-aware"):
        transform(history)


def test_preserves_observation_with_missing_market_values():
    history = make_history("2026-11-13 09:30:00")
    history.loc[:, "Open"] = float("nan")
    history["Volume"] = history["Volume"].astype("float64")
    history.loc[:, "Volume"] = float("nan")

    records = transform(history)

    assert len(records) == 1
    assert records[0]["open"] is None
    assert records[0]["volume"] is None


def test_preserves_infinite_market_values():
    history = make_history("2026-11-13 09:30:00")
    history.loc[:, "Open"] = float("inf")

    records = transform(history)

    assert len(records) == 1
    assert records[0]["open"] == float("inf")
    assert records[0]["observation_hash"]


def test_rejects_fractional_volume():
    history = make_history("2026-11-13 09:30:00")
    history["Volume"] = history["Volume"].astype("float64")
    history.loc[:, "Volume"] = 1000.5

    with pytest.raises(ValueError, match="Expected an integer"):
        transform(history)


def test_preserves_original_yahoo_record():
    history = make_history("2026-11-13 09:30:00")

    # Include an extra provider field to verify we preserve
    # fields that aren't part of our structured Bronze schema.
    history["Extra Field"] = "provider-value"

    records = transform(history)

    raw_record = json.loads(records[0]["raw_record"])

    assert raw_record["Open"] == history.iloc[0]["Open"]
    assert raw_record["Adj Close"] == history.iloc[0]["Adj Close"]
    assert raw_record["Volume"] == history.iloc[0]["Volume"]
    assert raw_record["Extra Field"] == "provider-value"


def test_raw_record_preserves_missing_values_as_json_null():
    history = make_history("2026-11-13 09:30:00")
    history.loc[:, "Open"] = float("nan")

    records = transform(history)

    raw_record = json.loads(records[0]["raw_record"])

    assert raw_record["Open"] is None
    assert records[0]["open"] is None
