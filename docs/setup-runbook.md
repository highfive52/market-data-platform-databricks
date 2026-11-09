# Market Data Platform — Databricks Environment Setup Runbook

**Document:** `docs/setup-runbook.md`
**Project:** `market-data-platform-databricks`
**Status:** Initial setup
**Target environment:** Databricks Free Edition

---

## 1. Purpose

Establish a reproducible local development environment and initialize the GitHub repository for the Databricks implementation of the Market Data Platform.

The initial setup includes:

- Git and GitHub repository.
- Python environment managed by `uv`.
- Ruff for linting and formatting.
- pytest for automated testing.
- pre-commit for local Git hooks.
- GitHub Actions for continuous integration.
- Databricks CLI for workspace access and deployment.
- Databricks extension for VS Code.
- Initial Declarative Automation Bundle configuration.
- Project directory and file structure.

The objective is to establish the development foundation before implementing any market data functionality.

## 2. Development Architecture

### 2.1 Local development environment

Use the following tools:

| Tool | Responsibility |
|---|---|
| VS Code | Primary development environment |
| Git | Source control |
| GitHub | Remote repository and collaboration |
| Python | Application development |
| uv | Python version, virtual environment, dependencies, lockfile |
| Ruff | Linting and formatting |
| pytest | Unit and integration testing |
| pre-commit | Automated checks before commits |
| GitHub Actions | Continuous integration |
| Databricks CLI | Workspace authentication and deployment |
| Databricks VS Code extension | Remote workspace development |

### 2.2 Development workflow

```text
                  LOCAL DEVELOPMENT
                         |
                    VS CODE
                         |
                  PYTHON SOURCE
                         |
                  UV ENVIRONMENT
                         |
               +---------+---------+
               |                   |
             RUFF                PYTEST
               |                   |
               +---------+---------+
                         |
                    PRE-COMMIT
                         |
                      GIT
                         |
                      GITHUB
                         |
                   GITHUB ACTIONS
                         |
                    CI VALIDATION
                         |
                  DATABRICKS CLI
                         |
                  DATABRICKS WORKSPACE
```

GitHub Actions will initially validate Python code and tests. Automated Databricks deployment will be introduced later, once we understand workspace authentication and deployment requirements.

### 2.3 Operating system

The primary instructions assume:

- Windows 11.
- WSL2 with Ubuntu.
- VS Code connected to WSL.
- Linux terminal for Python, Git, and Databricks CLI commands.

Keep development tools in the same environment where the repository is opened. Avoid accidentally mixing Windows and WSL Python installations, Git installations, or CLI executables.

For WSL development, prefer storing the repository in the Linux filesystem for performance. If necessary, it can also reside under `/mnt/c/working/public`.

---

## 3. Install Prerequisite Tools

### 3.1 System dependencies

Open an Ubuntu WSL terminal.

Update packages:

```bash
sudo apt update
sudo apt upgrade -y
```

Install basic utilities:

```bash
sudo apt install -y \
    git \
    curl \
    unzip \
    build-essential
```

Verify Git:

```bash
git --version
```

### 3.2 VS Code

Install the following VS Code extensions:

| Extension | Purpose |
|---|---|
| WSL | Develop inside Ubuntu WSL |
| Python | Python language support |
| Pylance | Python language intelligence |
| Ruff | Python linting and formatting |
| Databricks | Databricks workspace integration |

The Databricks extension should be the verified extension published by Databricks.

Official documentation:

- https://code.visualstudio.com/docs/remote/wsl
- https://marketplace.visualstudio.com/items?itemName=databricks.databricks

### 3.3 Install uv

Install the official uv standalone installer:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart the terminal or reload the shell environment if necessary.

Verify:

```bash
uv --version
```

uv will manage:

- Python installation.
- Project virtual environment.
- Dependency installation.
- Dependency groups.
- `uv.lock`.
- Reproducible environment synchronization.

We will not use `pip`, `requirements.txt`, or manually activated virtual environments as our normal dependency-management workflow.

Official documentation:

