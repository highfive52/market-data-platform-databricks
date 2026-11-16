# Market Data Platform — Databricks Implementation Plan

## 1. Project Overview

### Objective

Build an independently executable market data platform using Databricks, implementing the core functionality and architectural concepts of the existing Market Data Platform (MDP).

The project has four objectives:

1. Learn Databricks as a modern managed data engineering platform.
2. Explore how an existing multi-provider data platform can be implemented using Databricks-native capabilities and industry-standard complementary tools.
3. Understand how managed services change the responsibilities of a data engineering application and its supporting platform.
4. Build a reproducible, independently demonstrable data platform that can serve as a professional portfolio example.

The primary objective is practical Databricks competence: the ability to design, implement, deploy, troubleshoot, and explain a functioning MVP in a Databricks environment.

The project will emphasize data architecture, ingestion, transformation, reliability, governance, orchestration, reproducibility, and operational practices.

It will favor established Databricks capabilities over custom implementations of functionality already provided by the platform.

### Relationship to the Existing MDP

This project is a separate implementation, not an extension or dependency of the original MDP repository.

| Project | Architecture |
| --- | --- |
| `market-data-platform` | Custom-built platform using AWS, Kafka, Spark, and Delta Lake |
| `market-data-platform-databricks` | Managed lakehouse implementation using Databricks |

Both projects share the same domain requirements and conceptual architecture but maintain independent source code, infrastructure, configuration, and execution.

The goal is to compare architectural approaches, understand the benefits and limitations of managed services, and identify which responsibilities move from application code into the Databricks platform.

### Reproducibility and Rebuild Objective

Git should be the source of truth for application code, deployment configuration, pipeline definitions, transformation models, and other deployable resources.

The Databricks workspace should be treated as a deployable environment rather than the only place where the platform's configuration and definitions exist.

The intended outcome is that a replacement workspace can be provisioned and reconstructed from the repository without depending on manually created pipeline definitions, workspace configuration, or undocumented database changes.

The target rebuild sequence is:

1. **Create the workspace:** Establish Databricks, Unity Catalog access, required permissions, SQL Warehouse access, and authentication.
2. **Deploy the bundle:** Run `databricks bundle deploy -t dev` to deploy supported workspace resources, pipeline definitions, jobs, and declared catalog/schema resources.
3. **Materialize pipeline-managed objects:** Run the deployed Lakeflow pipelines to create or update their managed tables and views.
4. **Deploy and execute analytical models:** Make the dbt project available and execute its models to reconstruct Gold analytical objects.
5. **Run ingestion:** Execute historical ingestion to repopulate the platform from market-data providers or retained source data.
6. **Rebuild derived data:** Execute Silver and Gold processing to reconstruct downstream datasets.

The exact sequencing will be refined as the deployment architecture is implemented.

**Important distinction:** Recreating workspace resources and table definitions does not restore deleted data. Market data must be re-ingested or restored from independent backups if preservation is required. Pipeline checkpoints and streaming state also require separate consideration.

---

## 2. Learning Objectives

The project will progressively introduce the following technologies and concepts.

| Area | Technologies / Concepts |
| --- | --- |
| Development environment | Databricks workspace, VS Code extension, Databricks CLI |
| Project deployment | Declarative Automation Bundles |
| Data governance | Unity Catalog, permissions, lineage |
| Storage | Delta Lake, managed tables, transaction logs |
| Data architecture | Medallion architecture, Bronze / Silver / Gold |
| Data ingestion | Python provider integrations, Auto Loader |
| Managed processing | Lakeflow Spark Declarative Pipelines |
| Processing | PySpark, Spark SQL, DataFrames |
| Streaming | Structured Streaming, checkpoints, incremental processing |
| Transformation management | dbt, SQL models, dependencies, testing, documentation |
| Orchestration | Lakeflow Jobs, task dependencies, scheduling |
| Data contracts | Python, Pydantic, schema enforcement |
| Data quality | Pipeline expectations, dbt tests, validation, reconciliation |
| Development practices | Git, pytest, Ruff, modular Python |
| Operations | Monitoring, execution plans, performance optimization |
| Reproducibility | Declarative deployment, pipeline reconstruction, data recovery boundaries |
| CI/CD | GitHub Actions, bundle validation, deployment workflows |

