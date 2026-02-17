---
name: agent-creator
description: Create new OpenClaw Telegram bot agents with workspace, config, and Telegram binding. Use when the user wants to add a new agent, create a new bot, set up a new AI assistant, or onboard a new character to the OpenClaw platform.
---

# Agent Creator

Create a fully configured OpenClaw agent with workspace files, runtime directories, config entries, and Telegram binding.

## Required Information

Gather from the user before starting:

1. **Agent ID** — lowercase, hyphen-case (e.g., `secretary`, `code-review`)
2. **Display name** — character name in Chinese/English (e.g., 秘書紫苑)
3. **Creature/role** — what they are (e.g., 鬼人族秘書)
4. **Emoji** — representative emoji
5. **Personality** — vibe, communication style, core principles
6. **Model** — which LLM model to use (see [config-reference.md](references/config-reference.md) for available models)
7. **Telegram bot token** — from @BotFather (ask user to provide or create one)

Optional: specialty, relationship to other agents, delegation rules.

## Workflow

### 1. Create Directories

```
~/.openclaw/workspace-<agent_id>/
  ├── memory/
  └── skills/
~/.openclaw/agents/<agent_id>/
  ├── agent/
  └── sessions/
```

### 2. Create Workspace Files

Use templates from [workspace-templates.md](references/workspace-templates.md). Create all of:

- `IDENTITY.md` — name, creature, vibe, emoji, self-intro
- `SOUL.md` — core principles, boundaries, communication style
- `USER.md` — copy from existing agent (user info is shared)
- `TOOLS.md` — minimal template
- `MEMORY.md` — initialized empty
- `AGENTS.md` — copy from `~/.openclaw/workspace/AGENTS.md` as base, customize if agent has coordination role

Write personality content in Traditional Chinese, matching existing agents' tone.

### 3. Update openclaw.json

See [config-reference.md](references/config-reference.md) for exact JSON structure. Add three entries:

1. **`agents.list`** — append new agent object
2. **`channels.telegram.accounts`** — add account with bot token
3. **`bindings`** — map agent to Telegram account

### 4. Initialize Git

```bash
cd ~/.openclaw/workspace-<agent_id> && git init && git add -A && git commit -m "Initialize <agent_id> agent workspace (<display_name>)"
```

### 5. Activate

```bash
openclaw gateway restart
sleep 5 && openclaw health
```

Verify the new agent appears in the health output agents list and Telegram shows `ok`.

## Notes

- All agents in this system are themed after characters from "That Time I Got Reincarnated as a Slime" (轉生史萊姆). Suggest fitting characters if the user hasn't chosen one, but respect their preference.
- USER.md content is identical across all agents — copy from any existing workspace.
- AGENTS.md base template lives at `~/.openclaw/workspace/AGENTS.md`.
- Never expose bot tokens, API keys, or auth tokens in output.
