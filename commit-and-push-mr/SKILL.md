---
name: commit-and-push-mr
description: Git commit、push 並發 MR。自動分析變更產生語意化 commit message，push 到遠端分支，並用 glab 建立 Merge Request。
---

# Git Commit, Push & MR Agent

當用戶需要 commit 和 push 變更時，此 skill 會自動分析變更並產生適當的 commit message。
也支援在 push 後建立 GitLab Merge Request。

## 使用方式

```
/commit [可選的額外描述或指定 commit message]
/commit mr  — commit + push 後自動發 MR
/commit --mr — 同上
```

- 不帶參數：自動分析變更產生 commit message，commit 並 push
- 帶 `mr`：commit + push 後額外建立 Merge Request
- 帶其他參數：使用參數作為 commit message 或作為額外描述補充

## User Input

```text
$ARGUMENTS
```

如果上方有用戶提供的輸入，應優先使用該內容作為 commit message 或參考。

## 執行流程

### 0. 重要：執行前必須確認

**在執行任何 git 操作之前，必須先向用戶展示以下資訊並取得確認：**

1. 列出所有將被 commit 的檔案
2. 顯示建議的 commit message
3. 確認將 push 到哪個 remote branch
4. **使用 `AskUserQuestion` 工具詢問用戶是否確認執行**

```
範例確認訊息：

📋 即將執行 Commit & Push

Branch: feature/xxx → origin/feature/xxx

將 commit 的檔案：
  M  myproject/orders/services.py
  M  myproject/orders/tests.py
  A  myproject/orders/utils.py

建議的 Commit Message:
  feat(orders): 新增訂單處理功能

是否確認執行？
```

**⚠️ 未經用戶確認，絕對不可執行 git commit 或 git push。**

---

### 1. 檢查目前狀態

```bash
# 查看目前分支
git branch --show-current

# 查看所有變更（staged + unstaged + untracked）
git status

# 查看 staged 的變更
git diff --cached --stat

# 查看 unstaged 的變更
git diff --stat

# 列出 untracked 檔案
git ls-files --others --exclude-standard
```

**如果沒有任何變更，告知用戶並結束。**

### 2. 分析變更內容

#### 2.1 查看詳細變更

```bash
# 查看 staged 的詳細 diff
git diff --cached

# 查看 unstaged 的詳細 diff（如果有的話）
git diff
```

#### 2.2 參考近期 commit 風格

```bash
# 查看最近 5 個 commit 的風格
git log --oneline -5
```

### 3. 產生 Commit Message

#### 3.1 Commit Message 格式

使用 Conventional Commits 風格：

```
<type>(<scope>): <subject>

<body>
```

**Type 類型：**
| Type | 使用情境 |
|------|---------|
| `feat` | 新功能 |
| `fix` | Bug 修復 |
| `refactor` | 重構（不影響功能） |
| `docs` | 文件變更 |
| `style` | 格式調整（不影響程式邏輯） |
| `test` | 測試相關 |
| `chore` | 雜項（設定、相依套件等） |

**Scope（可選）：** 影響的 Django app 或模組名稱

**Subject 規則：**
- 使用中文或英文（參考專案既有風格）
- 簡潔描述變更內容
- 不超過 50 字元

**Body（可選）：**
- 詳細說明變更原因
- 列出主要修改項目

#### 3.2 範例

```
feat(gift_promotion): 新增滿額贈計算邏輯

- 新增 GiftPromotionService.calculate_eligible_gifts()
- 支援多門檻贈品規則
- 整合 Shopify 訂單資料
```

```
fix(orders): 修正訂單狀態更新錯誤

修復當訂單取消時狀態未正確更新的問題
```

### 4. 確認並執行 Commit

**⚠️ 必須先完成「步驟 0」的用戶確認後，才能執行以下操作。**

#### 4.1 Stage 所有變更（如果需要）

```bash
# 如果有 unstaged 或 untracked 檔案，詢問用戶是否要一起 commit
# 用戶確認後執行：
git add .

# 或只加入特定檔案
git add <specific_files>
```

#### 4.2 執行 Commit

```bash
git commit -m "$(cat <<'EOF'
<commit message>

Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

**重要：**
- 如果 commit 因為 pre-commit hook 失敗，修正問題後建立**新的 commit**，不要使用 `--amend`
- 不要使用 `--no-verify` 跳過 hooks

### 5. Push 到 Remote

**⚠️ 必須在用戶確認後才能執行 push。**

#### 5.1 檢查 Remote 狀態

```bash
# 檢查是否有設定 upstream
git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null

# 如果沒有 upstream，需要設定
git push -u origin $(git branch --show-current)
```

#### 5.2 執行 Push

```bash
# 一般 push
git push

