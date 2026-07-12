# [A_test] module_id: SRC-TST-1783 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §3.1
# [MODULE] tests.test_verdict_engine
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_verdict_engine.py -q
# [TTL] task_bound

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import pytest

from zephyr.trading.verdict_engine import (
    _YELLOW_TRUST_THRESHOLD,
    _YELLOW_VIOLATION_THRESHOLD,
    ActorInfo,
    AuditEvent,
    AuthCheckResult,
    EvidenceChain,
    GraduatedLevel,
    MultiModelResult,
    OperationInfo,
    ProtectionLevel,
    ResponseInfo,
    Verdict,
    VerdictEngine,
    VerdictLevel,
)


def _audit_event(**overrides) -> AuditEvent:
    defaults = dict(
        event_type="file_write",
        agent_id="agent-001",
        session_id="sess-001",
        target_path="src/zephyr/core.py",
        operation="write",
        is_human=False,
        is_cross_module=False,
        protection_level="normal",
        gate_passed=False,
        trust_score=50.0,
        violation_count=0,
        timestamp="2026-05-23T00:00:00Z",
    )
    defaults.update(overrides)
    return AuditEvent(**defaults)


class TestVerdictLevel:
    def test_values(self):
        assert VerdictLevel.PASS == "PASS"
        assert VerdictLevel.YELLOW == "YELLOW"
        assert VerdictLevel.RED == "RED"

    def test_is_str_enum(self):
        assert isinstance(VerdictLevel.PASS, str)


class TestProtectionLevel:
    def test_values(self):
        assert ProtectionLevel.anchor == "anchor"
        assert ProtectionLevel.protected == "protected"
        assert ProtectionLevel.normal == "normal"
        assert ProtectionLevel.public == "public"

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            ProtectionLevel("top_secret")


class TestGraduatedLevel:
    def test_values(self):
        assert GraduatedLevel.L0 == 0
        assert GraduatedLevel.L1 == 1
        assert GraduatedLevel.L2 == 2
        assert GraduatedLevel.L3 == 3
        assert GraduatedLevel.L4 == 4
        assert GraduatedLevel.L5 == 5
        assert GraduatedLevel.L6 == 6

    def test_ordering(self):
        assert GraduatedLevel.L0 < GraduatedLevel.L3 < GraduatedLevel.L6


class TestActorInfo:
    def test_defaults(self):
        a = ActorInfo()
        assert a.agent_id == ""
        assert a.is_human is False
        assert a.trust_score == 50.0
        assert a.violation_count == 0

    def test_custom(self):
        a = ActorInfo(agent_id="a1", is_human=True, trust_score=10.0, violation_count=5)
        assert a.agent_id == "a1"
        assert a.is_human is True
        assert a.trust_score == 10.0
        assert a.violation_count == 5


class TestOperationInfo:
    def test_defaults(self):
        o = OperationInfo()
        assert o.operation == ""
        assert o.protection_level == ProtectionLevel.normal
        assert o.is_cross_module is False

    def test_custom(self):
        o = OperationInfo(
            operation="delete",
            target_path="src/zephyr/x.py",
            is_cross_module=True,
            protection_level=ProtectionLevel.anchor,
        )
        assert o.protection_level == ProtectionLevel.anchor


class TestAuthCheckResult:
    def test_defaults(self):
        r = AuthCheckResult()
        assert r.gate_passed is False
        assert r.gate_id == ""
        assert r.check_duration_ms == 0.0
        assert r.error == ""


class TestResponseInfo:
    def test_defaults(self):
        r = ResponseInfo()
        assert r.verdict == VerdictLevel.PASS
        assert r.graduated_level == GraduatedLevel.L0
        assert r.reason == ""
        assert r.requires_consensus is False
        assert r.latency_ms == 0.0


class TestEvidenceChain:
    def test_defaults(self):
        e = EvidenceChain()
        assert isinstance(e.actor, ActorInfo)
        assert isinstance(e.operation, OperationInfo)
        assert isinstance(e.auth_check, AuthCheckResult)
        assert isinstance(e.response, ResponseInfo)


class TestMultiModelResult:
    def test_defaults(self):
        m = MultiModelResult()
        assert m.model_id == ""
        assert m.verdict == VerdictLevel.PASS
        assert m.confidence == 0.0
        assert m.reasoning == ""
        assert m.latency_ms == 0.0


