# [A_test] module_id: SRC-TST-1685 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_state_migration_validator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.forensic.state_migration_validator
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_state_migration_validator.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.forensic.state_migration_validator import (
    MigrationResult,
    StateMigrationValidator,
)


class TestMigrationResult:
    def test_enum_values(self):
        assert MigrationResult.COMPATIBLE.value == "COMPATIBLE"
        assert MigrationResult.MIGRATED.value == "MIGRATED"
        assert MigrationResult.PARTIAL.value == "PARTIAL"
        assert MigrationResult.INCOMPATIBLE.value == "INCOMPATIBLE"


class TestStateMigrationValidator:
    def test_instantiation_defaults(self):
        smv = StateMigrationValidator()
        assert smv.max_divergence_pct == 1.0
        assert smv.min_baseline_samples == 100
        assert smv.state_snapshot_hashes == {}
        assert smv.migration_results == []
        assert smv.compatibility_map == {}

    def test_instantiation_custom(self):
        smv = StateMigrationValidator(max_divergence_pct=5.0, min_baseline_samples=50)
        assert smv.max_divergence_pct == 5.0
        assert smv.min_baseline_samples == 50

    def test_snapshot_creates_hash(self):
        smv = StateMigrationValidator()
        h = smv.snapshot("baseline-v1", b"state-data")
        assert len(h) == 16
        assert "baseline-v1" in smv.state_snapshot_hashes

    def test_snapshot_deterministic(self):
        smv1 = StateMigrationValidator()
        smv2 = StateMigrationValidator()
        h1 = smv1.snapshot("s1", b"same-data")
        h2 = smv2.snapshot("s1", b"same-data")
        assert h1 == h2

    def test_snapshot_different_data_different_hash(self):
        smv = StateMigrationValidator()
        h1 = smv.snapshot("s1", b"data-a")
        h2 = smv.snapshot("s2", b"data-b")
        assert h1 != h2

    def test_validate_migration_compatible(self):
        smv = StateMigrationValidator()
        old = {"threshold": 0.5, "mode": "auto"}
        new = {"threshold": 0.5, "mode": "auto"}
        result = smv.validate_migration("0.39", "0.40", "config", old, new)
        assert result["result"] == MigrationResult.COMPATIBLE.value
        assert result["recommendation"] == "proceed"
        assert result["divergence_pct"] == 0.0

    def test_validate_migration_incompatible(self):
        smv = StateMigrationValidator()
        old = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8, "i": 9, "j": 10}
        new = {"a": 99, "b": 99, "c": 99, "d": 99, "e": 99, "f": 99, "g": 99, "h": 99, "i": 99, "j": 99}
        result = smv.validate_migration("0.39", "0.40", "state", old, new)
        assert result["result"] == MigrationResult.INCOMPATIBLE.value
        assert result["recommendation"] == "rollback_and_investigate"

    def test_validate_migration_partial(self):
        smv = StateMigrationValidator(max_divergence_pct=10.0)
        old = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8, "i": 9, "j": 10}
        new = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8, "i": 99, "j": 10}
        result = smv.validate_migration("0.39", "0.40", "state", old, new)
        assert result["result"] in (
            MigrationResult.PARTIAL.value,
            MigrationResult.MIGRATED.value,
            MigrationResult.COMPATIBLE.value,
        )

    def test_validate_migration_migrated(self):
        smv = StateMigrationValidator(max_divergence_pct=50.0)
        old = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}
        new = {"a": 1, "b": 2, "c": 99, "d": 4, "e": 5}
        result = smv.validate_migration("0.39", "0.40", "state", old, new)
        assert result["result"] == MigrationResult.MIGRATED.value

    def test_validate_migration_empty_outputs(self):
        smv = StateMigrationValidator()
        result = smv.validate_migration("0.39", "0.40", "empty", {}, {})
        assert result["result"] == MigrationResult.COMPATIBLE.value

    def test_can_migrate_safely_no_test(self):
        smv = StateMigrationValidator()
        result = smv.can_migrate_safely("0.39", "0.40")
        assert result["safe"] is False
        assert result["reason"] == "no_migration_tested"

    def test_can_migrate_safely_all_compatible(self):
        smv = StateMigrationValidator()
        smv.validate_migration("0.39", "0.40", "s1", {"a": 1}, {"a": 1})
        result = smv.can_migrate_safely("0.39", "0.40")
        assert result["safe"] is True
        assert result["recommendation"] == "safe_to_upgrade"

    def test_can_migrate_safely_with_incompatible(self):
        smv = StateMigrationValidator()
        smv.validate_migration("0.39", "0.40", "s1", {"a": 1}, {"a": 1})
        smv.validate_migration(
            "0.39",
            "0.40",
            "s2",
            {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8, "i": 9, "j": 10},
            {"a": 99, "b": 99, "c": 99, "d": 99, "e": 99, "f": 99, "g": 99, "h": 99, "i": 99, "j": 99},
        )
        result = smv.can_migrate_safely("0.39", "0.40")
        assert result["safe"] is False
        assert result["incompatible"] >= 1

    def test_get_migration_history(self):
        smv = StateMigrationValidator()
        smv.validate_migration("0.39", "0.40", "s1", {"a": 1}, {"a": 1})
        smv.validate_migration("0.40", "0.41", "s1", {"a": 1}, {"a": 2})
        history = smv.get_migration_history("0.39", "0.40")
        assert len(history) == 1
        assert history[0]["state_name"] == "s1"

    def test_get_migration_history_empty(self):
        smv = StateMigrationValidator()
        history = smv.get_migration_history("0.39", "0.40")
        assert len(history) == 0

    def test_overall_migration_health_perfect(self):
        smv = StateMigrationValidator()
        smv.validate_migration("0.39", "0.40", "s1", {"a": 1}, {"a": 1})
        assert smv.overall_migration_health() == 1.0

    def test_overall_migration_health_no_results(self):
        smv = StateMigrationValidator()
        assert smv.overall_migration_health() == 1.0

    def test_overall_migration_health_mixed(self):
        smv = StateMigrationValidator()
        smv.validate_migration("0.39", "0.40", "s1", {"a": 1}, {"a": 1})
        smv.validate_migration(
            "0.39",
            "0.40",
            "s2",
            {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8, "i": 9, "j": 10},
            {"a": 99, "b": 99, "c": 99, "d": 99, "e": 99, "f": 99, "g": 99, "h": 99, "i": 99, "j": 99},
        )
        health = smv.overall_migration_health()
        assert 0.0 <= health <= 1.0
