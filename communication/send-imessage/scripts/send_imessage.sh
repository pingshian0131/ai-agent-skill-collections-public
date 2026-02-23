#!/usr/bin/env bash
set -euo pipefail

RECIPIENT="${1:?Usage: send_imessage.sh <recipient> <message>}"
MESSAGE="${2:?Usage: send_imessage.sh <recipient> <message>}"

# 從 .env 讀取（Docker 內為 ~/.openclaw/.env，host 為 ~/.openclaw-personal/.env）
ENV_FILE=""
if [ -f "${HOME}/.openclaw/.env" ]; then
  ENV_FILE="${HOME}/.openclaw/.env"
elif [ -f "${HOME}/.openclaw-personal/.env" ]; then
  ENV_FILE="${HOME}/.openclaw-personal/.env"
fi

if [ -n "$ENV_FILE" ]; then
  BLUEBUBBLES_URL="$(grep '^BLUEBUBBLES_URL=' "$ENV_FILE" | cut -d= -f2-)"
  BLUEBUBBLES_PASSWORD="$(grep '^BLUEBUBBLES_PASSWORD=' "$ENV_FILE" | cut -d= -f2-)"
fi

: "${BLUEBUBBLES_URL:?ERROR: BLUEBUBBLES_URL not set. Add to ~/.openclaw/.env}"
: "${BLUEBUBBLES_PASSWORD:?ERROR: BLUEBUBBLES_PASSWORD not set. Add to ~/.openclaw/.env}"

CHAT_GUID="iMessage;-;${RECIPIENT}"
if command -v uuidgen >/dev/null 2>&1; then
  TEMP_GUID="temp-$(uuidgen | tr '[:upper:]' '[:lower:]')"
elif [ -f /proc/sys/kernel/random/uuid ]; then
  TEMP_GUID="temp-$(cat /proc/sys/kernel/random/uuid)"
else
  TEMP_GUID="temp-$(date +%s)-$$"
fi

# JSON escape（處理訊息中的 " 和 \ ）
json_escape() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'; }

JSON_BODY="{\"chatGuid\":\"$(json_escape "$CHAT_GUID")\",\"message\":\"$(json_escape "$MESSAGE")\",\"method\":\"apple-script\",\"tempGuid\":\"$(json_escape "$TEMP_GUID")\"}"

CURL_EXIT=0
RESPONSE=$(curl -s --max-time 10 -w "\n%{http_code}" -X POST \
  "${BLUEBUBBLES_URL}/api/v1/message/text?password=${BLUEBUBBLES_PASSWORD}" \
  -H "Content-Type: application/json" \
  -d "$JSON_BODY") || CURL_EXIT=$?

# curl exit 28 = timeout，apple-script method 常見，訊息已送出
if [ "$CURL_EXIT" -eq 28 ]; then
  echo "OK: iMessage sent to ${RECIPIENT} (apple-script method)"
  exit 0
elif [ "$CURL_EXIT" -ne 0 ]; then
  echo "ERROR: curl failed (exit code ${CURL_EXIT})"
  exit 1
fi

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 300 ]; then
  echo "OK: iMessage sent to ${RECIPIENT}"
elif [ "$HTTP_CODE" -eq 500 ] || [ "$HTTP_CODE" = "000" ]; then
  # apple-script method 常回 500 或 timeout，但訊息實際已送出
  echo "OK: iMessage sent to ${RECIPIENT} (apple-script method)"
else
  echo "ERROR: HTTP ${HTTP_CODE} — ${BODY}"
  exit 1
fi