class TestVerdict:
    def test_defaults(self):
        v = Verdict()
        assert v.verdict_level == VerdictLevel.PASS
        assert v.graduated_level == GraduatedLevel.L0
        assert v.protection_level == ProtectionLevel.normal
        assert v.gate_passed is False
        assert v.requires_consensus is False
        assert isinstance(v.evidence, EvidenceChain)
        assert v.multi_model_results == []
        assert v.reason == ""

    def test_custom(self):
        v = Verdict(
            verdict_level=VerdictLevel.RED,
            graduated_level=GraduatedLevel.L6,
            protection_level=ProtectionLevel.anchor,
            gate_passed=False,
            requires_consensus=True,
            reason="ai_on_anchor_blocked",
        )
        assert v.verdict_level == VerdictLevel.RED
        assert v.requires_consensus is True


class TestVerdictEngineInit:
    def test_defaults(self):
        engine = VerdictEngine()
        assert engine._protection_index is None
        assert engine._gpu_scheduler is None
        assert engine._verdict_timeout_s == 10.0
        assert engine._eval_count == 0
        assert engine._red_count == 0
        assert engine._yellow_count == 0
        assert engine._pass_count == 0

    def test_custom_timeout(self):
        engine = VerdictEngine(verdict_timeout_s=30.0)
        assert engine._verdict_timeout_s == 30.0

    def test_with_dependencies(self):
        pi = MagicMock()
        gs = MagicMock()
        engine = VerdictEngine(protection_index=pi, gpu_scheduler=gs)
        assert engine._protection_index is pi
        assert engine._gpu_scheduler is gs


