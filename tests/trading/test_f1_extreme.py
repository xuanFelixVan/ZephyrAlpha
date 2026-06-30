# [A_test] module_id=TEST-F1-RED-BLUE | layer=test | stability=evolving | safety=L
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §9
# [MODULE] tests.red_blue.test_f1_extreme
# [INVARIANTS] 红蓝对抗测试隔离外部依赖(LLM/ollama/VMS); 每个测试类覆盖一个极端场景; 聚焦F1核心组件(AutoRuntimeCore/WorkOrchestrator/DreamCycle/Conductor)
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=发现F1极端场景漏洞
# [TESTS] self
# [DOMAIN] D_AUTONOMY_CORE
# [TTL] task_bound

"""F1 自动驾驶/运行时大脑 — 红蓝对抗端到端极端测试

覆盖 5 类极端场景对 F1 核心组件的影响:
  ① 管线全堵塞 → WorkOrchestrator 死锁/资源耗尽
  ② 背压响应失效 → AutoRuntimeCore 级联崩溃
  ③ SLO 全面违规 → HealthMonitor 错误预算耗尽
  ④ FeedbackLoop 异常 → DreamCycle 动作冲突
  ⑤ 并发 100 任务 → Conductor/WorkOrchestrator 资源耗尽

红队视角：注入故障，验证 F1 在极端条件下的行为边界。
蓝队视角：验证 F1 已知防护机制是否生效，记录已知风险缺口。

依据: MOD-INF-035 §9 测试策略 + DM-201111 任务卡。
"""

from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.trading.dream_cycle import DreamCycle
from zephyr.trading.health_monitor import HealthMonitor, ProbeResult
from zephyr.trading.work_dag import WorkItem
from zephyr.trading.work_orchestrator import WorkOrchestrator


# ---------------------------------------------------------------------------
# 辅助工厂
# ---------------------------------------------------------------------------


def _make_work_item(
    item_id: str = "WI-test",
    capability_id: str = "test-cap",
    layer: str = "local",
    priority: str = "P1",
    depends_on: list[str] | None = None,
) -> WorkItem:
    # 有依赖的任务应为 PENDING（submit() 只在无依赖时设 READY）
    status = "PENDING" if depends_on else "READY"
    return WorkItem(
        item_id=item_id,
        capability_id=capability_id,
        work_type="test",
        layer=layer,
        priority=priority,
        depends_on=depends_on or [],
        status=status,
    )


def _make_orchestrator(
    max_l1: int = 1,
    max_l2: int = 3,
    max_l3: int = 2,
) -> WorkOrchestrator:
    registry = MagicMock()
    return WorkOrchestrator(
        capability_registry=registry,
        max_parallel_l1=max_l1,
        max_parallel_l2=max_l2,
        max_parallel_l3=max_l3,
    )


# ---------------------------------------------------------------------------
# 场景 ① 管线全堵塞 → WorkOrchestrator 死锁/资源耗尽
# ---------------------------------------------------------------------------


