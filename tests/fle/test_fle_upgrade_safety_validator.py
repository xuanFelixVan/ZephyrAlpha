# [A_test] module_id: SRC-TST-1024 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fle_upgrade_safety_validator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.forensic.fle_upgrade_safety_validator
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fle_upgrade_safety_validator.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.forensic.fle_upgrade_safety_validator import (
    FLEUpgradeSafetyValidator,
    UpgradeSafetyResult,
)


class TestUpgradeSafetyResult:
    def test_creation(self):
        r = UpgradeSafetyResult(
            version_from="0.40.0",
            version_to="0.41.0",
            compatible=True,
            breaking_changes=[],
            state_compatibility={"thresholds": True},
        )
        assert r.compatible is True
        assert r.breaking_changes == []
        assert r.state_compatibility == {"thresholds": True}

    def test_creation_incompatible(self):
        r = UpgradeSafetyResult(
            version_from="0.40.0",
            version_to="0.41.0",
            compatible=False,
            breaking_changes=["schema_hash_mismatch"],
            state_compatibility={},
        )
        assert r.compatible is False
        assert len(r.breaking_changes) == 1


class TestFLEUpgradeSafetyValidator:
    def test_instantiation_defaults(self):
        v = FLEUpgradeSafetyValidator()
        assert v.current_version == "0.41.0"
        assert v.state_schema_hash == ""
        assert v.known_compatible_versions == set()
        assert v.upgrade_log == []

    def test_register_current_state_schema(self):
        v = FLEUpgradeSafetyValidator()
        schema = {"thresholds": {"max": 100}, "rules": []}
        h = v.register_current_state_schema(schema)
        assert len(h) == 16
        assert v.state_schema_hash == h
        assert v.current_version in v.known_compatible_versions

    def test_register_state_schema_deterministic(self):
        v1 = FLEUpgradeSafetyValidator()
        v2 = FLEUpgradeSafetyValidator()
        schema = {"key": "value"}
        h1 = v1.register_current_state_schema(schema)
        h2 = v2.register_current_state_schema(schema)
        assert h1 == h2

    def test_validate_upgrade_compatible(self):
        v = FLEUpgradeSafetyValidator()
        schema = {"thresholds": {}, "rules": {}}
        h = v.register_current_state_schema(schema)
        result = v.validate_upgrade(
            "0.42.0",
            h,
            ["thresholds", "rules", "baselines", "config_hashes", "guard_states", "cycle_count", "self_model"],
        )
        assert result["can_upgrade"] is True
        assert result["recommendation"] == "SAFE_TO_UPGRADE"

    def test_validate_upgrade_schema_mismatch(self):
        v = FLEUpgradeSafetyValidator()
        v.register_current_state_schema({"a": 1})
        result = v.validate_upgrade("0.42.0", "different_hash_1234", ["thresholds"])
        assert result["can_upgrade"] is False
        assert result["recommendation"] == "BLOCKED_breaking_changes"
        assert len(result["breaking_changes"]) > 0

    def test_validate_upgrade_missing_state_keys(self):
        v = FLEUpgradeSafetyValidator()
        schema = {"thresholds": {}}
        v.register_current_state_schema(schema)
        result = v.validate_upgrade("0.42.0", v.state_schema_hash, ["thresholds", "unknown_key"])
        assert result["can_upgrade"] is False
        assert any("missing_state_keys" in bc for bc in result["breaking_changes"])

    def test_validate_upgrade_all_expected_keys(self):
        v = FLEUpgradeSafetyValidator()
        schema = {"all": True}
        v.register_current_state_schema(schema)
        expected_keys = [
            "thresholds",
            "rules",
            "baselines",
            "config_hashes",
            "guard_states",
            "cycle_count",
            "self_model",
        ]
        result = v.validate_upgrade("0.42.0", v.state_schema_hash, expected_keys)
        assert result["can_upgrade"] is True
        assert result["state_keys_verified"] == 7

    def test_upgrade_log_capped(self):
        v = FLEUpgradeSafetyValidator()
        schema = {"x": 1}
        v.register_current_state_schema(schema)
        for i in range(25):
            v.validate_upgrade(f"0.{i}.0", v.state_schema_hash, ["thresholds"])
        assert len(v.upgrade_log) <= 20

    def test_record_successful_upgrade(self):
        v = FLEUpgradeSafetyValidator()
        v.record_successful_upgrade("0.42.0")
        assert v.current_version == "0.42.0"
        assert "0.42.0" in v.known_compatible_versions

    def test_validate_upgrade_empty_keys(self):
        v = FLEUpgradeSafetyValidator()
        schema = {"x": 1}
        v.register_current_state_schema(schema)
        result = v.validate_upgrade("0.42.0", v.state_schema_hash, [])
        assert result["can_upgrade"] is True
        assert result["state_keys_verified"] == 0
