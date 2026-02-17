---
name: email
description: "Send email via SMTP with Gmail App Password. Trigger when the user asks to send an email, compose a message, or mail someone."
metadata: {"clawdbot":{"emoji":"📧","os":["darwin","linux"],"requires":{"bins":["python3"]}}}
---

# Email

Send email via Python SMTP. Default: Gmail App Password (smtp.gmail.com:587, STARTTLS).

## Setup

1. Go to https://myaccount.google.com/apppasswords
   - Requires 2FA enabled on your Google account
   - Create a new app password (name it "OpenClaw" or similar)
   - Copy the 16-character password

2. Add credentials to `~/.openclaw/.env`:
   ```
   SMTP_USER=you@gmail.com
   SMTP_PASS=abcdefghijklmnop
   ```

3. Verify:
   ```bash
   python3 {baseDir}/scripts/send_email.py \
     --to you@gmail.com --subject "Test" --body "Hello" --dry-run
   ```

## Usage

Basic send:
```bash
python3 {baseDir}/scripts/send_email.py \
  --to recipient@example.com \
  --subject "Meeting tomorrow" \
  --body "Hi, just confirming our meeting at 3pm."
```

HTML email:
```bash
python3 {baseDir}/scripts/send_email.py \
  --to recipient@example.com \
  --subject "Report" \
  --body "<h1>Monthly Report</h1><p>See attached.</p>" \
  --html
```

With attachments:
```bash
python3 {baseDir}/scripts/send_email.py \
  --to recipient@example.com \
  --subject "Files" \
  --body "Please find attached." \
  --attach /path/to/report.pdf \
  --attach /path/to/data.csv
```

Multiple recipients with CC/BCC:
```bash
python3 {baseDir}/scripts/send_email.py \
  --to "a@example.com, b@example.com" \
  --cc "manager@example.com" \
  --bcc "archive@example.com" \
  --subject "Update" \
  --body "Team update for this week."
```

JSON output (for scripting):
```bash
python3 {baseDir}/scripts/send_email.py \
  --to a@example.com --subject "Hi" --body "Hello" --json
```

Custom SMTP server:
```bash
python3 {baseDir}/scripts/send_email.py \
  --host smtp.office365.com --port 587 \
  --user me@company.com --password "xxx" \
  --to colleague@company.com \
  --subject "Note" --body "FYI"
```

## Credentials

Resolution order (first match wins):
1. `--user` / `--password` flags
2. `SMTP_USER` / `SMTP_PASS` environment variables
3. `~/.openclaw/.env` file

## Notes

- Always confirm with the user before sending (especially to external recipients).
- Use `--dry-run` to preview the full MIME message without sending.
- Attachments are auto-detected for MIME type.
- Gmail rate limit: ~500 emails/day for personal accounts.
- Exit codes: 0=success, 1=validation error, 2=credential error, 3=SMTP error, 4=send error.
