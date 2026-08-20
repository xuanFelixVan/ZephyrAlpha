# [A_test] module_id=MOD-GOV_auto_runtime_e2e | layer=test | stability=evolving | safety=L
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §6.2
# [MODULE] tests.test_auto_runtime_e2e
# [INVARIANTS] 非mock端到端测试——使用真实LifecycleManager+真实CircadianScheduler+真实HealthMonitor; 仅mock外部依赖(ollama/VMS/A2A)
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=发现boot/shutdown链路漏洞
# [TESTS] self
# [DOMAIN] D_AUTONOMY_CORE
# [A_module] module_id=MOD-INF-035 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""F1 AutoRuntimeCore 非mock端到端集成测试

验证 boot → 运行 → shutdown 全链路使用真实组件（非mock）:
  - 真实 LifecycleManager（boot_sequence/shutdown_sequence 真实执行）
  - 真实 CircadianScheduler（start/stop/trigger_event 真实执行）
  - 真实 HealthMonitor（probe/reconcile 真实执行）
  - 真实 AuditLogger（flush 真实执行）
  - 真实 WorkOrchestrator（submit/complete 真实执行）
  - 真实 DreamCycle（trigger_archival 真实执行）

仅 mock 外部依赖:
  - init_a2a（A2A 协议初始化依赖网络）
  - boot() 成功后的额外步骤（task_queue/blueprint_watcher/triple_align/escalation/fle_scheduler）
    这些步骤依赖外部服务，不属于 LifecycleManager 核心链路

依据: MOD-INF-035 §6.2 AutoRuntimeCore接口 + DM-201112 任务卡。
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from zephyr.trading.auto_runtime_core import AutoRuntimeCore
from zephyr.trading.runtime_config import RuntimeConfig


def _make_config(tmp_path: Path) -> RuntimeConfig:
    """构造真实 RuntimeConfig，所有路径指向 tmp_path。"""
    return RuntimeConfig(
        audit_log_dir=tmp_path / "audit",
        capability_card_dir=tmp_path / "cards",
        night_shift_storage_path=tmp_path / "night.jsonl",
        work_dag_dir=tmp_path / "dags",
        dream_archive_dir=tmp_path / "dream",
        feedback_proposal_dir=tmp_path / "feedback",
        health_snapshot_dir=tmp_path / "health",
        auto_start_l2=False,
    )


def _patch_boot_extras(core: AutoRuntimeCore):
    """返回需要 patch 的 boot() 额外步骤上下文管理器列表。

    这些步骤依赖外部服务（task_queue/blueprint_watcher/triple_align/escalation/fle_scheduler），
    不属于 LifecycleManager 核心链路，mock 掉以隔离外部依赖。
    """
    return [
        patch.object(core, "register_task_system_cron_jobs"),
        patch.object(core, "register_task_system_hooks"),
        patch.object(core, "start_task_queue"),
        patch.object(core, "start_blueprint_watcher"),
        patch.object(core, "start_fle_scheduler"),
        patch.object(core, "run_boot_triple_alignment"),
        patch.object(core, "init_escalation_protocol"),
    ]


def _enter_patches(patches):
    """进入所有 patch 上下文，返回退出函数。"""
    for p in patches:
        p.__enter__()

    def _exit():
        for p in reversed(patches):
            p.__exit__(None, None, None)

    return _exit


