# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md
# [MODULE] tests.ex_core.adapters.test_qmt_file_bridge_broker
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.adapters.qmt_file_bridge_broker
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
"""QMT File Bridge Broker 单元测试"""

from __future__ import annotations

import tempfile
import time
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.ex_core.adapters.qmt_file_bridge_broker import (
    FileBridgeInstruction,
    QmtFileBridgeBroker,
    QmtFileBridgeError,
    check_broker_health,
)
from zephyr.shared.contracts.order import Order, OrderSide, OrderStatus, OrderType


class TestQmtFileBridgeBroker:
    """QmtFileBridgeBroker 测试"""

    @pytest.fixture
    def temp_bridge_dir(self):
        """临时桥接目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def broker(self, temp_bridge_dir):
        """测试用 Broker（模拟环境，临时目录）"""
        config = QmtFileBridgeBroker.ENV_CONFIG["sim"].copy()
        config["bridge_dir"] = str(temp_bridge_dir)
        config["orders_file"] = str(temp_bridge_dir / "orders_sim.csv")
        config["ack_file"] = str(temp_bridge_dir / "ack_sim.csv")
        config["stock_dir"] = str(temp_bridge_dir / "Stock")

        with patch.dict(QmtFileBridgeBroker.ENV_CONFIG, {"sim": config}):
            broker = QmtFileBridgeBroker(env="sim", sync_interval=0.1)
            yield broker
            broker.disconnect()

    def test_broker_id(self, broker):
        """broker_id 格式"""
        assert broker.broker_id == "qmt_sim"

    def test_connect_creates_directories(self, broker, temp_bridge_dir):
        """connect 创建目录和文件"""
        assert broker.connect() is True
        assert (temp_bridge_dir / "Stock").exists()
        assert (temp_bridge_dir / "orders_sim.csv").exists()
        assert (temp_bridge_dir / "ack_sim.csv").exists()

    def test_submit_order_writes_instruction(self, broker, temp_bridge_dir):
        """submit_order 写入指令行"""
        broker.connect()

        order = Order(
            order_id="test-001",
            idempotency_key="test-001",
            symbol="510300.SH",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("4.50"),
            strategy_id="test",
        )

        order_id = broker.submit_order(order)
        assert order_id == "test-001"

        # 验证指令文件
        orders_file = temp_bridge_dir / "orders_sim.csv"
        content = orders_file.read_text(encoding="ascii")
        assert "test-001,order,510300.SH,buy,100,limit,4.5" in content

        # 验证缓存
        cached = broker.query_order("test-001")
        assert cached is not None
        assert cached.status == OrderStatus.SUBMITTED

    def test_submit_order_idempotency(self, broker):
        """幂等拦截"""
        broker.connect()

        order = Order(
            order_id="test-002",
            idempotency_key="test-002",
            symbol="510300.SH",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("100"),
            strategy_id="test",
        )

        id1 = broker.submit_order(order)
        id2 = broker.submit_order(order)  # 重复提交

        assert id1 == id2 == "test-002"

    def test_submit_order_validation(self, broker):
        """A股约束校验"""
        broker.connect()

        # 数量不足 100 股
        order = Order(
            order_id="test-003",
            idempotency_key="test-003",
            symbol="510300.SH",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("50"),
            limit_price=Decimal("4.50"),
            strategy_id="test",
        )

        with pytest.raises(QmtFileBridgeError, match="数量不合法"):
            broker.submit_order(order)

    def test_cancel_order_writes_instruction(self, broker, temp_bridge_dir):
        """cancel_order 写入撤单指令"""
        broker.connect()

        # 先下一个单
        order = Order(
            order_id="test-004",
            idempotency_key="test-004",
            symbol="510300.SH",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("4.50"),
            strategy_id="test",
        )
        broker.submit_order(order)

        # 撤单
        result = broker.cancel_order("test-004")
        assert result is True

        # 验证撤单指令
        orders_file = temp_bridge_dir / "orders_sim.csv"
        content = orders_file.read_text(encoding="ascii")
        assert "Ctest-004,cancel,test-004,,0,,0.0" in content

    def test_get_positions_empty(self, broker, temp_bridge_dir):
        """空持仓查询"""
        broker.connect()

        # 创建空 CSV
        stock_dir = temp_bridge_dir / "Stock"
        (stock_dir / "PositionStatics.csv").write_text("", encoding="gbk")
        (stock_dir / "Account.csv").write_text("", encoding="gbk")

        snapshot = broker.get_positions()
        assert snapshot.cash == Decimal("0")
        assert snapshot.holdings == {}

    def test_invalid_env(self):
        """非法环境标识"""
        with pytest.raises(QmtFileBridgeError, match="非法环境标识"):
            QmtFileBridgeBroker(env="invalid")

    def test_health_check_not_connected(self, broker):
        """健康检查：未连接 → down"""
        h = check_broker_health(broker)
        assert h["level"] == "down"
        assert h["connected"] is False

    def test_health_check_connected_no_exports(self, broker):
        """健康检查：已连接但官方导出缺失 → degraded"""
        broker.connect()
        h = check_broker_health(broker)
        assert h["level"] == "degraded"
        assert h["sync_thread_alive"] is True
        assert "导出" in h["detail"]
        broker.disconnect()

    def test_health_check_connected_with_exports(self, broker, temp_bridge_dir):
        """健康检查：已连接且导出新鲜 → ok"""
        broker.connect()
        stock_dir = temp_bridge_dir / "Stock"
        for name in ("Order.csv", "PositionStatics.csv", "Account.csv", "Deal.csv"):
            (stock_dir / name).write_text("", encoding="gbk")
        h = check_broker_health(broker)
        assert h["level"] == "ok"
        assert h["ok"] is True
        assert h["export_age_seconds"]["Order.csv"] is not None
        broker.disconnect()


class TestFileBridgeInstruction:
    """指令数据结构测试"""

    def test_instruction_fields(self):
        inst = FileBridgeInstruction(
            order_id="T001",
            action="order",
            symbol="510300.SH",
            side="buy",
            qty=100,
            pricetype="limit",
            price=4.50,
        )
        assert inst.order_id == "T001"
        assert inst.action == "order"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
