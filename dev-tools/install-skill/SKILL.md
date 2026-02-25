---
name: install-skill
description: >
  Install third-party AgentSkills from GitHub or ClawHub URLs with security scanning.
  Use when asked to "install a skill", "add a skill from GitHub/ClawHub",
  "download a skill from URL", or "import a skill".
---

# Install Skill

Install a third-party skill from a GitHub or ClawHub URL with automated security scanning.

## Step 1: Download Skill

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
| **HIGH** | Stop immediately. Display: file path, line numbers, threat category, description, and suspicious code snippet. Ask user to explicitly choose: abandon installation or acknowledge risk and continue. |
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

5. **Clean up temp files:**
   ```bash
   rm -rf /tmp/skills/{skill-name}/
   ```

## Step 5: Publish

Ask the user if they want to publish the installed skill to their GitHub skill collection repos.

If yes, invoke `/publish-skill` targeting the installed skill directory.

If no, skip and report installation complete.
