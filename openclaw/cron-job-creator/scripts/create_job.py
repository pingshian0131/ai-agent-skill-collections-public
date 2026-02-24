#!/usr/bin/env python3
import argparse
import uuid

from _cron_registry import load_registry, backup_registry, write_registry, now_ms, DEFAULT_JOBS_PATH


def main():
    ap = argparse.ArgumentParser(description="Create an OpenClaw cron job entry in jobs.json.")
    ap.add_argument("--jobs", default=DEFAULT_JOBS_PATH)

    ap.add_argument("--name", required=True)
    ap.add_argument("--agentId", required=True)
    ap.add_argument("--enabled", type=lambda s: s.lower() == "true", default=True)
    ap.add_argument("--notify", type=lambda s: s.lower() == "true", default=True)

    ap.add_argument("--schedule-kind", choices=["cron", "every"], required=True)
    ap.add_argument("--cron", help='cron expr "m h dom mon dow" when --schedule-kind=cron')
    ap.add_argument("--tz", default="Asia/Taipei")
    ap.add_argument("--every-ms", type=int, help="interval ms when --schedule-kind=every")
    ap.add_argument("--anchor-ms", type=int, help="anchor ms when --schedule-kind=every (default now)")

    ap.add_argument("--sessionTarget", default="isolated", choices=["isolated", "main"])
    ap.add_argument("--wakeMode", default="now", choices=["now"])

    ap.add_argument("--payload-kind", default="agentTurn", choices=["agentTurn", "systemEvent"])
    ap.add_argument("--message", help="payload message (agentTurn.message or systemEvent.text)")
    ap.add_argument("--thinking", default="off")
    ap.add_argument("--model", default=None)
    ap.add_argument("--timeoutSeconds", type=int, default=None)

    ap.add_argument("--delivery-mode", default="announce", choices=["announce"])
    ap.add_argument("--delivery-channel", default="telegram")
    ap.add_argument("--delivery-to", required=True)
    ap.add_argument("--bestEffort", type=lambda s: s.lower() == "true", default=True)

    args = ap.parse_args()

    if not args.message:
        ap.error("--message is required")

    schedule = {"kind": args.schedule_kind}
    if args.schedule_kind == "cron":
        if not args.cron:
            ap.error("--cron required when --schedule-kind=cron")
        schedule.update({"expr": args.cron, "tz": args.tz})
    else:
        if not args.every_ms:
            ap.error("--every-ms required when --schedule-kind=every")
        schedule.update({"everyMs": args.every_ms, "anchorMs": args.anchor_ms or now_ms()})

    payload = {"kind": args.payload_kind}
    if args.payload_kind == "agentTurn":
        payload.update({"thinking": args.thinking, "message": args.message})
        if args.model:
            payload["model"] = args.model
        if args.timeoutSeconds is not None:
            payload["timeoutSeconds"] = args.timeoutSeconds
    else:
        payload["text"] = args.message

    job = {
        "id": str(uuid.uuid4()),
        "agentId": args.agentId,
        "name": args.name,
        "enabled": args.enabled,
        "notify": args.notify,
        "createdAtMs": now_ms(),
        "updatedAtMs": now_ms(),
        "schedule": schedule,
        "sessionTarget": args.sessionTarget,
        "wakeMode": args.wakeMode,
        "payload": payload,
        "delivery": {
            "mode": args.delivery_mode,
            "channel": args.delivery_channel,
            "to": args.delivery_to,
            "bestEffort": args.bestEffort,
        },
        "state": {"consecutiveErrors": 0},
    }

    reg = load_registry(args.jobs)
    reg.setdefault("jobs", [])

    bak = backup_registry(args.jobs)
    reg["jobs"].append(job)
    write_registry(reg, args.jobs)

    print(f"created id={job['id']} backup={bak}")


if __name__ == "__main__":
    main()
