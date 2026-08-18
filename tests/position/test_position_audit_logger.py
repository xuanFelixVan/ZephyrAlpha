# [BLUEPRINT] MOD-POS-009 | docs/03_modules/_domain_position/position_audit_logger/blueprint.md
# [MODULE] tests.position.test_position_audit_logger
# [DOMAIN] D_POSITION
# [TESTS] tests/position/test_position_audit_logger.py
# [A_module] module_id=MOD-POS-009 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Position Audit Logger 测试 — MOD-POS-009

覆盖: 事件记录 + 哈希链 + 查询 + 报告 + 持久化 + 异常安全 + 不可变。
"""

from __future__ import annotations

import dataclasses
import json
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from zephyr.position.core.position_drift_monitor import (
    DriftAlert,
    DriftDetectedEvent,
    DriftResult,
    DriftScope,
    TriageLevel,
)
from zephyr.position.core.position_sizing_engine import (
    PositionSizingEngine,
    PositionSizingInput,
    PositionSizingPlan,
    PositionTarget,
    SymbolInput,
)
from zephyr.position.core.position_state_machine import (
    ObservingReason,
    PositionState,
    PositionStateMachine,
    StateChangedEvent,
)
from zephyr.position.core.rebalance_engine import (
    RebalanceAction,
    RebalanceDecision,
    RebalanceOrder,
    RebalanceTrigger,
    RebalanceTriggeredEvent,
)
from zephyr.position.services.position_audit_logger import (
    ZERO_HASH,
    AuditChainError,
    AuditSource,
    PositionAuditEventType,
    PositionAuditLogger,
    PositionAuditRecord,
    PositionAuditReport,
)

# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def audit() -> PositionAuditLogger:
    """干净的审计记录器 (仅内存)。"""
    return PositionAuditLogger()


@pytest.fixture
def t0() -> datetime:
    """固定时间基准。"""
    return datetime(2026, 8, 2, 10, 0, 0, tzinfo=UTC)


def make_state_changed_event(
    symbol: str = "000001.SZ",
    from_state: PositionState = PositionState.BUILDING,
    to_state: PositionState = PositionState.ACTIVE,
    timestamp: datetime | None = None,
    reason: str = "graduation_complete",
) -> StateChangedEvent:
    """构造 StateChangedEvent。"""
    return StateChangedEvent(
        symbol=symbol,
        from_state=from_state,
        to_state=to_state,
        timestamp=timestamp or datetime(2026, 8, 2, 10, 0, 0, tzinfo=UTC),
        reason=reason,
    )


def make_drift_event(
    timestamp: datetime | None = None,
) -> DriftDetectedEvent:
    """构造 DriftDetectedEvent。"""
    alert = DriftAlert(
        scope=DriftScope.SYMBOL,
        symbol="000001.SZ",
        actual_weight=0.08,
        target_weight=0.05,
        drift=0.03,
        threshold=0.03,
        triage=TriageLevel.MONITOR,
    )
    result = DriftResult(
        portfolio_alert=None,
        symbol_alerts=[alert],
        timestamp=timestamp or datetime(2026, 8, 2, 10, 0, 0, tzinfo=UTC),
    )
    return DriftDetectedEvent(
        result=result,
        timestamp=timestamp or datetime(2026, 8, 2, 10, 0, 0, tzinfo=UTC),
    )


def make_rebalance_event(
    timestamp: datetime | None = None,
) -> RebalanceTriggeredEvent:
    """构造 RebalanceTriggeredEvent。"""
    order = RebalanceOrder(
        symbol="000001.SZ",
        current_weight=0.08,
        target_weight=0.05,
        delta=-0.03,
        action=RebalanceAction.SELL,
    )
    decision = RebalanceDecision(
        should_rebalance=True,
        trigger=RebalanceTrigger.DEVIATION,
        orders=[order],
        expected_improvement=0.002,
        transaction_cost=0.001,
        improvement_ratio=2.0,
        reason="drift_exceeds_threshold",
    )
    return RebalanceTriggeredEvent(
        decision=decision,
        timestamp=timestamp or datetime(2026, 8, 2, 10, 0, 0, tzinfo=UTC),
    )


def make_sizing_plan(
    timestamp: datetime | None = None,
    degraded: bool = False,
) -> PositionSizingPlan:
    """构造 PositionSizingPlan。"""
    return PositionSizingPlan(
        plan_id="plan-001",
        strategy_id="strat-001",
        positions={
            "000001.SZ": PositionTarget(
                symbol="000001.SZ",
                target_qty=500,
                current_qty=300,
                delta=200,
                target_weight=0.05,
                reason="kelly_sized",
            ),
        },
        cash_reserve=50000.0,
        total_exposure=0.05,
        capital_curve_discount=1.0,
        calendar_constraint_active=False,
        volatility_adjustment=1.0,
        constraints_check={"kelly": {"passed": True}},
        created_at=timestamp or datetime(2026, 8, 2, 10, 0, 0, tzinfo=UTC),
        idempotency_key="test-key-001",
        degraded=degraded,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 1. 事件记录测试
# ──────────────────────────────────────────────────────────────────────────────


class TestLogPositionSized:
    """测试 log_position_sized (E-POS-01)。"""

    def test_basic_record(self, audit: PositionAuditLogger, t0: datetime) -> None:
        plan = make_sizing_plan(timestamp=t0)
        audit.log_position_sized(plan)

        assert audit.record_count == 1
        rec = audit.query()[0]
        assert rec.event_type == PositionAuditEventType.POSITION_SIZED
        assert rec.symbol == "000001.SZ"
        assert rec.source == AuditSource.AUTO
        assert rec.detail["plan_id"] == "plan-001"
        assert rec.detail["strategy_id"] == "strat-001"
        assert rec.detail["total_exposure"] == 0.05
        assert rec.detail["degraded"] is False
        assert rec.detail["symbols"] == ["000001.SZ"]
        assert rec.detail["idempotency_key"] == "test-key-001"

    def test_degraded_marks_emergency(self, audit: PositionAuditLogger) -> None:
        plan = make_sizing_plan(degraded=True)
        audit.log_position_sized(plan)

        rec = audit.query()[0]
        assert rec.source == AuditSource.EMERGENCY
        assert rec.detail["degraded"] is True

    def test_empty_positions_uses_star(self, audit: PositionAuditLogger, t0: datetime) -> None:
        plan = dataclasses.replace(make_sizing_plan(timestamp=t0), positions={})
        audit.log_position_sized(plan)

        rec = audit.query()[0]
        assert rec.symbol == "*"


class TestLogStateChanged:
    """测试 on_state_changed (E-POS-05)。"""

    def test_basic_record(self, audit: PositionAuditLogger, t0: datetime) -> None:
        event = make_state_changed_event(timestamp=t0)
        audit.on_state_changed(event)

        assert audit.record_count == 1
        rec = audit.query()[0]
        assert rec.event_type == PositionAuditEventType.STATE_CHANGED
        assert rec.symbol == "000001.SZ"
        assert rec.source == AuditSource.AUTO
        assert rec.detail["from_state"] == "BUILDING"
        assert rec.detail["to_state"] == "ACTIVE"
        assert rec.detail["reason"] == "graduation_complete"

    def test_via_state_machine_listener(self, audit: PositionAuditLogger) -> None:
        """通过实际 PositionStateMachine.on_state_changed 验证集成。"""
        fsm = PositionStateMachine("000001.SZ")
        fsm.on_state_changed(audit.on_state_changed)
        fsm.start_building(now=datetime(2026, 8, 1, tzinfo=UTC))

        assert audit.record_count == 1
        rec = audit.query()[0]
        assert rec.event_type == PositionAuditEventType.STATE_CHANGED


class TestLogDriftDetected:
    """测试 on_drift_detected (E-POS-02)。"""

    def test_basic_record(self, audit: PositionAuditLogger, t0: datetime) -> None:
        event = make_drift_event(timestamp=t0)
        audit.on_drift_detected(event)

        assert audit.record_count == 1
        rec = audit.query()[0]
        assert rec.event_type == PositionAuditEventType.DRIFT_DETECTED
        assert rec.symbol == "000001.SZ"
        assert rec.source == AuditSource.DRIFT
        assert rec.detail["alerts"][0]["symbol"] == "000001.SZ"
        assert rec.detail["alerts"][0]["drift"] == 0.03

    def test_portfolio_level_drift(self, audit: PositionAuditLogger, t0: datetime) -> None:
        """组合级漂移 (无 symbol_alerts) symbol="*"。"""
        pa = DriftAlert(
            scope=DriftScope.PORTFOLIO,
            symbol=None,
            actual_weight=0.85,
            target_weight=0.80,
            drift=0.05,
            threshold=0.02,
            triage=TriageLevel.WATCH,
        )
        result = DriftResult(
            portfolio_alert=pa,
            symbol_alerts=[],
            timestamp=t0,
        )
        event = DriftDetectedEvent(result=result, timestamp=t0)
        audit.on_drift_detected(event)

        rec = audit.query()[0]
        assert rec.symbol == "*"
        assert rec.detail["portfolio"]["drift"] == 0.05


class TestLogRebalanceTriggered:
    """测试 on_rebalance_triggered (E-POS-03)。"""

    def test_basic_record(self, audit: PositionAuditLogger, t0: datetime) -> None:
        event = make_rebalance_event(timestamp=t0)
        audit.on_rebalance_triggered(event)

        assert audit.record_count == 1
        rec = audit.query()[0]
        assert rec.event_type == PositionAuditEventType.REBALANCE_TRIGGERED
        assert rec.symbol == "000001.SZ"
        assert rec.source == AuditSource.REBALANCE
        assert rec.detail["should_rebalance"] is True
        assert rec.detail["trigger"] == "DEVIATION"
        assert rec.detail["order_count"] == 1
        assert rec.detail["symbols"] == ["000001.SZ"]
        assert rec.detail["improvement_ratio"] == 2.0

    def test_skip_rebalance(self, audit: PositionAuditLogger, t0: datetime) -> None:
        """should_rebalance=False 仍记录 (全记录 C1)。"""
        decision = RebalanceDecision(
            should_rebalance=False,
            trigger=RebalanceTrigger.CALENDAR,
            orders=[],
            reason="cost_exceeds_benefit",
        )
        event = RebalanceTriggeredEvent(decision=decision, timestamp=t0)
        audit.on_rebalance_triggered(event)

        rec = audit.query()[0]
        assert rec.detail["should_rebalance"] is False
        assert rec.detail["order_count"] == 0
        assert rec.symbol == "*"


# ──────────────────────────────────────────────────────────────────────────────
# 2. 哈希链测试
# ──────────────────────────────────────────────────────────────────────────────


class TestHashChain:
    """测试哈希链连续性 + 篡改检测。"""

    def test_first_record_prev_hash_is_zero(self, audit: PositionAuditLogger) -> None:
        audit.log_position_sized(make_sizing_plan())
        rec = audit.query()[0]
        assert rec.prev_hash == ZERO_HASH

    def test_chain_continuity(self, audit: PositionAuditLogger, t0: datetime) -> None:
        """多条记录 prev_hash 链接正确。"""
        audit.log_position_sized(make_sizing_plan(timestamp=t0))
        audit.on_state_changed(make_state_changed_event(timestamp=t0 + timedelta(minutes=1)))
        audit.on_drift_detected(make_drift_event(timestamp=t0 + timedelta(minutes=2)))
        audit.on_rebalance_triggered(make_rebalance_event(timestamp=t0 + timedelta(minutes=3)))

        records = audit.query()
        assert len(records) == 4
        for i in range(1, len(records)):
            assert records[i].prev_hash == records[i - 1].record_hash

    def test_verify_chain_valid(self, audit: PositionAuditLogger, t0: datetime) -> None:
        audit.log_position_sized(make_sizing_plan(timestamp=t0))
        audit.on_state_changed(make_state_changed_event(timestamp=t0 + timedelta(minutes=1)))

        valid, break_at = audit.verify_chain()
        assert valid is True
        assert break_at is None

    def test_verify_chain_detects_tamper(self, audit: PositionAuditLogger, t0: datetime) -> None:
        """篡改记录的 detail 后, 哈希链校验失败。"""
        audit.log_position_sized(make_sizing_plan(timestamp=t0))
        audit.on_state_changed(make_state_changed_event(timestamp=t0 + timedelta(minutes=1)))

        # 篡改: 替换中间记录 (frozen dataclass 不可直接改, 用替换整个 list 元素)
        records = audit._records
        tampered = dataclasses.replace(records[0], detail={"tampered": True})
        audit._records[0] = tampered

        valid, break_at = audit.verify_chain()
        assert valid is False
        assert break_at == tampered.record_id

    def test_verify_chain_detects_broken_link(self, audit: PositionAuditLogger, t0: datetime) -> None:
        """prev_hash 链接断裂检测。"""
        audit.log_position_sized(make_sizing_plan(timestamp=t0))
        audit.on_state_changed(make_state_changed_event(timestamp=t0 + timedelta(minutes=1)))

        # 篡改: 修改第二条记录的 prev_hash
        records = audit._records
        tampered = dataclasses.replace(records[1], prev_hash="deadbeef")
        audit._records[1] = tampered

        valid, break_at = audit.verify_chain()
        assert valid is False
        assert break_at == tampered.record_id

    def test_verify_empty_chain(self, audit: PositionAuditLogger) -> None:
        """空链视为有效。"""
        valid, break_at = audit.verify_chain()
        assert valid is True
        assert break_at is None


# ──────────────────────────────────────────────────────────────────────────────
# 3. 查询测试
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    """测试 query 过滤。"""

    @pytest.fixture
    def audit_with_data(self, audit: PositionAuditLogger, t0: datetime) -> PositionAuditLogger:
        audit.log_position_sized(make_sizing_plan(timestamp=t0))
        audit.on_state_changed(make_state_changed_event(symbol="600000.SH", timestamp=t0 + timedelta(minutes=10)))
        audit.on_drift_detected(make_drift_event(timestamp=t0 + timedelta(minutes=20)))
        audit.on_rebalance_triggered(make_rebalance_event(timestamp=t0 + timedelta(minutes=30)))
        return audit

    def test_query_all(self, audit_with_data: PositionAuditLogger) -> None:
        results = audit_with_data.query()
        assert len(results) == 4

    def test_query_by_symbol(self, audit_with_data: PositionAuditLogger) -> None:
        results = audit_with_data.query(symbol="000001.SZ")
        assert len(results) == 3  # sized, drift, rebalance
        assert all("000001.SZ" in r.symbol for r in results)

    def test_query_by_symbol_no_match(self, audit_with_data: PositionAuditLogger) -> None:
        results = audit_with_data.query(symbol="999999.SZ")
        assert len(results) == 0

    def test_query_by_event_type(self, audit_with_data: PositionAuditLogger) -> None:
        results = audit_with_data.query(event_type=PositionAuditEventType.STATE_CHANGED)
        assert len(results) == 1
        assert results[0].event_type == PositionAuditEventType.STATE_CHANGED

    def test_query_by_time_range(self, audit_with_data: PositionAuditLogger, t0: datetime) -> None:
        results = audit_with_data.query(
            start=t0 + timedelta(minutes=5),
            end=t0 + timedelta(minutes=25),
        )
        assert len(results) == 2  # state_changed + drift

    def test_query_combined(self, audit_with_data: PositionAuditLogger, t0: datetime) -> None:
        results = audit_with_data.query(
            symbol="000001.SZ",
            event_type=PositionAuditEventType.DRIFT_DETECTED,
        )
        assert len(results) == 1
        assert results[0].event_type == PositionAuditEventType.DRIFT_DETECTED


# ──────────────────────────────────────────────────────────────────────────────
# 4. 报告测试
# ──────────────────────────────────────────────────────────────────────────────


class TestGenerateReport:
    """测试 generate_report。"""

    def test_report_statistics(self, audit: PositionAuditLogger, t0: datetime) -> None:
        audit.log_position_sized(make_sizing_plan(timestamp=t0))
        audit.on_state_changed(make_state_changed_event(timestamp=t0 + timedelta(minutes=1)))
        audit.on_drift_detected(make_drift_event(timestamp=t0 + timedelta(minutes=2)))

        report = audit.generate_report(
            period_start=t0 - timedelta(hours=1),
            period_end=t0 + timedelta(hours=1),
        )

        assert report.total_records == 3
        assert report.by_event_type["POSITION_SIZED"] == 1
        assert report.by_event_type["STATE_CHANGED"] == 1
        assert report.by_event_type["DRIFT_DETECTED"] == 1
        assert report.by_symbol["000001.SZ"] == 3
        assert report.by_source["AUTO"] == 2
        assert report.by_source["DRIFT"] == 1
        assert report.chain_valid is True
        assert report.chain_break_at is None
        assert isinstance(report.report_id, str)

    def test_report_empty_period(self, audit: PositionAuditLogger, t0: datetime) -> None:
        report = audit.generate_report(
            period_start=t0,
            period_end=t0 + timedelta(hours=1),
        )
        assert report.total_records == 0
        assert report.by_event_type == {}
        assert report.chain_valid is True

    def test_report_chain_invalid(self, audit: PositionAuditLogger, t0: datetime) -> None:
        audit.log_position_sized(make_sizing_plan(timestamp=t0))
        # 篡改
        audit._records[0] = dataclasses.replace(audit._records[0], detail={"x": 1})

        report = audit.generate_report(
            period_start=t0 - timedelta(hours=1),
            period_end=t0 + timedelta(hours=1),
        )
        assert report.chain_valid is False
        assert report.chain_break_at is not None


# ──────────────────────────────────────────────────────────────────────────────
# 5. 异常安全测试 (C5)
# ──────────────────────────────────────────────────────────────────────────────


class TestListenerExceptionSafety:
    """测试 listener 异常不阻断主流程 (C5)。"""

    def test_state_changed_exception_swallowed(self, audit: PositionAuditLogger) -> None:
        """传入异常事件, on_state_changed 不抛出。"""
        bad_event = type(
            "BadEvent",
            (),
            {
                "symbol": "000001.SZ",
                "from_state": None,  # None 无 .value → AttributeError
                "to_state": None,
                "timestamp": datetime.now(UTC),
                "reason": None,
            },
        )()
        # 不抛异常
        audit.on_state_changed(bad_event)
        # 记录未被添加 (异常被吞)
        assert audit.record_count == 0

    def test_drift_exception_swallowed(self, audit: PositionAuditLogger) -> None:
        bad_event = type(
            "BadEvent",
            (),
            {
                "result": None,
                "timestamp": datetime.now(UTC),
            },
        )()
        audit.on_drift_detected(bad_event)
        assert audit.record_count == 0


# ──────────────────────────────────────────────────────────────────────────────
# 6. 持久化测试
# ──────────────────────────────────────────────────────────────────────────────


class TestPersistJsonl:
    """测试 JSONL 持久化 + 加载。"""

    def test_flush_and_load(self, t0: datetime, tmp_path: Path) -> None:
        persist_path = tmp_path / "audit"
        audit1 = PositionAuditLogger(persist_path=persist_path)
        audit1.log_position_sized(make_sizing_plan(timestamp=t0))
        audit1.on_state_changed(make_state_changed_event(timestamp=t0 + timedelta(minutes=1)))
        audit1.flush()

        jsonl_path = persist_path.with_suffix(".jsonl")
        assert jsonl_path.exists()

        audit2 = PositionAuditLogger(persist_path=persist_path)
        audit2.load()

        assert audit2.record_count == 2
        records = audit2.query()
        assert records[0].event_type == PositionAuditEventType.POSITION_SIZED
        assert records[1].event_type == PositionAuditEventType.STATE_CHANGED

        # 链完整性保持
        valid, _ = audit2.verify_chain()
        assert valid is True

    def test_load_nonexistent_file(self, tmp_path: Path) -> None:
        audit = PositionAuditLogger(persist_path=tmp_path / "nonexistent")
        audit.load()  # 不抛异常
        assert audit.record_count == 0

    def test_flush_without_path(self, audit: PositionAuditLogger) -> None:
        """无 persist_path 时 flush 是空操作。"""
        audit.log_position_sized(make_sizing_plan())
        audit.flush()  # 不抛异常


# ──────────────────────────────────────────────────────────────────────────────
# 7. 不可变测试 (C4)
# ──────────────────────────────────────────────────────────────────────────────


class TestFrozenRecord:
    """测试 PositionAuditRecord 不可变 (C4)。"""

    def test_record_is_frozen(self, audit: PositionAuditLogger) -> None:
        audit.log_position_sized(make_sizing_plan())
        rec = audit.query()[0]

        with pytest.raises(dataclasses.FrozenInstanceError):
            rec.symbol = "HACKED"

    def test_report_is_frozen(self, audit: PositionAuditLogger, t0: datetime) -> None:
        audit.log_position_sized(make_sizing_plan(timestamp=t0))
        report = audit.generate_report(
            period_start=t0 - timedelta(hours=1),
            period_end=t0 + timedelta(hours=1),
        )

        with pytest.raises(dataclasses.FrozenInstanceError):
            report.total_records = 999
