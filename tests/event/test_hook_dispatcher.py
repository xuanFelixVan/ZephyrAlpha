# [A_test] module_id: SRC-TST-1098 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-393 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_hook_dispatcher
# [INVARIANTS] HookDispatcher must dispatch registered hooks on matching events
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from zephyr.shared.events.hook_dispatcher import HookConfig, HookDispatcher, HookExecution
from zephyr.shared.event_bus import EventBus, EventType


class TestHookConfig:
    def test_instantiation_defaults(self):
        cfg = HookConfig(hook_id="HK-1", event_type=EventType.TASK_COMPLETED)
        assert cfg.hook_id == "HK-1"
        assert cfg.event_type == EventType.TASK_COMPLETED
        assert cfg.callback_url == ""
        assert cfg.callback_script == ""
        assert cfg.enabled is True
        assert cfg.max_retries == 3

    def test_instantiation_with_all_fields(self):
        cfg = HookConfig(
            hook_id="HK-2",
            event_type=EventType.TASK_FAILED,
            callback_url="https://example.com/hook",
            callback_script="echo hello",
            enabled=False,
            max_retries=5,
        )
        assert cfg.callback_url == "https://example.com/hook"
        assert cfg.callback_script == "echo hello"
        assert cfg.enabled is False
        assert cfg.max_retries == 5


class TestHookExecution:
    def test_instantiation(self):
        ex = HookExecution(
            hook_id="HK-1",
            event_id="EV-1",
            success=True,
            response="ok",
            timestamp_utc="2026-01-01T00:00:00+00:00",
        )
        assert ex.hook_id == "HK-1"
        assert ex.success is True
        assert ex.response == "ok"


