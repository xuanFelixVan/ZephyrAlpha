"""t1_sellable（T+1 可卖持仓口径工具）单元测试。

覆盖：31号 遗留 #30 / 32号 §6 T+1 口径行——
- 可卖权重 = 昨仓 − 今日已卖
- 今日买入 T+1 冻结（不在输入域）
- 负值兜底 0（Fail-Closed）/ 非法输入 ValueError / 退化用例
"""

from __future__ import annotations

import pytest

from zephyr.position.core.t1_sellable import t1_sellable_weights


class TestT1SellableWeights:
    def test_no_sells_passthrough(self) -> None:
        """今日无卖出 → 可卖=昨仓原样。"""
        w = t1_sellable_weights({"A": 0.05, "B": 0.03})
        assert w == {"A": 0.05, "B": 0.03}

    def test_none_solds_passthrough(self) -> None:
        """today_sold_weights=None → 可卖=昨仓。"""
        w = t1_sellable_weights({"A": 0.05}, None)
        assert w["A"] == pytest.approx(0.05)

    def test_partial_sell_deducted(self) -> None:
        """今日卖出部分从昨仓扣减。"""
        w = t1_sellable_weights({"A": 0.05, "B": 0.03}, {"A": 0.02})
        assert w["A"] == pytest.approx(0.03)
        assert w["B"] == pytest.approx(0.03)

    def test_full_sell_to_zero(self) -> None:
        """昨仓全卖 → 可卖=0（标的保留，权重 0）。"""
        w = t1_sellable_weights({"A": 0.05}, {"A": 0.05})
        assert w["A"] == pytest.approx(0.0)

    def test_oversell_clipped_to_zero(self) -> None:
        """卖出>昨仓（数据异常）→ 负值兜底 0（只缩不增 Fail-Closed）。"""
        w = t1_sellable_weights({"A": 0.03}, {"A": 0.08})
        assert w["A"] == pytest.approx(0.0)

    def test_sold_symbol_not_in_holdings_ignored(self) -> None:
        """今卖中出现的非持仓标的忽略（昨仓未持有无可卖）。"""
        w = t1_sellable_weights({"A": 0.05}, {"B": 0.02})
        assert w == {"A": 0.05}

    def test_empty_holdings(self) -> None:
        """空仓（退化）→ 空结果。"""
        assert t1_sellable_weights({}) == {}

    def test_invalid_weights_raise(self) -> None:
        """负值/NaN/Inf 输入 → ValueError。"""
        with pytest.raises(ValueError):
            t1_sellable_weights({"A": -0.01})
        with pytest.raises(ValueError):
            t1_sellable_weights({"A": float("nan")})
        with pytest.raises(ValueError):
            t1_sellable_weights({"A": 0.05}, {"A": float("inf")})