@pytest.mark.asyncio
class TestEvaluate:
    async def test_human_actor_pass(self):
        engine = VerdictEngine()
        event = _audit_event(is_human=True, protection_level="anchor")
        result = await engine.evaluate(event)
        assert result.verdict_level == VerdictLevel.PASS
        assert result.reason == "human_actor_auto_pass"

    async def test_human_actor_pass_even_on_anchor(self):
        engine = VerdictEngine()
        event = _audit_event(is_human=True, protection_level="anchor", is_cross_module=True)
        result = await engine.evaluate(event)
        assert result.verdict_level == VerdictLevel.PASS

    async def test_cross_module_blocked(self):
        engine = VerdictEngine()
        event = _audit_event(is_cross_module=True)
        result = await engine.evaluate(event)
        assert result.verdict_level == VerdictLevel.RED
        assert result.reason == "cross_module_blocked"

    async def test_anchor_blocked(self):
        engine = VerdictEngine()
        event = _audit_event(protection_level="anchor")
        result = await engine.evaluate(event)
        assert result.verdict_level == VerdictLevel.RED
        assert result.reason == "ai_on_anchor_blocked"

    async def test_protected_no_gate(self):
        engine = VerdictEngine()
        event = _audit_event(protection_level="protected", gate_passed=False)
        result = await engine.evaluate(event)
        assert result.verdict_level == VerdictLevel.RED
        assert result.reason == "ai_on_protected_no_gate"

    async def test_protected_with_gate(self):
        engine = VerdictEngine()
        event = _audit_event(protection_level="protected", gate_passed=True)
        result = await engine.evaluate(event)
        assert result.verdict_level == VerdictLevel.PASS
        assert result.reason == "ai_on_protected_gate_passed"

    async def test_normal_low_trust(self):
        engine = VerdictEngine()
        event = _audit_event(protection_level="normal", trust_score=20.0)
        result = await engine.evaluate(event)
        assert result.verdict_level == VerdictLevel.YELLOW
        assert result.reason == "low_trust_score"

    async def test_normal_high_violation_count(self):
        engine = VerdictEngine()
        event = _audit_event(protection_level="normal", trust_score=50.0, violation_count=3)
        result = await engine.evaluate(event)
        assert result.verdict_level == VerdictLevel.YELLOW
        assert result.reason == "high_violation_count"

    async def test_normal_pass(self):
        engine = VerdictEngine()
        event = _audit_event(protection_level="normal", trust_score=50.0, violation_count=0)
        result = await engine.evaluate(event)
        assert result.verdict_level == VerdictLevel.PASS
        assert result.reason == "ai_on_normal"

    async def test_public_pass(self):
        engine = VerdictEngine()
        event = _audit_event(protection_level="public")
        result = await engine.evaluate(event)
        assert result.verdict_level == VerdictLevel.PASS
        assert result.reason == "ai_on_public"

    async def test_unknown_event_type_red(self):
        engine = VerdictEngine()
        result = await engine.evaluate("not_a_valid_event")
        assert result.verdict_level == VerdictLevel.RED
        assert result.reason == "unknown_event_type"
        assert result.graduated_level == GraduatedLevel.L6

    async def test_dict_event(self):
        engine = VerdictEngine()
        event = {
            "agent_id": "agent-002",
            "is_human": False,
            "trust-score": 50.0,
            "violation_count": 0,
            "operation": "read",
            "target_path": "src/zephyr/x.py",
            "is_cross_module": False,
            "protection_level": "public",
            "gate_passed": False,
        }
        result = await engine.evaluate(event)
        assert result.verdict_level == VerdictLevel.PASS
        assert result.reason == "ai_on_public"

    async def test_dict_event_cross_module(self):
        engine = VerdictEngine()
        event = {"is_cross_module": True, "is_human": False}
        result = await engine.evaluate(event)
        assert result.verdict_level == VerdictLevel.RED
        assert result.reason == "cross_module_blocked"

    async def test_dict_event_invalid_protection_level(self):
        engine = VerdictEngine()
        event = {"protection_level": "top_secret", "is_human": False}
        result = await engine.evaluate(event)
        assert result.protection_level == ProtectionLevel.normal

    async def test_audit_event_invalid_protection_level(self):
        engine = VerdictEngine()
        event = _audit_event(protection_level="invalid_level")
        result = await engine.evaluate(event)
        assert result.protection_level == ProtectionLevel.normal

    async def test_evidence_chain_populated(self):
        engine = VerdictEngine()
        event = _audit_event(agent_id="a1", operation="write", trust_score=50.0)
        result = await engine.evaluate(event)
        assert result.evidence.actor.agent_id == "a1"
        assert result.evidence.operation.operation == "write"
        assert result.evidence.auth_check.gate_passed is False
        assert result.evidence.response.verdict == VerdictLevel.PASS

    async def test_counter_increment_pass(self):
        engine = VerdictEngine()
        await engine.evaluate(_audit_event(protection_level="public"))
        assert engine._pass_count == 1
        assert engine._eval_count == 1

    async def test_counter_increment_red(self):
        engine = VerdictEngine()
        await engine.evaluate(_audit_event(protection_level="anchor"))
        assert engine._red_count == 1

    async def test_counter_increment_yellow(self):
        engine = VerdictEngine()
        await engine.evaluate(_audit_event(protection_level="normal", trust_score=10.0))
        assert engine._yellow_count == 1

    async def test_trust_threshold_boundary(self):
        engine = VerdictEngine()
        event_at = _audit_event(protection_level="normal", trust_score=_YELLOW_TRUST_THRESHOLD)
        result = await engine.evaluate(event_at)
        assert result.verdict_level == VerdictLevel.PASS

        event_below = _audit_event(protection_level="normal", trust_score=_YELLOW_TRUST_THRESHOLD - 0.1)
        result_below = await engine.evaluate(event_below)
        assert result_below.verdict_level == VerdictLevel.YELLOW

    async def test_violation_threshold_boundary(self):
        engine = VerdictEngine()
        event_at = _audit_event(protection_level="normal", violation_count=_YELLOW_VIOLATION_THRESHOLD)
        result = await engine.evaluate(event_at)
        assert result.verdict_level == VerdictLevel.YELLOW

        event_below = _audit_event(protection_level="normal", violation_count=_YELLOW_VIOLATION_THRESHOLD - 1)
        result_below = await engine.evaluate(event_below)
        assert result_below.verdict_level == VerdictLevel.PASS

    async def test_protection_index_query(self):
        pi = MagicMock()
        pi.query.return_value = ProtectionLevel.anchor
        engine = VerdictEngine(protection_index=pi)
        event = _audit_event(protection_level="normal", target_path="src/zephyr/core.py")
        result = await engine.evaluate(event)
        pi.query.assert_called_once_with("src/zephyr/core.py")
        assert result.verdict_level == VerdictLevel.RED
        assert result.reason == "ai_on_anchor_blocked"

    async def test_protection_index_query_exception_ignored(self):
        pi = MagicMock()
        pi.query.side_effect = RuntimeError("db error")
        engine = VerdictEngine(protection_index=pi)
        event = _audit_event(protection_level="normal")
        result = await engine.evaluate(event)
        assert result.verdict_level == VerdictLevel.PASS

    async def test_protection_index_query_returns_none(self):
        pi = MagicMock()
        pi.query.return_value = None
        engine = VerdictEngine(protection_index=pi)
        event = _audit_event(protection_level="normal")
        result = await engine.evaluate(event)
        assert result.verdict_level == VerdictLevel.PASS

    async def test_protection_index_skipped_when_no_target(self):
        pi = MagicMock()
        engine = VerdictEngine(protection_index=pi)
        event = _audit_event(target_path="")
        await engine.evaluate(event)
        pi.query.assert_not_called()

    async def test_consensus_flag_set(self):
        engine = VerdictEngine()
        event = _audit_event(protection_level="anchor")
        result = await engine.evaluate(event)
        assert result.requires_consensus is True

    async def test_consensus_flag_not_set(self):
        engine = VerdictEngine()
        event = _audit_event(protection_level="normal", trust_score=50.0)
        result = await engine.evaluate(event)
        assert result.requires_consensus is False


