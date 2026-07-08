# [A_test] module_id: SRC-TST-F214 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] tests.test_f21_auto_shutdown
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] CI
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_f21_auto_shutdown.py
# [TTL] task_bound

"""
F21 自动关闭测试 — DM-201250
验证 Finalizer flush + 健康快照保存。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# 确保 src 在 path
_src = Path(__file__).resolve().parent.parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))


class TestFinalizerAutoShutdown:
    """Finalizer 自动关闭测试。"""

    def setup_method(self) -> None:
        """每个测试前重置状态。"""
        import zephyr.trading.finalizer as fin_mod
        fin_mod._monitoring_finalizers_registered = False
        fin_mod._global_finalizer = None

    def test_finalizer_importable(self) -> None:
        """Finalizer 可导入。"""
        from zephyr.trading.finalizer import Finalizer
        assert Finalizer is not None

    def test_finalizer_instantiable(self) -> None:
        """Finalizer 可实例化。"""
        from zephyr.trading.finalizer import Finalizer
        f = Finalizer()
        assert f is not None

    def test_finalizer_register(self) -> None:
        """Finalizer 可注册 cleanup 函数。"""
        from zephyr.trading.finalizer import Finalizer
        f = Finalizer()

        called = []
        def _cleanup():
            called.append(True)

        f.register("test-resource", _cleanup)
        assert len(f._cleanup_fns) == 1

    def test_finalizer_run(self) -> None:
        """Finalizer run 执行所有 cleanup。"""
        from zephyr.trading.finalizer import Finalizer
        f = Finalizer()

        called = []
        f.register("r1", lambda: called.append("r1"))
        f.register("r2", lambda: called.append("r2"))

        results = f.run()
        assert results["r1"] is True
        assert results["r2"] is True
        assert "r1" in called
        assert "r2" in called

    def test_finalizer_exception_safety(self) -> None:
        """Finalizer cleanup 异常安全。"""
        from zephyr.trading.finalizer import Finalizer
        f = Finalizer()

        def _bad_cleanup():
            raise RuntimeError("intentional test error")

        def _good_cleanup():
            pass

        f.register("bad", _bad_cleanup)
        f.register("good", _good_cleanup)

        results = f.run()
        assert results["bad"] is False  # 异常被捕获
        assert results["good"] is True  # 正常执行

    def test_get_finalizer_singleton(self) -> None:
        """get_finalizer 返回单例。"""
        from zephyr.trading.finalizer import get_finalizer
        f1 = get_finalizer()
        f2 = get_finalizer()
        assert f1 is f2

    def test_register_monitoring_finalizers(self) -> None:
        """register_monitoring_finalizers 注册监控 cleanup。"""
        from zephyr.trading.finalizer import Finalizer, register_monitoring_finalizers
        f = Finalizer()

        initial = len(f._cleanup_fns)
        register_monitoring_finalizers(f)
        after = len(f._cleanup_fns)

        assert after == initial + 2, f"应注册 2 个 cleanup，实际增加 {after - initial}"

    def test_register_monitoring_finalizers_idempotent(self) -> None:
        """register_monitoring_finalizers 幂等。"""
        from zephyr.trading.finalizer import Finalizer, register_monitoring_finalizers
        f = Finalizer()

        register_monitoring_finalizers(f)
        after_first = len(f._cleanup_fns)
        register_monitoring_finalizers(f)  # 第二次
        after_second = len(f._cleanup_fns)

        assert after_first == after_second, f"幂等失败: {after_first} -> {after_second}"

    def test_register_monitoring_finalizers_auto(self) -> None:
        """register_monitoring_finalizers_auto 使用全局单例。"""
        from zephyr.trading.finalizer import register_monitoring_finalizers_auto, get_finalizer
        register_monitoring_finalizers_auto()
        f = get_finalizer()
        assert len(f._cleanup_fns) == 2

    def test_monitor_flush_cleanup(self) -> None:
        """monitor-flush cleanup 执行成功。"""
        from zephyr.trading.finalizer import register_monitoring_finalizers_auto, get_finalizer
        register_monitoring_finalizers_auto()
        f = get_finalizer()
        results = f.run()
        assert results.get("monitor-flush") is True, f"monitor-flush 失败: {results}"

    def test_monitor_health_snapshot_cleanup(self) -> None:
        """monitor-health-snapshot cleanup 执行成功。"""
        from zephyr.trading.finalizer import register_monitoring_finalizers_auto, get_finalizer
        register_monitoring_finalizers_auto()
        f = get_finalizer()
        results = f.run()
        assert results.get("monitor-health-snapshot") is True, f"monitor-health-snapshot 失败: {results}"

    def test_finalizer_with_event_data(self) -> None:
        """Finalizer 在有事件数据时正常工作。"""
        from zephyr.trading.finalizer import register_monitoring_finalizers_auto, get_finalizer
        from zephyr.shared.lifecycle.health import subscribe_monitoring_events, get_event_health_log
        from zephyr.shared.event_bus import bus

        import zephyr.shared.lifecycle.health as health_mod
        health_mod._monitoring_events_subscribed = False
        health_mod._event_health_log = []

        # 订阅事件
        subscribe_monitoring_events()

        # 触发事件
        bus.emit("f5.deadlock_detected", {"test": "finalizer"})
        bus.emit("fle.anomaly", {"test": "finalizer"})

        # 验证事件已记录
        log = get_event_health_log()
        assert len(log) >= 2

        # 注册 finalizer 并运行
        register_monitoring_finalizers_auto()
        f = get_finalizer()
        results = f.run()

        # monitor-health-snapshot 应成功（捕获了事件日志）
        assert results.get("monitor-health-snapshot") is True

    def test_boot_hooks_integrates_finalizer(self) -> None:
        """boot_hooks 集成了 finalizer 注册。"""
        from zephyr.trading import boot_hooks
        import inspect
        src = inspect.getsource(boot_hooks)
        assert "register_monitoring_finalizers_auto" in src, "boot_hooks 未集成 finalizer"

    def test_finalizer_cleanup_order(self) -> None:
        """Finalizer cleanup 按注册顺序执行。"""
        from zephyr.trading.finalizer import Finalizer
        f = Finalizer()

        order = []
        f.register("first", lambda: order.append("first"))
        f.register("second", lambda: order.append("second"))
        f.register("third", lambda: order.append("third"))

        f.run()
        assert order == ["first", "second", "third"], f"cleanup 顺序错误: {order}"

    def test_finalizer_empty_run(self) -> None:
        """Finalizer 无 cleanup 时 run 返回空结果。"""
        from zephyr.trading.finalizer import Finalizer
        f = Finalizer()
        results = f.run()
        assert results == {}
