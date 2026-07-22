# [A_test] module_id: MOD-GOV_boot_hooks | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] tests.test_boot_hooks
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_boot_hooks.py
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock, patch

from zephyr.trading.boot_hooks import register_boot_hooks

_HOOK_REGISTRY_PATH = "zephyr.governance.event_hook.hook_registry"
_TASK_REPO_PATH = "zephyr.governance.persistence.task_repo.TaskRepository"


class TestRegisterBootHooks:
    def test_registers_three_hooks(self):
        mock_registry = MagicMock()
        with patch(_HOOK_REGISTRY_PATH, mock_registry), patch(_TASK_REPO_PATH, create=True):
            register_boot_hooks()
        assert mock_registry.register.call_count >= 3
        names = [call.kwargs.get("name", "") for call in mock_registry.register.call_args_list]
        assert "auto_unblock_dependents" in names
        assert "auto_retry_on_failure" in names
        assert "triple_alignment_on_verified" in names

    def test_hook_priorities(self):
        mock_registry = MagicMock()
        with patch(_HOOK_REGISTRY_PATH, mock_registry), patch(_TASK_REPO_PATH, create=True):
            register_boot_hooks()
        priorities = {
            call.kwargs.get("name", ""): call.kwargs.get("priority", 0)
            for call in mock_registry.register.call_args_list
        }
        assert priorities.get("auto_unblock_dependents") == 50
        assert priorities.get("auto_retry_on_failure") == 60
        assert priorities.get("triple_alignment_on_verified") == 70

    def test_failure_does_not_raise(self):
        with patch(_HOOK_REGISTRY_PATH, side_effect=ImportError("no hooks")):
            register_boot_hooks()

    def test_auto_unblock_callback_handles_exception(self):
        mock_registry = MagicMock()
        captured = {}

        def _capture(callback, *, priority=0, name=None):
            captured[name] = callback

        mock_registry.register.side_effect = _capture

        with patch(_HOOK_REGISTRY_PATH, mock_registry), patch(_TASK_REPO_PATH, create=True) as mock_repo_cls:
            mock_repo = MagicMock()
            mock_repo.list_by_dependency.side_effect = RuntimeError("db error")
            mock_repo_cls.return_value = mock_repo
            register_boot_hooks()

        cb = captured.get("auto_unblock_dependents")
        assert cb is not None
        event = MagicMock()
        event.task_id = "t1"
        cb(event)

    def test_auto_retry_callback_handles_missing_task(self):
        mock_registry = MagicMock()
        captured = {}

        def _capture(callback, *, priority=0, name=None):
            captured[name] = callback

        mock_registry.register.side_effect = _capture

        with patch(_HOOK_REGISTRY_PATH, mock_registry), patch(_TASK_REPO_PATH, create=True) as mock_repo_cls:
            mock_repo = MagicMock()
            mock_repo.get.return_value = None
            mock_repo_cls.return_value = mock_repo
            register_boot_hooks()

        cb = captured.get("auto_retry_on_failure")
        assert cb is not None
        event = MagicMock()
        event.task_id = "t2"
        cb(event)

    def test_ide_health_daemon_registration_attempted(self):
        mock_registry = MagicMock()
        with patch(_HOOK_REGISTRY_PATH, mock_registry), patch(_TASK_REPO_PATH, create=True):
            with patch("zephyr.trading.ide_health_daemon.register_daemon", create=True) as mock_daemon:
                register_boot_hooks()
                mock_daemon.assert_called_once()
