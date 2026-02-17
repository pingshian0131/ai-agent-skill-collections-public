#!/usr/bin/env bash
# Usage: reset_sessions.sh [--agent <agentId>]
# Without --agent: resets all sessions
# With --agent <id>: resets only sessions for that agent

set -euo pipefail

AGENT_FILTER=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent) AGENT_FILTER="$2"; shift 2 ;;
    *) echo "Unknown argument: $1"; exit 1 ;;
  esac
done

echo "Fetching session list..."
# Strip the leading "Gateway call: ..." header line, keep only the JSON block
sessions_json=$(openclaw gateway call sessions.list --params '{}' 2>&1 | sed '1d')

if [[ -n "$AGENT_FILTER" ]]; then
  echo "Filtering to agent: $AGENT_FILTER"
  keys=$(echo "$sessions_json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
prefix = 'agent:$AGENT_FILTER:'
for s in data.get('sessions', []):
    if s['key'].startswith(prefix):
        print(s['key'])
")
else
  keys=$(echo "$sessions_json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for s in data.get('sessions', []):
    print(s['key'])
")
fi

total=$(echo "$keys" | grep -c . 2>/dev/null || echo 0)

if [[ "$total" -eq 0 ]]; then
  echo "No sessions found."
  exit 0
fi

success=0
failed=0

echo "Found $total sessions. Resetting..."

while IFS= read -r key; do
  [[ -z "$key" ]] && continue
  result=$(openclaw gateway call sessions.reset --params "{\"key\": \"$key\"}" 2>&1)
  if echo "$result" | grep -q '"ok": true'; then
    echo "  ✓ $key"
    ((success++)) || true
  else
    echo "  ✗ $key"
    ((failed++)) || true
  fi
done <<< "$keys"

echo ""
echo "Done: $success succeeded, $failed failed (total: $total)"
