#!/usr/bin/env python3
import argparse

from _cron_registry import load_registry, DEFAULT_JOBS_PATH


def main():
    ap = argparse.ArgumentParser(description="List OpenClaw cron jobs.")
    ap.add_argument("--jobs", default=DEFAULT_JOBS_PATH)
    args = ap.parse_args()

    reg = load_registry(args.jobs)
    jobs = reg.get("jobs", [])

    for j in jobs:
        sched = j.get("schedule", {})
        if sched.get("kind") == "cron":
            s = f"cron {sched.get('expr')} tz={sched.get('tz')}"
        else:
            s = f"every {sched.get('everyMs')}ms"
        print(f"{j.get('id')}\t{('EN' if j.get('enabled') else 'DIS')}\t{j.get('agentId')}\t{j.get('name')}\t{s}")


if __name__ == "__main__":
    main()
