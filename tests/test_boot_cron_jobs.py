# [A_test] module_id: SRC-TST-0444 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] tests.test_boot_cron_jobs
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_boot_cron_jobs.py

from __future__ import annotations

from unittest.mock import MagicMock, patch

from zephyr.trading.boot_cron_jobs import register_boot_cron_jobs


class TestRegisterBootCronJobs:
    """定时调度已废除（2026-06-26裁定）：register_boot_cron_jobs 保留函数签名
    但不再调用 register_task。以下测试验证 no-op 行为。"""

    def test_does_not_register_tasks(self, tmp_path):
        """register_task 不被调用（定时调度已废除）。"""
        scheduler = MagicMock()
        orchestrator = MagicMock()
        with patch("zephyr.trading.boot_cron_jobs.TaskRepository", create=True) as mock_repo_cls:
            with patch("zephyr.trading.boot_cron_jobs.TaskCompletionGate", create=True) as mock_gate_cls:
                mock_repo_cls.return_value = MagicMock()
                mock_gate_cls.return_value = MagicMock()
                register_boot_cron_jobs(scheduler, orchestrator, tmp_path)
        assert scheduler.register_task.call_count == 0

    def test_failure_does_not_raise(self, tmp_path):
        scheduler = MagicMock()
        orchestrator = MagicMock()
        with patch(
            "zephyr.trading.boot_cron_jobs.TaskRepository",
            side_effect=ImportError("no module"),
            create=True,
        ):
            register_boot_cron_jobs(scheduler, orchestrator, tmp_path)
