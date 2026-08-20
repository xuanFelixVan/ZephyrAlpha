# [BLUEPRINT] MOD-L07-001 | docs/03_modules/_domain_reporting/blueprint.md
# [MODULE] tests.reporting.test_attribution
# [DOMAIN] D_REPORTING
# [INVARIANTS] fill_id幂等; FIFO配对; 求和不变量1bp门禁; Shapley效率公理; 裸卖空Fail-Closed
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidAttributionInputError
# [TESTS] self
# [TTL] permanent
"""54 号 §3.5/§3.12 归因函数级实现测试（AI-NIGHT-001 包P）。

覆盖：
  - StrategyPnlAccountant：买卖闭环净 PnL / FIFO 多批次部分卖出 / fill_id 幂等
    / 裸卖空拒绝 / 空 strategy_id 拒绝 / 买入费用即负 PnL / 跨 session 连续追踪
    / all_strategy_pnls 聚合 / open_positions 快照
  - validate_strategy_pnl_invariant：PASS/FAIL 1bp 门禁 / 零 firm_pnl 边界 / 非法容差
  - shapley_strategy_attribution：效率公理 / 等收益均分 / 单策略退化 / 空输入 /
    规模超限 / 序列不等长 / weights 缺项
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from zephyr.reporting.attribution import (
    SHAPLEY_MAX_STRATEGIES,
    InvalidAttributionInputError,
    StrategyPnlAccountant,
    shapley_strategy_attribution,
    validate_strategy_pnl_invariant,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide
from zephyr.shared.contracts.fill import Fill
from zephyr.trading.pnl_calculator import AShareFeeCalculator, FeeConfig

#: 免最低佣金费率（测试算术确定性）
_ZERO_MIN_FEE_CALC = AShareFeeCalculator(FeeConfig(commission_min=Decimal("0")))


def _fill(fill_id: str, symbol: str, price: str, qty: str, strategy: str = "S1") -> Fill:
    return Fill(
        fill_id=fill_id,
        fill_price=Decimal(price),
        fill_timestamp=datetime(2026, 8, 20, 10, 0, tzinfo=UTC),
        filled_quantity=Decimal(qty),
        idempotency_key=f"idem-{fill_id}",
        order_id=f"ord-{fill_id}",
        strategy_id=strategy,
        symbol=symbol,
    )


class TestStrategyPnlAccountant:
    def test_buy_sell_round_trip_net_pnl(self):
        acct = StrategyPnlAccountant(fee_calculator=_ZERO_MIN_FEE_CALC)
        buy_net = acct.record_fill(_fill("f1", "600000", "10.00", "100"), OrderSide.BUY)
        # 买入费用 1000×(0.00025+0.00001)=0.26，BUY realized = -费用
        assert buy_net == pytest.approx(Decimal("-0.26"))
        sell_net = acct.record_fill(_fill("f2", "600000", "11.00", "100"), OrderSide.SELL)
        # unit_cost=10.0026; gross=(11-10.0026)×100=99.74; 卖出费=0.275+0.55+0.011=0.836
        assert sell_net == pytest.approx(Decimal("98.904"))
        assert acct.strategy_net_pnl("S1") == pytest.approx(Decimal("98.644"))

    def test_fifo_partial_sell_multi_lot(self):
        acct = StrategyPnlAccountant(fee_calculator=_ZERO_MIN_FEE_CALC)
        acct.record_fill(_fill("f1", "600000", "10.00", "100"), OrderSide.BUY)
        acct.record_fill(_fill("f2", "600000", "12.00", "100"), OrderSide.BUY)
        # 卖 150：先撮合第一批 100@10.0026，再撮合第二批 50@12.00312
        acct.record_fill(_fill("f3", "600000", "11.00", "150"), OrderSide.SELL)
        snap = acct.open_positions("S1")
        assert snap["600000"].open_quantity == Decimal("50")
        assert acct.strategy_net_pnl("S1") > 0

    def test_duplicate_fill_id_idempotent(self):
        acct = StrategyPnlAccountant(fee_calculator=_ZERO_MIN_FEE_CALC)
        acct.record_fill(_fill("f1", "600000", "10.00", "100"), OrderSide.BUY)
        again = acct.record_fill(_fill("f1", "600000", "10.00", "100"), OrderSide.BUY)
        assert again == Decimal("0")
        assert acct.open_positions("S1")["600000"].open_quantity == Decimal("100")

    def test_sell_exceeding_holdings_fail_closed(self):
        acct = StrategyPnlAccountant(fee_calculator=_ZERO_MIN_FEE_CALC)
        acct.record_fill(_fill("f1", "600000", "10.00", "100"), OrderSide.BUY)
        with pytest.raises(InvalidAttributionInputError):
            acct.record_fill(_fill("f2", "600000", "11.00", "200"), OrderSide.SELL)

    def test_empty_strategy_id_rejected(self):
        acct = StrategyPnlAccountant(fee_calculator=_ZERO_MIN_FEE_CALC)
        with pytest.raises(InvalidAttributionInputError):
            acct.record_fill(_fill("f1", "600000", "10.00", "100", strategy=""), OrderSide.BUY)

    def test_non_positive_price_qty_rejected(self):
        acct = StrategyPnlAccountant(fee_calculator=_ZERO_MIN_FEE_CALC)
        with pytest.raises(InvalidAttributionInputError):
            acct.record_fill(_fill("f1", "600000", "0", "100"), OrderSide.BUY)
        with pytest.raises(InvalidAttributionInputError):
            acct.record_fill(_fill("f2", "600000", "10.00", "-5"), OrderSide.BUY)

    def test_cross_session_position_continuous(self):
        """跨 session 持仓连续：两批买入间隔再卖，不依赖 session_id 隔离。"""
        acct = StrategyPnlAccountant(fee_calculator=_ZERO_MIN_FEE_CALC)
        acct.record_fill(_fill("f1", "600000", "10.00", "100"), OrderSide.BUY)  # session A
        acct.record_fill(_fill("f2", "600000", "11.00", "100"), OrderSide.SELL)  # session B
        assert acct.strategy_net_pnl("S1") > 0
        assert "600000" not in acct.open_positions("S1")

    def test_all_strategy_pnls_aggregation(self):
        acct = StrategyPnlAccountant(fee_calculator=_ZERO_MIN_FEE_CALC)
        acct.record_fill(_fill("f1", "600000", "10.00", "100", strategy="S1"), OrderSide.BUY)
        acct.record_fill(_fill("f2", "600000", "11.00", "100", strategy="S1"), OrderSide.SELL)
        acct.record_fill(_fill("f3", "000001", "20.00", "100", strategy="S2"), OrderSide.BUY)
        pnls = acct.all_strategy_pnls()
        assert set(pnls) == {"S1", "S2"}
        assert pnls["S1"] > 0
        assert pnls["S2"] < 0  # S2 仅买入，净 PnL = -买入费用

    def test_open_positions_excludes_other_strategies(self):
        acct = StrategyPnlAccountant(fee_calculator=_ZERO_MIN_FEE_CALC)
        acct.record_fill(_fill("f1", "600000", "10.00", "100", strategy="S1"), OrderSide.BUY)
        acct.record_fill(_fill("f2", "000001", "20.00", "200", strategy="S2"), OrderSide.BUY)
        assert set(acct.open_positions("S1")) == {"600000"}
        assert acct.open_positions("S1")["600000"].open_quantity == Decimal("100")


class TestValidateStrategyPnlInvariant:
    def test_pass_within_1bp(self):
        result = validate_strategy_pnl_invariant({"S1": 60.0, "S2": 40.0}, 100.0)
        assert result["invariant_status"] == "PASS"
        assert result["diff"] == 0.0
        assert result["strategy_contributions"]["S1"]["contribution_ratio"] == pytest.approx(0.6)

    def test_fail_beyond_tolerance(self):
        result = validate_strategy_pnl_invariant({"S1": 60.0, "S2": 30.0}, 100.0)
        assert result["invariant_status"] == "FAIL"
        assert result["diff_bps"] == pytest.approx(1000.0)

    def test_zero_firm_pnl_edge(self):
        result = validate_strategy_pnl_invariant({"S1": 1.0}, 0.0)
        assert result["invariant_status"] == "PASS"  # firm=0 时 diff_bps 退化 0
        assert result["strategy_contributions"]["S1"]["contribution_ratio"] == 0.0

    def test_invalid_tolerance_rejected(self):
        with pytest.raises(InvalidAttributionInputError):
            validate_strategy_pnl_invariant({"S1": 1.0}, 1.0, tolerance_bps=0)


class TestShapleyAttribution:
    def test_efficiency_axiom_sum_equals_full(self):
        returns = {"S1": [0.01, -0.005, 0.002], "S2": [0.0, 0.01, -0.003], "S3": [0.005] * 3}
        result = shapley_strategy_attribution(returns)
        assert result["invariant_status"] == "PASS"
        assert result["sum_check"] == pytest.approx(result["full_portfolio_return"], abs=1e-9)

    def test_identical_strategies_equal_split(self):
        returns = {"S1": [0.01, 0.02], "S2": [0.01, 0.02]}
        result = shapley_strategy_attribution(returns)
        assert result["shapley_values"]["S1"] == pytest.approx(result["shapley_values"]["S2"], abs=1e-12)

    def test_single_strategy_gets_full_return(self):
        returns = {"S1": [0.01, 0.02]}
        result = shapley_strategy_attribution(returns)
        expected = 1.01 * 1.02 - 1
        assert result["shapley_values"]["S1"] == pytest.approx(expected, abs=1e-12)

    def test_zero_return_strategy_dilutes_compounding(self):
        # 复合收益口径下零收益策略稀释正收益策略（等权联盟日收益减半），
        # Shapley 边际贡献为负——交互效应公平分配的数学正确行为（非零）。
        returns = {"S1": [0.01, 0.01], "S2": [0.0, 0.0]}
        result = shapley_strategy_attribution(returns)
        assert result["shapley_values"]["S2"] < 0
        assert result["shapley_values"]["S1"] > result["full_portfolio_return"]
        assert result["invariant_status"] == "PASS"

    def test_empty_input_rejected(self):
        with pytest.raises(InvalidAttributionInputError):
            shapley_strategy_attribution({})

    def test_oversize_rejected(self):
        returns = {f"S{i}": [0.001] for i in range(SHAPLEY_MAX_STRATEGIES + 1)}
        with pytest.raises(InvalidAttributionInputError):
            shapley_strategy_attribution(returns)

    def test_unequal_length_rejected(self):
        with pytest.raises(InvalidAttributionInputError):
            shapley_strategy_attribution({"S1": [0.01], "S2": [0.01, 0.02]})

    def test_weights_missing_entry_rejected(self):
        with pytest.raises(InvalidAttributionInputError):
            shapley_strategy_attribution({"S1": [0.01], "S2": [0.02]}, weights={"S1": 1.0})

    def test_weighted_coalition(self):
        returns = {"S1": [0.01], "S2": [0.02]}
        result = shapley_strategy_attribution(returns, weights={"S1": 0.7, "S2": 0.3})
        assert result["invariant_status"] == "PASS"
