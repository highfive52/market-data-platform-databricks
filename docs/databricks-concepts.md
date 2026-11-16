# Databricks Concepts

## 1. Purpose

This document describes the Databricks platform concepts, services, and development practices used by the Market Data Platform Databricks implementation.

The goal is to understand not only how to use Databricks, but also the problems its components solve and how they relate to established data engineering and software engineering principles.

This is a learning reference, not a comprehensive description of every Databricks capability. Concepts will be added as they become relevant to the implementation.

## 2. Databricks and the Cloud Platform

Databricks is a managed data and AI platform that operates on cloud infrastructure provided by AWS, Azure, or Google Cloud.

It is not a general-purpose cloud application hosting platform. Its primary focus is providing an integrated environment for:

- Data engineering and processing
- Data storage and lakehouse architectures
- Data analytics and SQL
- Data governance
- Machine learning and AI

The underlying cloud provider supplies infrastructure such as compute, storage, networking, and identity services. Databricks provides managed capabilities and abstractions for building and operating data workloads on that infrastructure.

### 2.1 Data Engineering vs. Application Engineering

Databricks applies software engineering practices to data and analytics workloads.

The development practices are familiar:

- Source control and versioning
- Dependency management
- Modular application code
- Automated testing
- Build and packaging processes
- Deployment automation
- Monitoring and operational management

However, the workloads being engineered are different from conventional cloud applications.

A typical cloud application might expose APIs, serve web requests, and implement interactive business functionality.

A Databricks workload typically ingests, transforms, validates, stores, or analyzes data.

For this project, the distinction is:

| Concern | Responsibility |
|---|---|
| Data platform | Databricks, Spark, Unity Catalog, Delta Lake, Lakeflow |
| Data application | Python packages implementing provider integrations, domain logic, and application-specific processing |
| Development tooling | uv, pytest, Ruff, Git, Python wheels |
| Deployment tooling | Databricks CLI and Declarative Automation Bundles |

The objective is to use software engineering practices to build a reliable and maintainable data platform.

## 3. Databricks Workspace

A Databricks workspace is the primary environment through which users interact with Databricks resources.

It provides access to capabilities such as:

- Notebooks and workspace files
- Jobs and workflows
- Compute resources
- Data exploration and SQL
- Unity Catalog
- Administrative and development tools

A workspace is not itself the data warehouse or data lake. It is the managed environment through which users develop, deploy, execute, and manage data workloads.

This project currently uses one development workspace and deploys resources into it through the Databricks CLI.

## 4. Compute and Execution

Databricks separates the definition of a workload from the compute environment that executes it.

Compute resources provide the processing environment for notebooks, jobs, and other workloads.

### 4.1 Serverless Compute

This project uses Databricks serverless compute for both notebook/job execution and Lakeflow pipeline processing.

Serverless compute allows Databricks to provision and manage the underlying execution infrastructure rather than requiring the project to configure and maintain traditional clusters.

Two execution paths currently exist:

- **Legacy Yahoo historical job:** The `yahoo_historical_bronze` job runs `notebooks/02_bronze.py` and uses the packaged Python application wheel.
- **Bronze Auto Loader POC:** The `bronze_poc` Lakeflow Spark Declarative Pipeline runs `pipelines/bronze_poc.py` using serverless pipeline compute.

The POC pipeline is configured in triggered mode. A triggered run processes available input and stops after the update completes, rather than continuously running.

The two paths are intentionally distinct. The legacy job represents the earlier application-managed ingestion approach; the POC explores Databricks-native file ingestion and pipeline-managed tables.

### 4.2 Apache Spark

Apache Spark provides the distributed data-processing engine used by Databricks.

PySpark exposes Spark functionality through Python. A Spark DataFrame represents a distributed dataset, while transformations describe the processing to be performed.

Spark supports both batch and streaming workloads:

- **Batch processing:** Processes a bounded dataset.
- **Structured Streaming:** Processes data incrementally as new input becomes available.

The Bronze Auto Loader POC uses Structured Streaming. Its source is configured with:

```python
spark.readStream.format("cloudFiles")
```

The `cloudFiles` source identifies Auto Loader. The pipeline reads Parquet files from a Unity Catalog Volume and returns a streaming DataFrame to Lakeflow.

This separates responsibilities:

- Python provider integrations retrieve and prepare source data.
- Spark processes the data using distributed DataFrame operations.
- Auto Loader discovers and incrementally ingests files.
- Lakeflow manages pipeline execution and the resulting table.

