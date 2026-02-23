---
name: send-imessage
description: "Send iMessage via BlueBubbles REST API. Use when the user asks to send a message, text someone, 發訊息, 傳 iMessage, or message a contact."
---

# Send iMessage

透過 BlueBubbles Server REST API 發送 iMessage。Docker agent 可透過 HTTP 呼叫。

## 前置需求

- **BlueBubbles Server** 已安裝並運行（https://bluebubbles.app）
- `~/.openclaw/.env` 已設定：
  - `BLUEBUBBLES_URL` — BlueBubbles Server URL（Cloudflare tunnel URL 會定期變動，需確認最新值）
  - `BLUEBUBBLES_PASSWORD` — API 密碼
- `curl` 已安裝

## 發送流程

### Step 1：確定收件人

**直接請使用者提供電話號碼或 email。** 不做自動聯絡人查詢。

- 若使用者給了名字/暱稱但沒給電話或 email，請使用者提供收件人的電話號碼或 email 地址
- 若使用者直接給了電話號碼或 email，直接使用

### Step 2：直接發送訊息

收到使用者的發送請求後，**不需要再次確認，直接執行發送：**

```bash
bash {baseDir}/scripts/send_imessage.sh "<收件人電話或email>" "<訊息內容>"
```

- 收件人格式：電話號碼（如 `+XXXXXXXXXXX`）或 email（如 `you@example.com`）
- 成功回傳 `OK: iMessage sent to ...`
- 失敗回傳 `ERROR: ...` 並附錯誤訊息

回報發送結果給使用者。

## 錯誤處理

| 錯誤情境 | 處理方式 |
|---------|---------|
| `ERROR: BLUEBUBBLES_URL not set` | 提醒使用者在 `~/.openclaw/.env` 設定 BlueBubbles URL |
| `ERROR: BLUEBUBBLES_PASSWORD not set` | 提醒使用者在 `~/.openclaw/.env` 設定 BlueBubbles 密碼 |
| `ERROR: HTTP 401` | BlueBubbles 密碼錯誤 |
| `ERROR: curl failed (exit code 7)` | BlueBubbles Server 未啟動或 URL 已失效（Cloudflare tunnel 需更新） |
| `ERROR: curl failed` | 網路問題或 BlueBubbles Server 無法連線 |
| `ERROR: HTTP 4xx/5xx` | 顯示 API 回傳的錯誤訊息 |

## 限制

- 僅支援**純文字**訊息（不支援圖片、附件）
- 需要 BlueBubbles Server 運行中
- BLUEBUBBLES_URL 若使用 Cloudflare tunnel，URL 會定期變動，連線失敗時需先確認 URL 是否最新
- 使用 AppleScript method 發送，收件人需已存在於 iMessage 對話紀錄中（如需發送至全新對話，需改用 `private-api` method 並停用 SIP）

## Resources

### scripts/

- `send_imessage.sh` — 透過 curl 呼叫 BlueBubbles REST API 發送 iMessage（無需 jq）
