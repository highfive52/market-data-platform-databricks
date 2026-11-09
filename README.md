# Market Data Platform — Databricks

An independent Databricks implementation of a multi-provider market data platform, built as a hands-on learning project.

The project explores how Databricks-native capabilities can support a medallion architecture for ingesting, normalizing, reconciling, and analyzing market data.

## Architecture

The platform follows a Bronze / Silver / Gold architecture:

- **Bronze:** Preserve normalized provider observations for replay and auditing.
- **Silver:** Reconcile provider data into canonical, trusted one-minute market bars.
- **Gold:** Provide analytics-ready datasets for downstream exploration and analysis.

The design emphasizes provider-specific ingestion, reusable data contracts, UTC timestamp consistency, idempotency, and data quality.

## Technology Stack

- Databricks
- Delta Lake
- Python 3.12
- Pydantic
- uv
- Ruff and pytest
- pre-commit
- GitHub Actions

Databricks-native capabilities and services will be introduced incrementally as the implementation develops.

## Development Setup

Requires Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run pytest
uv run pre-commit run --all-files
```

## Project Structure

```text
src/market_data_platform/   # Reusable Python modules and contracts
notebooks/                  # Databricks notebooks
resources/                  # Databricks resource definitions
sql/                        # SQL analysis and validation
tests/                      # Automated tests
docs/                       # Architecture, concepts, and runbooks
```

## Project Status

Initial project scaffolding and local development tooling are in place. Databricks workspace integration, deployment, and pipeline implementation are planned next.

## Related Project

The original platform implementation is maintained separately:

[Market Data Platform](https://github.com/highfive52/market-data-platform)