The POC demonstrates that the application does not need to implement its own file-discovery loop, streaming checkpoint management, or Delta table write lifecycle for this ingestion path.

## 5. Lakehouse Storage and Data Management

### 5.1 Delta Lake

Delta Lake is the transactional table-storage layer used by Databricks.

A Delta table consists of data files, stored in Parquet format, and a transaction log that records table changes. The transaction log provides the metadata needed to manage table versions and transactional operations.

This is different from storing raw Parquet files in a directory:

- **Parquet files:** Store columnar data but do not independently provide table-level transaction history.
- **Delta tables:** Combine Parquet data files with a transaction log to provide transactional table behavior, schema enforcement, and table history.

The project uses both formats for different purposes.

Raw provider-derived data is initially landed as Parquet files in a Unity Catalog Volume. Lakeflow then ingests those files into a managed Delta streaming table.

The Bronze Auto Loader POC created:

`workspace.market_data.bronze_poc_yahoo_market_bars`

The table is managed by Lakeflow. Its data is stored in Databricks-managed storage, rather than in the raw Volume directory.

`DESCRIBE HISTORY` can be used to inspect the Delta table's transaction history. The POC showed an initial streaming update that added four records, followed by another update that added two records.

`DESCRIBE DETAIL` can be used to inspect Delta table metadata, including its format, storage location, size, and properties. In this POC, the command exposed an internal Lakeflow materialization/backing-table name in its output. That is an implementation detail of the pipeline, not the logical table name that application queries should depend on.

Use the declared table name when querying the table:

`workspace.market_data.bronze_poc_yahoo_market_bars`

Delta transaction history describes changes to the table. It should not be confused with business-level observation versioning or ingestion-run history.

### 5.2 Unity Catalog

Unity Catalog provides centralized governance for data and other assets in Databricks.

Its hierarchy is:

- **Catalog**
- **Schema**
- **Tables, Volumes, and other securable objects**

This project currently uses:

- Catalog: `workspace`
- Schema: `market_data`

The catalog and schema organize the project's data objects and provide the context for permissions and access management.

### 5.3 Unity Catalog Volumes

Unity Catalog governs more than tables. It also provides Volumes for managing access to files stored in cloud object storage.

A Volume provides a governed file-storage location within a catalog and schema. It can be used for files such as Parquet, JSON, CSV, and other supported formats.

The project uses a Volume for raw provider-derived market data:

`workspace.market_data.raw_market_data`

Its path is:

`/Volumes/workspace/market_data/raw_market_data/`

The historical Yahoo POC writes Parquet files beneath:

`/Volumes/workspace/market_data/raw_market_data/poc/yahoo/historical/`

The Volume is the raw-file landing area. It does not convert those files into tables or provide Delta transaction semantics.

The distinction is:

- **Volume:** Governed file storage for raw and intermediate files.
- **Delta table:** Structured, queryable data managed through the Delta transaction log.

Raw-file immutability is an application-level convention in this project. A Volume does not inherently enforce append-only behavior.

### 5.4 Auto Loader and Lakeflow Spark Declarative Pipelines

Auto Loader incrementally discovers and processes new files arriving in supported cloud storage locations.

It is implemented through Spark's `cloudFiles` source and is designed for file-based ingestion. It is not responsible for calling external provider APIs.

The project separates provider ingestion from file ingestion:

1. A Python provider integration retrieves data.
2. The integration writes provider-derived records to a Unity Catalog Volume.
3. Auto Loader discovers new files.
4. A Lakeflow Spark Declarative Pipeline processes the files and manages the resulting table.

The initial implementation uses:

`pipelines/bronze_poc.py`

The pipeline declares a streaming table using the Lakeflow Python API:

```python
@dp.table
```

The function returns a streaming DataFrame sourced from Auto Loader. Lakeflow manages the pipeline execution and the lifecycle of the declared table.

The POC demonstrated incremental ingestion:

- Initial landing: four records, two each for AAPL and MSFT.
- Subsequent landing: two additional records, one each for AAPL and MSFT.
- Subsequent pipeline update: the table contained six records, with the original four retained and the two new records added.

This demonstrates incremental file discovery and ingestion. It does not demonstrate business-key deduplication across separate files. Auto Loader tracks file ingestion state; it does not determine whether two different files contain the same logical market observation.

The pipeline currently uses Parquet input without implementing schema evolution or a rescued-data strategy. Those capabilities remain future work.

