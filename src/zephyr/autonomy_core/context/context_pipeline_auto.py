# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §automation
# [MODULE] zephyr.autonomy_core.context.context_pipeline_auto
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES]
# [CONSUMERS] zephyr.trading.boot_hooks; tests/test_context_pipeline_auto
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] auto_start is idempotent; KillSwitch fuse ON blocks auto_run; timeout triggers auto_shutdown; auto_shutdown is idempotent
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError when fuse ON blocks auto_run; pipeline errors recorded to KillSwitch
# [TESTS] tests/context/test_context_pipeline_auto.py
# [A_module] module_id=MOD-CONTEXT_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: threading.Timer是auto_run的一次性超时保护(超时触发auto_shutdown),非周期触发(与timeout_guard同类)

"""context_pipeline_auto.py — ContextPipeline 三层自动化机制

三层自动化：
1. 自动启动 (auto_start): 系统启动时初始化，注册 EventBus 订阅
2. 事件启动 (event-driven): TASK_STARTED/TASK_COMPLETED/TASK_FAILED 事件自动触发
3. 自动关闭 (auto_shutdown): KillSwitch 熔断 + 超时保护 + 资源清理
"""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from typing import Any

from zephyr.autonomy_core.context.context_pipeline import (
    ContextFourStageResult,
    run_context_four_stage,
)
from zephyr.infrastructure.capacity_assurance.kill_switch import KillSwitch
from zephyr.shared.event_bus import DomainEvent, EventBus, EventType

logger = logging.getLogger(__name__)

__all__ = ["ContextPipelineAuto"]


class ContextPipelineAuto:
    """ContextPipeline 自动化包装器——三层自动化机制。

    自动启动 -> 事件启动 -> 自动运行 -> 自动关闭
    """

    def __init__(
        self,
        kill_switch: KillSwitch | None = None,
        timeout_seconds: int = 300,
        auto_kill_threshold: int = 5,
    ) -> None:
        self._kill_switch = kill_switch or KillSwitch(threshold=auto_kill_threshold)
        self._timeout_seconds = timeout_seconds
        self._started = False
        self._event_subscribed = False
        self._cleanup_callbacks: list[Callable[[], None]] = []
        self._lock = threading.Lock()

    @property
    def kill_switch(self) -> KillSwitch:
        return self._kill_switch

    @property
    def is_started(self) -> bool:
        return self._started

    @property
    def fuse_on(self) -> bool:
        return self._kill_switch._fuse_on

    def auto_start(self) -> None:
        """自动启动：初始化 ContextPipeline，注册 EventBus 订阅。幂等。"""
        with self._lock:
            if self._started:
                logger.debug("ContextPipelineAuto already started, skip")
                return
            self._started = True
            self._register_event_subscriptions()
            logger.info(
                "ContextPipelineAuto started (timeout=%ds, kill_threshold=%d)",
                self._timeout_seconds,
                self._kill_switch._threshold,
            )

    def _register_event_subscriptions(self) -> None:
        """事件启动：订阅 EventBus 事件。"""
        if self._event_subscribed:
            return
        try:
            bus = EventBus.get_instance()
            bus.subscribe(EventType.TASK_STARTED, self._on_task_started)
            bus.subscribe(EventType.TASK_COMPLETED, self._on_task_completed)
            bus.subscribe(EventType.TASK_FAILED, self._on_task_failed)
            self._event_subscribed = True
            logger.info("ContextPipelineAuto event subscriptions registered")
        except Exception as exc:
            logger.warning("ContextPipelineAuto event subscription failed: %s", exc, exc_info=True)

    def _on_task_started(self, event: DomainEvent) -> None:
        """事件启动：TASK_STARTED 时自动准备上下文。"""
        if self.fuse_on:
            logger.warning(
                "ContextPipelineAuto: fuse ON, skip TASK_STARTED for %s", event.task_id
            )
            return
        logger.debug("ContextPipelineAuto: TASK_STARTED for %s", event.task_id)

    def _on_task_completed(self, event: DomainEvent) -> None:
        """事件启动：TASK_COMPLETED 时自动清理上下文。"""
        if self.fuse_on:
            return
        logger.debug("ContextPipelineAuto: TASK_COMPLETED for %s", event.task_id)

    def _on_task_failed(self, event: DomainEvent) -> None:
        """事件启动：TASK_FAILED 时记录错误到 KillSwitch。"""
        self._kill_switch.record_error(f"task_failed: {event.task_id}")
        if self.fuse_on:
            logger.error(
                "ContextPipelineAuto: KillSwitch fuse ON after TASK_FAILED for %s",
                event.task_id,
            )
            self.auto_shutdown(reason=f"fuse triggered by task failure: {event.task_id}")

    def auto_run(
        self,
        manifest: list[dict[str, str]],
        **kwargs: Any,
    ) -> ContextFourStageResult:
        """自动运行：执行四阶段，带超时和 KillSwitch 保护。"""
        if self.fuse_on:
            raise RuntimeError("KillSwitch fuse is ON, pipeline blocked")

        if not self._started:
            self.auto_start()

        timer = threading.Timer(
            self._timeout_seconds,
            self._on_timeout,
        )
        timer.daemon = True
        timer.start()

        try:
            result = run_context_four_stage(manifest, **kwargs)
            if not result.g3_passed:
                self._kill_switch.record_error("g3_validation_failed")
            if result.assembled.errors:
                self._kill_switch.record_error("assembled_errors")
            return result
        except Exception as exc:
            self._kill_switch.record_error(f"pipeline_error: {exc}")
            if self.fuse_on:
                self.auto_shutdown(reason=f"fuse triggered by error: {exc}")
            raise
        finally:
            timer.cancel()

    def _on_timeout(self) -> None:
        """超时回调：记录错误并触发自动关闭。"""
        self._kill_switch.record_error(f"timeout: {self._timeout_seconds}s")
        if self.fuse_on:
            self.auto_shutdown(reason=f"timeout: {self._timeout_seconds}s")

    def auto_shutdown(self, reason: str = "") -> None:
        """自动关闭：触发 KillSwitch 熔断，执行资源清理。幂等。"""
        with self._lock:
            if not self._started:
                return
            logger.warning("ContextPipelineAuto shutting down: %s", reason)

            for cb in self._cleanup_callbacks:
                try:
                    cb()
                except Exception as exc:
                    logger.error("ContextPipelineAuto cleanup callback failed: %s", exc, exc_info=True)

            self._cleanup_callbacks.clear()
            self._started = False
            logger.info("ContextPipelineAuto shutdown complete: %s", reason)

    def register_cleanup(self, callback: Callable[[], None]) -> None:
        """注册资源清理回调（auto_shutdown 时执行）。"""
        self._cleanup_callbacks.append(callback)

    def reset_fuse(self) -> None:
        """重置 KillSwitch 熔断（手动恢复）。"""
        self._kill_switch.reset()
        logger.info("ContextPipelineAuto KillSwitch fuse reset")