# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/check_cross_plane_communication.py | §
# [MODULE] scripts.arch_guard.check_cross_plane_communication
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
check_cross_plane_communication.py — INV-011 拓扑 + 静态越界 import 嗅探

  - 读取 capacity_slo.arch_guard.deployment_topology.cold_to_hot_requires_warm_shadow 须为 true
  - 扫描 l00/l02/l13 路径下 Python：禁止 import zephyr.ex_core

exit: 0=pass, 1=fail
"""

from __future__ import annotations

import re
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

_FORBIDDEN = re.compile(
    r"from\s+zephyr\.ex_core\b|import\s+zephyr\.ex_core",
    re.IGNORECASE,
)
_COLD_PREFIXES = ("data", "factor", "simulation")  # noqa: gate-vocab  冷层前缀业务子集

def main() -> int:
    slo = load_yaml(CAPACITY_SLO_PATH)
    topo = (slo.get("arch_guard") or {}).get("deployment_topology") or {}
    if topo.get("cold_to_hot_requires_warm_shadow") is not True:
        print("FAIL: deployment_topology.cold_to_hot_requires_warm_shadow 必须为 true（INV-011）")
        return 1

    src = REPO_ROOT / "src" / "zephyr"
    violations: list[str] = []
    if src.is_dir():
        for py in src.rglob("*.py"):
            if "__pycache__" in py.parts:
                continue
            parts = set(py.parts)
            is_coldish = any(p in parts for p in _COLD_PREFIXES)
            if not is_coldish:
                continue
            try:
                text = py.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if _FORBIDDEN.search(text):
                violations.append(str(py.relative_to(REPO_ROOT)))

    if violations:
        print("FAIL: Cold/因子侧代码直接 import ex_core（疑似绕过 Warm/Shadow）:")
        for v in violations:
            print(f"  - {v}")
        return 1

    print("OK: deployment_topology 声明满足；未发现 l00/l02/l13 路径对 l06 的直连 import")
    return 0

if __name__ == "__main__":
    sys.exit(main())
