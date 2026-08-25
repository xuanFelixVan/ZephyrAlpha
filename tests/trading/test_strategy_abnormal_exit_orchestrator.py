# [BLUEPRINT] MOD-TRADING-008 | docs/03_modules/_domain_trading/strategy_abnormal_exit/blueprint.md | §test
# [A_test] module_id: MOD-TRADING-008 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""StrategyAbnormalExitOrchestrator 单元测试 (MOD-TRADING-008, D-SIGNAL-150 MVP)。

覆盖: 三触发路径(CRASH/TIMEOUT/RISK_TRIGGERED) / 五步编排顺序(冻结→撤单→平仓→
核对→置态) / 冻结失败不宣称EXITED(Fail-Closed) / 优先级降序撤单平仓 / 核对残留
EXIT_FAILED+升级告警 / 幂等键重放缓存 / 单腿异常隔离 / 生命周期事件契约 / frozen不可变。
"""

from __future__ import annotations

import dataclasses
from datetime import UTC, datetime

import pytest

pytest.importorskip(
    "zephyr.trading.strategy_abnormal_exit_orchestrator",
    reason="strategy_abnormal_exit_orchestrator not importable",
)

from zephyr.trading.strategy_abnormal_exit_orchestrator import (  # noqa: E402
    AbnormalExitReport,
    AbnormalExitRequest,
    ExitFinalStatus,
    ExitLeg,
    ExitTrigger,
    InvalidExitRequestError,
    StrategyAbnormalExitOrchestrator,
)

_NOW = datetime(2026, 8, 25, 1, 30, tzinfo=UTC)


def _legs(*specs: tuple[str, int]) -> tuple[ExitLeg, ...]:
    return tuple(ExitLeg(ref_id=rid, priority=prio) for rid, prio in specs)


def _request(**overrides) -> AbnormalExitRequest:
    base = dict(
        strategy_id="STRAT-001",
        trigger=ExitTrigger.CRASH,
        reason="strategy process crashed",
        open_orders=_legs(("ORD-LOW", 1), ("ORD-HIGH", 9), ("ORD-MID", 5)),
        positions=_legs(("POS-LOW", 1), ("POS-HIGH", 9)),
        idempotency_key="IDEMP-0001",
    )
    base.update(overrides)
    return AbnormalExitRequest(**base)


class _Ports:
    """注入端口测试桩：记录调用序列与载荷。"""

    def __init__(self, *, freeze_ok: bool = True, remaining: tuple[str, ...] = ()) -> None:
        self.calls: list[str] = []
        self.alerts: list[tuple[str, dict]] = []
        self.audits: list[tuple[str, dict]] = []
        self.lifecycle_events: list[object] = []
        self._freeze_ok = freeze_ok
        self._remaining = remaining
        self.fail_on: set[str] = set()

    def freezer(self, strategy_id: str) -> bool:
        self.calls.append(f"freeze:{strategy_id}")
        if "freeze" in self.fail_on:
            raise RuntimeError("freezer boom")
        return self._freeze_ok

    def canceller(self, ref_id: str) -> None:
        self.calls.append(f"cancel:{ref_id}")
        if ref_id in self.fail_on:
            raise RuntimeError(f"cancel {ref_id} boom")

    def closer(self, ref_id: str) -> None:
        self.calls.append(f"close:{ref_id}")
        if ref_id in self.fail_on:
            raise RuntimeError(f"close {ref_id} boom")

    def verifier(self, strategy_id: str) -> tuple[str, ...]:
        self.calls.append(f"verify:{strategy_id}")
        if "verify" in self.fail_on:
            raise RuntimeError("verifier boom")
        return self._remaining

    def recorder(self, event: object) -> None:
        self.calls.append("record")
        if "record" in self.fail_on:
            raise RuntimeError("recorder boom")
        self.lifecycle_events.append(event)

    def alert(self, level: str, payload: dict) -> None:
        self.alerts.append((level, payload))

    def audit(self, event: str, payload: dict) -> None:
        self.audits.append((event, payload))


def _orch(ports: _Ports) -> StrategyAbnormalExitOrchestrator:
    return StrategyAbnormalExitOrchestrator(
        signal_freezer=ports.freezer,
        order_canceller=ports.canceller,
        position_closer=ports.closer,
        position_verifier=ports.verifier,
        lifecycle_recorder=ports.recorder,
        alert_sink=ports.alert,
        audit_sink=ports.audit,
        clock=lambda: _NOW,
    )


# ── 三触发路径 happy path ─────────────────────────────────────────────


@pytest.mark.parametrize(
    "trigger",
    [ExitTrigger.CRASH, ExitTrigger.TIMEOUT, ExitTrigger.RISK_TRIGGERED],
)
def test_three_trigger_paths_exited(trigger: ExitTrigger) -> None:
    ports = _Ports()
    report = _orch(ports).execute(_request(trigger=trigger))
    assert report.final_status is ExitFinalStatus.EXITED
    assert report.trigger is trigger
    assert report.freeze_ok is True
    assert report.failed_legs == ()
    assert report.remaining_positions == ()
    assert len(ports.lifecycle_events) == 1
    assert report.alerts_emitted >= 1
    assert report.audit_records >= 2


# ── 编排顺序：冻结在最前，撤单/平仓按优先级降序，核对在置态前 ──────────


def test_orchestration_order_and_priority() -> None:
    ports = _Ports()
    _orch(ports).execute(_request())
    assert ports.calls[0] == "freeze:STRAT-001"
    cancel_idx = [i for i, c in enumerate(ports.calls) if c.startswith("cancel:")]
    close_idx = [i for i, c in enumerate(ports.calls) if c.startswith("close:")]
    verify_idx = ports.calls.index("verify:STRAT-001")
    record_idx = ports.calls.index("record")
    # 撤单优先级降序
    assert [ports.calls[i] for i in cancel_idx] == [
        "cancel:ORD-HIGH",
        "cancel:ORD-MID",
        "cancel:ORD-LOW",
    ]
    # 平仓优先级降序
    assert [ports.calls[i] for i in close_idx] == ["close:POS-HIGH", "close:POS-LOW"]
    # 冻结 < 撤单 < 平仓 < 核对 < 置态
    assert 0 < cancel_idx[0] < close_idx[0] < verify_idx < record_idx


# ── 冻结失败：不宣称 EXITED，但撤单/平仓仍继续（安全方向），升级告警 ────


def test_freeze_failure_exit_failed_but_cleanup_continues() -> None:
    ports = _Ports(freeze_ok=False)
    report = _orch(ports).execute(_request())
    assert report.final_status is ExitFinalStatus.EXIT_FAILED
    assert report.freeze_ok is False
    assert "cancel:ORD-HIGH" in ports.calls
    assert "close:POS-HIGH" in ports.calls
    assert ports.lifecycle_events == []  # 不置 EXITED
    assert any(level == "CRITICAL" for level, _ in ports.alerts)


def test_freezer_exception_treated_as_failure() -> None:
    ports = _Ports()
    ports.fail_on.add("freeze")
    report = _orch(ports).execute(_request())
    assert report.final_status is ExitFinalStatus.EXIT_FAILED
    assert report.freeze_ok is False
    assert any(leg.phase == "freeze" for leg in report.failed_legs)


# ── 核对残留：EXIT_FAILED + 升级告警 ─────────────────────────────────


def test_remaining_positions_exit_failed() -> None:
    ports = _Ports(remaining=("POS-HIGH",))
    report = _orch(ports).execute(_request())
    assert report.final_status is ExitFinalStatus.EXIT_FAILED
    assert report.remaining_positions == ("POS-HIGH",)
    assert ports.lifecycle_events == []
    assert any(level == "CRITICAL" for level, _ in ports.alerts)


def test_verifier_exception_fail_closed() -> None:
    ports = _Ports()
    ports.fail_on.add("verify")
    report = _orch(ports).execute(_request())
    assert report.final_status is ExitFinalStatus.EXIT_FAILED
    assert any(leg.phase == "verify" for leg in report.failed_legs)


# ── 单腿异常隔离：其余腿继续，最终不得宣称 EXITED ──────────────────────


def test_single_leg_failure_isolated() -> None:
    ports = _Ports()
    ports.fail_on.add("ORD-MID")
    report = _orch(ports).execute(_request())
    assert "cancel:ORD-LOW" in ports.calls  # 后续腿继续
    assert "close:POS-HIGH" in ports.calls
    assert report.final_status is ExitFinalStatus.EXIT_FAILED
    failed = report.failed_legs
    assert len(failed) == 1 and failed[0].phase == "cancel_order" and failed[0].ref_id == "ORD-MID"
    assert report.cancelled_order_ids == ("ORD-HIGH", "ORD-LOW")


def test_recorder_exception_fail_closed() -> None:
    ports = _Ports()
    ports.fail_on.add("record")
    report = _orch(ports).execute(_request())
    assert report.final_status is ExitFinalStatus.EXIT_FAILED
    assert any(leg.phase == "record_status" for leg in report.failed_legs)


# ── 幂等：同 idempotency_key 重放返回缓存报告，端口不重复调用 ──────────


def test_idempotency_replay_returns_cached_report() -> None:
    ports = _Ports()
    orch = _orch(ports)
    first = orch.execute(_request())
    calls_after_first = len(ports.calls)
    second = orch.execute(_request())
    assert second is first
    assert len(ports.calls) == calls_after_first


# ── 生命周期事件契约（CTR-P1-006）────────────────────────────────────


def test_lifecycle_event_contract() -> None:
    ports = _Ports()
    _orch(ports).execute(_request())
    event = ports.lifecycle_events[0]
    assert event.strategy_id == "STRAT-001"
    assert event.new_status == "EXITED"
    assert event.previous_status == "ACTIVE"
    assert event.idempotency_key == "IDEMP-0001"
    assert event.triggered_by == ExitTrigger.CRASH.value
    assert "crash" in event.reason


# ── 校验与不可变 ──────────────────────────────────────────────────────


def test_invalid_request_raises() -> None:
    ports = _Ports()
    with pytest.raises(InvalidExitRequestError):
        _orch(ports).execute(_request(strategy_id=""))
    with pytest.raises(InvalidExitRequestError):
        _orch(ports).execute(_request(idempotency_key=""))


def test_report_frozen() -> None:
    ports = _Ports()
    report = _orch(ports).execute(_request())
    assert isinstance(report, AbnormalExitReport)
    with pytest.raises(dataclasses.FrozenInstanceError):
        report.final_status = ExitFinalStatus.EXIT_FAILED  # type: ignore[misc]


# ── 集成面：finalizer 清理函数 + 未决退出探针 ─────────────────────────


def test_has_unresolved_exits_and_finalizer_cleanup() -> None:
    ports = _Ports(remaining=("POS-X",))
    orch = _orch(ports)
    assert orch.has_unresolved_exits() is False
    orch.execute(_request(positions=_legs(("POS-X", 1))))
    assert orch.has_unresolved_exits() is True
    cleanup = orch.make_finalizer_cleanup()
    cleanup()  # 永不抛异常（finalizer 语义）