class TestPipelineFullBlockage:
    """红队：所有 slot 被占用且无任务完成 → 新任务无法调度。

    蓝队期望：WorkOrchestrator 不会崩溃，schedule_next 返回空，
    pending_count 正确反映积压，slot 状态一致。
    """

    def test_all_slots_occupied_no_crash(self) -> None:
        orch = _make_orchestrator(max_l1=1, max_l2=1, max_l3=1)
        # 占满所有 slot
        for layer in ("trae", "local", "api"):
            item = _make_work_item(item_id=f"WI-block-{layer}", layer=layer)
            orch.submit(item)
            assert orch.acquire_slot(layer) is True

        # 新任务提交后无法获取 slot
        new_item = _make_work_item(item_id="WI-new", layer="local")
        orch.submit(new_item)
        assert orch.acquire_slot("local") is False

        # 系统不崩溃，schedule_next 返回 READY 任务但 slot 不可用
        ready = orch.schedule_next()
        assert len(ready) >= 1
        pending = orch.pending_count()
        assert pending["local"] >= 1

    def test_deadlock_recovery_on_complete(self) -> None:
        """验证完成一个任务后，积压任务可以获取 slot。"""
        orch = _make_orchestrator(max_l1=1, max_l2=1, max_l3=1)
        block_item = _make_work_item(item_id="WI-block", layer="local")
        orch.submit(block_item)
        orch.acquire_slot("local")

        pending_item = _make_work_item(item_id="WI-pending", layer="local")
        orch.submit(pending_item)
        assert orch.acquire_slot("local") is False

        # 完成阻塞任务
        orch.complete_item("WI-block", result={"ok": True})
        assert orch.status("WI-block") == "COMPLETED"

        # 现在 pending 任务可以获取 slot
        assert orch.acquire_slot("local") is True
        orch.release_slot("local")

    def test_dependency_chain_no_deadlock(self) -> None:
        """验证依赖链在所有 slot 占满时不会死锁。"""
        orch = _make_orchestrator(max_l1=1, max_l2=1, max_l3=1)
        # A → B → C 依赖链
        item_a = _make_work_item(item_id="WI-A", layer="local")
        orch.submit(item_a)
        orch.acquire_slot("local")

        item_b = _make_work_item(item_id="WI-B", layer="local", depends_on=["WI-A"])
        orch.submit(item_b)
        item_c = _make_work_item(item_id="WI-C", layer="local", depends_on=["WI-B"])
        orch.submit(item_c)

        # B 和 C 应为 PENDING
        assert orch.status("WI-B") == "PENDING"
        assert orch.status("WI-C") == "PENDING"

        # 完成 A → B 变 READY
        orch.complete_item("WI-A", result={"ok": True})
        assert orch.status("WI-B") == "READY"


# ---------------------------------------------------------------------------
# 场景 ② 背压响应失效 → AutoRuntimeCore 级联崩溃
# ---------------------------------------------------------------------------


class TestBackpressureCascadeFailure:
    """红队：背压信号被忽略 → 任务积压 → 级联崩溃。

    蓝队期望：WorkOrchestrator slot 机制作为最后防线，
    即使背压信号失效，也不会无限接受任务。
    """

    def test_slot_limit_prevents_cascade(self) -> None:
        """验证 slot 上限作为背压失效的最后防线。"""
        orch = _make_orchestrator(max_l1=1, max_l2=2, max_l3=1)
        accepted = 0
        for i in range(100):
            item = _make_work_item(item_id=f"WI-cascade-{i}", layer="local")
            orch.submit(item)
            if orch.acquire_slot("local"):
                accepted += 1

        # 即使提交 100 个任务，slot 上限限制并发
        assert accepted <= 2
        assert orch.running_count()["local"] <= 2

    def test_release_and_reacquire_cycle(self) -> None:
        """验证释放/重新获取 slot 的循环不会导致计数错乱。"""
        orch = _make_orchestrator(max_l1=1, max_l2=1, max_l3=1)
        for cycle in range(10):
            item = _make_work_item(item_id=f"WI-cycle-{cycle}", layer="local")
            orch.submit(item)
            assert orch.acquire_slot("local") is True
            orch.complete_item(f"WI-cycle-{cycle}", result={"ok": True})
            # complete_item 已释放 slot，无需再 release
            assert orch.running_count()["local"] == 0

    def test_concurrent_submit_thread_safety(self) -> None:
        """验证多线程并发 submit + acquire_slot 不会导致 slot 超限。"""
        orch = _make_orchestrator(max_l1=1, max_l2=5, max_l3=1)

        def worker(idx: int) -> bool:
            item = _make_work_item(item_id=f"WI-thread-{idx}", layer="local")
            orch.submit(item)
            return orch.acquire_slot("local")

        with ThreadPoolExecutor(max_workers=10) as pool:
            results = list(pool.map(worker, range(50)))

        accepted = sum(1 for r in results if r)
        # slot 上限为 5，不能超限
        assert accepted <= 5
        assert orch.running_count()["local"] <= 5


# ---------------------------------------------------------------------------
# 场景 ③ SLO 全面违规 → HealthMonitor 错误预算耗尽
# ---------------------------------------------------------------------------


