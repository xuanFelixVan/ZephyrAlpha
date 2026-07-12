# [A_test] module_id: SRC-TST-1557 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_self_ha
# [INVARIANTS] SelfHA.active_instance is str; standby_instances is list[str]
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_self_ha.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.self_ha import SelfHA


class TestSelfHAInstantiation:
    def test_default_active_instance(self):
        obj = SelfHA()
        assert obj.active_instance == "primary"

    def test_default_standby_empty(self):
        obj = SelfHA()
        assert obj.standby_instances == []

    def test_custom_active_instance(self):
        obj = SelfHA(active_instance="secondary")
        assert obj.active_instance == "secondary"

    def test_custom_standby_instances(self):
        obj = SelfHA(standby_instances=["backup-1", "backup-2"])
        assert obj.standby_instances == ["backup-1", "backup-2"]

    def test_standby_is_list_type(self):
        obj = SelfHA()
        assert isinstance(obj.standby_instances, list)


class TestSelfHAStandbyManagement:
    def test_add_standby_instance(self):
        obj = SelfHA()
        obj.standby_instances.append("backup-1")
        assert "backup-1" in obj.standby_instances

    def test_remove_standby_instance(self):
        obj = SelfHA(standby_instances=["backup-1", "backup-2"])
        obj.standby_instances.remove("backup-1")
        assert "backup-1" not in obj.standby_instances
        assert len(obj.standby_instances) == 1

    def test_separate_instances_independent(self):
        a = SelfHA()
        b = SelfHA()
        a.standby_instances.append("backup-a")
        assert len(b.standby_instances) == 0

    def test_failover_simulation(self):
        obj = SelfHA(standby_instances=["backup-1"])
        old_active = obj.active_instance
        obj.active_instance = obj.standby_instances[0]
        obj.standby_instances.remove(obj.active_instance)
        obj.standby_instances.append(old_active)
        assert obj.active_instance == "backup-1"
        assert old_active in obj.standby_instances
