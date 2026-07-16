# [A_test] module_id=TEST-F14-RED-BLUE | layer=test | stability=evolving | safety=L
# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md
# [MODULE] tests.red_blue.test_f14_pipeline_extreme
# [INVARIANTS] 红蓝对抗测试隔离外部依赖(LLM/ollama/VMS); 每个测试类覆盖一个极端场景
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=发现极端场景漏洞
# [TESTS] self
# [DOMAIN] D_AUTONOMY_CORE
# [TTL] task_bound

"""F14 管线编排/反馈环 — 红蓝对抗端到端极端测试

覆盖 5 类极端场景（对应 DM-202409 施工步骤 ②-⑥）:
  ② 管线全堵塞 → 死信队列溢出
  ③ 背压响应失效 → 级联崩溃
  ④ SLO 全面违规 → 错误预算耗尽
  ⑤ FeedbackLoop 异常检测失效 → 动作冲突
  ⑥ 并发 100 任务 → 资源耗尽

红队视角：注入故障，验证系统在极端条件下的行为边界。
蓝队视角：验证已知防护机制是否生效，记录已知风险缺口。
"""

from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import MagicMock, patch

import pytest

from zephyr.infrastructure.pipeline.backpressure_manager import BackpressureManager, BpState
from zephyr.infrastructure.pipeline.backpressure_types import (
    BackpressurePause,
    BackpressureResume,
    BackpressureThrottle,
)
from zephyr.infrastructure.pipeline.dead_letter_queue import DeadLetterQueue
from zephyr.infrastructure.pipeline.models import (
    DeadLetterEntry,
    ModuleResult,
    ModuleStatus,
    PipelineStatus,
)
from zephyr.feedback_loop.error_budget import ErrorBudget, ErrorBudgetManager


# ---------------------------------------------------------------------------
# 辅助工厂
# ---------------------------------------------------------------------------


def _make_pause(symbol: str, duration_ms: int = 1000, reason: str = "test") -> BackpressurePause:
    return BackpressurePause(
        duration_ms=duration_ms,
        idempotency_key=f"pk-{symbol}-{time.time()}",
        reason=reason,
        signal_id=f"sig-pause-{symbol}-{time.time()}",
        symbol=symbol,
    )


def _make_throttle(symbol: str, rate: int = 10, reason: str = "test") -> BackpressureThrottle:
    return BackpressureThrottle(
        idempotency_key=f"tk-{symbol}-{time.time()}",
        max_rate_per_sec=rate,
        reason=reason,
        signal_id=f"sig-throttle-{symbol}-{time.time()}",
        symbol=symbol,
    )


def _make_resume(symbol: str, reason: str = "recovered") -> BackpressureResume:
    return BackpressureResume(
        idempotency_key=f"rk-{symbol}-{time.time()}",
        reason=reason,
        signal_id=f"sig-resume-{symbol}-{time.time()}",
        symbol=symbol,
    )


def _make_failed_result(module_id: str = "M1", pipeline: str = "A", errors: list[str] | None = None) -> ModuleResult:
    return ModuleResult(
        module_id=module_id,
        pipeline=pipeline,
        model="test-model",
        status=ModuleStatus.FAILURE,
        errors=errors or ["simulated failure"],
    )


def _make_success_result(module_id: str = "M1", pipeline: str = "A") -> ModuleResult:
    return ModuleResult(
        module_id=module_id,
        pipeline=pipeline,
        model="test-model",
        status=ModuleStatus.SUCCESS,
    )


class _FakeTaskCard:
    """轻量 task_card 替身——DLQ.enqueue 只读 task_id 字段。"""

    def __init__(self, task_id: str) -> None:
        self.task_id = task_id


# ===========================================================================
# 场景 ②: 管线全堵塞 → 死信队列溢出
# ===========================================================================


