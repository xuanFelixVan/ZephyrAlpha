# [A_test] module_id: SRC-TST-0420 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §test
# [MODULE] zephyr.governance.behavioral_admission
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_behavioral_admission.py
# [TTL] task_bound

from __future__ import annotations

import asyncio

import pytest

from zephyr.shared.foundation.errors import SessionError

ve_mod = pytest.importorskip("zephyr.trading.verdict_engine")
ac_mod = pytest.importorskip("zephyr.trading.admission_controller")
pi_mod = pytest.importorskip("zephyr.trading.protection_index")
sl_mod = pytest.importorskip("zephyr.governance.behavioral_admission.session_lifecycle")

VerdictEngine = ve_mod.VerdictEngine
VerdictLevel = ve_mod.VerdictLevel
ProtectionLevel = ve_mod.ProtectionLevel
GraduatedLevel = ve_mod.GraduatedLevel
AuditEvent = ve_mod.AuditEvent
Verdict = ve_mod.Verdict

AdmissionController = ac_mod.AdmissionController
AdmissionDecision = ac_mod.AdmissionDecision
AdmissionResult = ac_mod.AdmissionResult
TokenBucketConfig = ac_mod.TokenBucketConfig

ProtectionIndex = pi_mod.ProtectionIndex

SessionLifecycle = sl_mod.SessionLifecycle
SessionState = sl_mod.SessionState
SessionTransition = sl_mod.SessionTransition
SessionTrustTier = sl_mod.SessionTrustTier


class TestVerdictEngine:
    def test_instantiation(self):
        engine = VerdictEngine()
        assert engine._eval_count == 0
        assert engine._verdict_timeout_s == 10.0

    def test_evaluate_normal_ai(self):
        engine = VerdictEngine()
        event = AuditEvent(
            agent_id="agent-1",
            is_human=False,
            trust_score=60.0,
            violation_count=0,
            protection_level="normal",
            gate_passed=False,
            is_cross_module=False,
        )
        result = asyncio.run(engine.evaluate(event))
        assert isinstance(result, Verdict)
        assert result.verdict_level == VerdictLevel.PASS

    def test_evaluate_human_auto_pass(self):
        engine = VerdictEngine()
        event = AuditEvent(
            agent_id="human-1",
            is_human=True,
            trust_score=50.0,
            protection_level="anchor",
            gate_passed=False,
        )
        result = asyncio.run(engine.evaluate(event))
        assert result.verdict_level == VerdictLevel.PASS
        assert "human" in result.reason.lower()

    def test_evaluate_cross_module_blocked(self):
        engine = VerdictEngine()
        event = AuditEvent(
            agent_id="agent-2",
            is_human=False,
            is_cross_module=True,
            trust_score=80.0,
            protection_level="normal",
        )
        result = asyncio.run(engine.evaluate(event))
        assert result.verdict_level == VerdictLevel.RED

    def test_evaluate_anchor_blocked(self):
        engine = VerdictEngine()
        event = AuditEvent(
            agent_id="agent-3",
            is_human=False,
            protection_level="anchor",
            gate_passed=True,
        )
        result = asyncio.run(engine.evaluate(event))
        assert result.verdict_level == VerdictLevel.RED

    def test_evaluate_protected_no_gate(self):
        engine = VerdictEngine()
        event = AuditEvent(
            agent_id="agent-4",
            is_human=False,
            protection_level="protected",
            gate_passed=False,
        )
        result = asyncio.run(engine.evaluate(event))
        assert result.verdict_level == VerdictLevel.RED

    def test_evaluate_protected_gate_passed(self):
        engine = VerdictEngine()
        event = AuditEvent(
            agent_id="agent-5",
            is_human=False,
            protection_level="protected",
            gate_passed=True,
        )
        result = asyncio.run(engine.evaluate(event))
        assert result.verdict_level == VerdictLevel.PASS

    def test_evaluate_low_trust_yellow(self):
        engine = VerdictEngine()
        event = AuditEvent(
            agent_id="agent-6",
            is_human=False,
            trust_score=20.0,
            violation_count=0,
            protection_level="normal",
        )
        result = asyncio.run(engine.evaluate(event))
        assert result.verdict_level == VerdictLevel.YELLOW

    def test_evaluate_high_violations_yellow(self):
        engine = VerdictEngine()
        event = AuditEvent(
            agent_id="agent-7",
            is_human=False,
            trust_score=60.0,
            violation_count=5,
            protection_level="normal",
        )
        result = asyncio.run(engine.evaluate(event))
        assert result.verdict_level == VerdictLevel.YELLOW

    def test_evaluate_dict_event(self):
        engine = VerdictEngine()
        event = {
            "agent_id": "agent-dict",
            "is_human": False,
            "trust-score": 60.0,
            "violation_count": 0,
            "protection_level": "normal",
            "operation": "write",
            "target_path": "src/foo.py",
            "is_cross_module": False,
            "gate_passed": False,
        }
        result = asyncio.run(engine.evaluate(event))
        assert result.verdict_level == VerdictLevel.PASS

    def test_evaluate_unknown_type_red(self):
        engine = VerdictEngine()
        result = asyncio.run(engine.evaluate(42))
        assert result.verdict_level == VerdictLevel.RED
        assert result.graduated_level == GraduatedLevel.L6

    def test_evaluate_batch(self):
        engine = VerdictEngine()
        events = [
            AuditEvent(agent_id="a1", is_human=True),
            AuditEvent(agent_id="a2", is_human=False, protection_level="anchor"),
        ]
        results = asyncio.run(engine.evaluate_batch(events))
        assert len(results) == 2
        assert results[0].verdict_level == VerdictLevel.PASS
        assert results[1].verdict_level == VerdictLevel.RED

    def test_evaluate_batch_empty(self):
        engine = VerdictEngine()
        results = asyncio.run(engine.evaluate_batch([]))
        assert results == []

    def test_resolve_graduated_level_pass_public(self):
        engine = VerdictEngine()
        level = engine.resolve_graduated_level(VerdictLevel.PASS, ProtectionLevel.public, True, 0)
        assert level == GraduatedLevel.L0

    def test_resolve_graduated_level_pass_normal(self):
        engine = VerdictEngine()
        level = engine.resolve_graduated_level(VerdictLevel.PASS, ProtectionLevel.normal, True, 0)
        assert level == GraduatedLevel.L1

    def test_resolve_graduated_level_red_anchor(self):
        engine = VerdictEngine()
        level = engine.resolve_graduated_level(VerdictLevel.RED, ProtectionLevel.anchor, False, 0)
        assert level == GraduatedLevel.L6

    def test_should_trigger_consensus_red_anchor(self):
        engine = VerdictEngine()
        assert engine.should_trigger_consensus(VerdictLevel.RED, ProtectionLevel.anchor) is True

    def test_should_trigger_consensus_pass_normal(self):
        engine = VerdictEngine()
        assert engine.should_trigger_consensus(VerdictLevel.PASS, ProtectionLevel.normal) is False

    def test_health_check(self):
        engine = VerdictEngine()
        hc = engine.health_check()
        assert hc["status"] == "healthy"
        assert hc["total_evaluations"] == 0


