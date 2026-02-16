#!/usr/bin/env python3
"""Send email via SMTP. Default: Gmail App Password (smtp.gmail.com:587, STARTTLS)."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


DEFAULT_HOST = "smtp.gmail.com"
DEFAULT_PORT = 587
DOTENV_PATH = "~/.openclaw/.env"


def eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


def load_dotenv(path: str) -> Dict[str, str]:
    """Parse KEY=VALUE lines from a .env file."""
    result: Dict[str, str] = {}
    env_path = Path(path).expanduser()
    if not env_path.is_file():
        return result
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        result[key] = value
    return result


def resolve_credentials(args: argparse.Namespace) -> Tuple[str, str]:
    """Resolve SMTP credentials: CLI flags > env vars > .env file."""
    user = args.user or os.environ.get("SMTP_USER")
    password = args.password or os.environ.get("SMTP_PASS")

    if not user or not password:
        dotenv = load_dotenv(DOTENV_PATH)
        user = user or dotenv.get("SMTP_USER")
        password = password or dotenv.get("SMTP_PASS")

    if not user:
        eprint("Error: SMTP_USER not set. Use --user, SMTP_USER env var, or add to ~/.openclaw/.env")
        raise SystemExit(2)
    if not password:
        eprint("Error: SMTP_PASS not set. Use --password, SMTP_PASS env var, or add to ~/.openclaw/.env")
        raise SystemExit(2)

    return user, password


def parse_recipients(value: Optional[str]) -> List[str]:
    """Split comma-separated email addresses."""
    if not value:
        return []
    return [addr.strip() for addr in value.split(",") if addr.strip()]


def attach_file(msg: EmailMessage, filepath: str) -> None:
    """Attach a file to the message with auto-detected MIME type."""
    path = Path(filepath)
    mime_type, _ = mimetypes.guess_type(str(path))
    if mime_type is None:
        mime_type = "application/octet-stream"
    maintype, subtype = mime_type.split("/", 1)
    data = path.read_bytes()
    msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=path.name)


def build_message(args: argparse.Namespace, sender: str) -> EmailMessage:
    """Build an EmailMessage from parsed arguments."""
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = args.to
    msg["Subject"] = args.subject

    if args.cc:
        msg["Cc"] = args.cc

    if args.html:
        msg.set_content(args.body, subtype="html")
    else:
        msg.set_content(args.body)

    if args.attach:
        for filepath in args.attach:
            attach_file(msg, filepath)

    return msg


def send(
    msg: EmailMessage,
    bcc: List[str],
    host: str,
    port: int,
    user: str,
    password: str,
) -> Dict[str, Any]:
    """Send the message via SMTP with STARTTLS."""
    all_recipients: List[str] = []
    if msg["To"]:
        all_recipients.extend(parse_recipients(msg["To"]))
    if msg["Cc"]:
        all_recipients.extend(parse_recipients(msg["Cc"]))
    all_recipients.extend(bcc)

    with smtplib.SMTP(host, port, timeout=30) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(user, password)
        server.send_message(msg, to_addrs=all_recipients)

    return {
        "ok": True,
        "message_id": msg.get("Message-ID"),
        "recipients": all_recipients,
        "subject": msg["Subject"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Send email via SMTP (default: Gmail App Password).",
    )
    parser.add_argument("--to", required=True, help="Recipient(s), comma-separated")
    parser.add_argument("--subject", required=True, help="Email subject line")
    parser.add_argument("--body", required=True, help="Email body (plain text or HTML with --html)")
    parser.add_argument("--cc", help="CC recipient(s), comma-separated")
    parser.add_argument("--bcc", help="BCC recipient(s), comma-separated")
    parser.add_argument("--from", dest="sender", help="Override sender address (default: SMTP_USER)")
    parser.add_argument("--attach", action="append", help="File path to attach (repeatable)")
    parser.add_argument("--html", action="store_true", help="Treat body as HTML")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"SMTP server (default: {DEFAULT_HOST})")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"SMTP port (default: {DEFAULT_PORT})")
    parser.add_argument("--user", help="SMTP username (overrides env)")
    parser.add_argument("--password", help="SMTP password (overrides env)")
    parser.add_argument("--json", dest="json_output", action="store_true", help="JSON output")
    parser.add_argument("--dry-run", action="store_true", help="Preview message without sending")

    args = parser.parse_args()

    # Resolve credentials
    try:
        user, password = resolve_credentials(args)
    except SystemExit:
        return 2

    sender = args.sender or user

    # Parse recipients
    to_addrs = parse_recipients(args.to)
    cc_addrs = parse_recipients(args.cc)
    bcc_addrs = parse_recipients(args.bcc)

    if not to_addrs:
        eprint("Error: --to requires at least one recipient.")
        return 1

    # Validate attachments
    if args.attach:
        for filepath in args.attach:
            if not Path(filepath).is_file():
                eprint(f"Error: attachment not found: {filepath}")
                return 1

    # Build message
    msg = build_message(args, sender=sender)

    # Dry run
    if args.dry_run:
        print(msg.as_string())
        return 0

    # Send
    try:
        result = send(msg, bcc=bcc_addrs, host=args.host, port=args.port,
                       user=user, password=password)
    except smtplib.SMTPAuthenticationError as exc:
        error_msg = f"SMTP authentication failed: {exc}"
        if args.json_output:
            print(json.dumps({"ok": False, "error": error_msg}))
        else:
            eprint(error_msg)
        return 3
    except smtplib.SMTPException as exc:
        error_msg = f"SMTP error: {exc}"
        if args.json_output:
            print(json.dumps({"ok": False, "error": error_msg}))
        else:
            eprint(error_msg)
        return 3
    except Exception as exc:
        error_msg = f"Send failed: {exc}"
        if args.json_output:
            print(json.dumps({"ok": False, "error": error_msg}))
        else:
            eprint(error_msg)
        return 4

    # Output
    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(f"Sent to: {', '.join(to_addrs)}")
        if cc_addrs:
            print(f"CC: {', '.join(cc_addrs)}")
        if bcc_addrs:
            print(f"BCC: {', '.join(bcc_addrs)}")
        print(f"Subject: {args.subject}")
        print(f"Message-ID: {result.get('message_id', 'N/A')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
