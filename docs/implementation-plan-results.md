## Current Project Status

**Current stage: Stage 2 — Lakehouse Foundation and Lakeflow POC**

Stage 1 is complete. Stage 2 is in progress. The project has completed its initial Databricks environment and deployment setup, explored database object management through a custom migration implementation, and established the target approach for Databricks-native table and pipeline management.

The architecture decision is to use Databricks-native capabilities for platform-managed data objects and transformations rather than introduce a separate database migration framework.

The initial historical Yahoo Finance ingestion architecture is now defined:

**Python / yfinance → Unity Catalog Volume → Auto Loader → Lakeflow Bronze**

Python retrieves historical market data and writes uniquely identified Parquet files to a Unity Catalog Volume. Auto Loader, running within a Lakeflow Spark Declarative Pipeline, incrementally discovers and processes those files. Bronze processing applies the platform's observation identity, content-hash, and versioning rules.

This architecture separates raw source-file retention, file-level ingestion progress, and business-level observation idempotency.

The next milestone is a small proof of concept that validates the Volume, Auto Loader, and Lakeflow workflow in Databricks Free Edition.

Some Bronze database implementation has already been completed ahead of the formal Bronze ingestion work. Historical data ingestion and Silver transformations have not yet been completed.

| Stage | Description | Status |
|---|---|---|
| 1 | Project Foundation and Databricks Environment | Complete |
| 2 | Lakehouse Foundation and Lakeflow POC | In progress |
| 3 | Bronze Ingestion and Historical Market Data | Foundation started |
| 4 | Silver Transformations and Reconciliation | Not started |
| 5 | Gold Analytics, dbt, and Databricks SQL | Not started |
| 6 | Orchestration and Lakeflow Jobs | Not started |
| 7 | Incremental Ingestion and Schema Evolution | Not started |
| 8 | Streaming Market Data | Not started |
| 9 | Platform Engineering and Optimization | Not started |

---

## Stage 2 — Lakehouse Foundation and Lakeflow POC

**Status: In progress**

### Objective

Establish a reproducible Databricks lakehouse implementation using native platform capabilities for resource deployment, file ingestion, table management, and transformations.

The preferred architecture separates responsibilities:

- **Declarative Automation Bundles:** Define and deploy supported Databricks workspace resources and configurations.
- **Unity Catalog:** Provides data organization, governance, permissions, and lineage.
- **Unity Catalog Volumes:** Provide file storage for raw source landing.
- **Delta Lake:** Provides transactional table storage and data-management capabilities.
- **Auto Loader:** Supports incremental ingestion of files from supported cloud storage locations, including Unity Catalog Volumes.
- **Lakeflow Spark Declarative Pipelines:** Manages pipeline-defined transformations, dependencies, and pipeline-managed tables.
- **Python:** Implements provider integrations, application-specific logic, contracts, and processing that belongs outside platform-managed functionality.
- **dbt:** Manages analytical SQL models, dependencies, tests, and documentation, particularly in the Gold layer.
- **Lakeflow Jobs:** Orchestrates workflows and coordinates pipeline and other task execution.

The architecture deliberately favors Databricks-native capabilities over custom implementations of functionality already provided by the platform.

### Completed Work

**#### Databricks Resource and Object Exploration**

- Reviewed the distinction between workspace resources and Unity Catalog data objects.
- Investigated which resource types can be declared and deployed through bundles.
- Established that bundle deployment and data processing are separate activities.
- Identified catalog and schema configuration as part of the platform foundation.
- Explored the relationship between declarative resource definitions and independently materialized data objects.

**#### Custom Migration Implementation — Legacy**

A custom migration implementation was developed before evaluating external migration tools.

The implementation included:

- `src/market_data_platform/migrations/runner.py`
- Packaged SQL migration files.
- Migration discovery.
- Checksum validation.
- Migration execution.
- Unit tests.

Initial migrations:

| Migration | Purpose |
|---|---|
| `0001_create_market_data_schema.sql` | Creates `workspace.market_data` |
| `0002_create_bronze_yahoo_market_bars.sql` | Creates the Bronze Yahoo market-bars table |

