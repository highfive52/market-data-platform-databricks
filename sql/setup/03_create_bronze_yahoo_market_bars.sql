
-- Bronze table for historical Yahoo Finance market bar observations.
--
-- Business key:
--   provider, symbol, provider_interval, provider_timestamp_utc
--
-- Version identity:
--   Business key + observation_hash
--
-- Identical observations are deduplicated. Changed observations are retained
-- as separate versions, with exactly one current version per business key.

CREATE TABLE IF NOT EXISTS workspace.market_data.bronze_yahoo_market_bars (
    -- Provider and observation identity
    symbol STRING NOT NULL,
    provider STRING NOT NULL,
    provider_interval STRING NOT NULL,

    -- Source timestamp representation
    provider_timestamp_local TIMESTAMP_NTZ NOT NULL,
    provider_timezone STRING NOT NULL,
    provider_timestamp_utc TIMESTAMP_NTZ NOT NULL,

    -- UTC calendar date, derived from provider_timestamp_utc
    bar_date DATE NOT NULL,

    -- Provider market data fields
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    adj_close DOUBLE,
    volume BIGINT,
    dividends DOUBLE,
    stock_splits DOUBLE,

    -- Observation versioning
    observation_hash STRING NOT NULL,
    is_current BOOLEAN NOT NULL,

    -- Ingestion lineage
    ingestion_run_id STRING NOT NULL,
    first_seen_at_utc TIMESTAMP_NTZ NOT NULL,
    last_seen_at_utc TIMESTAMP_NTZ NOT NULL
)
USING DELTA
PARTITIONED BY (bar_date)
COMMENT 'Bronze provider observations for historical Yahoo Finance market bars, including observation version history and ingestion lineage.';
