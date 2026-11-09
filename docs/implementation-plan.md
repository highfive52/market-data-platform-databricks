# Market Data Platform — Databricks Implementation Plan

## 1\. Project Overview

### Objective

Build an independently executable market data platform using Databricks, implementing the core functionality and architectural concepts of the existing Market Data Platform (MDP).

The project will serve two purposes:

1. Learn Databricks as a modern managed data engineering platform.
2. Explore how an existing multi-provider data platform can be implemented using Databricks-native capabilities.

The project will emphasize software engineering practices, data architecture, incremental processing, reliability, and platform operations rather than simply demonstrating individual Databricks features.

### Relationship to the Existing MDP

This project is a separate implementation, not an extension or dependency of the original MDP repository.

| Project | Architecture |
| --- | --- |
| market-data-platform | Custom-built platform using AWS, Kafka, Spark, and Delta Lake |
| market-data-platform-databricks | Managed lakehouse implementation using Databricks |

Both projects share the same domain requirements and conceptual architecture but maintain independent source code, infrastructure, configuration, and execution.

The goal is to compare architectural approaches, understand the benefits and limitations of managed services, and identify which responsibilities move from application code into the Databricks platform.

---

## 2\. Learning Objectives

The project will progressively introduce the following technologies and concepts.

| Area | Technologies / Concepts |
| --- | --- |
| Development environment | Databricks workspace, VS Code extension, Databricks CLI |
| Project deployment | Declarative Automation Bundles |
| Data contracts | Python, Pydantic, schema enforcement |
| Storage | Delta Lake, managed tables, transaction logs |
| Data architecture | Medallion architecture, Bronze / Silver / Gold |
| Processing | PySpark, Spark SQL, DataFrames |
| Data ingestion | Historical ingestion, Auto Loader |
| Streaming | Structured Streaming, checkpoints, incremental processing |
| Orchestration | Lakeflow Jobs, task dependencies, scheduling |
| Governance | Unity Catalog, permissions, lineage |
| Data quality | Validation, constraints, reconciliation, error handling |
| Development practices | Git, pytest, Ruff, modular Python |
| Operations | Monitoring, execution plans, performance optimization |

### Development Philosophy

- Git is the source of truth for application code and deployment configuration.
- Develop primarily in VS Code, using the Databricks workspace for execution and platform management.
- Keep business logic in reusable Python modules rather than embedding everything in notebooks.
- Use notebooks for exploration, demonstrations, and lightweight orchestration where appropriate.
- Define Databricks resources declaratively wherever supported.
- Build incrementally, validating each stage before introducing additional complexity.
- Prefer Databricks-native capabilities when they provide a meaningful advantage, while retaining external services when architecturally justified.

---

## 3\. Target Architecture

The platform will implement a multi-provider market data ingestion and analytics workflow.

### Logical Architecture

``` text
                 DATA PROVIDERS
                 /            \
             Finnhub          Yahoo
             Live Trades      Historical Bars
                 |                |
                 +-------+--------+
                         |
                  DATA INGESTION
                         |
                 BRONZE DELTA LAYER
                 Raw Provider Data
                         |
                 SILVER DELTA LAYER
                 Canonical Market Bars
                 Reconciliation / Quality
                         |
                  GOLD DELTA LAYER
                  Analytics / Aggregates
                         |
                 DATABRICKS SQL
                 Analytics / Reporting
```

The implementation will evolve through several stages.

Not every component needs to be introduced immediately. Initial development will use historical data and controlled inputs before adding live streaming ingestion.

### Data Layer Responsibilities

**Bronze**

- Preserve source observations.
- Retain provider identification and relevant source metadata.
- Support replay and reprocessing.
- Enforce appropriate schema and data-quality boundaries.
- Maintain ingestion lineage.

**Silver**

- Produce canonical market data.
- Normalize provider-specific representations.
- Reconcile overlapping historical and streaming observations.
- Enforce the canonical one-minute bar grain.
- Provide trusted, consistent data for downstream consumers.

**Gold**

- Produce analytics-oriented datasets.
- Aggregate market data across symbols and time intervals.
- Support analytical queries and reporting.
- Provide a clean interface for Databricks SQL.

### Core Domain Contracts

