## Current Project Status

**Current stage: Stage 3 — Bronze Ingestion and Historical Market Data**

Stage 1 — Project Foundation and Databricks Environment — is complete.

Stage 2 — Lakehouse Foundation and Lakeflow POC — is complete. The project established its Databricks development environment, deployed resources through Declarative Automation Bundles, and demonstrated Unity Catalog Volumes, Auto Loader, Lakeflow-managed Bronze tables, and incremental file ingestion.

Stage 3 — Bronze Ingestion and Historical Market Data — has completed its technical implementation and verification. Documentation and final repository updates remain.

The implemented historical Yahoo Finance ingestion architecture is:

**Python / yfinance → Unity Catalog Volume → Auto Loader → Lakeflow Bronze**

Python retrieves historical market data, transforms it into a normalized contract, and writes explicitly typed Parquet files to uniquely identified ingestion-run directories in a Unity Catalog Volume.

Auto Loader, running within a Lakeflow Spark Declarative Pipeline, incrementally discovers and processes newly landed files. Lakeflow manages the resulting Bronze streaming table as a managed Delta table.

The implementation preserves provider-derived observations, raw records, provider timestamps, and ingestion-run lineage.

An important architectural distinction has been demonstrated: Auto Loader tracks file-processing progress, not business-level observation identity. A new extraction containing overlapping observations is appended to Bronze, even when some observations are identical to previously ingested records. Business-level reconciliation and current-version selection remain downstream responsibilities.

Schema evolution has also been explored through isolated pipelines. The project demonstrated both additive schema evolution and rescue mode, including the behavior of the `_rescued_data` column.

Delta transaction history, time travel, file retention, and independent pipeline recreation have been investigated. A new pipeline with independent state successfully rebuilt a separate Bronze table from the retained raw Parquet files without retrieving the data from Yahoo again.

| Stage | Description | Status |
|---|---|---|
| 1 | Project Foundation and Databricks Environment | Complete |
| 2 | Lakehouse Foundation and Lakeflow POC | Complete |
| 3 | Bronze Ingestion and Historical Market Data | Technical work complete; documentation remaining |
| 4 | Silver Transformations and Reconciliation | Not started |
| 5 | Gold Analytics, dbt, and Databricks SQL | Not started |
| 6 | Orchestration and Lakeflow Jobs | Not started |
| 7 | Incremental Ingestion and Schema Evolution | Experiments completed in Stage 3; further work deferred |
| 8 | Streaming Market Data | Not started |
| 9 | Platform Engineering and Optimization | Not started |

---

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

The Lakehouse and Lakeflow POC demonstrated:

- A Unity Catalog Volume used as a raw Parquet landing location.
- Auto Loader discovering and incrementally ingesting Parquet files.
- A Lakeflow Spark Declarative Pipeline creating and managing a Bronze streaming table.
- Repeated pipeline execution without re-ingesting previously processed files.
- Bundle deployment of pipeline resources.
- Separation of bundle deployment from pipeline execution.
- Delta table history and metadata inspection.

The POC initially ingested four records and subsequently ingested two additional records, resulting in six records in the managed Bronze table.

Schema evolution was subsequently explored through separate experiments. The additive-evolution experiment demonstrated automatic addition of a new field, while the rescue-mode experiment demonstrated preservation of an unexpected field in `_rescued_data`.

**### Completion Criteria**

Stage 2 is complete. The project has demonstrated the basic Databricks-native resource deployment, governed file landing, incremental ingestion, and pipeline-managed table lifecycle needed for the historical ingestion implementation.

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

### Implemented Ingestion Workflow

The implemented historical ingestion path is:

**Python / yfinance → Unity Catalog Volume → Auto Loader → Lakeflow Bronze**

1. The Databricks Job executes `notebooks/07_yahoo_historical_landing.py`.
2. The notebook retrieves historical market data through yfinance.
3. The Python transformation normalizes the provider records and adds ingestion metadata.
4. Spark creates a DataFrame using an explicit schema.
5. The landing writer stores the records as Parquet files in a unique ingestion-run directory within the Unity Catalog Volume.
6. Auto Loader discovers newly landed files.
7. The Lakeflow pipeline processes those files into the managed Bronze streaming table.

