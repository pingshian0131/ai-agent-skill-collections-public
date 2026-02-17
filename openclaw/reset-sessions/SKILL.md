---
name: reset-sessions
description: Reset OpenClaw agent sessions — all at once or for a specific agent. Use when the user asks to reset sessions, clear conversation context, start fresh, or wipe session history for one or all agents.
---

# Reset Sessions

## Reset All Sessions

```bash
bash ~/.openclaw/.claude/skills/reset-sessions/scripts/reset_sessions.sh
```

## Reset a Specific Agent

```bash
bash ~/.openclaw/.claude/skills/reset-sessions/scripts/reset_sessions.sh --agent <agentId>
```

Example: `--agent main`, `--agent research`, `--agent gobta`

The script fetches all session keys via `sessions.list`, filters by agent if specified, then calls `sessions.reset` for each key and prints a success/failure summary.