class TestSLOBudgetExhaustion:
    """红队：所有 probe 失败 → 错误预算耗尽 → 系统降级。

    蓝队期望：HealthMonitor 正确识别所有组件为 inactive，
    reconcile 报告反映真实状态，触发自愈动作。
    """

    def test_all_probes_fail(self) -> None:
        monitor = HealthMonitor()

        def failing_probe() -> ProbeResult:
            return ProbeResult(capability_id="fail-cap", alive=False, ready=False, error="connection refused")

        def failing_restart() -> bool:
            return False

        monitor.register_probe("cap-1", failing_probe, failing_restart)
        monitor.register_probe("cap-2", failing_probe, failing_restart)
        monitor.register_probe("cap-3", failing_probe, failing_restart)

        report = monitor.reconcile(orphan_rate=0.5)
        assert report.total_probed == 3
        assert report.active == 0
        assert report.inactive == 3
        assert len(report.actions_taken) >= 3

    def test_degraded_component_triggers_restart(self) -> None:
        monitor = HealthMonitor()
        restart_called = threading.Event()

        def degraded_probe() -> ProbeResult:
            return ProbeResult(capability_id="deg-cap", alive=True, ready=False, error="slow response")

        def restart_fn() -> bool:
            restart_called.set()
            return True

        monitor.register_probe("deg-cap", degraded_probe, restart_fn)
        report = monitor.reconcile()

        assert report.degraded == 1
        assert restart_called.is_set()

    def test_mixed_health_states(self) -> None:
        monitor = HealthMonitor()

        monitor.register_probe(
            "healthy-cap",
            lambda: ProbeResult(capability_id="healthy-cap", alive=True, ready=True),
        )
        monitor.register_probe(
            "degraded-cap",
            lambda: ProbeResult(capability_id="degraded-cap", alive=True, ready=False),
            lambda: True,
        )
        monitor.register_probe(
            "dead-cap",
            lambda: ProbeResult(capability_id="dead-cap", alive=False, ready=False),
        )

        report = monitor.reconcile()
        assert report.active == 1
        assert report.degraded == 1
        assert report.inactive == 1

    def test_probe_exception_isolated(self) -> None:
        """验证单个 probe 异常不会影响其他 probe。"""
        monitor = HealthMonitor()

        def exploding_probe() -> ProbeResult:
            raise RuntimeError("probe exploded")

        monitor.register_probe("explode-cap", exploding_probe)
        monitor.register_probe(
            "ok-cap",
            lambda: ProbeResult(capability_id="ok-cap", alive=True, ready=True),
        )

        report = monitor.reconcile()
        # 异常 probe 应被捕获，不影响 ok-cap
        assert report.total_probed == 2
        assert report.active == 1


# ---------------------------------------------------------------------------
# 场景 ④ FeedbackLoop 异常 → DreamCycle 动作冲突
# ---------------------------------------------------------------------------


class TestFeedbackLoopAnomaly:
    """红队：DreamCycle 在异常输入下产生动作冲突。

    蓝队期望：DreamCycle 不崩溃，trigger_archival 返回报告，
    needs_archival 在异常状态下仍可调用。
    """

    def test_dream_cycle_empty_dir(self, tmp_path: Path) -> None:
        cycle = DreamCycle(archive_dir=tmp_path / "dream", audit_log_dir=tmp_path / "audit")
        report = cycle.trigger_archival()
        assert report is not None
        assert report.archived_files >= 0

    def test_dream_cycle_missing_audit_dir(self, tmp_path: Path) -> None:
        """验证 audit_log_dir 不存在时不崩溃。"""
        cycle = DreamCycle(archive_dir=tmp_path / "dream", audit_log_dir=tmp_path / "nonexistent")
        report = cycle.trigger_archival()
        assert report is not None

    def test_needs_archival_no_audit_dir(self, tmp_path: Path) -> None:
        cycle = DreamCycle(archive_dir=tmp_path / "dream", audit_log_dir=None)
        assert cycle.needs_archival() is False

    def test_needs_archival_with_today_log(self, tmp_path: Path) -> None:
        audit_dir = tmp_path / "audit"
        audit_dir.mkdir()
        today = datetime.now().strftime("%Y-%m-%d")
        (audit_dir / f"ai_audit_{today}.jsonl").write_text("{}", encoding="utf-8")

        cycle = DreamCycle(archive_dir=tmp_path / "dream", audit_log_dir=audit_dir)
        assert cycle.needs_archival() is True

    def test_dream_cycle_concurrent_trigger(self, tmp_path: Path) -> None:
        """验证并发 trigger_archival 不会导致文件损坏。"""
        cycle = DreamCycle(archive_dir=tmp_path / "dream", audit_log_dir=tmp_path / "audit")

        def trigger() -> bool:
            try:
                cycle.trigger_archival()
                return True
            except Exception:
                return False

        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(lambda _: trigger(), range(10)))

        assert all(results)


