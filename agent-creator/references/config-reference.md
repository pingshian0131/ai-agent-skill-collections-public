# openclaw.json Config Reference for Agent Creation

## Paths

- Config: `~/.openclaw/openclaw.json`
- Workspaces: `~/.openclaw/workspace-<agent_id>/`
- Agent runtime: `~/.openclaw/agents/<agent_id>/`
  - `agent/` — auth profiles
  - `sessions/` — conversation session logs

## agents.list Entry

Add to `agents.list` array:

```json
{
  "id": "<agent_id>",
  "name": "<agent_id>",
  "workspace": "~/.openclaw/workspace-<agent_id>",
  "agentDir": "~/.openclaw/agents/<agent_id>/agent",
  "model": "<provider>/<model_name>"
}
```

## channels.telegram.accounts Entry

Add to `channels.telegram.accounts` object:

```json
"<agent_id>": {
  "dmPolicy": "pairing",
  "botToken": "<telegram_bot_token>",
  "groupPolicy": "allowlist",
  "streamMode": "partial"
}
```

## bindings Entry

Add to `bindings` array:

```json
{
  "agentId": "<agent_id>",
  "match": {
    "channel": "telegram",
    "accountId": "<agent_id>"
  }
}
```

## Available Models

| Provider | Model ID | Alias |
|----------|----------|-------|
| `google` | `google/gemini-2.5-flash` | Flash |
| `google` | `google/gemini-3-pro-preview` | Gemini3 |
| `openai-codex` | `openai-codex/gpt-5.3-codex` | GPT53 |
| `openai-codex` | `openai-codex/gpt-5.1-codex` | GPT51C |
| `anthropic` | `anthropic/claude-opus-4-6` | Opus |
| `anthropic` | `anthropic/claude-sonnet-4-5-20250929` | Sonnet |

## Existing Agents (for reference)

| ID | Name | Model |
|----|------|-------|
| `main` | 利姆路·坦派斯特 | google/gemini-2.5-flash (default) |
| `research` | 智慧之王拉婓爾 | openai-codex/gpt-5.3-codex |
| `craftsman` | 工匠凱金 | anthropic/claude-sonnet-4-5-20250929 |
| `diablo` | 原初之黑迪亞布羅 | anthropic/claude-sonnet-4-5-20250929 |
| `secretary` | 秘書紫苑 | openai-codex/gpt-5.3-codex |

## Post-Creation

```bash
openclaw gateway restart
sleep 5 && openclaw health
```
