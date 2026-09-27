# [BLUEPRINT] MOD-CMP-009 | docs/03_modules/_domain_compliance/compliance_report_registry/blueprint.md | §test
# [MODULE] tests.compliance.test_f62_compliance_gate_wiring
# [DOMAIN] D_COMPLIANCE
# [INVARIANTS] 生产装配点三门齐注(非 None); CancelRateGuard 在 OrderManager 与 TradingSession 必须同实例(is); ManipulationRealtimeMonitor 必 attach_order_manager(否则永不冻结=接了等于没接); broker_ack 缺项 fail-closed 拒发且 broker.submit_order 零调用; 登记表/合规日志全注入 tmp_path(禁写生产证据链, 宪法 §9.6)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ComplianceGateBlockError(ZA-EX-0011)
# [TESTS] self
# [TTL] permanent
"""F62 C-002 订单级合规闸装配点接线测试（43 号 §7.4/§8/§7.3）。

实证目标（案卷病灶：三门代码与测试全绿，生产装配点零注入=闸装了没通水）：
    1. 正门 ``scripts/start_paper_session.assemble_session`` 与 ``QmtTradingSession``
       构造后 OrderManager 确实持有三门（report_gate / declaration_guard /
       manipulation_monitor 均非 None）；
    2. CancelRateGuard 同实例约束（``is``）——分裂双实例=日申报 1 万笔阻断线
       "只查不计数"的假激活（trading_session.py 同实例防护直接 raise）；
    3. ``ManipulationRealtimeMonitor.attach_order_manager`` 在装配期被真实调用
       （spy 断调用，不只看对象存在），且 attach 的真后果=报单事件确实流入监测器；
    4. fail-closed 双侧：六项 broker_ack 全真 → ReportGate 放行且订单达 broker；
       任一项改 false → ComplianceGateBlockError 且 broker.submit_order 零调用。

登记表与合规日志一律写 tmp_path（同 tests/compliance/test_runtime_wiring.py 范式），
不连 ClickHouse、不污染 MAIN_REPO_ROOT 证据链。
"""

from __future__ import annotations

import importlib.util
import json
import sys
from decimal import Decimal
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
import yaml

from zephyr.compliance.compliance_log import ComplianceLogger
from zephyr.compliance.compliance_report_registry import (
    ComplianceReportRegistry,
    ReportGate,
)
from zephyr.compliance.manipulation_realtime_monitor import ManipulationRealtimeMonitor
from zephyr.ex_core.adapters.qmt_file_bridge_broker import QmtFileBridgeBroker
from zephyr.ex_core.cancel_rate_guard import CancelRateGuard
from zephyr.ex_core.order_manager import ComplianceGateBlockError, OrderManager
from zephyr.ex_core.qmt_trading_session import QmtTradingSession
from zephyr.ex_core.trading_session import TradingSession
from zephyr.governance.strategies.strategy_base import StrategyBase
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderType

_ROOT = Path(__file__).resolve().parents[2]


def _load_paper_session_module() -> ModuleType:
    """按脚本真身加载 start_paper_session（与 tests/scripts/test_start_paper_session.py 同口径）。"""
    name = "start_paper_session_f62"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, _ROOT / "scripts" / "start_paper_session.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------
# tmp 侧合规件（禁触生产登记表与证据链）
# ---------------------------------------------------------------------

_REQUIRED_ITEMS = (
    ("RPT-ACCOUNT-INFO", "账户基本信息"),
    ("RPT-SOFTWARE-INFO", "交易软件信息"),
    ("RPT-STRATEGY-TYPES", "策略类型（6 大类）"),
    ("RPT-MAX-ORDER-RATE", "最高申报速率"),
    ("RPT-MAX-DAILY-ORDERS", "单日最高申报笔数"),
    ("RPT-MAJOR-CHANGE", "重大变更"),
)


def _registry(tmp_path: Path, *, unacked: str | None = None) -> ComplianceReportRegistry:
    """六项必报登记表写 tmp；unacked 指定单项 broker_ack=false。"""
    items = [
        {
            "item_id": item_id,
            "name": name,
            "content_source": "tmp",
            "timing": "首次交易前",
            "required": True,
            "reported_at": None if item_id == unacked else "2026-09-27",
            "broker_ack": item_id != unacked,
        }
        for item_id, name in _REQUIRED_ITEMS
    ]
    path = tmp_path / "compliance_report_registry.yaml"
    path.write_text(yaml.safe_dump({"report_items": items}, allow_unicode=True), encoding="utf-8")
    return ComplianceReportRegistry(registry_path=path)