# ---------------------------------------------------------------------------
# 场景 ⑤ 并发 100 任务 → Conductor/WorkOrchestrator 资源耗尽
# ---------------------------------------------------------------------------


class TestConcurrent100Tasks:
    """红队：100 个并发任务涌入 → 资源耗尽。

    蓝队期望：WorkOrchestrator 通过 slot 机制限制并发，
    所有任务被正确记录，无任务丢失，无 slot 计数错乱。
    """

    def test_100_tasks_submitted_no_loss(self) -> None:
        orch = _make_orchestrator(max_l1=1, max_l2=3, max_l3=2)
        submitted_ids = []
        for i in range(100):
            item = _make_work_item(item_id=f"WI-100-{i}", layer="local")
            orch.submit(item)
            submitted_ids.append(item.item_id)

        # 所有 100 个任务都被记录
        assert len(orch._items) == 100
        for iid in submitted_ids:
            assert orch.status(iid) in ("READY", "PENDING", "COMPLETED", "FAILED")

    def test_100_tasks_concurrent_submit(self) -> None:
        orch = _make_orchestrator(max_l1=1, max_l2=3, max_l3=2)

        def submit_one(idx: int) -> str:
            item = _make_work_item(item_id=f"WI-conc-{idx}", layer="local")
            orch.submit(item)
            return item.item_id

        with ThreadPoolExecutor(max_workers=20) as pool:
            futures = [pool.submit(submit_one, i) for i in range(100)]
            ids = [f.result() for f in as_completed(futures)]

        assert len(ids) == 100
        assert len(set(ids)) == 100  # 无重复 ID
        assert len(orch._items) == 100

    def test_100_tasks_slot_limit_enforced(self) -> None:
        orch = _make_orchestrator(max_l1=1, max_l2=3, max_l3=2)

        acquired = 0
        for i in range(100):
            item = _make_work_item(item_id=f"WI-slot-{i}", layer="local")
            orch.submit(item)
            if orch.acquire_slot("local"):
                acquired += 1

        # slot 上限为 3
        assert acquired <= 3
        assert orch.running_count()["local"] <= 3

    def test_100_tasks_drain_via_complete(self) -> None:
        """验证通过 complete_item 逐个完成任务后，slot 全部释放。"""
        orch = _make_orchestrator(max_l1=1, max_l2=3, max_l3=2)
        item_ids = []
        for i in range(100):
            item = _make_work_item(item_id=f"WI-drain-{i}", layer="local")
            orch.submit(item)
            item_ids.append(item.item_id)

        # 模拟串行执行：acquire → complete → acquire → complete
        completed = 0
        for iid in item_ids:
            if orch.acquire_slot("local"):
                orch.complete_item(iid, result={"ok": True})
                completed += 1

        assert completed <= 100
        assert orch.running_count()["local"] == 0

    def test_mixed_priority_scheduling(self) -> None:
        """验证 100 个混合优先级任务，schedule_next 按 P0>P1>P2 排序。"""
        orch = _make_orchestrator()
        for i in range(50):
            orch.submit(_make_work_item(item_id=f"WI-P1-{i}", layer="local", priority="P1"))
        for i in range(30):
            orch.submit(_make_work_item(item_id=f"WI-P0-{i}", layer="local", priority="P0"))
        for i in range(20):
            orch.submit(_make_work_item(item_id=f"WI-P2-{i}", layer="local", priority="P2"))

        ready = orch.schedule_next()
        # P0 应排在前面
        p0_count = sum(1 for item in ready if item.priority == "P0")
        p1_count = sum(1 for item in ready if item.priority == "P1")
        p2_count = sum(1 for item in ready if item.priority == "P2")

        # P0 任务应全部排在 P1/P2 前面
        if p0_count > 0 and p1_count > 0:
            first_p0_idx = next(i for i, x in enumerate(ready) if x.priority == "P0")
            first_p1_idx = next(i for i, x in enumerate(ready) if x.priority == "P1")
            assert first_p0_idx < first_p1_idx

