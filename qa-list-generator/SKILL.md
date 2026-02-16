---
name: qa-list-generator
description: 當使用者提供任意 function、method 或 class，分析其邏輯並判斷測試方式，產生可實際執行的 QA 驗證方案。適用於 Django 專案。
---

# QA List Generator

## Overview

分析使用者指定的 function、method 或 class，**判斷該程式碼的測試入口**，產生可實際操作的 QA 驗證方案。

## Workflow

### Step 1: 定位目標程式碼

根據使用者提供的 function/method/class 名稱，使用 Grep 和 Read 工具定位完整的程式碼實作。

### Step 2: 追蹤呼叫鏈，判斷測試方式

**關鍵步驟：** 分析目標程式碼的上層呼叫者，判斷屬於哪種類型：

1. **追蹤呼叫鏈** — 用 Grep 搜尋誰呼叫了這個 function，一路往上追到最終入口（view / URL / admin action / Celery task / management command）
2. **判斷測試類型**：

| 類型 | 判斷條件 | 測試方式 |
|------|----------|----------|
| **有 URL 的頁面/API** | 呼叫鏈最終到達 view，且有對應的 URL pattern | 產生手動測試清單，附上完整 URL 和操作步驟 |
| **Django Admin action** | 透過 admin.py 的 action 觸發 | 產生手動測試清單，附上 admin 頁面路徑和操作步驟 |
| **Celery 排程任務** | 呼叫鏈最終到達 `@shared_task` / `@app.task` | 產生 Django shell 驗證指令 |
| **Management command** | 呼叫鏈到達 `BaseCommand` | 產生 manage.py 指令範例 |
| **純內部方法** | 無直接的外部觸發入口 | 產生 Django shell 驗證指令 |

### Step 3: 分析查詢邏輯

深入分析目標程式碼的以下面向：

1. **資料來源** — 查詢哪些 Model/Table
2. **篩選條件 (Filter)** — `.filter()`、`Q()` 條件
3. **排除條件 (Exclude)** — `.exclude()` 條件
4. **參數影響** — 各參數如何影響查詢行為
5. **邊界條件** — assert、日期修正、None 處理等
6. **業務邏輯** — 從程式碼註解和命名推斷的業務意圖

### Step 4: 產生報告

根據 Step 2 判斷的測試類型，使用對應的報告格式。

---

## 報告格式 A：有 URL / Admin 頁面（可手動測試）

適用於有前端頁面可操作的功能。

```markdown
# QA List: [function/method 名稱]

## 概述
- **目標程式碼位置**: `app/module.py:行號`
- **業務用途**: 一句話描述
- **測試 URL**: `http://localhost:8080/admin/...` 或 `/api/...`
- **操作路徑**: Admin > 某頁面 > 某按鈕

## 前置條件
- 需要的測試資料或狀態設定
- 相關的 Django shell 資料準備指令（如需要）

## QA 測試項目

### 正向測試
- [ ] **QA-001**: [具體操作步驟] — 預期結果: [頁面上可觀察到的結果]

### 邊界條件
- [ ] **QA-101**: [具體操作步驟] — 預期結果: [預期]

### 負向測試
- [ ] **QA-201**: [具體操作步驟] — 預期結果: [預期]
```

## 報告格式 B：Celery Task / 內部方法 / Management Command（無 UI）

適用於沒有前端頁面的背景任務或底層方法。

```markdown
# QA 驗證: [function/method 名稱]

## 概述
- **目標程式碼位置**: `app/module.py:行號`
- **業務用途**: 一句話描述
- **呼叫鏈**: task/command → service → 目標方法
- **測試方式**: Django shell / manage.py command

## 篩選條件摘要

| # | 條件 | 說明 |
|---|------|------|
| 1 | condition_a=True | 業務說明 |

## 參數行為

| 參數 | 型別 | 預設值 | 影響 |
|------|------|--------|------|
| param_a | date | 必填 | 說明 |

## 驗證指令

### 基本驗證
\```python
# pipenv run python manage.py shell
from xxx.models import XXX

# 驗證描述
result = XXX.objects.method(...)
print(f"筆數: {result.count()}")
for item in result[:5]:
    print(f"  {item}")
\```

### 邊界情境驗證
\```python
# 情境描述
result = XXX.objects.method(邊界參數=...)
# 預期: ...
\```

### 負向驗證
\```python
# 確認不該出現的資料
# 情境描述
result = XXX.objects.method(...)
# 預期: 不包含 ...
\```

## 注意事項
- 是否會寫入資料（唯讀 vs 有副作用）
- 開發環境連 PRD DB 的風險提醒
```

### Step 5: 輸出報告

將報告寫入 `.claude_output/qa_list_[function名稱]_[日期時間].md`。

日期時間格式：`YYYYMMDD_HHmm`，例如 `qa_list_get_in_stock_logistics_products_20241119_1430.md`。

## 測試項目產生原則

- **只產生可實際執行的測試項目** — 每個項目都要有明確的操作方式（URL 操作步驟或 shell 指令）
- **精簡** — 只列有意義的測試情境，不需要把每個 filter 條件都展開成獨立項目
- **合併相關條件** — 多個 filter 條件如果服務同一個業務目的，合併為一個測試情境
- **區分唯讀 vs 副作用** — 明確標示哪些驗證會寫入資料，提醒注意 PRD DB 風險