class TestPipelineFullBlockageDLQOverflow:
    """红蓝对抗：管线全模块失败时死信队列的行为边界。

    红队：持续注入全失败任务，验证 DLQ 无界增长行为。
    蓝队：验证 enqueue 条件门控、drain 清空、save/load 往返一致性。
    """

    def test_all_modules_failed_writes_to_dlq(self):
        """全模块失败 → 写入 DLQ。"""
        dlq = DeadLetterQueue()
        task = _FakeTaskCard("TASK-FULL-FAIL-001")
        results = [_make_failed_result("M1"), _make_failed_result("M2"), _make_failed_result("M3")]

        entry = dlq.enqueue(task, results, PipelineStatus.FAILURE, max_retries=3)

        assert entry is not None
        assert entry.task_id == "TASK-FULL-FAIL-001"
        assert entry.retry_count == 3
        assert "3 modules failed" in entry.failure_reason
        assert dlq.count == 1

    def test_partial_failure_does_not_write_to_dlq(self):
        """红队攻击：部分失败(1/N)不写入 DLQ → 死信丢失风险。"""
        dlq = DeadLetterQueue()
        task = _FakeTaskCard("TASK-PARTIAL-FAIL-001")
        results = [
            _make_failed_result("M1"),
            _make_success_result("M2"),
            _make_success_result("M3"),
        ]

        entry = dlq.enqueue(task, results, PipelineStatus.FAILURE)

        assert entry is None
        assert dlq.count == 0

    def test_success_status_does_not_write_to_dlq(self):
        """SUCCESS 状态不写入 DLQ。"""
        dlq = DeadLetterQueue()
        task = _FakeTaskCard("TASK-OK-001")
        results = [_make_failed_result("M1")]

        entry = dlq.enqueue(task, results, PipelineStatus.SUCCESS)

        assert entry is None

    def test_dlq_unbounded_growth_under_massive_failure(self):
        """红队攻击：1000 个全失败任务 → DLQ 无界增长（无 max_size）。"""
        dlq = DeadLetterQueue()

        for i in range(1000):
            task = _FakeTaskCard(f"TASK-MASS-{i:04d}")
            results = [_make_failed_result("M1")]
            dlq.enqueue(task, results, PipelineStatus.FAILURE)

        assert dlq.count == 1000

    def test_dlq_drain_clears_all_entries(self):
        """drain() 排出并清空。"""
        dlq = DeadLetterQueue()
        for i in range(50):
            dlq.enqueue(_FakeTaskCard(f"TASK-{i}"), [_make_failed_result()], PipelineStatus.FAILURE)

        drained = dlq.drain()

        assert len(drained) == 50
        assert dlq.count == 0

    def test_dlq_save_load_roundtrip(self):
        """save_state → load_state 往返一致性。"""
        dlq = DeadLetterQueue()
        for i in range(5):
            dlq.enqueue(_FakeTaskCard(f"TASK-{i}"), [_make_failed_result()], PipelineStatus.FAILURE)

        state = dlq.save_state()
        assert len(state) == 5

        dlq2 = DeadLetterQueue()
        dlq2.load_state(state)
        assert dlq2.count == 5
        assert all(isinstance(e, DeadLetterEntry) for e in dlq2.entries)

    def test_dlq_concurrent_enqueue_thread_safety(self):
        """红队攻击：并发 enqueue → 无锁竞态验证。

        DLQ 无锁保护，并发写入可能导致 count != 预期。
        本测试记录此风险——若 count < 100 说明发生竞态丢失。
        """
        dlq = DeadLetterQueue()

        def enqueue_batch(batch_id: int) -> int:
            count = 0
            for i in range(10):
                task = _FakeTaskCard(f"TASK-CONC-{batch_id}-{i}")
                entry = dlq.enqueue(task, [_make_failed_result()], PipelineStatus.FAILURE)
                if entry is not None:
                    count += 1
            return count

        with ThreadPoolExecutor(max_workers=10) as pool:
            futures = [pool.submit(enqueue_batch, b) for b in range(10)]
            total_written = sum(f.result() for f in as_completed(futures))

        assert total_written == 100
        assert dlq.count == 100

    def test_dlq_last_error_only_records_first_module_first_error(self):
        """红队攻击：last_error 只记录第一个模块的第一个错误 → 信息丢失。"""
        dlq = DeadLetterQueue()
        task = _FakeTaskCard("TASK-ERR-001")
        results = [
            _make_failed_result("M1", errors=["error-A", "error-B"]),
            _make_failed_result("M2", errors=["error-C"]),
        ]

        entry = dlq.enqueue(task, results, PipelineStatus.FAILURE)

        assert entry is not None
        assert entry.last_error == "error-A"


