"""Transform provider market data into Bronze observations."""

import hashlib
import json
import math
from datetime import date, datetime, timezone
from typing import Any

import pandas as pd


def _observation_hash(
    *,
    provider_timestamp_utc: datetime,
    values: dict[str, Any],
) -> str:
    """Calculate a deterministic hash of the provider observation."""
    hash_payload = {
        "provider_timestamp_utc": provider_timestamp_utc.isoformat(),
        **{key: _hash_value(value) for key, value in values.items()},
    }

    serialized = json.dumps(
        hash_payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )

    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _nullable_number(value: Any, *, integer: bool = False) -> int | float | None:
    """Convert a provider numeric value, preserving missing values as None."""
    if pd.isna(value):
        return None

    if integer:
        numeric_value = float(value)
        if not numeric_value.is_integer():
            raise ValueError(f"Expected an integer value, received: {value}")
        return int(numeric_value)

    return float(value)


def _hash_value(value: Any) -> Any:
    """Convert non-finite floats to deterministic JSON-compatible values."""
    if isinstance(value, float) and math.isinf(value):
        return "Infinity" if value > 0 else "-Infinity"

    return value


def _raw_record(row: pd.Series) -> str:
    """Serialize an original provider row as standard JSON."""
    raw_values = {}

    for key, value in row.items():
        if pd.isna(value):
            raw_values[str(key)] = None
            continue

        # Convert NumPy scalar types into native Python types.
        if hasattr(value, "item"):
            value = value.item()

        raw_values[str(key)] = _hash_value(value)

    return json.dumps(
        raw_values,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def transform_yahoo_history(
    history: pd.DataFrame,
    *,
    symbol: str,
    interval: str,
    ingestion_run_id: str,
    ingested_at_utc: datetime,
) -> list[dict[str, Any]]:
    """Convert a yfinance history DataFrame into Bronze records."""
    if history.empty:
        return []

    if not isinstance(history.index, pd.DatetimeIndex):
        raise ValueError("Yahoo history must have a DatetimeIndex")

    if history.index.tz is None:
        raise ValueError("Yahoo history timestamps must be timezone-aware")

    if ingested_at_utc.tzinfo is None or ingested_at_utc.utcoffset() is None:
        raise ValueError("ingested_at_utc must be timezone-aware")

    ingestion_timestamp = ingested_at_utc.astimezone(timezone.utc).replace(tzinfo=None)

    provider_timezone = str(history.index.tz)
    normalized_symbol = symbol.strip().upper()

    required_columns = {
        "Open",
        "High",
        "Low",
        "Close",
        "Adj Close",
        "Volume",
        "Dividends",
        "Stock Splits",
    }

    missing_columns = required_columns - set(history.columns)
    if missing_columns:
        raise ValueError(f"Yahoo history is missing columns: {sorted(missing_columns)}")

    records = []

    for timestamp, row in history.iterrows():
        provider_timestamp_local = timestamp.to_pydatetime().replace(tzinfo=None)

        provider_timestamp_utc = (
            timestamp.to_pydatetime().astimezone(timezone.utc).replace(tzinfo=None)
        )

        raw_record = _raw_record(row)

        values = {
            "open": _nullable_number(row["Open"]),
            "high": _nullable_number(row["High"]),
            "low": _nullable_number(row["Low"]),
            "close": _nullable_number(row["Close"]),
            "adj_close": _nullable_number(row["Adj Close"]),
            "volume": _nullable_number(row["Volume"], integer=True),
            "dividends": _nullable_number(row["Dividends"]),
            "stock_splits": _nullable_number(row["Stock Splits"]),
        }

        observation_hash = _observation_hash(
            provider_timestamp_utc=provider_timestamp_utc,
            values=values,
        )

        records.append(
            {
                "symbol": normalized_symbol,
                "provider": "yahoo",
                "provider_interval": interval,
                "provider_timestamp_local": provider_timestamp_local,
                "provider_timezone": provider_timezone,
                "provider_timestamp_utc": provider_timestamp_utc,
                "bar_date": date.fromisoformat(provider_timestamp_utc.date().isoformat()),
                **values,
                "raw_record": raw_record,
                "observation_hash": observation_hash,
                "is_current": True,
                "ingestion_run_id": ingestion_run_id,
                "first_seen_at_utc": ingestion_timestamp,
                "last_seen_at_utc": ingestion_timestamp,
            }
        )

    return records
