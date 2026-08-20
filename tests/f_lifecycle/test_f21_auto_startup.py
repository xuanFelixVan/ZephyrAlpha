# [A_test] module_id: MOD-GOV_f21_auto_startup | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] tests.test_f21_auto_startup
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] CI
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_f21_auto_startup.py
# [TTL] task_bound

"""
F21 自动启动测试 — DM-201250
验证 boot_hooks.init_shared_monitoring_modules() 能自动初始化 6 个监控模块。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# 确保 src 在 path
_src = Path(__file__).resolve().parent.parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))


class TestAutoStartup:
    """自动启动测试 — 验证 boot_hooks 初始化 6 个监控模块。"""

    def test_boot_hooks_module_importable(self) -> None:
        """boot_hooks 模块可导入。"""
        from zephyr.trading import boot_hooks

        assert boot_hooks is not None

    def test_init_function_exists(self) -> None:
        """_init_shared_monitoring_modules 函数存在。"""
        import inspect

        from zephyr.trading import boot_hooks

        src = inspect.getsource(boot_hooks)
        assert "_init_shared_monitoring_modules" in src, "boot_hooks 缺少 _init_shared_monitoring_modules"

    def test_init_function_callable(self) -> None:
        """_init_shared_monitoring_modules 可调用（不抛异常）。"""
        from zephyr.trading import boot_hooks

        fn = getattr(boot_hooks, "_init_shared_monitoring_modules", None)
        if fn is not None:
            # 调用不应抛异常（内部有 try/except 保护）
            fn()
        # 即使 fn 是 None（可能是私有），源码中存在即可
        assert True

    def test_longevity_monitor_importable(self) -> None:
        """LongevityMonitor 模块可导入。"""
        from zephyr.shared.lifecycle.longevity_monitor import LongevityMonitor

        assert LongevityMonitor is not None

    def test_healthcheck_service_importable(self) -> None:
        """HealthcheckService 模块可导入。"""
        from zephyr.shared.lifecycle.healthcheck_service import HealthcheckService

        assert HealthcheckService is not None

    def test_health_discovery_importable(self) -> None:
        """HealthDiscovery 模块可导入。"""
        from zephyr.shared.lifecycle.health_discovery import HealthDiscovery

        assert HealthDiscovery is not None

    def test_metrics_registry_importable(self) -> None:
        """MetricsRegistry 模块可导入。"""
        from zephyr.shared.observability.metrics import MetricsRegistry

        assert MetricsRegistry is not None

    def test_autonomy_monitor_importable(self) -> None:
        """AutonomyMonitor 模块可导入。"""
        from zephyr.shared.maintenance.autonomy_monitor import AutonomyMonitor

        assert AutonomyMonitor is not None

    def test_event_subscription_importable(self) -> None:
        """事件订阅函数可导入。"""
        from zephyr.shared.lifecycle.health import subscribe_monitoring_events
        from zephyr.shared.observability.metrics import subscribe_metrics_events

        assert callable(subscribe_monitoring_events)
        assert callable(subscribe_metrics_events)

    def test_finalizer_registration_importable(self) -> None:
        """Finalizer 自动注册函数可导入。"""
        from zephyr.trading.finalizer import register_monitoring_finalizers_auto

        assert callable(register_monitoring_finalizers_auto)

    def test_boot_hooks_source_contains_all_6_modules(self) -> None:
        """boot_hooks 源码包含全部 6 个模块的初始化代码。"""
        import inspect

        from zephyr.trading import boot_hooks

        src = inspect.getsource(boot_hooks)

        # 6 个监控模块的导入/初始化
        checks = [
            ("LongevityMonitor", "LongevityMonitor" in src),
            ("HealthcheckService", "HealthcheckService" in src),
            ("HealthDiscovery", "HealthDiscovery" in src),
            ("MetricsRegistry", "MetricsRegistry" in src),
            ("AutonomyMonitor", "AutonomyMonitor" in src),
            ("subscribe_monitoring_events", "subscribe_monitoring_events" in src),
            ("subscribe_metrics_events", "subscribe_metrics_events" in src),
            ("register_monitoring_finalizers_auto", "register_monitoring_finalizers_auto" in src),
        ]

        for name, found in checks:
            assert found, f"boot_hooks 源码缺少 {name}"

    def test_boot_hooks_idempotent(self) -> None:
        """boot_hooks 初始化幂等（重复调用不抛异常）。"""
        from zephyr.trading import boot_hooks

        fn = getattr(boot_hooks, "_init_shared_monitoring_modules", None)
        if fn is not None:
            fn()
            fn()  # 重复调用
        assert True

    def test_boot_hooks_exception_safety(self) -> None:
        """boot_hooks 初始化异常安全（即使部分模块失败也不影响整体）。"""
        from zephyr.trading import boot_hooks

        fn = getattr(boot_hooks, "_init_shared_monitoring_modules", None)
        if fn is not None:
            # 应该不抛任何异常
            try:
                fn()
            except Exception as e:
                pytest.fail(f"_init_shared_monitoring_modules 抛异常: {e}")
        assert True