@pytest.mark.asyncio
class TestEvaluateAuditEntryV1:
    async def test_audit_entry_v1(self):
        try:
            from zephyr.gov_audit.models import AuditEntryV1
        except ImportError:
            pytest.skip("AuditEntryV1 not available")

        entry = AuditEntryV1(
            agent_id="agent-v1",
            operation="write",
            target_path="src/zephyr/x.py",
            permission_level="anchor",
            indirect_operation=False,
            guard_checks_passed=[],
            trust_score=50.0,
        )
        engine = VerdictEngine()
        result = await engine.evaluate(entry)
        assert result.verdict_level == VerdictLevel.RED
        assert result.reason == "ai_on_anchor_blocked"

    async def test_audit_entry_v1_with_gate(self):
        try:
            from zephyr.gov_audit.models import AuditEntryV1
        except ImportError:
            pytest.skip("AuditEntryV1 not available")

        entry = AuditEntryV1(
            agent_id="agent-v1",
            operation="write",
            target_path="src/zephyr/x.py",
            permission_level="protected",
            indirect_operation=False,
            guard_checks_passed=["gate-001"],
            trust_score=50.0,
        )
        engine = VerdictEngine()
        result = await engine.evaluate(entry)
        assert result.verdict_level == VerdictLevel.PASS
        assert result.reason == "ai_on_protected_gate_passed"

    async def test_audit_entry_v1_cross_module(self):
        try:
            from zephyr.gov_audit.models import AuditEntryV1
        except ImportError:
            pytest.skip("AuditEntryV1 not available")

        entry = AuditEntryV1(
            agent_id="agent-v1",
            operation="write",
            target_path="src/zephyr/x.py",
            permission_level="normal",
            indirect_operation=True,
            guard_checks_passed=[],
            trust_score=50.0,
        )
        engine = VerdictEngine()
        result = await engine.evaluate(entry)
        assert result.verdict_level == VerdictLevel.RED
        assert result.reason == "cross_module_blocked"

    async def test_audit_entry_v1_none_trust_score(self):
        try:
            from zephyr.gov_audit.models import AuditEntryV1
        except ImportError:
            pytest.skip("AuditEntryV1 not available")

        entry = AuditEntryV1(
            agent_id="agent-v1",
            operation="read",
            target_path="src/zephyr/x.py",
            permission_level="normal",
            indirect_operation=False,
            guard_checks_passed=[],
            trust_score=None,
        )
        engine = VerdictEngine()
        result = await engine.evaluate(entry)
        assert result.evidence.actor.trust_score == 50.0

    async def test_audit_entry_v1_invalid_permission_level(self):
        try:
            from zephyr.gov_audit.models import AuditEntryV1
        except ImportError:
            pytest.skip("AuditEntryV1 not available")

        entry = AuditEntryV1(
            agent_id="agent-v1",
            operation="read",
            target_path="src/zephyr/x.py",
            permission_level="bogus",
            indirect_operation=False,
            guard_checks_passed=[],
            trust_score=50.0,
        )
        engine = VerdictEngine()
        result = await engine.evaluate(entry)
        assert result.protection_level == ProtectionLevel.normal


