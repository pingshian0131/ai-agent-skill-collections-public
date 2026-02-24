#!/usr/bin/env python3
import argparse
import copy
import uuid

from _cron_registry import load_registry, backup_registry, write_registry, now_ms, DEFAULT_JOBS_PATH


def main():
    ap = argparse.ArgumentParser(description="Clone an OpenClaw job by id.")
    ap.add_argument("--jobs", default=DEFAULT_JOBS_PATH)
    ap.add_argument("--id", required=True, help="source job id")
    ap.add_argument("--new-name", required=True)
    ap.add_argument("--enable", choices=["true", "false"], default="true")
    args = ap.parse_args()

    reg = load_registry(args.jobs)
    jobs = reg.get("jobs", [])
    src = next((j for j in jobs if j.get("id") == args.id), None)

    if not src:
        print(f"not_found id={args.id}")
        return

    bak = backup_registry(args.jobs)

    j = copy.deepcopy(src)
    j["id"] = str(uuid.uuid4())
    j["name"] = args.new_name
    j["enabled"] = args.enable == "true"
    j["createdAtMs"] = now_ms()
    j["updatedAtMs"] = now_ms()
    # state should reset
    j["state"] = {"consecutiveErrors": 0}

    jobs.append(j)
    reg["jobs"] = jobs
    write_registry(reg, args.jobs)
    print(f"cloned new_id={j['id']} from={args.id} backup={bak}")


if __name__ == "__main__":
    main()
