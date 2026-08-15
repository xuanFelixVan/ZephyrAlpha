# [A_test] module_id: MOD-EXE-order_manager_compliance_gate_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md | §
# [MODULE] tests.ex_core.test_order_manager_compliance_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""C-002 执行域合规门禁单元测试（43 号 §7.4/§8，AI-ASM-001 装配批接线）。

覆盖：
  - ReportGate BLOCK → ComplianceGateBlockError 拒发（先报告后交易铁律）
  - ReportGate 登记表不可读 → Fail-Closed BLOCK
  - 日申报笔数 >=1 万 → 拒发；>=5000 → WARNING 不阻断
  - 门禁在状态机转换+broker 发送前触发（阻断后订单保持 PENDING，broker 零调用）
  - 未注入门禁 → 既有行为不变（向后兼容）
"""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock

import pytest
import yaml

from zephyr.compliance.compliance_log import ComplianceLogger
from zephyr.compliance.compliance_report_registry import (
    ComplianceReportRegistry,
    ReportGate,
)
from zephyr.ex_core.cancel_rate_guard import CancelRateGuard
from zephyr.ex_core.order_manager import ComplianceGateBlockError, OrderManager
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderStatus, OrderType

# ---------------------------------------------------------------------
# 测试辅助
# ---------------------------------------------------------------------


def _make_broker() -> MagicMock:
    broker = MagicMock()
    broker.submit_order.return_value = "broker-oid-1"
    return broker


def _make_om(
    broker: MagicMock,
    report_gate: ReportGate | None = None,
    declaration_guard: CancelRateGuard | None = None,
) -> OrderManager:
    om = OrderManager(report_gate=report_gate, declaration_guard=declaration_guard)
    om.register_broker("test_broker", broker)
    return om


def _create_and_submit(om: OrderManager) -> str:
    order = om.create_order(
        symbol="600519.SH",
        strategy_id="test",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("100"),
        limit_price=Decimal("10"),
        broker_id="test_broker",
    )
    return om.submit_order(order.order_id, "test_broker")


def _write_registry(tmp_path, items: list[dict]) -> ComplianceReportRegistry:
    path = tmp_path / "compliance_report_registry.yaml"
    path.write_text(
        yaml.safe_dump({"report_items": items}, allow_unicode=True),
        encoding="utf-8",
    )
    return ComplianceReportRegistry(registry_path=path)


def _make_gate(tmp_path, items: list[dict]) -> ReportGate:
    registry = _write_registry(tmp_path, items)
    return ReportGate(
        registry=registry,
        logger=ComplianceLogger(path=tmp_path / "compliance_log.jsonl"),
    )


_ACKED_ITEM = {
    "item_id": "RPT-1",
    "name": "账户基本信息",
    "required": True,
    "reported_at": "2026-08-15",
    "broker_ack": True,
}

_UNACKED_ITEM = {
    "item_id": "RPT-1",
    "name": "账户基本信息",
    "required": True,
    "reported_at": None,
    "broker_ack": False,
}


# ---------------------------------------------------------------------
# ReportGate（先报告后交易）
# ---------------------------------------------------------------------


class TestReportGateWiring:
    def test_gate_pass_submits(self, tmp_path):
        broker = _make_broker()
        gate = _make_gate(tmp_path, [_ACKED_ITEM])
        om = _make_om(broker, report_gate=gate)
        assert _create_and_submit(om) == "broker-oid-1"
        broker.submit_order.assert_called_once()

    def test_gate_block_rejects_before_broker(self, tmp_path):
        """任一必报项 broker_ack 缺失 → 拒发，broker 零调用。"""
        broker = _make_broker()
        gate = _make_gate(tmp_path, [_UNACKED_ITEM])
        om = _make_om(broker, report_gate=gate)
        with pytest.raises(ComplianceGateBlockError, match="先报告后交易"):
            _create_and_submit(om)
        broker.submit_order.assert_not_called()

    def test_gate_block_keeps_order_pending(self, tmp_path):
        """阻断发生在状态机转换前——订单保持 PENDING（未误转 SUBMITTED）。"""
        broker = _make_broker()
        gate = _make_gate(tmp_path, [_UNACKED_ITEM])
        om = _make_om(broker, report_gate=gate)
        order = om.create_order(
            symbol="600519.SH",
            strategy_id="test",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("10"),
            broker_id="test_broker",
        )
        with pytest.raises(ComplianceGateBlockError):
            om.submit_order(order.order_id, "test_broker")
        assert om.get_order(order.order_id).status is OrderStatus.PENDING

    def test_gate_unreadable_registry_fail_closed(self, tmp_path):
        """登记表不可读 → Fail-Closed BLOCK（43 号 §7.4 降级）。"""
        broker = _make_broker()
        registry = ComplianceReportRegistry(registry_path=tmp_path / "missing.yaml")
        gate = ReportGate(
            registry=registry,
            logger=ComplianceLogger(path=tmp_path / "compliance_log.jsonl"),
        )
        om = _make_om(broker, report_gate=gate)
        with pytest.raises(ComplianceGateBlockError, match="先报告后交易"):
            _create_and_submit(om)
        broker.submit_order.assert_not_called()

    def test_error_code(self):
        assert ComplianceGateBlockError.error_code == "ZA-EX-0011"


# ---------------------------------------------------------------------
# 日申报笔数读数检查（5000 预警 / 1 万阻断）
# ---------------------------------------------------------------------


class TestDailyDeclarationWiring:
    def test_blocked_at_10000_rejects(self):
        """日申报 >=1 万笔 → 拒发（2026-06-08 新规限交易线）。"""
        broker = _make_broker()
        guard = CancelRateGuard(daily_warn_threshold=3, daily_block_threshold=5)
        for _ in range(5):
            guard.record_submit()
        om = _make_om(broker, declaration_guard=guard)
        with pytest.raises(ComplianceGateBlockError, match="日申报笔数"):
            _create_and_submit(om)
        broker.submit_order.assert_not_called()

    def test_warning_at_5000_still_submits(self, caplog):
        """5000 预警线只告警不阻断。"""
        broker = _make_broker()
        guard = CancelRateGuard(daily_warn_threshold=3, daily_block_threshold=100)
        for _ in range(3):
            guard.record_submit()
        om = _make_om(broker, declaration_guard=guard)
        with caplog.at_level("WARNING"):
            assert _create_and_submit(om) == "broker-oid-1"
        broker.submit_order.assert_called_once()
        assert any("日申报笔数预警" in r.message for r in caplog.records)

    def test_normal_submits(self):
        broker = _make_broker()
        guard = CancelRateGuard()
        om = _make_om(broker, declaration_guard=guard)
        assert _create_and_submit(om) == "broker-oid-1"

    def test_default_threshold_block_boundary(self):
        """默认阈值实证：1 万笔整即阻断（>= 口径）。"""
        broker = _make_broker()
        guard = CancelRateGuard()
        for _ in range(10000):
            guard.record_submit()
        om = _make_om(broker, declaration_guard=guard)
        with pytest.raises(ComplianceGateBlockError):
            _create_and_submit(om)
        broker.submit_order.assert_not_called()


# ---------------------------------------------------------------------
# 向后兼容与门禁顺序
# ---------------------------------------------------------------------


class TestBackwardCompatAndOrder:
    def test_no_gates_injected_unchanged(self):
        """未注入门禁 → 既有行为不变（向后兼容）。"""
        broker = _make_broker()
        om = _make_om(broker)
        assert _create_and_submit(om) == "broker-oid-1"
        broker.submit_order.assert_called_once()

    def test_report_gate_checked_before_declaration(self, tmp_path):
        """ReportGate 先于申报笔数检查（先报告后交易是第一硬闸）。"""
        broker = _make_broker()
        gate = _make_gate(tmp_path, [_UNACKED_ITEM])
        guard = CancelRateGuard(daily_warn_threshold=1, daily_block_threshold=2)
        for _ in range(2):
            guard.record_submit()  # 已超阻断线
        om = _make_om(broker, report_gate=gate, declaration_guard=guard)
        with pytest.raises(ComplianceGateBlockError, match="先报告后交易"):
            _create_and_submit(om)
        broker.submit_order.assert_not_called()
