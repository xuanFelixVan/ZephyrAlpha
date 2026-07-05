# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.utils.async_utils
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] run_sync 永不因已有事件循环而抛 RuntimeError
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_async_utils | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""async_utils.py — async/sync 边界桥接（5.12.8 修复）

痛点：asyncio.run() 在已有事件循环上下文中抛 RuntimeError：
  "asyncio.run() cannot be called from a running event loop"

本模块提供 run_sync() —— 从同步代码安全运行协程，无论是否已有运行中的事件循环。
替代散布 40+ 处的裸 asyncio.run() 调用（5.12.8 签名漂移/边界统一）。

设计：
  - 无运行中的事件循环 → asyncio.run(coro)（快速路径，与原行为完全一致）
  - 有运行中的事件循环 → 在新线程中创建独立事件循环运行协程
    （避免嵌套 RuntimeError；协程每次新建，不捕获 loop-bound 状态，线程隔离安全）

SSoT: 5.12.8 修复方向「统一async/sync边界」
Version: 0.1.0
"""

from __future__ import annotations

import asyncio
import concurrent.futures
from collections.abc import Awaitable
from typing import TypeVar

T = TypeVar("T")

__all__ = ["run_sync"]


def run_sync(coro: Awaitable[T], *, timeout: float | None = None) -> T:
    """从同步代码安全运行协程——不会因已有事件循环而抛 RuntimeError。

    5.12.8 修复：替代散布 40+ 处的裸 asyncio.run() 调用。

    行为：
      - 无运行中的事件循环 → asyncio.run(coro)（快速路径，与原行为一致）
      - 有运行中的事件循环 → 在新线程中创建独立事件循环运行协程
        （避免 "asyncio.run() cannot be called from a running event loop"）

    Args:
        coro: 协程或 awaitable。
        timeout: 可选超时秒数（None=无超时）。

    Returns:
        协程结果。

    Raises:
        TimeoutError: 超时。
        Exception: 协程抛出的异常原样传播。
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # 无运行中的事件循环——快速路径（与原 asyncio.run 行为一致）
        if timeout is not None:
            return asyncio.run(_with_timeout(coro, timeout))  # type: ignore[arg-type]
        return asyncio.run(coro)  # type: ignore[arg-type]

    # 有运行中的事件循环——在新线程中用独立循环运行，避免嵌套 RuntimeError
    def _run_in_thread() -> T:
        loop = asyncio.new_event_loop()
        try:
            if timeout is not None:
                return loop.run_until_complete(_with_timeout(coro, timeout))
            return loop.run_until_complete(coro)  # type: ignore[arg-type]
        finally:
            loop.close()

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(_run_in_thread)
        return future.result()


async def _with_timeout(coro: Awaitable[T], timeout: float) -> T:
    """内部辅助——为协程包装超时。"""
    return await asyncio.wait_for(coro, timeout=timeout)
