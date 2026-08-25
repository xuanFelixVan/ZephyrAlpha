# [BLUEPRINT] MOD-TRADING-011 | docs/03_modules/_domain_trading/manual_instruction_channel/blueprint.md | §test
# [MODULE] tests.trading.test_manual_instruction_channel
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.manual_instruction_channel
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_manual_instruction_channel.py
# [A_test] module_id: MOD-TRADING-011 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-TRADING-011 单元测试: ManualInstructionChannel — C-013 外部指令盯盘（人工指令通道）。

覆盖: 指令 schema 校验全边界、intake ACCEPTED / PREMARKET_NOT_READY / RISK_REJECTED /
PROBE_UNWIRED / PROBE_ERROR（Fail-Closed 未接线绝不臆造放行）、双闸不短路审计事件序、
reconcile MATCHED/DRIFT/UNFILLED/PROBE_ERROR、alert/audit 委托与吞没、输出 frozen。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from zephyr.trading.manual_instruction_channel import (
    ExecutionReconReport,
    InstructionAuditEvent,
    InstructionSide,
    IntakeVerdict,
    InvalidManualInstructionError,
    ManualInstruction,
    ManualInstructionChannel,
    ReconStatus,
)

T0 = datetime(2026, 8, 25, 9, 0, tzinfo=UTC)
T1 = T0 + timedelta(hours=6)


def _clock() -> datetime:
    return T0


def _instruction(**overrides) -> ManualInstruction:
    kwargs = {
        "instruction_id": "MI-0001",
        "symbol": "600519.SH",
        "side": InstructionSide.BUY,
        "quantity": Decimal("100"),
        "expire_at": T1,
        "operator": "trader-01",
        "created_at": T0,
    }
    kwargs.update(overrides)
    return ManualInstruction(**kwargs)


def _channel(**kwargs) -> ManualInstructionChannel:
    defaults = {
        "premarket_check_fn": lambda: True,
        "risk_check_fn": lambda ins: (True, "OK"),
        "clock": _clock,
    }
    defaults.update(kwargs)
    return ManualInstructionChannel(**defaults)


# ── ① schema 校验 ───────────────────────────────────────────────


class TestInstructionSchema:
    def test_valid_instruction(self) -> None:
        ins = _instruction()
        assert ins.instruction_id == "MI-0001"
        assert ins.side is InstructionSide.BUY

    @pytest.mark.parametrize(
        "field,value",
        [
            ("instruction_id", ""),
            ("symbol", ""),
            ("operator", ""),
        ],
    )
    def test_empty_required_field_rejected(self, field: str, value: str) -> None:
        with pytest.raises(InvalidManualInstructionError):
            _instruction(**{field: value})

    def test_non_positive_quantity_rejected(self) -> None:
        with pytest.raises(InvalidManualInstructionError):
            _instruction(quantity=Decimal("0"))
        with pytest.raises(InvalidManualInstructionError):
            _instruction(quantity=Decimal("-5"))

    def test_non_decimal_quantity_rejected(self) -> None:
        with pytest.raises(InvalidManualInstructionError):
            _instruction(quantity=100)  # type: ignore[arg-type]

    def test_expired_window_rejected(self) -> None:
        with pytest.raises(InvalidManualInstructionError):
            _instruction(expire_at=T0)  # expire 必须严格晚于 created
        with pytest.raises(InvalidManualInstructionError):
            _instruction(expire_at=T0 - timedelta(minutes=1))

    def test_instruction_frozen(self) -> None:
        ins = _instruction()
        with pytest.raises(Exception):
            ins.quantity = Decimal("1")  # type: ignore[misc]


# ── ② intake 裁决 ───────────────────────────────────────────────


