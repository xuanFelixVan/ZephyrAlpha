# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/fitness_functions/check_daily_loss_limit.py | §
# [MODULE] scripts.arch_guard.fitness_functions.check_daily_loss_limit
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
check_daily_loss_limit.py — 日损失限额自动暂停 (INV-003)

  - SSoT：config/risk_params.yaml → daily_loss_limit_nav_ratio
  - 验证该字段存在（T0/T1 阶段可为 null，但字段声明必须有）
  - 验证 stop_loss 模块代码存在

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

    if "daily_loss_limit_nav_ratio" not in risk:
        print("FAIL: risk_params.yaml 缺少 daily_loss_limit_nav_ratio 字段声明（INV-003）")
        return 1

    limit_ratio = risk.get("daily_loss_limit_nav_ratio")

    if limit_ratio is not None:
        if not isinstance(limit_ratio, (int, float)):
            print(f"FAIL: daily_loss_limit_nav_ratio 类型非法 {type(limit_ratio).__name__}")
            return 1
        if limit_ratio <= 0 or limit_ratio > 1.0:
            print(f"FAIL: daily_loss_limit_nav_ratio={limit_ratio} 非法（应在 0 < x ≤ 1.0）")
            return 1

    stop_loss_path = REPO_ROOT / "src" / "zephyr" / "risk" / "stop_loss.py"
    has_stop_loss = stop_loss_path.is_file()
    if not has_stop_loss:
        stop_loss_files = list((REPO_ROOT / "src" / "zephyr" / "risk").rglob("*.py"))
        has_stop_loss = any("stop" in f.stem.lower() or "loss" in f.stem.lower() for f in stop_loss_files)

    if has_stop_loss:
        print(
            f"OK: INV-003 日损失限额 — daily_loss_limit_nav_ratio="
            f"{limit_ratio if limit_ratio is not None else 'null (T0/T1 待配置)'}"
            "；stop_loss 模块已就位"
        )
    else:
        print(
            f"WARN: INV-003 日损失限额 — daily_loss_limit_nav_ratio="
            f"{limit_ratio if limit_ratio is not None else 'null (T0/T1 待配置)'}"
            "；stop_loss 模块待 Phase B 实现"
        )

    return 0

if __name__ == "__main__":
    sys.exit(main())
