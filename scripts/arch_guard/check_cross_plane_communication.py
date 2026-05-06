"""
check_cross_plane_communication.py — INV-011 拓扑 + 静态越界 import 嗅探

  - 读取 capacity_slo.arch_guard.deployment_topology.cold_to_hot_requires_warm_shadow 须为 true
  - 扫描 l00/l02/l13 路径下 Python：禁止 import zephyr.l06_trade_execution

exit: 0=pass, 1=fail
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from _arch_ssot import CAPACITY_SLO_PATH, REPO_ROOT, load_yaml  # noqa: E402

_FORBIDDEN = re.compile(
    r"from\s+zephyr\.l06_trade_execution\b|import\s+zephyr\.l06_trade_execution",
    re.IGNORECASE,
)
_COLD_PREFIXES = ("l00_data_source", "l02_alpha_factor", "l13_experiment")


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
        print("FAIL: Cold/因子侧代码直接 import l06_trade_execution（疑似绕过 Warm/Shadow）:")
        for v in violations:
            print(f"  - {v}")
        return 1

    print("OK: deployment_topology 声明满足；未发现 l00/l02/l13 路径对 l06 的直连 import")
    return 0


if __name__ == "__main__":
    sys.exit(main())
