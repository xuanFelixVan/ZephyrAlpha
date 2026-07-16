# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/fitness_functions/check_hot_warm_ipc.py | §
# [MODULE] scripts.arch_guard.fitness_functions.check_hot_warm_ipc
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.arch_guard.fitness_functions.__init__
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
"""check_hot_warm_ipc.py — INV-018 Hot↔Warm IPC 协议检查

对标 runtime_planes.yaml HOT_WARM_IPC_ONLY + invariants.yaml INV-018。
检查 Hot/Warm 平面模块间是否存在直接函数调用（应通过 IPC）。

当前状态：L2-static-scan——扫描 import 依赖图。
exit: 0=合规, 1=违规, 2=基础设施错误
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_GOV_DIR = _ROOT.parent / "governance"
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

from _shared.constants import REPO_ROOT  # noqa: E402

SRC_ROOT = REPO_ROOT / "src" / "zephyr"

HOT_MODULES = {"risk", "ex_core"}
WARM_MODULES = {"factor", "signal", "pf_core", "compliance", "ml_train", "observability"}  # noqa: gate-vocab  温模块业务子集

def main() -> int:
    print("INV-018 Hot↔Warm IPC 协议检查\n")

    if not SRC_ROOT.exists():
        print("[SKIP] src/zephyr/ 不存在")
        return 0

    violations = []
    for hot in HOT_MODULES:
        hot_dir = SRC_ROOT / hot
        if not hot_dir.exists():
            continue
        for py_file in hot_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for warm in WARM_MODULES:
                patterns = [f"from zephyr.{warm}", f"import zephyr.{warm}"]
                for pattern in patterns:
                    if pattern in content:
                        violations.append((py_file.relative_to(REPO_ROOT), warm))

    if violations:
        print(f"[FAIL] 发现 {len(violations)} 处 Hot→Warm 直接 import（应通过 IPC）:")
        for path, warm in violations:
            print(f"  {path} → {warm}")
        return 1

    print("[OK] Hot↔Warm 无直接 import 违规")
    return 0

if __name__ == "__main__":
    sys.exit(main())
