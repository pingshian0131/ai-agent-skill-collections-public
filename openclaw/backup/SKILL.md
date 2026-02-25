---
name: backup
description: Back up OpenClaw directories (~/.openclaw-personal and ~/.openclaw-work) as timestamped tar.gz archives. Use when the user asks to back up, create a snapshot, save current state, or archive the OpenClaw config. Also handles listing existing backups and cleaning up old ones.
---

# OpenClaw Backup

Create, list, and manage timestamped backups of `~/.openclaw-personal` and `~/.openclaw-work`.

## Commands

All operations use the bundled script at `scripts/backup.sh` (relative to this skill).

Third argument selects the environment: `personal`, `work`, or `all` (default).

### Create backup

```bash
# Back up both environments (default)
{baseDir}/.claude/skills/backup/scripts/backup.sh ~ backup

# Back up only personal
{baseDir}/.claude/skills/backup/scripts/backup.sh ~ backup personal

# Back up only work
{baseDir}/.claude/skills/backup/scripts/backup.sh ~ backup work
```

Output: `~/openclaw-{personal,work}-backup-YYYY-MM-DD-HHMM.tar.gz`

### List backups

```bash
{baseDir}/.claude/skills/backup/scripts/backup.sh ~ list
{baseDir}/.claude/skills/backup/scripts/backup.sh ~ list personal
```

### Upload latest backup to Google Drive

```bash
{baseDir}/.claude/skills/backup/scripts/backup.sh ~ upload
```

Uploads the most recent backup(s) to `gdrive:backups/openclaw/`. Optional overrides:

```bash
{baseDir}/.claude/skills/backup/scripts/backup.sh ~ upload personal <remote_name> <remote_path>
```

### Clean old backups (keep newest N)

```bash
{baseDir}/.claude/skills/backup/scripts/backup.sh ~ clean all 5
```

Deletes all but the 5 newest backups per environment. Ask user for confirmation before running clean.

## Cron schedule

Daily at 3:00 AM: backup → upload → clean (keep 7).

## Notes

- Default backup destination is `~/` (home directory).
- First argument overrides the destination directory.
- Default environment is `all` — backs up both personal and work.
- Always confirm the backup file size after creation.
- For clean operations, always confirm with the user before deleting.
- Upload requires `rclone` with a configured `gdrive` remote.