class TestHookDispatcher:
    def test_instantiation_with_explicit_bus(self, tmp_path):
        bus = EventBus()
        dispatcher = HookDispatcher(event_bus=bus, data_dir=tmp_path)
        assert dispatcher._bus is bus
        assert dispatcher._data_dir == tmp_path

    def test_register_hook(self, tmp_path):
        bus = EventBus()
        dispatcher = HookDispatcher(event_bus=bus, data_dir=tmp_path)
        hook = HookConfig(hook_id="HK-REG", event_type=EventType.TASK_COMPLETED)
        dispatcher.register_hook(hook)
        assert hook in dispatcher._hooks[EventType.TASK_COMPLETED]

    def test_register_multiple_hooks_same_type(self, tmp_path):
        bus = EventBus()
        dispatcher = HookDispatcher(event_bus=bus, data_dir=tmp_path)
        h1 = HookConfig(hook_id="HK-A", event_type=EventType.TASK_COMPLETED)
        h2 = HookConfig(hook_id="HK-B", event_type=EventType.TASK_COMPLETED)
        dispatcher.register_hook(h1)
        dispatcher.register_hook(h2)
        assert len(dispatcher._hooks[EventType.TASK_COMPLETED]) == 2

    def test_script_hook_dispatches_on_task_completed(self, tmp_path):
        bus = EventBus()
        dispatcher = HookDispatcher(event_bus=bus, data_dir=tmp_path)
        hook = HookConfig(
            hook_id="HK-SCRIPT",
            event_type=EventType.TASK_COMPLETED,
            callback_script="python -c \"print('done')\"",
        )
        dispatcher.register_hook(hook)
        bus.publish(EventType.TASK_COMPLETED, "TASK-100")
        executions = dispatcher.get_executions()
        assert len(executions) == 1
        assert executions[0].hook_id == "HK-SCRIPT"
        assert executions[0].success is True

    def test_script_hook_dispatches_on_task_failed(self, tmp_path):
        bus = EventBus()
        dispatcher = HookDispatcher(event_bus=bus, data_dir=tmp_path)
        hook = HookConfig(
            hook_id="HK-FAIL",
            event_type=EventType.TASK_FAILED,
            callback_script="python -c \"print('fail-handled')\"",
        )
        dispatcher.register_hook(hook)
        bus.publish(EventType.TASK_FAILED, "TASK-200")
        executions = dispatcher.get_executions()
        assert len(executions) == 1
        assert executions[0].hook_id == "HK-FAIL"

    def test_disabled_hook_not_dispatched(self, tmp_path):
        bus = EventBus()
        dispatcher = HookDispatcher(event_bus=bus, data_dir=tmp_path)
        hook = HookConfig(
            hook_id="HK-DIS",
            event_type=EventType.TASK_COMPLETED,
            callback_script="python -c \"print('should-not-run')\"",
            enabled=False,
        )
        dispatcher.register_hook(hook)
        bus.publish(EventType.TASK_COMPLETED, "TASK-300")
        assert dispatcher.get_executions() == []

    def test_unregistered_event_type_no_dispatch(self, tmp_path):
        bus = EventBus()
        dispatcher = HookDispatcher(event_bus=bus, data_dir=tmp_path)
        hook = HookConfig(
            hook_id="HK-UNREG",
            event_type=EventType.TASK_COMPLETED,
            callback_script="python -c \"print('x')\"",
        )
        dispatcher.register_hook(hook)
        bus.publish(EventType.TASK_CREATED, "TASK-400")
        assert dispatcher.get_executions() == []

    def test_get_executions_filtered_by_hook_id(self, tmp_path):
        bus = EventBus()
        dispatcher = HookDispatcher(event_bus=bus, data_dir=tmp_path)
        h1 = HookConfig(
            hook_id="HK-F1", event_type=EventType.TASK_COMPLETED, callback_script="python -c \"print('a')\""
        )
        h2 = HookConfig(hook_id="HK-F2", event_type=EventType.TASK_FAILED, callback_script="python -c \"print('b')\"")
        dispatcher.register_hook(h1)
        dispatcher.register_hook(h2)
        bus.publish(EventType.TASK_COMPLETED, "TASK-500")
        bus.publish(EventType.TASK_FAILED, "TASK-501")
        filtered = dispatcher.get_executions(hook_id="HK-F1")
        assert len(filtered) == 1
        assert filtered[0].hook_id == "HK-F1"

    def test_get_executions_returns_all(self, tmp_path):
        bus = EventBus()
        dispatcher = HookDispatcher(event_bus=bus, data_dir=tmp_path)
        h1 = HookConfig(
            hook_id="HK-G1", event_type=EventType.TASK_COMPLETED, callback_script="python -c \"print('a')\""
        )
        h2 = HookConfig(hook_id="HK-G2", event_type=EventType.TASK_FAILED, callback_script="python -c \"print('b')\"")
        dispatcher.register_hook(h1)
        dispatcher.register_hook(h2)
        bus.publish(EventType.TASK_COMPLETED, "TASK-600")
        bus.publish(EventType.TASK_FAILED, "TASK-601")
        all_ex = dispatcher.get_executions()
        assert len(all_ex) == 2

    def test_failing_script_records_failure(self, tmp_path):
        bus = EventBus()
        dispatcher = HookDispatcher(event_bus=bus, data_dir=tmp_path)
        hook = HookConfig(
            hook_id="HK-BAD",
            event_type=EventType.TASK_COMPLETED,
            callback_script='python -c "raise SystemExit(1)"',
        )
        dispatcher.register_hook(hook)
        bus.publish(EventType.TASK_COMPLETED, "TASK-700")
        executions = dispatcher.get_executions()
        assert len(executions) == 1
        assert executions[0].success is False

    def test_webhook_hook_no_script_no_crash(self, tmp_path):
        bus = EventBus()
        dispatcher = HookDispatcher(event_bus=bus, data_dir=tmp_path)
        hook = HookConfig(
            hook_id="HK-WH",
            event_type=EventType.TASK_COMPLETED,
            callback_url="https://example.com/webhook",
        )
        dispatcher.register_hook(hook)
        bus.publish(EventType.TASK_COMPLETED, "TASK-800")
        executions = dispatcher.get_executions()
        assert len(executions) == 0