### Development Philosophy

- Git is the source of truth for application code, deployment configuration, and transformation definitions.
- Learn and use Databricks-native capabilities where they are the established approach.
- Use industry-standard complementary tools when they provide a meaningful capability that Databricks does not adequately provide.
- Keep business logic in reusable Python modules where appropriate rather than embedding everything in notebooks.
- Use Lakeflow Spark Declarative Pipelines for managed data transformations and pipeline-managed table lifecycles.
- Use Auto Loader for supported incremental file ingestion rather than building custom file-discovery and checkpoint mechanisms.
- Use dbt for analytical SQL models, testing, documentation, and dependencies in the Gold layer.
- Use Lakeflow Jobs for workflow orchestration.
- Use Declarative Automation Bundles to deploy supported Databricks resources.
- Avoid building custom infrastructure or frameworks when an appropriate managed capability already exists.
- Avoid introducing multiple tools that compete to manage the same resource or responsibility.
- Keep implementation focused on delivering a functioning data platform rather than building infrastructure for hypothetical future requirements.
- Document platform limitations and distinguish managed-service capabilities from application-level responsibilities.

### Technology Selection Principle

Technology choices should be based on the problem being solved, not simply on familiarity with a programming language.

The preferred order is:

1. Databricks-native capabilities where appropriate.
2. Established industry-standard complementary tools where they provide meaningful value.
3. Custom Python implementations where application-specific logic or external integrations require them.

Python remains an important part of the project, but it should not automatically become the solution to every platform problem.

---

## 3. Target Architecture

The platform will implement a multi-provider market data ingestion and analytics workflow.

### Logical Data Architecture

```text
                    DATA PROVIDERS
                    /             \
                Finnhub           Yahoo
              Live Trades      Historical Bars
                    |               |
                    +-------+-------+
                            |
                  PYTHON PROVIDER
                    INTEGRATIONS
                            |
                 SOURCE DATA LANDING
                  Where appropriate
                            |
                 AUTO LOADER / FILE
                    INGESTION
                            |
                   BRONZE DELTA
                  Source Observations
                            |
               LAKEFLOW DECLARATIVE
                     PIPELINES
                            |
                    SILVER DELTA
                 Canonical Market Bars
                Reconciliation / Quality
                            |
                       dbt MODELS
                            |
                     GOLD DELTA
                Analytics / Aggregates
                            |
                   DATABRICKS SQL
                  Analytics / Reporting
```

This is the target logical architecture. The precise ingestion path will depend on the source and the capabilities available in the Free Edition environment.

Auto Loader is intended for files arriving in supported cloud storage locations. It is not a general-purpose REST API ingestion tool.

Python provider integrations remain appropriate for calling external market-data APIs. Their output can be delivered to an appropriate landing location or written through a supported ingestion path. The implementation will establish the best approach based on the actual Databricks environment.

### Platform and Deployment Architecture

```text
                       GIT REPOSITORY
                              |
             +----------------+----------------+
             |                |                |
        Python Source    Bundle Config     dbt Project
             |                |                |
             |          DATABRICKS CLI    dbt CLI / Job
             |                |                |
             +----------------+----------------+
                              |
                     DATABRICKS WORKSPACE
                              |
          +-------------------+-------------------+
          |                   |                   |
    UNITY CATALOG        LAKEFLOW             DATABRICKS
    Governance           Pipelines            SQL
    Catalogs             Jobs                 Warehouse
    Schemas              Transformations
          |                   |
          +-------------------+
                              |
                       DELTA LAKE
                              |
                     BRONZE / SILVER
                              |
                         dbt GOLD
```

### Platform Responsibilities

