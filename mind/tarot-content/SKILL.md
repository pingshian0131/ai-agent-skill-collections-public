---
name: tarot-content
description: 個人塔羅占卜與星象解讀。支援每日一牌、三牌陣（挑戰/指引/祝福）、關係牌陣，結合即時天象資料提供深度解讀與反思引導。Use when asked to "塔羅占卜", "抽牌", "今日塔羅", "tarot reading", "抽一張牌", "三牌陣", or "幫我算一下".
---

# 個人塔羅占卜

為使用者提供個人化的塔羅牌解讀，結合即時星象資料，作為自我反思與陪伴的工具。

> Forked from [ClawHub: alexyuui/tarot-content](https://clawhub.ai/alexyuui/tarot-content) (MIT License)，改為個人占卜用途。

## 占卜流程

### Step 1：了解問題

先詢問使用者：
- 想問什麼方向？（感情、事業、人際、自我成長、一般指引）
- 有沒有具體的情境或困惑？
- 如果使用者沒有特定問題，預設為「今日能量指引」

### Step 2：選擇牌陣

根據問題推薦牌陣，或讓使用者選擇：

| 牌陣 | 張數 | 適用情境 |
|------|------|---------|
| 每日一牌 | 1 | 今日能量、快速指引 |
| 挑戰 / 指引 / 祝福 | 3 | 通用問題、每週回顧 |
| 關係牌陣 | 5 | 你 / 對方 / 關係現況 / 挑戰 / 建議 |

### Step 3：抽牌與解讀

1. 隨機抽取對應張數的塔羅牌（含正逆位）
2. 查詢 `references/tarot-cards.md` 取得牌義關鍵字
3. 結合使用者的問題情境，給出個人化解讀
4. 如果 `USER.md` 中有使用者的星座資訊，將其納入解讀脈絡

### Step 4：星象脈絡（選用）

使用 `scripts/ephemeris_helper.py` 查詢當前行星位置與相位，為解讀加上天象背景：

```python
import swisseph as swe
from datetime import datetime

def get_planet_position(planet_id, dt):
    """Get planet longitude in zodiac."""
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60)
    pos = swe.calc_ut(jd, planet_id)[0]
    longitude = pos[0]
    sign_num = int(longitude / 30)
    degree = longitude % 30
    signs = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo',
             'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
    return signs[sign_num], degree

# Planet IDs: SUN=0, MOON=1, MERCURY=2, VENUS=3, MARS=4,
#             JUPITER=5, SATURN=6, URANUS=7, NEPTUNE=8, PLUTO=9
```

### Step 5：反思提問

每次解讀結尾，提供 1-2 個引導反思的問題，幫助使用者深入思考，例如：
- 「這張牌提到的『放手』，在你目前的生活中，有什麼是你一直抓著不放的？」
- 「如果這個建議是對的，你明天可以做的最小一步是什麼？」

## 三牌陣框架（挑戰 / 指引 / 祝福）

| 位置 | 含義 | 語氣 |
|------|------|------|
| 挑戰 | 目前需要留意的 | 誠實但不嚇人 |
| 指引 | 可以聚焦的方向 | 具體可行的建議 |
| 祝福 | 正在到來的 | 鼓勵、溫暖 |

## 關係牌陣框架

| 位置 | 含義 |
|------|------|
| 1 — 你 | 你在這段關係中的狀態 |
| 2 — 對方 | 對方目前的能量 |
| 3 — 關係現況 | 兩人之間的動態 |
| 4 — 挑戰 | 需要面對的課題 |
| 5 — 建議 | 可以嘗試的方向 |

## 解讀風格

- **像朋友聊天** — 「你最近是不是覺得卡卡的？」而非「牌面顯示停滯之象」
- **用生活場景** — 「那個一直想開口但沒說的事？也許是時候了」
- **不恐嚇** — 即使抽到塔、死神、惡魔，都給建設性的解讀
- **不老套** — 禁止「宇宙自有安排」、「一切都是最好的安排」、「相信過程」
- **尊重自主** — 解讀是參考，選擇永遠在使用者手上

## 敏感內容守則

- 不做醫療診斷或健康預測（「這張牌說你會康復」）
- 不做具體財務建議（「現在投資，木星說的」）
- 不做恐嚇式預言（「前方有危險」、「死神牌代表...」）
- 塔羅是反思工具，不是預測未來的水晶球