https://docs.astral.sh/uv/

### 3.4 Install Databricks CLI

The Databricks CLI is a standalone executable, not a Python dependency.

Install using the official Linux/WSL installer:

```bash
curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/v1.25.0/install.sh | sudo sh
```

Verify:

```bash
databricks -v
```

The CLI provides commands for:

- Workspace authentication.
- Workspace inspection.
- Bundle initialization.
- Bundle validation.
- Bundle deployment.
- Job execution.
- Resource management.

Official documentation:

https://docs.databricks.com/aws/en/dev-tools/cli/install

---

## 4. Create the Databricks Workspace

### 4.1 Create a Free Edition account

Create a Databricks Free Edition account:

https://www.databricks.com/learn/free-edition

Free Edition provides a managed Databricks workspace with serverless compute and default storage.

This will be our initial development and learning environment.

### 4.2 Record the workspace URL

After creating the workspace:

1. Open the Databricks workspace.
2. Copy the workspace URL from the browser.
3. Record the URL for CLI authentication.

The URL will resemble:

```text
https://<workspace-id>.cloud.databricks.com
```

Use the actual workspace URL supplied by Databricks.

### 4.3 Understand the environment boundary

Free Edition is intended for personal, non-commercial learning and experimentation.

It is serverless-only and has networking and compute limitations. Do not assume that arbitrary external market-data APIs or custom infrastructure will be accessible.

We will initially develop using controlled historical datasets and introduce external ingestion only after validating connectivity.

---

## 5. Create the GitHub Repository

### 5.1 Configure Git identity

Configure your Git identity if it has not already been configured:

```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

Verify:

```bash
git config --global --list
```

### 5.2 Create the project directory

Choose the project workspace location.

Example:

```bash
mkdir -p ~/working/public
cd ~/working/public
mkdir market-data-platform-databricks
cd market-data-platform-databricks
```

Initialize Git:

```bash
git init -b main
```

Create a .gitignore file in the repository root. This prevents generated files, local environments, caches, and sensitive configuration from being committed to version control.

```bash
cat > .gitignore <<'EOF'
# Python bytecode and caches
__pycache__/
*.py[cod]
*$py.class

# Python build and package artifacts
*.egg-info/
build/
dist/

# Virtual environments
.venv/
venv/
ENV/

# Testing and coverage
.pytest_cache/
.coverage
.coverage.*
htmlcov/

# Linters and type checkers
.ruff_cache/
.mypy_cache/
.pyright/

# Environment variables and secrets
.env
.env.*
!.env.example

# Databricks local bundle state and artifacts
.databricks/

# Jupyter
.ipynb_checkpoints/

# Logs
*.log

# Operating system files
.DS_Store
Thumbs.db
EOF
```

Keep uv.lock under version control so that dependency versions can be reproduced across environments. Do not ignore project source, notebooks, SQL, or Databricks resource configuration.

### 5.3 Create the GitHub repository

Create a new repository named:

```text
market-data-platform-databricks
```

Choose public or private visibility.

Do not initialize the GitHub repository with an additional README or license because we will create those locally.

After the initial local commit, connect the remote repository:

```bash
git remote add origin \
    git@github.com:<github-username>/market-data-platform-databricks.git
```

Push:

```bash
git push -u origin main
```

SSH authentication should already be configured for GitHub. If not, configure it before pushing.

---

## 6. Initialize the Python Project with uv

### 6.1 Initialize the project

From the repository root:

```bash
uv init --bare \
    --name market-data-platform-databricks \
    --python 3.12
```

Pin the Python version:

```bash
uv python pin 3.12
```

This creates the initial Python project configuration and `.python-version`.

Python 3.12 is our initial development target. Before introducing Databricks Connect or other runtime-specific dependencies, verify compatibility with the actual Databricks runtime.

### 6.2 Configure pyproject.toml

Use `pyproject.toml` as the central configuration file for:

- Project metadata.
- Runtime dependencies.
- Development dependencies.
- Build configuration.
- Ruff.
- pytest.

Initial configuration:

```toml
[project]
name = "market-data-platform-databricks"
version = "0.1.0"
description = "A Databricks implementation of a multi-provider market data platform."
readme = "README.md"
requires-python = ">=3.12,<3.13"
dependencies = [
    "pydantic>=2,<3",
]

