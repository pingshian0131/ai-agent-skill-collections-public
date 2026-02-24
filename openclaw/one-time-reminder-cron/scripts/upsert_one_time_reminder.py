#!/usr/bin/env python3
import argparse
import uuid
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from _cronlib import load_jobs, write_jobs, backup_file, cron_expr_for_datetime

DEFAULT_JOBS_PATH = "{baseDir}/cron/jobs.json"
TEMPLATE_NAME = "One-time reminder (edit time + content)"
DEFAULT_CHANNEL = "telegram"
DEFAULT_TO = "YOUR_CHAT_ID_HERE"  # TODO: Replace with your Telegram chat ID
DEFAULT_AGENT = "YOUR_AGENT_HERE"  # TODO: Replace with your agent name


def parse_when(s: str, tz: str) -> datetime:
    # Accept: "YYYY-MM-DD HH:MM"
    dt = datetime.strptime(s, "%Y-%m-%d %H:%M")
    return dt.replace(tzinfo=ZoneInfo(tz))


def main():
    ap = argparse.ArgumentParser(description="Create/update the OpenClaw one-time reminder template job.")
    ap.add_argument("--jobs", default=DEFAULT_JOBS_PATH)
    ap.add_argument("--when", required=True, help='e.g. "2026-02-24 06:00"')
    ap.add_argument("--tz", default="Asia/Taipei")
    ap.add_argument("--message", required=True)
    ap.add_argument("--to", default=DEFAULT_TO)
    ap.add_argument("--channel", default=DEFAULT_CHANNEL)
    ap.add_argument("--agent", default=DEFAULT_AGENT)
    args = ap.parse_args()

    dt = parse_when(args.when, args.tz)
    expr = cron_expr_for_datetime(dt)

    data = load_jobs(args.jobs)
    jobs = data.get("jobs", [])

    now_ms = int(time.time() * 1000)

    # Find template by name
    job = next((j for j in jobs if j.get("name") == TEMPLATE_NAME), None)

    backup = backup_file(args.jobs)

    if job is None:
        job = {
            "id": str(uuid.uuid4()),
            "agentId": args.agent,
            "name": TEMPLATE_NAME,
            "enabled": True,
            "notify": True,
            "createdAtMs": now_ms,
            "updatedAtMs": now_ms,
            "schedule": {"kind": "cron", "expr": expr, "tz": args.tz},
            "sessionTarget": "isolated",
            "wakeMode": "now",
            "payload": {
                "kind": "agentTurn",
                "thinking": "off",
                "message": args.message,
            },
            "delivery": {
                "mode": "announce",
                "channel": args.channel,
                "to": args.to,
                "bestEffort": True,
            },
            "state": {"consecutiveErrors": 0},
        }
        jobs.append(job)
        data["jobs"] = jobs
        write_jobs(args.jobs, data)
        print(f"created id={job['id']} backup={backup} expr={expr} tz={args.tz}")
        return

    # Update existing
    job["enabled"] = True
    job["notify"] = True
    job["updatedAtMs"] = now_ms
    job["schedule"] = {"kind": "cron", "expr": expr, "tz": args.tz}
    job.setdefault("payload", {})
    job["payload"]["kind"] = "agentTurn"
    job["payload"]["thinking"] = "off"
    job["payload"]["message"] = args.message
    job["delivery"] = {
        "mode": "announce",
        "channel": args.channel,
        "to": args.to,
        "bestEffort": True,
    }
    job.setdefault("state", {})
    job["state"].setdefault("consecutiveErrors", 0)

    write_jobs(args.jobs, data)
    print(f"updated id={job['id']} backup={backup} expr={expr} tz={args.tz}")


if __name__ == "__main__":
    main()
