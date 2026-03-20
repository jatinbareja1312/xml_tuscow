# XML Graph Backend Challenge

## Tech Stack and Why
- Python 3.12: modern typing/features with strong ecosystem support.
- Django + Django REST Framework: fast, reliable API + ORM for a small but complete backend.
- PostgreSQL (primary) + SQLite (local fallback): PostgreSQL for target-grade relational queries, SQLite for easy local/CI runs.
- `defusedxml`: safer XML parsing for untrusted/malformed input handling.
- `psycopg` (v3): PostgreSQL driver used by Django and raw SQL execution.
- Docker Compose: reproducible local database setup.
- Pytest: lightweight test runner for parser/logic validation.
- SonarLint CLI: static analysis in the local/CI pipeline.

## Overview
This project ingests a graph from XML, validates and stores it in the database, and exposes a REST API endpoint (`POST /query`) to answer path queries (`paths` and `cheapest`) against stored data.

## Prerequisites
- Python `3.12`
- Docker + Docker Compose (optional if you use SQLite local mode)

## Install
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements_dev.txt -i https://pypi.org/simple
python3 -m pip install -r DatabaseModels/requirements.txt
python3 -m pip install -r Jobs/bootstrap_upsert_graph/requirements.txt
python3 -m pip install -r API/requirements.txt
```

## Environment
```bash
cp .env.example .env
```

## Run Migrations
```bash
set -a && source .env && set +a
python3 DatabaseModels/make_migrations.py --skip-makemigrations
```

SQLite local mode (no Docker):
```bash
SQLITE_PATH=/tmp/xml_tuscow.sqlite3 python3 DatabaseModels/make_migrations.py --skip-makemigrations
```

## Load XML Job
```bash
docker compose up -d db
set -a && source .env && set +a
bash "Pipeline/Graph Ingestion Job/run_job.sh"
```

SQLite local mode (no Docker):
```bash
SQLITE_PATH=/tmp/xml_tuscow.sqlite3 bash "Pipeline/Graph Ingestion Job/run_job.sh"
```

The sample input XML is at `Jobs/bootstrap_upsert_graph/sample_graph.xml`.

## Run API
```bash
set -a && source .env && set +a
python3 DatabaseModels/manage.py runserver 0.0.0.0:8000
```

## Example API Call
```bash
curl -X POST "http://127.0.0.1:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "queries": [
      {"paths": {"start": "a", "end": "e"}},
      {"cheapest": {"start": "a", "end": "e"}}
    ]
  }'
```

## Run Tests
```bash
python3 Jobs/run_tests.py
python3 API/run_tests.py
python3 DatabaseModels/run_tests.py
```

## CI
A minimal pipeline exists at `.github/workflows/ci.yml`.

You can also run the full local pipeline:
```bash
bash "Pipeline/Graph Ingestion Job/run_all.sh"
```

SQLite local mode (no Docker):
```bash
SQLITE_PATH=/tmp/xml_tuscow.sqlite3 bash "Pipeline/Graph Ingestion Job/run_all.sh"
```

Run logs are written to:
- `Pipeline/RunLogs/pipeline.log` (tests + job)
- `Pipeline/RunLogs/sonarlint.log` (lint)

## Project Structure
- `API/`
- `CommonUtils/`
- `DatabaseModels/`
- `Jobs/`
- `Pipeline/`

## SQL and Performance Notes
- Normalized schema SQL: `DatabaseModels/sql/schema.sql`
- Cycle detection SQL: `CommonUtils/sql/find_cycles.sql`
- `EXPLAIN ANALYZE` examples: `DatabaseModels/sql/explain_analyze_samples.md`
- Raw SQL execution uses named parameter binding (for example `{"graph_id": graph_id}`) to prevent SQL injection.