[dependency-groups]
dev = [
    "pre-commit>=4,<5",
    "pytest>=8,<10",
    "ruff>=0.10",
]

[build-system]
requires = ["setuptools>=75"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]
include = ["market_data_platform*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "-ra"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = [
    "E4",
    "E7",
    "E9",
    "F",
    "I",
]
```

Pydantic is included because the project will retain explicit domain contracts.

We are deliberately not installing PySpark or Databricks Connect yet. Databricks provides Spark in its managed execution environment. We'll decide whether local Spark execution or Databricks Connect is useful when we reach those stages.

### 6.3 Synchronize the environment

Before synchronizing the environment, create the initial source-code structure.

We're establishing the project's Python package and organizing it around the major responsibilities of the market data platform: contracts, ingestion, bronze, silver, gold, and shared utilities.

These directories are intentionally created as empty packages for now. We'll implement them incrementally as we work through the project stages. This also gives us a conventional Python package that can be imported by notebooks and Databricks jobs, keeping reusable application logic separate from notebook-specific code.

The __init__.py files identify these directories as Python packages, while README.md satisfies the project metadata configured in pyproject.toml.

```bash
mkdir -p \
  src/market_data_platform/contracts \
  src/market_data_platform/ingestion \
  src/market_data_platform/bronze \
  src/market_data_platform/silver \
  src/market_data_platform/gold \
  src/market_data_platform/common

touch src/market_data_platform/__init__.py
touch src/market_data_platform/contracts/__init__.py
touch src/market_data_platform/ingestion/__init__.py
touch src/market_data_platform/bronze/__init__.py
touch src/market_data_platform/silver/__init__.py
touch src/market_data_platform/gold/__init__.py
touch src/market_data_platform/common/__init__.py

touch README.md
```

Generate the lockfile and install dependencies:

```bash
uv lock
uv sync
```

Verify:

```bash
uv run python --version
uv run pytest --version
uv run ruff --version
uv run pre-commit --version
```

The following files should now exist:

```text
.python-version
pyproject.toml
uv.lock
.venv/
```

Commit `.python-version`, `pyproject.toml`, and `uv.lock`.

Do not commit `.venv`.

### 6.4 Managing dependencies going forward

Add application dependencies:

```bash
uv add package-name
```

Add development dependencies:

```bash
uv add --dev package-name
```

Remove dependencies:

```bash
uv remove package-name
```

Synchronize the environment:

```bash
uv sync
```

Update dependencies and the lockfile deliberately:

```bash
uv lock --upgrade
uv sync
```

Do not manually edit `uv.lock`.

---

## 7. Create the Remaining Project Structure

In the previous section, we created the initial Python package structure under `src/market_data_platform/` and verified that `uv` can successfully build and install the project.

Now we'll create the remaining directories for notebooks, SQL, tests, Databricks resources, and development tooling.

The project separates reusable Python application logic from Databricks-specific execution artifacts:

- `src/market_data_platform/` contains reusable domain contracts, ingestion logic, and data transformations.
- `notebooks/` contains Databricks notebooks used for exploration and orchestration of development workflows.
- `sql/` contains analytical queries and data validation scripts.
- `resources/` contains Databricks Declarative Automation Bundle resource definitions.
- `tests/` contains unit and integration tests.
- `.github/` and `.vscode/` contain CI and local development configuration.

These directories are created incrementally so we can build the Databricks implementation in stages without introducing unnecessary code or dependencies upfront.

### 7.1 Create the remaining directories

Create the directories that have not already been established:

```bash
mkdir -p resources

mkdir -p notebooks

mkdir -p sql/analysis
mkdir -p sql/validation

mkdir -p tests/unit
mkdir -p tests/integration

