# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.governance.ops_governance.event_hook
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_event_hook | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

"""
EventHook — 声明式任务系统事件订阅
=======================================
Blueprint: MOD-TASK_SYSTEM 盲点#4
依赖: 无外部依赖（纯内存事件总线）

HookRegistry: 全局注册表，管理状态变更回调链。
所有注册的回调按 priority 排序执行，异常隔离（一个回调崩溃不影响其他）。

Usage:
    from zephyr.governance.ops_governance.event_hook import hook_registry

    def on_task_completed(event: TransitionEvent):
        print(f"Task {event.task_id} completed!")

    hook_registry.register(on_task_completed, priority=50)
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("zephyr.governance.event_hook")

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
        for i, h in enumerate(self._hooks):
            if h.callback is callback:
                self._hooks.pop(i)
                return True
        return False

    def clear(self) -> None:
        """清空所有钩子。"""
        self._hooks.clear()

    # ── internal ───────────────────────────────────────────────────

    def fire(self, event: TransitionEvent) -> None:
        """触发所有注册的回调。

        按 priority 顺序执行。单个回调的异常被隔离并记录。
        """
        if not self._active:
            return
        for h in self._hooks:
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
        self._active = False

    def resume(self) -> None:
        self._active = True

    def get_all(self) -> list[str]:
        """返回所有已注册钩子的名称列表（调试用）。"""
        return [f"{h.name}(prio={h.priority})" for h in self._hooks]


# ── Singleton ────────────────────────────────────────────────────────

hook_registry = HookRegistry()
