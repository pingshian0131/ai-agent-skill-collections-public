# Security Scan Patterns

7 threat categories for evaluating third-party skill files. For each pattern, consider context — some patterns have legitimate uses noted under "Exceptions."

---

## 1. Prompt Injection

Attempts to override system instructions or inject hidden commands.

**Signatures:**
- Text like "ignore previous instructions", "you are now", "new system prompt", "disregard all prior"
- Hidden instructions in HTML comments (`<!-- -->`), markdown comments, or after excessive whitespace
- Unicode zero-width characters (U+200B, U+200C, U+200D, U+FEFF) embedding hidden text
- Base64-encoded strings that decode to instruction-like text
- Markdown/YAML that renders invisible text (e.g., white-on-white, font-size: 0)
- Instructions to "not mention", "hide from user", or "act as if"

**Exceptions:**
- Skills that legitimately set persona or role context (e.g., "You are a code reviewer") — the key distinction is whether it *supplements* vs *overrides* the system prompt

---

## 2. Data Exfiltration

Sending local data to external servers.

**Signatures:**
- `curl`, `wget`, `fetch`, `requests.post/put/patch` sending local file contents or env vars to external URLs
- Commands reading then transmitting: `cat ~/.ssh/id_rsa | curl ...`
- Webhook URLs (Discord, Slack, custom) receiving data payloads
- Environment variable harvesting: bulk reads of `$HOME`, `$PATH`, API keys, tokens
- DNS exfiltration patterns: encoding data in DNS queries
- Piping local data to `nc`/`ncat`/netcat

**Exceptions:**
- Skills that interact with known APIs (GitHub, Trello, etc.) using user-provided credentials
- Logging to user-specified endpoints explicitly documented in the skill

---

## 3. Obfuscation / Encoding

Hiding malicious intent through encoding or string manipulation.

**Signatures:**
- Long base64 strings (> 100 chars) not clearly serving a documented purpose
- Hex-encoded strings being decoded and executed
- String concatenation to build URLs or commands: `"ht" + "tp" + "://" + ...`
- `eval()`, `exec()`, `Function()`, `subprocess.run(user_string)` with dynamic input
- ROT13, XOR, or custom encoding/decoding routines
- Template literals or f-strings constructing shell commands from variables

**Exceptions:**
- Base64 in asset files (images, fonts) is normal
- `eval`/`exec` in legitimate scripting contexts with static, visible inputs

---

## 4. Reverse Shell / Backdoor

Establishing persistent unauthorized access.

**Signatures:**
- `nc -e`, `ncat`, `socat` with shell redirection
- `bash -i >& /dev/tcp/...`, `/bin/sh -i`, reverse shell one-liners
- SSH key injection: writing to `~/.ssh/authorized_keys`
- Crontab modifications: `crontab -e`, writing to `/var/spool/cron/`
- LaunchAgent/LaunchDaemon creation on macOS (`~/Library/LaunchAgents/`)
- Systemd service creation on Linux
- Listening on network ports: `bind()`, `listen()`, `nc -l`

**Exceptions:**
- Skills that legitimately manage cron (e.g., openclaw-cron) — must be clearly documented
- SSH key management skills with explicit user consent flows

---

## 5. Suspicious Prerequisites

Demanding dangerous setup steps or pulling untrusted code.

**Signatures:**
- `curl | bash`, `curl | sh`, `wget | bash` — pipe-to-shell patterns
- Installing from non-official package sources or adding untrusted PPAs/repos
- Requiring `sudo` or root access without clear justification
- Disabling security mechanisms: `--no-verify`, `set +e`, disabling firewalls/Gatekeeper
- Downloading and executing binaries from arbitrary URLs
- `npm install` / `pip install` from non-registry sources (git URLs, tarballs)

**Exceptions:**
- Official tool installation commands (e.g., Homebrew, nvm) are generally acceptable
- `pip install` / `npm install` from official registries with pinned versions

---

## 6. File System Manipulation

Unauthorized modification of system or user configuration files.

**Signatures:**
- Writing to dotfiles: `.bashrc`, `.zshrc`, `.profile`, `.gitconfig`
- Modifying OpenClaw config: `openclaw.json`, `jobs.json`, agent workspace files
- Symlink attacks: creating symlinks to sensitive files
- `rm -rf` targeting home directory, system paths, or broad globs
- Modifying `/etc/` files or system configurations
- Writing to `~/.claude/`, `~/.config/`, or other tool config directories
- `chmod 777` or overly permissive file permissions

**Exceptions:**
- Skills that explicitly manage OpenClaw config (e.g., agent-creator) — must be clearly documented as their core purpose
- Writing to the skill's own directory or designated output directories

---

## 7. Credential Harvesting

Collecting or exposing authentication material.

**Signatures:**
- Prompting the user to paste API keys, passwords, or tokens into the conversation
- Reading keychain/credential stores: `security find-generic-password`, Keychain Access
- Accessing 1Password CLI: `op read`, `op get`
- Reading browser cookies or local storage databases
- Accessing cloud credential files: `~/.aws/credentials`, `~/.kube/config`, `~/.docker/config.json`
- Reading `.env` files and extracting secret values
- Git credential extraction: `.git-credentials`, `git credential fill`

**Exceptions:**
- Skills that need a specific API key for their function (e.g., a Trello skill asking for a Trello API key) — must store it via the user's established credential management, not in plain text within the skill
- Reading `.env` for non-secret configuration (e.g., `NODE_ENV`, `PORT`)
