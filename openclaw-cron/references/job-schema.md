# Cron Job JSON Schema

## Job Object

```json
{
  "id": "uuid",
  "agentId": "main",
  "name": "Job display name",
  "description": "Optional metadata",
  "enabled": true,
  "createdAtMs": 1771115087622,
  "updatedAtMs": 1771200000033,
  "schedule": { "..." },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": { "..." },
  "delivery": { "..." },
  "deleteAfterRun": false,
  "notify": false,
  "state": { "..." }
}
```

## Schedule Types

### One-shot

```json
{ "kind": "at", "at": "2026-02-01T16:00:00Z" }
```

### Fixed interval

```json
{ "kind": "every", "everyMs": 3600000 }
```

### Cron expression

```json
{ "kind": "cron", "expr": "0 8 * * *", "tz": "Asia/Taipei" }
```

## Payload Types

### Main session (systemEvent)

```json
{ "kind": "systemEvent", "text": "Event description" }
```

### Isolated session (agentTurn)

```json
{
  "kind": "agentTurn",
  "message": "Agent prompt text",
  "model": "google/gemini-2.5-flash",
  "timeoutSeconds": 120
}
```

Model resolution order: payload.model > hook defaults > agent config default.

Remove `"model"` key entirely to use agent default.

## Delivery (isolated only)

```json
{
  "mode": "announce",
  "channel": "telegram",
  "to": "YOUR_TELEGRAM_ID",
  "bestEffort": true
}
```

### Telegram topic targets

- `-1001234567890` (chat ID)
- `-1001234567890:topic:123` (preferred)
- `-1001234567890:123` (shorthand)

## State (read-only, managed by scheduler)

```json
{
  "nextRunAtMs": 1771286400000,
  "lastRunAtMs": 1771200000010,
  "lastStatus": "ok",
  "lastDurationMs": 5186,
  "lastError": null,
  "consecutiveErrors": 0
}
```

## Full Example: Recurring Isolated Job

```json
{
  "id": "5857be7f-5492-43d8-bbda-f3de8898ffc5",
  "agentId": "main",
  "name": "Daily 8AM session reset + memory capture reminder",
  "enabled": true,
  "createdAtMs": 1771115087622,
  "updatedAtMs": 1771218837502,
  "schedule": {
    "kind": "cron",
    "expr": "0 8 * * *",
    "tz": "Asia/Taipei"
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "Execute daily reset routine."
  },
  "delivery": {
    "mode": "announce",
    "channel": "telegram",
    "to": "YOUR_TELEGRAM_ID",
    "bestEffort": true
  }
}
```

## Retry Behavior

Recurring jobs use exponential backoff on consecutive errors:
30s → 1m → 5m → 15m → 60m. Resets after next successful run.

One-shot jobs do not retry; they disable after terminal run.
