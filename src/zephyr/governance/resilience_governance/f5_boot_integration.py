# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §2
# [MODULE] zephyr.governance.resilience_governance.f5_boot_integration
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS] zephyr.trading.boot_hooks; zephyr.trading.feedback_loop.scheduler
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] register_startup_hook is idempotent; on_startup initializes F5四组件; on_shutdown clears F5 state; run_health_checks never raises
# [MODIFY-GUARD] boot_hooks registration name must be "f5_boot_init"
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] returns BootResult; logs error on failure; never raises during boot; run_health_checks returns dict
# [TESTS] tests/test_f5_auto_startup.py
# [A_module] module_id=MOD-RES_f5_boot_integration | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
F5BootIntegration — F5 自动启动/关闭集成 (MOD-INF-022 §2).

F5 = EscalationProtocol 五件套: EscalationEngine + DelegationEngine + DeadlockDetector
+ Arbitrator + EscalationAPI. 本模块负责将 F5 组件接入系统启动/关闭生命周期:

1. session_startup 钩子: 系统启动时按依赖顺序初始化 F5 四组件
   (DeadlockDetector -> EscalationEngine -> DelegationEngine -> Arbitrator)
2. FLE _periodic_checks() 集成: 巡检死锁/超时锁/升级队列/过期委托
3. boot_hooks 触发接口: register_startup_hook() 注册到 hook_registry

注: CircadianScheduler 定时任务注册（f5_deadlock_scan / f5_escalation_queue_scan）
已于 2026-06-26 裁定随 CircadianScheduler 一并废除；F5 巡检改由 FLE
_periodic_checks() 事件驱动触发。
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zephyr.governance.escalation.escalation_engine import EscalationEngine
    from zephyr.governance.intelligence_governance.delegation_engine import DelegationEngine
    from zephyr.governance.resilience_governance.deadlock_detector import DeadlockDetector
    from zephyr.infrastructure.a2a_protocol.layer3_coordination.arbitrator import Arbitrator

logger = logging.getLogger(__name__)


@dataclass
class BootResult:
    """启动/关闭结果。"""
    success: bool
    component: str
    errors: list[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)