class TestAdmissionController:
    def test_instantiation(self):
        ctrl = AdmissionController()
        assert ctrl is not None

    def test_admit_single(self):
        ctrl = AdmissionController()
        result = ctrl.admit({"event_type": "file_write"})
        assert result.decision == AdmissionDecision.ADMIT

    def test_admit_batch(self):
        ctrl = AdmissionController()
        events = [
            {"event_type": "file_write"},
            {"event_type": "api_call"},
        ]
        results = ctrl.admit_batch(events)
        assert len(results) == 2

    def test_get_metrics(self):
        ctrl = AdmissionController()
        ctrl.admit({"event_type": "file_write"})
        metrics = ctrl.get_metrics()
        assert metrics.total_requests == 1
        assert metrics.admitted == 1

    def test_get_retry_after(self):
        ctrl = AdmissionController()
        retry = ctrl.get_retry_after("file_write")
        assert isinstance(retry, int)

    def test_reset_circuit_breaker(self):
        ctrl = AdmissionController()
        ctrl.reset_circuit_breaker()
        metrics = ctrl.get_metrics()
        assert metrics.circuit_breaker_state == "closed"

    def test_update_rate(self):
        ctrl = AdmissionController()
        ctrl.update_rate(100.0, 200.0)
        result = ctrl.admit({"event_type": "default"})
        assert result.decision == AdmissionDecision.ADMIT

    def test_health_check(self):
        ctrl = AdmissionController()
        hc = ctrl.health_check()
        assert hc["status"] == "healthy"

    def test_unknown_event_type_defaults(self):
        ctrl = AdmissionController()
        result = ctrl.admit({"event_type": "unknown_type"})
        assert result.event_type == "default"

    def test_no_event_type_defaults(self):
        ctrl = AdmissionController()
        result = ctrl.admit({})
        assert result.event_type == "default"

    def test_rate_limiting(self):
        ctrl = AdmissionController(
            global_config=TokenBucketConfig(rate=1.0, burst=2.0),
        )
        results = []
        for _ in range(10):
            results.append(ctrl.admit({"event_type": "default"}))
        rate_limited = [r for r in results if r.decision == AdmissionDecision.RATE_LIMITED]
        assert len(rate_limited) > 0


