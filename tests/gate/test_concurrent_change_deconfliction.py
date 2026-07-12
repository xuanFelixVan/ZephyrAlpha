# [A_test] module_id: SRC-TST-0560 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_concurrent_change_deconfliction
# [INVARIANTS] Optimistic locking must reject version mismatches
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.concurrent_change_deconfliction import (
    ChangeSource,
    ConcurrentChangeDeconfliction,
)


class TestChangeSource:
    def test_enum_values(self):
        assert ChangeSource.OWNER == "OWNER"
        assert ChangeSource.FLE == "FLE"
        assert ChangeSource.EXTERNAL == "EXTERNAL"


class TestConcurrentChangeDeconflictionInstantiation:
    def test_default_values(self):
        ccd = ConcurrentChangeDeconfliction()
        assert ccd.resource_versions == {}
        assert ccd.resolution_log == []
        assert ccd.conflict_grace_period == 5.0


class TestAttempt:
    def test_first_attempt_succeeds(self):
        ccd = ConcurrentChangeDeconfliction()
        result = ccd.attempt(ChangeSource.OWNER, "config.yaml", 0)
        assert result is True
        assert ccd.resource_versions["config.yaml"] == 1

    def test_version_mismatch_fails(self):
        ccd = ConcurrentChangeDeconfliction()
        ccd.attempt(ChangeSource.OWNER, "config.yaml", 0)
        result = ccd.attempt(ChangeSource.FLE, "config.yaml", 0)
        assert result is False

    def test_correct_version_succeeds(self):
        ccd = ConcurrentChangeDeconfliction()
        ccd.attempt(ChangeSource.OWNER, "config.yaml", 0)
        result = ccd.attempt(ChangeSource.FLE, "config.yaml", 1)
        assert result is True

    def test_log_records_accepted(self):
        ccd = ConcurrentChangeDeconfliction()
        ccd.attempt(ChangeSource.OWNER, "config.yaml", 0)
        assert ccd.resolution_log[0].accepted is True

    def test_log_records_rejected(self):
        ccd = ConcurrentChangeDeconfliction()
        ccd.attempt(ChangeSource.OWNER, "config.yaml", 0)
        ccd.attempt(ChangeSource.FLE, "config.yaml", 0)
        assert ccd.resolution_log[1].accepted is False

    def test_multiple_resources_independent(self):
        ccd = ConcurrentChangeDeconfliction()
        r1 = ccd.attempt(ChangeSource.OWNER, "a.yaml", 0)
        r2 = ccd.attempt(ChangeSource.OWNER, "b.yaml", 0)
        assert r1 is True
        assert r2 is True


class TestRecentConflicts:
    def test_no_conflicts(self):
        ccd = ConcurrentChangeDeconfliction()
        ccd.attempt(ChangeSource.OWNER, "config.yaml", 0)
        assert ccd.recent_conflicts() == []

    def test_recent_conflict_found(self):
        ccd = ConcurrentChangeDeconfliction()
        ccd.attempt(ChangeSource.OWNER, "config.yaml", 0)
        ccd.attempt(ChangeSource.FLE, "config.yaml", 0)
        conflicts = ccd.recent_conflicts()
        assert len(conflicts) == 1
