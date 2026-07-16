# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/fitness_functions/check_warm_cold_async.py | §
# [MODULE] scripts.arch_guard.fitness_functions.check_warm_cold_async
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
"""check_warm_cold_async.py — INV-019 Warm→Cold 异步通信检查

对标 runtime_planes.yaml WARM_COLD_ASYNC_ONLY + invariants.yaml INV-019。
检查 Warm→Cold 调用是否使用异步机制（Parquet/Redis Streams），而非同步阻塞。

当前状态：L2-static-scan——扫描同步调用 pattern。
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

WARM_MODULES = {"factor", "signal", "pf_core", "compliance", "ml_train", "observability"}  # noqa: gate-vocab  温模块业务子集
COLD_MODULES = {"data", "pf_core", "research", "integration"}  # noqa: gate-vocab  冷模块业务子集

BLOCKING_PATTERNS = ["requests.get", "requests.post", "urllib.request", "subprocess.run", "subprocess.call"]

def main() -> int:
    print("INV-019 Warm→Cold 异步通信检查\n")

    if not SRC_ROOT.exists():
        print("[SKIP] src/zephyr/ 不存在")
        return 0

    violations = []
    for warm in WARM_MODULES:
        warm_dir = SRC_ROOT / warm
        if not warm_dir.exists():
            continue
        for py_file in warm_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for cold in COLD_MODULES:
                for pattern in BLOCKING_PATTERNS:
                    if cold in content and pattern in content:
                        violations.append((py_file.relative_to(REPO_ROOT), cold, pattern))

    if violations:
        print(f"[FAIL] 发现 {len(violations)} 处 Warm→Cold 同步阻塞调用:")
        for path, cold, pattern in violations:
            print(f"  {path} → {cold} via {pattern}")
        return 1

    print("[OK] Warm→Cold 无同步阻塞违规")
    return 0

if __name__ == "__main__":
    sys.exit(main())
