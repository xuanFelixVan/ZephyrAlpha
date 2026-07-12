# [A_test] module_id: SRC-TST-1201 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_known_unknown_registry
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.collectors.known_unknown_registry
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_known_unknown_registry.py
# [TTL] task_bound

from zephyr.feedback_loop.collectors.known_unknown_registry import (
    KnownUnknown,
    KnownUnknownRegistry,
    KnownUnknownState,
)


class TestKnownUnknownStateEnum:
    def test_open_value(self):
        assert KnownUnknownState.OPEN == "OPEN"

    def test_mitigated_value(self):
        assert KnownUnknownState.MITIGATED == "MITIGATED"

    def test_accepted_value(self):
        assert KnownUnknownState.ACCEPTED == "ACCEPTED"


class TestKnownUnknownInstantiation:
    def test_default_state_is_open(self):
        ku = KnownUnknown(id="KU-001", domain="risk", description="unknown risk factor")
        assert ku.state == KnownUnknownState.OPEN

    def test_default_last_reviewed_empty(self):
        ku = KnownUnknown(id="KU-001", domain="risk", description="test")
        assert ku.last_reviewed == ""

    def test_explicit_state(self):
        ku = KnownUnknown(
            id="KU-002",
            domain="market",
            description="test",
            state=KnownUnknownState.ACCEPTED,
        )
        assert ku.state == KnownUnknownState.ACCEPTED


class TestKnownUnknownRegistryInstantiation:
    def test_default_empty_items(self):
        reg = KnownUnknownRegistry()
        assert reg.items == []

    def test_explicit_items(self):
        ku = KnownUnknown(id="KU-001", domain="risk", description="test")
        reg = KnownUnknownRegistry(items=[ku])
        assert len(reg.items) == 1


class TestKnownUnknownRegistryRegister:
    def test_register_returns_known_unknown(self):
        reg = KnownUnknownRegistry()
        item = reg.register("KU-001", "risk", "unknown risk factor")
        assert isinstance(item, KnownUnknown)
        assert item.id == "KU-001"
        assert item.domain == "risk"
        assert item.description == "unknown risk factor"
        assert item.state == KnownUnknownState.OPEN

    def test_register_appends_to_items(self):
        reg = KnownUnknownRegistry()
        reg.register("KU-001", "risk", "first")
        reg.register("KU-002", "market", "second")
        assert len(reg.items) == 2


class TestKnownUnknownRegistryOpenCount:
    def test_open_count_empty_registry(self):
        reg = KnownUnknownRegistry()
        assert reg.open_count() == 0

    def test_open_count_all_open(self):
        reg = KnownUnknownRegistry()
        reg.register("KU-001", "risk", "a")
        reg.register("KU-002", "market", "b")
        assert reg.open_count() == 2

    def test_open_count_mixed_states(self):
        reg = KnownUnknownRegistry()
        reg.register("KU-001", "risk", "a")
        item2 = reg.register("KU-002", "market", "b")
        item2.state = KnownUnknownState.MITIGATED
        assert reg.open_count() == 1

    def test_open_count_all_mitigated(self):
        reg = KnownUnknownRegistry()
        item = reg.register("KU-001", "risk", "a")
        item.state = KnownUnknownState.MITIGATED
        assert reg.open_count() == 0


class TestKnownUnknownRegistryByDomain:
    def test_by_domain_empty_registry(self):
        reg = KnownUnknownRegistry()
        assert reg.by_domain("risk") == []

    def test_by_domain_filters_correctly(self):
        reg = KnownUnknownRegistry()
        reg.register("KU-001", "risk", "a")
        reg.register("KU-002", "market", "b")
        reg.register("KU-003", "risk", "c")
        result = reg.by_domain("risk")
        assert len(result) == 2
        assert all(i.domain == "risk" for i in result)

    def test_by_domain_no_match(self):
        reg = KnownUnknownRegistry()
        reg.register("KU-001", "risk", "a")
        assert reg.by_domain("nonexistent") == []
