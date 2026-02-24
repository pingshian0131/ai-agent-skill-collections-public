---
name: openclaw-rebuild
description: Update OpenClaw to the latest version — pull source, rebuild Docker image, and restart containers. Use when the user wants to update, upgrade, rebuild, or restart OpenClaw.
---

# OpenClaw Rebuild

Pull latest source, rebuild the `openclaw:local` Docker image, and restart all gateway containers.

## Workflow

### 1. Fetch and checkout latest stable release

```bash
git -C ~/Documents/openclaw fetch --tags
LATEST_TAG=$(git -C ~/Documents/openclaw tag --sort=-v:refname | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' | head -1)
git -C ~/Documents/openclaw checkout "$LATEST_TAG"
```

This checks out the latest stable release tag (e.g. `v2026.2.23`), skipping pre-releases and unreleased commits on main.

### 2. Build the image

```bash
docker build -t openclaw:local -f ~/Documents/openclaw/Dockerfile ~/Documents/openclaw
```

Timeout: allow up to 5 minutes. Most rebuilds use Docker cache and finish in under 30 seconds.

### 3. Restart containers

```bash
docker compose -f ~/openclaw-docker/docker-compose.yml up -d
```

### 4. Verify

```bash
docker compose -f ~/openclaw-docker/docker-compose.yml ps
```

Confirm both gateways are `Up`:
- `openclaw-work` on port `18791`
- `openclaw-personal` on port `18793`

## Auto-update cron

A crontab entry runs `rebuild.sh` every 2 days at 04:00 (after the 03:00 backup window):

```
0 4 */2 * * ~/.openclaw-personal/.claude/skills/openclaw-rebuild/scripts/rebuild.sh
```

- Log: `/tmp/openclaw-rebuild.log`
- Script: `.claude/skills/openclaw-rebuild/scripts/rebuild.sh`

To check recent rebuild output: `tail -50 /tmp/openclaw-rebuild.log`

## Key paths

| Item | Path |
|------|------|
| Source repo | `~/Documents/openclaw/` |
| Dockerfile | `~/Documents/openclaw/Dockerfile` |
| docker-compose | `~/openclaw-docker/docker-compose.yml` |
| .env | `~/openclaw-docker/.env` |
| Image tag | `openclaw:local` |
