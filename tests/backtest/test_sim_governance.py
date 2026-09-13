# [BLUEPRINT] MOD-BT-095 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_sim_governance
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; scripts.backtest.sim_governance
# [CONSUMERS] 治理建议生成器质量守卫（MODIFY-GUARD）
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] recommend() 纯函数合成史测试（不依赖 CH）；流转建议只产不改册
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-BT-141 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""sim_governance 质量守卫——流转建议规则的纯函数断言。"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "sim_governance", _REPO / "scripts" / "backtest" / "sim_governance.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["sim_governance"] = mod
spec.loader.exec_module(mod)


def _hist(*reasons: str) -> list[dict]:
    return [{"batch": f"SIM-DEV-2026-{i:02d}", "reason": r, "notes": ""}
            for i, r in enumerate(reasons, 1)]


def test_two_pass_promotes():
    rec, why = mod.recommend(_hist("monthly_pass", "monthly_pass"))
    assert rec == "promote_paper" and "连续 2 月" in why


def test_two_breach_demotes():
    rec, _ = mod.recommend(_hist("monthly_pass", "monthly_breach", "monthly_breach"))
    assert rec == "demote_decayed"


def test_single_month_no_action():
    rec, _ = mod.recommend(_hist("monthly_pass"))
    assert rec is None


def test_consecutive_flag_demotes():
    rec, _ = mod.recommend(_hist("monthly_breach_consecutive"))
    assert rec == "demote_decayed"