### 5.5 SQL Reference — Bronze POC Validation

The following statements inspect the logical Bronze table, its contents, and its Delta metadata.

```sql
-- Inspect the Bronze POC table definition.
DESCRIBE TABLE workspace.market_data.bronze_poc_yahoo_market_bars;

-- Summarize the ingested observations.
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

-- Inspect Delta table details.
DESCRIBE DETAIL workspace.market_data.bronze_poc_yahoo_market_bars;

-- Inspect Delta transaction history.
DESCRIBE HISTORY workspace.market_data.bronze_poc_yahoo_market_bars;
```

Raw Parquet files can also be queried directly from the Volume without first creating a permanent table:

```sql
SELECT *
FROM read_files(
    '/Volumes/workspace/market_data/raw_market_data/poc/yahoo/historical/run_id=6adf317d-19a6-43d7-9dd7-8e3190e19beb',
    format => 'parquet'
)
ORDER BY symbol, provider_timestamp_utc;
```

The path above identifies one specific POC ingestion run. Change the `run_id` directory when inspecting another run.

The repeatable validation statements are maintained in:

`sql/validation/bronze_poc.sql`

## 6. Databricks Jobs and Lakeflow Pipelines

Databricks provides multiple execution and orchestration mechanisms. They have related but distinct responsibilities.

### 6.1 Databricks Jobs

Jobs execute and coordinate tasks such as notebooks, Python scripts, pipelines, and other supported workloads.

The project currently retains the `yahoo_historical_bronze` job, which runs `notebooks/02_bronze.py` using the packaged Python application wheel.

This is the earlier application-managed ingestion path.

### 6.2 Lakeflow Spark Declarative Pipelines

Lakeflow Spark Declarative Pipelines define and execute managed data-processing pipelines.

The project has introduced the `bronze_poc` pipeline, which runs `pipelines/bronze_poc.py`.

The pipeline uses Auto Loader to incrementally ingest Parquet files from the raw-data Volume and creates the Lakeflow-managed Bronze streaming table.

The pipeline is configured in triggered mode and uses serverless compute.

### 6.3 Separation of Responsibilities

The distinction is important:

- Jobs coordinate the execution of tasks.
- Lakeflow pipelines define and manage data-processing pipelines and their tables.
- Auto Loader discovers and ingests new files.
- Delta Lake provides transactional table storage.

A bundle deployment creates or updates the configured workspace resource. It does not itself execute the pipeline or populate its table. Pipeline execution is a separate operation.

## 7. Declarative Automation Bundles

Declarative Automation Bundles (formerly Databricks Asset Bundles) provide a way to define, validate, deploy, and manage Databricks project resources as source-controlled configuration.

They apply infrastructure-as-code and software delivery practices to data and AI projects.

A bundle can contain:

- Source files and notebooks
- Python application artifacts
- Job and pipeline definitions
- Environment-specific configuration
- Tests and supporting project metadata

Bundle configuration is primarily expressed through YAML files.

### 7.1 Bundle Configuration

The root configuration file is `databricks.yml`.

It identifies the bundle, includes additional resource definitions, configures build artifacts, and defines deployment targets.

This project uses:

```text
databricks.yml
resources/
    jobs.yml
    pipelines.yml
```

The root configuration includes the resource YAML files and defines how to build the Python wheel.

### 7.2 Deployment Targets

Targets describe the environments into which a bundle can be deployed.

Common examples include:

- `dev`: Development and experimentation
- `staging`: Pre-production validation
- `prod`: Production execution

Targets allow the same project definition to be deployed with environment-specific configuration.

This project currently defines only a `dev` target.

### 7.3 Bundle Lifecycle

The primary bundle operations used in this project are:

```bash
# Validate bundle configuration
databricks bundle validate -t dev --profile MDP

# Build and deploy configured resources
databricks bundle deploy -t dev --profile MDP

# Inspect deployed resources
databricks bundle summary -t dev --profile MDP

# Execute a deployed job
databricks bundle run yahoo_historical_bronze \
    -t dev \
    --profile MDP
```

Validation, deployment, and execution are separate operations.

Deploying a bundle synchronizes its declared resources and files with the target workspace. Running a job executes the deployed workload; it does not automatically deploy uncommitted local changes.

A deployment without resource selection can affect all resources declared in the bundle. During development, selective deployment can be used to limit which resources are created or updated.

### 7.4 Scope of Bundle Management

