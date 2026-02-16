---
name: openclaw-cron
description: Manage OpenClaw cron jobs — create, edit, debug, and troubleshoot scheduled agent tasks. Use when the user asks about cron jobs, scheduled tasks, timed automation, or when diagnosing cron errors (e.g. "model not allowed", job failures, missed runs).
---

# OpenClaw Cron

Gateway-internal scheduler that persists jobs, wakes agents on schedule, and optionally delivers output to chat.

## CLI Quick Reference

| Command | Usage | Purpose |
|---------|-------|---------|
| `list` | `openclaw cron list` | Show all jobs |
| `status` | `openclaw cron status` | Scheduler status |
| `add` | `openclaw cron add --name "..." ...` | Create a job |
| `edit` | `openclaw cron edit <jobId> ...` | Patch job fields |
| `run` | `openclaw cron run <jobId>` | Force-run now |
| `run --due` | `openclaw cron run <jobId> --due` | Run only if schedule is due |
| `runs` | `openclaw cron runs --id <jobId> --limit N` | View run history |
| `enable` | `openclaw cron enable <jobId>` | Enable a job |
| `disable` | `openclaw cron disable <jobId>` | Disable a job |
| `rm` | `openclaw cron rm <jobId>` | Delete a job |

## Creating Jobs

### One-shot (main session)

```bash
openclaw cron add --name "Reminder" \
  --at "2026-02-01T16:00:00Z" \
  --session main --system-event "Check battery" \
  --wake now --delete-after-run
```

### Recurring isolated with delivery

```bash
openclaw cron add --name "Morning brief" \
  --cron "0 7 * * *" --tz "Asia/Taipei" \
  --session isolated --message "Summarize updates." \
  --announce --channel telegram --to "YOUR_TELEGRAM_ID"
```

### Key `add` / `edit` flags

| Flag | Description |
|------|-------------|
| `--name` | Job name |
| `--at` | One-shot ISO 8601 timestamp |
| `--cron` | 5-field cron expression |
| `--every` | Fixed interval (ms) |
| `--tz` | IANA timezone (default: host tz) |
| `--session` | `main` or `isolated` |
| `--system-event` | Text payload for main sessions |
| `--message` | Text prompt for isolated sessions |
| `--model` | Model override (e.g. `opus`, `google/gemini-2.5-flash`) |
| `--thinking` | Thinking level: `off\|minimal\|low\|medium\|high\|xhigh` |
| `--announce` | Enable summary delivery |
| `--channel` | Target: `telegram\|whatsapp\|slack\|discord\|signal\|imessage\|mattermost` |
| `--to` | Channel-specific recipient |
| `--agent` | Bind to specific agent |
| `--clear-agent` | Remove agent binding (edit only) |
| `--wake` | `now` or `next-heartbeat` |
| `--delete-after-run` | Auto-remove one-shot jobs after completion |

## Editing Jobs

Two approaches:

### 1. CLI edit (preferred for single fields)

```bash
openclaw cron edit <jobId> --message "New prompt" --model "opus"
```

### 2. Direct file edit (for fields not exposed by CLI)

Edit `~/.openclaw/cron/jobs.json` directly, then restart gateway:

```bash
# After editing jobs.json:
openclaw gateway restart && sleep 5 && openclaw health
```

**Job JSON structure** — see `references/job-schema.md` for full schema and examples.

## Debugging Failed Jobs

1. **Check run history:**
   ```bash
   openclaw cron runs --id <jobId> --limit 5
   ```
   Returns JSON with `status`, `error`, `durationMs`.

2. **Check gateway logs:**
   ```bash
   tail -100 /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log
   ```

3. **Check session JSONL** (isolated runs):
   Sessions are stored at `~/.openclaw/agents/<agentId>/sessions/`.
   Isolated cron runs use session key `cron:<jobId>`.

4. **Common errors:**
   - `model not allowed: <model>` → Remove or fix model override in payload
   - `429 / RESOURCE_EXHAUSTED` → Rate limit hit, check fallback chain
   - `gateway timeout` → CLI timeout (30s default), job may still be running in background

## Storage Paths

| File | Path |
|------|------|
| Job definitions | `~/.openclaw/cron/jobs.json` |
| Run history | `~/.openclaw/cron/runs/<jobId>.jsonl` |
| Gateway logs | `/tmp/openclaw/openclaw-YYYY-MM-DD.log` |
| Session logs | `~/.openclaw/agents/<agentId>/sessions/` |
