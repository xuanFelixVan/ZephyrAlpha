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
    """定时调度已废除（2026-06-26裁定）：register_boot_cron_jobs 仅保留事件订阅
    （bus.subscribe skill.freshness_critical）。以下测试验证事件驱动行为和容错性。"""

    def test_subscribes_freshness_event(self, tmp_path):
        """subscribe skill.freshness_critical 事件（事件驱动入口）。"""
        orchestrator = MagicMock()
        with patch("zephyr.shared.event_bus.bus") as mock_bus:
            register_boot_cron_jobs(orchestrator, tmp_path)
            mock_bus.subscribe.assert_called_once()
            event_name = mock_bus.subscribe.call_args.args[0]
            assert event_name == "skill.freshness_critical"

    def test_failure_does_not_raise(self, tmp_path):
        """bus.subscribe 失败时不抛异常（容错）。"""
        orchestrator = MagicMock()
        with patch("zephyr.shared.event_bus.bus") as mock_bus:
            mock_bus.subscribe.side_effect = RuntimeError("broken")
            # Should not raise
            register_boot_cron_jobs(orchestrator, tmp_path)
