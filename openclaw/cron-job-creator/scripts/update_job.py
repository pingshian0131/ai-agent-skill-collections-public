#!/usr/bin/env python3
import argparse
import json

from _cron_registry import load_registry, backup_registry, write_registry, now_ms, DEFAULT_JOBS_PATH


def main():
    ap = argparse.ArgumentParser(description="Update fields of an existing OpenClaw job.")
    ap.add_argument("--jobs", default=DEFAULT_JOBS_PATH)
    ap.add_argument("--id", required=True)

    ap.add_argument("--name", default=None)
    ap.add_argument("--agentId", default=None)
    ap.add_argument("--enabled", choices=["true", "false"], default=None)
    ap.add_argument("--notify", choices=["true", "false"], default=None)

    ap.add_argument("--schedule-kind", choices=["cron", "every"], default=None)
    ap.add_argument("--cron", default=None)
    ap.add_argument("--tz", default=None)
    ap.add_argument("--every-ms", type=int, default=None)
    ap.add_argument("--anchor-ms", type=int, default=None)

    ap.add_argument("--payload-kind", choices=["agentTurn", "systemEvent"], default=None)
    ap.add_argument("--message", default=None)
    ap.add_argument("--thinking", default=None)
    ap.add_argument("--model", default=None)
    ap.add_argument("--timeoutSeconds", type=int, default=None)

    ap.add_argument("--delivery-channel", default=None)
    ap.add_argument("--delivery-to", default=None)

    args = ap.parse_args()

    reg = load_registry(args.jobs)
    jobs = reg.get("jobs", [])
    job = next((j for j in jobs if j.get("id") == args.id), None)

    if not job:
        print(f"not_found id={args.id}")
        return

    changed = []

    if args.name is not None:
        job["name"] = args.name
        changed.append("name")
    if args.agentId is not None:
        job["agentId"] = args.agentId
        changed.append("agentId")
    if args.enabled is not None:
        job["enabled"] = args.enabled == "true"
        changed.append("enabled")
    if args.notify is not None:
        job["notify"] = args.notify == "true"
        changed.append("notify")

    # Schedule updates
    sched = job.setdefault("schedule", {})
    if args.schedule_kind is not None:
        sched["kind"] = args.schedule_kind
        changed.append("schedule.kind")
    if args.cron is not None:
        sched["expr"] = args.cron
        changed.append("schedule.expr")
    if args.tz is not None:
        sched["tz"] = args.tz
        changed.append("schedule.tz")
    if args.every_ms is not None:
        sched["everyMs"] = args.every_ms
        changed.append("schedule.everyMs")
    if args.anchor_ms is not None:
        sched["anchorMs"] = args.anchor_ms
        changed.append("schedule.anchorMs")

    # Payload updates
    payload = job.setdefault("payload", {})
    if args.payload_kind is not None:
        payload["kind"] = args.payload_kind
        changed.append("payload.kind")
    if args.message is not None:
        if payload.get("kind") == "agentTurn":
            payload["message"] = args.message
        else:
            payload["text"] = args.message
        changed.append("payload.message")
    if args.thinking is not None:
        payload["thinking"] = args.thinking
        changed.append("payload.thinking")
    if args.model is not None:
        payload["model"] = args.model
        changed.append("payload.model")
    if args.timeoutSeconds is not None:
        payload["timeoutSeconds"] = args.timeoutSeconds
        changed.append("payload.timeoutSeconds")

    # Delivery updates
    delivery = job.setdefault("delivery", {})
    if args.delivery_channel is not None:
        delivery["channel"] = args.delivery_channel
        changed.append("delivery.channel")
    if args.delivery_to is not None:
        delivery["to"] = args.delivery_to
        changed.append("delivery.to")

    if not changed:
        print(f"no_changes id={args.id}")
        return

    bak = backup_registry(args.jobs)
    job["updatedAtMs"] = now_ms()
    write_registry(reg, args.jobs)
    print(f"updated id={args.id} fields={','.join(changed)} backup={bak}")


if __name__ == "__main__":
    main()