The initial implementation will retain the conceptual domain model from MDP.

`MarketTrade`

- symbol
- trade\_timestamp\_utc
- price
- quantity
- provider

`MarketBar`

- symbol
- bar\_timestamp\_utc
- interval
- open
- high
- low
- close
- volume
- provider

Provider-specific semantics must remain explicit. Individual trades and OHLCV bars are different observations and should not be treated as interchangeable records.

---

## 4\. Implementation Stages

### Stage 1 — Project Foundation and Databricks Environment

**Objective:** Establish the development environment and understand how Databricks projects are developed and deployed.

Tasks:

- Create the GitHub repository.
- Initialize the Python project.
- Configure `pyproject.toml`.
- Install and configure the Databricks CLI.
- Install the Databricks VS Code extension.
- Create a Databricks Free Edition workspace.
- Configure workspace authentication.
- Connect VS Code to Databricks.
- Initialize Declarative Automation Bundles.
- Establish the initial project structure.
- Create the initial README and architecture documentation.

Concepts to learn:

- Workspace versus local development.
- Databricks CLI.
- Workspace authentication and profiles.
- Declarative Automation Bundles.
- Deployment targets.
- Databricks workspace resources.

Deliverables:

- Independently executable project skeleton.
- Working local development environment.
- Successful connection to Databricks.
- Initial bundle validation and deployment.
- Documented development workflow.

Completion criteria:

The project can be cloned, configured, validated, and deployed to the Databricks workspace.

### Stage 2 — Delta Lake and Bronze Ingestion

**Objective:** Learn Delta Lake and implement the initial ingestion workflow.

Tasks:

- Explore Unity Catalog.
- Establish catalog and schema organization.
- Understand managed versus external tables.
- Load historical Yahoo market data.
- Implement bronze Delta tables.
- Preserve provider metadata and ingestion lineage.
- Explore schema enforcement and evolution.
- Examine transaction logs and table history.
- Implement basic data validation.

Concepts to learn:

- Delta Lake architecture.
- ACID transactions.
- Delta transaction logs.
- Managed tables.
- Schema enforcement.
- Schema evolution.
- Table history and time travel.
- Unity Catalog.

Deliverables:

- Working historical ingestion.
- Bronze Delta tables.
- Documented data contracts.
- Basic ingestion tests.
- SQL queries demonstrating bronze data.

Completion criteria:

Historical market data can be loaded repeatedly into durable Delta tables with appropriate lineage and validation.

### Stage 3 — Silver Transformations and Reconciliation

**Objective:** Implement the canonical market data layer using PySpark and Delta Lake.

Tasks:

- Implement provider-specific normalization.
- Validate canonical market data contracts.
- Transform historical OHLCV data into canonical market bars.
- Establish the silver table grain.
- Implement duplicate detection.
- Implement reconciliation using Delta MERGE.
- Address overlapping source observations.
- Handle invalid and late-arriving records.
- Implement data-quality checks.

Concepts to learn:

- PySpark DataFrames.
- Spark SQL.
- Lazy evaluation.
- Joins and aggregations.
- Delta MERGE.
- Idempotent processing.
- Data-quality expectations.
- Partitioning considerations.

Deliverables:

- Canonical silver market-bar table.
- Reconciliation implementation.
- Data-quality validation.
- Unit and integration tests.
- Documented reconciliation rules.

Completion criteria:

Historical data can be processed repeatedly without creating duplicate canonical records, and the resulting silver data conforms to the agreed business rules.

### Stage 4 — Gold Analytics and Databricks SQL

**Objective:** Build analytical data products and learn Databricks SQL.

Tasks:

- Define analytical use cases.
- Build gold market-data tables.
- Create multi-interval aggregates.
- Implement analytical queries.
- Explore SQL warehouses.
- Build sample dashboards.
- Examine query execution and performance.

Concepts to learn:

- Databricks SQL.
- SQL warehouses.
- Analytical data modeling.
- Aggregations and window functions.
- Query optimization.
- Execution plans.
- Data consumption and access patterns.

Deliverables:

- Gold analytical tables.
- SQL analysis scripts.
- Sample dashboard.
- Documented analytical use cases.

Completion criteria:

