# [BLUEPRINT] MOD-OPS-002 | docs/03_modules/_domain_infrastructure/incident_responder/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-OPS-002 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.infrastructure.system_telemetry.test_incident_responder
# [TESTS] src/zephyr/infrastructure/system_telemetry/incident_responder.py
"""MOD-OPS-002 单元测试：incident_responder 事件响应器。

蓝图验收（B9-11645/CAND-OPS-002，B9 OPS-03）：
P0~P2 分级解析 + 自动处置策略表（事件类型→handler 注入，未注册 Fail-Closed）
+ 升级规则（超时判 TIMEOUT 不重试 / 失败按 max_attempts 重试，注入时钟）
+ 处置结果回写学习（PolicyEffectiveness 效果统计）。
时钟/handler/升级回调全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.infrastructure.system_telemetry.incident_responder",
    reason="incident_responder not importable",
)

from zephyr.infrastructure.system_telemetry.incident_responder import (  # noqa: E402
    EscalationRule,
    IncidentResponder,
    IncidentResponderError,
    RemediationOutcome,
)
from zephyr.infrastructure.system_telemetry.ops_incident_aggregate import (  # noqa: E402
    IncidentSeverity,
    IncidentStatus,
    OpsIncident,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 0, 0)


class _Clock:
    """确定性注入时钟（handler 内可推进）。"""

    def __init__(self) -> None:
        self.now = _T0

    def __call__(self) -> datetime.datetime:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += datetime.timedelta(seconds=seconds)


def _incident(
    incident_id: str = "INC-1",
    severity: IncidentSeverity = IncidentSeverity.P1,
) -> OpsIncident:
    return OpsIncident(
        incident_id=incident_id,
        severity=severity,
        status=IncidentStatus.OPEN,
        title="撮合延迟突增",
        source="latency_attributor",
        detected_at=_T0,
        updated_at=_T0,
        history=(),
    )


def _responder(
    clock: _Clock | None = None,
    rules: dict | None = None,
    escalations: list | None = None,
) -> IncidentResponder:
    return IncidentResponder(
        clock=(clock or _Clock()),
        rules=rules,
        escalation_sink=(
            (lambda inc, reason: escalations.append((inc.incident_id, reason)))
            if escalations is not None else None
        ),
    )


# ──────────────────────────────────────────────────────────────────────────────
# 事件分级（P0~P2 词表）
# ──────────────────────────────────────────────────────────────────────────────


class TestClassify:
    def test_enum_passthrough(self) -> None:
        assert IncidentResponder.classify(IncidentSeverity.P0) is IncidentSeverity.P0

    def test_str_values(self) -> None:
        assert IncidentResponder.classify("P0") is IncidentSeverity.P0
        assert IncidentResponder.classify("P1") is IncidentSeverity.P1
        assert IncidentResponder.classify("P2") is IncidentSeverity.P2

    def test_invalid_raises(self) -> None:
        for raw in ("P9", "", "p1", 123, None):
            with pytest.raises(IncidentResponderError):
                IncidentResponder.classify(raw)


# ──────────────────────────────────────────────────────────────────────────────
# 策略表
# ──────────────────────────────────────────────────────────────────────────────


class TestPolicy:
    def test_register_policy_ok(self) -> None:
        r = _responder()
        r.register_policy("latency_spike", lambda inc: True)
        rec = r.respond(_incident(), "latency_spike")
        assert rec.outcome is RemediationOutcome.SUCCESS

    def test_register_empty_event_type_raises(self) -> None:
        r = _responder()
        with pytest.raises(IncidentResponderError):
            r.register_policy("", lambda inc: True)

    def test_register_non_callable_raises(self) -> None:
        r = _responder()
        with pytest.raises(IncidentResponderError):
            r.register_policy("x", "not-callable")  # type: ignore[arg-type]

    def test_respond_unregistered_event_type_raises(self) -> None:
        r = _responder()
        with pytest.raises(IncidentResponderError):
            r.respond(_incident(), "ghost_type")

    def test_respond_empty_event_type_raises(self) -> None:
        r = _responder()
        with pytest.raises(IncidentResponderError):
            r.respond(_incident(), "")

    def test_respond_invalid_incident_raises(self) -> None:
        r = _responder()
        r.register_policy("x", lambda inc: True)
        with pytest.raises(IncidentResponderError):
            r.respond("not-an-incident", "x")  # type: ignore[arg-type]

    def test_invalid_rule_raises(self) -> None:
        with pytest.raises(IncidentResponderError):
            _responder(rules={IncidentSeverity.P0: EscalationRule(0, 60.0)})
        with pytest.raises(IncidentResponderError):
            _responder(rules={IncidentSeverity.P0: EscalationRule(1, 0.0)})
        with pytest.raises(IncidentResponderError):
            _responder(rules={"P0": EscalationRule(1, 60.0)})  # type: ignore[dict-item]


# ──────────────────────────────────────────────────────────────────────────────
# 处置执行（重试/超时/升级）
# ──────────────────────────────────────────────────────────────────────────────


class TestRespond:
    def test_success_first_attempt(self) -> None:
        r = _responder()
        r.register_policy("latency_spike", lambda inc: True)
        rec = r.respond(_incident(), "latency_spike")
        assert rec.outcome is RemediationOutcome.SUCCESS
        assert rec.attempts == 1
        assert rec.escalated is False

    def test_failure_retries_then_success(self) -> None:
        calls = {"n": 0}

        def _flaky(inc: OpsIncident) -> bool:
            calls["n"] += 1
            return calls["n"] >= 2  # 首次失败，第二次成功

        r = _responder(rules={IncidentSeverity.P1: EscalationRule(3, 60.0)})
        r.register_policy("latency_spike", _flaky)
        rec = r.respond(_incident(), "latency_spike")
        assert rec.outcome is RemediationOutcome.SUCCESS
        assert rec.attempts == 2

    def test_all_attempts_failed_escalates(self) -> None:
        escalations: list = []
        r = _responder(
            rules={IncidentSeverity.P1: EscalationRule(2, 60.0)},
            escalations=escalations,
        )
        r.register_policy("latency_spike", lambda inc: False)
        rec = r.respond(_incident(), "latency_spike")
        assert rec.outcome is RemediationOutcome.FAILED
        assert rec.attempts == 2
        assert rec.escalated is True
        assert len(escalations) == 1
        assert escalations[0][0] == "INC-1"
        assert "failed" in escalations[0][1]

    def test_handler_exception_treated_as_failure(self) -> None:
        def _boom(inc: OpsIncident) -> bool:
            raise RuntimeError("handler boom")

        escalations: list = []
        r = _responder(escalations=escalations)
        r.register_policy("latency_spike", _boom)
        rec = r.respond(_incident(), "latency_spike")
        assert rec.outcome is RemediationOutcome.FAILED
        assert rec.escalated is True

    def test_timeout_no_retry_and_escalates(self) -> None:
        clock = _Clock()

        def _slow(inc: OpsIncident) -> bool:
            clock.advance(120.0)  # 单次耗时 120s 超 timeout 60s
            return True

        escalations: list = []
        r = _responder(
            clock=clock,
            rules={IncidentSeverity.P1: EscalationRule(3, 60.0)},
            escalations=escalations,
        )
        r.register_policy("latency_spike", _slow)
        rec = r.respond(_incident(), "latency_spike")
        assert rec.outcome is RemediationOutcome.TIMEOUT
        assert rec.attempts == 1  # 超时不重试
        assert rec.escalated is True
        assert "timeout" in escalations[0][1]

    def test_within_timeout_success(self) -> None:
        clock = _Clock()

        def _ok(inc: OpsIncident) -> bool:
            clock.advance(30.0)
            return True

        r = _responder(clock=clock, rules={IncidentSeverity.P1: EscalationRule(1, 60.0)})
        r.register_policy("latency_spike", _ok)
        rec = r.respond(_incident(), "latency_spike")
        assert rec.outcome is RemediationOutcome.SUCCESS
        assert rec.elapsed_seconds == pytest.approx(30.0)

    def test_severity_specific_rule_applied(self) -> None:
        calls = {"n": 0}

        def _always_fail(inc: OpsIncident) -> bool:
            calls["n"] += 1
            return False

        r = _responder(rules={
            IncidentSeverity.P0: EscalationRule(3, 60.0),
            IncidentSeverity.P2: EscalationRule(1, 60.0),
        })
        r.register_policy("x", _always_fail)
        rec_p0 = r.respond(_incident("INC-P0", IncidentSeverity.P0), "x")
        rec_p1 = r.respond(_incident("INC-P1", IncidentSeverity.P1), "x")  # 默认规则
        assert rec_p0.attempts == 3
        assert rec_p1.attempts == 1  # DEFAULT_RULE max_attempts=1

    def test_failure_without_sink_not_escalated(self) -> None:
        r = _responder()  # 未注入 escalation_sink
        r.register_policy("x", lambda inc: False)
        rec = r.respond(_incident(), "x")
        assert rec.outcome is RemediationOutcome.FAILED
        assert rec.escalated is False

    def test_sink_exception_not_blocking(self) -> None:
        r = IncidentResponder(
            clock=_Clock(),
            escalation_sink=lambda inc, reason: (_ for _ in ()).throw(RuntimeError("x")),
        )
        r.register_policy("x", lambda inc: False)
        rec = r.respond(_incident(), "x")
        assert rec.outcome is RemediationOutcome.FAILED
        assert rec.escalated is False


# ──────────────────────────────────────────────────────────────────────────────
# 回写学习（效果统计）
# ──────────────────────────────────────────────────────────────────────────────


class TestLearning:
    def _trained(self) -> IncidentResponder:
        r = _responder(rules={IncidentSeverity.P1: EscalationRule(2, 60.0)})
        r.register_policy("ok_type", lambda inc: True)
        r.register_policy("bad_type", lambda inc: False)
        r.respond(_incident("INC-1"), "ok_type")
        r.respond(_incident("INC-2"), "ok_type")
        r.respond(_incident("INC-3"), "bad_type")
        return r

    def test_policy_effectiveness_counts(self) -> None:
        eff = self._trained().policy_effectiveness("bad_type")
        assert eff.responds == 1
        assert eff.attempts == 2  # max_attempts=2 全部用尽
        assert eff.failures == 1
        assert eff.successes == 0
        assert eff.success_rate == 0.0

    def test_success_rate_calculation(self) -> None:
        eff = self._trained().policy_effectiveness("ok_type")
        assert eff.responds == 2
        assert eff.successes == 2
        assert eff.success_rate == 1.0

    def test_effectiveness_table_sorted(self) -> None:
        table = self._trained().effectiveness_table()
        assert [e.event_type for e in table] == ["bad_type", "ok_type"]

    def test_effectiveness_unknown_type_raises(self) -> None:
        with pytest.raises(IncidentResponderError):
            self._trained().policy_effectiveness("ghost")

    def test_records_in_order(self) -> None:
        rs = self._trained().records()
        assert [r.incident_id for r in rs] == ["INC-1", "INC-2", "INC-3"]

    def test_determinism_same_inputs_same_records(self) -> None:
        a = self._trained().records()
        b = self._trained().records()
        assert a == b