class TestProtectionIndex:
    def test_instantiation(self):
        idx = ProtectionIndex(project_root=".")
        assert idx is not None

    def test_query_anchor(self):
        idx = ProtectionIndex(project_root=".")
        result = idx.query(".trae/rules/project_rules.md")
        assert result == ProtectionLevel.anchor

    def test_query_protected(self):
        idx = ProtectionIndex(project_root=".")
        result = idx.query("src/zephyr/shared/utils.py")
        assert result == ProtectionLevel.protected

    def test_query_normal(self):
        idx = ProtectionIndex(project_root=".")
        result = idx.query("src/zephyr/pipeline/worker.py")
        assert result == ProtectionLevel.normal

    def test_query_public(self):
        idx = ProtectionIndex(project_root=".")
        result = idx.query("docs/README.md")
        assert result == ProtectionLevel.public

    def test_query_unknown_defaults_normal(self):
        idx = ProtectionIndex(project_root=".")
        result = idx.query("some/random/path.txt")
        assert result == ProtectionLevel.normal

    def test_query_batch(self):
        idx = ProtectionIndex(project_root=".")
        results = idx.query_batch([".trae/rules/project_rules.md", "docs/README.md"])
        assert results[".trae/rules/project_rules.md"] == ProtectionLevel.anchor
        assert results["docs/README.md"] == ProtectionLevel.public

    def test_is_anchor(self):
        idx = ProtectionIndex(project_root=".")
        assert idx.is_anchor(".trae/rules/project_rules.md") is True
        assert idx.is_anchor("docs/README.md") is False

    def test_register_and_unregister(self):
        idx = ProtectionIndex(project_root=".")
        idx.register("custom/path.py", ProtectionLevel.anchor, "test_module", "test reason")
        assert idx.query("custom/path.py") == ProtectionLevel.anchor
        assert idx.unregister("custom/path.py") is True
        assert idx.query("custom/path.py") == ProtectionLevel.normal

    def test_unregister_nonexistent(self):
        idx = ProtectionIndex(project_root=".")
        assert idx.unregister("nonexistent") is False

    def test_get_entry(self):
        idx = ProtectionIndex(project_root=".")
        idx.register("test/entry.py", ProtectionLevel.protected, "mod")
        entry = idx.get_entry("test/entry.py")
        assert entry is not None
        assert entry.level == ProtectionLevel.protected

    def test_rebuild(self):
        idx = ProtectionIndex(project_root=".")
        idx.register("rebuild/test.py", ProtectionLevel.normal, "mod")
        stats = idx.rebuild()
        assert isinstance(stats.total_entries, int)

    def test_get_stats(self):
        idx = ProtectionIndex(project_root=".")
        stats = idx.get_stats()
        assert stats.total_entries >= 0

    def test_verify_integrity(self):
        idx = ProtectionIndex(project_root=".")
        issues = idx.verify_integrity()
        assert isinstance(issues, list)

    def test_health_check(self):
        idx = ProtectionIndex(project_root=".")
        hc = idx.health_check()
        assert "status" in hc
        assert "stats" in hc


