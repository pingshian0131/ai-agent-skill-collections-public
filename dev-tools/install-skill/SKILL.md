---
name: install-skill
description: >
  Install third-party AgentSkills from GitHub or ClawHub URLs with security scanning.
  Also explains and inspects installed skills — what they do, when they trigger, and security review.
  Use when asked to "install a skill", "add a skill from GitHub/ClawHub",
  "download a skill from URL", "import a skill",
  "explain skill", "這個 skill 是什麼", "skill-xxx 做什麼用", "what does this skill do",
  "列出所有 skills", "list skills", "我裝了哪些 skills",
  "這個 skill 安全嗎", "review this skill", or when the user wants to
  understand, audit, or review any installed skill (especially third-party ones).
---

# Install Skill

Install third-party skills from GitHub/ClawHub URLs with security scanning, or inspect/explain installed skills.

Determine which mode based on user intent:
- **Install mode** — user provides a URL or asks to install/download a skill → go to "Install Workflow"
- **Explain mode** — user asks about a skill's purpose, wants to list skills, or review security → go to "Explain Workflow"

---

## Explain Workflow

### 1. Identify target

- If user specifies a skill name → inspect that skill.
- If user asks "list all" / "列出所有" → run `--list`.
- If ambiguous → run `--list` first, then ask which skill to inspect.

### 2. Run inspection script

```bash
python3 {baseDir}/scripts/inspect_skill.py <skill-name>
# Or with custom path:
python3 {baseDir}/scripts/inspect_skill.py <skill-name> --path /custom/skills/dir
# Or absolute path:
python3 {baseDir}/scripts/inspect_skill.py /path/to/skill-dir
# List all:
python3 {baseDir}/scripts/inspect_skill.py --list
```

The script outputs: description, file tree with sizes, scripts analysis (flags risky patterns), references/assets listing, and SKILL.md body preview.

### 3. Read the full SKILL.md if needed

For deeper explanation, read `~/.claude/skills/<name>/SKILL.md` to understand complete instructions.

### 4. Present the explanation in 繁體中文

| 項目 | 說明 |
|------|------|
| 功能 | 一句話說明這個 skill 做什麼 |
| 觸發條件 | 什麼情況下會被啟動 |
| 包含的腳本 | scripts/ 中的檔案及用途 |
| 參考資料 | references/ 中的檔案 |
| 素材 | assets/ 中的檔案 |

### 5. Security review

Always include when scripts exist. Check for:
- **Network access** — curl, wget, requests, fetch
- **File deletion** — rm -rf, shutil.rmtree
- **Shell execution** — subprocess, os.system, eval, exec
- **Credential references** — password, secret, token, api_key
- **Obfuscated code** — base64, minified, binary

Risk rating:
- **Low** — No scripts or no risky patterns
- **Medium** — File-write or network patterns (common in legitimate skills)
- **High** — shell-exec + network + credential patterns combined; recommend manual review

---

## Install Workflow

### Step 1: Download Skill

1. **Parse the URL:**
   - **GitHub**: extract `{owner}`, `{repo}`, `{branch}`, `{path}` from `github.com/{owner}/{repo}/tree/{branch}/{path}`
   - **ClawHub**: fetch the page with WebFetch to locate the underlying GitHub repo URL, then parse as above
   - If the URL points to a repo root with no path, default `{path}` to the repo root

2. **List all files** recursively:
   ```bash
   gh api repos/{owner}/{repo}/contents/{path}?ref={branch} | jq -r '.[].path'
   ```
   For nested directories, recurse into each `type: "dir"` entry.

3. **Download** each file to `/tmp/skills/{skill-name}/`, preserving directory structure:
   ```bash
   gh api repos/{owner}/{repo}/contents/{file_path}?ref={branch} -q '.content' | base64 -d > /tmp/skills/{skill-name}/{relative_path}
   ```

4. **Validate**: confirm a `SKILL.md` exists in the downloaded directory root and contains valid YAML frontmatter with `name` and `description` fields. If missing, abort with an error.

## Step 2: Security Scan

Read every file in `/tmp/skills/{skill-name}/` and evaluate against the threat patterns in [references/scan-patterns.md](references/scan-patterns.md).

**Scanning strategy:**
- **< 10 files**: read and scan each file sequentially
- **>= 10 files**: use sub-agents (Task tool) to scan in parallel — split files into batches, each sub-agent receives its batch + the full pattern list from scan-patterns.md

**For each file, produce:**
- Risk level: `CLEAN` | `LOW` | `MEDIUM` | `HIGH`
- Findings: list of matched patterns with category, description, and line numbers
- Suspicious code snippets (for MEDIUM/HIGH)

## Step 3: Risk Gate

Act based on the highest risk level found across all files:

| Highest Risk | Action |
|-------------|--------|
| **HIGH** | Stop immediately. Display: file path, line numbers, threat category, description, and suspicious code snippet. Ask user to explicitly choose: abandon installation or acknowledge risk and continue. **If user abandons, jump to Step 6 (Cleanup) and stop.** |
| **MEDIUM** | Display all findings with file paths and line numbers. Ask user to confirm before continuing. |
| **LOW** | Display summary of findings. Continue automatically. |
| **CLEAN** | Display "All files passed security scan." Continue automatically. |

## Step 4: Choose Environment & Agent

1. **Detect available environments:**
   ```bash
   ls -d ~/.openclaw-*/ | sed 's|.*/.openclaw-||;s|/||'
   ```
   Ask the user which environment to install to.

2. **List agents** in the chosen environment by scanning workspace directories:
   ```bash
   # 'main' agent uses workspace/, others use workspace-{name}/
   ls -d ~/.openclaw-{env}/workspace/ ~/.openclaw-{env}/workspace-*/ 2>/dev/null | sed 's|.*/workspace-||;s|.*/workspace|main|;s|/||'
   ```
   Ask the user which agent should receive the skill.

3. **If the agent doesn't exist**, offer to create it using `/agent-creator`. After creation, continue with the install.

4. **Copy skill to target:**
   ```bash
   cp -r /tmp/skills/{skill-name}/ ~/.openclaw-{env}/workspace-{agent}/skills/{skill-name}/
   # For 'main' agent:
   cp -r /tmp/skills/{skill-name}/ ~/.openclaw-{env}/workspace/skills/{skill-name}/
   ```

## Step 5: Publish

Ask the user if they want to publish the installed skill to their GitHub skill collection repos.

If yes, invoke `/publish-skill` targeting the installed skill directory.

If no, skip and continue to Step 6.

## Step 6: Cleanup

**This step ALWAYS runs**, regardless of how the flow ended (abandoned at risk gate, installed without publish, or installed with publish).

Remove the downloaded temp files:
```bash
rm -rf /tmp/skills/{skill-name}/
```

Report final status to the user.
