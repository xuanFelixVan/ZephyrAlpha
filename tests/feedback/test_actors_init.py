# [A_test] module_id: SRC-TST-0270 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_actors_init
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_actors_init.py -q
# [TTL] task_bound

from zephyr.feedback_loop.actors import __all__


class TestActorsInitInstantiation:
    def test_all_is_list(self):
        assert isinstance(__all__, list)

    def test_all_not_empty(self):
        assert len(__all__) > 0

    def test_all_entries_are_strings(self):
        for entry in __all__:
            assert isinstance(entry, str)


class TestAllExports:
    def test_alert_router_in_all(self):
        assert "alert_router" in __all__

    def test_saga_compensator_in_all(self):
        assert "saga_compensator" in __all__

    def test_notification_personalizer_in_all(self):
        assert "notification_personalizer" in __all__

    def test_intent_driven_ops_in_all(self):
        assert "intent_driven_ops" in __all__

    def test_multi_agent_orchestrator_in_all(self):
        assert "multi_agent_orchestrator" in __all__

    def test_agent_lifecycle_in_all(self):
        assert "agent_lifecycle" in __all__

    def test_action_selector_in_all(self):
        assert "action_selector" in __all__

    def test_global_action_scheduler_in_all(self):
        assert "global_action_scheduler" in __all__

    def test_owner_absence_escalation_in_all(self):
        assert "owner_absence_escalation" in __all__

    def test_secondary_alert_channel_in_all(self):
        assert "secondary_alert_channel" in __all__

    def test_incident_priority_triage_automator_in_all(self):
        assert "incident_priority_triage_automator" in __all__

    def test_api_version_contract_in_all(self):
        assert "api_version_contract" in __all__


class TestModuleImportability:
    def test_alert_router_importable(self):
        from zephyr.feedback_loop.actors import alert_router

        assert alert_router is not None

    def test_saga_compensator_importable(self):
        from zephyr.feedback_loop.actors import saga_compensator

        assert saga_compensator is not None

    def test_agent_lifecycle_importable(self):
        from zephyr.feedback_loop.actors import agent_lifecycle

        assert agent_lifecycle is not None


class TestAllConsistency:
    def test_all_count_matches_expected(self):
        assert len(__all__) == 12

    def test_no_duplicates_in_all(self):
        assert len(__all__) == len(set(__all__))

    def test_all_entries_follow_naming_convention(self):
        for entry in __all__:
            assert entry.islower(), f"Entry {entry} should be lowercase"
            assert "_" in entry or entry.isalpha(), f"Entry {entry} should use snake_case"
