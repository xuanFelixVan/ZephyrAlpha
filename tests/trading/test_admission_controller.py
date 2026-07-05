# [A_test] module_id: SRC-TST-0273 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_admission_controller
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_admission_controller.py -q
# [TTL] task_bound

from __future__ import annotations

import threading
import time

import pytest

from zephyr.trading.admission_controller import (
    AdmissionController,
    AdmissionDecision,
    AdmissionMetrics,
    AdmissionResult,
    EventTypeBudget,
    PerTypeBucketConfig,
    TokenBucketConfig,
    _CircuitBreaker,
    _TokenBucket,
)
from zephyr.trading.verdict_engine import AuditEvent, VerdictEngine, VerdictLevel


class TestAdmissionDecision:
    def test_enum_values(self):
        assert AdmissionDecision.ADMIT.value == "ADMIT"
        assert AdmissionDecision.RATE_LIMITED.value == "RATE_LIMITED"
        assert AdmissionDecision.CIRCUIT_OPEN.value == "CIRCUIT_OPEN"
        assert AdmissionDecision.REJECTED.value == "REJECTED"

    def test_all_decisions_count(self):
        assert len(AdmissionDecision) == 4


class TestEventTypeBudget:
    def test_enum_values(self):
        assert EventTypeBudget.FILE_WRITE.value == "file_write"
        assert EventTypeBudget.FILE_DELETE.value == "file_delete"
        assert EventTypeBudget.GATE_OPERATION.value == "gate_operation"
        assert EventTypeBudget.RBAC_DECISION.value == "rbac_decision"
        assert EventTypeBudget.API_CALL.value == "api_call"
        assert EventTypeBudget.SESSION.value == "session"
        assert EventTypeBudget.DEFAULT.value == "default"

    def test_all_types_count(self):
        assert len(EventTypeBudget) == 7


class TestTokenBucketConfig:
    def test_defaults(self):
        cfg = TokenBucketConfig()
        assert cfg.rate == 50.0
        assert cfg.burst == 100.0

    def test_custom(self):
        cfg = TokenBucketConfig(rate=10.0, burst=20.0)
        assert cfg.rate == 10.0
        assert cfg.burst == 20.0

    def test_extra_forbidden(self):
        with pytest.raises(Exception):
            TokenBucketConfig(rate=10.0, burst=20.0, unknown=True)


class TestPerTypeBucketConfig:
    def test_defaults(self):
        cfg = PerTypeBucketConfig()
        assert cfg.file_write.rate == 20.0
        assert cfg.file_delete.rate == 5.0
        assert cfg.gate_operation.rate == 30.0
        assert cfg.rbac_decision.rate == 50.0
        assert cfg.api_call.rate == 10.0
        assert cfg.session.rate == 15.0
        assert cfg.default.rate == 25.0


class TestAdmissionResult:
    def test_defaults(self):
        r = AdmissionResult()
        assert r.decision == AdmissionDecision.ADMIT
        assert r.event_type == ""
        assert r.retry_after_ms == 0
        assert r.remaining_tokens == 0.0
        assert r.is_circuit_open is False  # 5.153.4 修复: 字段重命名

    def test_custom(self):
        r = AdmissionResult(
            decision=AdmissionDecision.RATE_LIMITED,
            event_type="file_write",
            retry_after_ms=50,
            remaining_tokens=0.0,
        )
        assert r.decision == AdmissionDecision.RATE_LIMITED
        assert r.event_type == "file_write"
        assert r.retry_after_ms == 50


class TestAdmissionMetrics:
    def test_defaults(self):
        m = AdmissionMetrics()
        assert m.total_requests == 0
        assert m.admitted == 0
        assert m.rate_limited == 0
        assert m.circuit_open_count == 0  # 5.153.4 修复: 字段重命名
        assert m.rejected == 0
        assert m.global_tokens_remaining == 0.0
        assert m.circuit_breaker_state == "closed"
        assert m.last_admit_time == 0.0


