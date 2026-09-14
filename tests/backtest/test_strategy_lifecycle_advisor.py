# [BLUEPRINT] MOD-BT-187-test | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_strategy_lifecycle_advisor
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest
# [CONSUMERS] MOD-BT-187 质量守卫
# [TESTS] tests/backtest/test_strategy_lifecycle_advisor.py
# [A_module] module_id=MOD-BT-187-test | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""lifecycle 流转建议器规则纯函数测试（不连 CH）。"""
from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts" / "backtest"
sys.path.insert(0, str(_SCRIPTS))

from strategy_lifecycle_advisor import advise, compute_decay  # noqa: E402


class TestComputeDecay:
    def test_formula_matches_runner(self):
        # 与 c4_batch_screen OOS 批公式一致：(-0.089 - -0.242)/0.089/2.5 = 0.6876（实弹对账值）
        assert compute_decay(-0.089, -0.242) == 0.6876

    def test_clamps(self):
        assert compute_decay(0.1, -3.0) == 1.0, "恶化超界钳顶"
        assert compute_decay(-2.2, -1.165) == 0.0, "改善向钳零（漂亮50 实弹对账值）"


class TestAdvise:
    def test_reject_both_negative(self):
        assert advise(-0.31, -0.61)[0] == "reject"

    def test_decay_watch_line(self):
        verdict, reason = advise(0.876, -0.966)
        assert verdict == "decay_watch" and "0.5" in reason

    def test_candidate(self):
        assert advise(0.9, 0.6)[0] == "candidate"

    def test_hold_insufficient(self):
        assert advise(None, 0.5)[0] == "hold"
        assert advise(0.3, 0.4)[0] == "hold", "未达双侧线且未越存疑线=维持现状"
