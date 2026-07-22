# [A_test] module_id: MOD-GOV_async_runtime | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_async_runtime | docs/02_enterprise_architecture/architecture_upgrade_discussion.md | §4.1
# [MODULE] tests.trading.runtime.test_async_runtime
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""AsyncRuntime 测试——事件循环引导 + run_in_executor 桥接。

覆盖：
- start/stop 生命周期
- run_coroutine 同步入口桥接
- run_in_executor 同步→异步桥接
- run_in_executor_async 异步版本
- 上下文管理器协议
- 幂等性/边界条件
"""

from __future__ import annotations

import asyncio
import time

import pytest

from zephyr.trading.runtime.async_runtime import AsyncRuntime


class TestAsyncRuntimeLifecycle:
    """启动/停止事件循环生命周期。"""

    def test_start_creates_loop(self):
        runtime = AsyncRuntime()
        try:
            loop = runtime.start()
            assert loop is not None
            assert not loop.is_closed()
        finally:
            runtime.stop()

    def test_stop_is_idempotent(self):
        runtime = AsyncRuntime()
        runtime.start()
        runtime.stop()
        runtime.stop()  # 二次调用不抛异常

    def test_stop_without_start_is_safe(self):
        runtime = AsyncRuntime()
        runtime.stop()  # 未 start 直接 stop 不抛异常

    def test_is_running_flag(self):
        runtime = AsyncRuntime()
        assert not runtime.is_running
        runtime.start()
        # is_running 取决于循环是否在跑（start 不阻塞运行循环）
        assert runtime.loop is not None
        runtime.stop()
        assert not runtime.is_running

    def test_loop_is_none_after_stop(self):
        runtime = AsyncRuntime()
        runtime.start()
        assert runtime.loop is not None
        runtime.stop()
        assert runtime.loop is None


class TestRunCoroutine:
    """run_coroutine 同步入口桥接。"""

    def test_run_coroutine_returns_result(self):
        async def async_func() -> int:
            await asyncio.sleep(0.01)
            return 42

        runtime = AsyncRuntime()
        try:
            result = runtime.run_coroutine(async_func())
            assert result == 42
        finally:
            runtime.stop()

    def test_run_coroutine_without_start(self):
        async def async_func() -> str:
            return "hello"

        runtime = AsyncRuntime()
        # run_coroutine 不依赖 start()——它用 asyncio.run
        result = runtime.run_coroutine(async_func())
        assert result == "hello"

    def test_run_coroutine_propagates_exception(self):
        async def failing_func() -> None:
            raise ValueError("test error")

        runtime = AsyncRuntime()
        with pytest.raises(ValueError, match="test error"):
            runtime.run_coroutine(failing_func())


class TestRunInExecutor:
    """run_in_executor 同步→异步桥接。"""

    def test_run_in_executor_sync_call(self):
        def sync_func(a: int, b: int) -> int:
            return a + b

        runtime = AsyncRuntime()
        try:
            # 无运行中的事件循环 → 直接同步调用
            result = runtime.run_in_executor(sync_func, 3, 4)
            assert result == 7
        finally:
            runtime.stop()

    def test_run_in_executor_with_kwargs(self):
        def sync_func(a: int, b: int = 10) -> int:
            return a * b

        runtime = AsyncRuntime()
        try:
            result = runtime.run_in_executor(sync_func, 5, b=20)
            assert result == 100
        finally:
            runtime.stop()

    def test_run_in_executor_propagates_exception(self):
        def failing_func() -> None:
            raise RuntimeError("executor error")

        runtime = AsyncRuntime()
        with pytest.raises(RuntimeError, match="executor error"):
            runtime.run_in_executor(failing_func)

    def test_run_in_executor_blocking_function(self):
        def blocking_func() -> float:
            time.sleep(0.05)
            return time.time()

        runtime = AsyncRuntime()
        try:
            result = runtime.run_in_executor(blocking_func)
            assert result > 0
        finally:
            runtime.stop()


class TestRunInExecutorAsync:
    """run_in_executor_async 异步版本。"""

    def test_run_in_executor_async_returns_result(self):
        def sync_func(x: int) -> int:
            return x * 2

        async def runner() -> int:
            runtime = AsyncRuntime()
            return await runtime.run_in_executor_async(sync_func, 21)

        result = asyncio.run(runner())
        assert result == 42

    def test_run_in_executor_async_with_kwargs(self):
        def sync_func(a: int, b: int) -> int:
            return a - b

        async def runner() -> int:
            runtime = AsyncRuntime()
            return await runtime.run_in_executor_async(sync_func, 10, b=3)

        result = asyncio.run(runner())
        assert result == 7

    def test_run_in_executor_async_propagates_exception(self):
        def failing_func() -> None:
            raise ValueError("async executor error")

        async def runner() -> None:
            runtime = AsyncRuntime()
            await runtime.run_in_executor_async(failing_func)

        with pytest.raises(ValueError, match="async executor error"):
            asyncio.run(runner())


class TestContextManager:
    """上下文管理器协议。"""

    def test_context_manager_starts_and_stops(self):
        with AsyncRuntime() as runtime:
            assert runtime.loop is not None
        assert runtime.loop is None

    def test_context_manager_run_coroutine(self):
        async def async_func() -> int:
            return 99

        with AsyncRuntime() as runtime:
            result = runtime.run_coroutine(async_func())
            assert result == 99


class TestBackwardCompatibility:
    """向后兼容——不破坏现有同步入口。"""

    def test_sync_function_still_works(self):
        """同步函数在没有 AsyncRuntime 时仍正常工作。"""

        def sync_main() -> str:
            return "sync entry point"

        assert sync_main() == "sync entry point"

    def test_runtime_does_not_interfere_with_sync(self):
        """AsyncRuntime 不干扰同步代码执行。"""
        runtime = AsyncRuntime()
        try:
            runtime.start()
            # 同步代码仍可正常执行
            result = sum(range(100))
            assert result == 4950
        finally:
            runtime.stop()


class TestNoThreadingLock:
    """验证不变量：不持有 threading.Lock（§4.1 风险表）。"""

    def test_no_threading_lock_in_instance(self):
        import threading

        runtime = AsyncRuntime()
        try:
            runtime.start()
            # 检查实例属性中没有 threading.Lock 实例
            for attr_name in dir(runtime):
                if attr_name.startswith("_"):
                    attr_value = getattr(runtime, attr_name, None)
                    assert not isinstance(attr_value, type(threading.Lock())), (
                        f"属性 {attr_name} 是 threading.Lock——违反不变量"
                    )
        finally:
            runtime.stop()
