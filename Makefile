PROFILE ?= MDP
TARGET ?= dev

.PHONY: validate deploy summary wheel test lint

# Databricks bundle commands
validate:
	databricks bundle validate -t $(TARGET) --profile $(PROFILE)

deploy: validate
	databricks bundle deploy -t $(TARGET) --profile $(PROFILE)

summary:
	databricks bundle summary -t $(TARGET) --profile $(PROFILE)

# Python build commands
wheel:
	uv build --wheel

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .

check: test lint
