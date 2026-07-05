# [BLUEPRINT] R1-1 | docs/02_enterprise_architecture/architecture_upgrade_discussion.md | §4.1
# [MODULE] zephyr.trading.runtime.async_runtime
# [DOMAIN] D_TRADING
# [DEPENDENCIES]
# [CONSUMERS] R1-2 AsyncEventBus；R1-3 PipelineOrchestrator；R1-4 Conductor；__main__.py（未来迁移）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不持有 threading.Lock（避免与 asyncio 死锁，§4.1 风险表）；事件循环单例——同一进程只引导一次；优雅关闭——stop() 等待 pending 任务完成或超时
# [MODIFY-GUARD] 修改本文件必须同步检查 __main__.py 同步入口是否仍可用；修改 run_in_executor 签名必须同步更新所有调用方
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] start() 复用已有循环或创建新循环；stop() 幂等（多次调用安全）；run_coroutine 在已运行循环中抛 RuntimeError；run_in_executor 无循环时直接同步调用
# [TESTS] tests/trading/runtime/test_async_runtime.py
# [A_module] module_id=MOD-TRADING-RUNTIME-ASYNC | layer=infrastructure | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations
from zephyr.shared.utils.async_utils import run_sync  # 5.12.8 修复：统一 async/sync 边界
"""AsyncRuntime — 事件循环引导 + run_in_executor 桥接（R1-1）

渐进式 async 化的入口：提供事件循环生命周期管理 + 同步→异步桥接，
不破坏现有 __main__.py 同步入口。现有同步代码通过 run_in_executor 在 async
环境中调用，逐步迁移。

蓝图: docs/02_enterprise_architecture/architecture_upgrade_discussion.md §4.1 R1-1
风险表: asyncio 事件循环与 threading.Lock 死锁 → 本模块用 run_in_executor 桥接，
        不混用 asyncio.Lock 与 threading.Lock
"""

import asyncio
import concurrent.futures
import contextvars
import functools
import logging
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

__all__ = ["AsyncRuntime"]