Gold datasets can support representative analytical queries without requiring consumers to understand provider-specific ingestion details.

### Stage 5 — Orchestration and Lakeflow Jobs

**Objective:** Convert the independent processing steps into an orchestrated data platform.

Tasks:

- Define ingestion, silver, and gold jobs.
- Configure task dependencies.
- Introduce job parameters.
- Configure scheduling.
- Implement retries and failure handling.
- Monitor job execution.
- Manage resources through Declarative Automation Bundles.

Concepts to learn:

- Lakeflow Jobs.
- Task dependencies.
- Job parameters.
- Scheduling.
- Retries and error handling.
- Deployment and configuration management.
- Databricks job monitoring.

Deliverables:

- Declaratively defined workflows.
- Deployable job configuration.
- End-to-end batch workflow.
- Execution and failure-handling documentation.

Completion criteria:

The complete historical ingestion and transformation process can execute through a managed Databricks workflow.

### Stage 6 — Incremental Ingestion

**Objective:** Move beyond full historical loads and implement incremental processing.

Tasks:

- Introduce incremental source data.
- Explore Auto Loader.
- Understand file discovery and schema handling.
- Implement incremental bronze ingestion.
- Track ingestion progress.
- Handle repeated input and recovery.
- Validate incremental processing against batch results.

Concepts to learn:

- Auto Loader.
- Incremental ingestion.
- Structured Streaming fundamentals.
- Checkpointing.
- Exactly-once processing considerations.
- Idempotency.
- Schema evolution.

Deliverables:

- Incremental ingestion workflow.
- Incremental bronze tables.
- Checkpoint configuration.
- Recovery and replay tests.

Completion criteria:

New market data can be ingested incrementally without requiring complete historical reloads.

### Stage 7 — Streaming Market Data

**Objective:** Extend the platform to support live market data.

Tasks:

- Introduce Finnhub live trade ingestion.
- Evaluate external connectivity limitations.
- Implement streaming ingestion.
- Process incoming trade observations.
- Persist streaming data into bronze Delta tables.
- Reconcile streaming observations with historical data.
- Handle late-arriving and duplicate observations.
- Evaluate checkpoint recovery and replay.

Concepts to learn:

- Spark Structured Streaming.
- Streaming DataFrames.
- Checkpoint management.
- Micro-batch execution.
- Watermarks.
- Late-arriving data.
- Streaming-to-Delta writes.
- Fault tolerance.

Deliverables:

- Working streaming ingestion path.
- Streaming bronze persistence.
- Historical and streaming reconciliation.
- Documented recovery behavior.

Completion criteria:

The platform can process live market observations and incorporate them into the canonical silver data layer.

### Stage 8 — Platform Engineering and Optimization

**Objective:** Understand how the platform is operated, governed, tested, and optimized.

Tasks:

- Review Unity Catalog permissions and lineage.
- Improve data-quality monitoring.
- Add failure notifications where supported.
- Review job and pipeline execution metrics.
- Evaluate table maintenance.
- Explore OPTIMIZE and other applicable Delta maintenance features.
- Examine partitioning and file sizes.
- Profile Spark execution.
- Introduce CI/CD practices.
- Document operational procedures.

Concepts to learn:

- Data governance.
- Lineage.
- Monitoring and observability.
- Delta maintenance.
- Performance optimization.
- CI/CD.
- Deployment environments.
- Production reliability.

Deliverables:

- Operational documentation.
- Performance analysis.
- Improved testing and validation.
- Deployment workflow.
- Final architecture documentation.

Completion criteria:

The project demonstrates the engineering and operational practices needed to maintain a managed Databricks data platform.

---

## 5\. Repository Structure

The repository will evolve as implementation progresses.

``` text
market-data-platform-databricks/
│
├── databricks.yml
│
├── resources/
│   ├── jobs.yml
│   └── pipelines.yml
│
├── src/
│   ├── contracts/
│   │   ├── market_trade.py
│   │   └── market_bar.py
│   │
│   ├── ingestion/
│   │   ├── historical.py
│   │   └── streaming.py
│   │
│   ├── bronze/
│   │   └── market_data.py
│   │
│   ├── silver/
│   │   ├── reconciliation.py
│   │   └── market_bars.py
│   │
│   ├── gold/
│   │   └── analytics.py
│   │
│   └── common/
│
├── notebooks/
│   ├── 01_exploration.py
│   ├── 02_bronze.py
│   ├── 03_silver.py
│   └── 04_gold.py
│
├── sql/
│   ├── analysis/
│   └── validation/
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── docs/
│   ├── architecture.md
│   ├── databricks-concepts.md
│   └── mdp-comparison.md
│
├── pyproject.toml
└── README.md
```

