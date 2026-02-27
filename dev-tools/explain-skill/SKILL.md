---
name: explain-skill
description: >
  Explain what an installed skill does, when it triggers, and highlight security concerns.
  Use when the user asks about a skill's purpose, functionality, or safety — e.g.,
  "這個 skill 是什麼", "skill-xxx 做什麼用", "explain skill xxx", "what does this skill do",
  "/explain-skill", "列出所有 skills", "list skills", "我裝了哪些 skills",
  "這個 skill 安全嗎", "review this skill". Also triggers when the user wants to
  understand, audit, or review any installed skill, especially third-party ones.
---

# Explain Skill

Inspect and explain installed skills, with emphasis on third-party skill safety review.

## Workflow

### 1. Identify the target

- If user specifies a skill name, inspect that skill.
- If user asks "list all" / "列出所有", run `scripts/inspect_skill.py --list`.
- If ambiguous, run `--list` first, then ask the user which skill to inspect.

### 2. Run the inspection script

```bash
python3 {baseDir}/scripts/inspect_skill.py <skill-name>
```

The script outputs:
- **Description** — the frontmatter description (triggering conditions)
- **File tree** — all files with sizes
- **Scripts analysis** — flags executable code and risky patterns (network access, file deletion, shell exec, credential references, file writes)
- **References / Assets** — bundled resource files
- **Body preview** — first 20 lines of SKILL.md instructions

### 3. Read the full SKILL.md if needed

For deeper explanation, read `~/.claude/skills/<name>/SKILL.md` to understand the complete instructions.

### 4. Present the explanation in 繁體中文

Structure the response as:

**[Skill 名稱]**

| 項目 | 說明 |
|------|------|
| 功能 | 一句話說明這個 skill 做什麼 |
| 觸發條件 | 什麼情況下會被啟動（從 description 摘要） |
| 包含的腳本 | 列出 scripts/ 中的檔案及其用途 |
| 參考資料 | references/ 中的檔案 |
| 素材 | assets/ 中的檔案 |

### 5. Security review (important for third-party skills)

Always include a security section when scripts exist. Check for:

- **Network access** — curl, wget, requests, fetch calls
- **File system writes/deletes** — rm -rf, shutil.rmtree, file writes
- **Shell execution** — subprocess, os.system, eval, exec
- **Credential references** — password, secret, token, api_key patterns
- **Obfuscated code** — base64 encoded strings, minified code, binary files

Rate the risk level:
- **Low** — No scripts, or scripts with no risky patterns
- **Medium** — Scripts with file-write or network patterns (common in legitimate skills)
- **High** — Scripts with shell-exec + network + credential patterns combined

Present the security section clearly:

**安全性評估: [Low/Medium/High]**
- 列出偵測到的模式及其所在檔案
- 如果是 High，建議使用者在執行前先手動檢查腳本內容