| Component | Responsibility |
| --- | --- |
| Git | Version-controlled source of truth |
| Declarative Automation Bundles | Deploy supported Databricks workspace resources, jobs, pipelines, and catalog/schema resources |
| Unity Catalog | Data organization, governance, access control, and lineage |
| Delta Lake | Transactional data storage and table management |
| Auto Loader | Incremental ingestion of supported files from cloud storage |
| Lakeflow Spark Declarative Pipelines | Managed declarative transformations, dependencies, data quality, and pipeline-managed table lifecycle |
| Python application | External provider integrations, data contracts, and specialized application logic |
| dbt | Analytical SQL models, dependencies, tests, and documentation |
| Lakeflow Jobs | Orchestration and scheduling of platform workflows |
| Databricks SQL | Analytical query and reporting interface |
| GitHub Actions | Local/CI validation and deployment workflow integration |
| Market-data providers | Supply source observations used to populate the platform |

These tools have distinct responsibilities. Pipeline-managed tables should not also be independently managed through a separate migration framework. Similarly, dbt should own the analytical models it manages rather than competing with Lakeflow for the same table definitions.

### Data Layer Responsibilities

**Bronze**

- Preserve source observations.
- Retain provider identification and relevant source metadata.
- Support replay and reprocessing where the source data is retained.
- Apply appropriate schema enforcement and controlled schema evolution.
- Maintain ingestion lineage.
- Use Delta Lake tables managed through the selected ingestion and pipeline approach.

**Silver**

- Produce canonical market data.
- Normalize provider-specific representations.
- Reconcile overlapping historical and streaming observations.
- Enforce the canonical one-minute bar grain.
- Detect duplicates and invalid observations.
- Provide trusted, consistent data for downstream consumers.
- Use Lakeflow for managed transformations and data-quality expectations.

**Gold**

- Produce analytics-oriented datasets.
- Aggregate market data across symbols and time intervals.
- Support analytical queries and reporting.
- Provide a clean interface for Databricks SQL.
- Use dbt for SQL-based analytical models, dependencies, tests, and documentation.

### Core Domain Contracts

The initial implementation will retain the conceptual domain model from MDP.

`MarketTrade`

- symbol
- trade_timestamp_utc
- price
- quantity
- provider

`MarketBar`

- symbol
- bar_timestamp_utc
- interval
- open
- high
- low
- close
- volume
- provider

Provider-specific semantics must remain explicit. Individual trades and OHLCV bars are different observations and should not be treated as interchangeable records.

---

## 4. Implementation Stages

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
- Establish local testing, linting, formatting, and CI workflows.

Concepts to learn:

- Workspace versus local development.
- Databricks CLI.
- Workspace authentication and profiles.
- Declarative Automation Bundles.
- Deployment targets.
- Databricks workspace resources.
- Local Python packaging and development workflows.

Deliverables:

- Independently executable project skeleton.
- Working local development environment.
- Successful connection to Databricks.
- Initial bundle validation and deployment.
- Documented development workflow.

Completion criteria:

The project can be cloned, configured, validated, and deployed to the Databricks workspace.

### Stage 2 — Lakehouse Foundation and Lakeflow Proof of Concept

**Objective:** Establish the Databricks-native approach to managing tables, ingestion, transformations, and deployment before expanding the platform.

This stage replaces the previous standalone database migration evaluation.

Tasks:

- Review the existing bundle configuration.
- Review Unity Catalog catalogs, schemas, permissions, and resource organization.
- Identify the pipeline-managed objects and workspace resources that should be defined in Git.
- Review Lakeflow Spark Declarative Pipelines and current Databricks development conventions.
- Build a small Lakeflow pipeline using controlled market-data files.
- Use Auto Loader for supported file ingestion.
- Define a Bronze streaming table.
- Verify table creation and pipeline execution.
- Introduce a new source column and observe schema evolution.
- Test an incompatible schema change and examine the failure and recovery behavior.
- Deploy the pipeline definition through Declarative Automation Bundles.
- Run the pipeline after deployment.
- Verify that the required pipeline-managed objects are created or updated.
- Document the ownership boundaries between Bundles, Lakeflow, Unity Catalog, and Delta Lake.

Concepts to learn:

- Unity Catalog.
- Delta Lake.
- Managed tables and pipeline-managed tables.
- Lakeflow Spark Declarative Pipelines.
- Streaming tables and materialized views.
- Auto Loader.
- Schema inference and schema evolution.
- Pipeline expectations.
- Pipeline deployment and execution.
- Workspace resources versus data objects.

Deliverables:

- Working Lakeflow proof of concept.
- Version-controlled pipeline source.
- Declarative bundle configuration.
- Bronze table created and populated through pipeline execution.
- Schema evolution demonstration.
- Documented deployment and reconstruction workflow.
- Updated architecture decisions.

Completion criteria:

A pipeline can be deployed from Git and executed to create or update its managed data objects. Its behavior under supported schema evolution and incompatible changes is understood and documented.

**Migration strategy:** The existing custom migration runner and SQL migrations are retained only as legacy implementation artifacts during this transition. They are not part of the target architecture for pipeline-managed tables. Once the relevant objects are owned by Lakeflow or another selected native mechanism, remove the custom runner, obsolete migration files, and associated unit tests.

Do not introduce Liquibase or Alembic as a replacement. If a genuine requirement for independently managed DDL emerges, document and evaluate it separately rather than assuming another migration framework is necessary.

### Stage 3 — Bronze Ingestion and Historical Market Data

**Objective:** Implement the actual market-data ingestion workflow and establish the Bronze layer using appropriate Databricks capabilities.

Tasks:

- Review the existing provider contracts and historical ingestion implementation.
- Establish the source-data landing approach.
- Implement or adapt the Yahoo historical market-data provider integration.
- Determine whether the API output should be landed as files or written through another supported ingestion path.
- Use Auto Loader for supported file-based ingestion.
- Define Bronze streaming tables or other appropriate pipeline-managed tables.
- Preserve provider metadata and ingestion lineage.
- Explore schema enforcement and controlled schema evolution.
- Examine Delta transaction logs and table history.
- Implement ingestion validation.
- Validate repeatability and replay behavior.

Concepts to learn:

- Delta Lake architecture.
- ACID transactions.
- Delta transaction logs.
- Managed tables.
- Auto Loader.
- Schema enforcement.
- Schema evolution.
- Table history and time travel.
- Unity Catalog.
- Source-data landing and ingestion patterns.
- Data contracts versus source schema inference.

Deliverables:

- Working historical ingestion.
- Bronze Delta tables.
- Version-controlled pipeline definitions.
- Documented data contracts.
- Basic ingestion tests.
- SQL queries demonstrating Bronze data.
- Documented source-data handling.

Completion criteria:

Historical market data can be loaded repeatedly into durable Delta tables with appropriate lineage and validation. Pipeline-managed objects can be recreated from the repository and repopulated independently of their original data.

### Stage 4 — Silver Transformations and Reconciliation

**Objective:** Implement the canonical market data layer using Lakeflow, PySpark, Spark SQL, and Delta Lake.

Tasks:

- Implement provider-specific normalization.
- Validate canonical market data contracts.
- Transform historical OHLCV data into canonical market bars.
- Establish the Silver table grain.
- Implement duplicate detection.
- Implement reconciliation using Delta MERGE where appropriate.
- Address overlapping source observations.
- Handle invalid and late-arriving records.
- Implement data-quality expectations.
- Evaluate pipeline dependencies and incremental processing.
- Compare declarative pipeline transformations with the original MDP processing approach.

Concepts to learn:

- PySpark DataFrames.
- Spark SQL.
- Lazy evaluation.
- Joins and aggregations.
- Delta MERGE.
- Idempotent processing.
- Lakeflow expectations.
- Pipeline dependencies.
- Incremental processing.
- Partitioning considerations.
- Data-quality enforcement.

Deliverables:

- Canonical Silver market-bar table.
- Reconciliation implementation.
- Data-quality validation.
- Unit and integration tests.
- Documented reconciliation rules.
- Demonstration of repeatable processing.

Completion criteria:

