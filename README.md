# AI Agent Skill Collections

一系列可重複使用的 Claude Code Skills，用於擴展 AI Agent 的專業工作流程。

## Skills 清單

| Skill | 說明 |
|-------|------|
| [claude-code](./claude-code/) | 透過本機 `claude` CLI 執行程式碼任務，支援重構、除錯、測試與整個 repo 的批次編輯。 |
| [ddd-summary](./ddd-summary/) | 為《Learning Domain-Driven Design》指定章節製作繁中摘要，分成 5 份 .md 檔並推送到 Obsidian vault。 |
| [email](./email/) | 透過 Gmail App Password 以 SMTP 發送 Email，支援 HTML、附件、CC/BCC 及自訂 SMTP 伺服器。 |
| [skill-creator](./skill-creator/) | 建立或更新 AgentSkill，提供 skill 設計、結構化、打包的完整流程指南與腳本。 |
| [agent-creator](./agent-creator/) | 建立新的 OpenClaw Telegram bot agent，包含 workspace 設定、config 更新與 Telegram 綁定。 |
| [openclaw-cron](./openclaw-cron/) | 管理 OpenClaw cron 排程任務 — 建立、編輯、除錯與疑難排解，含完整 CLI 指令速查與 JSON schema。 |

## 使用方式

每個 Skill 為獨立目錄，內含 `SKILL.md` 定義其行為。安裝至 Claude Code 環境後，透過 `/skill-name` 指令呼叫。

## 新增 Skill

1. 建立以 Skill 命名的新目錄。
2. 在目錄中新增 `SKILL.md`，遵循 [Claude Code Skill 格式](https://docs.anthropic.com/en/docs/claude-code)。
3. 更新本 README，將新 Skill 加入上方表格。

## License

MIT
