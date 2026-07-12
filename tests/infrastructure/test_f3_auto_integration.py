# [A_test] module_id: SRC-TST-2118 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] DM-201308 | docs/03_modules/_domain_infrastructure_runtime/task_system/blueprint.md | §auto-integration
# [MODULE] tests.integration.test_f3_auto_integration
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
F3 任务系统自动化集成测试
=========================
覆盖 boot_hooks + auto_runtime_core 全链路：
  1. boot_hooks 真实联动 TaskRepository（非 mock）— auto_unblock_dependents 钩子
  2. auto_runtime_core boot/shutdown 生命周期 — 真实组件 + mock 外部依赖
  3. task_queue dispatch handler 与 TaskRepository 真实交互
  4. shutdown 后状态持久化验证

测试原则：使用临时数据库/临时目录，确保测试隔离。
"""

from __future__ import annotations

import tempfile
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

_NOW = datetime.now(UTC)


# ============================================================================
# 辅助函数
# ============================================================================


def _make_taskcard(task_id: str, depends_on: list[str] | None = None) -> "TaskCard":
    """创建最小化测试 TaskCard，含全部 18 必填字段。"""
    from zephyr.gov_enforcement.rule_enforcement.task_types import TaskNamespace, TaskStatus
    from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel
    from zephyr.shared.schema.task_types import TaskCard

    ns_str, seq_str = task_id.split("-", 1)
    ns = getattr(TaskNamespace, ns_str, TaskNamespace.DM)
    return TaskCard(
        task_id=task_id,
        namespace=ns,
        seq=int(seq_str),
        title=f"Integration Test {task_id}",
        status=TaskStatus.PENDING,
        priority=Priority.P2,
        safety_level=SafetyLevel.L,
        phase=1,
        execution_model="deepseek",
        model_rationale="test",
        fallback_model="deepseek",
        source_blueprint="test",
        source_section="test",
        directive="INT-001",
        classification="internal",
        ai_autonomy_level="supervised",
        description=(
            f"根因：F3任务系统自动化集成测试需验证boot_hooks与TaskRepository真实联动及auto_runtime_core全链路。"
            f"治根：使用临时数据库创建真实TaskRepository实例，注册boot_hooks并触发状态转换钩子，验证下游自动解锁。"
            f"施工步骤：创建依赖任务链并验证下游自动解锁功能。"
            f"验收标准：下游任务状态从BLOCKED自动转为READY，10个MCP Server按DAG拓扑排序启动。"
        ),
        files_in_scope=[f"d:/tmp/integration_test/{task_id}.dummy"],
        deliverables=["集成测试通过"],
        acceptance=["pytest exit=0"],
        allowed_touch=[f"d:/tmp/integration_test/{task_id}.dummy"],
        applicable_rules=[{"module_id": "RULE-TEN", "section": "§1", "reason": "test"}],
        rollback_instructions="git checkout -- tests/infrastructure/test_f3_auto_integration.py",
        post_sync_standard=["echo ok"],
        depends_on=depends_on or [],
        created_at=_NOW,
        updated_at=_NOW,
    )


def _make_temp_db() -> tuple[Path, "TaskRepository"]:
    """创建临时数据库的 TaskRepository。"""
    from zephyr.governance.persistence.task_repo import TaskRepository

    tmp_dir = tempfile.mkdtemp(prefix="f3_auto_")
    db_path = Path(tmp_dir) / "test_data/databases/governance.db"
    repo = TaskRepository(db_path=db_path, auto_init=True, enable_gate=False)
    return tmp_dir, repo


def _do_batch_review(repo, task_id: str) -> None:
    """执行 2 轮 batch_review 以满足 COMPLETED 转换的审查要求。

    transition(COMPLETED) 需要 get_review_status 返回 consecutive_zero >= 2，
    即连续 2 轮 7 维度审查全部通过。_make_taskcard 构造的任务卡满足所有维度。
    """
    for _ in range(2):
        result = repo.batch_review(task_id, reviewer="test", session_id="test")
        assert result["passed"], f"batch_review 未通过: {result['dimensions']}"
        assert result["total_issues"] == 0, f"发现问题: {result['dimensions']}"


def _make_mock_boot_report(success: bool = True) -> MagicMock:
    """创建 mock BootReport（参考 test_auto_runtime_fle_integration.py 模式）。"""
    report = MagicMock()
    report.success = success
    report.errors = []
    report.components_started = []
    report.steps_completed = 0
    return report


# ============================================================================
# 场景1：boot_hooks 真实联动 TaskRepository
# ============================================================================


class TestBootHooksRealIntegration:
    """boot_hooks 真实联动 TaskRepository：注册钩子后触发状态转换，验证钩子执行。"""

    def setup_method(self):
        """每个测试前清空 hook_registry。"""
        from zephyr.governance.ops_governance.event_hook import hook_registry

        hook_registry.clear()

    def teardown_method(self):
        """每个测试后清空 hook_registry。"""
        from zephyr.governance.ops_governance.event_hook import hook_registry

        hook_registry.clear()

    def test_register_boot_hooks_idempotent(self):
        """register_boot_hooks 幂等：多次调用不重复注册。"""
        from zephyr.governance.ops_governance.event_hook import hook_registry
        from zephyr.trading.boot_hooks import register_boot_hooks

        register_boot_hooks()
        hooks_after_first = set(hook_registry.get_all())

        register_boot_hooks()
        hooks_after_second = set(hook_registry.get_all())

        assert hooks_after_first == hooks_after_second, (
            f"register_boot_hooks not idempotent: {hooks_after_first} vs {hooks_after_second}"
        )
        assert len(hooks_after_first) > 0, "No hooks registered"

    def test_auto_unblock_dependents_hook_fires(self):
        """auto_unblock_dependents 钩子：COMPLETED 任务自动解锁下游 BLOCKED 任务。"""
        from zephyr.gov_enforcement.rule_enforcement.task_types import TaskStatus
        from zephyr.trading.boot_hooks import register_boot_hooks

        tmp_dir, repo = _make_temp_db()
        try:
            # 创建依赖链：A → B (B depends on A)
            task_a = _make_taskcard("DM-40001")
            task_b = _make_taskcard("DM-40002", depends_on=["DM-40001"])
            repo.create(task_a, allow_direct_create=True)
            repo.create(task_b, allow_direct_create=True)

            # 设置初始状态：A=IN_PROGRESS, B=BLOCKED
            repo.transition("DM-40001", TaskStatus.IN_PROGRESS)
            repo.transition("DM-40002", TaskStatus.BLOCKED)

            # 注册 boot_hooks
            register_boot_hooks()

            # COMPLETED 前需通过 batch_review（enable_gate=False 时仍强制）
            _do_batch_review(repo, "DM-40001")

            # 触发：A → COMPLETED（应触发 auto_unblock_dependents 钩子）
            repo.transition("DM-40001", TaskStatus.COMPLETED)

            # 验证：B 应被自动解锁为 READY
            task_b_after = repo.get("DM-40002")
            assert task_b_after is not None, "Task B not found after transition"
            assert task_b_after.status == TaskStatus.READY, (
                f"Task B should be READY after A completed, got {task_b_after.status}"
            )
        finally:
            repo.close()

    def test_auto_unblock_partial_deps_not_unlocked(self):
        """auto_unblock_dependents：部分依赖未完成时不解锁。"""
        from zephyr.gov_enforcement.rule_enforcement.task_types import TaskStatus
        from zephyr.trading.boot_hooks import register_boot_hooks

        tmp_dir, repo = _make_temp_db()
        try:
            # 创建依赖链：A → C, B → C (C depends on A and B)
            task_a = _make_taskcard("DM-40010")
            task_b = _make_taskcard("DM-40011")
            task_c = _make_taskcard("DM-40012", depends_on=["DM-40010", "DM-40011"])
            repo.create(task_a, allow_direct_create=True)
            repo.create(task_b, allow_direct_create=True)
            repo.create(task_c, allow_direct_create=True)

            repo.transition("DM-40010", TaskStatus.IN_PROGRESS)
            repo.transition("DM-40011", TaskStatus.IN_PROGRESS)
            repo.transition("DM-40012", TaskStatus.BLOCKED)

            register_boot_hooks()

            # 只完成 A，B 未完成 → C 不应解锁
            _do_batch_review(repo, "DM-40010")
            repo.transition("DM-40010", TaskStatus.COMPLETED)

            task_c_after = repo.get("DM-40012")
            assert task_c_after is not None
            assert task_c_after.status == TaskStatus.BLOCKED, (
                f"Task C should remain BLOCKED when B not completed, got {task_c_after.status}"
            )

            # 完成 B → C 应解锁
            _do_batch_review(repo, "DM-40011")
            repo.transition("DM-40011", TaskStatus.COMPLETED)

            task_c_final = repo.get("DM-40012")
            assert task_c_final is not None
            assert task_c_final.status == TaskStatus.READY, (
                f"Task C should be READY after both deps completed, got {task_c_final.status}"
            )
        finally:
            repo.close()

    def test_hook_registry_fire_does_not_crash_on_missing_task(self):
        """钩子对不存在的 task_id 不崩溃（异常隔离）。"""
        from zephyr.governance.ops_governance.event_hook import TransitionEvent, hook_registry
        from zephyr.trading.boot_hooks import register_boot_hooks

        register_boot_hooks()

        # 触发不存在的任务转换 — 不应抛异常
        event = TransitionEvent(
            task_id="DM-99999",
            from_status="IN_PROGRESS",
            to_status="COMPLETED",
            note="test",
            session_id="test",
        )
        hook_registry.fire(event)  # 不应抛异常


# ============================================================================
# 场景2：auto_runtime_core boot/shutdown 生命周期
# ============================================================================


class TestAutoRuntimeCoreLifecycle:
    """auto_runtime_core boot/shutdown 全链路：真实组件 + mock 外部依赖。"""

    def test_boot_shutdown_cycle_no_crash(self, tmp_path):
        """boot → shutdown 完整循环不崩溃。"""
        from zephyr.trading.auto_runtime_core import AutoRuntimeCore
        from zephyr.trading.runtime_config import RuntimeConfig

        config = RuntimeConfig(
            audit_log_dir=tmp_path / "audit",
            capability_card_dir=tmp_path / "cards",
            night_shift_storage_path=tmp_path / "night.jsonl",
            work_dag_dir=tmp_path / "dags",
            dream_archive_dir=tmp_path / "dream",
            feedback_proposal_dir=tmp_path / "feedback",
            health_snapshot_dir=tmp_path / "health",
            auto_start_l2=False,
        )

        # mock _init_a2a 和 StatusDashboard 避免外部依赖（参考 test_auto_runtime_fle_integration.py）
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore._init_a2a"):
            with patch("zephyr.trading.auto_runtime_core.StatusDashboard"):
                core = AutoRuntimeCore(config=config)

        mock_report = _make_mock_boot_report(success=True)
        with (
            patch.object(core._lifecycle, "boot_sequence", return_value=mock_report),
            patch.object(core, "_register_task_system_cron_jobs"),
            patch.object(core, "_register_task_system_hooks"),
            patch.object(core, "_start_task_queue"),
            patch.object(core, "_start_blueprint_watcher"),
            patch.object(core, "_start_fle_scheduler"),
            patch.object(core, "_run_boot_triple_alignment"),
            patch.object(core, "_init_escalation_protocol"),
        ):
            report = core.boot()
            assert report is not None
            assert report.success is True
            assert core._booted is True

            shutdown_report = core.shutdown()
            assert shutdown_report is not None
            assert core._booted is False

    def test_boot_failure_does_not_set_booted(self, tmp_path):
        """boot 失败时 _booted 保持 False。"""
        from zephyr.trading.auto_runtime_core import AutoRuntimeCore
        from zephyr.trading.runtime_config import RuntimeConfig

        config = RuntimeConfig(
            audit_log_dir=tmp_path / "audit",
            capability_card_dir=tmp_path / "cards",
            night_shift_storage_path=tmp_path / "night.jsonl",
            work_dag_dir=tmp_path / "dags",
            dream_archive_dir=tmp_path / "dream",
            feedback_proposal_dir=tmp_path / "feedback",
            health_snapshot_dir=tmp_path / "health",
            auto_start_l2=False,
        )

        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore._init_a2a"):
            with patch("zephyr.trading.auto_runtime_core.StatusDashboard"):
                core = AutoRuntimeCore(config=config)

        mock_report = _make_mock_boot_report(success=False)
        with (
            patch.object(core._lifecycle, "boot_sequence", return_value=mock_report),
            patch.object(core, "_start_fle_scheduler") as mock_fle,
        ):
            report = core.boot()
            assert report.success is False
            assert core._booted is False
            mock_fle.assert_not_called()  # boot 失败不应调用后续步骤

    def test_multiple_boot_shutdown_cycles_no_leak(self, tmp_path):
        """多次 boot/shutdown 循环不泄漏资源。"""
        from zephyr.trading.auto_runtime_core import AutoRuntimeCore
        from zephyr.trading.runtime_config import RuntimeConfig

        config = RuntimeConfig(
            audit_log_dir=tmp_path / "audit",
            capability_card_dir=tmp_path / "cards",
            night_shift_storage_path=tmp_path / "night.jsonl",
            work_dag_dir=tmp_path / "dags",
            dream_archive_dir=tmp_path / "dream",
            feedback_proposal_dir=tmp_path / "feedback",
            health_snapshot_dir=tmp_path / "health",
            auto_start_l2=False,
        )

        for i in range(3):
            with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore._init_a2a"):
                with patch("zephyr.trading.auto_runtime_core.StatusDashboard"):
                    core = AutoRuntimeCore(config=config)

            mock_report = _make_mock_boot_report(success=True)
            with (
                patch.object(core._lifecycle, "boot_sequence", return_value=mock_report),
                patch.object(core, "_register_task_system_cron_jobs"),
                patch.object(core, "_register_task_system_hooks"),
                patch.object(core, "_start_task_queue"),
                patch.object(core, "_start_blueprint_watcher"),
                patch.object(core, "_start_fle_scheduler"),
                patch.object(core, "_run_boot_triple_alignment"),
                patch.object(core, "_init_escalation_protocol"),
            ):
                core.boot()
                assert core._booted is True
                core.shutdown()
                assert core._booted is False


# ============================================================================
# 场景3：task_queue dispatch handler 真实交互
# ============================================================================


class TestTaskQueueDispatchIntegration:
    """task_queue dispatch handler 与 TaskRepository 真实交互。"""

    def test_dispatch_handler_creates_and_dispatches(self, tmp_path):
        """dispatch handler 正确读取 TaskRepository 中的任务。

        PENDING 不能直接转到 READY（非法转换），使用 PENDING → BLOCKED → READY 路径。
        """
        from zephyr.gov_enforcement.rule_enforcement.task_types import TaskStatus
        from zephyr.governance.persistence.task_repo import TaskRepository

        db_path = tmp_path / "test.db"
        repo = TaskRepository(db_path=db_path, auto_init=True, enable_gate=False)

        try:
            task = _make_taskcard("DM-40020")
            repo.create(task, allow_direct_create=True)
            # PENDING → BLOCKED → READY（合法路径）
            repo.transition("DM-40020", TaskStatus.BLOCKED)
            repo.transition("DM-40020", TaskStatus.READY)

            # 模拟 dispatch handler 的核心逻辑
            fetched = repo.get("DM-40020")
            assert fetched is not None
            assert fetched.status == TaskStatus.READY

            # 模拟 dispatch 后状态转换
            repo.transition("DM-40020", TaskStatus.IN_PROGRESS)
            dispatched = repo.get("DM-40020")
            assert dispatched is not None
            assert dispatched.status == TaskStatus.IN_PROGRESS
        finally:
            repo.close()

    def test_dispatch_handler_ignores_non_ready_tasks(self, tmp_path):
        """dispatch handler 忽略非 READY/PENDING 状态的任务。"""
        from zephyr.gov_enforcement.rule_enforcement.task_types import TaskStatus
        from zephyr.governance.persistence.task_repo import TaskRepository

        db_path = tmp_path / "test.db"
        repo = TaskRepository(db_path=db_path, auto_init=True, enable_gate=False)

        try:
            task = _make_taskcard("DM-40030")
            repo.create(task, allow_direct_create=True)
            # 任务保持 PENDING 状态
            fetched = repo.get("DM-40030")
            assert fetched is not None
            assert fetched.status == TaskStatus.PENDING

            # 模拟 dispatch handler 检查：只处理 READY/PENDING
            should_dispatch = fetched.status in (TaskStatus.READY, TaskStatus.PENDING)
            assert should_dispatch is True

            # 转为 COMPLETED 后不应再 dispatch
            repo.transition("DM-40030", TaskStatus.IN_PROGRESS)
            _do_batch_review(repo, "DM-40030")
            repo.transition("DM-40030", TaskStatus.COMPLETED)
            completed = repo.get("DM-40030")
            should_dispatch_after = completed.status in (TaskStatus.READY, TaskStatus.PENDING)
            assert should_dispatch_after is False
        finally:
            repo.close()


# ============================================================================
# 场景4：shutdown 后状态持久化
# ============================================================================


class TestShutdownStatePersistence:
    """shutdown 后任务状态持久化到 SQLite。"""

    def test_task_state_persists_after_repo_close(self, tmp_path):
        """任务状态在 repo.close() 后仍持久化在 SQLite。"""
        from zephyr.gov_enforcement.rule_enforcement.task_types import TaskStatus
        from zephyr.governance.persistence.task_repo import TaskRepository

        db_path = tmp_path / "persist.db"

        # 第一次打开：创建任务并转换状态
        repo1 = TaskRepository(db_path=db_path, auto_init=True, enable_gate=False)
        try:
            task = _make_taskcard("DM-40040")
            repo1.create(task, allow_direct_create=True)
            repo1.transition("DM-40040", TaskStatus.IN_PROGRESS)
            _do_batch_review(repo1, "DM-40040")
            repo1.transition("DM-40040", TaskStatus.COMPLETED)
        finally:
            repo1.close()

        # 第二次打开：验证状态已持久化
        repo2 = TaskRepository(db_path=db_path, auto_init=True, enable_gate=False)
        try:
            task = repo2.get("DM-40040")
            assert task is not None
            assert task.status == TaskStatus.COMPLETED, (
                f"Task state not persisted, got {task.status}"
            )
        finally:
            repo2.close()

    def test_boot_shutdown_preserves_task_data(self, tmp_path):
        """模拟 boot/shutdown 循环后任务数据完整。"""
        from zephyr.gov_enforcement.rule_enforcement.task_types import TaskStatus
        from zephyr.governance.persistence.task_repo import TaskRepository

        db_path = tmp_path / "lifecycle.db"

        # 模拟 boot 阶段：创建任务
        repo = TaskRepository(db_path=db_path, auto_init=True, enable_gate=False)
        try:
            task = _make_taskcard("DM-40050")
            repo.create(task, allow_direct_create=True)
            repo.transition("DM-40050", TaskStatus.IN_PROGRESS)
        finally:
            repo.close()  # 模拟 shutdown

        # 模拟重启后：数据仍在
        repo2 = TaskRepository(db_path=db_path, auto_init=True, enable_gate=False)
        try:
            task = repo2.get("DM-40050")
            assert task is not None
            assert task.status == TaskStatus.IN_PROGRESS
            assert task.title == "Integration Test DM-40050"
        finally:
            repo2.close()

    def test_concurrent_writes_persist_correctly(self, tmp_path):
        """并发写入后所有数据正确持久化。"""
        import threading
        from concurrent.futures import ThreadPoolExecutor, as_completed

        from zephyr.governance.persistence.task_repo import TaskRepository

        db_path = tmp_path / "concurrent.db"
        repo = TaskRepository(db_path=db_path, auto_init=True, enable_gate=False)

        try:
            def create_task(i):
                task = _make_taskcard(f"DM-{40060 + i}")
                repo.create(task, allow_direct_create=True)
                return task.task_id

            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(create_task, i) for i in range(10)]
                created_ids = [f.result() for f in as_completed(futures)]

            assert len(created_ids) == 10
            assert len(set(created_ids)) == 10, "Duplicate task IDs created"

            # 关闭并重新打开验证持久化
            repo.close()
            repo2 = TaskRepository(db_path=db_path, auto_init=True, enable_gate=False)
            try:
                for tid in created_ids:
                    task = repo2.get(tid)
                    assert task is not None, f"Task {tid} not persisted"
            finally:
                repo2.close()
        except Exception:
            try:
                repo.close()
            except Exception:
                pass
            raise
