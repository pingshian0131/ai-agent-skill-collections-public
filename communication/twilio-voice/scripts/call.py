#!/usr/bin/env python3
"""Make outbound phone calls using Twilio Voice API.

Supports custom TwiML messages in Traditional Chinese (zh-TW).
Credentials resolution: CLI args > 1Password > environment variables.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.parse
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
except ImportError:
    print(
        "Error: twilio package not installed. "
        "Install with: pip3 install twilio",
        file=sys.stderr,
    )
    sys.exit(2)


# Constants
RECIPIENT_NUMBER = "+886XXXXXXXXX"  # TODO: Replace with your recipient number
TWIML_LANGUAGE = "zh-TW"  # Traditional Chinese (Taiwan)


def eprint(msg: str) -> None:
    """Print to stderr."""
    print(msg, file=sys.stderr)


def resolve_credentials(
    args: argparse.Namespace,
) -> Tuple[str, str, str]:
    """Resolve Twilio credentials: CLI flags > env vars.

    Returns: (account_sid, auth_token, from_number)
    Raises: SystemExit with code 2 if credentials missing
    """
    account_sid = args.account_sid
    auth_token = args.auth_token
    from_number = args.from_number

    # If all CLI args provided, use them directly
    if account_sid and auth_token and from_number:
        return (account_sid, auth_token, from_number)

    # Use environment variables (injected by gateway via op run)
    account_sid = account_sid or os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = auth_token or os.environ.get("TWILIO_AUTH_TOKEN")
    from_number = from_number or os.environ.get("TWILIO_FROM_NUMBER")

    # Validate all credentials are present
    errors = []
    if not account_sid:
        errors.append(
            "TWILIO_ACCOUNT_SID not found. "
            "Provide via --account-sid or TWILIO_ACCOUNT_SID env var (injected from 1Password via gateway)"
        )
    if not auth_token:
        errors.append(
            "TWILIO_AUTH_TOKEN not found. "
            "Provide via --auth-token or TWILIO_AUTH_TOKEN env var (injected from 1Password via gateway)"
        )
    if not from_number:
        errors.append(
            "TWILIO_FROM_NUMBER not found. "
            "Provide via --from-number or TWILIO_FROM_NUMBER env var (injected from 1Password via gateway)"
        )

    if errors:
        for error in errors:
            eprint(f"Error: {error}")
        raise SystemExit(2)

    return (account_sid, auth_token, from_number)


def build_twiml(
    message: str,
    language: str = TWIML_LANGUAGE,
    backup_say: bool = False,
) -> str:
    """Build TwiML XML for voice message.

    Strategy:
    1) Prefer <Play> with a generated MP3 URL (more reliable than live TTS on some routes)
    2) Keep <Say> as fallback
    """
    # Escape special XML characters in message
    message_escaped = (
        message.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )

    # Public Google TTS endpoint for quick MP3 playback (URL-encoded text)
    q = urllib.parse.quote(message)
    tts_mp3_url = (
        f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl={language}&q={q}"
    )
    tts_mp3_url_xml = tts_mp3_url.replace("&", "&amp;")

    if backup_say:
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Pause length="1"/>
    <Play>{tts_mp3_url_xml}</Play>
    <Pause length="1"/>
    <Say language="{language}">{message_escaped}</Say>
</Response>"""
    else:
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Pause length="1"/>
    <Play>{tts_mp3_url_xml}</Play>
