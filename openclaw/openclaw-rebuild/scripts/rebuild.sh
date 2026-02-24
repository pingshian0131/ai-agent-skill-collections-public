#!/usr/bin/env bash
set -euo pipefail
export PATH="/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin:$HOME/.orbstack/bin:$PATH"

REPO="$HOME/Documents/openclaw"
COMPOSE="$HOME/openclaw-docker/docker-compose.yml"
LOG="/tmp/openclaw-rebuild.log"

echo "=== OpenClaw rebuild started at $(date) ===" >> "$LOG"

# Fetch tags and checkout latest stable release
git -C "$REPO" fetch --tags >> "$LOG" 2>&1
LATEST_TAG=$(git -C "$REPO" tag --sort=-v:refname | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' | head -1)
CURRENT_TAG=$(git -C "$REPO" describe --tags --exact-match 2>/dev/null || echo "none")

if [ "$LATEST_TAG" = "$CURRENT_TAG" ]; then
  echo "Already on latest release $LATEST_TAG, skipping rebuild." >> "$LOG"
  echo "=== OpenClaw rebuild skipped at $(date) ===" >> "$LOG"
  exit 0
fi

echo "Updating from $CURRENT_TAG to $LATEST_TAG" >> "$LOG"
git -C "$REPO" checkout "$LATEST_TAG" >> "$LOG" 2>&1

# Build
docker build -t openclaw:local -f "$REPO/Dockerfile" "$REPO" >> "$LOG" 2>&1

# Restart
docker compose -f "$COMPOSE" up -d >> "$LOG" 2>&1

echo "=== OpenClaw rebuild completed at $(date) ===" >> "$LOG"