Historical data can be processed repeatedly without creating duplicate canonical records, and the resulting Silver data conforms to the agreed business rules.

### Stage 5 — Gold Analytics and dbt

**Objective:** Build analytical data products using dbt and Databricks SQL.

Tasks:

- Define representative analytical use cases.
- Establish the dbt project and Databricks adapter.
- Configure dbt connectivity to Databricks.
- Build Gold market-data models.
- Create multi-interval aggregates.
- Implement analytical SQL models.
- Define model dependencies.
- Implement dbt tests.
- Generate model documentation.
- Examine lineage and materialization strategies.
- Explore SQL Warehouses.
- Build sample dashboards.
- Examine query execution and performance.

Concepts to learn:

- dbt project structure.
- dbt models and materializations.
- Model dependencies.
- Incremental models.
- Tests and assertions.
- Documentation and lineage.
- Databricks SQL.
- SQL Warehouses.
- Analytical data modeling.
- Aggregations and window functions.
- Query optimization and execution plans.

Deliverables:

- dbt project.
- Gold analytical models.
- dbt tests and documentation.
- SQL analysis scripts.
- Sample dashboard.
- Documented analytical use cases and dependencies.

Completion criteria:

Gold datasets can support representative analytical queries without requiring consumers to understand provider-specific ingestion details.

dbt should be used for meaningful analytical transformations rather than introduced merely to add another technology to the stack.

### Stage 6 — Orchestration and Lakeflow Jobs

**Objective:** Convert the independent processing steps into an orchestrated data platform.

Tasks:

- Define ingestion, Lakeflow pipeline, and dbt execution tasks.
- Configure task dependencies.
- Introduce job parameters.
- Configure scheduling.
- Implement retries and failure handling.
- Monitor job execution.
- Manage job resources through Declarative Automation Bundles.
- Establish appropriate separation between deployment and workflow execution.
- Test the end-to-end historical ingestion and transformation process.

Concepts to learn:

- Lakeflow Jobs.
- Task dependencies.
- Job parameters.
- Scheduling.
- Retries and error handling.
- Job monitoring.
- Pipeline orchestration.
- dbt execution within a managed workflow.
- Deployment and configuration management.

Deliverables:

- Declaratively defined workflows.
- Deployable job configuration.
- End-to-end batch workflow.
- Execution and failure-handling documentation.

Completion criteria:

The complete historical ingestion and transformation process can execute through a managed Databricks workflow.

### Stage 7 — Incremental Ingestion and Schema Evolution

**Objective:** Move beyond full historical loads and implement incremental processing.

Tasks:

- Introduce incremental source data.
- Explore Auto Loader in greater depth.
- Understand file discovery and schema handling.
- Implement incremental Bronze ingestion.
- Track ingestion progress.
- Handle repeated input and recovery.
- Test schema additions.
- Test incompatible schema changes.
- Validate incremental processing against batch results.
- Document checkpoint and recovery behavior.

Concepts to learn:

- Auto Loader.
- Incremental ingestion.
- Structured Streaming fundamentals.
- Checkpointing.
- Exactly-once processing considerations.
- Idempotency.
- Schema evolution.
- Recovery and replay.

Deliverables:

- Incremental ingestion workflow.
- Incremental Bronze tables.
- Checkpoint configuration.
- Recovery and replay tests.
- Documented schema evolution behavior.

Completion criteria:

New market data can be ingested incrementally without requiring complete historical reloads.

### Stage 8 — Streaming Market Data

**Objective:** Extend the platform to support live market data.

Tasks:

- Introduce Finnhub live trade ingestion.
- Evaluate external connectivity limitations.
- Implement streaming ingestion using an appropriate supported approach.
- Process incoming trade observations.
- Persist streaming data into Bronze Delta tables.
- Reconcile streaming observations with historical data.
- Handle late-arriving and duplicate observations.
- Evaluate checkpoint recovery and replay.
- Integrate streaming processing into the managed workflow where supported.

Concepts to learn:

