#!/usr/bin/env python3
import argparse
import time

from _cronlib import load_jobs, write_jobs, backup_file

DEFAULT_JOBS_PATH = "{baseDir}/cron/jobs.json"


def main():
    ap = argparse.ArgumentParser(description="Disable an OpenClaw cron job by exact name.")
    ap.add_argument("--jobs", default=DEFAULT_JOBS_PATH)
    ap.add_argument("--name", required=True)
    args = ap.parse_args()

    data = load_jobs(args.jobs)
    jobs = data.get("jobs", [])
    target = [j for j in jobs if j.get("name") == args.name]

    backup = backup_file(args.jobs)
    now_ms = int(time.time() * 1000)

    if not target:
        print(f"not_found backup={backup}")
        return

    for j in target:
        j["enabled"] = False
        j["updatedAtMs"] = now_ms

    write_jobs(args.jobs, data)
    print(f"disabled count={len(target)} backup={backup}")


if __name__ == "__main__":
    main()