The main Bronze table is:

`workspace.market_data.bronze_yahoo_historical_bars`

The landing contract preserves:

- Provider and symbol.
- Provider interval.
- Local business date.
- OHLCV and associated market fields.
- Original provider timestamp as a local ISO-8601 string with offset.
- Provider IANA timezone.
- UTC-converted provider timestamp.
- Ingestion run identifier and ingestion timestamp.
- Original provider-derived record as JSON.

For Yahoo daily data, the provider timestamp represents a midnight local date label, not the actual market close time. The separate `bar_date` field preserves the provider-local business date.

### Schema Evolution Experiments

Two isolated Lakeflow pipelines were used to investigate Auto Loader schema behavior.

**Additive evolution:** The default schema-evolution behavior was demonstrated by adding a new field to subsequently landed Parquet files. The table schema evolved, and older records contained null for the new field.

**Rescue mode:** A separate pipeline configured with `cloudFiles.schemaEvolutionMode = rescue` preserved an unexpected field in `_rescued_data` rather than promoting it into the table schema.

These experiments established that schema detection and preservation do not replace data-contract governance. Unexpected fields still require review and an explicit decision about whether to change the accepted contract.

### Delta History and Time Travel

The main Yahoo Bronze table's Delta history was inspected.

The history showed:

- Initial table creation.
- Lakeflow pipeline setup.
- A streaming update appending the initial six records.
- A later streaming update appending four records from a second extraction run.

Time travel was used to inspect historical table versions. File retention and log retention were investigated separately, establishing that retained transaction history does not guarantee that the underlying data files remain available.

The logical Lakeflow table name is the supported interface. Internal materialization and backing-table names exposed through metadata inspection are implementation details.

### Ingestion Validation

SQL validation was developed and executed against the Yahoo Bronze table.

Validation covered:

- Record counts and distinct symbols.
- Missing required metadata.
- Rescued records.
- OHLC plausibility and volume validity.
- Provider and timestamp metadata.
- Ingestion-run lineage.
- Duplicate business keys across ingestion runs.
- Reconciliation between landed Parquet records and Bronze records.

The initial six-record ingestion was reconciled against its raw landing files. A subsequent overlapping extraction was also validated, demonstrating that Bronze preserves repeated business observations across distinct ingestion runs.

The validation queries are maintained in:

`sql/validation/bronze_yahoo_historical.sql`

### Repeatability and Independent Recreation

Two historical extraction runs were landed:

- First run: six records.
- Second run: four records, with overlapping business dates.

The primary Bronze pipeline ingested all ten records. Re-running the pipeline without new files did not append the same files again.

A separate recreation pipeline was then deployed with independent pipeline state and a new target table:

`workspace.market_data.bronze_yahoo_historical_recreation`

The recreation pipeline ingested all ten records from the existing raw Parquet files without calling Yahoo Finance again.

This demonstrated that the pipeline-managed Bronze table can be reconstructed independently of the original pipeline state, provided the raw landing files remain available.

### Architectural Boundaries

The current implementation deliberately does not perform business-level deduplication or observation versioning in Bronze.

It does not currently implement:

- Observation content hashes.
- `is_current` or current-version selection.
- Business-key uniqueness enforcement.
- A persistent dead-letter or data-quality findings framework.
- Automated orchestration between the extraction job and Bronze pipeline.

These are separate design and implementation decisions. They should not be attributed to the current Bronze ingestion workflow.

### Completion Criteria

Stage 3's technical completion criteria have been demonstrated:

- Historical Yahoo market data can be extracted and landed as durable Parquet files.
- Auto Loader incrementally ingests newly landed files.
- Lakeflow manages the resulting Bronze Delta table.
- Ingestion lineage and provider metadata are preserved.
- SQL validation establishes expected record contents and source-to-Bronze reconciliation.
- Repeated extraction runs demonstrate the distinction between file-level processing and business-level duplicates.
- A separate pipeline can recreate a Bronze table from retained raw files without calling the provider.

Remaining Stage 3 work is to finalize documentation, review the repository artifacts, and commit the completed implementation.

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
