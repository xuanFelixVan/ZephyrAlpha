# [A_test] module_id: MOD-GOV_brain_integration_resource_optimization | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-547 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.resource_optimization.test_brain_integration
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
test_brain_integration.py - Brain system + ResourceOptimizationEngine integration
==================================================================================

Verifies:
  1. HealthMonitor.pressure_level() delegates to ResourceOptimizationEngine
  2. AutoRuntimeCore.boot() starts engine monitor
  3. AutoRuntimeCore.shutdown() stops engine monitor
  4. Pressure level mapping between ROE and brain system
"""

from __future__ import annotations

import pandas  # noqa: F401  # 预热导入，勿删（非 unused）：
# 2026-08-24 四轮全量 sweep 实证：隔离 19/19 全绿；三路并发 sweep 极限负载下，
# 用例内延迟导入 auto_runtime_core 时与残留监控线程并发首导 pandas，触发 C 扩展
# 部分初始化竞态（AttributeError: partially initialized module 'pandas' has no
# attribute '_pandas_datetime_CAPI'）。收集期主线程完成全量初始化后，线程并发
# import 走 sys.modules 快路径，竞态确定性消除。

from unittest.mock import MagicMock, patch

from zephyr.trading.health_monitor import HealthMonitor, PressureLevel


class TestHealthMonitorDelegation:
    def setup_method(self):
        from zephyr.trading.resource_optimization import ResourceOptimizationEngine

        ResourceOptimizationEngine.reset()

    def teardown_method(self):
        from zephyr.trading.resource_optimization import ResourceOptimizationEngine

        ResourceOptimizationEngine.reset()

    def test_pressure_level_delegates_to_roe(self):
        from zephyr.shared.lifecycle.resource_optimization_models import PressureLevel as ROELevel
        from zephyr.trading.resource_optimization import ResourceOptimizationEngine

        engine = ResourceOptimizationEngine()
        engine.force_pressure(ROELevel.WARNING, "test")  # 跟进：current 只读 property，公开入口 force_pressure

        monitor = HealthMonitor()
        level = monitor.pressure_level()
        assert level == PressureLevel.ELEVATED

    def test_pressure_level_mapping_critical(self):
        from zephyr.shared.lifecycle.resource_optimization_models import PressureLevel as ROELevel
        from zephyr.trading.resource_optimization import ResourceOptimizationEngine

        engine = ResourceOptimizationEngine()
        engine.force_pressure(ROELevel.CRITICAL, "test")  # 跟进：current 只读 property，公开入口 force_pressure

        monitor = HealthMonitor()
        level = monitor.pressure_level()
        assert level == PressureLevel.HIGH

    def test_pressure_level_mapping_emergency(self):
        from zephyr.shared.lifecycle.resource_optimization_models import PressureLevel as ROELevel
        from zephyr.trading.resource_optimization import ResourceOptimizationEngine

        engine = ResourceOptimizationEngine()
        engine.force_pressure(ROELevel.EMERGENCY, "test")  # 跟进：current 只读 property，公开入口 force_pressure

        monitor = HealthMonitor()
        level = monitor.pressure_level()
        assert level == PressureLevel.CRITICAL

    def test_pressure_level_mapping_normal(self):
        from zephyr.shared.lifecycle.resource_optimization_models import PressureLevel as ROELevel
        from zephyr.trading.resource_optimization import ResourceOptimizationEngine

        engine = ResourceOptimizationEngine()
        engine.force_pressure(ROELevel.NORMAL, "test")  # 跟进：current 只读 property，公开入口 force_pressure

        monitor = HealthMonitor()
        level = monitor.pressure_level()
        assert level == PressureLevel.NORMAL

    def test_pressure_level_fallback_on_import_error(self):
        monitor = HealthMonitor()
        with patch.dict(
            "sys.modules", {"zephyr.infrastructure.shared_services.lifecycle.resource_optimization_engine": None}
        ):
            level = monitor.pressure_level()
            assert isinstance(level, PressureLevel)


class TestAutoRuntimeCoreLifecycle:
    def setup_method(self):
        from zephyr.trading.resource_optimization import ResourceOptimizationEngine

        ResourceOptimizationEngine.reset()

    def teardown_method(self):
        from zephyr.trading.resource_optimization import ResourceOptimizationEngine

        ResourceOptimizationEngine.reset()

    def test_boot_starts_engine_monitor(self):
        from zephyr.trading.auto_runtime_core import AutoRuntimeCore
        from zephyr.trading.lifecycle_manager import BootReport

        mock_engine = MagicMock()
        with patch(
            "zephyr.trading.auto_runtime_core.ResourceOptimizationEngine",  # 跟进：消费点模块级 import（auto_runtime_core L83 模块级 import）
            return_value=mock_engine,
        ):
            core = AutoRuntimeCore()
            # _start_local_models connects to local Ollama (HTTP/localhost:11434).
            # Without Ollama it hangs 25s+, must mock.
            with (
                patch.object(core, "_start_local_models"),
                patch.object(core.lifecycle, "boot_sequence", return_value=BootReport(success=True)),
            ):
                core.boot()
            mock_engine.start_monitor.assert_called_once_with(interval=30.0)

    def test_shutdown_stops_engine_monitor(self):
        from zephyr.trading.auto_runtime_core import AutoRuntimeCore
        from zephyr.trading.lifecycle_manager import ShutdownReport

        mock_engine = MagicMock()
        with patch(
            "zephyr.trading.auto_runtime_core.ResourceOptimizationEngine",  # 跟进：消费点模块级 import（auto_runtime_core L83 模块级 import）
            return_value=mock_engine,
        ):
            core = AutoRuntimeCore()
            with (
                patch.object(core, "_start_local_models"),
                patch.object(core.lifecycle, "shutdown_sequence", return_value=ShutdownReport()),
            ):
                core.shutdown()
            mock_engine.stop_monitor.assert_called_once()

    def test_boot_skips_engine_on_failure(self):
        from zephyr.trading.auto_runtime_core import AutoRuntimeCore
        from zephyr.trading.lifecycle_manager import BootReport

        core = AutoRuntimeCore()
        with patch.object(core.lifecycle, "boot_sequence", return_value=BootReport(success=False)):
            report = core.boot()

        assert report.success is False