def _logger(tmp_path: Path) -> ComplianceLogger:
    return ComplianceLogger(path=tmp_path / "compliance_log.jsonl")


def _gate(tmp_path: Path, *, unacked: str | None = None) -> ReportGate:
    return ReportGate(registry=_registry(tmp_path, unacked=unacked), logger=_logger(tmp_path))


def _submit_one(om: OrderManager, broker_id: str = "f62_broker") -> str:
    order = om.create_order(
        symbol="600519.SH",
        strategy_id="f62-wiring",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("100"),
        limit_price=Decimal("10"),
        broker_id=broker_id,
    )
    return om.submit_order(order.order_id, broker_id)


def _gate_log_records(tmp_path: Path) -> list[dict]:
    lines = (tmp_path / "compliance_log.jsonl").read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines]


class _KeepAliveStrategy(StrategyBase):
    """最小策略替身（装配期不产生权重）。"""

    def generate_target_weights(self, universe, signals, constraints):
        return {}


class _NavBroker:
    """assemble_session 最小券商替身：只给净值，绝不连真 QMT。"""

    def __init__(self, cash: str = "10000000") -> None:
        self._cash = Decimal(cash)
        self.submitted: list = []
        self.disconnected = False
        self.fill_callbacks: list = []

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        self.disconnected = True

    def register_fill_callback(self, callback) -> None:
        self.fill_callbacks.append(callback)

    def submit_order(self, order) -> str:
        self.submitted.append(order)
        return f"brk-{len(self.submitted)}"

    def cancel_order(self, broker_order_id: str) -> bool:
        return True

    def get_positions(self) -> SimpleNamespace:
        return SimpleNamespace(
            cash=self._cash,
            total_market_value=Decimal("0"),
            market_values={},
            holdings={},
        )

    def query_trades_today(self, trade_date: str | None = None) -> list:
        return []


def _assemble(tmp_path: Path, *, isolate_report_gate: bool = False):
    """装配正门（返回 sps/session/order_manager/broker）。

    isolate_report_gate=True 时把装配出的 ReportGate 换成 tmp 登记表+tmp 证据链
    同款——否则 PASS 结论会追写 MAIN_REPO_ROOT/data/compliance_log 生产证据链
    （宪法 §9.6 测试隔离）。三门注入事实本身由不隔离的那两个测负责。
    """
    sps = _load_paper_session_module()
    broker = _NavBroker()
    session = sps.assemble_session(sps.parse_args([]), broker, state_dir=tmp_path)
    om = session._order_manager
    if isolate_report_gate:
        om._report_gate = _gate(tmp_path)
    return sps, session, om, broker


# ---------------------------------------------------------------------
# ① + ② + ③：正门装配（scripts/start_paper_session.assemble_session）
# ---------------------------------------------------------------------


