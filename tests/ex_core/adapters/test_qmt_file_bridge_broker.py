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
import os
import tempfile
import threading
import time
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import zephyr.ex_core.adapters.qmt_file_bridge_broker as bridge_mod
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


class TestTrdA10SilentDropAndCancelRace:
    """TRD-A10 桥客户端两缺陷证尺（隔夜单静默丢弃 + submit→cancel 竞态）

    判据真源=docs/_working/decision_map_campaign_20260924/17_quantified_acceptance.md §四
    案卷=docs/_working/three_piece_infra/p0_bridge/CASE.md
    封闭化：tmp_path 假文件 + 假时钟 + http_port=None（零 socket / 零柜台 / 零生产 data/ 写），
    后台同步线程用 sync_interval=3600 闲置，逐轮由测试显式驱动（确定性，不靠 sleep 竞争）。
    """

    class _Clock:
        def __init__(self, base: float):
            self.t = base

        def now(self) -> datetime:
            return datetime.fromtimestamp(self.t, tz=UTC)

        def advance(self, seconds: float) -> None:
            self.t += seconds

    class _Hub:
        PHANTOM_GRACE_S = 180.0
        CANCEL_HOLD_S = 20.0

        def __init__(self, root: Path, clock: TestTrdA10SilentDropAndCancelRace._Clock):
            self.root = root
            self.stock_dir = root / "Stock"
            self.stock_dir.mkdir(parents=True, exist_ok=True)
            self.clock = clock
            self.brokers: list[QmtFileBridgeBroker] = []

        def new_broker(self, *, connect: bool = False, **kwargs) -> QmtFileBridgeBroker:
            params: dict = {
                "env": "sim",
                "sync_interval": 3600.0,  # 线程闲置：逐轮由测试驱动
                "http_port": None,  # 禁 HTTP 快路径（默认 18901 会打真 EXEC）
            }
            params.update(kwargs)
            broker = QmtFileBridgeBroker(**params)
            self.brokers.append(broker)
            if connect:
                assert broker.connect() is True
            return broker

        def submit(self, broker, order_id: str, idem: str, *, quantity: str = "100") -> object:
            order = Order(
                order_id=order_id,
                idempotency_key=idem,
                symbol="510300.SH",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                quantity=Decimal(quantity),
                limit_price=Decimal("4.50"),
                strategy_id="trd-a10",
            )
            broker.submit_order(order)
            return order

        def instruction_lines(self, action: str) -> list[list[str]]:
            p = self.root / "orders_sim.csv"
            if not p.exists():
                return []
            out = []
            for raw in p.read_text(encoding="ascii").splitlines():
                if not raw or raw.startswith("order_id") or raw.startswith("#"):
                    continue
                cells = raw.split(",")
                if len(cells) >= 2 and cells[1] == action:
                    out.append(cells)
            return out

        def mark_lines(self, mark: str) -> list[str]:
            p = self.root / "orders_sim.csv"
            if not p.exists():
                return []
            return [ln for ln in p.read_text(encoding="ascii").splitlines() if ln.startswith(mark)]

        def write_counter_order(self, remark: str, status: str = "已报", *, stale_seconds: float | None = None) -> Path:
            row = [""] * 26
            row[9] = remark
            row[10] = "510300"
            row[11] = "510300.SH"
            row[13] = "4.50"
            row[14] = "100"
            row[15] = f"SYS-{remark}"
            row[16] = status
            row[17] = "0"
            row[25] = "买入"
            path = self.stock_dir / "Order.csv"
            with open(path, "a", encoding="gbk", newline="") as f:
                csv.writer(f).writerow(row)
            if stale_seconds is not None:
                ts = self.clock.t - stale_seconds
                os.utime(path, (ts, ts))
            return path

        def append_ack(self, line: str) -> None:
            path = self.root / "ack_sim.csv"
            with open(path, "a", encoding="ascii", newline="") as f:
                f.write(line + "\n")

        def advance(self, seconds: float, *, keep_export_fresh: bool = True) -> None:
            """推进假时钟；默认把柜台导出 mtime 一起前移（=柜台回读平面仍然新鲜）。

            不做这件事会让"时钟前移"被误判成"导出超龄"，从而触发幽灵单判定暂停防线，
            测试就打不到想打的分支（本班实测踩到，见 CASE.md §五）。
            """
            self.clock.advance(seconds)
            if keep_export_fresh:
                path = self.stock_dir / "Order.csv"
                if path.exists():
                    os.utime(path, (self.clock.t, self.clock.t))

        def append_mark(self, line: str) -> None:
            path = self.root / "orders_sim.csv"
            with open(path, "a", encoding="ascii", newline="") as f:
                f.write(line + "\n")

    @pytest.fixture
    def hub(self, tmp_path):
        config = QmtFileBridgeBroker.ENV_CONFIG["sim"].copy()
        config["bridge_dir"] = str(tmp_path)
        config["orders_file"] = str(tmp_path / "orders_sim.csv")
        config["ack_file"] = str(tmp_path / "ack_sim.csv")
        config["stock_dir"] = str(tmp_path / "Stock")
        clock = self._Clock(time.time())
        handle = TestTrdA10SilentDropAndCancelRace._Hub(tmp_path, clock)
        with (
            patch.dict(QmtFileBridgeBroker.ENV_CONFIG, {"sim": config}),
            patch("zephyr.ex_core.adapters.qmt_file_bridge_broker.now_utc", clock.now),
        ):
            yield handle
        for broker in handle.brokers:
            broker.disconnect()

    def test_phantom_claim_becomes_rejected_instead_of_stuck_submitted(self, hub):
        """缺陷①：柜台零收录的声称（隔夜单）必须超时拒单化，不得永远停在 SUBMITTED"""
        broker = hub.new_broker()
        hub.write_counter_order("somebody-elses-remark")  # 柜台视图新鲜且权威，但没有我们这张单
        order = hub.submit(broker, "oid-a1", "idem-a1")

        broker._sync_round()
        hub.advance(hub.PHANTOM_GRACE_S + 1)
        broker._sync_round()

        assert order.status == OrderStatus.REJECTED, (
            f"柜台零收录却停在 {order.status} —— 静默丢弃本体"
        )

    def test_drop_is_announced_through_alert_sink_exactly_once(self, hub):
        """缺陷①（变响）：丢弃路径必须经既有 alert_sink 出口外发一次，不是只写日志"""
        payloads: list[dict] = []
        broker = hub.new_broker(alert_sink=payloads.append)
        hub.write_counter_order("other-remark")
        hub.submit(broker, "oid-a2", "idem-a2")
        hub.advance(hub.PHANTOM_GRACE_S + 1)
        broker._sync_round()

        assert len(payloads) == 1, f"期望恰好 1 次告警外发，实得 {len(payloads)}"
        payload = payloads[0]
        assert payload["order_id"] == "oid-a2"
        assert payload["remark"] == "idem-a2"
        assert payload.get("reason")

        hub.advance(600)
        broker._sync_round()  # 已终态，不得重复外发（静默窗外的重复=告警风暴）
        assert len(payloads) == 1

    def test_client_self_stamped_done_and_sent_ack_are_not_counter_confirmation(self, hub):
        """缺陷①：客户端自盖 #DONE + SENT ack 不等于柜台收录，不得当作终态销案"""
        broker = hub.new_broker()
        hub.write_counter_order("other-remark")
        order = hub.submit(broker, "oid-a3", "idem-a3")
        hub.append_mark("#DONE idem-a3,order,510300.SH,buy,100,limit,4.5")
        hub.append_ack("idem-a3,SENT,accepted")

        broker._sync_round()  # 吃掉自盖章 + SENT 回执
        assert order.status != OrderStatus.REJECTED  # 宽限未到，先不误杀
        hub.advance(hub.PHANTOM_GRACE_S + 1)
        broker._sync_round()

        assert order.status == OrderStatus.REJECTED, "自盖 #DONE/SENT 被当成柜台收录 → 静默蒸发"

    def test_ack_without_matching_order_is_counted_not_swallowed(self, hub):
        """缺陷①（同族吞单）：缓存未命中的 ack 旧代码 continue 零痕迹，必须计数+error 留痕"""
        broker = hub.new_broker()
        hub.write_counter_order("other-remark")
        hub.append_ack("unknown-remark,FAIL,counter has no such order")

        broker._sync_round()

        counters = broker.bridge_diagnostics()["sync_counters"]
        assert counters.get("ack_unmatched", 0) == 1, f"未匹配 ack 被静默吞掉：{counters}"

    def test_counter_visible_remark_closes_the_claim(self, hub):
        """误杀防线①：柜台一旦出现该 remark 立即销案，宽限过后也不得转 REJECTED"""
        broker = hub.new_broker()
        hub.write_counter_order("idem-a4")
        order = hub.submit(broker, "oid-a4", "idem-a4")

        broker._sync_round()
        assert broker.bridge_diagnostics()["unconfirmed_claims"] == []
        hub.advance(hub.PHANTOM_GRACE_S + 1)
        broker._sync_round()

        assert order.status == OrderStatus.SUBMITTED

    def test_stale_or_missing_counter_export_forbids_reject(self, hub):
        """误杀防线②：柜台导出缺失/超龄时禁判幽灵单（宁可不判，不可误杀活单）"""
        broker = hub.new_broker()
        hub.write_counter_order("other-remark", stale_seconds=3600)
        order = hub.submit(broker, "oid-a5", "idem-a5")

        hub.clock.advance(hub.PHANTOM_GRACE_S + 1)  # 故意不刷新导出 mtime
        broker._sync_round()

        assert order.status == OrderStatus.SUBMITTED

    def test_rejected_drop_reaches_execution_report_ledger(self, hub):
        """缺陷①（台账面）：被丢弃的单必须在 execution_report 可见（既有 _observe_terminal_orders 通道）"""
        broker = hub.new_broker()
        hub.write_counter_order("other-remark")
        producer = MagicMock()
        observed: list[list] = []
        producer.observe.side_effect = lambda orders: observed.append(list(orders))
        broker.attach_execution_report_producer(producer)
        hub.submit(broker, "oid-a6", "idem-a6")
        hub.advance(hub.PHANTOM_GRACE_S + 1)
        broker._sync_round()

        assert any(o.order_id == "oid-a6" and o.status == OrderStatus.REJECTED for o in observed[-1]), (
            "拒单化未落台账观察面"
        )

    def test_health_exposes_unconfirmed_claims(self, hub):
        """缺陷①（可观测面）：既有 check_broker_health 必须吐出没被销案的声称数（前端可读）"""
        broker = hub.new_broker(connect=True)
        hub.write_counter_order("other-remark")
        hub.submit(broker, "oid-a7", "idem-a7")

        health = check_broker_health(broker)

        assert health["counter"]["unconfirmed_claims"] >= 1
        assert "silently_dropped_total" in health["counter"]

    def test_concurrent_duplicate_submit_writes_exactly_one_instruction_line(self, hub):
        """缺陷②：幂等检查在锁外、登记在锁内 → 同 idempotency_key 并发必写两行=两张柜台合同

        交叠点刻意放在"幂等检查之后、认领之前"（=缺陷②的 check-then-act 窗口本身，
        旧代码 :515 检查 → :556 落盘 → :561 才登记）：拦在 _append_instruction 里
        只能证明旧代码红，证明不了"复用 self._lock 做 check-then-claim"是承重的。
        """
        broker = hub.new_broker()
        n_threads = 16  # 放大并发扇出：两线程版打不出"每次新建锁"这种退化实现的窗口（16 线程可）
        barrier = threading.Barrier(n_threads)
        original_cage = bridge_mod.check_price_cage

        def racing_cage(*args, **kwargs):
            try:
                barrier.wait(timeout=3)
            except threading.BrokenBarrierError:
                pass
            return original_cage(*args, **kwargs)

        order = Order(
            order_id="oid-r1",
            idempotency_key="idem-r1",
            symbol="510300.SH",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("4.50"),
            strategy_id="trd-a10",
        )
        with patch.object(bridge_mod, "check_price_cage", racing_cage):
            returned = []
            threads = [threading.Thread(target=lambda: returned.append(broker.submit_order(order))) for _ in range(n_threads)]
            for t in threads:
                t.start()
            for t in threads:
                t.join(timeout=10)

        lines = hub.instruction_lines("order")
        assert len(lines) == 1, f"同 idempotency_key 写出 {len(lines)} 条指令行（重复合同）"
        assert set(returned) == {"oid-r1"}, f"幂等契约=16 次调用返回同一个 order_id，实得 {set(returned)}"

    def test_concurrent_cancel_writes_exactly_one_cancel_line(self, hub):
        """缺陷②：cancel_order 无锁读缓存 + 无撤单在途幂等 → 并发撤单写重复撤单行"""
        broker = hub.new_broker()
        hub.write_counter_order("idem-c1")
        hub.submit(broker, "oid-c1", "idem-c1")
        # 柜台凭证回填走修复前就存在的 API —— 本例测"同目标不重复写行"，不是测暂缓窗
        broker._mirror.sync_all(broker._pairing_cache, broker._dispatch_fill)
        barrier = threading.Barrier(2)
        original = broker._append_instruction

        def racing(inst):
            try:
                barrier.wait(timeout=2)
            except threading.BrokenBarrierError:
                pass
            original(inst)

        broker._append_instruction = racing
        threads = [threading.Thread(target=broker.cancel_order, args=("oid-c1",)) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        lines = hub.instruction_lines("cancel")
        assert len(lines) == 1, f"同一目标写出 {len(lines)} 条撤单指令行"

    def test_cancel_without_counter_credential_is_held_within_window(self, hub):
        """缺陷②：撤一张柜台从未收录的单，旧代码无条件 True=撤单假成功（调用方以为已撤）"""
        broker = hub.new_broker()
        hub.write_counter_order("other-remark")  # 柜台视图新鲜，但没有我们这张单
        hub.submit(broker, "oid-c2", "idem-c2")

        assert broker.cancel_order("oid-c2") is False, "未获柜台凭证却报撤单成功"
        assert hub.instruction_lines("cancel") == []

    def test_held_cancel_is_deferred_not_dropped(self, hub):
        """护栏必须把"挡下"实现为**延后**：风控直通面（risk_layer_orchestrator:390-392）
        拿到 False 不重试，若 broker 不补发就会制造一个新的静默洞。"""
        broker = hub.new_broker()
        hub.write_counter_order("other-remark")
        hub.submit(broker, "oid-c5", "idem-c5")
        assert broker.cancel_order("oid-c5") is False
        assert broker.bridge_diagnostics()["cancel_pending"] == {"idem-c5": "oid-c5"}

        hub.advance(hub.CANCEL_HOLD_S + 1)  # 仍在幽灵单宽限内，只过撤单暂缓窗
        broker._sync_round()

        assert [ln[0] for ln in hub.instruction_lines("cancel")] == ["Coid-c5"], "暂缓撤单未补发=挡下即蒸发"
        assert broker.bridge_diagnostics()["cancel_pending"] == {}
        assert broker.bridge_diagnostics()["sync_counters"]["cancel_deferred_fired"] == 1

    def test_cancel_after_hold_window_always_fires(self, hub):
        """护栏不得挡住风控动作：超撤单暂缓窗必放行（撤单永远发得出去）"""
        broker = hub.new_broker()
        hub.write_counter_order("other-remark")
        hub.submit(broker, "oid-c3", "idem-c3")
        hub.advance(hub.CANCEL_HOLD_S + 1)

        assert broker.cancel_order("oid-c3") is True
        assert [ln[0] for ln in hub.instruction_lines("cancel")] == ["Coid-c3"]

    def test_cancel_with_counter_credential_fires_immediately(self, hub):
        """柜台已收录（有 sysid 凭证）→ 撤单立即下发，不必等窗"""
        broker = hub.new_broker()
        hub.write_counter_order("idem-c4")
        hub.submit(broker, "oid-c4", "idem-c4")
        # 回填 broker_order_id=柜台凭证（走修复前就存在的 API，使本例在修复前即行为红）
        broker._mirror.sync_all(broker._pairing_cache, broker._dispatch_fill)

        assert broker.cancel_order("oid-c4") is True
        assert len(hub.instruction_lines("cancel")) == 1

    def test_submit_cancel_race_100_rounds_no_leak(self, hub):
        """判据"撤单竞态压测 100 次 0 漏单"的仓内等价尺：100 轮 下单→立刻撤单→柜台零收录"""
        broker = hub.new_broker()
        hub.write_counter_order("other-remark")
        orders = []
        for i in range(100):
            orders.append(hub.submit(broker, f"oid-s{i}", f"idem-s{i}"))
            broker.cancel_order(f"oid-s{i}")

        hub.advance(hub.PHANTOM_GRACE_S + 1)
        broker._sync_round()

        order_lines = hub.instruction_lines("order")
        cancel_lines = hub.instruction_lines("cancel")
        assert len(order_lines) == 100
        assert len({cells[0] for cells in order_lines}) == 100, "指令行出现重复 remark（重复合同）"
        assert len({cells[0] for cells in cancel_lines}) == len(cancel_lines), "撤单行重复"
        stuck = [o.order_id for o in orders if o.status is not OrderStatus.REJECTED]
        assert stuck == [], f"{len(stuck)} 张单停在非终态（漏单）"
        assert broker.bridge_diagnostics()["sync_counters"]["phantom_rejected"] == 100


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
