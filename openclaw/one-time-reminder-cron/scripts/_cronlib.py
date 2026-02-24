import json
import shutil
import time
from pathlib import Path

def load_jobs(path: str) -> dict:
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8"))

def backup_file(path: str) -> str:
    p = Path(path)
    ts = time.strftime("%Y%m%d-%H%M%S")
    bak = p.with_suffix(p.suffix + f".{ts}.bak")
    shutil.copy2(p, bak)
    return str(bak)

def write_jobs(path: str, data: dict) -> None:
    p = Path(path)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def cron_expr_for_datetime(dt, *, tz_note: str = "") -> str:
    # dt is assumed already in the intended timezone.
    # OpenClaw cron format: "m h dom mon dow".
    # We set dow to * and rely on dom+mon. This will recur yearly unless disabled after run.
    return f"{dt.minute} {dt.hour} {dt.day} {dt.month} *"
