---
name: twilio-voice
description: "Make outbound phone calls via Twilio Voice API with zh-TW text-to-speech. Use when the agent needs to call, phone, ring, or voice-notify the user. Plays Google TTS MP3 via <Play> for reliable zh-TW delivery; optional <Say> fallback via --backup-say."
metadata: {"openclaw":{"emoji":"📞","os":["darwin","linux"],"requires":{"bins":["python3"]}}}
---

# Twilio Voice

Make outbound phone calls with zh-TW TTS via Twilio Voice API.

## Quick Start

```bash
python3 {baseDir}/scripts/call.py \
  --message "北鼻好可愛" \
  --from-number +1XXXXXXXXXX
```

Add `--backup-say` to append Twilio `<Say>` after `<Play>` (recipient may hear message twice):

```bash
python3 {baseDir}/scripts/call.py --message "北鼻好可愛" --from-number +1XXXXXXXXXX --backup-say
```

Add `--dry-run --json` to preview TwiML without placing the call.

## Constraints

- **Recipient hardcoded:** `+886XXXXXXXXX` — edit `RECIPIENT_NUMBER` in call.py to set your number
- **Message limit:** 2000 characters
- **TTS strategy:** Google TTS MP3 via `<Play>` (more reliable than live `<Say>` on zh-TW routes)

## Flags

| Flag | Required | Description |
|------|----------|-------------|
| `--message` | Yes | Text to speak |
| `--from-number` | No | Caller number (default: `TWILIO_FROM_NUMBER` env) |
| `--backup-say` | No | Append `<Say>` after `<Play>` for extra reliability |
| `--dry-run` | No | Preview TwiML only, no call placed |
| `--json` | No | Machine-readable JSON output |
| `--account-sid` | No | Override Twilio SID (default: env) |
| `--auth-token` | No | Override Twilio token (default: env) |

## Required Environment Variables

Injected by gateway via 1Password (`op run`):

- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_FROM_NUMBER`

## Exit Codes

`0` success · `1` validation error · `2` credential error · `3` Twilio API error · `4` network error
