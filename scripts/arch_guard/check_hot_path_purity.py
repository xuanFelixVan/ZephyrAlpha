# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/check_hot_path_purity.py | §
# [MODULE] scripts.arch_guard.check_hot_path_purity
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.arch_guard.__init__
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
"""
check_hot_path_purity.py — INV-012 Hot 路径 Python 禁 asyncio（配置驱动）

  - 读取 capacity_slo.arch_guard.hot_path_python_scan.roots + forbid_asyncio

exit: 0=pass, 1=fail
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_GOV_DIR = _ROOT.parent / "governance"
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

from _shared.constants import REPO_ROOT  # noqa: E402

from _arch_ssot import CAPACITY_SLO_PATH, load_yaml  # noqa: E402

def main() -> int:
    slo = load_yaml(CAPACITY_SLO_PATH)
    hps = (slo.get("arch_guard") or {}).get("hot_path_python_scan") or {}
    if not hps.get("forbid_asyncio"):
        print("OK: hot_path_python_scan.forbid_asyncio 未启用 — 跳过")
        return 0

    roots = hps.get("roots") or []
    bad: list[str] = []
    for rel in roots:
        if not isinstance(rel, str):
            continue
        root = (REPO_ROOT / rel).resolve()
        if not root.is_dir():
            continue
        for py in root.rglob("*.py"):
            if "__pycache__" in py.parts:
                continue
            try:
                text = py.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if "asyncio" in text or "async def" in text:
                bad.append(str(py.relative_to(REPO_ROOT)))

    if bad:
        print("FAIL: Hot 路径目录下存在 asyncio / async def（INV-012）:")
        for b in bad:
            print(f"  - {b}")
        return 1

    print("OK: Hot 路径扫描根目录下无 asyncio 用法")
    return 0

if __name__ == "__main__":
    sys.exit(main())
