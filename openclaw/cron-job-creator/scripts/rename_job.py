#!/usr/bin/env python3
import argparse

from _cron_registry import load_registry, backup_registry, write_registry, now_ms, DEFAULT_JOBS_PATH


def main():
    ap = argparse.ArgumentParser(description="Rename an OpenClaw job by id.")
    ap.add_argument("--jobs", default=DEFAULT_JOBS_PATH)
    ap.add_argument("--id", required=True)
    ap.add_argument("--name", required=True)
    args = ap.parse_args()

    reg = load_registry(args.jobs)
    jobs = reg.get("jobs", [])
    job = next((j for j in jobs if j.get("id") == args.id), None)

    if not job:
        print(f"not_found id={args.id}")
        return

    bak = backup_registry(args.jobs)
    job["name"] = args.name
    job["updatedAtMs"] = now_ms()
    write_registry(reg, args.jobs)
    print(f"renamed id={args.id} backup={bak}")


if __name__ == "__main__":
    main()
