#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG_DIR="$ROOT_DIR/Pipeline/RunLogs"
PIPELINE_LOG="$LOG_DIR/pipeline.log"

mkdir -p "$LOG_DIR"

run() {
  echo "RunAll start"
  bash "$ROOT_DIR/Pipeline/Graph Ingestion Job/run_sonarlint.sh"
  bash "$ROOT_DIR/Pipeline/Graph Ingestion Job/run_tests.sh"
  bash "$ROOT_DIR/Pipeline/Graph Ingestion Job/run_job.sh"
  echo "RunAll finished"
}

if [[ -n "${PIPELINE_RUN_LOG:-}" ]]; then
  run
  exit $?
fi

export PIPELINE_RUN_LOG="$PIPELINE_LOG"
run 2>&1 | tee "$PIPELINE_LOG"
exit "${PIPESTATUS[0]}"
