# [BLUEPRINT] MOD-INF-005 | scripts/governance/sync_progress.py | §
#!/usr/bin/env python
"""
sync_progress.py — 从 domain_progress.json 同步进度到 §2 模块清单表.

DOM-GOV-001 §2 + §7 运维脚本体系.
用法: python scripts/governance/sync_progress.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROGRESS_FILE = PROJECT_ROOT / "docs" / "03_modules" / "_domain-governance" / "domain_progress.json"


def load_progress() -> dict:
    """load_progress implementation."""
    if not PROGRESS_FILE.exists():
        return {}
    return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))


def save_progress(data: dict) -> None:
    """save_progress implementation."""
    ts = datetime.now(timezone.utc).isoformat()
    data["last_updated"] = ts
    tmp = str(PROGRESS_FILE) + f".{__import__('os').getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    __import__("os").replace(tmp, str(PROGRESS_FILE))


def sync_all() -> dict:
    """Synchronize target with source of truth."""
    data = load_progress()
    if not data:
        print("ERROR: domain_progress.json 不存在", file=sys.stderr)
        return {"error": "domain_progress.json not found"}

    total_progress = 0
    module_count = 0
    for mod_name, mod_data in data.get("modules", {}).items():
        module_count += 1
        total_progress += mod_data.get("progress", 0)

    avg = total_progress / module_count if module_count > 0 else 0
    data["aggregate_progress"] = round(avg, 1)

    save_progress(data)

    print(f"Synced: {module_count} modules, avg progress: {avg:.1f}%")
    return data


if __name__ == "__main__":
    result = sync_all()
    print(json.dumps(result, indent=2, ensure_ascii=False))
