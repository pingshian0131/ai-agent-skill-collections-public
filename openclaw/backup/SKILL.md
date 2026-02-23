---
name: backup
description: Back up the OpenClaw base directory as a timestamped tar.gz archive. Use when the user asks to back up, create a snapshot, save current state, or archive the OpenClaw config. Also handles listing existing backups and cleaning up old ones.
---

# OpenClaw Backup

Create, list, and manage timestamped backups of `{baseDir}`.

## Commands

All operations use the bundled script at `scripts/backup.sh` (relative to this skill).

### Create backup

```bash
{baseDir}/.claude/skills/backup/scripts/backup.sh ~ backup
```

Output: `~/openclaw-backup-YYYY-MM-DD-HHMM.tar.gz`

### List backups

```bash
{baseDir}/.claude/skills/backup/scripts/backup.sh ~ list
```

### Upload latest backup to Google Drive

```bash
{baseDir}/.claude/skills/backup/scripts/backup.sh ~ upload
```

Uploads the most recent backup to `gdrive:backups/openclaw/`. Optional overrides:

```bash
{baseDir}/.claude/skills/backup/scripts/backup.sh ~ upload <remote_name> <remote_path>
```

### Clean old backups (keep newest N)

```bash
{baseDir}/.claude/skills/backup/scripts/backup.sh ~ clean 5
```

Deletes all but the 5 newest backups. Ask user for confirmation before running clean.

## Cron schedule

Daily at 3:00 AM: backup → upload → clean (keep 7).

## Notes

- Default backup destination is `~/` (home directory).
- First argument overrides the destination directory.
- Always confirm the backup file size after creation.
- For clean operations, always confirm with the user before deleting.
- Upload requires `rclone` with a configured `gdrive` remote.
