#!/usr/bin/env bash
set -euo pipefail

RECIPIENT="${1:?Usage: send_imessage.sh <recipient> <message>}"
MESSAGE="${2:?Usage: send_imessage.sh <recipient> <message>}"

# 從 .env 讀取
# TODO: Replace with your base directory path
ENV_FILE="${HOME}/.openclaw-personal/.env"
if [ -f "$ENV_FILE" ]; then
  BLUEBUBBLES_URL="${BLUEBUBBLES_URL:-$(grep '^BLUEBUBBLES_URL=' "$ENV_FILE" | cut -d= -f2-)}"
  BLUEBUBBLES_PASSWORD="${BLUEBUBBLES_PASSWORD:-$(grep '^BLUEBUBBLES_PASSWORD=' "$ENV_FILE" | cut -d= -f2-)}"
fi

: "${BLUEBUBBLES_URL:?ERROR: BLUEBUBBLES_URL not set. Add to your .env file}"
: "${BLUEBUBBLES_PASSWORD:?ERROR: BLUEBUBBLES_PASSWORD not set. Add to your .env file}"

CHAT_GUID="iMessage;-;${RECIPIENT}"
TEMP_GUID="temp-$(uuidgen | tr '[:upper:]' '[:lower:]')"

CURL_EXIT=0
RESPONSE=$(curl -s --max-time 10 -w "\n%{http_code}" -X POST \
  "${BLUEBUBBLES_URL}/api/v1/message/text?password=${BLUEBUBBLES_PASSWORD}" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg guid "$CHAT_GUID" --arg msg "$MESSAGE" --arg tguid "$TEMP_GUID" \
    '{chatGuid: $guid, message: $msg, method: "apple-script", tempGuid: $tguid}')") || CURL_EXIT=$?

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
  echo "ERROR: HTTP ${HTTP_CODE}"
  echo "$BODY" | jq -r '.message // .error // .' 2>/dev/null || echo "$BODY"
  exit 1
fi
