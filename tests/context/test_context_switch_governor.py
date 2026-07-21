# [A_test] module_id: MOD-GOV_context_switch_governor | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_context_switch_governor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_context_switch_governor.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.context_governance.context_switch_governor import ContextSwitchGovernor


class TestContextSwitchGovernorInstantiation:
    def test_create_instance(self):
        gov = ContextSwitchGovernor()
        assert gov is not None

    def test_initial_daily_switches_empty(self):
        gov = ContextSwitchGovernor()
        assert gov._daily_switches == {}

    def test_max_switches_per_owner(self):
        gov = ContextSwitchGovernor()
        assert gov._max_switches_per_owner == 12


class TestCanSwitch:
    def test_can_switch_initially(self):
        gov = ContextSwitchGovernor()
        assert gov.can_switch("owner_1") is True

    def test_can_switch_after_few_switches(self):
        gov = ContextSwitchGovernor()
        for _ in range(11):
            gov.record_switch("owner_1")
        assert gov.can_switch("owner_1") is True

    def test_cannot_switch_at_max(self):
        gov = ContextSwitchGovernor()
        for _ in range(12):
            gov.record_switch("owner_1")
        assert gov.can_switch("owner_1") is False

    def test_cannot_switch_over_max(self):
        gov = ContextSwitchGovernor()
        for _ in range(15):
            gov.record_switch("owner_1")
        assert gov.can_switch("owner_1") is False

    def test_boundary_exactly_max_minus_one(self):
        gov = ContextSwitchGovernor()
        for _ in range(11):
            gov.record_switch("owner_1")
        assert gov.can_switch("owner_1") is True

    def test_independent_owners(self):
        gov = ContextSwitchGovernor()
        for _ in range(12):
            gov.record_switch("owner_a")
        assert gov.can_switch("owner_a") is False
        assert gov.can_switch("owner_b") is True

    def test_unknown_owner_can_switch(self):
        gov = ContextSwitchGovernor()
        assert gov.can_switch("unknown_owner") is True


class TestRecordSwitch:
    def test_record_single_switch(self):
        gov = ContextSwitchGovernor()
        gov.record_switch("owner_1")
        assert gov._daily_switches["owner_1"] == 1

    def test_record_multiple_switches(self):
        gov = ContextSwitchGovernor()
        gov.record_switch("owner_1")
        gov.record_switch("owner_1")
        gov.record_switch("owner_1")
        assert gov._daily_switches["owner_1"] == 3

    def test_record_switches_different_owners(self):
        gov = ContextSwitchGovernor()
        gov.record_switch("owner_a")
        gov.record_switch("owner_b")
        assert gov._daily_switches["owner_a"] == 1
        assert gov._daily_switches["owner_b"] == 1

    def test_record_beyond_max_still_increments(self):
        gov = ContextSwitchGovernor()
        for _ in range(15):
            gov.record_switch("owner_1")
        assert gov._daily_switches["owner_1"] == 15

    def test_can_and_record_integration(self):
        gov = ContextSwitchGovernor()
        count = 0
        while gov.can_switch("owner_1"):
            gov.record_switch("owner_1")
            count += 1
        assert count == 12
