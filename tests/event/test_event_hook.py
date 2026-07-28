# [A_test] module_id: MOD-GOV_event_hook | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §
# [MODULE] tests.test_event_hook
# [INVARIANTS] test_register_and_fire;test_priority_order;test_unregister;test_exception_isolation
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.ExitCode
# [TESTS] test_event_hook.py
# [TTL] task_bound


from zephyr.governance.ops_governance.event_hook import HookRegistry, TransitionEvent, hook_registry


class TestTransitionEvent:
    def test_creation_with_required_fields(self):
        event = TransitionEvent(task_id="DW-001", from_status="PENDING", to_status="IN_PROGRESS", note="started")
        assert event.task_id == "DW-001"
        assert event.from_status == "PENDING"
        assert event.to_status == "IN_PROGRESS"
        assert event.note == "started"
        assert event.session_id is None
        assert event.metadata == {}

    def test_creation_with_all_fields(self):
        event = TransitionEvent(
            task_id="DW-002",
            from_status="IN_PROGRESS",
            to_status="COMPLETED",
            note="done",
            session_id="session-001",
            metadata={"key": "val"},
        )
        assert event.session_id == "session-001"
        assert event.metadata == {"key": "val"}


class TestHookRegistry:
    def test_instantiation(self):
        registry = HookRegistry()
        assert registry.hooks == []
        assert registry.active is True

    def test_register_and_fire(self):
        registry = HookRegistry()
        received = []
        registry.register(lambda e: received.append(e.task_id), name="cb1")
        event = TransitionEvent(task_id="DW-100", from_status="A", to_status="B", note="")
        registry.fire(event)
        assert received == ["DW-100"]

    def test_priority_order(self):
        registry = HookRegistry()
        order = []
        registry.register(lambda e: order.append("low"), priority=200, name="low")
        registry.register(lambda e: order.append("high"), priority=10, name="high")
        registry.register(lambda e: order.append("mid"), priority=100, name="mid")
        event = TransitionEvent(task_id="DW-101", from_status="A", to_status="B", note="")
        registry.fire(event)
        assert order == ["high", "mid", "low"]

    def test_unregister(self):
        registry = HookRegistry()

        def cb(e):
            pass

        registry.register(cb, name="removable")
        assert len(registry.hooks) == 1
        result = registry.unregister(cb)
        assert result is True
        assert len(registry.hooks) == 0

    def test_unregister_not_found(self):
        registry = HookRegistry()
        result = registry.unregister(lambda e: None)
        assert result is False

    def test_clear(self):
        registry = HookRegistry()
        registry.register(lambda e: None, name="a")
        registry.register(lambda e: None, name="b")
        registry.clear()
        assert len(registry.hooks) == 0

    def test_exception_isolation(self):
        registry = HookRegistry()
        results = []

        def bad_cb(e):
            raise RuntimeError("boom")

        def good_cb(e):
            results.append(e.task_id)

        registry.register(bad_cb, priority=1, name="bad")
        registry.register(good_cb, priority=2, name="good")
        event = TransitionEvent(task_id="DW-102", from_status="A", to_status="B", note="")
        registry.fire(event)
        assert results == ["DW-102"]

    def test_suspend_and_resume(self):
        registry = HookRegistry()
        received = []
        registry.register(lambda e: received.append(e.task_id), name="cb")
        event = TransitionEvent(task_id="DW-103", from_status="A", to_status="B", note="")
        registry.suspend()
        registry.fire(event)
        assert received == []
        registry.resume()
        registry.fire(event)
        assert received == ["DW-103"]

    def test_get_all(self):
        registry = HookRegistry()
        registry.register(lambda e: None, priority=10, name="alpha")
        registry.register(lambda e: None, priority=20, name="beta")
        names = registry.get_all()
        assert len(names) == 2
        assert "alpha(prio=10)" in names
        assert "beta(prio=20)" in names

    def test_fire_with_no_hooks(self):
        registry = HookRegistry()
        event = TransitionEvent(task_id="DW-104", from_status="A", to_status="B", note="")
        registry.fire(event)

    def test_singleton_exists(self):
        assert isinstance(hook_registry, HookRegistry)
