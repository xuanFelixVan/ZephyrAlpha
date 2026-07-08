# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §
# [MODULE] zephyr.infrastructure.hooks.event_hook
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.hooks.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_event_hook | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
EventHook — 声明式任务系统事件订阅
=======================================
Blueprint: MOD-TASK_SYSTEM 盲点#4
依赖: 无外部依赖（纯内存事件总线）

HookRegistry: 全局注册表，管理状态变更回调链。
所有注册的回调按 priority 排序执行，异常隔离（一个回调崩溃不影响其他）。

Usage:
    from zephyr.infrastructure.hooks.event_hook import hook_registry

    def on_task_completed(event: TransitionEvent):
        print(f"Task {event.task_id} completed!")

    hook_registry.register(on_task_completed, priority=50)
"""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("zephyr.infrastructure.hooks")

# ── Event ────────────────────────────────────────────────────────────


@dataclass
class TransitionEvent:
    task_id: str
    from_status: str
    to_status: str
    note: str
    session_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


# ── Callback descriptor ──────────────────────────────────────────────


@dataclass(order=True)
class _HookEntry:
    priority: int
    name: str = field(compare=False)
    callback: Callable[[TransitionEvent], None] = field(compare=False)
    registered_at: str = field(compare=False, default_factory=lambda: "")


# ── Registry ─────────────────────────────────────────────────────────


class HookRegistry:
    """声明式事件钩子注册表（内部事件总线）。

    线程安全：所有操作通过 _lock 保护。
    回调异常会记录日志，不会传播——一个钩子的崩溃不影响其他。
    """

    def __init__(self) -> None:
        self._hooks: list[_HookEntry] = []
        self._active: bool = True
        # P1-8 修复：添加 _lock 实现线程安全（docstring 已声明但缺失实现）
        self._lock = threading.Lock()

    # ── public API ────────────────────────────────────────────────

    def register(
        self,
        callback: Callable[[TransitionEvent], None],
        *,
        priority: int = 100,
        name: str | None = None,
    ) -> None:
        """注册一个 transition 回调。

        Parameters
        ----------
        callback : callable(TransitionEvent) -> None
            回调函数。
        priority : int
            数字越小越先执行 (default 100)。
        name : str | None
            回调名称，用于日志和调试。
        """
        entry = _HookEntry(
            priority=priority,
            name=name or getattr(callback, "__name__", repr(callback)),
            callback=callback,
        )
        with self._lock:
            inserted = False
            for i, h in enumerate(self._hooks):
                if entry < h:
                    self._hooks.insert(i, entry)
                    inserted = True
                    break
            if not inserted:
                self._hooks.append(entry)

    def unregister(self, callback: Callable[[TransitionEvent], None]) -> bool:
        """移除一个已注册的回调。返回 True 表示成功移除。"""
        with self._lock:
            for i, h in enumerate(self._hooks):
                if h.callback is callback:
                    self._hooks.pop(i)
                    return True
        return False

    def clear(self) -> None:
        """清空所有钩子。"""
        with self._lock:
            self._hooks.clear()

    # ── internal ───────────────────────────────────────────────────

    def fire(self, event: TransitionEvent) -> None:
        """触发所有注册的回调。

        按 priority 顺序执行。单个回调的异常被隔离并记录。
        """
        with self._lock:
            if not self._active:
                return
            # 快照 hooks 列表，避免回调中 register/unregister 导致迭代异常
            hooks_snapshot = list(self._hooks)
        for h in hooks_snapshot:
            try:
                h.callback(event)
            except Exception:
                logger.exception(
                    "Hook '%s' (prio=%d) crashed on task=%s (%s->%s)",
                    h.name,
                    h.priority,
                    event.task_id,
                    event.from_status,
                    event.to_status,
                )

    def suspend(self) -> None:
        with self._lock:
            self._active = False

    def resume(self) -> None:
        with self._lock:
            self._active = True

    def get_all(self) -> list[str]:
        """返回所有已注册钩子的名称列表（调试用）。"""
        with self._lock:
            return [f"{h.name}(prio={h.priority})" for h in self._hooks]


# ── Singleton ────────────────────────────────────────────────────────

hook_registry = HookRegistry()