- Spark Structured Streaming.
- Streaming DataFrames.
- Checkpoint management.
- Micro-batch execution.
- Watermarks.
- Late-arriving data.
- Streaming-to-Delta writes.
- Fault tolerance.
- Historical and streaming reconciliation.

Deliverables:

- Working streaming ingestion path, subject to Free Edition capabilities.
- Streaming Bronze persistence.
- Historical and streaming reconciliation.
- Documented recovery behavior.

Completion criteria:

The platform can process live market observations and incorporate them into the canonical Silver data layer, or document a clearly defined alternative if Free Edition prevents the required external connectivity or execution model.

### Stage 9 — Platform Engineering, Operations, and Portfolio Readiness

**Objective:** Understand how the platform is operated, governed, tested, optimized, and demonstrated.

Tasks:

- Review Unity Catalog permissions and lineage.
- Improve data-quality monitoring.
- Add failure notifications where supported.
- Review job and pipeline execution metrics.
- Evaluate table maintenance.
- Explore OPTIMIZE and other applicable Delta maintenance features.
- Examine partitioning and file sizes.
- Profile Spark execution.
- Refine CI/CD practices.
- Validate deployment into a clean environment.
- Document operational procedures and rebuild steps.
- Produce architecture diagrams and a portfolio demonstration.
- Document Free Edition limitations and the differences from production deployments.
- Prepare to explain architectural decisions and trade-offs in technical interviews.

Concepts to learn:

- Data governance.
- Lineage.
- Monitoring and observability.
- Delta maintenance.
- Performance optimization.
- CI/CD.
- Deployment environments.
- Production reliability.
- Environment reconstruction.
- Disaster recovery boundaries.
- Operational trade-offs.

Deliverables:

- Operational documentation.
- Performance analysis.
- Improved testing and validation.
- Deployment workflow.
- Rebuild runbook.
- Final architecture documentation.
- Portfolio-ready README and demonstration.
- Documented comparison with the original MDP.

Completion criteria:

The project demonstrates the engineering and operational practices needed to build and maintain a managed Databricks data platform, including the ability to reconstruct supported resources from Git and explain how the system works.

---

## 5. Repository Structure

The repository will evolve as implementation progresses.

The following represents the intended direction, incorporating the existing package structure and the selected Databricks architecture.

```text
market-data-platform-databricks/
│
├── databricks.yml
│
├── resources/
│   ├── jobs.yml
│   └── pipelines.yml
│
├── src/
│   └── market_data_platform/
│       ├── contracts/
│       │   ├── market_trade.py
│       │   └── market_bar.py
│       │
│       ├── ingestion/
│       │   ├── historical.py
│       │   └── streaming.py
│       │
│       ├── common/
│       │
│       └── providers/
│           ├── yahoo.py
│           └── finnhub.py
│
├── pipelines/
│   ├── bronze.py
│   └── silver.py
│
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml.example
│   ├── models/
│   │   ├── staging/
│   │   └── marts/
│   ├── tests/
│   └── README.md
│
├── notebooks/
│   └── 01_exploration.py
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
│   ├── implementation-plan.md
│   ├── implementation-plan-results.md
│   ├── mdp-comparison.md
│   └── setup-runbook.md
│
├── pyproject.toml
├── uv.lock
└── README.md
```

The structure is an evolving design, not a requirement to create every file immediately.

Additional directories and files will be introduced when justified by implementation needs.

Specific deployment and source layouts will follow the requirements of the selected Databricks resources and dbt integration.

The following are deliberately not part of the target structure:

- A custom database migration framework.
- A Liquibase project.
- An Alembic project.
- A separate SQL migration runner for pipeline-managed tables.

If an independently managed database object later requires a different lifecycle, its ownership and deployment mechanism will be evaluated explicitly.

---

## 6. Architectural Decisions and Constraints

### Independent Implementation

The Databricks project must not import code or require infrastructure from the original MDP repository.

Domain concepts can be reused, but implementation must be independent.

### Git as the Source of Truth

Git should contain:

- Python application code.
- Databricks bundle configuration.
- Lakeflow pipeline definitions.
- Job and deployment configuration.
- dbt models and project configuration.
- Tests and validation logic.
- Documentation and operational runbooks.

