# [BLUEPRINT] MOD-EX-062 | docs/03_modules/MOD-EX-062/
# [MODULE] tests.ex_core.test_execution_strategy_selector
# [DOMAIN] D_EX_CORE
# [INVARIANTS] 纯函数确定性; 分档边界精确(<1%/1-5%/5-15%/>15%); ADV非正Fail-Closed; 超顶拒判留结构化details
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] StrategySelectionError
# [TESTS] self
# [TTL] permanent
"""执行策略选择器测试（MOD-EX-062，阶段9 执行链路批）。"""

from __future__ import annotations

from decimal import Decimal

import pytest

from zephyr.ex_core.execution_strategy_selector import (
    ExecutionStrategy,
    OrderFeatures,
    StrategySelectionError,
    select_execution_strategy,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide


def _features(quantity, adv, side=OrderSide.BUY):
    return OrderFeatures(
        symbol="600000.SH",
        side=side,
        quantity=Decimal(str(quantity)),
        adv=Decimal(str(adv)),
    )


class TestFailClosed:
    def test_zero_adv_rejected(self):
        with pytest.raises(StrategySelectionError) as exc_info:
            select_execution_strategy(_features(100, 0))
        assert exc_info.value.error_code == "ZA-EX-0020"

    def test_negative_adv_rejected(self):
        with pytest.raises(StrategySelectionError):
            select_execution_strategy(_features(100, -50000))

    def test_non_positive_quantity_rejected(self):
        with pytest.raises(StrategySelectionError):
            select_execution_strategy(_features(0, 100000))
        with pytest.raises(StrategySelectionError):
            select_execution_strategy(_features(-100, 100000))

    def test_over_15pct_adv_rejected(self):
        # §13.1 硬顶：>15% ADV 须上游拆分，本层拒判
        with pytest.raises(StrategySelectionError) as exc_info:
            select_execution_strategy(_features(16000, 100000))
        assert "15%" in exc_info.value.message
        assert exc_info.value.details["max_fraction"] == "0.15"


class TestTiering:
    def test_tiny_order_limit_direct(self):
        sel = select_execution_strategy(_features(500, 100000))  # 0.5%
        assert sel.strategy is ExecutionStrategy.LIMIT_DIRECT
        assert sel.suggested_slices == 1
        assert "限价直发" in sel.reason

    def test_boundary_1pct_goes_twap(self):
        sel = select_execution_strategy(_features(1000, 100000))  # 恰 1%
        assert sel.strategy is ExecutionStrategy.TWAP

    def test_medium_order_twap(self):
        sel = select_execution_strategy(_features(3000, 100000))  # 3%
        assert sel.strategy is ExecutionStrategy.TWAP
        assert 2 <= sel.suggested_slices <= 12

    def test_boundary_5pct_goes_vwap(self):
        sel = select_execution_strategy(_features(5000, 100000))  # 恰 5%
        assert sel.strategy is ExecutionStrategy.VWAP

    def test_large_order_vwap(self):
        sel = select_execution_strategy(_features(10000, 100000))  # 10%
        assert sel.strategy is ExecutionStrategy.VWAP
        assert sel.suggested_slices == 10
        assert "VWAP" in sel.reason

    def test_boundary_15pct_still_vwap(self):
        sel = select_execution_strategy(_features(15000, 100000))  # 恰 15%
        assert sel.strategy is ExecutionStrategy.VWAP
        assert sel.suggested_slices == 12  # 夹边上界

    def test_sell_side_same_tiers(self):
        sel = select_execution_strategy(_features(3000, 100000, side=OrderSide.SELL))
        assert sel.strategy is ExecutionStrategy.TWAP


class TestPurity:
    def test_same_input_same_output(self):
        a = select_execution_strategy(_features(3000, 100000))
        b = select_execution_strategy(_features(3000, 100000))
        assert a == b

    def test_adv_fraction_recorded(self):
        sel = select_execution_strategy(_features(3000, 100000))
        assert sel.adv_fraction == pytest.approx(0.03)
