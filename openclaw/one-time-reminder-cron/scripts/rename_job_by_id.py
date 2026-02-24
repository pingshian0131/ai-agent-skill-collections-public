#!/usr/bin/env python3
import argparse
import time

from _cronlib import load_jobs, write_jobs, backup_file

DEFAULT_JOBS_PATH = "{baseDir}/cron/jobs.json"


def main():
    ap = argparse.ArgumentParser(description="Rename an OpenClaw cron job by id.")
    ap.add_argument("--jobs", default=DEFAULT_JOBS_PATH)
    ap.add_argument("--id", required=True)
    ap.add_argument("--name", required=True)
    args = ap.parse_args()

    data = load_jobs(args.jobs)
    jobs = data.get("jobs", [])
    job = next((j for j in jobs if j.get("id") == args.id), None)

    backup = backup_file(args.jobs)
    if job is None:
        print(f"not_found backup={backup}")
        return

    job["name"] = args.name
    job["updatedAtMs"] = int(time.time() * 1000)
    write_jobs(args.jobs, data)
    print(f"renamed id={args.id} backup={backup}")


if __name__ == "__main__":
    main()
