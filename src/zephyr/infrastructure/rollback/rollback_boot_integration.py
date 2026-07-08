# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §1.2
# [MODULE] zephyr.infrastructure.rollback.rollback_boot_integration
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES]
# [CONSUMERS] zephyr.trading.boot_hooks
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] register_startup_hook is idempotent; on_startup initializes WAL+Verifier; on_shutdown flushes WAL+cleans temp
# [MODIFY-GUARD] boot_hooks registration name must be "rollback_boot_init"
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] returns BootResult; logs error on failure; never raises during boot
# [TESTS] tests/adversarial/test_rollback_boot_integration.py
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
RollbackBootIntegration — 回滚系统自动启动/关闭集成 (MOD-INF-021 §1.2).

蓝图要求: "回滚必须自动触发，不能等 Owner 确认"
实现: 注册到 boot_hooks 启动序列，系统启动时自动初始化 WAL + Verifier，
系统关闭时自动 flush WAL + 清理临时文件。
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class BootResult:
    """启动/关闭结果。"""
    success: bool
    component: str
    errors: list[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)


class RollbackBootIntegration:
    """回滚系统启动/关闭集成。

    在系统启动时:
    1. 初始化 RollbackWAL（检查完整性 + 恢复未完成的回滚）
    2. 初始化 RollbackVerifier（G0 门禁就绪）
    3. 注册 AutoRollbackTrigger 到事件总线

    在系统关闭时:
    1. Flush WAL（将未写入的日志落盘）
    2. 清理临时文件（.zephyr/rollback_in_flight/）
    3. 释放回滚锁
    """

    HOOK_NAME = "rollback_boot_init"

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._wal = None
        self._verifier = None
        self._initialized = False

    def register_startup_hook(self) -> None:
        """注册到 boot_hooks 启动序列。"""
        try:
            from zephyr.governance.ops_governance.event_hook import hook_registry

            def _on_boot(event: object) -> None:
                self.on_startup()

            hook_registry.register(_on_boot, priority=10, name=self.HOOK_NAME)
            logger.info("RollbackBootIntegration registered to boot_hooks as '%s'", self.HOOK_NAME)
        except Exception as e:
            logger.warning("Failed to register rollback boot hook: %s", e, exc_info=True)

    def on_startup(self) -> BootResult:
        """系统启动时初始化回滚系统。"""
        errors: list[str] = []
        details: dict = {}

        # 1. 初始化 RollbackWAL
        try:
            from zephyr.infrastructure.rollback.rollback_wal import RollbackWAL
            self._wal = RollbackWAL(project_root=self._project_root)
            # 检查 WAL 完整性
            incomplete = self._wal.check_incomplete()
            if incomplete:
                logger.warning("RollbackWAL has incomplete entries from previous session")
            details["wal_initialized"] = True
            details["wal_incomplete_found"] = bool(incomplete)
        except Exception as e:
            errors.append(f"WAL init failed: {e}")
            logger.error("RollbackWAL initialization failed: %s", e, exc_info=True)

        # 2. 初始化 RollbackVerifier
        try:
            from zephyr.infrastructure.rollback.rollback_verifier import RollbackVerifier
            self._verifier = RollbackVerifier(project_root=self._project_root)
            details["verifier_initialized"] = True
        except Exception as e:
            errors.append(f"Verifier init failed: {e}")
            logger.error("RollbackVerifier initialization failed: %s", e, exc_info=True)

        self._initialized = len(errors) == 0

        return BootResult(
            success=self._initialized,
            component="rollback_boot",
            errors=errors,
            details=details,
        )

    def on_shutdown(self) -> BootResult:
        """系统关闭时清理回滚系统。"""
        errors: list[str] = []
        details: dict = {}

        # 1. Flush WAL
        if self._wal is not None:
            try:
                if hasattr(self._wal, "flush"):
                    self._wal.flush()
                details["wal_flushed"] = True
            except Exception as e:
                errors.append(f"WAL flush failed: {e}")
                logger.error("RollbackWAL flush failed: %s", e, exc_info=True)

        # 2. 清理临时文件
        in_flight_dir = self._project_root / ".zephyr" / "rollback_in_flight"
        if in_flight_dir.exists():
            try:
                import shutil
                shutil.rmtree(in_flight_dir, ignore_errors=True)
                details["in_flight_cleaned"] = True
            except Exception as e:
                errors.append(f"In-flight cleanup failed: {e}")

        # 3. 释放回滚锁
        try:
            from zephyr.infrastructure.rollback.rollback_lock import RollbackLock
            lock = RollbackLock(project_root=self._project_root)
            if hasattr(lock, "force_release_all"):
                lock.force_release_all()
            details["lock_released"] = True
        except Exception as e:
            errors.append(f"Lock release failed: {e}")

        return BootResult(
            success=len(errors) == 0,
            component="rollback_shutdown",
            errors=errors,
            details=details,
        )

    @property
    def is_initialized(self) -> bool:
        return self._initialized


