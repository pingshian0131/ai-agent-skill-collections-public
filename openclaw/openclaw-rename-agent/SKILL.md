---
name: openclaw-rename-agent
description: Rename an OpenClaw agent — updates the agent's ID across openclaw.json (agent definition, allowAgents lists, Discord bindings, LanceDB scopes), cron/jobs.json, workspace and agent directories, and all markdown files that reference the old ID. Use when the user wants to rename an agent, change an agent's ID, or sync an agent's ID with their actual character name/identity. Triggers on phrases like "rename agent X to Y", "change agent ID from X to Y", "agent X 改名為 Y", "把 agent X 的 ID 改成 Y", or when an agent's current ID doesn't match their displayed identity.
---

# OpenClaw Agent Rename

Renaming an agent touches many files. Follow these steps in order — skipping any step risks leaving dangling references that will cause runtime errors.

## Step 0: Gather info and plan

You need:
- **OLD_ID**: the current agent ID (e.g., `craftsman`)
- **NEW_ID**: the desired agent ID (e.g., `kaijin`)
- **DATA_DIR**: OpenClaw data directory (default: `~/.openclaw`)

If not provided by the user, ask before proceeding.

**Pre-flight checks** — read `$DATA_DIR/openclaw.json` and confirm:
1. OLD_ID exists in `agents.list` — if not, abort and tell the user
2. NEW_ID is not already in use — if it is, abort

**Detect LanceDB**: check if any entry in `plugins.entries` has `"enabled": true` and its key contains `lancedb`. Save result as `HAS_LANCEDB=true/false`. This determines whether to update scope config and what to write in MEMORY.md.

Show the user a summary of what will change and ask for confirmation before proceeding.

---

## Step 1: Update openclaw.json

`openclaw.json` is large. Use `sed` for batch replacements — the Edit tool may fail on large files.

### 1a. Agent definition block

Find the agent's entry in `agents.list` and update four fields. These require targeted edits because the new workspace/agentDir paths differ structurally from the agent ID string:

```bash
# Replace workspace path (e.g., workspace-craftsman → workspace-kaijin)
sed -i '' "s|workspace-${OLD_ID}|workspace-${NEW_ID}|g" "$DATA_DIR/openclaw.json"

# Replace agents dir path (e.g., /agents/craftsman/ → /agents/kaijin/)
sed -i '' "s|/agents/${OLD_ID}/|/agents/${NEW_ID}/|g" "$DATA_DIR/openclaw.json"
```

### 1b. All quoted ID references (allowAgents, bindings, account key, agentAccess key)

Agent IDs appear as quoted JSON strings `"craftsman"` in many places:
- Other agents' `subagents.allowAgents` arrays
- `bindings[].agentId` and `bindings[].match.accountId`
- `channels.discord.accounts` key
- `plugins.*.config.scopes.agentAccess` key

One sed covers all of these:

```bash
sed -i '' "s/\"${OLD_ID}\"/\"${NEW_ID}\"/g" "$DATA_DIR/openclaw.json"
```

This is safe because agent IDs only appear as standalone quoted strings. The workspace/agentDir paths (handled above) contain the name embedded inside a longer string and won't match this pattern.

### 1c. LanceDB scope definitions (only if HAS_LANCEDB)

LanceDB scope keys use the `agent:id` pattern. If LanceDB is configured:

```bash
sed -i '' "s/\"agent:${OLD_ID}\"/\"agent:${NEW_ID}\"/g" "$DATA_DIR/openclaw.json"
```

**Do NOT touch the actual LanceDB binary files** (Parquet format under `memory/`). The old namespace will be orphaned — this is intentional and harmless.

Verify the changes look correct:
```bash
grep -n "${OLD_ID}" "$DATA_DIR/openclaw.json"
# Should return nothing (or only in unrelated strings)
```

---

## Step 2: Update cron/jobs.json

Replace all `agentId` references. The file can be large, so use `sed`:

```bash
sed -i '' "s/\"agentId\": \"${OLD_ID}\"/\"agentId\": \"${NEW_ID}\"/g" \
  "$DATA_DIR/cron/jobs.json"
```

