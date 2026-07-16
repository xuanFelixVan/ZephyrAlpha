# [BLUEPRINT] MOD-INF-005 | scripts/governance/update_progress.py | §
# [MODULE] scripts.governance.update_progress
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
#!/usr/bin/env python
"""
update_progress.py — 从 domain_progress.json 批量更新施工进度.

DOM-GOV-001 §7 运维脚本.
用法: python scripts/governance/update_progress.py [module_id] [progress_pct]
"""

from __future__ import annotations

__manifest__ = """
args: []
description: update_progress.py — 从 domain_progress.json 批量更新施工进度.
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT as PROJECT_ROOT

PROGRESS_FILE = PROJECT_ROOT / "docs" / "03_modules" / "_domain-governance" / "domain_progress.json"


def load() -> dict:
    """load implementation."""
    if not PROGRESS_FILE.exists():
        return {}
    return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))


def save(data: dict) -> None:
    """save implementation."""
    data["last_updated"] = datetime.now(UTC).isoformat()
    tmp = str(PROGRESS_FILE) + f".{__import__('os').getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    __import__("os").replace(tmp, str(PROGRESS_FILE))


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    if len(sys.argv) < 3:
        print("Usage: python update_progress.py <module_id> <progress_pct>")
        print("Example: python update_progress.py MOD-INF-018 100")
        return EXIT_FINDINGS

    module_id = sys.argv[1]
    progress = int(sys.argv[2])

    data = load()
    modules = data.get("modules", {})
    for name, info in modules.items():
        if info.get("module_id") == module_id:
            info["progress"] = progress
            print(f"Updated {name} ({module_id}): {progress}%")
            break
    else:
        print(f"Module {module_id} not found in domain_progress.json")
        return EXIT_FINDINGS

    save(data)
    print("Progress saved.")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