class TestResolveGraduatedLevel:
    def setup_method(self):
        self.engine = VerdictEngine()

    def test_pass_public_l0(self):
        assert (
            self.engine.resolve_graduated_level(VerdictLevel.PASS, ProtectionLevel.public, False, 0)
            == GraduatedLevel.L0
        )

    def test_pass_normal_l1(self):
        assert (
            self.engine.resolve_graduated_level(VerdictLevel.PASS, ProtectionLevel.normal, False, 0)
            == GraduatedLevel.L1
        )

    def test_pass_protected_gate_l2(self):
        assert (
            self.engine.resolve_graduated_level(VerdictLevel.PASS, ProtectionLevel.protected, True, 0)
            == GraduatedLevel.L2
        )

    def test_pass_protected_no_gate_l3(self):
        assert (
            self.engine.resolve_graduated_level(VerdictLevel.PASS, ProtectionLevel.protected, False, 0)
            == GraduatedLevel.L3
        )

    def test_pass_anchor_l3(self):
        assert (
            self.engine.resolve_graduated_level(VerdictLevel.PASS, ProtectionLevel.anchor, False, 0)
            == GraduatedLevel.L3
        )

    def test_yellow_violations_5_l5(self):
        assert (
            self.engine.resolve_graduated_level(VerdictLevel.YELLOW, ProtectionLevel.normal, False, 5)
            == GraduatedLevel.L5
        )

    def test_yellow_violations_3_l4(self):
        assert (
            self.engine.resolve_graduated_level(VerdictLevel.YELLOW, ProtectionLevel.normal, False, 3)
            == GraduatedLevel.L4
        )

    def test_yellow_violations_4_l4(self):
        assert (
            self.engine.resolve_graduated_level(VerdictLevel.YELLOW, ProtectionLevel.normal, False, 4)
            == GraduatedLevel.L4
        )

    def test_yellow_violations_2_l3(self):
        assert (
            self.engine.resolve_graduated_level(VerdictLevel.YELLOW, ProtectionLevel.normal, False, 2)
            == GraduatedLevel.L3
        )

    def test_yellow_zero_violations_l3(self):
        assert (
            self.engine.resolve_graduated_level(VerdictLevel.YELLOW, ProtectionLevel.normal, False, 0)
            == GraduatedLevel.L3
        )

    def test_red_anchor_l6(self):
        assert (
            self.engine.resolve_graduated_level(VerdictLevel.RED, ProtectionLevel.anchor, False, 0) == GraduatedLevel.L6
        )

    def test_red_protected_l5(self):
        assert (
            self.engine.resolve_graduated_level(VerdictLevel.RED, ProtectionLevel.protected, False, 0)
            == GraduatedLevel.L5
        )

    def test_red_normal_l4(self):
        assert (
            self.engine.resolve_graduated_level(VerdictLevel.RED, ProtectionLevel.normal, False, 0) == GraduatedLevel.L4
        )

    def test_red_public_l4(self):
        assert (
            self.engine.resolve_graduated_level(VerdictLevel.RED, ProtectionLevel.public, False, 0) == GraduatedLevel.L4
        )