The migrations were executed against Databricks, and the resulting database objects were inspected.

This work demonstrated a custom approach to database object management. It is now considered a legacy implementation rather than the target architecture.

The migration runner, SQL files, and associated tests will be removed after the relevant objects have been transitioned to and verified under their intended Databricks-native ownership.

**#### Liquibase Evaluation — Stopped**

Liquibase was investigated as a possible alternative to the custom migration implementation.

The evaluation included:

- Installing Liquibase 5.0.4 through the official APT repository.
- Installing and checking Java 17.0.15.
- Exploring Liquibase Package Manager (LPM) 0.3.9.
- Attempting package-management operations.
- Investigating installation-directory permissions and configuration.

The installation encountered permission and configuration problems. It was subsequently removed to allow a clean restart.

The evaluation did not establish a working Databricks Liquibase integration.

Current environment state:

- APT-installed Liquibase has been removed.
- The `liquibase` executable is no longer available.
- Java 17 remains installed.
- No clean user-owned Liquibase installation was completed.
- No Databricks Liquibase extension or JDBC connection was validated.

**Decision:** Stop the Liquibase evaluation. Do not introduce Liquibase or Alembic as the project's database migration framework. The project will use Databricks-native resource and pipeline management for the objects those capabilities own.

### Verification Performed

The custom migration implementation was exercised through unit tests and against the Databricks workspace.

The last reported full test run included:

```text
tests/unit/test_bronze_market_data.py
tests/unit/test_migrations.py
tests/unit/test_project_setup.py

16 passed
```

Code-quality checks also completed successfully:

```bash
uv run ruff check .
uv run ruff format --check .
```

These results document the earlier custom implementation. They do not represent verification of the new Lakeflow architecture.

### Architectural Decisions

- **Git as source of truth:** Source code, resource definitions, pipeline definitions, and analytical models should be maintained in the repository.
- **Native Databricks capabilities first:** Prefer platform-managed functionality over custom frameworks when the platform provides an appropriate capability.
- **Declarative Automation Bundles:** Use bundles to deploy supported workspace resources and configurations.
- **Unity Catalog and Delta Lake:** Use the platform's governance and transactional storage capabilities rather than building parallel management layers.
- **Unity Catalog Volumes for raw source landing:** Use Volumes to retain extracted source files independently of Bronze Delta tables.
- **Python provider integrations:** Use Python for external provider API interactions and preparation of extracted source data.
- **Auto Loader for file ingestion:** Use Auto Loader to incrementally discover and ingest supported files. It is not a generic replacement for REST API integrations.
- **Lakeflow pipeline ownership:** Use Lakeflow Spark Declarative Pipelines to manage the tables and transformations defined by those pipelines.
- **Business-level idempotency:** Do not confuse Auto Loader's file-processing progress with deduplication of market-data observations across separate files. Bronze processing must apply explicit observation identity and versioning rules.
- **dbt for analytical modeling:** Use dbt for analytical SQL models, model dependencies, tests, and documentation.
- **Lakeflow Jobs for orchestration:** Coordinate ingestion, pipeline execution, and other workflow tasks.
- **No generic migration framework:** Do not maintain a custom migration runner, Liquibase, or Alembic for objects managed by Databricks pipelines.
- **Clear ownership boundaries:** Avoid having multiple tools independently manage the same table.
- **Disposable-environment testing:** Validate reconstruction and deployment in an appropriately isolated environment rather than relying on destructive changes to existing workspace objects.

### Important Lifecycle Distinction

The project distinguishes between deploying definitions, executing workloads, and restoring data.

1. Bundles deploy supported resource definitions and configuration.
2. Lakeflow pipeline execution materializes or updates pipeline-managed tables and views.
3. dbt execution creates or updates dbt-managed analytical objects.
4. Provider integrations retrieve source data and land it through the appropriate ingestion workflow.
5. Auto Loader tracks file-processing progress; it does not provide business-level deduplication of observations.
6. Unity Catalog governs access and organization; Delta Lake provides transactional storage.

