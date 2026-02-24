#!/usr/bin/env bash
set -euo pipefail
export PATH="/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin:$HOME/.orbstack/bin:$PATH"

KEEP=7
CMD="${1:-scan}"

# Get dangling images sorted by creation time (newest first)
# Format: "CreatedAt\tID"
get_dangling() {
  docker images -f dangling=true --format "{{.CreatedAt}}\t{{.ID}}" | sort -r
}

scan() {
  local images
  images=$(get_dangling)

  if [ -z "$images" ]; then
    echo "No dangling images found."
    return
  fi

  local total
  total=$(echo "$images" | wc -l | tr -d ' ')
  echo "Found $total dangling image(s). Keeping newest $KEEP."
  echo ""

  local i=0
  while IFS=$'\t' read -r created id; do
    i=$((i + 1))
    if [ "$i" -le "$KEEP" ]; then
      echo "  KEEP   $id  ($created)"
    else
      echo "  DELETE $id  ($created)"
    fi
  done <<< "$images"

  local to_delete=$((total - KEEP))
  if [ "$to_delete" -gt 0 ]; then
    echo ""
    echo "$to_delete image(s) would be deleted."
  else
    echo ""
    echo "Nothing to delete."
  fi
}

clean() {
  local images
  images=$(get_dangling)

  if [ -z "$images" ]; then
    echo "[$(date)] No dangling images found."
    return
  fi

  local total
  total=$(echo "$images" | wc -l | tr -d ' ')
  echo "[$(date)] Found $total dangling image(s). Keeping newest $KEEP."

  local i=0
  local deleted=0
  while IFS=$'\t' read -r created id; do
    i=$((i + 1))
    if [ "$i" -le "$KEEP" ]; then
      continue
    fi
    echo "[$(date)] Removing $id ($created)..."
    if docker rmi "$id" 2>&1; then
      deleted=$((deleted + 1))
    else
      echo "[$(date)] WARNING: Failed to remove $id (may be in use), skipping."
    fi
  done <<< "$images"

  echo "[$(date)] Done. Removed $deleted image(s), kept $KEEP."
}

case "$CMD" in
  scan)  scan  ;;
  clean) clean ;;
  *)
    echo "Usage: $0 {scan|clean}"
    exit 1
    ;;
esac
