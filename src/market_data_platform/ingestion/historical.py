"""Extract and normalize historical market data from providers."""

import json
import math
from datetime import date, datetime, timezone
from typing import Any

import pandas as pd

YAHOO_REQUIRED_COLUMNS = {
    "Open",
    "High",
    "Low",
    "Close",
    "Adj Close",
    "Volume",
    "Dividends",
    "Stock Splits",
}


def _nullable_number(value: Any, *, integer: bool = False) -> int | float | None:
    """Convert a provider numeric value, preserving missing values as None."""
    if pd.isna(value):
        return None

    numeric_value = float(value)

    if integer:
        if not math.isfinite(numeric_value) or not numeric_value.is_integer():
            raise ValueError(f"Expected an integer value, received: {value}")
        return int(numeric_value)

    return numeric_value


def _json_value(value: Any) -> Any:
    """Convert provider values into standard JSON-compatible values."""
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        value = value.item()

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, float) and not math.isfinite(value):
        if math.isnan(value):
            return None
        return "Infinity" if value > 0 else "-Infinity"

    return value


def _raw_record(row: pd.Series) -> str:
    """Serialize the original provider row as standard JSON."""
    raw_values = {str(key): _json_value(value) for key, value in row.items()}

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
    """Normalize a yfinance history DataFrame into landing records."""
    if history.empty:
        return []

    if not isinstance(history.index, pd.DatetimeIndex):
        raise ValueError("Yahoo history must have a DatetimeIndex")

    if history.index.tz is None:
        raise ValueError("Yahoo history timestamps must be timezone-aware")

    if ingested_at_utc.tzinfo is None or ingested_at_utc.utcoffset() is None:
        raise ValueError("ingested_at_utc must be timezone-aware")

    missing_columns = YAHOO_REQUIRED_COLUMNS - set(history.columns)
    if missing_columns:
        raise ValueError(f"Yahoo history is missing columns: {sorted(missing_columns)}")

    normalized_symbol = symbol.strip().upper()
    provider_timezone = str(history.index.tz)
    ingestion_timestamp = ingested_at_utc.astimezone(timezone.utc)

    records = []

    for timestamp, row in history.iterrows():
        provider_timestamp = timestamp.to_pydatetime()

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

        records.append(
            {
                "symbol": normalized_symbol,
                "provider": "yahoo",
                "provider_interval": interval,
                "bar_date": provider_timestamp.date(),
                "open": values["open"],
                "high": values["high"],
                "low": values["low"],
                "close": values["close"],
                "adj_close": values["adj_close"],
                "volume": values["volume"],
                "dividends": values["dividends"],
                "stock_splits": values["stock_splits"],
                "provider_timestamp_local": provider_timestamp.isoformat(),
                "provider_timezone": provider_timezone,
                "provider_timestamp_utc": provider_timestamp.astimezone(timezone.utc),
                "ingestion_run_id": ingestion_run_id,
                "ingested_at_utc": ingestion_timestamp,
                "raw_record": _raw_record(row),
            }
        )

    return records
