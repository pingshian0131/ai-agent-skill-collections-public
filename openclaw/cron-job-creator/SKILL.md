---
name: cron-job-creator
description: Create, update, delete, rename, enable/disable, or clone OpenClaw cron jobs by editing the cron registry file directly. Use when the user asks to add a scheduled notification, recurring watcher, one-time reminder via cron, or manage existing scheduled jobs (list, modify, remove, toggle).
---

# Cron Job Creator (OpenClaw)

Manage OpenClaw scheduled jobs by editing `/home/node/.openclaw/cron/jobs.json`.
All mutating scripts auto-backup the registry before writing.

## Create a job (cron expr)

```bash
python3 skills/cron-job-creator/scripts/create_job.py \
  --name "Watch: foo" \
  --agentId souei \
  --schedule-kind cron --cron "0 9 * * *" --tz Asia/Taipei \
  --payload-kind agentTurn --message "..." \
  --delivery-channel telegram --delivery-to <chatId>
```

## Create a job (every N ms)

```bash
python3 skills/cron-job-creator/scripts/create_job.py \
  --name "Watch: releases" \
  --agentId souei \
  --schedule-kind every --every-ms 21600000 \
  --payload-kind agentTurn --message "..." \
  --delivery-channel telegram --delivery-to <chatId>
```

## List jobs

```bash
python3 skills/cron-job-creator/scripts/list_jobs.py
```

## Update job fields

```bash
python3 skills/cron-job-creator/scripts/update_job.py --id <jobId> \
  --message "new prompt" --cron "30 8 * * *" --model openai/gpt-4o
```

Accepts any combination of: `--name`, `--agentId`, `--enabled`, `--notify`, `--schedule-kind`, `--cron`, `--tz`, `--every-ms`, `--anchor-ms`, `--payload-kind`, `--message`, `--thinking`, `--model`, `--timeoutSeconds`, `--delivery-channel`, `--delivery-to`.

## Delete by id

```bash
python3 skills/cron-job-creator/scripts/delete_job.py --id <jobId>
```

## Enable/disable by id

```bash
python3 skills/cron-job-creator/scripts/set_enabled.py --id <jobId> --enabled false
```

## Rename by id

```bash
python3 skills/cron-job-creator/scripts/rename_job.py --id <jobId> --name "New name"
```

## Clone an existing job

```bash
python3 skills/cron-job-creator/scripts/clone_job.py --id <jobId> --new-name "Copy"
```

## Guardrails

- Prefer `schedule.kind=every` for periodic watches.
- For one-time reminders via `schedule.kind=cron` with day+month set, **disable after it fires** to avoid yearly repeats.
- `payload.kind`: `agentTurn` (runs an agent message) or `systemEvent` (injects text into main session).
- Default Telegram delivery: `--delivery-channel telegram --delivery-to <chatId>`. <!-- TODO: Replace with your Telegram chat ID -->