class TestIntake:
    def test_accepted_when_both_gates_pass(self) -> None:
        verdict = _channel().intake(_instruction())
        assert isinstance(verdict, IntakeVerdict)
        assert verdict.accepted is True
        assert verdict.reason_code == "ACCEPTED"

    def test_premarket_not_ready_rejects(self) -> None:
        verdict = _channel(premarket_check_fn=lambda: False).intake(_instruction())
        assert verdict.accepted is False
        assert verdict.reason_code == "PREMARKET_NOT_READY"

    def test_risk_rejected(self) -> None:
        verdict = _channel(risk_check_fn=lambda ins: (False, " KillSwitch 熔断中 ")).intake(_instruction())
        assert verdict.accepted is False
        assert verdict.reason_code == "RISK_REJECTED"
        assert "KillSwitch" in verdict.reason

    def test_unwired_premarket_probe_fail_closed(self) -> None:
        verdict = _channel(premarket_check_fn=None).intake(_instruction())
        assert verdict.accepted is False
        assert verdict.reason_code == "PROBE_UNWIRED"

    def test_unwired_risk_probe_fail_closed(self) -> None:
        verdict = _channel(risk_check_fn=None).intake(_instruction())
        assert verdict.accepted is False
        assert verdict.reason_code == "PROBE_UNWIRED"

    def test_probe_exception_fail_closed(self) -> None:
        def boom() -> bool:
            raise RuntimeError("premarket down")

        verdict = _channel(premarket_check_fn=boom).intake(_instruction())
        assert verdict.accepted is False
        assert verdict.reason_code == "PROBE_ERROR"

    def test_risk_probe_exception_fail_closed(self) -> None:
        def boom(ins) -> tuple[bool, str]:
            raise RuntimeError("risk down")

        verdict = _channel(risk_check_fn=boom).intake(_instruction())
        assert verdict.accepted is False
        assert verdict.reason_code == "PROBE_ERROR"

    def test_both_gates_evaluated_no_short_circuit(self) -> None:
        calls: list[str] = []
        verdict = _channel(
            premarket_check_fn=lambda: calls.append("pre") or False,
            risk_check_fn=lambda ins: calls.append("risk") or (False, "限额越界"),
        ).intake(_instruction())
        assert verdict.accepted is False
        assert calls == ["pre", "risk"]  # 双闸全量评估不短路
        stages = [e.stage for e in verdict.audit_trail]
        assert stages == ["RECEIVED", "PREMARKET", "RISK", "VERDICT"]

    def test_audit_trail_sequence_and_clock(self) -> None:
        verdict = _channel().intake(_instruction())
        stages = [e.stage for e in verdict.audit_trail]
        assert stages == ["RECEIVED", "PREMARKET", "RISK", "VERDICT"]
        assert [e.seq for e in verdict.audit_trail] == [1, 2, 3, 4]
        assert all(isinstance(e, InstructionAuditEvent) for e in verdict.audit_trail)
        assert all(e.at == T0 for e in verdict.audit_trail)

    def test_audit_sink_receives_each_event(self) -> None:
        events: list[InstructionAuditEvent] = []
        _channel(audit_sink=events.append).intake(_instruction())
        assert [e.stage for e in events] == ["RECEIVED", "PREMARKET", "RISK", "VERDICT"]

    def test_audit_sink_exception_swallowed(self) -> None:
        def bad_sink(e: InstructionAuditEvent) -> None:
            raise RuntimeError("audit down")

        verdict = _channel(audit_sink=bad_sink).intake(_instruction())
        assert verdict.accepted is True  # 主链不被审计出口拖死


# ── ③ 执行回报对账 ──────────────────────────────────────────────


@dataclass(frozen=True)
class _FillReport:
    filled_quantity: Decimal


class TestReconcile:
    def test_matched(self) -> None:
        report = _channel().reconcile(_instruction(), lambda iid: _FillReport(Decimal("100")))
        assert isinstance(report, ExecutionReconReport)
        assert report.status is ReconStatus.MATCHED
        assert report.filled_quantity == Decimal("100")
        assert report.expected_quantity == Decimal("100")

    def test_drift_alerts_and_audits(self) -> None:
        alerts: list[str] = []
        events: list[InstructionAuditEvent] = []
        report = _channel(alert_sink=alerts.append, audit_sink=events.append).reconcile(
            _instruction(), lambda iid: _FillReport(Decimal("80"))
        )
        assert report.status is ReconStatus.DRIFT
        assert len(alerts) == 1 and "MI-0001" in alerts[0]
        assert any(e.stage == "RECONCILE" and e.outcome == "DRIFT" for e in events)

    def test_unfilled_when_probe_returns_none(self) -> None:
        report = _channel().reconcile(_instruction(), lambda iid: None)
        assert report.status is ReconStatus.UNFILLED
        assert report.filled_quantity == Decimal("0")

    def test_probe_error(self) -> None:
        alerts: list[str] = []

        def boom(iid: str):
            raise RuntimeError("broker api down")

        report = _channel(alert_sink=alerts.append).reconcile(_instruction(), boom)
        assert report.status is ReconStatus.PROBE_ERROR
        assert len(alerts) == 1

    def test_qty_tolerance_config(self) -> None:
        # 容差内（含恰等）→ MATCHED；越界 → DRIFT
        ch = _channel(qty_tolerance=Decimal("5"))
        assert ch.reconcile(_instruction(), lambda iid: _FillReport(Decimal("95"))).status is ReconStatus.MATCHED
        assert ch.reconcile(_instruction(), lambda iid: _FillReport(Decimal("94"))).status is ReconStatus.DRIFT

    def test_alert_sink_exception_swallowed(self) -> None:
        def bad_sink(m: str) -> None:
            raise RuntimeError("alert down")

        report = _channel(alert_sink=bad_sink).reconcile(_instruction(), lambda iid: _FillReport(Decimal("80")))
        assert report.status is ReconStatus.DRIFT
