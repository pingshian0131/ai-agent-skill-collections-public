# AI Agent Skill Collections

一系列可重複使用的 Claude Code Skills，用於擴展 AI Agent 的專業工作流程。

## Skills 清單

### Dev Tools — 開發工具

| Skill | 說明 |
|-------|------|
| [claude-code](./dev-tools/claude-code/) | 透過本機 `claude` CLI 執行程式碼任務，支援重構、除錯、測試與整個 repo 的批次編輯。 |
| [skill-creator](./dev-tools/skill-creator/) | 建立或更新 AgentSkill，提供 skill 設計、結構化、打包的完整流程指南與腳本。 |
| [publish-skill](./dev-tools/publish-skill/) | 將 skill 發佈到 GitHub skill collection repos（private + public），含機敏資料掃描、路徑正規化與清除。 |
| [doc-commit-push](./dev-tools/doc-commit-push/) | 分析 git repo 的近期變更，自動更新 CLAUDE.md 與 README.md 後 commit & push。 |
| [install-skill](./dev-tools/install-skill/) | 從 GitHub 或 ClawHub URL 一鍵安裝第三方 AgentSkill，含 7 大類別安全掃描與風險閘門。 |
| [self-improving-agent](./dev-tools/self-improving-agent/) | 記錄學習、錯誤與修正以實現持續改進，支援 OpenClaw hook 自動觸發，學習可晉升至專案 memory。 |
| [explain-skill](./dev-tools/explain-skill/) | 解釋已安裝 skill 的功能、觸發條件與安全性，含腳本自動偵測第三方 skill 的風險模式。 |
| [agent-browser-core](./dev-tools/agent-browser-core/) | agent-browser CLI（Rust + Node.js fallback）的操作手冊，提供 AI-friendly 網頁自動化的 snapshot、refs 與結構化指令。 |

### OpenClaw — 平台管理

| Skill | 說明 |
|-------|------|
| [agent-creator](./openclaw/agent-creator/) | 建立新的 OpenClaw Telegram bot agent，包含 workspace 設定、config 更新與 Telegram 綁定。 |
| [openclaw-cron](./openclaw/openclaw-cron/) | 管理 OpenClaw cron 排程任務 — 建立、編輯、除錯與疑難排解，含完整 CLI 指令速查與 JSON schema。 |
| [openclaw-rebuild](./openclaw/openclaw-rebuild/) | 更新 OpenClaw 至最新穩定 release — 追蹤 release tag、重建 Docker image 並重啟 containers，含自動 cron 排程。 |
| [reset-sessions](./openclaw/reset-sessions/) | 重置 OpenClaw agent 對話 session，可一次清除所有 agent 或指定單一 agent，適合清空上下文重新開始。 |
| [backup](./openclaw/backup/) | 備份 `~/.openclaw-personal` 及 `~/.openclaw-work` 為帶時戳的 tar.gz，支援列出、清理舊備份，及透過 rclone 上傳至 Google Drive。 |
| [memory-cleanup](./openclaw/memory-cleanup/) | 掃描並清理各 workspace agent 的空白/極簡 session memory 檔案，支援 scan、clean、report 子指令與 cron 排程。 |
| [one-time-reminder-cron](./openclaw/one-time-reminder-cron/) | 透過編輯 cron registry 建立一次性提醒，支援建立/更新、停用與重新命名 cron job。 |
| [cron-job-creator](./openclaw/cron-job-creator/) | 直接編輯 cron registry 管理排程任務 — 建立、更新、刪除、啟用/停用、重新命名與複製 cron job。 |
| [docker-cleanup](./openclaw/docker-cleanup/) | 清理 `openclaw:local` rebuild 後產生的 dangling Docker images，保留最新 7 個，含 cron 排程自動執行。 |

### Communication — 通訊

| Skill | 說明 |
|-------|------|
| [email](./communication/email/) | 透過 Gmail App Password 以 SMTP 發送 Email，支援 HTML、附件、CC/BCC 及自訂 SMTP 伺服器。 |
| [twilio-voice](./communication/twilio-voice/) | 透過 Twilio Voice API 撥打電話，支援 zh-TW 語音合成（Google TTS MP3），可用於語音通知與提醒。 |
| [send-imessage](./communication/send-imessage/) | 透過 BlueBubbles REST API 發送 iMessage，Docker agent 可透過 HTTP 呼叫，無需 jq。 |

### Mind — 身心靈 / 內容創作