Deploying a bundle does not, by itself, execute a pipeline or restore its data. Rebuilding definitions and restoring records are separate responsibilities.

### Remaining Work

1. Create a small, controlled Parquet dataset in a Unity Catalog Volume.
2. Configure a Lakeflow Spark Declarative Pipeline.
3. Use Auto Loader to ingest the files from the Volume.
4. Materialize a pipeline-managed Bronze table.
5. Deploy the pipeline resource through Declarative Automation Bundles.
6. Execute the pipeline and verify the resulting table.
7. Test incremental file discovery and processing.
8. Explore schema evolution and an incompatible schema change.
9. Document the pipeline's ownership of its managed objects.
10. Review the existing custom migration implementation and identify objects that need to transition.
11. Remove the legacy migration runner, SQL migration files, and associated tests after the replacement is verified.

The POC should establish the actual capabilities and limitations of Databricks Free Edition rather than assume that every feature available in other Databricks environments is available here.

### Completion Criteria

Stage 2 will be complete when:

- A Lakeflow pipeline is defined in the repository.
- The pipeline is deployed through Declarative Automation Bundles.
- Auto Loader ingests a controlled file-based dataset from a Unity Catalog Volume.
- Pipeline execution materializes the expected Bronze table.
- Incremental file processing is demonstrated.
- Schema evolution behavior is demonstrated and documented.
- The responsibilities of bundles, pipelines, Unity Catalog, Volumes, Auto Loader, and Delta Lake are clear.
- The legacy migration implementation has been retired where its responsibilities have been replaced.
- The relevant deployment and execution workflow is reproducible.

---

## Stage 3 — Bronze Ingestion and Historical Market Data

**Status: Foundation started**

### Objective

Implement repeatable historical market-data ingestion using the established Python, Unity Catalog Volume, Auto Loader, and Lakeflow architecture.

The initial implementation focuses on Yahoo Finance historical OHLCV data retrieved through the `yfinance` client.

### Work Completed Ahead of Stage 3

The initial Bronze database foundation was implemented as part of the earlier custom migration work.

Completed:

- Created the `workspace.market_data` schema.
- Defined the Bronze Yahoo market-bars table.
- Added the corresponding SQL migration.
- Implemented initial Bronze market-data functionality.
- Added unit tests for Bronze behavior.
- Executed the migration and inspected the resulting Databricks objects.

These accomplishments establish an initial Bronze foundation, but the table's existence does not mean that the complete historical ingestion workflow has been implemented.

### Target Ingestion Workflow

The agreed initial ingestion path is:

**Python / yfinance → Unity Catalog Volume → Auto Loader → Lakeflow Bronze**

1. Python retrieves historical market data for a requested date range.
2. The extracted observations are written as Parquet files to a Unity Catalog Volume.
3. Each extraction produces uniquely identified files so that separate runs do not overwrite previously landed data.
4. Lakeflow uses Auto Loader to incrementally discover and ingest newly landed files.
5. Bronze processing applies observation identity and content-hash rules to determine whether an observation is new, unchanged, or revised.
6. Bronze Delta tables preserve provider observations, version information, and ingestion lineage.

Raw source files are retained independently of Bronze tables to support replay, investigation, and reprocessing.

Auto Loader provides file-level processing progress. It does not deduplicate overlapping observations contained in different extraction files. Business-level idempotency and observation versioning remain explicit Bronze processing responsibilities.

The Yahoo observation business key is:

`(provider, symbol, interval, provider_timestamp_utc)`

The content hash distinguishes an unchanged observation from a changed provider observation with the same business key.

- Same key and same content hash: do not create another observation version.
- Same key and changed content hash: preserve the changed observation as a new version.
- New key: insert a new observation.

The `is_current` indicator identifies the latest observation version independently of its data-quality status.

### Remaining Work

