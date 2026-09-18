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

import csv
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
            broker = QmtFileBridgeBroker(env="sim", sync_interval=0.1, http_port=None)  # 测试封闭化：禁 HTTP 快路径（默认 18901 会打真 EXEC）
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


class TestHttpFastPath:
    """HTTP 桥快路径测试（93 号备忘 §12：HTTP 主通道+文件桥降级）"""

    @pytest.fixture
    def temp_bridge_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def broker(self, temp_bridge_dir):
        config = QmtFileBridgeBroker.ENV_CONFIG["sim"].copy()
        config["bridge_dir"] = str(temp_bridge_dir)
        config["orders_file"] = str(temp_bridge_dir / "orders_sim.csv")
        config["ack_file"] = str(temp_bridge_dir / "ack_sim.csv")
        config["stock_dir"] = str(temp_bridge_dir / "Stock")
        with patch.object(QmtFileBridgeBroker, "ENV_CONFIG", {"sim": config}):
            b = QmtFileBridgeBroker(env="sim", http_port=18999)  # 无监听的端口
            b.connect()
            yield b
            b.disconnect()

    @staticmethod
    def _make_order(oid: str) -> Order:
        return Order(
            order_id=oid,
            idempotency_key=oid,
            symbol="510300.SH",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("4.50"),
            strategy_id="test",
        )

    def test_http_success_skips_file(self, broker, temp_bridge_dir):
        """HTTP 受理（200）时不写指令文件（快路径独占）"""
        with patch.object(broker, "_http_post_order", return_value=True):
            broker.submit_order(self._make_order("HP-001"))
        content = (temp_bridge_dir / "orders_sim.csv").read_text(encoding="ascii")
        assert "HP-001" not in content
        assert broker.query_order("HP-001").status == OrderStatus.SUBMITTED

    def test_http_fail_degrades_to_file(self, broker, temp_bridge_dir):
        """HTTP 失败自动降级写指令文件（fail-open 兜底）"""
        with patch.object(broker, "_http_post_order", return_value=False):
            broker.submit_order(self._make_order("HP-002"))
        content = (temp_bridge_dir / "orders_sim.csv").read_text(encoding="ascii")
        assert "HP-002,order,510300.SH,buy,100,limit,4.5" in content

    def test_http_down_by_default(self, broker):
        """端口无监听时 _http_post_order 返回 False（连接拒绝路径）"""
        assert broker._http_post_order("X,order,510300.SH,buy,100,limit,4.00") is False


class TestDistinctKeyPairing:
    """P0-1 回归：order_id 与 idempotency_key 为独立 uuid4（OM.create_order 生产形态）

    柜台侧 remark=指令 order_id 列=idempotency_key；挂单同步/成交配对/撤单都必须
    经 remark 解析回本地 order_id（qmt_file_bridge_broker 双键配对视图）。
    历史教训：旧测试全部以两键相同造单，掩盖配对断裂（深度审查 rpt_x08 P0-1）。
    """

    @pytest.fixture
    def temp_bridge_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def broker(self, temp_bridge_dir):
        config = QmtFileBridgeBroker.ENV_CONFIG["sim"].copy()
        config["bridge_dir"] = str(temp_bridge_dir)
        config["orders_file"] = str(temp_bridge_dir / "orders_sim.csv")
        config["ack_file"] = str(temp_bridge_dir / "ack_sim.csv")
        config["stock_dir"] = str(temp_bridge_dir / "Stock")
        with patch.dict(QmtFileBridgeBroker.ENV_CONFIG, {"sim": config}):
            b = QmtFileBridgeBroker(env="sim", sync_interval=0.1, http_port=None)  # 测试封闭化：禁 HTTP 快路径（默认 18901 会打真 EXEC）
            b.connect()
            yield b
            b.disconnect()

    @staticmethod
    def _make_order() -> Order:
        return Order(
            order_id="oid-1",
            idempotency_key="idem-abc-123",
            symbol="510300.SH",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("4.50"),
            strategy_id="strat-a",
        )

    def test_order_sync_pairs_by_remark(self, broker, temp_bridge_dir):
        """柜台挂单以 remark（=idem）回查：broker_order_id 回填+状态推进必须命中"""
        order = self._make_order()
        assert broker.submit_order(order) == "oid-1"

        row = [""] * 26
        row[9] = "idem-abc-123"
        row[10] = "510300"
        row[11] = "510300.SH"
        row[13] = "4.50"
        row[14] = "100"
        row[15] = "SYS-001"
        row[16] = "已报"
        row[17] = "0"
        row[25] = "买入"
        with open(temp_bridge_dir / "Stock" / "Order.csv", "a", encoding="gbk", newline="") as f:
            csv.writer(f).writerow(row)

        broker._mirror.sync_all(broker._pairing_cache, broker._dispatch_fill)
        assert order.broker_order_id == "SYS-001"
        assert order.status == OrderStatus.SUBMITTED
        assert broker.query_order("oid-1") is order

    def test_fill_pairs_back_to_local_order_id(self, broker, temp_bridge_dir):
        """柜台成交 remark=idem：Fill.order_id 必须解析回本地 order_id（OM 配对键）"""
        order = self._make_order()
        broker.submit_order(order)
        fills: list = []
        broker._fill_callbacks.append(fills.append)

        row = [""] * 24
        row[9] = "idem-abc-123"
        row[11] = "510300"
        row[12] = "510300.SH"
        row[14] = "D-001"
        row[17] = "4.50"
        row[18] = "100"
        row[19] = "20260918"
        row[20] = "093001"
        row[21] = "5.10"
        row[23] = "买入"
        with open(temp_bridge_dir / "Stock" / "Deal.csv", "a", encoding="gbk", newline="") as f:
            csv.writer(f).writerow(row)

        broker._mirror.sync_all(broker._pairing_cache, broker._dispatch_fill)
        assert len(fills) == 1
        assert fills[0].order_id == "oid-1"
        assert fills[0].strategy_id == "strat-a"
        assert order.status == OrderStatus.FILLED

    def test_cancel_targets_remark(self, broker, temp_bridge_dir):
        """撤单指令 symbol 列必须写 remark（柜台配对键），而非本地 order_id"""
        order = self._make_order()
        broker.submit_order(order)
        assert broker.cancel_order("oid-1") is True
        content = (temp_bridge_dir / "orders_sim.csv").read_text(encoding="ascii")
        assert "Coid-1,cancel,idem-abc-123,,0,,0.0" in content


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
