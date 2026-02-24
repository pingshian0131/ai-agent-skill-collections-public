#!/usr/bin/env python3
import argparse

from _cron_registry import load_registry, backup_registry, write_registry, DEFAULT_JOBS_PATH


def main():
    ap = argparse.ArgumentParser(description="Delete an OpenClaw job by id.")
    ap.add_argument("--jobs", default=DEFAULT_JOBS_PATH)
    ap.add_argument("--id", required=True)
    args = ap.parse_args()

    reg = load_registry(args.jobs)
    jobs = reg.get("jobs", [])
    idx = next((i for i, j in enumerate(jobs) if j.get("id") == args.id), None)

    if idx is None:
        print(f"not_found id={args.id}")
        return

    bak = backup_registry(args.jobs)
    removed = jobs.pop(idx)
    write_registry(reg, args.jobs)
    print(f"deleted id={args.id} name={removed.get('name')} backup={bak}")


if __name__ == "__main__":
    main()