class TestShouldTriggerConsensus:
    def setup_method(self):
        self.engine = VerdictEngine()

    def test_red_anchor_true(self):
        assert self.engine.should_trigger_consensus(VerdictLevel.RED, ProtectionLevel.anchor) is True

    def test_red_protected_true(self):
        assert self.engine.should_trigger_consensus(VerdictLevel.RED, ProtectionLevel.protected) is True

    def test_red_normal_false(self):
        assert self.engine.should_trigger_consensus(VerdictLevel.RED, ProtectionLevel.normal) is False

    def test_red_public_false(self):
        assert self.engine.should_trigger_consensus(VerdictLevel.RED, ProtectionLevel.public) is False

    def test_yellow_anchor_true(self):
        assert self.engine.should_trigger_consensus(VerdictLevel.YELLOW, ProtectionLevel.anchor) is True

    def test_yellow_protected_false(self):
        assert self.engine.should_trigger_consensus(VerdictLevel.YELLOW, ProtectionLevel.protected) is False

    def test_yellow_normal_false(self):
        assert self.engine.should_trigger_consensus(VerdictLevel.YELLOW, ProtectionLevel.normal) is False

    def test_pass_anchor_false(self):
        assert self.engine.should_trigger_consensus(VerdictLevel.PASS, ProtectionLevel.anchor) is False

    def test_pass_normal_false(self):
        assert self.engine.should_trigger_consensus(VerdictLevel.PASS, ProtectionLevel.normal) is False


@pytest.mark.asyncio
class TestEvaluateBatch:
    async def test_empty_list(self):
        engine = VerdictEngine()
        result = await engine.evaluate_batch([])
        assert result == []

    async def test_multiple_events(self):
        engine = VerdictEngine()
        events = [
            _audit_event(protection_level="public"),
            _audit_event(protection_level="anchor"),
            _audit_event(is_human=True, protection_level="anchor"),
        ]
        results = await engine.evaluate_batch(events)
        assert len(results) == 3
        assert results[0].verdict_level == VerdictLevel.PASS
        assert results[1].verdict_level == VerdictLevel.RED
        assert results[2].verdict_level == VerdictLevel.PASS

    async def test_batch_counters(self):
        engine = VerdictEngine()
        events = [
            _audit_event(protection_level="public"),
            _audit_event(protection_level="anchor"),
            _audit_event(protection_level="normal", trust_score=10.0),
        ]
        await engine.evaluate_batch(events)
        assert engine._eval_count == 3
        assert engine._pass_count == 1
        assert engine._red_count == 1
        assert engine._yellow_count == 1

    async def test_batch_timeout(self):
        engine = VerdictEngine(verdict_timeout_s=0.001)

        async def slow_evaluate(event):
            await asyncio.sleep(10)
            return Verdict()

        original = engine.evaluate
        engine.evaluate = slow_evaluate

        events = [_audit_event(protection_level="normal")]
        results = await engine.evaluate_batch(events)
        assert results[0].verdict_level == VerdictLevel.RED
        assert results[0].reason == "evaluate_timeout"

    async def test_batch_error_handling(self):
        engine = VerdictEngine()

        async def failing_evaluate(event):
            raise RuntimeError("boom")

        engine.evaluate = failing_evaluate

        events = [_audit_event(protection_level="normal")]
        results = await engine.evaluate_batch(events)
        assert results[0].verdict_level == VerdictLevel.RED
        assert "boom" in results[0].reason

    async def test_batch_mixed_success_and_failure(self):
        engine = VerdictEngine()
        call_count = 0

        async def flaky_evaluate(event):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise RuntimeError("flaky")
            return Verdict(verdict_level=VerdictLevel.PASS, reason="ok")

        engine.evaluate = flaky_evaluate

        events = [_audit_event(), _audit_event(), _audit_event()]
        results = await engine.evaluate_batch(events)
        assert len(results) == 3
        assert results[0].verdict_level == VerdictLevel.PASS
        assert results[1].verdict_level == VerdictLevel.RED
        assert results[2].verdict_level == VerdictLevel.PASS


class TestHealthCheck:
    def test_initial_health(self):
        engine = VerdictEngine()
        health = engine.health_check()
        assert health["status"] == "healthy"
        assert health["total_evaluations"] == 0
        assert health["red_count"] == 0
        assert health["yellow_count"] == 0
        assert health["pass_count"] == 0
        assert health["red_rate"] == 0.0
        assert health["has_protection_index"] is False
        assert health["has_gpu_scheduler"] is False
        assert health["verdict_timeout_s"] == 10.0

    def test_health_after_evaluations(self):
        engine = VerdictEngine()
        engine._eval_count = 10
        engine._red_count = 2
        engine._yellow_count = 3
        engine._pass_count = 5
        health = engine.health_check()
        assert health["total_evaluations"] == 10
        assert health["red_rate"] == 0.2

    def test_health_with_dependencies(self):
        pi = MagicMock()
        gs = MagicMock()
        engine = VerdictEngine(protection_index=pi, gpu_scheduler=gs, verdict_timeout_s=30.0)
        health = engine.health_check()
        assert health["has_protection_index"] is True
        assert health["has_gpu_scheduler"] is True
        assert health["verdict_timeout_s"] == 30.0

    def test_red_rate_zero_evaluations(self):
        engine = VerdictEngine()
        health = engine.health_check()
        assert health["red_rate"] == 0.0