class F5BootIntegration:
    """F5 系统启动/关闭集成。

    在系统启动时:
    1. 初始化 DeadlockDetector (DFS循环检测 + Dijkstra排序 + 超时破解)
    2. 初始化 EscalationEngine (规则匹配 + 熔断器 + 经济守卫)
    3. 初始化 DelegationEngine (注入 DeadlockDetector, MAX_DEPTH=3)
    4. 初始化 Arbitrator (注入 EscalationEngine + DeadlockDetector)

    在系统关闭时:
    1. 清理 DelegationEngine 过期委托
    2. 重置 DeadlockDetector 等待图
    3. 释放 F5 组件引用
    """

    HOOK_NAME = "f5_boot_init"
    DEADLOCK_TIMEOUT_SECONDS = 300.0

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._escalation_engine: EscalationEngine | None = None
        self._delegation_engine: DelegationEngine | None = None
        self._deadlock_detector: DeadlockDetector | None = None
        self._arbitrator: Arbitrator | None = None
        self._initialized = False
        self._last_periodic_result: dict = {}

    def register_startup_hook(self) -> None:
        """注册到 boot_hooks 启动序列 (幂等)。"""
        try:
            from zephyr.governance.ops_governance.event_hook import hook_registry

            def _on_boot(event: object) -> None:
                self.on_startup()

            existing = hook_registry.get_all()
            if any(self.HOOK_NAME in name for name in existing):
                logger.info("F5BootIntegration hook '%s' already registered, skip", self.HOOK_NAME)
                return
            hook_registry.register(_on_boot, priority=15, name=self.HOOK_NAME)
            logger.info("F5BootIntegration registered to boot_hooks as '%s'", self.HOOK_NAME)
        except Exception as e:
            logger.warning("Failed to register F5 boot hook: %s", e, exc_info=True)

    def on_startup(self) -> BootResult:
        """系统启动时初始化 F5 四组件 (按依赖顺序)。"""
        errors: list[str] = []
        details: dict = {}

        # 1. 初始化 DeadlockDetector (无依赖)
        try:
            from zephyr.governance.resilience_governance.deadlock_detector import DeadlockDetector
            self._deadlock_detector = DeadlockDetector()
            details["deadlock_detector_initialized"] = True
            logger.info("F5: DeadlockDetector initialized")
        except Exception as e:
            errors.append(f"DeadlockDetector init failed: {e}")
            logger.error("F5: DeadlockDetector initialization failed: %s", e, exc_info=True)

        # 2. 初始化 EscalationEngine (无依赖, 但内部加载扩展探测器)
        try:
            from zephyr.governance.escalation.escalation_engine import EscalationEngine
            self._escalation_engine = EscalationEngine(name="f5_default", hooks_enabled=True)
            details["escalation_engine_initialized"] = True
            logger.info("F5: EscalationEngine initialized")
        except Exception as e:
            errors.append(f"EscalationEngine init failed: {e}")
            logger.error("F5: EscalationEngine initialization failed: %s", e, exc_info=True)

        # 3. 初始化 DelegationEngine (注入 DeadlockDetector)
        try:
            from zephyr.governance.intelligence_governance.delegation_engine import DelegationEngine
            self._delegation_engine = DelegationEngine(deadlock_detector=self._deadlock_detector)
            details["delegation_engine_initialized"] = True
            details["delegation_max_depth"] = DelegationEngine.MAX_DELEGATION_DEPTH
            logger.info("F5: DelegationEngine initialized (MAX_DEPTH=%d)", DelegationEngine.MAX_DELEGATION_DEPTH)
        except Exception as e:
            errors.append(f"DelegationEngine init failed: {e}")
            logger.error("F5: DelegationEngine initialization failed: %s", e, exc_info=True)

        # 4. 初始化 Arbitrator (注入 EscalationEngine + DeadlockDetector)
        try:
            from zephyr.infrastructure.a2a_protocol.layer3_coordination.arbitrator import Arbitrator
            self._arbitrator = Arbitrator(
                escalation_engine=self._escalation_engine,
                deadlock_detector=self._deadlock_detector,
            )
            details["arbitrator_initialized"] = True
            logger.info("F5: Arbitrator initialized (3-tier: priority->rule->escalation)")
        except Exception as e:
            errors.append(f"Arbitrator init failed: {e}")
            logger.error("F5: Arbitrator initialization failed: %s", e, exc_info=True)

        self._initialized = len(errors) == 0

        return BootResult(
            success=self._initialized,
            component="f5_boot",
            errors=errors,
            details=details,
        )

    def on_shutdown(self) -> BootResult:
        """系统关闭时清理 F5 状态。"""
        errors: list[str] = []
        details: dict = {}

        # 1. 清理 DelegationEngine 过期委托
        if self._delegation_engine is not None:
            try:
                cleaned = self._delegation_engine.cleanup_expired()
                details["delegations_cleaned"] = int(cleaned) if isinstance(cleaned, int) else 0
            except Exception as e:
                errors.append(f"Delegation cleanup failed: {e}")
                logger.error("F5: DelegationEngine cleanup failed: %s", e, exc_info=True)

        # 2. 重置 DeadlockDetector 等待图
        if self._deadlock_detector is not None:
            try:
                self._deadlock_detector._wait_graph.clear()
                self._deadlock_detector._locks.clear()
                self._deadlock_detector._lock_timestamps.clear()
                details["deadlock_graph_reset"] = True
            except Exception as e:
                errors.append(f"Deadlock reset failed: {e}")
                logger.error("F5: DeadlockDetector reset failed: %s", e, exc_info=True)

        # 3. 释放组件引用
        self._escalation_engine = None
        self._delegation_engine = None
        self._deadlock_detector = None
        self._arbitrator = None
        self._initialized = False
        details["references_released"] = True

        return BootResult(
            success=len(errors) == 0,
            component="f5_shutdown",
            errors=errors,
            details=details,
        )

    def run_health_checks(self) -> dict:
        """FLE _periodic_checks() 集成入口 — 巡检死锁/超时锁/升级队列/过期委托。

        本方法永不抛异常 (遵循 FLE _periodic_checks 契约)。
        返回巡检结果字典。
        """
        result: dict = {
            "timestamp": time.time(),
            "deadlock_cycles": [],
            "expired_locks": [],
            "active_escalations": 0,
            "expired_delegations_cleaned": 0,
            "errors": [],
        }

        # 1. 死锁检测 — DFS 循环检测
        if self._deadlock_detector is not None:
            try:
                cycle = self._deadlock_detector.detect_cycle()
                if cycle:
                    result["deadlock_cycles"] = list(cycle)
                    logger.warning("F5 periodic: deadlock cycle detected: %s", cycle)
                    # 自动破解死锁 — 取最低优先级节点
                    try:
                        victim = self._deadlock_detector.preempt_lowest()
                        if victim:
                            logger.info("F5 periodic: preempted lowest-priority node: %s", victim)
                    except Exception as e:
                        result["errors"].append(f"preempt failed: {e}")
            except Exception as e:
                result["errors"].append(f"detect_cycle failed: {e}")

            # 2. 超时锁破解
            try:
                expired = self._deadlock_detector.break_timeout(self.DEADLOCK_TIMEOUT_SECONDS)
                if expired:
                    result["expired_locks"] = list(expired)
                    logger.info("F5 periodic: broke %d expired locks", len(expired))
            except Exception as e:
                result["errors"].append(f"break_timeout failed: {e}")

        # 3. 升级队列巡检
        if self._escalation_engine is not None:
            try:
                active = self._escalation_engine.get_active_count()
                result["active_escalations"] = int(active)
                if active > 0:
                    logger.info("F5 periodic: %d active escalations", active)
            except Exception as e:
                result["errors"].append(f"get_active_count failed: {e}")

        # 4. 过期委托清理
        if self._delegation_engine is not None:
            try:
                cleaned = self._delegation_engine.cleanup_expired()
                result["expired_delegations_cleaned"] = int(cleaned) if isinstance(cleaned, int) else 0
                if cleaned:
                    logger.info("F5 periodic: cleaned %d expired delegations", cleaned)
            except Exception as e:
                result["errors"].append(f"cleanup_expired failed: {e}")

        self._last_periodic_result = result
        return result

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    @property
    def escalation_engine(self) -> EscalationEngine | None:
        return self._escalation_engine

    @property
    def delegation_engine(self) -> DelegationEngine | None:
        return self._delegation_engine

    @property
    def deadlock_detector(self) -> DeadlockDetector | None:
        return self._deadlock_detector

    @property
    def arbitrator(self) -> Arbitrator | None:
        return self._arbitrator

    @property
    def last_periodic_result(self) -> dict[str, Any]:
        return dict(self._last_periodic_result)


def register_f5_boot_hook(project_root: Path | None = None) -> F5BootIntegration:
    """模块级便捷函数: 创建 F5BootIntegration 并注册到 boot_hooks。

    供 zephyr.trading.boot_hooks 调用。
    """
    integration = F5BootIntegration(project_root=project_root)
    integration.register_startup_hook()
    return integration