class TestPaperSessionFrontDoor:
    def test_three_gates_injected(self, tmp_path):
        """正门装配后 OrderManager 三门齐注（案卷病灶=全生产构造点默认 None）。"""
        _, session, om, _ = _assemble(tmp_path)
        assert isinstance(session, TradingSession)
        # 三门中仅 declaration_guard / manipulation_monitor 有只读 property，
        # report_gate 无公共出口（差异已列证据清单待总筹裁定）
        assert getattr(om, "_report_gate", None) is not None
        assert isinstance(om.declaration_guard, CancelRateGuard)
        assert isinstance(om.manipulation_monitor, ManipulationRealtimeMonitor)

    def test_production_registry_pins_no_false_block(self, tmp_path):
        """装配出的门走生产登记表默认路径——六项 broker_ack 全真故不会误拦（只读，不写证据链）。"""
        _, _, om, _ = _assemble(tmp_path)
        assert isinstance(om._report_gate, ReportGate)
        items = ComplianceReportRegistry().load_items()
        assert items and all(i.broker_ack for i in items if i.required)

    def test_cancel_rate_guard_same_instance_in_session_and_order_manager(self, tmp_path):
        """同实例约束：分裂双实例=日申报阻断线只查不计数（假激活）。"""
        _, session, om, _ = _assemble(tmp_path)
        assert om.declaration_guard is not None
        assert session._cancel_rate_guard is om.declaration_guard

    def test_submit_counts_into_the_guard_the_session_reads(self, tmp_path, monkeypatch):
        """同实例的**后果**：放行一笔后 session 侧读数 +1（计数不分裂）。"""
        events: list = []
        monkeypatch.setattr(
            ManipulationRealtimeMonitor,
            "on_order_placed",
            lambda self, record: events.append(record) or [],
        )
        sps, session, om, broker = _assemble(tmp_path, isolate_report_gate=True)
        before = session._cancel_rate_guard.daily_declaration_count
        _submit_one(om, sps._BROKER_ID)
        assert session._cancel_rate_guard.daily_declaration_count == before + 1
        assert len(broker.submitted) == 1
        assert len(events) == 1  # 事件确实到达监测器（attach 生效）

    def test_attach_order_manager_called_with_assembled_manager(self, tmp_path, monkeypatch):
        """attach 必须被真实调用——只断言对象存在测不出"接了等于没接"。"""
        sps = _load_paper_session_module()
        calls: list[OrderManager] = []
        real_attach = ManipulationRealtimeMonitor.attach_order_manager

        def spy(self: ManipulationRealtimeMonitor, order_manager: OrderManager) -> None:
            calls.append(order_manager)
            real_attach(self, order_manager)

        monkeypatch.setattr(ManipulationRealtimeMonitor, "attach_order_manager", spy)
        session = sps.assemble_session(sps.parse_args([]), _NavBroker(), state_dir=tmp_path)
        assert calls == [session._order_manager]

    def test_attached_monitor_receives_submit_event(self, tmp_path, monkeypatch):
        """attach 的真后果：OrderManager 事件总线里挂着监测器的订单回调。"""
        seen: list[str] = []
        monkeypatch.setattr(
            ManipulationRealtimeMonitor,
            "_on_order_event",
            lambda self, order: seen.append(order.symbol),
        )
        sps, _, om, _ = _assemble(tmp_path, isolate_report_gate=True)
        _submit_one(om, sps._BROKER_ID)
        assert seen == ["600519.SH"]

    def test_assembled_door_blocks_when_registry_item_unacked(self, tmp_path):
        """fail-closed 侧在**装配点**成立：单项 broker_ack 改 false → 拒发且 broker 零调用。"""
        sps, _, om, broker = _assemble(tmp_path)
        om._report_gate = _gate(tmp_path, unacked="RPT-MAJOR-CHANGE")
        with pytest.raises(ComplianceGateBlockError, match="先报告后交易"):
            _submit_one(om, sps._BROKER_ID)
        assert broker.submitted == []


# ---------------------------------------------------------------------
# ① + ③：QMT 文件桥会话装配点（env∈{real,sim} 双通道）
# ---------------------------------------------------------------------


