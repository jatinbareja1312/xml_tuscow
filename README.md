# Project Layout (Your Style)

This repo is now arranged to match your preferred structure:

- `API/`
  - `specifications/internal/` (`prod.yaml`)
  - `tests/`
  - `views/`
  - `requirements.txt`
  - `run_tests.py`
- `DatabaseModels/`
  - `build/`
  - `django_models/`
    - `migrations/`
    - `models/`
    - `partsavatar/`
    - `tests/`
    - `apps.py`
    - `settings.py`
  - `make_migrations.py`
  - `manage.py`
  - `requirements.txt`
  - `run_tests.py`
  - `setup.py`
- `Jobs/`
  - `bootstrap_upsert_graph/`
    - `tests/`
      - `test_upsert_graph.py`
    - `main.py`
    - `requirements.txt`
    - `sample_graph.xml`
  - `run_tests.py`
- `Pipeline/`
  - `Graph Ingestion Job/`
    - `run_all.sh`
    - `run_sonarlint.sh`
    - `run_tests.sh`
    - `run_job.sh`
    - `run_local_container.sh`
  - `RunLogs/`

## Install
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements_dev.txt -i https://pypi.org/simple
```

## Environment
```bash
cp .env.example .env
```

## Start Postgres
```bash
docker compose up -d db
```

## Run Migrations
```bash
set -a && source .env && set +a
python3 DatabaseModels/make_migrations.py --skip-makemigrations
```

## Load XML Into DB (Job)
```bash
set -a && source .env && set +a
bash "Pipeline/Graph Ingestion Job/run_job.sh"
```

`sample_graph.xml` now lives inside `Jobs/bootstrap_upsert_graph/`.

## Pipeline Automation
```bash
# All-in-one: SonarLint + tests + job
bash "Pipeline/Graph Ingestion Job/run_all.sh"

# Local Docker + migration + job run
bash "Pipeline/Graph Ingestion Job/run_local_container.sh"
```

Run logs are written to:
- `Pipeline/RunLogs/pipeline.log` (all non-lint scripts)
- `Pipeline/RunLogs/sonarlint.log` (SonarLint only)

## Run API
```bash
set -a && source .env && set +a
python3 DatabaseModels/manage.py runserver 0.0.0.0:8000
```

## API Endpoints
- `POST /query`

## Library Choices
- XML parsing: `defusedxml.ElementTree` for safer XML handling than stdlib defaults.
- JSON parsing/serialization: Django REST Framework (`JSONParser` and `JSONRenderer`) via API view/request handling.

## SQL Schema and Query Assets
- Normalized SQL schema (PostgreSQL): `DatabaseModels/sql/schema.sql`
- Cycle detection SQL: `CommonUtils/sql/find_cycles.sql`
- `EXPLAIN ANALYZE` samples: `DatabaseModels/sql/explain_analyze_samples.md`

## Indexing and Query Plan Notes
- `edges(graph_id, from_node_id)`: speeds graph traversal/adjacency expansion.
- `edges(graph_id, id)`: supports ordered edge loading by graph for `/query`.
- Unique constraints auto-create indexes for graph/node/edge logical keys.
- Sample `EXPLAIN ANALYZE` output confirms index usage on graph/edge joins.

## Run Tests
```bash
python3 Jobs/run_tests.py
python3 API/run_tests.py
python3 DatabaseModels/run_tests.py
```

## CI/CD
A minimal pipeline exists at `.github/workflows/ci.yml`.
