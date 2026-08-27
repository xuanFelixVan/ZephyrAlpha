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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