class AsyncRuntime:
    """事件循环引导 + run_in_executor 桥接。

    职责：
    1. 启动/停止 asyncio 事件循环（优雅关闭）
    2. run_in_executor 桥接——让同步代码在 async 环境中调用
    3. run_coroutine——在同步入口中运行 async 函数（asyncio.run 封装）

    不变量：
    - 不持有 threading.Lock（避免与 asyncio 死锁，§4.1 风险表）
    - 事件循环单例——同一进程只引导一次
    - 优雅关闭——stop() 等待 pending 任务完成或超时

    使用示例::

        runtime = AsyncRuntime()
        result = runtime.run_coroutine(some_async_func())
        sync_result = runtime.run_in_executor(sync_blocking_func, arg1)
        runtime.stop()
    """

    def __init__(self, max_workers: int = 4, loop_timeout: float = 5.0) -> None:
        """初始化 AsyncRuntime。

        Args:
            max_workers: ThreadPoolExecutor 最大线程数（run_in_executor 用）
            loop_timeout: stop() 时等待 pending 任务的超时秒数
        """
        self._max_workers = max_workers
        self._loop_timeout = loop_timeout
        self._loop: asyncio.AbstractEventLoop | None = None
        # 5.16.8 修复：executor 在 __init__ 时一次性创建，消除 run_in_executor 竞态
        self._executor: concurrent.futures.ThreadPoolExecutor | None = (
            concurrent.futures.ThreadPoolExecutor(
                max_workers=max_workers,
                thread_name_prefix="AsyncRuntime",
            )
        )
        self._owns_loop = False

    @property
    def loop(self) -> asyncio.AbstractEventLoop | None:
        """当前事件循环（未启动时为 None）。"""
        return self._loop

    @property
    def is_running(self) -> bool:
        """事件循环是否正在运行。"""
        return self._loop is not None and self._loop.is_running()

    def start(self) -> asyncio.AbstractEventLoop:
        """启动事件循环（不阻塞）。

        如果当前线程已有运行中的事件循环，则复用；否则创建新循环。

        Returns:
            事件循环实例
        """
        if self._loop is not None and not self._loop.is_closed():
            return self._loop

        try:
            existing = asyncio.get_running_loop()
            self._loop = existing
            self._owns_loop = False
            logger.debug("AsyncRuntime: 复用已有事件循环")
            return existing
        except RuntimeError:
            pass

        self._loop = asyncio.new_event_loop()
        # 5.100.17 修复: 设置为当前线程的默认事件循环, 避免后续 asyncio.get_event_loop() 返回不同 loop
        asyncio.set_event_loop(self._loop)
        self._owns_loop = True
        logger.debug("AsyncRuntime: 创建新事件循环")
        return self._loop

    def stop(self) -> None:
        """优雅停止事件循环。

        - 取消所有 pending 任务
        - 等待任务完成（超时 self._loop_timeout）
        - 关闭 executor
        - 关闭事件循环（仅当 AsyncRuntime 拥有它时）
        """
        # 5.144.2 修复: executor 关闭独立 try/finally, 防止 loop.close() 抛异常跳过 executor.shutdown()
        try:
            if self._loop is None:
                return

            if self._owns_loop and not self._loop.is_closed():
                try:
                    pending = asyncio.all_tasks(self._loop)
                    for task in pending:
                        task.cancel()
                    if pending:
                        self._loop.run_until_complete(
                            asyncio.wait_for(
                                asyncio.gather(*pending, return_exceptions=True),
                                timeout=self._loop_timeout,
                            )
                        )
                except (TimeoutError, RuntimeError) as e:
                    logger.warning("AsyncRuntime.stop: 等待任务超时或失败: %s", e)
                finally:
                    try:
                        self._loop.close()
                    except Exception as e:
                        logger.warning("AsyncRuntime.stop: loop.close() 失败: %s", e, exc_info=True)
                    logger.debug("AsyncRuntime: 事件循环已关闭")

            if self._executor is not None:
                self._executor.shutdown(wait=False, cancel_futures=True)
                self._executor = None
                logger.debug("AsyncRuntime: executor 已关闭")
        finally:
            self._loop = None
            self._owns_loop = False

    def run_coroutine(self, coro: Awaitable[T]) -> T:
        """在同步入口中运行 async 函数（asyncio.run 封装）。

        用于 __main__.py 等同步入口调用 async 代码。
        不破坏现有同步入口——main() 仍是 def，内部用本方法桥接。

        Args:
            coro: 协程或 awaitable

        Returns:
            协程结果
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # 5.100.14 修复: 无运行中的事件循环时, 优先复用 self._loop (若存在且未运行),
            # 避免 asyncio.run() 创建新 loop 导致 self._loop 成为孤儿
            if self._loop is not None and not self._loop.is_closed() and not self._loop.is_running():
                return self._loop.run_until_complete(coro)  # type: ignore[arg-type]
            return run_sync(coro)  # type: ignore[arg-type]

        if loop.is_running():
            raise RuntimeError(
                "run_coroutine 不能在已运行的事件循环中调用——请用 await 代替，或用 run_in_executor 桥接同步代码"
            )
        return run_sync(coro)  # type: ignore[arg-type]

    def run_in_executor(
        self,
        func: Callable[..., T],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """在事件循环中运行同步阻塞函数（run_in_executor 桥接）。

        让现有同步代码（如 Conductor.plan_cycle）能在 async 环境中调用。
        如果当前无运行中的事件循环，则直接同步调用 func。

        Args:
            func: 同步阻塞函数
            *args: 位置参数
            **kwargs: 关键字参数（通过 functools.partial 传递）

        Returns:
            func 的返回值
        """
        bound = functools.partial(func, *args, **kwargs)

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return bound()

        # 5.100.13 修复: 在运行中的事件循环里调 .result() 会阻塞 loop 线程导致死锁
        # 调用方应改用 run_in_executor_async (返回 awaitable)
        raise RuntimeError(
            "run_in_executor 不能在已运行的事件循环中调用——"
            "请用 await run_in_executor_async(...) 代替"
        )

    async def run_in_executor_async(
        self,
        func: Callable[..., T],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """异步版本 run_in_executor——返回 awaitable。

        用于 async 代码中调用同步阻塞函数。

        Args:
            func: 同步阻塞函数
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            func 的返回值（await 后获得）
        """
        bound = functools.partial(func, *args, **kwargs)

        # 5.16.8 修复：executor 已在 __init__ 创建，消除竞态（fallback 仅用于 stop() 后调用）
        if self._executor is None:
            self._executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=self._max_workers,
                thread_name_prefix="AsyncRuntime",
            )

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self._wrap_ctx(bound))

    @staticmethod
    def _wrap_ctx(func: Callable[..., T]) -> Callable[..., T]:
        """5.119.1/5.119.2 修复: 包装函数使其在executor线程中继承当前contextvars上下文。

        run_in_executor 默认不传播 contextvars,导致 _ctx_allowance/trace_id/session_id
        在线程池中丢失。用 copy_context() + ctx.run() 显式传播。
        """
        ctx = contextvars.copy_context()
        return lambda: ctx.run(func)

    def __enter__(self) -> AsyncRuntime:
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.stop()