The structure is an initial target, not a requirement to create every file immediately. Additional directories and files will be introduced when justified by implementation needs.

---

## 6\. Architectural Decisions and Constraints

The following principles will guide implementation.

### Independent implementation

The Databricks project must not import code or require infrastructure from the original MDP repository.

Domain concepts can be reused, but implementation must be independent.

### Databricks-native first

Prefer managed Databricks capabilities when appropriate:

- Delta Lake for analytical storage.
- PySpark for distributed transformations.
- Unity Catalog for governance.
- Lakeflow Jobs for orchestration.
- Auto Loader for supported incremental file ingestion.
- Structured Streaming for streaming workloads.

External infrastructure will be introduced when it provides a meaningful architectural benefit.

### Separate ingestion from transformation

Provider-specific ingestion and normalization should remain separate from canonical transformations.

Provider changes should not require rewriting the entire data platform.

### Explicit data semantics

Maintain clear distinctions between:

- Trades and OHLCV bars.
- Provider observations and canonical records.
- Event timestamps and ingestion timestamps.
- Bronze source observations and trusted silver records.

Canonical timestamps will use the `_utc` suffix.

### Reliability and replayability

Design processing to be repeatable, recoverable, and idempotent where appropriate.

Do not assume that a platform feature automatically guarantees end-to-end exactly-once processing.

### Free Edition constraints

Initially target Databricks Free Edition.

Avoid dependencies on unavailable features, custom clusters, unrestricted networking, or infrastructure that requires a paid cloud deployment.

Where a feature is unavailable, document the limitation and use a reasonable alternative without misrepresenting it as equivalent functionality.

---

## 7\. Documentation and Learning Deliverables

Documentation is part of the implementation, not something postponed until the end.

Each stage should produce:

1. Working implementation.
2. Relevant tests.
3. Databricks concept explanations.
4. Architecture decisions.
5. Comparison with the original MDP.
6. Updated project README.

The `docs/databricks-concepts.md` document should become a running technical reference.

The `docs/mdp-comparison.md` document should capture differences in architecture, implementation, operational responsibilities, and tradeoffs.

Potential future blog topics include:

- Building a Data Engineering Project with Databricks Free Edition.
- Delta Lake Versus Traditional Parquet Storage.
- Implementing Medallion Architecture with Databricks.
- Reconciliation and Idempotency with Delta MERGE.
- Lakeflow Versus Airflow.
- Managed Spark Versus Self-Managed Spark.
- Data Contracts and Schema Governance.

---

## 8\. Definition of Project Completion

The project will be considered complete when it demonstrates:

- Independent repository and development environment.
- Reproducible Databricks deployment.
- Historical data ingestion.
- Bronze, Silver, and Gold Delta tables.
- Canonical market-data contracts.
- Reliable reconciliation.
- Incremental ingestion.
- Streaming processing, subject to available platform capabilities.
- Managed orchestration.
- SQL analytics.
- Data-quality validation.
- Governance and lineage exploration.
- Documented operational and performance considerations.

The final outcome should be an independently understandable implementation that demonstrates not only familiarity with Databricks features, but an understanding of how those features fit together to create and operate a modern data platform.

---

## 9\. Development Workflow

Use the following process for each implementation stage:

1. Review the overall project plan and identify the current stage.
2. Identify the Databricks concepts being introduced.
3. Review relevant official documentation.
4. Make any necessary architectural decisions.
5. Implement the functionality in small, testable increments.
6. Validate locally and in the Databricks workspace as appropriate.
7. Document the implementation and decisions.
8. Update the project plan with completed work and any changes.
9. Identify the next logical learning objective.

**Guiding principle:** Build a working data platform while learning Databricks, rather than completing isolated Databricks tutorials and attempting to assemble them into a project afterward.
