# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/fitness_functions/check_survivorship_bias.py | §
# [MODULE] scripts.arch_guard.fitness_functions.check_survivorship_bias
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
check_survivorship_bias.py — Survivorship 策略门禁 (INV-014)

  - 读取 config/survivorship_policy.yaml
  - 要求 require_delisted_symbols_in_backtest == true（声明级闭环）

exit: 0=pass, 1=fail
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from _arch_ssot import SURVIVORSHIP_POLICY_PATH, load_yaml  # noqa: E402


def main() -> int:
    if not SURVIVORSHIP_POLICY_PATH.is_file():
        print("FAIL: 缺少 config/survivorship_policy.yaml")
        return 1

    pol = load_yaml(SURVIVORSHIP_POLICY_PATH)
    if pol.get("require_delisted_symbols_in_backtest") is not True:
        print("FAIL: require_delisted_symbols_in_backtest 必须为 true")
        return 1
    if pol.get("require_suspend_flags_in_universe") is not True:
        print("FAIL: require_suspend_flags_in_universe 必须为 true")
        return 1

    print("OK: survivorship 策略开关已启用（数据集证据由 D_DATA manifest 后续补强）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
