#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG_DIR="$ROOT_DIR/Pipeline/RunLogs"
PIPELINE_LOG="$LOG_DIR/pipeline.log"

mkdir -p "$LOG_DIR"

run() {
  echo "Running Jobs tests..."
  python3 "$ROOT_DIR/Jobs/run_tests.py"
  echo "Running API tests..."
  python3 "$ROOT_DIR/API/run_tests.py"
  echo "Running DatabaseModels tests..."
  python3 "$ROOT_DIR/DatabaseModels/run_tests.py"
}

if [[ -n "${PIPELINE_RUN_LOG:-}" ]]; then
  run
  exit $?
fi

export PIPELINE_RUN_LOG="$PIPELINE_LOG"
run 2>&1 | tee "$PIPELINE_LOG"
exit "${PIPESTATUS[0]}"