# ── EventBusBackpressure 订阅 (DM-2507-D) ──────────────────────────────

_subscribed = False


def subscribe_eventbus() -> None:
    """订阅 EventBusBackpressure 的3个失败事件。

    幂等：重复调用安全。Backpressure 总线不可用时静默跳过。
    供 boot_hooks 统一调用。
    事件: pipeline_failed / mcp_call_failed / kill_switch_triggered
    """
    global _subscribed
    if _subscribed:
        return
    try:
        from zephyr.shared.event_bus import bus

        bus.subscribe("pipeline_failed", _on_pipeline_failed)
        bus.subscribe("mcp_call_failed", _on_mcp_call_failed)
        bus.subscribe("kill_switch_triggered", _on_kill_switch_triggered)
        # P0-3 修复：WAL GC 改为事件触发（rollback_completed 时触发，替代时间触发循环）
        bus.subscribe("rollback_completed", _on_rollback_completed)
        _subscribed = True
        logger.info(
            "RollbackBootIntegration: subscribed to 4 events "
            "(pipeline_failed/mcp_call_failed/kill_switch_triggered/rollback_completed)"
        )
    except Exception as e:
        logger.warning("RollbackBootIntegration: subscribe_eventbus failed: %s", e, exc_info=True)


def _on_pipeline_failed(payload: object) -> None:
    """pipeline_failed 事件：管线失败触发回滚评估。轻量handler。"""
    _trigger_rollback(payload, "pipeline_failed")


def _on_mcp_call_failed(payload: object) -> None:
    """mcp_call_failed 事件：MCP调用失败触发回滚评估。轻量handler。"""
    _trigger_rollback(payload, "mcp_call_failed")


def _on_kill_switch_triggered(payload: object) -> None:
    """kill_switch_triggered 事件：KillSwitch触发回滚。轻量handler。"""
    _trigger_rollback(payload, "kill_switch")


def _on_rollback_completed(payload: object) -> None:
    """rollback_completed 事件：回滚完成后触发 WAL GC（事件驱动，替代时间触发循环）。轻量handler。"""
    try:
        from zephyr.infrastructure.rollback.rollback_scheduler import RollbackScheduler

        scheduler = RollbackScheduler(project_root=Path.cwd())
        scheduler.schedule_wal_gc()
        logger.debug("WAL GC triggered by rollback_completed event")
    except Exception as e:
        logger.warning("WAL GC on rollback_completed failed: %s", e, exc_info=True)


def _trigger_rollback(payload: object, source: str) -> None:
    """触发回滚评估——日志+调用已有公开方法。

    流程: 构造 AutoGuardResult -> AutoRollbackTrigger.classify() ->
          若 should_rollback 且 payload 含 commit_sha -> RollbackExecutor.full_revert()
    """
    try:
        data = payload if isinstance(payload, dict) else {}
        detail = data.get("detail", str(payload))
        logger.warning("Rollback triggered by event '%s': %s", source, detail)

        from zephyr.infrastructure.rollback.auto_rollback_trigger import (
            AutoGuardResult,
            AutoRollbackTrigger,
        )

        result = AutoGuardResult(
            source=source,
            gate_id=data.get("source_function", source),
            task_id=data.get("task_id", ""),
            passed=False,
            error_message=detail,
            error_code=int(data.get("error_code", 1)),
        )
        trigger = AutoRollbackTrigger()
        decision = trigger.classify(result)
        logger.info(
            "Rollback decision for '%s': action=%s should_rollback=%s reason=%s",
            source,
            decision.action,
            decision.should_rollback,
            decision.reason,
        )

        if decision.should_rollback:
            commit_sha = data.get("commit_sha", "")
            if commit_sha:
                from zephyr.infrastructure.rollback.rollback_executor import RollbackExecutor

                executor = RollbackExecutor(project_root=Path.cwd())
                executor.full_revert(commit_sha, audit_session=f"eventbus:{source}")
                logger.warning("RollbackExecutor.full_revert completed for '%s'", source)
            else:
                logger.warning(
                    "Rollback required for '%s' but no commit_sha in payload; "
                    "manual intervention needed",
                    source,
                )
    except Exception as e:
        logger.error("Rollback trigger failed for '%s': %s", source, e, exc_info=True)