</Response>"""

    return twiml


def make_call(
    account_sid: str,
    auth_token: str,
    from_number: str,
    message: str,
    to_number: str = RECIPIENT_NUMBER,
    dry_run: bool = False,
    backup_say: bool = False,
) -> Dict[str, Any]:
    """Make an outbound call with Twilio Voice.

    Args:
        account_sid: Twilio Account SID
        auth_token: Twilio Auth Token
        from_number: Caller ID (sending number)
        message: Voice message to speak
        to_number: Recipient phone number (default: RECIPIENT_NUMBER constant)
        dry_run: If True, return TwiML without making actual call

    Returns:
        Dict with call details or error information
    """
    twiml = build_twiml(message, backup_say=backup_say)

    # Dry run: just return TwiML
    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "mode": "preview",
            "twiml": twiml,
            "from": from_number,
            "to": to_number,
            "message": message,
            "twiml_language": TWIML_LANGUAGE,
        }

    # Actual call
    try:
        client = Client(account_sid, auth_token)
        call = client.calls.create(
            twiml=twiml,
            to=to_number,
            from_=from_number,
        )

        return {
            "ok": True,
            "call_sid": call.sid,
            "status": call.status,
            "from": call.from_formatted or from_number,
            "to": call.to_formatted or to_number,
            "message": message,
            "twiml_language": TWIML_LANGUAGE,
            "created_at": str(call.date_created) if call.date_created else None,
        }

    except TwilioRestException as exc:
        error_msg = f"Twilio API error {exc.code}: {exc.msg}"
        error_code = "TWILIO_API_ERROR"

        # Map common error codes
        if exc.code == 20003:
            error_code = "ACCOUNT_SUSPENDED"
            error_msg = "Account suspended or billing issue (error 20003). Check payment method in Twilio dashboard."
        elif exc.code == 21211:
            error_code = "INVALID_PHONE"
            error_msg = "Invalid phone number format"
        elif exc.code == 21403:
            error_code = "TRIAL_RESTRICTION"
            error_msg = "Twilio trial account: recipient must be verified number"
        elif exc.code == 32001:
            error_code = "AUTH_FAILED"
            error_msg = "Authentication failed. Check Account SID and Auth Token."

        eprint(error_msg)
        return {
            "ok": False,
            "error": error_msg,
            "error_code": error_code,
            "twilio_code": exc.code,
        }

    except Exception as exc:
        error_msg = f"Unexpected error: {exc}"
        eprint(error_msg)
        return {
            "ok": False,
            "error": error_msg,
            "error_code": "UNKNOWN_ERROR",
        }


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Make outbound voice calls using Twilio Voice API",
    )

    parser.add_argument(
        "--message",
        required=True,
        help="Voice message to speak (supports Chinese, English, etc.)",
    )

    parser.add_argument(
        "--account-sid",
        help="Twilio Account SID (overrides 1Password and env var)",
    )

    parser.add_argument(
        "--auth-token",
        help="Twilio Auth Token (overrides 1Password and env var)",
    )

    parser.add_argument(
        "--from-number",
        help="Caller ID number (overrides 1Password and env var, default: from 1Password or TWILIO_FROM_NUMBER)",
    )


    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview TwiML without making actual call",
    )

    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Output as JSON (for scripting)",
    )

    parser.add_argument(
        "--backup-say",
        action="store_true",
        help="Play MP3 first, then use Twilio <Say> as backup (you may hear message twice)",
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()

    # Validate message
    if not args.message or not args.message.strip():
        eprint("Error: --message is required and cannot be empty")
        return 1

    if len(args.message) > 2000:
        eprint(
            f"Error: Message too long ({len(args.message)} chars). "
            "Maximum 2000 characters per Twilio Say instruction."
        )
        return 1

    # Resolve credentials
    try:
        account_sid, auth_token, from_number = resolve_credentials(args)
    except SystemExit:
        return 2

    # Make the call
    result = make_call(
        account_sid=account_sid,
        auth_token=auth_token,
        from_number=from_number,
        message=args.message,
        dry_run=args.dry_run,
        backup_say=args.backup_say,
    )

    # Output result
    if args.json_output:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result["ok"]:
            if result.get("dry_run"):
                print("[DRY RUN] TwiML preview:")
                print(result["twiml"])
                print(f"\nWould call: {result['to']} from {result['from']}")
                print(f"Message: {result['message']}")
            else:
                print("Call initiated successfully!")
                print(f"Call SID: {result['call_sid']}")
                print(f"Status: {result['status']}")
                print(f"From: {result['from']}")
                print(f"To: {result['to']}")
                print(f"Message: {result['message']}")
        else:
            eprint(result["error"])
            return 3 if "TWILIO_API_ERROR" in result.get("error_code", "") else 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
