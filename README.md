# Market Data Platform — Databricks

An independent Databricks implementation of a multi-provider market data platform, built as a hands-on data engineering learning project.

This project explores how established data engineering principles translate into Databricks-native architecture and managed services. It uses historical market data to investigate ingestion, file-based processing, schema evolution, Delta Lake, and reproducible pipeline deployment.

The implementation is designed to complement the original Python-oriented project while exploring where Databricks-native capabilities provide a better fit.

## Architecture

The intended platform follows a Bronze / Silver / Gold medallion architecture. The current implementation focuses on historical ingestion and Bronze.

### Current ingestion flow

1. **Extract:** A Python provider adapter uses `yfinance` to retrieve historical Yahoo Finance market data.
2. **Normalize:** Reusable Python code converts provider responses into a normalized record structure, preserving provider timestamps, timezone information, raw records, and ingestion lineage.
3. **Land:** The extraction Job writes Parquet files to a Unity Catalog Volume, using a separate directory for each ingestion run.
4. **Ingest:** Auto Loader incrementally discovers and processes landed files.
5. **Store:** Lakeflow Spark Declarative Pipelines manages the Bronze Delta table.

```text
Yahoo Finance
     |
     v
Python / yfinance
     |
     v
Normalize provider records
     |
     v
Parquet files
     |
     v
Unity Catalog Volume
     |
     v
Auto Loader
     |
     v
Lakeflow pipeline
     |
     v
Bronze Delta table
```

### Medallion layers

- **Bronze — implemented:** Preserve normalized provider observations, raw provider records, and ingestion lineage in a pipeline-managed Delta table.
- **Silver — planned:** Reconcile observations, handle overlapping ingestion runs, and establish canonical market data.
- **Gold — planned:** Provide analytics-ready datasets for downstream exploration and analysis.

The architecture deliberately separates file-level ingestion from business-level reconciliation. Auto Loader tracks files it has processed; it does not determine whether two observations represent the same business event or which observation should be considered current.

## Databricks Concepts Explored

The project investigates several Databricks capabilities and their relationship to established data engineering practices:

- **Unity Catalog:** Governed catalogs, schemas, tables, and Volumes.
- **Volumes:** Durable file landing locations for provider-derived data.
- **Auto Loader:** Incremental file discovery and ingestion.
- **Lakeflow Spark Declarative Pipelines:** Declarative, pipeline-managed Bronze tables.
- **Delta Lake:** Transaction history, table versions, time travel, and managed table storage.
- **Declarative Automation Bundles (DABs):** Version-controlled deployment of Databricks Jobs and pipelines.
- **Serverless compute:** Managed execution environments for ingestion and pipeline workloads.

Schema evolution experiments compare automatic additive schema evolution with rescue mode, demonstrating how unexpected fields can be detected and preserved for deliberate review.

## Technology Stack

- Databricks Free Edition
- Python 3.12
- PySpark
- pandas
- yfinance
- Delta Lake
- Unity Catalog
- Auto Loader and Lakeflow Spark Declarative Pipelines
- Databricks Declarative Automation Bundles
- uv
- Ruff
- pytest
- pre-commit

Python is used for provider integration and application-level transformations. Databricks-native services manage file ingestion, pipeline execution, and Bronze table storage.

## Development Setup

The local development environment uses Python 3.12, `uv`, and Git. The Databricks CLI and VS Code Databricks extension support workspace deployment and development.

Install project dependencies:

```bash
uv sync
```

Run the automated tests and code-quality checks:

```bash
make check
```

The project uses `uv.lock` to keep dependency resolution reproducible.

See [docs/setup-runbook.md](docs/setup-runbook.md) for environment setup and [docs/implementation-plan.md](docs/implementation-plan.md) for the development roadmap.

## Project Structure

```text
src/market_data_platform/
    ingestion/             # Provider normalization and Parquet landing

notebooks/                 # Databricks extraction and experiments
pipelines/                 # Lakeflow pipeline definitions
resources/                 # DAB Job and pipeline resources
sql/
    analysis/              # Exploratory SQL
    setup/                 # Databricks setup and learning exercises
    validation/            # Bronze validation queries

tests/
    unit/                  # Local automated tests

docs/                     # Architecture, concepts, results, and runbooks
```

Some notebooks and pipelines are retained as isolated proof-of-concept experiments. They document the behavior and design decisions behind the current implementation.

## Project Status

**Stage 3 — Historical ingestion and Bronze: technically complete.**

The implementation has demonstrated:

- Historical Yahoo Finance extraction through a Databricks Job.
- Normalization and Parquet landing in a Unity Catalog Volume.
- Incremental ingestion into a managed Bronze Delta table using Auto Loader and Lakeflow.
- Preservation of provider metadata, raw records, and ingestion lineage.
- Additive schema evolution and rescue-mode behavior.
- Delta transaction history and time travel.
- Repeatable ingestion without rediscovering previously processed files.
- Independent recreation of a Bronze table from existing raw files.

Automated unit tests cover the local normalization and landing logic. SQL validation checks cover Bronze completeness, data plausibility, metadata, lineage, and reconciliation against landed files.

Silver reconciliation, Gold analytics, and live market-data ingestion are future development areas.

See [docs/implementation-plan-results.md](docs/implementation-plan-results.md) for implementation details and verification results.

## Related Project

The original Python-oriented platform implementation is maintained separately:

[Market Data Platform](https://github.com/highfive52/market-data-platform)
