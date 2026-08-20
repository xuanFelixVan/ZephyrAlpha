# [BLUEPRINT] MOD-SELL-017 | docs/03_modules/_domain_sell_decision/blueprint.md
# [MODULE] tests.sell_decision.test_scaling_out
# [DOMAIN] D_SELL_DECISION
# [INVARIANTS] 三步状态机序; 首批1/3; 保本价=入场价; trailing=Chandelier(22,2.0); ATR缺失降级8%; 输入非正拒绝
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidScalingOutInputError
# [TESTS] self
# [TTL] permanent
"""MOD-SELL-017 simple_scaling_out 三步法测试（42 号 §3.7，AI-NIGHT-001 包P）。"""

from __future__ import annotations

from decimal import Decimal

import pytest

from zephyr.sell_decision.core.scaling_out import (
    InvalidScalingOutInputError,
    ScalingOutActionType,
    ScalingOutPositionView,
    ScalingOutState,
    simple_scaling_out,
)


def _position(risk_reward: float, qty: str = "300", entry: str = "10.00") -> ScalingOutPositionView:
    return ScalingOutPositionView(quantity=Decimal(qty), entry_price=Decimal(entry), risk_reward=risk_reward)


class TestStepSequencing:
    def test_step1_sell_first_tranche_at_1r(self):
        action = simple_scaling_out(
            _position(risk_reward=1.0),
            ScalingOutState(),
            Decimal("0.30"),
            lambda n: 12.0,
        )
        assert action.action is ScalingOutActionType.SELL
        assert action.quantity == Decimal("300") * Decimal("0.33")
        assert action.reason == "TAKE_PROFIT_1"

    def test_step1_not_triggered_below_1r(self):
        action = simple_scaling_out(
            _position(risk_reward=0.8),
            ScalingOutState(),
            Decimal("0.30"),
            lambda n: 12.0,
        )
        assert action.action is ScalingOutActionType.HOLD_WITH_TRAILING

    def test_step2_move_stop_to_breakeven(self):
        action = simple_scaling_out(
            _position(risk_reward=1.2),
            ScalingOutState(first_tranche_sold=True),
            Decimal("0.30"),
            lambda n: 12.0,
        )
        assert action.action is ScalingOutActionType.MOVE_STOP
        assert action.price == Decimal("10.00")
        assert action.reason == "BREAKEVEN"

    def test_step3_trailing_chandelier(self):
        # highest(22)=12.0, ATR=0.30 → trailing = 12.0 - 2.0×0.30 = 11.40
        action = simple_scaling_out(
            _position(risk_reward=1.5),
            ScalingOutState(first_tranche_sold=True, stop_at_breakeven=True),
            Decimal("0.30"),
            lambda n: 12.0,
        )
        assert action.action is ScalingOutActionType.HOLD_WITH_TRAILING
        assert action.price == Decimal("11.40")
        assert action.reason == "TRAILING"

    def test_full_three_step_progression(self):
        state = ScalingOutState()
        a1 = simple_scaling_out(_position(1.1), state, Decimal("0.3"), lambda n: 12.0)
        assert a1.action is ScalingOutActionType.SELL
        state = ScalingOutState(first_tranche_sold=True)
        a2 = simple_scaling_out(_position(1.1), state, Decimal("0.3"), lambda n: 12.0)
        assert a2.action is ScalingOutActionType.MOVE_STOP
        state = ScalingOutState(first_tranche_sold=True, stop_at_breakeven=True)
        a3 = simple_scaling_out(_position(1.1), state, Decimal("0.3"), lambda n: 12.0)
        assert a3.action is ScalingOutActionType.HOLD_WITH_TRAILING


class TestDegradation:
    def test_atr_missing_fallback_8pct(self):
        # highest=12.0 → trailing = 12.0×0.92 = 11.04
        action = simple_scaling_out(
            _position(1.5),
            ScalingOutState(first_tranche_sold=True, stop_at_breakeven=True),
            None,
            lambda n: 12.0,
        )
        assert action.price == Decimal("11.04")

    def test_atr_zero_also_fallback(self):
        action = simple_scaling_out(
            _position(1.5),
            ScalingOutState(first_tranche_sold=True, stop_at_breakeven=True),
            Decimal("0"),
            lambda n: 12.0,
        )
        assert action.price == Decimal("11.04")


class TestInputValidation:
    def test_zero_quantity_rejected(self):
        with pytest.raises(InvalidScalingOutInputError):
            simple_scaling_out(_position(1.5, qty="0"), ScalingOutState(), Decimal("0.3"), lambda n: 12.0)

    def test_non_positive_entry_rejected(self):
        with pytest.raises(InvalidScalingOutInputError):
            simple_scaling_out(_position(1.5, entry="0"), ScalingOutState(), Decimal("0.3"), lambda n: 12.0)

    def test_non_positive_highest_close_rejected(self):
        with pytest.raises(InvalidScalingOutInputError):
            simple_scaling_out(
                _position(1.5),
                ScalingOutState(first_tranche_sold=True, stop_at_breakeven=True),
                Decimal("0.3"),
                lambda n: 0.0,
            )

    def test_lookback_passed_to_fn(self):
        seen: list[int] = []
        simple_scaling_out(
            _position(1.5),
            ScalingOutState(first_tranche_sold=True, stop_at_breakeven=True),
            Decimal("0.3"),
            lambda n: seen.append(n) or 12.0,
        )
        assert seen == [22]  # 盈利区 N=22（42 号 §3.3）
