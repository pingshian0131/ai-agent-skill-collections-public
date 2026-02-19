---
name: publish-skill
description: "Publish an AgentSkill to GitHub skill collection repos (private + public). Scans for sensitive data, normalizes paths to {baseDir}, sanitizes for public distribution, updates READMEs, and commits. Use when the user wants to publish, distribute, release, or sync a skill to the collection repos."
---

# Publish Skill

Publish a skill to the private and public GitHub skill collection repos with proper sanitization.

## Repositories

| Repo | Path | Remote |
|------|------|--------|
| **Private** | `~/Documents/projects/ai-agent-skill-collections/` | `pingshian0131/ai-agent-skill-collections` |
| **Public** | `~/Documents/projects/ai-agent-skill-collections-public/` | `pingshian0131/ai-agent-skill-collections-public` |

### Category Directories

| Category | Private | Public |
|----------|---------|--------|
| Dev tools / meta | `meta/` | `dev-tools/` |
| OpenClaw ops | `openclaw/` | `openclaw/` |
| Communication | `communication/` | `communication/` |
| Knowledge | `knowledge/` | `knowledge/` |
| Panamera (private only) | `panamera/` | — |

## Step 1: Choose Category

Determine which category directory the skill belongs to based on its function. If unsure, ask the user.

## Step 2: Scan for Sensitive Data

Read every file in the skill directory. Flag any matches:

- **Phone numbers** — real personal or service numbers (e.g. `+886...`, `+1...`)
- **API keys / tokens** — any string resembling a secret (`sk-...`, `AC...`, bearer tokens)
- **Absolute paths** — `/Users/<username>/...` or any user-specific path
- **Email addresses** — personal emails
- **1Password vault paths** — `op://...` references (OK to keep if they only describe architecture)
- **Hardcoded credentials** — passwords, auth tokens in code

Report findings to the user with file:line references before proceeding.

## Step 3: Publish to Private Repo

1. Create `<category>/<skill-name>/` and copy all skill files
2. **Path normalization only:** replace absolute paths with `{baseDir}/...`
3. Keep real phone numbers, service credentials references (it's a private repo)
4. Update `README.md` — add row to the matching category table:
   ```
   | [skill-name](./category/skill-name/) | 中文說明 |
   ```
5. Commit & push:
   ```
   git add <category>/<skill-name>/ README.md
   git commit -m "feat: 新增 <skill-name> skill — <簡短說明>"
   git push origin main
   ```

## Step 4: Publish to Public Repo

1. Create `<category>/<skill-name>/` and copy all skill files
2. **Full sanitization:**
   - Absolute paths → `{baseDir}/...`
   - Phone numbers → `+XXXXXXXXXXX` (match format length)
   - API keys/tokens → `YOUR_<NAME>_HERE`
   - Personal emails → `you@example.com`
   - Add `# TODO: Replace with your ...` comments where values were sanitized
3. Update `README.md` — same table format as private
4. Commit & push (same format)

## Step 5: Verify

```bash
# Public repo must have ZERO real sensitive data
grep -rE '\+886[0-9]{9}' <public-repo>/communication/<skill>/    # zero matches
grep -r 'workspace-' <public-repo>/<category>/<skill>/            # zero matches

# Both repos must have zero absolute user paths
grep -r '/Users/' <private-repo>/<category>/<skill>/              # zero matches
grep -r '/Users/' <public-repo>/<category>/<skill>/               # zero matches
```
