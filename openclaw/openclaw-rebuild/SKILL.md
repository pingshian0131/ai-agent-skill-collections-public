---
name: openclaw-rebuild
description: Update OpenClaw to the latest version — pull source, rebuild Docker image, and restart containers. Use when the user wants to update, upgrade, rebuild, or restart OpenClaw.
---

# OpenClaw Rebuild

Pull latest source, rebuild the `openclaw:local` Docker image, and restart all gateway containers.

## Workflow

### 1. Pull latest source

```bash
git -C ~/Documents/openclaw pull
```

If pull fails due to local changes, stash first: `git -C ~/Documents/openclaw stash && git -C ~/Documents/openclaw pull`

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

## Key paths

| Item | Path |
|------|------|
| Source repo | `~/Documents/openclaw/` |
| Dockerfile | `~/Documents/openclaw/Dockerfile` |
| docker-compose | `~/openclaw-docker/docker-compose.yml` |
| .env | `~/openclaw-docker/.env` |
| Image tag | `openclaw:local` |
