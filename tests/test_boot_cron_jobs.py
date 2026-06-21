# [A_test] module_id: SRC-TST-0444 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md | §
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

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.trading.boot_cron_jobs import register_boot_cron_jobs


class TestRegisterBootCronJobs:
    def test_registers_tasks_on_success(self, tmp_path):
        scheduler = MagicMock()
        orchestrator = MagicMock()
        with patch("zephyr.trading.boot_cron_jobs.TaskRepository", create=True) as mock_repo_cls:
            with patch("zephyr.trading.boot_cron_jobs.TaskCompletionGate", create=True) as mock_gate_cls:
                mock_repo_cls.return_value = MagicMock()
                mock_gate_cls.return_value = MagicMock()
                register_boot_cron_jobs(scheduler, orchestrator, tmp_path)
        assert scheduler.register_task.call_count >= 5
        registered_names = [
            call.kwargs.get("name", "") for call in scheduler.register_task.call_args_list
        ]
        assert "task_escalation_check" in registered_names
        assert "task_timeout_check" in registered_names
        assert "orphan_task_scan" in registered_names
        assert "daily-code-dedup" in registered_names

    def test_registers_budget_health_check(self, tmp_path):
        scheduler = MagicMock()
        orchestrator = MagicMock()
        with patch("zephyr.trading.boot_cron_jobs.TaskRepository", create=True) as mock_repo_cls:
            with patch("zephyr.trading.boot_cron_jobs.TaskCompletionGate", create=True) as mock_gate_cls:
                mock_repo_cls.return_value = MagicMock()
                mock_gate_cls.return_value = MagicMock()
                register_boot_cron_jobs(scheduler, orchestrator, tmp_path)
        registered_names = [
            call.kwargs.get("name", "") for call in scheduler.register_task.call_args_list
        ]
        assert "budget_health_check" in registered_names
        assert "budget_blueprint_alignment" in registered_names

    def test_registers_temp_file_cleanup(self, tmp_path):
        scheduler = MagicMock()
        orchestrator = MagicMock()
        with patch("zephyr.trading.boot_cron_jobs.TaskRepository", create=True) as mock_repo_cls:
            with patch("zephyr.trading.boot_cron_jobs.TaskCompletionGate", create=True) as mock_gate_cls:
                mock_repo_cls.return_value = MagicMock()
                mock_gate_cls.return_value = MagicMock()
                register_boot_cron_jobs(scheduler, orchestrator, tmp_path)
        registered_names = [
            call.kwargs.get("name", "") for call in scheduler.register_task.call_args_list
        ]
        assert "temp_file_cleanup" in registered_names

    def test_registers_triple_alignment_check(self, tmp_path):
        scheduler = MagicMock()
        orchestrator = MagicMock()
        with patch("zephyr.trading.boot_cron_jobs.TaskRepository", create=True) as mock_repo_cls:
            with patch("zephyr.trading.boot_cron_jobs.TaskCompletionGate", create=True) as mock_gate_cls:
                mock_repo_cls.return_value = MagicMock()
                mock_gate_cls.return_value = MagicMock()
                register_boot_cron_jobs(scheduler, orchestrator, tmp_path)
        registered_names = [
            call.kwargs.get("name", "") for call in scheduler.register_task.call_args_list
        ]
        assert "triple_alignment_check" in registered_names

    def test_failure_does_not_raise(self, tmp_path):
        scheduler = MagicMock()
        orchestrator = MagicMock()
        with patch(
            "zephyr.trading.boot_cron_jobs.TaskRepository",
            side_effect=ImportError("no module"),
            create=True,
        ):
            register_boot_cron_jobs(scheduler, orchestrator, tmp_path)

    def test_callback_invocation_does_not_raise(self, tmp_path):
        scheduler = MagicMock()
        orchestrator = MagicMock()
        captured_callbacks = {}

        def _capture(hour, name, layer, callback=None):
            captured_callbacks[name] = callback

        scheduler.register_task.side_effect = _capture

        with patch("zephyr.trading.boot_cron_jobs.TaskRepository", create=True) as mock_repo_cls:
            with patch("zephyr.trading.boot_cron_jobs.TaskCompletionGate", create=True) as mock_gate_cls:
                mock_repo = MagicMock()
                mock_repo.search.return_value = []
                mock_repo_cls.return_value = mock_repo
                mock_gate_cls.return_value = MagicMock()
                register_boot_cron_jobs(scheduler, orchestrator, tmp_path)

        esc_cb = captured_callbacks.get("task_escalation_check")
        if esc_cb is not None:
            esc_cb()

    def test_daily_code_dedup_submits_dag(self, tmp_path):
        scheduler = MagicMock()
        orchestrator = MagicMock()
        captured_callbacks = {}

        def _capture(hour, name, layer, callback=None):
            captured_callbacks[name] = callback

        scheduler.register_task.side_effect = _capture

        with patch("zephyr.trading.boot_cron_jobs.TaskRepository", create=True) as mock_repo_cls:
            with patch("zephyr.trading.boot_cron_jobs.TaskCompletionGate", create=True) as mock_gate_cls:
                mock_repo_cls.return_value = MagicMock()
                mock_gate_cls.return_value = MagicMock()
                register_boot_cron_jobs(scheduler, orchestrator, tmp_path)

        dedup_cb = captured_callbacks.get("daily-code-dedup")
        assert dedup_cb is not None
        dedup_cb()
        orchestrator.submit_dag.assert_called_once_with("daily-code-dedup")
