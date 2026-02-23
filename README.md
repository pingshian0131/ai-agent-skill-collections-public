# AI Agent Skill Collections

一系列可重複使用的 Claude Code Skills，用於擴展 AI Agent 的專業工作流程。

## Skills 清單

### Dev Tools — 開發工具

| Skill | 說明 |
|-------|------|
| [claude-code](./dev-tools/claude-code/) | 透過本機 `claude` CLI 執行程式碼任務，支援重構、除錯、測試與整個 repo 的批次編輯。 |
| [skill-creator](./dev-tools/skill-creator/) | 建立或更新 AgentSkill，提供 skill 設計、結構化、打包的完整流程指南與腳本。 |
| [publish-skill](./dev-tools/publish-skill/) | 將 skill 發佈到 GitHub skill collection repos（private + public），含機敏資料掃描、路徑正規化與清除。 |

### OpenClaw — 平台管理

| Skill | 說明 |
|-------|------|
| [agent-creator](./openclaw/agent-creator/) | 建立新的 OpenClaw Telegram bot agent，包含 workspace 設定、config 更新與 Telegram 綁定。 |
| [openclaw-cron](./openclaw/openclaw-cron/) | 管理 OpenClaw cron 排程任務 — 建立、編輯、除錯與疑難排解，含完整 CLI 指令速查與 JSON schema。 |
| [reset-sessions](./openclaw/reset-sessions/) | 重置 OpenClaw agent 對話 session，可一次清除所有 agent 或指定單一 agent，適合清空上下文重新開始。 |
| [backup](./openclaw/backup/) | 將 `~/.openclaw` 建立帶時戳的 tar.gz 備份，支援列出、清理舊備份，及透過 rclone 上傳至 Google Drive。 |
| [memory-cleanup](./openclaw/memory-cleanup/) | 掃描並清理各 workspace agent 的空白/極簡 session memory 檔案，支援 scan、clean、report 子指令與 cron 排程。 |

### Communication — 通訊

| Skill | 說明 |
|-------|------|
| [email](./communication/email/) | 透過 Gmail App Password 以 SMTP 發送 Email，支援 HTML、附件、CC/BCC 及自訂 SMTP 伺服器。 |
| [twilio-voice](./communication/twilio-voice/) | 透過 Twilio Voice API 撥打電話，支援 zh-TW 語音合成（Google TTS MP3），可用於語音通知與提醒。 |
| [send-imessage](./communication/send-imessage/) | 透過 BlueBubbles REST API 發送 iMessage，Docker agent 可透過 HTTP 呼叫，無需 jq。 |

### Knowledge — 知識整理

| Skill | 說明 |
|-------|------|
| [ddd-summary](./knowledge/ddd-summary/) | 為《Learning Domain-Driven Design》指定章節製作繁中摘要，分成 5 份 .md 檔並推送到 Obsidian vault。 |

## 使用方式

每個 Skill 為獨立目錄，內含 `SKILL.md` 定義其行為。安裝至 Claude Code 環境後，透過 `/skill-name` 指令呼叫。

## 新增 Skill

1. 選擇適當的分類目錄（`dev-tools/`、`openclaw/`、`communication/`、`knowledge/`），或建立新分類。
2. 在分類目錄中建立以 Skill 命名的子目錄。
3. 在目錄中新增 `SKILL.md`，遵循 [Claude Code Skill 格式](https://docs.anthropic.com/en/docs/claude-code)。
4. 更新本 README，將新 Skill 加入對應分類表格。

## License

MIT
