---
name: docker-cleanup
description: Clean up dangling Docker images left by openclaw:local rebuilds. Keeps the newest 7 dangling images and removes the rest. Use when the user wants to clean Docker images, check disk usage from old builds, or manage dangling images.
---

# Docker Cleanup

Clean up dangling (`<none>:<none>`) Docker images left after `openclaw:local` rebuilds.

## Commands

All operations use the bundled script at `scripts/cleanup.sh` (relative to this skill).

### Scan (dry-run)

```bash
{baseDir}/.claude/skills/docker-cleanup/scripts/cleanup.sh scan
```

Lists all dangling images and shows which would be kept vs deleted.

### Clean

```bash
{baseDir}/.claude/skills/docker-cleanup/scripts/cleanup.sh clean
```

Deletes dangling images beyond the newest 7. Images currently in use are skipped with a warning.

## Retention policy

| Image type | Action |
|------------|--------|
| Tagged images (e.g. `openclaw:local`) | Always kept |
| Newest 7 dangling images | Kept |
| Older dangling images | Deleted |

## Cron schedule

Every 2 days at 04:30 (30 minutes after the rebuild cron at 04:00):

```
30 4 */2 * * {baseDir}/.claude/skills/docker-cleanup/scripts/cleanup.sh clean >> /tmp/openclaw-docker-cleanup.log 2>&1
```

Log: `/tmp/openclaw-docker-cleanup.log`
