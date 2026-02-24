#!/usr/bin/env python3
import argparse

from _cron_registry import load_registry, backup_registry, write_registry, now_ms, DEFAULT_JOBS_PATH


def main():
    ap = argparse.ArgumentParser(description="Enable/disable an OpenClaw job by id.")
    ap.add_argument("--jobs", default=DEFAULT_JOBS_PATH)
    ap.add_argument("--id", required=True)
    ap.add_argument("--enabled", required=True, choices=["true", "false"])
    args = ap.parse_args()

    reg = load_registry(args.jobs)
    jobs = reg.get("jobs", [])
    job = next((j for j in jobs if j.get("id") == args.id), None)

    if not job:
        print(f"not_found id={args.id}")
        return

    bak = backup_registry(args.jobs)
    job["enabled"] = args.enabled == "true"
    job["updatedAtMs"] = now_ms()
    write_registry(reg, args.jobs)
    print(f"updated id={args.id} enabled={job['enabled']} backup={bak}")


if __name__ == "__main__":
    main()