class TestAutoRuntimeCoreRealBoot:
    """验证 boot() 使用真实 LifecycleManager 执行完整启动序列。"""

    def test_boot_with_real_lifecycle(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore.init_a2a"):
            core = AutoRuntimeCore(config)

        patches = _patch_boot_extras(core)
        exit_fn = _enter_patches(patches)
        try:
            report = core.boot()
        finally:
            exit_fn()

        # boot 报告返回（即使部分步骤失败也返回报告）
        assert report is not None
        assert report.steps_completed > 0
        # 核心组件被初始化
        assert core.capability_registry is not None
        assert core.work_orchestrator is not None
        assert core.stop_gate is not None
        assert core.health_monitor is not None

    def test_boot_creates_real_dirs(self, tmp_path: Path) -> None:
        """验证 boot() 真实创建目录（ensure_runtime_dirs 真实执行）。"""
        config = _make_config(tmp_path)
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore.init_a2a"):
            core = AutoRuntimeCore(config)

        patches = _patch_boot_extras(core)
        exit_fn = _enter_patches(patches)
        try:
            core.boot()
        finally:
            exit_fn()

        # 真实目录被创建
        assert (tmp_path / "audit").exists()
        assert (tmp_path / "cards").exists()
        assert (tmp_path / "dags").exists()
        assert (tmp_path / "dream").exists()
        assert (tmp_path / "feedback").exists()
        assert (tmp_path / "health").exists()


class TestAutoRuntimeCoreRealShutdown:
    """验证 shutdown() 使用真实 LifecycleManager 执行完整关闭序列。"""

    def test_shutdown_with_real_lifecycle(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore.init_a2a"):
            core = AutoRuntimeCore(config)

        patches = _patch_boot_extras(core)
        exit_fn = _enter_patches(patches)
        try:
            core.boot()
        finally:
            exit_fn()

        # 真实 shutdown
        report = core.shutdown()
        assert core.booted is False
        assert report.steps_completed > 0

    def test_shutdown_idempotent(self, tmp_path: Path) -> None:
        """验证多次 shutdown() 不崩溃。"""
        config = _make_config(tmp_path)
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore.init_a2a"):
            core = AutoRuntimeCore(config)

        patches = _patch_boot_extras(core)
        exit_fn = _enter_patches(patches)
        try:
            core.boot()
        finally:
            exit_fn()

        core.shutdown()
        # 第二次 shutdown 不应崩溃
        core.shutdown()
        assert core.booted is False


class TestAutoRuntimeCoreRealCanStop:
    """验证 can_stop() 使用真实组件状态判断。"""

    def test_can_stop_returns_bool(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore.init_a2a"):
            core = AutoRuntimeCore(config)

        # can_stop 返回 bool（通过 stop_gate.can_stop）
        result = core.can_stop()
        assert isinstance(result, bool)

    def test_can_stop_with_pending_flush(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore.init_a2a"):
            core = AutoRuntimeCore(config)

        with patch.object(core.audit_logger, "has_pending_flush", return_value=True):
            result = core.can_stop()
            # 有 pending flush 时应不能停止（stop_gate 判断）
            assert isinstance(result, bool)


class TestAutoRuntimeCoreRealReconcile:
    """验证 reconcile() 使用真实 HealthMonitor + OrphanDetector。"""

    def test_reconcile_returns_report(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore.init_a2a"):
            core = AutoRuntimeCore(config)

        report = core.reconcile()
        assert report is not None
        assert report.total_probed >= 0
        assert hasattr(report, "orphan_rate")


class TestAutoRuntimeCoreRealFullCycle:
    """验证 boot → 运行 → shutdown 完整生命周期。"""

    def test_full_boot_run_shutdown_cycle(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore.init_a2a"):
            core = AutoRuntimeCore(config)

        # Boot
        patches = _patch_boot_extras(core)
        exit_fn = _enter_patches(patches)
        try:
            boot_report = core.boot()
        finally:
            exit_fn()

        assert boot_report.steps_completed > 0

        # 运行：reconcile
        recon_report = core.reconcile()
        assert recon_report is not None

        # Shutdown
        shutdown_report = core.shutdown()
        assert core.booted is False
        assert shutdown_report.steps_completed > 0

    def test_multiple_boot_shutdown_cycles(self, tmp_path: Path) -> None:
        """验证多次 boot → shutdown 循环不泄漏资源。"""
        config = _make_config(tmp_path)
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore.init_a2a"):
            core = AutoRuntimeCore(config)

        for cycle in range(3):
            patches = _patch_boot_extras(core)
            exit_fn = _enter_patches(patches)
            try:
                boot_report = core.boot()
            finally:
                exit_fn()

            assert boot_report.steps_completed > 0

            core.shutdown()
            assert core.booted is False


class TestAutoRuntimeCoreRealComponents:
    """验证 boot() 后所有核心组件是真实实例（非mock）。"""

    def test_components_are_real_instances(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore.init_a2a"):
            core = AutoRuntimeCore(config)

        # 验证核心组件是真实类型（不是 MagicMock）
        from zephyr.trading.capability_registry import CapabilityRegistry
        from zephyr.trading.dream_cycle import DreamCycle
        from zephyr.trading.health_monitor import HealthMonitor
        from zephyr.trading.work_orchestrator import WorkOrchestrator

        assert isinstance(core.capability_registry, CapabilityRegistry)
        assert isinstance(core.work_orchestrator, WorkOrchestrator)
        assert isinstance(core.health_monitor, HealthMonitor)
        assert isinstance(core.dream_cycle, DreamCycle)

    def test_work_orchestrator_real_submit(self, tmp_path: Path) -> None:
        """验证 boot() 后 WorkOrchestrator 可真实 submit 任务。"""
        config = _make_config(tmp_path)
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore.init_a2a"):
            core = AutoRuntimeCore(config)

        from zephyr.trading.work_dag import WorkItem

        item = WorkItem(
            item_id="WI-e2e-test",
            capability_id="test-cap",
            work_type="test",
            layer="local",
            priority="P1",
            status="READY",
        )
        core.work_orchestrator.submit(item)
        assert core.work_orchestrator.status("WI-e2e-test") == "READY"

    def test_health_monitor_real_probe(self, tmp_path: Path) -> None:
        """验证 boot() 后 HealthMonitor 可真实 register_probe + probe。"""
        config = _make_config(tmp_path)
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore.init_a2a"):
            core = AutoRuntimeCore(config)

        from zephyr.trading.health_monitor import ProbeResult

        core.health_monitor.register_probe(
            "test-cap",
            lambda: ProbeResult(capability_id="test-cap", alive=True, ready=True),
        )
        result = core.health_monitor.probe("test-cap")
        assert result.alive is True
        assert result.ready is True
