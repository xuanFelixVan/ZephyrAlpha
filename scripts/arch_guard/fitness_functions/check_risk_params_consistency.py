# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/fitness_functions/check_risk_params_consistency.py | §
# [MODULE] scripts.arch_guard.fitness_functions.check_risk_params_consistency
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
"""
check_risk_params_consistency.py — 风控参数真源 (INV-013) + 与 INV-002 声明对齐

  - 要求 config/risk_params.yaml 存在且含 max_single_position_nav_ratio（与 INV-002 5% 一致）
  - 扫描 src/zephyr 是否至少引用 RiskLimits 契约或 risk 限额语义（轻量引用检测）

exit: 0=pass, 1=fail
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_GOV_DIR = _ROOT.parent / "governance"
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

from _shared.constants import REPO_ROOT  # noqa: E402

from _arch_ssot import RISK_PARAMS_PATH, load_yaml  # noqa: E402

# INV-002: 单一持仓 ≤ 5% NAV
_EXPECTED_NAV = 0.05

_REF_PATTERNS = [
    re.compile(r"risk_params\.yaml", re.IGNORECASE),
    re.compile(r"RiskLimits\b"),
    re.compile(r"max_single_position"),
    re.compile(r"risk_params"),
]

def main() -> int:
    if not RISK_PARAMS_PATH.is_file():
        print("FAIL: 缺少 config/risk_params.yaml（INV-013 真源）")
        return 1

    cfg = load_yaml(RISK_PARAMS_PATH)
    nav = cfg.get("max_single_position_nav_ratio")
    if nav is None:
        print("FAIL: risk_params 缺少 max_single_position_nav_ratio")
        return 1
    if abs(float(nav) - _EXPECTED_NAV) > 1e-6:
        print(f"FAIL: max_single_position_nav_ratio={nav} 与 INV-002 期望 {_EXPECTED_NAV} 不一致")
        return 1

    src_root = REPO_ROOT / "src" / "zephyr"
    hits = 0
    if src_root.is_dir():
        for py in src_root.rglob("*.py"):
            if "__pycache__" in py.parts:
                continue
            try:
                text = py.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if any(p.search(text) for p in _REF_PATTERNS):
                hits += 1
    if hits < 1:
        print("WARN: src/zephyr 未发现 risk_params / RiskLimits 引用（骨架阶段仅警告，计数 0）")
        # 闭环：至少契约层应有 RiskLimits；检查 contract 文件存在
        risk_contract = REPO_ROOT / "src/zephyr/shared/contracts/risk_limits.py"
        if not risk_contract.is_file():
            print("FAIL: 缺少 src/zephyr/shared/contracts/risk_limits.py")
            return 1
        print("OK: risk_params 真源存在且与 INV-002 对齐；引用计数待业务代码接入后升高")
    else:
        print(f"OK: risk_params 真源存在；发现 {hits} 个源码文件含风险参数 / 契约引用")

    return 0

if __name__ == "__main__":
    sys.exit(main())
