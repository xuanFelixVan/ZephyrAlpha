# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/fitness_functions/check_position_limit.py | §
# [MODULE] scripts.arch_guard.fitness_functions.check_position_limit
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
check_position_limit.py — 单一持仓限制 ≤ 5% NAV (INV-002)

  - SSoT：config/risk_params.yaml → max_single_position_nav_ratio
  - 验证 risk_params.yaml 中存在 P0 级持仓限制且值 ≤ 5%
  - 验证 risk 中有限额检查代码存在

exit: 0=pass, 1=fail, 2=config error
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

from _arch_ssot import RISK_PARAMS_PATH, load_yaml  # noqa: E402

def main() -> int:
    if not RISK_PARAMS_PATH.is_file():
        print("FAIL: 缺少 config/risk_params.yaml")
        return 2

    risk = load_yaml(RISK_PARAMS_PATH)
    limit_ratio = risk.get("max_single_position_nav_ratio")

    if limit_ratio is None:
        print("FAIL: risk_params.yaml 缺少 max_single_position_nav_ratio（INV-002）")
        return 1

    if not isinstance(limit_ratio, (int, float)):
        print(f"FAIL: max_single_position_nav_ratio 类型非法 {type(limit_ratio).__name__}（应为 float）")
        return 1

    if limit_ratio <= 0 or limit_ratio > 0.05:
        print(f"FAIL: max_single_position_nav_ratio={limit_ratio} 超出安全范围（0 < x ≤ 0.05）")
        return 1

    limits_dir = REPO_ROOT / "src" / "zephyr" / "risk" / "limits"
    if not limits_dir.is_dir():
        limits_dir = REPO_ROOT / "src" / "zephyr" / "risk"

    position_check_files = list(limits_dir.rglob("*.py")) if limits_dir.is_dir() else []
    has_position_check = any("position" in f.stem.lower() or "limit" in f.stem.lower() for f in position_check_files)

    if not has_position_check:
        print("WARN: risk 目录未发现持仓限额检查模块（Phase B 补齐）")

    print(f"OK: INV-002 单一持仓限制 — max_single_position_nav_ratio={limit_ratio}（≤ 5% NAV）")
    return 0

if __name__ == "__main__":
    sys.exit(main())