Verify:
```bash
grep "\"agentId\": \"${OLD_ID}\"" "$DATA_DIR/cron/jobs.json"
# Should return nothing
```

---

## Step 3: Rename directories

```bash
mv "$DATA_DIR/workspace-${OLD_ID}" "$DATA_DIR/workspace-${NEW_ID}"
mv "$DATA_DIR/agents/${OLD_ID}" "$DATA_DIR/agents/${NEW_ID}"
```

---

## Step 4: Update markdown and settings files

### 4a. Broad sweep — find all affected files

```bash
grep -r "${OLD_ID}" "$DATA_DIR" \
  --include="*.md" \
  --include="*.json" \
  --exclude="*.bak" \
  --exclude-dir="sessions" \
  --exclude-dir="sessions-archive" \
  -l
```

### 4b. Categorize results

For each file found, classify it:

**Always update** (functional references):
- `CLAUDE.md`, `CODEX.md` — agent registry tables
- `workspace/AGENTS.md` — agent directory/routing table
- Any `workspace-*/AGENTS.md` — other agents' agent rosters
- Any `workspace-*/TOOLS.md` — agent dispatch tables
- Any `workspace-*/SOUL.md` — agent delegation instructions
- `skills/*/references/config-reference.md` — agent reference tables (in `.claude/`, `.codex/`, any workspace)
- `.claude/settings.local.json`, `.codex/settings.local.json` — may contain workspace paths

**Skip** (historical, not functional):
- Files in `sessions/` or `sessions-archive/`
- `obsidian-log-*.md` or similar historical logs
- `*.bak` files
- Build artifacts (e.g., `coverage/*.json`)
- The new MEMORY.md rename record you're about to write (Step 5)

### 4c. Apply updates

For each file to update, use targeted replacement. Typical patterns:

```bash
# Replace bare agent ID references (e.g., in tables: | craftsman | → | kaijin |)
sed -i '' "s/${OLD_ID}/${NEW_ID}/g" path/to/file

# Or use Edit tool for precise context-aware changes
```

For `settings.local.json` files, replace workspace path references:
```bash
sed -i '' "s/workspace-${OLD_ID}/workspace-${NEW_ID}/g" \
  "$DATA_DIR/.claude/settings.local.json" \
  "$DATA_DIR/.codex/settings.local.json" 2>/dev/null
```

---

## Step 5: Add rename record to MEMORY.md

This step is **always required**, regardless of LanceDB status.

Open `$DATA_DIR/workspace-${NEW_ID}/MEMORY.md` and prepend a rename record immediately after the first heading:

```markdown
## 身份變更紀錄
- {TODAY}: Agent ID 由 `{OLD_ID}` 改名為 `{NEW_ID}`。{LANCEDB_NOTE}
```

Where `{LANCEDB_NOTE}`:
- **If HAS_LANCEDB**: `LanceDB 舊向量記憶仍保留在 {OLD_ID} namespace 中（孤立，不影響運作）。`
- **If no LanceDB**: *(omit the note)*

---

## Step 6: Restart gateway and verify

```bash
launchctl unload ~/Library/LaunchAgents/ai.openclaw.gateway.plist
launchctl load ~/Library/LaunchAgents/ai.openclaw.gateway.plist
sleep 3
openclaw health
```

Confirm that:
1. `openclaw health` shows NEW_ID in the agents list
2. OLD_ID does not appear in the agents list

---

## Step 7: Final sweep

Do a final grep to surface any remaining functional references to OLD_ID:

```bash
grep -r "${OLD_ID}" "$DATA_DIR" \
  --include="*.json" \
  --include="*.md" \
  --exclude="*.bak" \
  --exclude-dir="sessions" \
  --exclude-dir="sessions-archive" \
  -l
```

For each remaining file, tell the user:
- **Functional files still referencing OLD_ID** — fix them now
- **Acceptable historical files** (obsidian logs, coverage reports, MEMORY.md rename record) — list them so the user knows they're intentionally left

Report a clean summary: what was renamed, what was skipped, and whether the health check passed.