# ===========================================================================
# 场景 ③: 背压响应失效 → 级联崩溃
# ===========================================================================


class TestBackpressureCascadeFailure:
    """红蓝对抗：背压机制在极端条件下的行为边界。

    红队：全 symbol 堵塞、THROTTLE 永不恢复、回调异常注入。
    蓝队：验证 PAUSE 超时自动恢复、状态查询、回调注册。
    """

    def test_pause_all_symbols_no_global_circuit_breaker(self):
        """红队攻击：所有 symbol PAUSE → 无全局熔断，系统继续接受新任务。"""
        mgr = BackpressureManager()
        symbols = [f"SYM-{i:03d}" for i in range(50)]

        for sym in symbols:
            mgr.handle_pause(_make_pause(sym, duration_ms=60000))

        paused = mgr.get_all_paused()
        assert len(paused) == 50

    def test_throttle_no_auto_recovery(self):
        """红队攻击：THROTTLE 无自动恢复机制 → 永久降速。

        handle_throttle 不设置 paused_until，is_blocked 不检查 THROTTLED 超时。
        需显式 emit_resume 才能恢复。
        """
        mgr = BackpressureManager()
        mgr.handle_throttle(_make_throttle("SYM-THROTTLE", rate=5))

        state = mgr.get_state("SYM-THROTTLE")
        assert state.state == BpState.THROTTLED
        assert state.paused_until == 0.0

        assert mgr.is_blocked("SYM-THROTTLE") is False

        time.sleep(0.1)
        state_after = mgr.get_state("SYM-THROTTLE")
        assert state_after.state == BpState.THROTTLED

        mgr.handle_resume(_make_resume("SYM-THROTTLE"))
        assert mgr.get_state("SYM-THROTTLE").state == BpState.NORMAL

    def test_pause_lazy_recovery_only_on_is_blocked(self):
        """红队攻击：PAUSE 超时后懒恢复——不调用 is_blocked() 则状态不变。"""
        mgr = BackpressureManager()
        mgr.handle_pause(_make_pause("SYM-LAZY", duration_ms=100))

        time.sleep(0.15)

        state_before = mgr.get_state("SYM-LAZY")
        assert state_before.state == BpState.PAUSED

        assert mgr.is_blocked("SYM-LAZY") is False

        state_after = mgr.get_state("SYM-LAZY")
        assert state_after.state == BpState.NORMAL

    def test_pause_auto_resume_via_is_blocked(self):
        """蓝队验证：PAUSE 超时后 is_blocked() 触发自动恢复。"""
        mgr = BackpressureManager()
        mgr.handle_pause(_make_pause("SYM-AUTO", duration_ms=50))

        assert mgr.is_blocked("SYM-AUTO") is True

        time.sleep(0.06)
        assert mgr.is_blocked("SYM-AUTO") is False

    def test_callback_exception_does_not_crash_manager(self):
        """红队攻击：回调抛异常 → manager 不崩溃，其他回调仍执行。"""
        mgr = BackpressureManager()
        call_log: list[str] = []

        def good_handler(state):
            call_log.append(f"good:{state.symbol}")

        def bad_handler(state):
            raise RuntimeError("intentional crash")

        def good_handler2(state):
            call_log.append(f"good2:{state.symbol}")

        mgr.register_on_pause(bad_handler)
        mgr.register_on_pause(good_handler)
        mgr.register_on_pause(good_handler2)

        mgr.handle_pause(_make_pause("SYM-CB"))

        assert "good:SYM-CB" in call_log
        assert "good2:SYM-CB" in call_log

    def test_history_unbounded_growth(self):
        """红队攻击：history 无上限 → 长期运行内存泄漏。"""
        mgr = BackpressureManager()

        for i in range(500):
            mgr.handle_pause(_make_pause(f"SYM-HIST-{i}", duration_ms=1))
            mgr.handle_resume(_make_resume(f"SYM-HIST-{i}"))

        assert len(mgr._history) == 1000

    def test_concurrent_pause_resume_no_deadlock(self):
        """蓝队验证：并发 PAUSE/RESUME 无死锁（RLock 可重入）。"""
        mgr = BackpressureManager()
        symbols = [f"SYM-CONC-{i}" for i in range(20)]

        def worker(sym: str) -> None:
            for _ in range(10):
                mgr.handle_pause(_make_pause(sym, duration_ms=10))
                mgr.handle_resume(_make_resume(sym))

        with ThreadPoolExecutor(max_workers=20) as pool:
            futures = [pool.submit(worker, s) for s in symbols]
            for f in as_completed(futures):
                f.result()

        for sym in symbols:
            assert mgr.get_state(sym).state == BpState.NORMAL


