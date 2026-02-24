import json
import shutil
import time
from pathlib import Path

DEFAULT_JOBS_PATH = "/home/node/.openclaw/cron/jobs.json"


def load_registry(path: str = DEFAULT_JOBS_PATH) -> dict:
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8"))


def backup_registry(path: str = DEFAULT_JOBS_PATH) -> str:
    p = Path(path)
    ts = time.strftime("%Y%m%d-%H%M%S")
    bak = p.with_suffix(p.suffix + f".{ts}.bak")
    shutil.copy2(p, bak)
    return str(bak)


def write_registry(data: dict, path: str = DEFAULT_JOBS_PATH) -> None:
    p = Path(path)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def now_ms() -> int:
    return int(time.time() * 1000)
