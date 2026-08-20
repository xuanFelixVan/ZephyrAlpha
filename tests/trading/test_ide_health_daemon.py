# [A_test] module_id: MOD-GOV_ide_health_daemon | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-RESOURCE_OPTIMIZATION_ENGINE | docs/03_modules/_cross_layer/resource_optimization_engine/blueprint.md | §new-IDE
# [MODULE] tests.test_ide_health_daemon
# [CONSUMERS] zephyr.trading.ide_health_daemon
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] task_bound

"""IdeHealthDaemon 测试."""

from __future__ import annotations

from zephyr.trading.ide_health_daemon import IdeHealthDaemon, cleanup_completed_tasks, scan_ghost_windows


class TestIdeHealthDaemonImport:
    def test_import_ok(self):
        from zephyr.trading.ide_health_daemon import IdeHealthDaemon

        assert IdeHealthDaemon is not None

    def test_module_all(self):
        import zephyr.trading.ide_health_daemon as mod

        assert "IdeHealthDaemon" in mod.__all__
        assert "scan_ghost_windows" in mod.__all__
        assert "cleanup_completed_tasks" in mod.__all__


class TestScanGhostWindows:
    def test_returns_list(self):
        result = scan_ghost_windows()
        assert isinstance(result, list)


class TestCleanupCompletedTasks:
    def test_returns_list(self):
        result = cleanup_completed_tasks()
        assert isinstance(result, list)