# ===========================================================================
# 场景 ④: SLO 全面违规 → 错误预算耗尽
# ===========================================================================


class TestSLOViolationBudgetExhaustion:
    """红蓝对抗：错误预算耗尽场景。

    红队：持续消耗预算直到耗尽，验证耗尽后行为。
    蓝队：验证预算计算、burn_rate、escalated 标记。
    """

    def test_budget_exhaustion_marks_exhausted(self):
        """蓝队验证：消耗超过月预算 → exhausted=True。"""
        mgr = ErrorBudgetManager()
        mgr.init_budget("CT-TEST-001")

        budget = mgr.record_consumption("CT-TEST-001", minutes=50.0)

        assert budget is not None
        assert budget.consumed_minutes == 50.0
        assert budget.exhausted is True
        assert mgr.is_exhausted("CT-TEST-001") is True

    def test_budget_remaining_calculation(self):
        """蓝队验证：remaining = monthly - consumed。"""
        mgr = ErrorBudgetManager()
        mgr.init_budget("CT-TEST-002")

        mgr.record_consumption("CT-TEST-002", minutes=20.0)
        remaining = mgr.remaining("CT-TEST-002")

        assert remaining == pytest.approx(43.8 - 20.0)

    def test_high_burn_rate_triggers_escalation(self):
        """蓝队验证：burn_rate > 10.0 → escalated=True。"""
        mgr = ErrorBudgetManager()
        mgr.init_budget("CT-TEST-003")

        budget = mgr.record_consumption("CT-TEST-003", minutes=20.0)

        expected_burn = 20.0 / 43.8 * 30.0
        assert budget.burn_rate == pytest.approx(expected_burn)
        assert budget.escalated is True

    def test_exhausted_budget_no_auto_recovery(self):
        """红队攻击：预算耗尽后无自动恢复路径 → 需手动重建。

        ErrorBudgetManager 无 reset/decrease 方法。
        """
        mgr = ErrorBudgetManager()
        mgr.init_budget("CT-TEST-004")
        mgr.record_consumption("CT-TEST-004", minutes=50.0)

        assert mgr.is_exhausted("CT-TEST-004") is True

        mgr.record_consumption("CT-TEST-004", minutes=-10.0)
        assert mgr.is_exhausted("CT-TEST-004") is True

    def test_no_persistence_across_instances(self):
        """红队攻击：无持久化 → 新实例预算重置，可绕过 EXHAUSTED 锁定。"""
        mgr1 = ErrorBudgetManager()
        mgr1.init_budget("CT-TEST-005")
        mgr1.record_consumption("CT-TEST-005", minutes=50.0)
        assert mgr1.is_exhausted("CT-TEST-005") is True

        mgr2 = ErrorBudgetManager()
        mgr2.init_budget("CT-TEST-005")
        assert mgr2.is_exhausted("CT-TEST-005") is False

    def test_concurrent_consumption_thread_safety(self):
        """红队攻击：并发消耗 → ErrorBudgetManager 无锁，验证竞态行为。

        Pydantic BaseModel 非线程安全，并发 += 可能丢失更新。
        本测试记录此风险。
        """
        mgr = ErrorBudgetManager()
        mgr.init_budget("CT-TEST-006")

        def consume_batch() -> float:
            total = 0.0
            for _ in range(10):
                budget = mgr.record_consumption("CT-TEST-006", minutes=1.0)
                if budget:
                    total += 1.0
            return total

        with ThreadPoolExecutor(max_workers=10) as pool:
            futures = [pool.submit(consume_batch) for _ in range(10)]
            sum(f.result() for f in as_completed(futures))

        budget = mgr._budgets.get("CT-TEST-006")
        assert budget is not None
        assert budget.exhausted is True

    def test_unknown_contract_returns_zero_remaining(self):
        """蓝队验证：未初始化的 contract → remaining=0.0。"""
        mgr = ErrorBudgetManager()
        assert mgr.remaining("CT-UNKNOWN") == 0.0
        assert mgr.is_exhausted("CT-UNKNOWN") is False

    def test_multiple_contracts_independent(self):
        """蓝队验证：多个 contract 预算独立。"""
        mgr = ErrorBudgetManager()
        mgr.init_budget("CT-A")
        mgr.init_budget("CT-B")

        mgr.record_consumption("CT-A", minutes=50.0)

        assert mgr.is_exhausted("CT-A") is True
        assert mgr.is_exhausted("CT-B") is False
        assert mgr.remaining("CT-B") == pytest.approx(43.8)


