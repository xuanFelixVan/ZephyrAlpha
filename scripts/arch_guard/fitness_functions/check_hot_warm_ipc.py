"""check_hot_warm_ipc.py — INV-018 Hot↔Warm IPC 协议检查

对标 runtime-planes.yaml HOT_WARM_IPC_ONLY + invariants.yaml INV-018。
检查 Hot/Warm 平面模块间是否存在直接函数调用（应通过 IPC）。

当前状态：L2-static-scan——扫描 import 依赖图。
exit: 0=合规, 1=违规, 2=基础设施错误
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src" / "zephyr"

HOT_MODULES = {"l04_risk_management", "l06_trade_execution"}
WARM_MODULES = {"l02_alpha_factor", "l03_signal_generation", "l05_portfolio_construction", "l10_compliance", "l11_ml_platform", "l12_system_telemetry"}


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
