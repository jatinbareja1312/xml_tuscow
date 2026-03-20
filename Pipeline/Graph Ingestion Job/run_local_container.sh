#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG_DIR="$ROOT_DIR/Pipeline/RunLogs"
PIPELINE_LOG="$LOG_DIR/pipeline.log"

mkdir -p "$LOG_DIR"

run() {
  echo "Starting Postgres container..."
  docker compose -f "$ROOT_DIR/docker-compose.yml" up -d db

  echo "Waiting for Postgres readiness..."
  for _ in {1..30}; do
    if docker compose -f "$ROOT_DIR/docker-compose.yml" exec -T db pg_isready -U postgres -d xml_graph >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done

  echo "Running migrations..."
  if [[ -f "$ROOT_DIR/.env" ]]; then
    set -a
    # shellcheck disable=SC1091
    source "$ROOT_DIR/.env"
    set +a
  fi
  python3 "$ROOT_DIR/DatabaseModels/make_migrations.py" --skip-makemigrations

  echo "Running graph import job..."
  bash "$ROOT_DIR/Pipeline/Graph Ingestion Job/run_job.sh"
}

if [[ -n "${PIPELINE_RUN_LOG:-}" ]]; then
  run
  exit $?
fi

export PIPELINE_RUN_LOG="$PIPELINE_LOG"
run 2>&1 | tee "$PIPELINE_LOG"
exit "${PIPESTATUS[0]}"