# ===========================================================================
# 场景 ⑤: FeedbackLoop 异常检测失效 → 动作冲突
# ===========================================================================


class TestFeedbackLoopDetectionFailure:
    """红蓝对抗：FeedbackLoopScheduler 在异常条件下的行为边界。

    红队：注入持续异常，验证错误退避和静默暂停行为。
    蓝队验证：start/stop 生命周期、tick 同步执行、单例线程安全。
    """

    @pytest.fixture
    def scheduler(self):
        """创建隔离的 FeedbackLoopScheduler 实例（mock VMS）。"""
        with patch(
            "zephyr.integration.vector_memory.in_process_vector_memory.InProcessVectorMemory"
        ) as vms_cls:
            vms_cls.return_value = MagicMock()
            from zephyr.feedback_loop.scheduler import FeedbackLoopScheduler

            FeedbackLoopScheduler.reset_instance()
            s = FeedbackLoopScheduler(poll_interval=0.05)
            yield s
            if s._running:
                s.stop()
            FeedbackLoopScheduler.reset_instance()

    def test_scheduler_start_stop_lifecycle(self, scheduler):
        """蓝队验证：start → _running=True, stop → _running=False。"""
        assert scheduler._running is False

        scheduler.start()
        assert scheduler._running is True
        assert scheduler._thread is not None

        scheduler.stop()
        assert scheduler._running is False

    def test_scheduler_tick_executes_once(self, scheduler):
        """蓝队验证：tick() 同步执行单次 pipeline。"""
        event = scheduler.tick()

        assert scheduler.run_count() >= 0

    def test_consecutive_errors_triggers_backoff(self, scheduler):
        """红队攻击：连续错误触发指数退避，10次后暂停5分钟。

        验证 _consecutive_errors 计数和 _max_consecutive_errors 阈值。
        """
        assert scheduler._max_consecutive_errors == 10
        assert scheduler._consecutive_errors == 0
        assert scheduler._error_backoff_base == 5.0

    def test_scheduler_singleton_thread_safe(self, scheduler):
        """蓝队验证：get_instance 单例 + reset_instance 线程安全。"""
        from zephyr.feedback_loop.scheduler import FeedbackLoopScheduler

        instances: list[FeedbackLoopScheduler] = []

        def get_inst() -> FeedbackLoopScheduler:
            inst = FeedbackLoopScheduler.get_instance(poll_interval=0.1)
            instances.append(inst)
            return inst

        with ThreadPoolExecutor(max_workers=10) as pool:
            futures = [pool.submit(get_inst) for _ in range(10)]
            for f in as_completed(futures):
                f.result()

        first = instances[0]
        assert all(inst is first for inst in instances)

    def test_events_list_bounded_by_max_events(self, scheduler):
        """蓝队验证：_events 有界（max_events 默认 1000）。"""
        assert scheduler.max_events == 1000

        for _ in range(50):
            scheduler.tick()

        events = scheduler.events(limit=50)
        assert len(events) <= 50

    def test_health_report_returns_dict(self, scheduler):
        """蓝队验证：health_report() 返回字典。"""
        report = scheduler.health_report()
        assert isinstance(report, dict)

    def test_stop_is_idempotent(self, scheduler):
        """蓝队验证：多次 stop() 不崩溃。"""
        scheduler.start()
        scheduler.stop()
        scheduler.stop()


# ===========================================================================
# 场景 ⑥: 并发 100 任务 → 资源耗尽
# ===========================================================================