class TestSessionLifecycle:
    def test_instantiation(self, tmp_path):
        db_path = str(tmp_path / "test_session.db")
        sl = SessionLifecycle(db_path=db_path)
        assert sl is not None

    def test_register_session(self, tmp_path):
        db_path = str(tmp_path / "test_session.db")
        sl = SessionLifecycle(db_path=db_path)
        record = sl.register_session("sess-001")
        assert record.session_id == "sess-001"
        assert record.state == SessionState.ACTIVE
        assert record.trust_tier == SessionTrustTier.SILVER

    def test_register_session_idempotent(self, tmp_path):
        db_path = str(tmp_path / "test_session.db")
        sl = SessionLifecycle(db_path=db_path)
        r1 = sl.register_session("sess-002")
        r2 = sl.register_session("sess-002")
        assert r1.session_id == r2.session_id

    def test_register_session_max_capacity(self, tmp_path):
        db_path = str(tmp_path / "test_session.db")
        sl = SessionLifecycle(db_path=db_path, max_active_sessions=2)
        sl.register_session("s1")
        sl.register_session("s2")
        with pytest.raises(RuntimeError, match="max_active_sessions"):
            sl.register_session("s3")

    def test_transition(self, tmp_path):
        db_path = str(tmp_path / "test_session.db")
        sl = SessionLifecycle(db_path=db_path)
        sl.register_session("sess-010")
        new_state = sl.transition("sess-010", SessionTransition.IDLE)
        assert new_state == SessionState.IDLE

    def test_transition_invalid(self, tmp_path):
        db_path = str(tmp_path / "test_session.db")
        sl = SessionLifecycle(db_path=db_path)
        sl.register_session("sess-011")
        with pytest.raises(SessionError, match="invalid transition"):
            sl.transition("sess-011", SessionTransition.EXPIRE)

    def test_transition_nonexistent(self, tmp_path):
        db_path = str(tmp_path / "test_session.db")
        sl = SessionLifecycle(db_path=db_path)
        with pytest.raises(SessionError, match="session not found"):
            sl.transition("nonexistent", SessionTransition.IDLE)

    def test_get_state(self, tmp_path):
        db_path = str(tmp_path / "test_session.db")
        sl = SessionLifecycle(db_path=db_path)
        sl.register_session("sess-020")
        record = sl.get_state("sess-020")
        assert record is not None
        assert record.state == SessionState.ACTIVE

    def test_get_state_nonexistent(self, tmp_path):
        db_path = str(tmp_path / "test_session.db")
        sl = SessionLifecycle(db_path=db_path)
        assert sl.get_state("nonexistent") is None

    def test_get_trust_tier(self, tmp_path):
        db_path = str(tmp_path / "test_session.db")
        sl = SessionLifecycle(db_path=db_path)
        sl.register_session("sess-030")
        tier = sl.get_trust_tier("sess-030")
        assert tier == SessionTrustTier.SILVER

    def test_get_trust_tier_nonexistent(self, tmp_path):
        db_path = str(tmp_path / "test_session.db")
        sl = SessionLifecycle(db_path=db_path)
        assert sl.get_trust_tier("nonexistent") == SessionTrustTier.REVOKED

    def test_update_trust_score(self, tmp_path):
        db_path = str(tmp_path / "test_session.db")
        sl = SessionLifecycle(db_path=db_path)
        sl.register_session("sess-040")
        new_score = sl.update_trust_score("sess-040", 30.0)
        assert new_score == 80.0

    def test_update_trust_score_clamped(self, tmp_path):
        db_path = str(tmp_path / "test_session.db")
        sl = SessionLifecycle(db_path=db_path)
        sl.register_session("sess-041")
        new_score = sl.update_trust_score("sess-041", 200.0)
        assert new_score == 100.0

    def test_update_trust_score_nonexistent(self, tmp_path):
        db_path = str(tmp_path / "test_session.db")
        sl = SessionLifecycle(db_path=db_path)
        with pytest.raises(SessionError, match="session not found"):
            sl.update_trust_score("nonexistent", 10.0)

    def test_increment_violation(self, tmp_path):
        db_path = str(tmp_path / "test_session.db")
        sl = SessionLifecycle(db_path=db_path)
        sl.register_session("sess-050")
        count = sl.increment_violation("sess-050")
        assert count == 1
        count = sl.increment_violation("sess-050")
        assert count == 2

    def test_close_session(self, tmp_path):
        db_path = str(tmp_path / "test_session.db")
        sl = SessionLifecycle(db_path=db_path)
        sl.register_session("sess-060")
        result = sl.close_session("sess-060")
        assert result is True
        record = sl.get_state("sess-060")
        assert record.state == SessionState.CLOSED

    def test_close_session_nonexistent(self, tmp_path):
        db_path = str(tmp_path / "test_session.db")
        sl = SessionLifecycle(db_path=db_path)
        result = sl.close_session("nonexistent")
        assert result is False

    def test_run_gc(self, tmp_path):
        db_path = str(tmp_path / "test_session.db")
        sl = SessionLifecycle(db_path=db_path, idle_timeout_s=0)
        sl.register_session("sess-070")
        sl.transition("sess-070", SessionTransition.IDLE)
        expired = sl.run_gc()
        assert expired >= 1

    def test_health_check(self, tmp_path):
        db_path = str(tmp_path / "test_session.db")
        sl = SessionLifecycle(db_path=db_path)
        sl.register_session("sess-080")
        hc = sl.health_check()
        assert hc["status"] == "healthy"
        assert hc["total_sessions"] >= 1
