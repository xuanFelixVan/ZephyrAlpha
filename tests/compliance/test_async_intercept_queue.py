# [BLUEPRINT] MOD-L10-001 | docs/03_modules/_domain_compliance/blueprint.md | §test
# [MODULE] tests.compliance.test_async_intercept_queue
# [DOMAIN] D_COMPLIANCE
# [DEPENDENCIES] zephyr.compliance.async_intercept_queue
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_async_intercept_queue.py
# [A_test] module_id: MOD-L10-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""MOD-L10-001 单元测试: AsyncInterceptQueue — 合规异步拦截队列 (GAP-L10-001)。

覆盖: 提交/处理/结果查询闭环, 内容缓存去重, 队列满 fail-closed,
网关异常转 BLOCK 裁决, pre_filter 短路, drain/worker 有界循环纪律。
"""

from __future__ import annotations

import threading
from datetime import UTC, datetime

import pytest

pytest.importorskip(
    "zephyr.compliance.async_intercept_queue",
    reason="async_intercept_queue not importable",
)

from zephyr.compliance.async_intercept_queue import (  # noqa: E402
    AsyncInterceptQueue,
    InterceptQueueFullError,
)
from zephyr.governance.security_governance.security_gateway_base import (  # noqa: E402
    AuditAction,
    AuditDecision,
)


class _StubGateway:
    """SecurityGateway 协议桩（按调用计数 + 可配置风险/异常）。"""

    def __init__(self, risks: list[str] | None = None, exc: Exception | None = None):
        self._risks = risks or []
        self._exc = exc
        self.scan_calls = 0
        self.decide_contexts: list[dict] = []

    def pre_filter(self, content: str, source: str) -> bool:
        return True

    def security_scan(self, content: str) -> list[str]:
        self.scan_calls += 1
        if self._exc is not None:
            raise self._exc
        return list(self._risks)

    def decide(self, risks: list[str], context: dict) -> AuditDecision:
        self.decide_contexts.append(context)
        action = AuditAction.BLOCK if risks else AuditAction.ALLOW
        return AuditDecision(
            decision_id=f"d-{len(self.decide_contexts)}",
            action=action,
            rule_id="stub-rule",
            reason=";".join(risks) or "clean",
            timestamp=datetime.now(UTC),
            metadata={},
        )


class _NoFilterGateway(_StubGateway):
    def pre_filter(self, content: str, source: str) -> bool:
        return False


# ── 基本闭环 ─────────────────────────────────────────────────────────


class TestSubmitProcessLoop:
    def test_submit_returns_ticket_and_process_allow(self):
        queue = AsyncInterceptQueue(gateway=_StubGateway())
        ticket = queue.submit("content-a", source="agent-x")
        assert ticket
        result = queue.process_next()
        assert result is not None
        assert result.ticket_id == ticket
        assert result.decision.action == AuditAction.ALLOW
        assert result.from_cache is False
        assert queue.get_result(ticket) is result

    def test_block_decision_passthrough(self):
        queue = AsyncInterceptQueue(gateway=_StubGateway(risks=["leak"]));
        ticket = queue.submit("bad", source="agent-x")
        result = queue.process_next()
        assert result is not None
        assert result.decision.action == AuditAction.BLOCK

    def test_process_next_empty_returns_none(self):
        queue = AsyncInterceptQueue(gateway=_StubGateway())
        assert queue.process_next() is None

    def test_get_result_unknown_ticket_none(self):
        queue = AsyncInterceptQueue(gateway=_StubGateway())
        assert queue.get_result("no-such-ticket") is None

    def test_pending_count(self):
        queue = AsyncInterceptQueue(gateway=_StubGateway())
        queue.submit("a", source="s")
        queue.submit("b", source="s")
        assert queue.pending_count == 2
        queue.process_next()
        assert queue.pending_count == 1


# ── 缓存 ─────────────────────────────────────────────────────────────


class TestContentCache:
    def test_repeat_content_served_from_cache(self):
        gateway = _StubGateway()
        queue = AsyncInterceptQueue(gateway=gateway)
        t1 = queue.submit("same-content", source="s")
        queue.process_next()
        t2 = queue.submit("same-content", source="s")
        result = queue.process_next()
        assert result is not None
        assert result.ticket_id == t2
        assert result.from_cache is True
        assert gateway.scan_calls == 1  # 第二次未再扫描
        assert t1 != t2

    def test_different_source_not_cached_together(self):
        gateway = _StubGateway()
        queue = AsyncInterceptQueue(gateway=gateway)
        queue.submit("c", source="s1")
        queue.submit("c", source="s2")
        queue.drain(max_items=10)
        assert gateway.scan_calls == 2

    def test_cache_bounded(self):
        gateway = _StubGateway()
        queue = AsyncInterceptQueue(gateway=gateway, cache_size=4)
        for i in range(10):
            queue.submit(f"content-{i}", source="s")
        queue.drain(max_items=10)
        # 缓存上限 4, 早期内容被淘汰 → 重扫第 0 条
        queue.submit("content-0", source="s")
        result = queue.process_next()
        assert result is not None
        assert result.from_cache is False


# ── Fail-Closed ──────────────────────────────────────────────────────


class TestFailClosed:
    def test_queue_full_raises(self):
        queue = AsyncInterceptQueue(gateway=_StubGateway(), max_queue_size=2)
        queue.submit("a", source="s")
        queue.submit("b", source="s")
        with pytest.raises(InterceptQueueFullError):
            queue.submit("c", source="s")

    def test_gateway_exception_produces_block(self):
        queue = AsyncInterceptQueue(gateway=_StubGateway(exc=RuntimeError("scanner down")))
        ticket = queue.submit("x", source="s")
        result = queue.process_next()
        assert result is not None
        assert result.decision.action == AuditAction.BLOCK
        assert result.error is not None
        assert queue.get_result(ticket) is result

    def test_pre_filter_false_skips_scan(self):
        gateway = _NoFilterGateway()
        queue = AsyncInterceptQueue(gateway=gateway)
        queue.submit("x", source="s")
        result = queue.process_next()
        assert result is not None
        assert gateway.scan_calls == 0
        assert gateway.decide_contexts  # decide 仍被调用（空风险）
        assert result.decision.action == AuditAction.ALLOW


# ── 有界循环纪律 ─────────────────────────────────────────────────────


class TestBoundedLoops:
    def test_drain_respects_max_items(self):
        queue = AsyncInterceptQueue(gateway=_StubGateway())
        for i in range(5):
            queue.submit(f"c-{i}", source="s")
        results = queue.drain(max_items=2)
        assert len(results) == 2
        assert queue.pending_count == 3

    def test_run_worker_bounded_and_stoppable(self):
        queue = AsyncInterceptQueue(gateway=_StubGateway())
        for i in range(3):
            queue.submit(f"c-{i}", source="s")
        stop = threading.Event()
        processed = queue.run_worker(stop, poll_interval_s=0.01, max_iterations=50)
        assert processed == 3
        assert queue.pending_count == 0

    def test_run_worker_stops_on_event(self):
        queue = AsyncInterceptQueue(gateway=_StubGateway())
        for i in range(3):
            queue.submit(f"c-{i}", source="s")
        stop = threading.Event()
        stop.set()
        processed = queue.run_worker(stop, poll_interval_s=0.01, max_iterations=50)
        assert processed == 0
        assert queue.pending_count == 3

    def test_run_worker_max_iterations_cap(self):
        # 队列持续有任务时 max_iterations 封顶（禁无界循环）
        queue = AsyncInterceptQueue(gateway=_StubGateway())
        for i in range(10):
            queue.submit(f"c-{i}", source="s")
        processed = queue.run_worker(
            threading.Event(), poll_interval_s=0.01, max_iterations=4,
        )
        assert processed == 4
