# [A_test] module_id: SRC-TST-0569 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_config_hot_reload_guard
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.resilience.config_hot_reload_guard
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_config_hot_reload_guard.py
# [TTL] task_bound


from zephyr.feedback_loop.resilience.config_hot_reload_guard import (
    ConfigConsistency,
    ConfigHotReloadGuard,
)


class TestConfigHotReloadGuardInstantiation:
    def test_default_instantiation(self):
        guard = ConfigHotReloadGuard()
        assert guard.max_unacknowledged_seconds == 30.0
        assert guard.mandatory_consumers == []
        assert guard.current_config_hash == ""
        assert guard.config_timestamp == 0.0
        assert guard.consumer_acks == {}
        assert guard.change_events == []
        assert guard.cycle_active is False

    def test_custom_instantiation(self):
        guard = ConfigHotReloadGuard(
            max_unacknowledged_seconds=60.0,
            mandatory_consumers=["detector", "diagnoser"],
        )
        assert guard.max_unacknowledged_seconds == 60.0
        assert guard.mandatory_consumers == ["detector", "diagnoser"]


class TestComputeConfigHash:
    def test_deterministic_hash(self):
        guard = ConfigHotReloadGuard()
        cfg = {"threshold": 0.9, "mode": "strict"}
        h1 = guard.compute_config_hash(cfg)
        h2 = guard.compute_config_hash(cfg)
        assert h1 == h2
        assert isinstance(h1, str)
        assert len(h1) == 64

    def test_different_configs_different_hashes(self):
        guard = ConfigHotReloadGuard()
        h1 = guard.compute_config_hash({"a": 1})
        h2 = guard.compute_config_hash({"a": 2})
        assert h1 != h2

    def test_empty_dict_hash(self):
        guard = ConfigHotReloadGuard()
        h = guard.compute_config_hash({})
        assert isinstance(h, str)
        assert len(h) == 64


class TestRegisterConfig:
    def test_register_returns_consistent(self):
        guard = ConfigHotReloadGuard()
        result = guard.register_config({"key": "value"})
        assert result["consistency"] == ConfigConsistency.CONSISTENT.value
        assert "config_hash" in result
        assert result["action"] == "propagate_to_consumers"

    def test_register_mid_cycle_returns_mid_cycle_change(self):
        guard = ConfigHotReloadGuard()
        guard.register_config({"v": 1})
        guard.mark_cycle_start()
        result = guard.register_config({"v": 2})
        assert result["consistency"] == ConfigConsistency.MID_CYCLE_CHANGE.value
        assert result["action"] == "defer_to_cycle_boundary"

    def test_register_same_config_mid_cycle_is_consistent(self):
        guard = ConfigHotReloadGuard()
        cfg = {"v": 1}
        guard.register_config(cfg)
        guard.mark_cycle_start()
        result = guard.register_config(cfg)
        assert result["consistency"] == ConfigConsistency.CONSISTENT.value


class TestConsumerAcknowledge:
    def test_ack_with_all_mandatory_returns_consistent(self):
        guard = ConfigHotReloadGuard(mandatory_consumers=["a", "b"])
        result = guard.register_config({"x": 1})
        cfg_hash = guard.current_config_hash
        r1 = guard.consumer_acknowledge("a", cfg_hash)
        assert r1["consistency"] == ConfigConsistency.PARTIAL_ACK.value
        r2 = guard.consumer_acknowledge("b", cfg_hash)
        assert r2["consistency"] == ConfigConsistency.CONSISTENT.value
        assert r2["all_acknowledged"] is True

    def test_ack_with_wrong_hash_returns_conflict(self):
        guard = ConfigHotReloadGuard(mandatory_consumers=["a"])
        guard.register_config({"x": 1})
        result = guard.consumer_acknowledge("a", "wrong_hash")
        assert result["consistency"] == ConfigConsistency.CONFLICT.value

    def test_ack_no_mandatory_consumers(self):
        guard = ConfigHotReloadGuard()
        guard.register_config({"x": 1})
        result = guard.consumer_acknowledge("any", guard.current_config_hash)
        assert result["consistency"] == ConfigConsistency.CONSISTENT.value


class TestCheckStaleAcks:
    def test_no_stale_acks(self):
        guard = ConfigHotReloadGuard(max_unacknowledged_seconds=9999)
        guard.register_config({"x": 1})
        guard.consumer_acknowledge("a", guard.current_config_hash)
        assert guard.check_stale_acks() == []

    def test_stale_ack_detected(self):
        guard = ConfigHotReloadGuard(max_unacknowledged_seconds=-1)
        guard.register_config({"x": 1})
        guard.consumer_acknowledge("a", guard.current_config_hash)
        stale = guard.check_stale_acks()
        assert "a" in stale


class TestGetConfigLineage:
    def test_lineage_returns_list(self):
        guard = ConfigHotReloadGuard()
        guard.register_config({"x": 1})
        lineage = guard.get_config_lineage()
        assert isinstance(lineage, list)
        assert len(lineage) == 1
        assert lineage[0]["consumers_acked"] == 0

    def test_lineage_empty_hash_shows_none(self):
        guard = ConfigHotReloadGuard()
        lineage = guard.get_config_lineage()
        assert lineage[0]["hash"] == "none"


class TestOverallConfigHealth:
    def test_no_mandatory_returns_one(self):
        guard = ConfigHotReloadGuard()
        assert guard.overall_config_health() == 1.0

    def test_all_acked_returns_one(self):
        guard = ConfigHotReloadGuard(mandatory_consumers=["a"])
        guard.register_config({"x": 1})
        guard.consumer_acknowledge("a", guard.current_config_hash)
        assert guard.overall_config_health() == 1.0

    def test_partial_ack_returns_fraction(self):
        guard = ConfigHotReloadGuard(mandatory_consumers=["a", "b"])
        guard.register_config({"x": 1})
        guard.consumer_acknowledge("a", guard.current_config_hash)
        assert guard.overall_config_health() == 0.5


class TestCycleMarkers:
    def test_mark_cycle_start_end(self):
        guard = ConfigHotReloadGuard()
        guard.mark_cycle_start()
        assert guard.cycle_active is True
        guard.mark_cycle_end()
        assert guard.cycle_active is False
