#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG_DIR="$ROOT_DIR/Pipeline/RunLogs"
LOG_FILE="$LOG_DIR/sonarlint.log"

mkdir -p "$LOG_DIR"

LOCAL_NODE_BIN="$HOME/.local/node_modules/.bin"
if [[ -d "$LOCAL_NODE_BIN" ]]; then
  export PATH="$LOCAL_NODE_BIN:$PATH"
fi

if command -v sonarlint >/dev/null 2>&1; then
  echo "Running SonarLint..." | tee "$LOG_FILE"
  sonarlint "$ROOT_DIR" \
    -Dsonar.sourceEncoding=UTF-8 \
    --exclude "**/__pycache__/**" \
    --exclude "**/*.pyc" \
    --exclude "**/*.md" \
    2>&1 | tee -a "$LOG_FILE"
  exit "${PIPESTATUS[0]}"
fi

echo "sonarlint command not found. Install SonarLint CLI to enable lint checks." | tee "$LOG_FILE"
exit 0