class TestQmtTradingSessionAssembly:
    @staticmethod
    def _build(env: str, tmp_path: Path) -> QmtTradingSession:
        config = QmtFileBridgeBroker.ENV_CONFIG["sim"].copy()
        config["bridge_dir"] = str(tmp_path)
        config["orders_file"] = str(tmp_path / "orders.csv")
        config["ack_file"] = str(tmp_path / "ack.csv")
        config["stock_dir"] = str(tmp_path / "Stock")
        with patch.dict(QmtFileBridgeBroker.ENV_CONFIG, {"sim": config, "real": config}):
            return QmtTradingSession(
                env=env,
                universe=["510300.SH"],
                strategy=_KeepAliveStrategy(),
                signal_provider=lambda symbols: {},
                price_provider=lambda symbols: {},
            )

    @pytest.mark.parametrize("env", ["sim", "real"])
    def test_three_gates_injected_both_channels(self, tmp_path, env):
        om = self._build(env, tmp_path).order_manager
        assert getattr(om, "_report_gate", None) is not None
        assert isinstance(om.declaration_guard, CancelRateGuard)
        assert isinstance(om.manipulation_monitor, ManipulationRealtimeMonitor)

    def test_attach_order_manager_called(self, tmp_path, monkeypatch):
        calls: list[OrderManager] = []
        real_attach = ManipulationRealtimeMonitor.attach_order_manager

        def spy(self: ManipulationRealtimeMonitor, order_manager: OrderManager) -> None:
            calls.append(order_manager)
            real_attach(self, order_manager)

        monkeypatch.setattr(ManipulationRealtimeMonitor, "attach_order_manager", spy)
        session = self._build("sim", tmp_path)
        assert calls == [session.order_manager]

    def test_attached_monitor_receives_submit_event(self, tmp_path, monkeypatch):
        seen: list[str] = []
        monkeypatch.setattr(
            ManipulationRealtimeMonitor,
            "_on_order_event",
            lambda self, order: seen.append(order.symbol),
        )
        session = self._build("sim", tmp_path)
        om = session.order_manager
        om._report_gate = _gate(tmp_path)
        broker = MagicMock()
        broker.submit_order.side_effect = lambda order: "brk-qmt"
        om.register_broker("qmt_sim", broker)
        order = om.create_order(
            symbol="510300.SH",
            strategy_id="f62-qmt",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("4.5"),
            broker_id="qmt_sim",
        )
        om.submit_order(order.order_id, "qmt_sim")
        assert seen == ["510300.SH"]


# ---------------------------------------------------------------------
# ④：ReportGate 通过面/阻断面（OrderManager 直注，tmp 登记表 + tmp 证据链）
# ---------------------------------------------------------------------


class TestReportGateFailClosed:
    def _om(self, tmp_path: Path, *, unacked: str | None) -> tuple[OrderManager, MagicMock]:
        broker = MagicMock()
        broker.submit_order.side_effect = lambda order: f"brk-{order.order_id[:8]}"
        om = OrderManager(report_gate=_gate(tmp_path, unacked=unacked), declaration_guard=CancelRateGuard())
        om.register_broker("f62_broker", broker)
        return om, broker

    def test_all_broker_ack_true_passes_and_reaches_broker(self, tmp_path):
        om, broker = self._om(tmp_path, unacked=None)
        assert _submit_one(om).startswith("brk-")
        assert broker.submit_order.call_count == 1
        assert _gate_log_records(tmp_path)[-1]["payload"]["decision"] == "PASS"

    @pytest.mark.parametrize("item_id", [item_id for item_id, _ in _REQUIRED_ITEMS])
    def test_any_single_unacked_blocks_without_touching_broker(self, tmp_path, item_id):
        """任一项 broker_ack=false → BLOCK 拒发，broker.submit_order MUST 未被调用。"""
        om, broker = self._om(tmp_path, unacked=item_id)
        with pytest.raises(ComplianceGateBlockError, match="先报告后交易"):
            _submit_one(om)
        broker.submit_order.assert_not_called()
        last = _gate_log_records(tmp_path)[-1]
        assert last["payload"]["decision"] == "BLOCK"
        assert last["payload"]["missing"] == [item_id]

    def test_unreadable_registry_fail_closed(self, tmp_path):
        """登记表不可读=Fail-Closed 拒发（43 号 §7.6），不得静默放行。"""
        broker = MagicMock()
        gate = ReportGate(
            registry=ComplianceReportRegistry(registry_path=tmp_path / "never_written.yaml"),
            logger=_logger(tmp_path),
        )
        om = OrderManager(report_gate=gate)
        om.register_broker("f62_broker", broker)
        with pytest.raises(ComplianceGateBlockError, match="Fail-Closed"):
            _submit_one(om)
        broker.submit_order.assert_not_called()
        assert _gate_log_records(tmp_path)[-1]["payload"]["decision"] == "BLOCK"


def test_bare_order_manager_still_skips_gates() -> None:
    """未注入=跳过（既有语义，本批不擅自把三道闸改成硬必填）。"""
    om = OrderManager()
    broker = MagicMock()
    broker.submit_order.side_effect = lambda order: "brk-bare"
    om.register_broker("f62_broker", broker)
    assert om.declaration_guard is None
    assert om.manipulation_monitor is None
    assert getattr(om, "_report_gate", None) is None
    assert _submit_one(om) == "brk-bare"
    assert broker.submit_order.call_count == 1
