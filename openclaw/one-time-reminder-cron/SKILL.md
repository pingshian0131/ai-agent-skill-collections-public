---
name: one-time-reminder-cron
description: Create or update a one-time reminder in OpenClaw by editing the local cron registry file (~/.openclaw/cron/jobs.json). Use when the user asks to set a one-off reminder (e.g., “tomorrow 6am remind me …”), rename the template reminder job, or quickly change only the reminder time + message content for repeated one-off reminders on Telegram.
---

# One-time reminder (cron)

Use the **template job** named:
- `One-time reminder (edit time + content)`

This “one-time” reminder is implemented as a cron entry and therefore **must be disabled after it fires** (otherwise it will recur yearly on the same month/day).

## Quick workflow

1) Update the template job’s schedule + message via script:

```bash
python3 skills/one-time-reminder-cron/scripts/upsert_one_time_reminder.py \
  --when "2026-02-24 06:00" --tz Asia/Taipei \
  --message "主人提醒：今天 10:00–12:00 物流會送貨。"
```

2) (Recommended) After the reminder fires, disable it:

```bash
python3 skills/one-time-reminder-cron/scripts/disable_job_by_name.py \
  --name "One-time reminder (edit time + content)"
```

## Notes / guardrails

- Cron registry file:
  - `{baseDir}/cron/jobs.json`
- Always write a backup before modifications (scripts do this automatically).
- If the template job does not exist, the script creates it targeting the default Telegram chat ID (configured in script).
- To rename the template job, use:

```bash
python3 skills/one-time-reminder-cron/scripts/rename_job_by_id.py \
  --id <jobId> --name "<new name>"
```
