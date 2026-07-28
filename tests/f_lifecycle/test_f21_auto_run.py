# [A_test] module_id: MOD-GOV_f21_auto_run | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] tests.test_f21_auto_run
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] CI
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_f21_auto_run.py
# [TTL] task_bound

"""
F21 自动运行测试 — DM-201250
验证 HealthMonitor 分钟级监控 + CircadianScheduler 小时级调度。
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pytest

# 确保 src 在 path
_src = Path(__file__).resolve().parent.parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))


class TestHealthMonitorAutoRun:
    """HealthMonitor 分钟级自动运行测试。"""

    def test_health_monitor_importable(self) -> None:
        """HealthMonitor 可导入。"""
        from zephyr.trading.health_monitor import HealthMonitor
        assert HealthMonitor is not None

    def test_health_monitor_instantiable(self) -> None:
        """HealthMonitor 可实例化。"""
        from zephyr.trading.health_monitor import HealthMonitor
        hm = HealthMonitor()
        assert hm is not None

    def test_health_monitor_start_stop(self) -> None:
        """HealthMonitor 可启动和停止。"""
        from zephyr.trading.health_monitor import HealthMonitor
        hm = HealthMonitor(health_check_interval=0.1, metrics_interval=0.05)
        hm.start()
        time.sleep(0.2)  # 让监控循环跑一会
        hm.stop()
        assert True

    def test_health_monitor_background_thread(self) -> None:
        """HealthMonitor 启动后台线程。"""
        from zephyr.trading.health_monitor import HealthMonitor
        hm = HealthMonitor(health_check_interval=0.1, metrics_interval=0.05)
        hm.start()

        # 验证线程已启动
        assert hm.monitor_thread is not None, "后台线程未启动"
        assert hm.monitor_thread.is_alive(), "后台线程未运行"

        hm.stop()

        # 验证线程已停止
        assert not hm.running, "HealthMonitor 仍在运行"

    def test_health_monitor_register_probe(self) -> None:
        """HealthMonitor 可注册 probe。"""
        from zephyr.trading.health_monitor import HealthMonitor, ProbeResult
        hm = HealthMonitor()

        def _test_probe():
            return ProbeResult(capability_id="test", alive=True, ready=True)

        hm.register_probe("test.capability", _test_probe)
        assert "test.capability" in hm.probe_fns or len(hm.probe_fns) > 0

    def test_health_monitor_register_shared_monitoring_probes(self) -> None:
        """HealthMonitor 可注册 shared/ 监控模块 probe。"""
        from zephyr.trading.health_monitor import HealthMonitor
        hm = HealthMonitor()
        hm.register_shared_monitoring_probes()
        assert True  # 不抛异常即可

    def test_health_monitor_reconcile(self) -> None:
        """HealthMonitor reconcile 可调用。"""
        from zephyr.trading.health_monitor import HealthMonitor
        hm = HealthMonitor()
        report = hm.reconcile()
        assert report is not None

    def test_health_monitor_collect_metrics(self) -> None:
        """HealthMonitor _collect_metrics 可调用。"""
        from zephyr.trading.health_monitor import HealthMonitor
        hm = HealthMonitor()
        hm.collect_metrics()
        assert True  # 不抛异常即可


class TestCircadianSchedulerAutoRun:
    """CircadianScheduler 小时级自动运行测试。"""

    def test_sla_hourly_report_not_registered(self) -> None:
        """定时调度已废除：sla_hourly_report 不再通过 CircadianScheduler 定时触发。"""
        from zephyr.trading import boot_cron_jobs
        import inspect
        src = inspect.getsource(boot_cron_jobs)
        # 定时调度已废除，不应有 sla_hourly_report 的 register_task 调用
        assert "sla_hourly_report" not in src or "register_task" not in src

    def test_health_monitor_monitor_loop_exception_safety(self) -> None:
        """HealthMonitor 监控循环异常安全。"""
        from zephyr.trading.health_monitor import HealthMonitor
        hm = HealthMonitor(health_check_interval=0.05, metrics_interval=0.02)
        hm.start()
        time.sleep(0.15)
        # 即使内部有异常，循环也应继续
        assert hm.monitor_thread.is_alive() if hm.monitor_thread else False, "监控循环因异常退出"
        hm.stop()