Declarative Automation Bundles manage supported Databricks workspace resources through version-controlled configuration.

The project currently defines both a legacy job and a Lakeflow pipeline in its bundle resources:

- `resources/jobs.yml`
- `resources/pipelines.yml`

The `bronze_poc` pipeline is bundle-managed. Its source code is maintained in `pipelines/bronze_poc.py`.

The pipeline definition declares the logical Bronze streaming table:

`workspace.market_data.bronze_poc_yahoo_market_bars`

The table itself is created and updated through Lakeflow pipeline execution. It is not separately declared as a bundle-managed table resource.

This distinction separates three responsibilities:

- **Bundle deployment:** Creates or updates the pipeline resource and deploys its associated source files.
- **Lakeflow execution:** Runs the pipeline and creates or updates its managed tables.
- **Data ingestion:** Reads source files and populates the resulting tables.

Deploying the bundle does not restore the table's data or execute the pipeline. Reconstructing workspace resources and repopulating data are separate operations.

The project uses a global wheel artifact configuration in `databricks.yml`. As a result, even a selective pipeline deployment may still build and upload the configured Python wheel. The wheel is used by the legacy job; the current Bronze POC pipeline does not depend on it.

## 8. Python Application Packaging

### 8.1 Python Wheels

A Python wheel is a built distribution of a Python package.

It allows application code to be installed into another Python environment without requiring the source repository or a local development environment.

This project uses `uv` to build a wheel:

```bash
uv build --wheel
```

The resulting artifact is stored in:

```text
dist/market_data_platform_databricks-0.1.0-py3-none-any.whl
```

The bundle configuration builds this wheel during deployment and makes it available to the Databricks job environment.

The wheel remains relevant to the legacy application-managed job and future Python application workloads. The current Auto Loader POC uses a Lakeflow pipeline definition and does not require the wheel for its ingestion logic.

### 8.2 Local Development vs. Databricks Runtime

The project deliberately separates local development from Databricks execution.

| Local environment | Databricks environment |
|---|---|
| Python 3.12 | Managed Python runtime |
| uv dependency management | Databricks-managed runtime and workload dependencies |
| pytest | Databricks job execution and integration validation |
| pandas and local Python logic | Spark DataFrames and distributed processing where appropriate |
| Local Python package | Installed application wheel for workloads that require it |
| Local development tools | Managed serverless compute |

This allows domain logic to be developed and tested locally while using Databricks for platform-specific execution and storage.

## 9. Project Development Workflow

### 9.1 Lakeflow Pipeline Development and Execution

The Bronze Auto Loader POC introduced a pipeline-based development workflow.

The workflow is:

1. Implement the pipeline definition in `pipelines/bronze_poc.py`.
2. Define the pipeline resource in `resources/pipelines.yml`.
3. Validate the bundle configuration.
4. Deploy the specific pipeline resource.
5. Trigger the pipeline in Databricks.
6. Inspect the resulting table through Databricks SQL.
7. Verify incremental behavior by landing additional files and running the pipeline again.

The pipeline can be selectively deployed:

```bash
databricks bundle deploy \
    --select pipelines.bronze_poc \
    -t dev \
    --profile MDP
```

The deployment and execution steps are separate. A successful deployment confirms that the pipeline resource and its associated source files have been deployed; it does not confirm that the pipeline has run successfully or ingested data.

### 9.2 Validation and Testing

The project uses different validation approaches for different layers:

- **Local Python validation:** pytest and Ruff validate application code and project conventions.
- **Bundle validation:** `databricks bundle validate` checks the bundle configuration.
- **Pipeline validation:** A triggered pipeline run verifies that the deployed pipeline can execute.
- **Data validation:** Databricks SQL queries inspect the resulting table and its contents.
- **Incremental-ingestion validation:** Additional raw files are landed and the pipeline is run again to verify that new records are ingested without re-ingesting previously processed files.

These checks provide evidence at different levels. Passing local tests does not establish that a deployed pipeline works, and a successful pipeline run does not by itself establish business-level data quality.

## 10. References

- [Databricks Lakehouse Platform](https://docs.databricks.com/)
- [Declarative Automation Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles/)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [Delta Lake Documentation](https://docs.delta.io/)
- [Unity Catalog Documentation](https://docs.databricks.com/aws/en/data-governance/unity-catalog/)
- [Auto Loader](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/)
- [Lakeflow Spark Declarative Pipelines](https://docs.databricks.com/aws/en/ldp/)