# 如果是新分支
git push -u origin $(git branch --show-current)
```

#### 5.3 Push 安全規則

- **絕對不要** 使用 `--force` 除非用戶明確要求
- **絕對不要** force push 到 `master` 或 `main` 分支
- 如果 push 失敗（因為 remote 有新 commit），告知用戶需要先 pull

### 6. 確認結果

```bash
# 確認 commit 已建立
git log --oneline -1

# 確認已 push 到 remote
git status
```

## 處理特殊情況

### 衝突或 Push 失敗

如果 push 失敗，告知用戶：

```
Push 失敗，remote 有新的 commit。建議執行：
1. git pull --rebase
2. 解決衝突（如果有）
3. 再次 push

```

### 敏感檔案警告

如果偵測到以下檔案被 staged，發出警告並詢問用戶：

- `.env*`
- `*credentials*`
- `*secret*`
- `*.pem`
- `*.key`

### Pre-commit Hook 失敗

如果 commit 被 pre-commit hook 拒絕：

1. 顯示 hook 的錯誤訊息
2. 嘗試修正問題（如格式化、lint 錯誤）
3. 重新 commit（建立新的 commit，不使用 --amend）

## 輸出摘要

完成後簡要報告：

```
✅ Commit 完成
- Branch: feature/xxx
- Commit: abc1234 - feat(app): commit message
- Pushed to: origin/feature/xxx
```

如果有任何問題：

```
⚠️ Commit 完成但 Push 失敗
- Branch: feature/xxx
- Commit: abc1234 - feat(app): commit message
- 原因: remote 有新的 commit，請先執行 git pull
```

---

## Merge Request（MR）功能

當用戶指定 `mr` 參數（如 `/commit mr`），在 commit + push 完成後，額外建立 GitLab Merge Request。

### 7. 建立 Merge Request

#### 7.1 判斷是否需要發 MR

以下情況觸發 MR 流程：
- 用戶輸入包含 `mr` 或 `--mr`
- 用戶明確要求「發 MR」、「建立 MR」、「create MR」等

#### 7.2 收集 MR 資訊

**使用 `AskUserQuestion` 詢問用戶：**

1. **Asana 任務連結** — 詢問是否有相關的 Asana 任務連結，沒有則留空
2. **目標分支（Target Branch）** — 預設為 `master`，詢問用戶是否要改為其他分支

#### 7.3 分析變更產生 MR 內容

根據 commit 歷史和 diff 自動產生 MR 描述：

```bash
# 取得目前分支與 target branch 的差異
git log --oneline master..HEAD
git diff master...HEAD --stat
```

#### 7.4 MR 描述模板

```markdown
## 描述

<!-- 根據 commit 內容和 diff 自動產生的變更說明 -->
- 變更摘要第一點
- 變更摘要第二點

## 相關任務或問題

Asana 任務連結：<用戶提供的連結或留空>

## 測試結果

<!-- 列出已執行的測試或測試建議 -->
- [ ] 單元測試通過
- [ ] 手動測試通過

## 相關參考

<!-- 相關文件、PR、或參考連結 -->
- 相關 commit: <commit hash list>
```

#### 7.5 確認並建立 MR

**⚠️ 必須先向用戶展示 MR 標題和描述，取得確認後才能建立。**

使用 `AskUserQuestion` 展示 MR 預覽並請用戶確認。

#### 7.6 執行 glab 建立 MR

```bash
# 建立 MR
glab mr create \
  --title "<MR 標題>" \
  --description "$(cat <<'EOF'
<MR 描述內容>
EOF
)" \
  --target-branch <target_branch> \
  --remove-source-branch
```

**MR 標題規則：**
- 使用與 commit message 相同的 Conventional Commits 風格
- 如果有多個 commit，產生一個總結性標題
- 不超過 70 字元

#### 7.7 MR 安全規則

- **絕對不要**在用戶未確認前建立 MR
- 如果 `glab` 未安裝，告知用戶需要先安裝 `glab`（`brew install glab`）
- 如果未登入 GitLab，提示用戶執行 `glab auth login`

### 8. MR 輸出摘要

MR 建立成功：

```
✅ Commit & MR 完成
- Branch: feature/xxx → master
- Commit: abc1234 - feat(app): commit message
- Pushed to: origin/feature/xxx
- MR: !123 - feat(app): commit message
- MR URL: https://gitlab.com/xxx/xxx/-/merge_requests/123
```

MR 建立失敗：

```
⚠️ Commit & Push 完成，但 MR 建立失敗
- Branch: feature/xxx
- Commit: abc1234 - feat(app): commit message
- Pushed to: origin/feature/xxx
- MR 錯誤: <錯誤訊息>
- 請手動執行: glab mr create --target-branch master
```
