---
name: openclaw-cron
description: Manage OpenClaw cron jobs — create, edit, debug, and troubleshoot scheduled agent tasks. Use when the user asks about cron jobs, scheduled tasks, timed automation, or when diagnosing cron errors (e.g. "model not allowed", job failures, missed runs).
---

# OpenClaw Cron

Gateway-internal scheduler that persists jobs, wakes agents on schedule, and optionally delivers output to chat.

## CLI Wrapper Commands

Each OpenClaw instance has a dedicated host-level wrapper:

| Instance | Command | Data directory |
|----------|---------|----------------|
| personal | `openclaw-personal` | `~/.openclaw-personal` |
| work | `openclaw-work` | `~/.openclaw-work` |

**Always use the instance-specific command** (`openclaw-personal` or `openclaw-work`), never bare `openclaw`.

## CLI Quick Reference

> Examples below use `openclaw-personal`. Replace with `openclaw-work` for the work instance.

| Command | Usage | Purpose |
|---------|-------|---------|
| `list` | `openclaw-personal cron list` | Show all jobs |
| `status` | `openclaw-personal cron status` | Scheduler status |
| `add` | `openclaw-personal cron add --name "..." ...` | Create a job |
| `edit` | `openclaw-personal cron edit <jobId> ...` | Patch job fields |
| `run` | `openclaw-personal cron run <jobId>` | Force-run now |
| `run --due` | `openclaw-personal cron run <jobId> --due` | Run only if schedule is due |
| `runs` | `openclaw-personal cron runs --id <jobId> --limit N` | View run history |
| `enable` | `openclaw-personal cron enable <jobId>` | Enable a job |
| `disable` | `openclaw-personal cron disable <jobId>` | Disable a job |
| `rm` | `openclaw-personal cron rm <jobId>` | Delete a job |

## Creating Jobs

### One-shot (main session)

```bash
openclaw-personal cron add --name "Reminder" \
  --at "2026-02-01T16:00:00Z" \
  --session main --system-event "Check battery" \
  --wake now --delete-after-run
```

### Recurring isolated with delivery

```bash
openclaw-personal cron add --name "Morning brief" \
  --cron "0 7 * * *" --tz "Asia/Taipei" \
  --session isolated --message "Summarize updates." \
  --announce --channel telegram --to "YOUR_CHAT_ID"
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
openclaw-personal cron edit <jobId> --message "New prompt" --model "opus"
```

### 2. Direct file edit (for fields not exposed by CLI)

Edit `~/.openclaw-personal/cron/jobs.json` directly, then restart gateway:

```bash
# After editing jobs.json:
openclaw-personal gateway restart && sleep 5 && openclaw-personal health
```

**Job JSON structure** — see `references/job-schema.md` for full schema and examples.

## Debugging Failed Jobs

1. **Check run history:**
   ```bash
   openclaw-personal cron runs --id <jobId> --limit 5
   ```
   Returns JSON with `status`, `error`, `durationMs`.

2. **Check gateway logs:**
   ```bash
   tail -100 /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log
   ```

3. **Check session JSONL** (isolated runs):
   Sessions are stored at `~/.openclaw-personal/agents/<agentId>/sessions/`.
   Isolated cron runs use session key `cron:<jobId>`.

4. **Common errors:**
   - `model not allowed: <model>` → Remove or fix model override in payload
   - `429 / RESOURCE_EXHAUSTED` → Rate limit hit, check fallback chain
   - `gateway timeout` → CLI timeout (30s default), job may still be running in background

## Storage Paths

Paths use the instance data directory (`~/.openclaw-personal` or `~/.openclaw-work`).

| File | Path (personal example) |
|------|------|
| Job definitions | `~/.openclaw-personal/cron/jobs.json` |
| Run history | `~/.openclaw-personal/cron/runs/<jobId>.jsonl` |
| Gateway logs | `/tmp/openclaw/openclaw-YYYY-MM-DD.log` |
| Session logs | `~/.openclaw-personal/agents/<agentId>/sessions/` |
