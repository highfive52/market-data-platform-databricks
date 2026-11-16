-- Reconciliation run:
-- 48ceea2a-16b2-4c94-a4cb-f477ec9be138

-- ============================================================
-- 1. Completeness and required metadata
-- ============================================================

SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT symbol) AS distinct_symbols,
    COUNT(DISTINCT ingestion_run_id) AS ingestion_runs,
    COUNT_IF(symbol IS NULL) AS missing_symbols,
    COUNT_IF(bar_date IS NULL) AS missing_dates,
    COUNT_IF(provider_timestamp_utc IS NULL) AS missing_provider_timestamps,
    COUNT_IF(ingested_at_utc IS NULL) AS missing_ingestion_timestamps,
    COUNT_IF(_rescued_data IS NOT NULL) AS rescued_records
FROM workspace.market_data.bronze_yahoo_historical_bars;

-- ============================================================
-- 2. Business-key uniqueness
-- ============================================================

SELECT
    symbol,
    provider_interval,
    bar_date,
    COUNT(*) AS observation_count,
    COUNT(DISTINCT ingestion_run_id) AS ingestion_runs
FROM workspace.market_data.bronze_yahoo_historical_bars
GROUP BY
    symbol,
    provider_interval,
    bar_date
HAVING COUNT(*) > 1
ORDER BY
    symbol,
    bar_date;

-- ============================================================
-- 3. OHLC and volume plausibility
-- ============================================================

SELECT
    symbol,
    bar_date,
    open,
    high,
    low,
    close,
    adj_close,
    volume,
    CASE
        WHEN open IS NULL OR high IS NULL
          OR low IS NULL OR close IS NULL
            THEN 'MISSING_OHLC'
        WHEN high < low
            THEN 'HIGH_BELOW_LOW'
        WHEN high < GREATEST(open, close)
            THEN 'HIGH_BELOW_OPEN_OR_CLOSE'
        WHEN low > LEAST(open, close)
            THEN 'LOW_ABOVE_OPEN_OR_CLOSE'
        WHEN volume IS NULL OR volume < 0
            THEN 'INVALID_VOLUME'
        ELSE 'PASS'
    END AS validation_status
FROM workspace.market_data.bronze_yahoo_historical_bars
ORDER BY symbol, bar_date;

-- ============================================================
-- 4. Provider metadata and lineage
-- ============================================================

SELECT
    symbol,
    bar_date,
    provider_timestamp_utc,
    ingested_at_utc
FROM workspace.market_data.bronze_yahoo_historical_bars
WHERE ingested_at_utc < provider_timestamp_utc;

SELECT
    COUNT(*) AS total_rows,
    COUNT_IF(provider <> 'yahoo' OR provider IS NULL) AS unexpected_provider,
    COUNT_IF(provider_interval <> '1d' OR provider_interval IS NULL) AS unexpected_interval,
    COUNT_IF(provider_timezone <> 'America/New_York'
        OR provider_timezone IS NULL) AS unexpected_timezone,
    COUNT_IF(
        SUBSTRING(provider_timestamp_local, 1, 10)
        <> CAST(bar_date AS STRING)
    ) AS timestamp_date_mismatches,
    COUNT_IF(ingestion_run_id <> run_id OR ingestion_run_id IS NULL)
        AS run_id_mismatches,
    COUNT_IF(raw_record IS NULL OR raw_record = '') AS missing_raw_records
FROM workspace.market_data.bronze_yahoo_historical_bars;

-- ============================================================
-- 5. Landing-to-Bronze reconciliation
-- ============================================================

-- Landing-to-Bronze reconciliation for a specific ingestion run
WITH landing AS (
    SELECT *
    FROM read_files(
        '/Volumes/workspace/market_data/raw_market_data/yahoo/historical/run_id=48ceea2a-16b2-4c94-a4cb-f477ec9be138/',
        format => 'parquet'
    )
),
bronze AS (
    SELECT *
    FROM workspace.market_data.bronze_yahoo_historical_bars
    WHERE ingestion_run_id = '48ceea2a-16b2-4c94-a4cb-f477ec9be138'
)
SELECT
    (SELECT COUNT(*) FROM landing) AS landing_rows,
    (SELECT COUNT(*) FROM bronze) AS bronze_rows,
    (SELECT COUNT(DISTINCT symbol) FROM landing) AS landing_symbols,
    (SELECT COUNT(DISTINCT symbol) FROM bronze) AS bronze_symbols;

-- Landing-to-Bronze reconciliation for a specific ingestion run (detailed)
WITH landing AS (
    SELECT
        symbol,
        provider,
        provider_interval,
        bar_date,
        open,
        high,
        low,
        close,
        adj_close,
        volume,
        dividends,
        stock_splits,
        provider_timestamp_local,
        provider_timezone,
        provider_timestamp_utc,
        ingestion_run_id,
        ingested_at_utc,
        raw_record
    FROM read_files(
        '/Volumes/workspace/market_data/raw_market_data/yahoo/historical/run_id=48ceea2a-16b2-4c94-a4cb-f477ec9be138/',
        format => 'parquet'
    )
),
bronze AS (
    SELECT
        symbol,
        provider,
        provider_interval,
        bar_date,
        open,
        high,
        low,
        close,
        adj_close,
        volume,
        dividends,
        stock_splits,
        provider_timestamp_local,
        provider_timezone,
        provider_timestamp_utc,
        ingestion_run_id,
        ingested_at_utc,
        raw_record
    FROM workspace.market_data.bronze_yahoo_historical_bars
    WHERE ingestion_run_id = '48ceea2a-16b2-4c94-a4cb-f477ec9be138'
),
landing_only AS (
    SELECT * FROM landing
    EXCEPT ALL
    SELECT * FROM bronze
),
bronze_only AS (
    SELECT * FROM bronze
    EXCEPT ALL
    SELECT * FROM landing
)
SELECT
    (SELECT COUNT(*) FROM landing_only) AS landing_only_rows,
    (SELECT COUNT(*) FROM bronze_only) AS bronze_only_rows;
