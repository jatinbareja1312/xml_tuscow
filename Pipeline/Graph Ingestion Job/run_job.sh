#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG_DIR="$ROOT_DIR/Pipeline/RunLogs"
PIPELINE_LOG="$LOG_DIR/pipeline.log"

mkdir -p "$LOG_DIR"

run() {
  if [[ -f "$ROOT_DIR/.env" ]]; then
    set -a
    # shellcheck disable=SC1091
    source "$ROOT_DIR/.env"
    set +a
  fi

  # Default to SQLite for local/CI runs when Postgres env is not provided.
  using_default_sqlite=0
  if [[ -z "${SQLITE_PATH:-}" && -z "${POSTGRES_HOST:-}" ]]; then
    export SQLITE_PATH="/tmp/xml_tuscow_job.sqlite3"
    using_default_sqlite=1
  fi

  if [[ "$using_default_sqlite" -eq 1 ]]; then
    rm -f "$SQLITE_PATH"
  fi

  echo "Running migrations for job..."
  cd "$ROOT_DIR"
  python3 "$ROOT_DIR/DatabaseModels/make_migrations.py" --skip-makemigrations
  echo "Running graph import job..."
  PYTHONPATH="$ROOT_DIR:${PYTHONPATH:-}" python3 "$ROOT_DIR/Jobs/bootstrap_upsert_graph/main.py"
}

if [[ -n "${PIPELINE_RUN_LOG:-}" ]]; then
  run
  exit $?
fi

export PIPELINE_RUN_LOG="$PIPELINE_LOG"
run 2>&1 | tee "$PIPELINE_LOG"
exit "${PIPESTATUS[0]}"
