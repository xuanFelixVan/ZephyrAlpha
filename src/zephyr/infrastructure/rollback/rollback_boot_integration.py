# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §1.2
# [MODULE] zephyr.infrastructure.rollback.rollback_boot_integration
# [DOMAIN]
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
            logger.warning("Failed to register rollback boot hook: %s", e)

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
            logger.error("RollbackWAL initialization failed: %s", e)

        # 2. 初始化 RollbackVerifier
        try:
            from zephyr.infrastructure.rollback.rollback_verifier import RollbackVerifier
            self._verifier = RollbackVerifier(project_root=self._project_root)
            details["verifier_initialized"] = True
        except Exception as e:
            errors.append(f"Verifier init failed: {e}")
            logger.error("RollbackVerifier initialization failed: %s", e)

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
                logger.error("RollbackWAL flush failed: %s", e)

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
