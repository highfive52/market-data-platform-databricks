SHOW CATALOGS;

SHOW SCHEMAS IN workspace;

SHOW VOLUMES IN workspace.market_data;

-----

CREATE VOLUME IF NOT EXISTS workspace.market_data.raw_market_data
COMMENT 'Raw provider-derived market data files for incremental ingestion experiments';

SHOW VOLUMES IN workspace.market_data;

---
-- Raw

SELECT *
FROM read_files(
    '/Volumes/workspace/market_data/raw_market_data/poc/yahoo/historical/run_id=6adf317d-19a6-43d7-9dd7-8e3190e19beb',
    format => 'parquet'
)
ORDER BY symbol, provider_timestamp_utc;

SELECT
    symbol,
    COUNT(*) AS observations,
    MIN(provider_timestamp_utc) AS first_observation,
    MAX(provider_timestamp_utc) AS last_observation,
    AVG(close) AS average_close
FROM read_files(
    '/Volumes/workspace/market_data/raw_market_data/poc/yahoo/historical/run_id=6adf317d-19a6-43d7-9dd7-8e3190e19beb',
    format => 'parquet'
)
GROUP BY symbol
ORDER BY symbol;

---
-- Bronze

SELECT
    symbol,
    provider,
    interval,
    COUNT(*) AS observations,
    MIN(provider_timestamp_utc) AS first_observation,
    MAX(provider_timestamp_utc) AS last_observation
FROM workspace.market_data.bronze_poc_yahoo_market_bars
GROUP BY symbol, provider, interval
ORDER BY symbol;

---

DESCRIBE DETAIL workspace.market_data.bronze_poc_yahoo_market_bars;

DESCRIBE HISTORY workspace.market_data.bronze_poc_yahoo_market_bars;
