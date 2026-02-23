---
name: send-imessage
description: "Send iMessage via BlueBubbles REST API. Use when the user asks to send a message, text someone, 發訊息, 傳 iMessage, or message a contact."
---

# Send iMessage

透過 BlueBubbles Server REST API 發送 iMessage。支援以暱稱/姓名查詢 macOS 通訊錄聯絡人，或直接指定電話號碼/email。

## 前置需求

- **BlueBubbles Server** 已安裝並運行（https://bluebubbles.app）
- 使用 AppleScript method（不需停用 SIP，不需 Private API helper）
- `{baseDir}/.env` 已設定：
  - `BLUEBUBBLES_URL` — BlueBubbles Server URL（預設 `http://localhost:1234`）
  - `BLUEBUBBLES_PASSWORD` — API 密碼
- `jq` 已安裝（`brew install jq`）

## 發送流程

### Step 1：確定收件人

**情境 A — 使用者給了名字/暱稱：**

執行聯絡人查詢：

```bash
bash {baseDir}/.claude/skills/send-imessage/scripts/lookup_contact.sh "<搜尋詞>"
```

輸出格式（每行一筆）：`姓名 | 暱稱 | 電話1,電話2 | email1,email2`

- 若回傳 `NO_MATCH`，告知使用者找不到聯絡人，請提供電話號碼或 email
- 若回傳多筆結果，列出所有匹配的聯絡人讓使用者選擇

**情境 B — 使用者直接給了電話號碼或 email：**

直接使用該號碼/email 作為收件人，跳過查詢步驟。

### Step 2：顯示確認提示

**在發送之前，務必向使用者確認。** 顯示格式：

```
準備發送 iMessage：
  收件人：{聯絡人姓名} ({電話號碼或 email})
  內容：「{訊息內容}」
確認發送？
```

等待使用者明確確認後才繼續。

### Step 3：發送訊息

使用者確認後，執行：

```bash
bash {baseDir}/.claude/skills/send-imessage/scripts/send_imessage.sh "<收件人電話或email>" "<訊息內容>"
```

- 收件人格式：電話號碼（如 `+XXXXXXXXXXX`）或 email（如 `user@example.com`）
- 成功回傳 `OK: iMessage sent to ...`
- 失敗回傳 `ERROR: HTTP ...` 並附錯誤訊息

回報發送結果給使用者。

## 多筆結果處理

當 `lookup_contact.sh` 回傳多筆匹配時：

1. 列出所有匹配的聯絡人（編號 + 姓名 + 電話/email）
2. 請使用者選擇要發送給哪一位
3. 使用者選擇後，進入 Step 2 確認流程

## 錯誤處理

| 錯誤情境 | 處理方式 |
|---------|---------|
| `NO_MATCH` — 找不到聯絡人 | 告知使用者，請提供電話號碼或 email |
| `ERROR: BLUEBUBBLES_URL not set` | 提醒使用者在 `{baseDir}/.env` 設定 BlueBubbles URL |
| `ERROR: BLUEBUBBLES_PASSWORD not set` | 提醒使用者在 `{baseDir}/.env` 設定 BlueBubbles 密碼 |
| `ERROR: HTTP 401` | BlueBubbles 密碼錯誤 |
| `ERROR: HTTP 000` 或連線失敗 | BlueBubbles Server 未啟動，提醒使用者啟動 |
| `ERROR: HTTP 4xx/5xx` | 顯示 API 回傳的錯誤訊息 |

## 限制

- 僅支援**純文字**訊息（不支援圖片、附件）
- 需要 BlueBubbles Server 在本機運行中
- 聯絡人查詢依賴 macOS Contacts.app
- 使用 AppleScript method，收件人需已存在於 iMessage 對話紀錄中（如需發送至全新對話，需改用 `private-api` method 並停用 SIP）

## Resources

### scripts/

- `send_imessage.sh` — 透過 curl 呼叫 BlueBubbles REST API 發送 iMessage
- `lookup_contact.sh` — 透過 AppleScript 查詢 macOS Contacts.app 聯絡人