- Transition the Bronze table to its intended Databricks-native ownership.
- Implement the Python historical Yahoo Finance extraction.
- Define the raw Parquet file contract, including schema, timestamps, null and non-finite value handling, and relevant extraction metadata.
- Establish the Unity Catalog Volume raw source landing area.
- Implement uniquely identified extraction files and avoid overwriting prior source files.
- Configure Auto Loader within a Lakeflow pipeline.
- Load actual historical market data into Bronze.
- Implement and test business-level idempotency and observation versioning.
- Validate provider metadata and ingestion lineage.
- Demonstrate repeatable ingestion, including overlapping historical date ranges.
- Explore Delta transaction logs, table history, and schema enforcement.
- Add SQL analysis and validation examples.
- Document the Bronze data contract and ingestion behavior.

### Completion Criteria

Historical market data can be loaded repeatedly into Bronze Delta tables with appropriate lineage, preservation, and validation. Repeated identical observations do not create unnecessary versions, while changed provider observations are retained. Raw source files remain available for replay and investigation.

The ingestion workflow and pipeline-managed table definitions can be reconstructed independently of the previous workspace.

---

## Stage 7 — Incremental Ingestion and Schema Evolution

**Status: Not started**

### Objective

Demonstrate incremental processing and controlled handling of evolving source data.

### Planned Work

- Implement incremental ingestion using Auto Loader.
- Explore Auto Loader schema evolution behavior.
- Distinguish source schema changes from business data-contract changes.
- Validate handling of new, missing, and incompatible fields.
- Test file-level processing progress and recovery.
- Test business-level idempotency separately from file-level processing.
- Test replay of retained raw source files.
- Document checkpointing, recovery, and reprocessing behavior.

### Completion Criteria

The platform can process newly landed files incrementally and handle expected schema changes without silently compromising data quality. File-processing progress, business-level deduplication, and replay behavior are understood and documented.

---

## 10. Engineering Baseline

The following development tooling has been established:

| Component | Technology |
|---|---|
| Python | CPython 3.12 |
| Dependency management | uv |
| Project packaging | setuptools |
| Data contracts | Pydantic 2 |
| Testing | pytest |
| Linting | Ruff |
| Formatting | Ruff |
| Git hooks | pre-commit |
| CI | GitHub Actions |
| Databricks deployment | Databricks CLI / Declarative Automation Bundles |
| Lakehouse storage | Delta Lake |
| Data governance | Unity Catalog |
| Raw source landing | Unity Catalog Volumes (planned) |
| File ingestion | Auto Loader (planned) |
| Managed transformations | Lakeflow Spark Declarative Pipelines (planned) |
| Analytical modeling | dbt (planned) |
| Workflow orchestration | Lakeflow Jobs (planned) |

The project uses `uv.lock` to maintain reproducible Python dependency resolution.

The local development workflow avoids manual `pip` and `requirements.txt` dependency management.

The table distinguishes the established engineering baseline from Databricks capabilities that remain planned.

---

## 12. Next Implementation Milestone

**Complete the Lakeflow and Auto Loader proof of concept.**

The immediate goal is to demonstrate the following workflow:

1. Create a small, controlled Parquet dataset.
2. Land the files in a Unity Catalog Volume.
3. Configure a Lakeflow Spark Declarative Pipeline.
4. Configure Auto Loader to ingest the files from the Volume.
5. Define and materialize a pipeline-managed Bronze table.
6. Deploy the pipeline resource through Declarative Automation Bundles.
7. Execute the pipeline in Databricks.
8. Inspect the resulting table and its metadata.
9. Add another file and verify incremental processing.
10. Test schema evolution and an incompatible schema change.
11. Document the responsibilities of Volumes, Auto Loader, Lakeflow, Unity Catalog, and Delta Lake.
12. Identify and retire the legacy migration implementation once its responsibilities have been replaced.

The POC should validate the managed file-ingestion and table-lifecycle capabilities independently of the full Yahoo Finance integration. Once that foundation works, the project can implement the actual Python/yfinance extraction and its raw-file contract as part of Stage 3.

The desired end state is that a replacement Databricks workspace can have its supported resources deployed from Git, its pipeline-managed data objects reconstructed by executing the pipeline definitions, and its records repopulated through repeatable ingestion workflows.

The project should then proceed to historical market-data ingestion rather than expanding the infrastructure evaluation indefinitely.