| Skill | 說明 | 來源 |
|-------|------|------|
| [tarot-content](./mind/tarot-content/) | 個人塔羅占卜與星象解讀 — 每日一牌、三牌陣、關係牌陣，結合即時天象。Fork 自 [alexyuui/tarot-content](https://clawhub.ai/alexyuui/tarot-content)，改為個人占卜用途。 | Fork from ClawHub |
| [mingli](./mind/mingli/) | 多系統命理技能 — 西洋星盤（Kerykeion）、八字四柱、數字學、易經，支援每日 Telegram 運勢推送。 | [ClawHub: hiehoo/mingli](https://github.com/openclaw/skills/tree/main/skills/hiehoo/mingli) |
| [meihua-yishu](./mind/meihua-yishu/) | 梅花易數（Plum Blossom I Ching）專業占卜系統 — 時間起卦、數字起卦、測字，含爻辭解讀與策略建議。 | [GitHub: muyen/meihua-yishu](https://github.com/muyen/meihua-yishu) |
| [transit-chart](./mind/transit-chart/) | 行星 Transit 盤產生器 — 用 Kerykeion (Swiss Ephemeris) 本地計算當天行星位置，支援 Transit+Natal 雙輪盤 PNG 圖片輸出。 | 自製 |

### Knowledge — 知識整理

| Skill | 說明 |
|-------|------|
| [ddd-summary](./knowledge/ddd-summary/) | 為《Learning Domain-Driven Design》指定章節製作繁中摘要，分成 5 份 .md 檔並推送到 Obsidian vault。 |
| [summarize](./knowledge/summarize/) | 使用 summarize CLI 一鍵摘要 URL、本地檔案（PDF、圖片、音視頻）及 YouTube 連結。 |
| [ontology](./knowledge/ontology/) | Typed knowledge graph 結構化 agent 記憶 — 支援 entity CRUD、關聯查詢、schema 驗證與跨 skill 狀態共享。 |

## 使用方式

每個 Skill 為獨立目錄，內含 `SKILL.md` 定義其行為。安裝至 Claude Code 環境後，透過 `/skill-name` 指令呼叫。

## 新增 Skill

1. 選擇適當的分類目錄（`dev-tools/`、`openclaw/`、`communication/`、`knowledge/`、`mind/`），或建立新分類。
2. 在分類目錄中建立以 Skill 命名的子目錄。
3. 在目錄中新增 `SKILL.md`，遵循 [Claude Code Skill 格式](https://docs.anthropic.com/en/docs/claude-code)。
4. 更新本 README，將新 Skill 加入對應分類表格。

## 第三方 Skills

部分 skills 來自外部開源社群，以 `_meta.json` 或 SKILL.md frontmatter 記錄原始出處。

| Skill | 原始作者 | 來源 | 來源連結 |
|-------|---------|------|---------|
| tarot-content | alexyuui | ClawHub | [clawhub.ai/alexyuui/tarot-content](https://clawhub.ai/alexyuui/tarot-content) |
| mingli | hiehoo | ClawHub | [github.com/openclaw/skills/tree/main/skills/hiehoo/mingli](https://github.com/openclaw/skills/tree/main/skills/hiehoo/mingli) |
| meihua-yishu | muyen | GitHub | [github.com/muyen/meihua-yishu](https://github.com/muyen/meihua-yishu) |
| summarize | steipete | GitHub | [github.com/openclaw/skills/tree/main/skills/steipete/summarize](https://github.com/openclaw/skills/tree/main/skills/steipete/summarize) |
| self-improving-agent | pskoett | GitHub | [github.com/openclaw/skills/tree/main/skills/pskoett/self-improving-agent](https://github.com/openclaw/skills/tree/main/skills/pskoett/self-improving-agent) |
| ontology | oswalpalash | ClawHub | [github.com/openclaw/skills/tree/main/skills/oswalpalash/ontology](https://github.com/openclaw/skills/tree/main/skills/oswalpalash/ontology) |
| agent-browser-core | codedao12 | ClawHub | [github.com/openclaw/skills/tree/main/skills/codedao12/agent-browser-core](https://github.com/openclaw/skills/tree/main/skills/codedao12/agent-browser-core) |

## License

本 repo 自有 skills 以 MIT License 發佈。

第三方 skills 遵循其原始授權條款：
- ClawHub skills（`openclaw/skills` repo）：[MIT License](https://github.com/openclaw/skills/blob/main/LICENSE)
- meihua-yishu：[CC BY-NC-SA 4.0](https://github.com/muyen/meihua-yishu/blob/main/LICENSE)
