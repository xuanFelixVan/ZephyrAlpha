# [A_test] module_id: MOD-GOV_trigger_monitor | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §
# [MODULE] tests.test_trigger_monitor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_trigger_monitor.py
# [TTL] task_bound

from zephyr.infrastructure.a2a_protocol.layer2_communication.trigger_monitor import TriggerMonitor


class TestTriggerMonitor:
    def test_create(self):
        tm = TriggerMonitor()
        assert tm._triggers == {}

    def test_watch_and_check(self):
        tm = TriggerMonitor()
        tm.watch("trig-1", lambda ctx: ctx.get("value", 0) > 10)
        assert tm.check("trig-1", {"value": 15}) is True
        assert tm.check("trig-1", {"value": 5}) is False

    def test_check_nonexistent_trigger(self):
        tm = TriggerMonitor()
        assert tm.check("missing", {}) is False

    def test_check_with_empty_context(self):
        tm = TriggerMonitor()
        tm.watch("trig-2", lambda ctx: bool(ctx))
        assert tm.check("trig-2", {}) is False
        assert tm.check("trig-2", {"key": "val"}) is True

    def test_multiple_triggers(self):
        tm = TriggerMonitor()
        tm.watch("t1", lambda ctx: ctx.get("a") == 1)
        tm.watch("t2", lambda ctx: ctx.get("b") == 2)
        assert tm.check("t1", {"a": 1}) is True
        assert tm.check("t2", {"a": 1}) is False

    def test_watch_overwrite(self):
        tm = TriggerMonitor()
        tm.watch("trig", lambda ctx: True)
        assert tm.check("trig", {}) is True
        tm.watch("trig", lambda ctx: False)
        assert tm.check("trig", {}) is False
