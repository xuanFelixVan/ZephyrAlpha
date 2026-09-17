# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md
# [MODULE] tests.ex_core.test_qmt_trading_session
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.qmt_trading_session
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] draft
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L06-001-QMTFB | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""QMT TradingSession 单元测试"""

from __future__ import annotations

import tempfile
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.ex_core.adapters.qmt_file_bridge_broker import QmtFileBridgeBroker
from zephyr.ex_core.qmt_trading_session import QmtTradingSession
from zephyr.governance.strategies.strategy_base import StrategyBase
from zephyr.shared.contracts.order import OrderSide, OrderType


class DummyStrategy(StrategyBase):
    """测试策略：固定权重"""

    def generate_target_weights(self, universe, signals, constraints):
        return {symbol: 1.0 / len(universe) for symbol in universe}


class TestQmtTradingSession:
    """QmtTradingSession 测试"""

    @pytest.fixture
    def temp_bridge_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def mock_providers(self):
        signal_provider = MagicMock(return_value={"510300.SH": 0.5})
        price_provider = MagicMock(return_value={"510300.SH": Decimal("4.50")})
        return signal_provider, price_provider

    def test_init_sim(self, temp_bridge_dir, mock_providers):
        """初始化（模拟环境）"""
        signal_provider, price_provider = mock_providers

        config = QmtFileBridgeBroker.ENV_CONFIG["sim"].copy()
        config["bridge_dir"] = str(temp_bridge_dir)
        config["orders_file"] = str(temp_bridge_dir / "orders_sim.csv")
        config["ack_file"] = str(temp_bridge_dir / "ack_sim.csv")
        config["stock_dir"] = str(temp_bridge_dir / "Stock")

        with patch.dict(QmtFileBridgeBroker.ENV_CONFIG, {"sim": config}):
            session = QmtTradingSession(
                env="sim",
                universe=["510300.SH"],
                strategy=DummyStrategy(),
                signal_provider=signal_provider,
                price_provider=price_provider,
            )
            assert session._env == "sim"
            assert session._broker_id == "qmt_sim"

    def test_init_invalid_env(self, mock_providers):
        """非法环境"""
        signal_provider, price_provider = mock_providers

        with pytest.raises(ValueError, match="非法环境标识"):
            QmtTradingSession(
                env="invalid",
                universe=["510300.SH"],
                strategy=DummyStrategy(),
                signal_provider=signal_provider,
                price_provider=price_provider,
            )


class TestInflightDeduction:
    """rpt_x01 P1 回归：rebalance delta 必须抵扣同侧在途单（防重复触发双下单）"""

    @staticmethod
    def _make_session():
        from zephyr.ex_core.trading_session import TradingSession, TradingSessionConfig

        return TradingSession(
            broker=MagicMock(),
            strategy=DummyStrategy(),
            risk_validator=MagicMock(),
            signal_provider=MagicMock(return_value={}),
            price_provider=MagicMock(return_value={}),
            order_manager=MagicMock(),
            config=TradingSessionConfig(universe=["510300.SH"]),
        )

    @staticmethod
    def _fake_order(symbol: str, side, qty: Decimal, filled: Decimal, status):
        from types import SimpleNamespace

        return SimpleNamespace(
            symbol=symbol,
            side=side,
            quantity=qty,
            filled_quantity=filled,
            status=status,
        )

    @staticmethod
    def _positions():
        from types import SimpleNamespace

        return SimpleNamespace(
            cash=Decimal("10000"),
            total_market_value=Decimal("0"),
            holdings={},
        )

    def test_fully_covered_inflight_produces_no_order(self):
        """在途买单已覆盖全部目标增量 → 二次 rebalance 不得再出同向单"""
        from types import SimpleNamespace

        from zephyr.shared.contracts.enums.order_enums import OrderStatus

        session = self._make_session()
        session._order_manager = SimpleNamespace(
            orders={
                "o1": self._fake_order(
                    "510300.SH", OrderSide.BUY, Decimal("2300"), Decimal("0"), OrderStatus.SUBMITTED
                )
            }
        )
        deltas = session._compute_order_deltas(
            {"510300.SH": 1.0}, self._positions(), {"510300.SH": Decimal("4.50")}
        )
        assert all(o.side != OrderSide.BUY for o in deltas)

    def test_partial_inflight_deducted(self):
        """部分覆盖 → 新单量=原始 delta−在途量，而非全量重复"""
        from types import SimpleNamespace

        from zephyr.shared.contracts.enums.order_enums import OrderStatus

        session = self._make_session()
        session._order_manager = SimpleNamespace(
            orders={
                "o1": self._fake_order(
                    "510300.SH", OrderSide.BUY, Decimal("100"), Decimal("0"), OrderStatus.SUBMITTED
                )
            }
        )
        deltas = session._compute_order_deltas(
            {"510300.SH": 1.0}, self._positions(), {"510300.SH": Decimal("4.50")}
        )
        buys = [o for o in deltas if o.side == OrderSide.BUY]
        assert len(buys) == 1
        assert buys[0].quantity < Decimal("2200")  # 必须小于未抵扣的全量

    def test_om_failure_fails_open_with_warning(self):
        """OM 读取异常时按无在途处理（保底仍出 delta，不静默丢调仓）"""
        session = self._make_session()
        session._order_manager = None  # 触发 AttributeError
        deltas = session._compute_order_deltas(
            {"510300.SH": 1.0}, self._positions(), {"510300.SH": Decimal("4.50")}
        )
        assert deltas  # 降级路径仍产出订单


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