The Databricks workspace should not be the only location where the definitions needed to reconstruct the platform exist.

Secrets, tokens, and environment-specific credentials must not be committed to Git.

### Databricks-Native Resource and Table Management

Use the appropriate Databricks capability for each resource:

- **Declarative Automation Bundles:** Supported workspace resources, jobs, pipelines, notebooks, and catalog/schema resources.
- **Lakeflow Spark Declarative Pipelines:** Pipeline-managed transformations and associated streaming tables and materialized views.
- **Auto Loader:** Supported incremental file ingestion and schema evolution.
- **Unity Catalog:** Catalog and schema organization, governance, permissions, and lineage.
- **Delta Lake:** Table storage, transactions, and history.
- **Lakeflow Jobs:** Workflow execution and orchestration.
- **dbt:** Analytical models and the objects managed by those models.

Do not introduce a separate migration framework to manage objects whose lifecycle is already owned by a selected Databricks capability.

Do not have multiple tools independently modify the same table.

### Separate Deployment from Execution

Deployment and data processing are related but distinct.

The general process is:

1. Define resources and application code in Git.
2. Validate the bundle.
3. Deploy supported resources.
4. Execute pipelines and jobs.
5. Verify the resulting data objects and processing outcomes.

Deploying a pipeline does not mean its data has been processed. Pipeline execution materializes or updates its managed outputs.

Similarly, dbt model definitions must be executed to create or update their resulting analytical objects.

### Python Application Responsibilities

Python remains appropriate for:

- External market-data provider integrations.
- Provider-specific API handling.
- Reusable application logic.
- Domain contracts.
- Specialized validation.
- Logic that is not appropriately expressed through native managed capabilities.

Do not build custom Python replacements for file ingestion, workflow orchestration, or pipeline lifecycle management when Databricks provides an appropriate managed service.

### Data Contracts and Schema Evolution

Maintain explicit domain semantics and appropriate data-quality boundaries.

Auto Loader schema inference and evolution should not be treated as a substitute for business-level data contracts.

A newly observed source column may represent legitimate schema evolution. An incompatible type change or unexpected provider response may represent a data-quality problem.

The implementation must distinguish these cases and document how they are handled.

### Separate Ingestion from Transformation

Provider-specific ingestion and normalization should remain separate from canonical transformations.

Provider changes should not require rewriting the entire data platform.

### Explicit Data Semantics

Maintain clear distinctions between:

- Trades and OHLCV bars.
- Provider observations and canonical records.
- Event timestamps and ingestion timestamps.
- Bronze source observations and trusted Silver records.

Canonical timestamps will use the `_utc` suffix.

### Reliability and Replayability

Design processing to be repeatable, recoverable, and idempotent where appropriate.

Understand the responsibilities of pipeline checkpoints, streaming state, source retention, and Delta transactions.

Do not assume that a platform feature automatically guarantees end-to-end exactly-once processing.

### Data Versus Definitions

The ability to recreate a table does not imply the ability to restore its records.

The project will distinguish:

- Recreating infrastructure and workspace resources.
- Recreating pipeline-managed database objects.
- Recreating dbt-managed analytical objects.
- Re-ingesting source data.
- Rebuilding derived datasets.
- Recovering checkpoints and streaming state.

Historical market data will initially be treated as reproducible from its providers, subject to their availability and retention policies. Any future requirement for durable data backups should be addressed separately.

### Free Edition Constraints

Initially target Databricks Free Edition.

Avoid dependencies on unavailable features, custom clusters, unrestricted networking, or infrastructure that requires a paid cloud deployment.

Where a feature is unavailable, document the limitation and use a reasonable alternative without misrepresenting it as equivalent functionality.

The Free Edition implementation should be understood as a learning and portfolio environment, not evidence of operating a production-scale enterprise deployment.

---

## 7. Documentation and Learning Deliverables

Documentation is part of the implementation, not something postponed until the end.

Each stage should produce:

1. Working implementation.
2. Relevant tests.
3. Databricks concept explanations.
4. Architecture decisions.
5. Comparison with the original MDP.
6. Updated project README.
7. Operational or deployment documentation where appropriate.

The `docs/databricks-concepts.md` document should become a running technical reference.

The `docs/mdp-comparison.md` document should capture differences in architecture, implementation, operational responsibilities, and trade-offs.

The `docs/architecture.md` document should explain the overall system, including deployment, ingestion, transformation, governance, and orchestration responsibilities.

The `docs/setup-runbook.md` document should explain how to configure the local development environment and connect to Databricks.

The `docs/implementation-plan.md` document should describe the target architecture, implementation stages, and architectural decisions.

The `docs/implementation-plan-results.md` document should record what has actually been implemented, tested, deployed, and verified, along with outstanding work.

Potential future blog topics include:

- Building a Data Engineering Project with Databricks Free Edition.
- Reconstructing a Databricks Environment from Git.
- Declarative Automation Bundles and Reproducible Deployment.
- Delta Lake Versus Traditional Parquet Storage.
- Implementing Medallion Architecture with Databricks.
- Auto Loader and Schema Evolution.
- Lakeflow Spark Declarative Pipelines Versus Procedural Spark.
- Reconciliation and Idempotency with Delta MERGE.
- dbt and Databricks for Analytics Engineering.
- Lakeflow Jobs and Managed Workflow Orchestration.
- Managed Spark Versus Self-Managed Spark.
- Data Contracts and Schema Governance.

---

## 8. Definition of Project Completion

The project will be considered complete when it demonstrates:

- Independent repository and development environment.
- Reproducible Databricks deployment.
- Unity Catalog organization and governance exploration.
- Lakeflow-managed Bronze and Silver processing.
- Appropriate use of Auto Loader.
- Historical data ingestion.
- Bronze, Silver, and Gold Delta tables.
- Canonical market-data contracts.
- Reliable reconciliation.
- Incremental ingestion.
- Streaming processing, subject to available platform capabilities.
- dbt analytical models, tests, and documentation.
- Managed orchestration.
- SQL analytics.
- Data-quality validation.
- Governance and lineage exploration.
- Documented operational and performance considerations.
- A demonstrated rebuild procedure for supported infrastructure and database objects.
- A public portfolio repository that explains the architecture and implementation.
- The ability to explain and defend the technology choices and architectural trade-offs.

The final outcome should be an independently understandable implementation that demonstrates not only familiarity with Databricks features, but an understanding of how those features fit together to create, deploy, reconstruct, and operate a modern data platform.

The project should provide enough hands-on experience to confidently assess and contribute to an MVP Databricks implementation in a professional environment.

---

## 9. Development Workflow

Use the following process for each implementation stage:

1. Review the overall project plan and identify the current stage.
2. Identify the Databricks concepts being introduced.
3. Review relevant official documentation and established industry practices.
4. Make necessary architectural decisions before introducing additional tools.
5. Implement functionality in small, testable increments.
6. Validate locally and in the Databricks workspace as appropriate.
7. Document the implementation and decisions.
8. Update `docs/implementation-plan-results.md` with completed work and any changes.
9. Identify the next logical learning objective.

For deployment and pipeline changes, additionally:

1. Identify which selected Databricks capability owns the resource or object.
2. Define the desired state in Git.
3. Validate the bundle and configuration.
4. Deploy changes to the development environment.
5. Execute pipelines or jobs as appropriate.
6. Verify the resulting workspace resources, database objects, and data.
7. Where practical, test reconstruction in a disposable environment.

### Guiding Principle

Build a working data platform while learning Databricks, rather than completing isolated Databricks tutorials and attempting to assemble them into a project afterward.

Prefer industry-standard Databricks approaches over recreating capabilities in custom Python.

Avoid unnecessary infrastructure and competing tools. Each selected technology should have a clear responsibility in the architecture and contribute to a functioning, demonstrable data platform.

The repository should demonstrate that the platform's definitions are reproducible, not just that the platform works in one existing workspace.