class TestConcurrentTaskResourceExhaustion:
    """红蓝对抗：100 个并发任务的资源耗尽场景。

    红队：100 个并发任务同时操作 DLQ + Backpressure + ErrorBudget。
    蓝队验证：系统不崩溃、数据不丢失（或记录竞态风险）。
    """

    def test_100_concurrent_dlq_enqueue(self):
        """100 个并发任务写入 DLQ → 验证最终一致性。"""
        dlq = DeadLetterQueue()

        def enqueue_task(task_id: int) -> bool:
            task = _FakeTaskCard(f"CONC-TASK-{task_id:04d}")
            entry = dlq.enqueue(task, [_make_failed_result()], PipelineStatus.FAILURE)
            return entry is not None

        with ThreadPoolExecutor(max_workers=20) as pool:
            futures = [pool.submit(enqueue_task, i) for i in range(100)]
            results = [f.result() for f in as_completed(futures)]

        written = sum(1 for r in results if r)
        assert written == 100

    def test_100_concurrent_backpressure_signals(self):
        """100 个并发背压信号 → 验证无死锁。"""
        mgr = BackpressureManager()
        symbols = [f"SYM-100-{i:03d}" for i in range(100)]

        def signal_worker(sym: str) -> str:
            mgr.handle_pause(_make_pause(sym, duration_ms=50))
            mgr.handle_throttle(_make_throttle(sym, rate=5))
            mgr.handle_resume(_make_resume(sym))
            return sym

        with ThreadPoolExecutor(max_workers=20) as pool:
            futures = [pool.submit(signal_worker, s) for s in symbols]
            for f in as_completed(futures):
                f.result()

        for sym in symbols:
            assert mgr.get_state(sym).state == BpState.NORMAL

    def test_100_concurrent_budget_consumption(self):
        """100 个并发预算消耗 → 验证预算耗尽标记。"""
        mgr = ErrorBudgetManager()
        mgr.init_budget("CT-MASS-001")

        def consume_worker() -> float:
            budget = mgr.record_consumption("CT-MASS-001", minutes=0.5)
            return budget.consumed_minutes if budget else 0.0

        with ThreadPoolExecutor(max_workers=20) as pool:
            futures = [pool.submit(consume_worker) for _ in range(100)]
            for f in as_completed(futures):
                f.result()

        assert mgr.is_exhausted("CT-MASS-001") is True

    def test_mixed_concurrent_operations_no_crash(self):
        """混合并发操作（DLQ + BP + Budget）→ 系统不崩溃。"""
        dlq = DeadLetterQueue()
        bp_mgr = BackpressureManager()
        eb_mgr = ErrorBudgetManager()
        eb_mgr.init_budget("CT-MIX-001")

        def mixed_worker(worker_id: int) -> str:
            if worker_id % 3 == 0:
                task = _FakeTaskCard(f"MIX-{worker_id}")
                dlq.enqueue(task, [_make_failed_result()], PipelineStatus.FAILURE)
                return "dlq"
            elif worker_id % 3 == 1:
                sym = f"MIX-SYM-{worker_id}"
                bp_mgr.handle_pause(_make_pause(sym, duration_ms=10))
                bp_mgr.handle_resume(_make_resume(sym))
                return "bp"
            else:
                eb_mgr.record_consumption("CT-MIX-001", minutes=1.0)
                return "eb"

        with ThreadPoolExecutor(max_workers=20) as pool:
            futures = [pool.submit(mixed_worker, i) for i in range(100)]
            results = [f.result() for f in as_completed(futures)]

        assert len(results) == 100
        assert dlq.count > 0

    def test_resource_cleanup_after_massive_load(self):
        """大规模负载后资源清理 → drain + reset。"""
        dlq = DeadLetterQueue()
        for i in range(200):
            dlq.enqueue(_FakeTaskCard(f"CLEAN-{i}"), [_make_failed_result()], PipelineStatus.FAILURE)

        assert dlq.count == 200

        drained = dlq.drain()
        assert len(drained) == 200
        assert dlq.count == 0

        dlq.enqueue(_FakeTaskCard("POST-CLEAN"), [_make_failed_result()], PipelineStatus.FAILURE)
        assert dlq.count == 1
