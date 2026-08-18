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


# ---------------------------------------------------------------------
# 撤单计数接线（2026-08-16 双轮审查 P1-5 裁定，AI-RFIX-001）：
# 撤单指令发往券商即 record_cancel() 计入日申报硬计数器（成功/失败均计）
# ---------------------------------------------------------------------


class TestCancelDeclarationWiring:
    def _submit_and_get_id(self, om: OrderManager) -> str:
        order = om.create_order(
            symbol="600519.SH",
            strategy_id="test",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("10"),
            broker_id="test_broker",
        )
        om.submit_order(order.order_id, "test_broker")
        return order.order_id

    def test_cancel_success_counts_declaration(self):
        """撤单成功 → 计入日申报硬计数器 + 撤单率窗口（"申报、撤单笔数"同口径）。"""
        broker = _make_broker()
        guard = CancelRateGuard()
        om = _make_om(broker, declaration_guard=guard)
        order_id = self._submit_and_get_id(om)
        assert guard.daily_declaration_count == 1  # submit 侧对称计数（AI-R2 ATK-5）
        assert om.cancel_order(order_id) is True
        assert guard.daily_declaration_count == 2
        assert guard.total_cancels == 1

    def test_cancel_broker_failure_still_counts(self):
        """券商端撤单失败（如已成交拒撤）仍计入——指令已发出即消耗申报口径。"""
        broker = _make_broker()
        broker.cancel_order.return_value = False  # 券商拒撤
        guard = CancelRateGuard()
        om = _make_om(broker, declaration_guard=guard)
        order_id = self._submit_and_get_id(om)
        assert guard.daily_declaration_count == 1  # submit 侧对称计数（AI-R2 ATK-5）
        assert om.cancel_order(order_id) is False
        assert guard.daily_declaration_count == 2
        assert guard.total_cancels == 1

    def test_local_pending_cancel_not_counted(self):
        """无 broker_order_id 的纯本地撤单（未报交易所）→ 不计申报口径。"""
        broker = _make_broker()
        guard = CancelRateGuard()
        om = _make_om(broker, declaration_guard=guard)
        order = om.create_order(
            symbol="600519.SH",
            strategy_id="test",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("10"),
            broker_id="test_broker",
        )  # 仅创建未提交 → PENDING 无 broker_order_id
        assert om.cancel_order(order.order_id) is True
        assert guard.daily_declaration_count == 0
        assert guard.total_cancels == 0

    def test_cancel_without_guard_unchanged(self):
        """未注入 declaration_guard → 撤单行为不变（向后兼容，None 守卫跳过）。"""
        broker = _make_broker()
        om = _make_om(broker)
        order_id = self._submit_and_get_id(om)
        assert om.cancel_order(order_id) is True
        assert om.get_order(order_id).status is OrderStatus.CANCELLED


# ---------------------------------------------------------------------
# 报单侧申报计数对称化（AI-R2 红队 ATK-5）：
# 指令发往券商即 record_submit()（成功/失败均计，与撤单侧同口径宁多勿漏）；
# C-002 BLOCKED 订单未发出不计
# ---------------------------------------------------------------------


class TestSubmitDeclarationWiring:
    def test_submit_success_counts_once(self):
        """报单成功 → 计入日申报硬计数器恰好 1 次（无双计）。"""
        broker = _make_broker()
        guard = CancelRateGuard()
        om = _make_om(broker, declaration_guard=guard)
        assert _create_and_submit(om) == "broker-oid-1"
        assert guard.daily_declaration_count == 1

    def test_submit_broker_failure_still_counts(self):
        """broker 异常（指令或已达交易所）仍计入——漏计则 1 万笔防线可穿透。"""
        broker = _make_broker()
        broker.submit_order.side_effect = ConnectionError("miniQMT 连接中断")
        guard = CancelRateGuard()
        om = _make_om(broker, declaration_guard=guard)
        order = om.create_order(
            symbol="600519.SH",
            strategy_id="test",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("10"),
            broker_id="test_broker",
        )
        with pytest.raises(ConnectionError):
            om.submit_order(order.order_id, "test_broker")
        assert guard.daily_declaration_count == 1

    def test_c002_blocked_submit_not_counted(self):
        """C-002 拒发订单未发出 → 不计申报口径（不过度计数自锁）。"""
        broker = _make_broker()
        guard = CancelRateGuard(daily_warn_threshold=1, daily_block_threshold=2)
        for _ in range(2):
            guard.record_submit()  # 已超阻断线
        om = _make_om(broker, declaration_guard=guard)
        with pytest.raises(ComplianceGateBlockError):
            _create_and_submit(om)
        assert guard.daily_declaration_count == 2  # 未新增
        broker.submit_order.assert_not_called()

    def test_submit_without_guard_unchanged(self):
        """未注入 declaration_guard → 报单行为不变（向后兼容）。"""
        broker = _make_broker()
        om = _make_om(broker)
        assert _create_and_submit(om) == "broker-oid-1"


# ---------------------------------------------------------------------
# 非法 fill 拒收（AI-R2 红队 ATK-9）：None/NaN/非正价格契约违反不半更新
# ---------------------------------------------------------------------


class TestOnFillPriceGuard:
    def _filled_order(self, om: OrderManager) -> str:
        order = om.create_order(
            symbol="600519.SH",
            strategy_id="test",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("10"),
            broker_id="test_broker",
        )
        om.submit_order(order.order_id, "test_broker")
        return order.order_id

    def test_none_price_fill_rejected_without_half_update(self):
        """fill_price=None → 拒收不崩溃（修复前 TypeError 半更新：
        qty 已加、状态未转 FILLED 的不一致态）。"""
        from datetime import UTC, datetime

        from zephyr.shared.contracts.fill import Fill

        broker = _make_broker()
        om = _make_om(broker)
        order_id = self._filled_order(om)
        evil = Fill(
            fill_id="evil-none",
            fill_price=None,
            fill_timestamp=datetime.now(UTC),
            filled_quantity=Decimal("100"),
            idempotency_key="evil-none",
            order_id=order_id,
            strategy_id="test",
            symbol="600519.SH",
        )
        om._on_fill(evil)  # 修复前 TypeError
        order = om.get_order(order_id)
        assert order.filled_quantity == Decimal("0")  # 未半更新
        assert order.status is OrderStatus.SUBMITTED

    def test_zero_and_negative_price_fill_rejected(self):
        """fill_price<=0 → 拒收（与 Saga _FillCollector 防御口径一致）。"""
        from datetime import UTC, datetime

        from zephyr.shared.contracts.fill import Fill

        broker = _make_broker()
        om = _make_om(broker)
        order_id = self._filled_order(om)
        for bad in (Decimal("0"), Decimal("-1.5")):
            om._on_fill(Fill(
                fill_id=f"evil-{bad}",
                fill_price=bad,
                fill_timestamp=datetime.now(UTC),
                filled_quantity=Decimal("100"),
                idempotency_key=f"evil-{bad}",
                order_id=order_id,
                strategy_id="test",
                symbol="600519.SH",
            ))
        assert om.get_order(order_id).filled_quantity == Decimal("0")
