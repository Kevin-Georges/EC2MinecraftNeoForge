#!/usr/bin/env bash
set -euo pipefail

MC_DIR="/opt/minecraft"
cd "$MC_DIR"

# NeoForge installer generates a run script; use it if present
if [[ -f "./run.sh" ]]; then
  exec bash ./run.sh nogui
fi

# Fallback: start the generated server jar if known
# Adjust jar name if needed:
JAR="$(ls -1 *.jar 2>/dev/null | head -n 1 || true)"
if [[ -z "${JAR}" ]]; then
  echo "No jar found in ${MC_DIR}. Did NeoForge install generate files?"
  exit 1
fi

exec java @user_jvm_args.txt -jar "${JAR}" nogui