mkdir -p .github/workflows
mkdir -p .vscode
```

The Python package directories under `src/market_data_platform/` were already created in Section 6. We do not need to recreate them.

The `docs/` directory and `README.md` also already exist.

### 7.2 Create initial source files

Create empty Python modules for the major areas of the platform.

These files provide an initial organizational structure. We'll implement them as we work through the corresponding project stages.

```bash
touch src/market_data_platform/contracts/market_trade.py
touch src/market_data_platform/contracts/market_bar.py

touch src/market_data_platform/ingestion/historical.py
touch src/market_data_platform/ingestion/streaming.py

touch src/market_data_platform/bronze/market_data.py

touch src/market_data_platform/silver/reconciliation.py
touch src/market_data_platform/silver/market_bars.py

touch src/market_data_platform/gold/analytics.py
```

### 7.3 Create notebook placeholders

Create the initial notebooks we'll use to explore and develop the medallion architecture.

```bash
touch notebooks/01_exploration.py
touch notebooks/02_bronze.py
touch notebooks/03_silver.py
touch notebooks/04_gold.py
```

These are initially empty placeholders. We'll determine which logic belongs in notebooks versus reusable Python modules as the implementation evolves.

### 7.4 Create SQL placeholders

Create directories for analytical SQL and validation queries.

```bash
touch sql/analysis/.gitkeep
touch sql/validation/.gitkeep
```

Git does not track empty directories, so `.gitkeep` files ensure these directories are included in the initial repository.

### 7.5 Create resource configuration files

Create `resources/jobs.yml`:

```bash
touch resources/jobs.yml
```

```yaml
resources:
  jobs: {}
```

Create `resources/pipelines.yml`:

```bash
touch resources/pipelines.yml
```

```yaml
resources:
  pipelines: {}
```

These are placeholders. We will define actual resources when we implement orchestration and pipelines.

### 7.6 Create documentation placeholders

```bash
touch docs/architecture.md
touch docs/databricks-concepts.md
touch docs/mdp-comparison.md
touch docs/setup-runbook.md
```

The implementation plan should also be saved as:

```text
docs/implementation-plan.md
```

---

## 8. Configure Ruff and pytest

### 8.1 Ruff

Ruff provides both linting and formatting.

Run lint checks:

```bash
uv run ruff check .
```

Automatically fix supported issues:

```bash
uv run ruff check --fix .
```

Format Python files:

```bash
uv run ruff format .
```

Verify formatting without modifying files:

```bash
uv run ruff format --check .
```

Ruff is configured centrally in `pyproject.toml`.

### 8.2 pytest

Tests are organized into:

```text
tests/
├── unit/
└── integration/
```

Unit tests should validate business logic without requiring Databricks infrastructure.

Integration tests will eventually validate behavior involving Delta tables, Databricks execution, and other external resources.

Create an initial smoke test at `tests/unit/test_project_setup.py`:

```bash
touch tests/unit/test_project_setup.py
```

```python
def test_project_setup():
    assert True
```

Run tests:

```bash
uv run pytest
```

This initial test only verifies that the test runner is configured. Replace it with meaningful tests as application functionality is introduced.

---

## 9. Configure pre-commit

pre-commit will automatically execute quality checks before Git commits.

Create `.pre-commit-config.yaml`:

```bash
touch .pre-commit-config.yaml
```

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: check-yaml
      - id: check-toml
      - id: check-merge-conflict
      - id: end-of-file-fixer
      - id: trailing-whitespace

  - repo: local
    hooks:
      - id: ruff-check
        name: Ruff lint
        entry: uv run --locked ruff check
        language: system
        types: [python]

      - id: ruff-format
        name: Ruff format check
        entry: uv run --locked ruff format --check
        language: system
        types: [python]
```

Install the Git hooks:

```bash
uv run pre-commit install
```

Run all hooks against the repository:

```bash
uv run pre-commit run --all-files
```

Normal Git commits will now trigger the configured checks automatically.

If a hook modifies a file, review the changes, stage them again, and repeat the commit.

---

## 10. Configure GitHub Actions CI

