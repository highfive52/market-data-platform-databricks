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
| Data platform | Databricks, Spark, Unity Catalog, Delta Lake, jobs |
| Data application | Python packages implementing ingestion, transformation, reconciliation, and analytics |
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

Serverless compute allows Databricks to provision and manage the execution environment without requiring users to configure and maintain the underlying compute infrastructure.

Databricks manages the provisioning and lifecycle of the execution environment.

For this project, Serverless is used to execute the Yahoo historical ingestion notebook.

The job environment specifies its dependencies, including the project's Python wheel.

This means the project does not need to provision or administer a traditional Spark cluster for the current development workflow.

### 4.2 Apache Spark

Apache Spark is a distributed data processing engine used by Databricks.

Spark provides APIs for working with structured data, including:

- DataFrames
- SQL queries
- Data transformations
- Aggregations
- Distributed processing

Databricks provides a managed Spark environment and integrates it with its storage, governance, and orchestration capabilities.

In this project, Spark is responsible for converting application transformation results into DataFrames and writing those records to Delta tables.

The distinction between local Python processing and Spark processing is intentional:

- Python and pandas handle provider integration and domain transformations where appropriate.
- Spark handles distributed data processing and integration with Databricks storage.

## 5. Lakehouse Storage and Data Management

### 5.1 Delta Lake

Delta Lake is a storage layer that adds transactional and data-management capabilities to data stored in cloud object storage.

It uses Parquet data files together with a transaction log to track table changes and provide capabilities such as:

- ACID transactions
- Schema enforcement
- Schema evolution
- Version history and time travel
- Reliable concurrent reads and writes

Delta tables can be queried through Spark and Databricks SQL.

In this project, Delta Lake is the persistence layer for Bronze, Silver, and Gold data.

### 5.2 Unity Catalog

Unity Catalog provides centralized governance and management of data and other securable resources in Databricks.

It organizes data using a hierarchical namespace:

```text
catalog.schema.table
```

For example:

```text
workspace.market_data.bronze_yahoo_market_bars
```

This identifies:

- Catalog: `workspace`
- Schema: `market_data`
- Table: `bronze_yahoo_market_bars`

Unity Catalog provides capabilities for:

- Organizing data assets
- Managing permissions
- Discovering data
- Tracking lineage
- Applying governance policies

The project uses Unity Catalog to organize its Bronze, Silver, and Gold Delta tables.

## 5.3 SQL Reference — Catalog and Table Inspection

Databricks SQL provides commands for exploring Unity Catalog objects and inspecting table definitions.

These commands are useful during development, troubleshooting, and validating that deployed tables match their expected data contracts.

### Inspect the Current Catalog and Schema

```sql
SELECT
    current_catalog(),
    current_schema();
```

### List Catalogs

```sql
SHOW CATALOGS;
```

### List Schemas in a Catalog

```sql
SHOW SCHEMAS IN workspace;
```

### Describe a Schema

```sql
DESCRIBE SCHEMA workspace.market_data;
```

### List Tables in a Schema

```sql
SHOW TABLES IN workspace.market_data;
```

### Describe a Table

Displays the table's columns, data types, and comments.

```sql
DESCRIBE TABLE workspace.market_data.bronze_yahoo_market_bars;
```

### Extended Table Description

Displays additional table metadata, including storage information and table properties.

```sql
DESCRIBE TABLE EXTENDED workspace.market_data.bronze_yahoo_market_bars;
```

### Inspect Table Data

```sql
SELECT *
FROM workspace.market_data.bronze_yahoo_market_bars
LIMIT 10;
```

### Count Table Records

```sql
SELECT COUNT(*) AS row_count
FROM workspace.market_data.bronze_yahoo_market_bars;
```

### Inspect Table History

Delta Lake maintains a transaction log that records changes to a table.

```sql
DESCRIBE HISTORY workspace.market_data.bronze_yahoo_market_bars;
```

This is useful for understanding when data was written, which operations were performed, and how the table has changed over time.

### Inspect Table Schema Through SQL

```sql
SELECT
    column_name,
    data_type,
    is_nullable
FROM workspace.information_schema.columns
WHERE table_schema = 'market_data'
  AND table_name = 'bronze_yahoo_market_bars'
ORDER BY ordinal_position;
```

Unity Catalog's `information_schema` provides queryable metadata about catalogs, schemas, tables, columns, and other objects. Access to metadata is subject to the user's permissions.

## 6. Databricks Jobs

A Databricks job defines and executes a workload.

Jobs can contain one or more tasks, with dependencies between tasks when a workflow requires multiple processing steps.

Tasks can execute notebooks, Python code, SQL, and other supported workload types.

A job definition includes configuration such as:

- Tasks and their dependencies
- Execution environments
- Parameters
- Schedules and triggers
- Retry behavior
- Notifications

This project currently defines a job named `MDP - Yahoo Historical Bronze`.

The job executes `notebooks/02_bronze.py` in a Serverless environment with the application wheel installed.

The job can be deployed and executed through the Databricks CLI or managed through the workspace UI.

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

# Build and deploy resources
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

### 7.4 Scope of Bundle Management

Bundles manage the Databricks resources and project artifacts declared in their configuration.

They do not automatically manage every resource in the Databricks workspace or replace all cloud infrastructure provisioning.

For example, this project's Bronze Delta table was created separately through SQL and is not currently a bundle-managed resource.

Cloud infrastructure provisioning and Databricks project deployment are related but distinct responsibilities.

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

### 8.2 Local Development vs. Databricks Runtime

The project deliberately separates local development from Databricks execution.

| Local environment | Databricks environment |
|---|---|
| Python 3.12 | Managed Python runtime |
| uv dependency management | Job environment dependencies |
| pytest | Databricks job execution and integration validation |
| pandas transformations | Spark processing |
| Local Python package | Installed application wheel |
| Local development tools | Managed Serverless compute |

This allows domain logic to be developed and tested locally while using Databricks for platform-specific execution and storage.

## 9. Project Development Workflow

The current development workflow is:

1. Develop application code locally in VS Code.
2. Manage dependencies with uv.
3. Validate code with Ruff and pytest.
4. Build the Python wheel.
5. Validate the Databricks bundle.
6. Deploy the bundle to the development workspace.
7. Execute jobs in Databricks.
8. Inspect results through the workspace UI and SQL.
9. Update tests, documentation, and implementation decisions as needed.

The Makefile provides convenience commands for common operations without hiding the underlying tools.

## 10. References

- [Databricks Lakehouse Platform](https://docs.databricks.com/)
- [Declarative Automation Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles/)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [Delta Lake Documentation](https://docs.delta.io/)
- [Unity Catalog Documentation](https://docs.databricks.com/aws/en/data-governance/unity-catalog/)
