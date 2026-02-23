---
name: memory-cleanup
description: Scan and clean up empty or minimal session memory files across all Claude Code workspace agents. Use when the user asks to clean memory, check memory usage, or manage agent session files.
---

# Memory Cleanup

Detect and remove empty/minimal session memory files from `~/.claude/projects/*/memory/`.

## Commands

All operations use the bundled script at `scripts/clean_memory.sh` (relative to this skill).

### Scan (dry-run preview)

```bash
{baseDir}/.claude/skills/memory-cleanup/scripts/clean_memory.sh scan
```

Lists files that would be deleted without actually removing them. **Default subcommand.**

### Clean (delete detected files)

```bash
{baseDir}/.claude/skills/memory-cleanup/scripts/clean_memory.sh clean
```

Deletes EMPTY and MINIMAL session files. Ask user for confirmation before running.

### Report (memory usage statistics)

```bash
{baseDir}/.claude/skills/memory-cleanup/scripts/clean_memory.sh report
```

Shows per-agent memory directory statistics: file count, total size, and breakdown by status.

## Detection Logic

Only `.md` files are evaluated. HTML/TSV/JSON files are never touched.

| Category | Criteria |
|----------|----------|
| **SKIP** | File does not start with `# Session:` (e.g., date-based `# 2026-02-16` headers, `MEMORY.md`) |
| **EMPTY** | Starts with `# Session:`, no `## Conversation Summary` section, only session metadata |
| **MINIMAL** | Starts with `# Session:`, has `## Conversation Summary` but content < 500 bytes and no real user messages |
| **OK** | File > 1500 bytes, or has substantive conversation content |

## Cron Schedule

Weekly on Sundays at 03:30 AM (30 minutes after the backup cron at 03:00):

```
# TODO: Replace {baseDir} with your actual base directory path
30 3 * * 0 {baseDir}/.claude/skills/memory-cleanup/scripts/clean_memory.sh clean >> /tmp/openclaw-memory-cleanup.log 2>&1
```

## Notes

- Conservative strategy: when in doubt, keep the file.
- Only processes files matching `# Session:` header pattern.
- Persistent memory files like `MEMORY.md` are never touched.
- Always run `scan` first to preview before running `clean`.