GitHub Actions will provide automated validation whenever code is pushed or a pull request is opened.

Create:

```text
.github/workflows/ci.yml
```

```bash
touch .github/workflows/ci.yml
```

Initial workflow:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  quality:
    name: Code quality and tests
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v6
        with:
          enable-cache: true

      - name: Install Python
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync --locked

      - name: Run pre-commit checks
        run: uv run pre-commit run --all-files

      - name: Run tests
        run: uv run pytest
```

### CI responsibilities

Initially, CI will validate:

1. Dependency lockfile consistency.
2. YAML and TOML syntax.
3. Git conflict markers and whitespace.
4. Ruff linting.
5. Ruff formatting.
6. pytest execution.

### Future CI/CD enhancements

Deployment automation is intentionally deferred.

Later we can introduce:

- Databricks bundle validation.
- Automated deployment to a development target.
- Databricks job execution.
- Environment-specific configuration.
- Secure CI authentication.

Do not store Databricks access tokens or other credentials in Git.

---

## 11. Configure VS Code

Create `.vscode/extensions.json`:

```bash
touch .vscode/extensions.json
```

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "charliermarsh.ruff",
    "databricks.databricks"
  ]
}
```

Create `.vscode/settings.json`:

```bash
 touch .vscode/settings.json
 ```

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "tests"
  ],
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff"
  }
}
```

Open the repository from WSL:

```bash
code .
```

Verify that VS Code is using the project's `.venv` interpreter.

The Databricks extension will be used for remote workspace integration, while Python and Ruff will provide the local development experience.

---

## 12. Configure Databricks Authentication

### 12.1 Authenticate using the Databricks CLI

Use OAuth interactive user authentication.

From the WSL terminal:

```bash
databricks auth login \
    --host https://<workspace-url> \
    --profile MDP
```

Replace the placeholder with the actual workspace URL.

Complete the browser authentication process.

The profile name `MDP` is our local reference to this Databricks workspace.

### 12.2 Verify authentication

Inspect the authentication configuration:

```bash
databricks auth describe --profile MDP
```

Verify access to the workspace:

```bash
databricks current-user me --profile MDP
```

Successful authentication should return the authenticated Databricks user.

Do not commit authentication configuration or credentials to the repository.

### 12.3 Configure the VS Code extension

1. Open the Databricks extension in VS Code.
2. Open its configuration view.
3. Select the Databricks workspace.
4. Choose OAuth user-to-machine authentication.
5. Sign in to the workspace.
6. Verify that the extension recognizes the configured workspace.

The CLI and VS Code extension should use the same workspace identity and authentication configuration where possible.

Official documentation:

https://docs.databricks.com/aws/en/dev-tools/vscode-ext/authentication

---

## 13. Initialize the Databricks Bundle

The repository will use Declarative Automation Bundles to manage Databricks resources.

We will manually establish the initial bundle configuration to preserve the selected repository structure.

### 13.1 Create databricks.yml

At the repository root:

```yaml
bundle:
  name: market-data-platform-databricks

targets:
  dev:
    mode: development
    default: true
```

The `dev` target represents our initial development deployment.

We will add workspace-specific configuration and resource definitions as we learn the deployment model.

### 13.2 Validate the bundle

From the repository root:

```bash
databricks bundle validate --profile MDP
```

Validation should identify the bundle and its deployment target.

Do not deploy any production resources at this stage.

### 13.3 Bundle development workflow

The normal workflow will eventually be:

```bash
# Validate configuration
databricks bundle validate --profile MDP

# Deploy to development
databricks bundle deploy -t dev --profile MDP

# Run a deployed job
databricks bundle run <job-name> -t dev --profile MDP
```

We will introduce actual jobs and pipelines in later implementation stages.

Official documentation:

https://docs.databricks.com/aws/en/dev-tools/bundles/

---

## 14. Create .gitignore

Create `.gitignore` in the repository root:

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/

# Virtual environments
.venv/
venv/

# uv
.python-version

# Testing
.pytest_cache/
.coverage
.coverage.*
htmlcov/

# Ruff
.ruff_cache/

# Environment variables and secrets
.env
.env.*
!.env.example

# Databricks local configuration
.databricks/
.bundle/

# Operating system
.DS_Store
Thumbs.db

# IDE temporary files
.idea/
*.swp
*.swo
```