class TestTokenBucket:
    def test_initial_tokens_equal_burst(self):
        b = _TokenBucket(rate=10.0, burst=20.0)
        assert b.tokens == 20.0

    def test_consume_success(self):
        b = _TokenBucket(rate=10.0, burst=5.0)
        assert b.consume(1.0) is True
        assert b.tokens < 5.0

    def test_consume_failure_when_empty(self):
        b = _TokenBucket(rate=0.0, burst=2.0)
        assert b.consume(1.0) is True
        assert b.consume(1.0) is True
        assert b.consume(1.0) is False

    def test_refill_over_time(self):
        b = _TokenBucket(rate=1000.0, burst=10.0)
        b.consume(10.0)
        assert b.tokens == 0.0
        time.sleep(0.01)
        assert b.tokens > 0.0

    def test_tokens_capped_at_burst(self):
        b = _TokenBucket(rate=100000.0, burst=5.0)
        time.sleep(0.01)
        assert b.tokens <= 5.0

    def test_update_rate(self):
        b = _TokenBucket(rate=10.0, burst=20.0)
        b.update_rate(5.0)
        assert b.tokens <= 20.0

    def test_update_rate_with_new_burst(self):
        b = _TokenBucket(rate=10.0, burst=20.0)
        b.update_rate(5.0, new_burst=10.0)
        assert b.tokens <= 10.0

    def test_thread_safety(self):
        b = _TokenBucket(rate=10000.0, burst=1000.0)
        results = []

        def consume_loop():
            for _ in range(100):
                results.append(b.consume(1.0))

        threads = [threading.Thread(target=consume_loop) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(results) == 500


class TestCircuitBreaker:
    def test_initial_state_closed(self):
        cb = _CircuitBreaker()
        assert cb.state == "closed"
        assert cb.is_open() is False

    def test_opens_after_threshold(self):
        cb = _CircuitBreaker(failure_threshold=3)
        cb.record_failure()
        cb.record_failure()
        cb.record_failure()
        assert cb.is_open() is True
        assert cb.state == "open"

    def test_retry_after_ms_when_open(self):
        cb = _CircuitBreaker(failure_threshold=1, recovery_timeout_s=10.0)
        cb.record_failure()
        assert cb.retry_after_ms > 0

    def test_retry_after_ms_when_closed(self):
        cb = _CircuitBreaker()
        assert cb.retry_after_ms == 0

    def test_half_open_after_recovery_timeout(self):
        cb = _CircuitBreaker(failure_threshold=1, recovery_timeout_s=0.01)
        cb.record_failure()
        assert cb.is_open() is True
        time.sleep(0.02)
        assert cb.is_open() is False
        assert cb.state == "half_open"

    def test_success_closes_from_half_open(self):
        cb = _CircuitBreaker(failure_threshold=1, recovery_timeout_s=0.01)
        cb.record_failure()
        time.sleep(0.02)
        cb.is_open()
        cb.record_success()
        assert cb.state == "closed"

    def test_reset(self):
        cb = _CircuitBreaker(failure_threshold=1)
        cb.record_failure()
        assert cb.is_open() is True
        cb.reset()
        assert cb.is_open() is False
        assert cb.state == "closed"


class TestAdmissionControllerInit:
    def test_default_init(self):
        ctrl = AdmissionController()
        assert ctrl is not None

    def test_custom_global_config(self):
        ctrl = AdmissionController(global_config=TokenBucketConfig(rate=10.0, burst=20.0))
        assert ctrl is not None

    def test_custom_per_type_config(self):
        ctrl = AdmissionController(per_type_config=PerTypeBucketConfig())
        assert ctrl is not None

    def test_circuit_breaker_disabled(self):
        ctrl = AdmissionController(enable_circuit_breaker=False)
        result = ctrl.admit({"event_type": "file_write"})
        assert result.decision == AdmissionDecision.ADMIT


class TestAdmissionControllerAdmit:
    def test_admit_simple_dict(self):
        ctrl = AdmissionController()
        result = ctrl.admit({"event_type": "file_write"})
        assert result.decision == AdmissionDecision.ADMIT
        assert result.event_type == "file_write"

    def test_admit_unknown_event_type_uses_default(self):
        ctrl = AdmissionController()
        result = ctrl.admit({"event_type": "unknown_type"})
        assert result.decision == AdmissionDecision.ADMIT
        assert result.event_type == "default"

    def test_admit_dict_without_event_type(self):
        ctrl = AdmissionController()
        result = ctrl.admit({})
        assert result.decision == AdmissionDecision.ADMIT
        assert result.event_type == "default"

    def test_admit_object_with_event_type_attr(self):
        ctrl = AdmissionController()

        class FakeEvent:
            event_type = "gate_operation"

        result = ctrl.admit(FakeEvent())
        assert result.decision == AdmissionDecision.ADMIT
        assert result.event_type == "gate_operation"

    def test_admit_plain_object_uses_default(self):
        ctrl = AdmissionController()
        result = ctrl.admit(42)
        assert result.decision == AdmissionDecision.ADMIT
        assert result.event_type == "default"

    def test_admit_rate_limited_when_tokens_exhausted(self):
        ctrl = AdmissionController(
            global_config=TokenBucketConfig(rate=0.0, burst=1.0),
            per_type_config=PerTypeBucketConfig(
                default=TokenBucketConfig(rate=0.0, burst=100.0),
            ),
        )
        ctrl.admit({"event_type": "default"})
        result = ctrl.admit({"event_type": "default"})
        assert result.decision == AdmissionDecision.RATE_LIMITED
        assert result.retry_after_ms > 0

    def test_admit_rate_limited_per_type(self):
        ctrl = AdmissionController(
            global_config=TokenBucketConfig(rate=1000.0, burst=1000.0),
            per_type_config=PerTypeBucketConfig(
                file_write=TokenBucketConfig(rate=0.0, burst=1.0),
            ),
        )
        ctrl.admit({"event_type": "file_write"})
        result = ctrl.admit({"event_type": "file_write"})
        assert result.decision == AdmissionDecision.RATE_LIMITED

    def test_admit_circuit_open(self):
        ctrl = AdmissionController(
            enable_circuit_breaker=True,
            cb_failure_threshold=1,
        )
        ctrl._circuit_breaker.record_failure()
        result = ctrl.admit({"event_type": "file_write"})
        assert result.decision == AdmissionDecision.CIRCUIT_OPEN
        assert result.is_circuit_open is True  # 5.153.4 修复: 字段重命名
        assert result.retry_after_ms > 0

    def test_admit_circuit_breaker_disabled_skips_check(self):
        ctrl = AdmissionController(
            enable_circuit_breaker=False,
            global_config=TokenBucketConfig(rate=1000.0, burst=1000.0),
        )
        ctrl._circuit_breaker.record_failure()
        ctrl._circuit_breaker.record_failure()
        result = ctrl.admit({"event_type": "file_write"})
        assert result.decision == AdmissionDecision.ADMIT


class TestAdmissionControllerAdmitBatch:
    def test_batch_empty(self):
        ctrl = AdmissionController()
        results = ctrl.admit_batch([])
        assert results == []

    def test_batch_multiple(self):
        ctrl = AdmissionController()
        events = [
            {"event_type": "file_write"},
            {"event_type": "gate_operation"},
            {"event_type": "api_call"},
        ]
        results = ctrl.admit_batch(events)
        assert len(results) == 3
        assert all(r.decision == AdmissionDecision.ADMIT for r in results)

    def test_batch_preserves_order(self):
        ctrl = AdmissionController(
            global_config=TokenBucketConfig(rate=0.0, burst=2.0),
            per_type_config=PerTypeBucketConfig(
                default=TokenBucketConfig(rate=0.0, burst=100.0),
            ),
        )
        events = [{"event_type": "default"}] * 4
        results = ctrl.admit_batch(events)
        assert results[0].decision == AdmissionDecision.ADMIT
        assert results[1].decision == AdmissionDecision.ADMIT
        assert results[2].decision == AdmissionDecision.RATE_LIMITED
        assert results[3].decision == AdmissionDecision.RATE_LIMITED


class TestAdmissionControllerMetrics:
    def test_initial_metrics(self):
        ctrl = AdmissionController()
        m = ctrl.get_metrics()
        assert m.total_requests == 0
        assert m.admitted == 0

    def test_metrics_after_admit(self):
        ctrl = AdmissionController()
        ctrl.admit({"event_type": "file_write"})
        m = ctrl.get_metrics()
        assert m.total_requests == 1
        assert m.admitted == 1

    def test_metrics_after_rate_limit(self):
        ctrl = AdmissionController(
            global_config=TokenBucketConfig(rate=0.0, burst=0.0),
        )
        ctrl.admit({"event_type": "default"})
        m = ctrl.get_metrics()
        assert m.total_requests == 1
        assert m.rate_limited == 1

    def test_metrics_after_circuit_open(self):
        ctrl = AdmissionController(cb_failure_threshold=1)
        ctrl._circuit_breaker.record_failure()
        ctrl.admit({"event_type": "default"})
        m = ctrl.get_metrics()
        assert m.circuit_open_count == 1  # 5.153.4 修复: 字段重命名


class TestAdmissionControllerHealthCheck:
    def test_healthy_when_circuit_closed(self):
        ctrl = AdmissionController()
        h = ctrl.health_check()
        assert h["status"] == "healthy"
        assert "metrics" in h
        assert "type_bucket_tokens" in h

    def test_degraded_when_circuit_open(self):
        ctrl = AdmissionController(cb_failure_threshold=1)
        ctrl._circuit_breaker.record_failure()
        h = ctrl.health_check()
        assert h["status"] == "degraded"

    def test_type_bucket_tokens_keys(self):
        ctrl = AdmissionController()
        h = ctrl.health_check()
        expected_keys = {e.value for e in EventTypeBudget}
        assert set(h["type_bucket_tokens"].keys()) == expected_keys


class TestAdmissionControllerRetryAfter:
    def test_retry_after_when_circuit_open(self):
        ctrl = AdmissionController(cb_failure_threshold=1, cb_recovery_timeout_s=30.0)
        ctrl._circuit_breaker.record_failure()
        ms = ctrl.get_retry_after("file_write")
        assert ms > 0

    def test_retry_after_when_circuit_closed(self):
        ctrl = AdmissionController()
        ms = ctrl.get_retry_after("file_write")
        assert ms >= 1


class TestAdmissionControllerResetCircuitBreaker:
    def test_reset(self):
        ctrl = AdmissionController(cb_failure_threshold=1)
        ctrl._circuit_breaker.record_failure()
        assert ctrl._circuit_breaker.is_open() is True
        ctrl.reset_circuit_breaker()
        assert ctrl._circuit_breaker.is_open() is False


class TestAdmissionControllerUpdateRate:
    def test_update_rate(self):
        ctrl = AdmissionController()
        ctrl.update_rate(100.0)
        m = ctrl.get_metrics()
        assert m.global_tokens_remaining <= 100.0

    def test_update_rate_with_burst(self):
        ctrl = AdmissionController()
        ctrl.update_rate(10.0, new_burst=20.0)
        m = ctrl.get_metrics()
        assert m.global_tokens_remaining <= 20.0


class TestAdmissionControllerWithVerdictEngine:
    def test_admission_then_verdict(self):
        ctrl = AdmissionController()
        engine = VerdictEngine()
        event = AuditEvent(
            event_type="file_write",
            agent_id="agent-1",
            operation="write",
            target_path="src/test.py",
            protection_level="normal",
            trust_score=80.0,
        )
        adm = ctrl.admit(event)
        assert adm.decision == AdmissionDecision.ADMIT

        import asyncio

        verdict = asyncio.get_event_loop().run_until_complete(engine.evaluate(event))
        assert verdict.verdict_level == VerdictLevel.PASS

    def test_verdict_red_on_anchor(self):
        ctrl = AdmissionController()
        engine = VerdictEngine()
        event = AuditEvent(
            event_type="file_write",
            agent_id="agent-1",
            operation="write",
            target_path="src/core.py",
            protection_level="anchor",
        )
        adm = ctrl.admit(event)
        assert adm.decision == AdmissionDecision.ADMIT

        import asyncio

        verdict = asyncio.get_event_loop().run_until_complete(engine.evaluate(event))
        assert verdict.verdict_level == VerdictLevel.RED

    def test_verdict_yellow_on_low_trust(self):
        engine = VerdictEngine()
        event = AuditEvent(
            event_type="file_write",
            agent_id="agent-1",
            operation="write",
            target_path="src/test.py",
            protection_level="normal",
            trust_score=10.0,
        )
        import asyncio

        verdict = asyncio.get_event_loop().run_until_complete(engine.evaluate(event))
        assert verdict.verdict_level == VerdictLevel.YELLOW

    def test_verdict_pass_for_human(self):
        engine = VerdictEngine()
        event = AuditEvent(
            event_type="file_write",
            agent_id="human-1",
            operation="write",
            target_path="src/test.py",
            protection_level="normal",
            is_human=True,
        )
        import asyncio

        verdict = asyncio.get_event_loop().run_until_complete(engine.evaluate(event))
        assert verdict.verdict_level == VerdictLevel.PASS
        assert verdict.reason == "human_actor_auto_pass"

    def test_verdict_batch(self):
        engine = VerdictEngine()
        events = [
            AuditEvent(event_type="file_write", agent_id="a1", protection_level="normal", trust_score=80.0),
            AuditEvent(event_type="file_write", agent_id="a2", protection_level="anchor"),
        ]
        import asyncio

        verdicts = asyncio.get_event_loop().run_until_complete(engine.evaluate_batch(events))
        assert len(verdicts) == 2
        assert verdicts[0].verdict_level == VerdictLevel.PASS
        assert verdicts[1].verdict_level == VerdictLevel.RED

    def test_verdict_batch_empty(self):
        engine = VerdictEngine()
        import asyncio

        verdicts = asyncio.get_event_loop().run_until_complete(engine.evaluate_batch([]))
        assert verdicts == []


class TestVerdictEngineHealthCheck:
    def test_healthy(self):
        engine = VerdictEngine()
        h = engine.health_check()
        assert h["status"] == "healthy"
        assert h["total_evaluations"] == 0
        assert h["has_protection_index"] is False
        assert h["has_gpu_scheduler"] is False

    def test_after_evaluation(self):
        engine = VerdictEngine()
        event = AuditEvent(event_type="file_write", agent_id="a1", protection_level="normal", trust_score=80.0)
        import asyncio

        asyncio.get_event_loop().run_until_complete(engine.evaluate(event))
        h = engine.health_check()
        assert h["total_evaluations"] == 1
        assert h["pass_count"] == 1