class TestApplyDecisionTree:
    def setup_method(self):
        self.engine = VerdictEngine()

    def test_human_pass(self):
        actor = ActorInfo(is_human=True)
        op = OperationInfo(protection_level=ProtectionLevel.anchor)
        level, reason = self.engine._apply_decision_tree(actor, op, False, 0)
        assert level == VerdictLevel.PASS
        assert reason == "human_actor_auto_pass"

    def test_cross_module_red(self):
        actor = ActorInfo(is_human=False)
        op = OperationInfo(is_cross_module=True)
        level, reason = self.engine._apply_decision_tree(actor, op, False, 0)
        assert level == VerdictLevel.RED
        assert reason == "cross_module_blocked"

    def test_anchor_red(self):
        actor = ActorInfo(is_human=False)
        op = OperationInfo(protection_level=ProtectionLevel.anchor)
        level, reason = self.engine._apply_decision_tree(actor, op, False, 0)
        assert level == VerdictLevel.RED
        assert reason == "ai_on_anchor_blocked"

    def test_protected_no_gate_red(self):
        actor = ActorInfo(is_human=False)
        op = OperationInfo(protection_level=ProtectionLevel.protected)
        level, reason = self.engine._apply_decision_tree(actor, op, False, 0)
        assert level == VerdictLevel.RED
        assert reason == "ai_on_protected_no_gate"

    def test_protected_gate_pass(self):
        actor = ActorInfo(is_human=False)
        op = OperationInfo(protection_level=ProtectionLevel.protected)
        level, reason = self.engine._apply_decision_tree(actor, op, True, 0)
        assert level == VerdictLevel.PASS
        assert reason == "ai_on_protected_gate_passed"

    def test_normal_low_trust(self):
        actor = ActorInfo(is_human=False, trust_score=10.0)
        op = OperationInfo(protection_level=ProtectionLevel.normal)
        level, reason = self.engine._apply_decision_tree(actor, op, False, 0)
        assert level == VerdictLevel.YELLOW
        assert reason == "low_trust_score"

    def test_normal_high_violations(self):
        actor = ActorInfo(is_human=False, trust_score=50.0, violation_count=3)
        op = OperationInfo(protection_level=ProtectionLevel.normal)
        level, reason = self.engine._apply_decision_tree(actor, op, False, 3)
        assert level == VerdictLevel.YELLOW
        assert reason == "high_violation_count"

    def test_normal_pass(self):
        actor = ActorInfo(is_human=False, trust_score=50.0, violation_count=0)
        op = OperationInfo(protection_level=ProtectionLevel.normal)
        level, reason = self.engine._apply_decision_tree(actor, op, False, 0)
        assert level == VerdictLevel.PASS
        assert reason == "ai_on_normal"

    def test_public_pass(self):
        actor = ActorInfo(is_human=False)
        op = OperationInfo(protection_level=ProtectionLevel.public)
        level, reason = self.engine._apply_decision_tree(actor, op, False, 0)
        assert level == VerdictLevel.PASS
        assert reason == "ai_on_public"

    def test_cross_module_takes_priority_over_anchor(self):
        actor = ActorInfo(is_human=False)
        op = OperationInfo(is_cross_module=True, protection_level=ProtectionLevel.anchor)
        level, reason = self.engine._apply_decision_tree(actor, op, False, 0)
        assert level == VerdictLevel.RED
        assert reason == "cross_module_blocked"

    def test_human_overrides_cross_module(self):
        actor = ActorInfo(is_human=True)
        op = OperationInfo(is_cross_module=True, protection_level=ProtectionLevel.anchor)
        level, reason = self.engine._apply_decision_tree(actor, op, False, 0)
        assert level == VerdictLevel.PASS
        assert reason == "human_actor_auto_pass"