**Correction:** `.python-version` is project configuration and must be committed. Remove the `.python-version` ignore entry shown above before committing.

The final `.gitignore` should therefore retain all entries except `.python-version`.

We want the Python version to be reproducible across development machines and CI.

---

## 15. Final Repository Structure

After initialization, the repository should resemble:

```text
market-data-platform-databricks/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .vscode/
│   ├── extensions.json
│   └── settings.json
│
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version
│
├── databricks.yml
│
├── resources/
│   ├── jobs.yml
│   └── pipelines.yml
│
├── src/
│   ├── contracts/
│   │   ├── __init__.py
│   │   ├── market_trade.py
│   │   └── market_bar.py
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── historical.py
│   │   └── streaming.py
│   │
│   ├── bronze/
│   │   ├── __init__.py
│   │   └── market_data.py
│   │
│   ├── silver/
│   │   ├── __init__.py
│   │   ├── reconciliation.py
│   │   └── market_bars.py
│   │
│   ├── gold/
│   │   ├── __init__.py
│   │   └── analytics.py
│   │
│   └── common/
│       └── __init__.py
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
│   │   └── test_project_setup.py
│   └── integration/
│
├── docs/
│   ├── architecture.md
│   ├── databricks-concepts.md
│   ├── mdp-comparison.md
│   ├── implementation-plan.md
│   └── setup-runbook.md
│
├── pyproject.toml
├── uv.lock
└── README.md
```

The `.venv` directory will exist locally but will not be committed.

---

## 16. Initial Validation

Before committing the initial project, execute the following checks.

### Python environment

```bash
uv sync --locked
uv run python --version
```

### Ruff

```bash
uv run ruff check .
uv run ruff format --check .
```

### pytest

```bash
uv run pytest
```

### pre-commit

```bash
uv run pre-commit run --all-files
```

### Databricks authentication

```bash
databricks current-user me --profile MDP
```

### Databricks bundle

```bash
databricks bundle validate --profile MDP
```

All checks should pass before the initial commit.

---

## 17. Initial Git Commit

Review the repository:

```bash
git status
```

Stage the files:

```bash
git add .
```

Commit:

```bash
git commit -m "chore: initialize Databricks project environment"
```

Push:

```bash
git push -u origin main
```

Verify that the GitHub Actions CI workflow executes successfully.

---

## 18. Completion Criteria

The environment setup is complete when:

- [ ] GitHub repository exists.
- [ ] Local Git repository is initialized.
- [ ] Python 3.12 is managed through uv.
- [ ] Virtual environment is created.
- [ ] Dependencies are recorded in pyproject.toml.
- [ ] uv.lock is committed.
- [ ] Ruff linting works.
- [ ] Ruff formatting works.
- [ ] pytest executes successfully.
- [ ] pre-commit hooks are installed and working.
- [ ] GitHub Actions CI workflow passes.
- [ ] Databricks Free Edition workspace exists.
- [ ] Databricks CLI is installed.
- [ ] CLI OAuth authentication works.
- [ ] Databricks VS Code extension is configured.
- [ ] Initial Declarative Automation Bundle validates.
- [ ] Initial repository structure is committed and pushed.

---

## 19. Next Steps

Once the environment is established, move to Stage 1 of the implementation plan.

The next development objectives are:

1. Review the initial Databricks workspace and its capabilities.
2. Explore the Databricks workspace, Catalog Explorer, and compute environment.
3. Understand the relationship between local source files and workspace resources.
4. Deploy a minimal Python notebook through a Declarative Automation Bundle.
5. Execute the notebook in Databricks.
6. Document the initial deployment process.

**Guiding principle:** Establish a reproducible software development environment first. Introduce Databricks functionality incrementally, ensuring that every new component is understood, version-controlled, and testable.
