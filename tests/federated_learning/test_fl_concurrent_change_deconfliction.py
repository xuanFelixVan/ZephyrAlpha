# [A_test] module_id: SRC-TST-0942 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_concurrent_change_deconfliction
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.concurrent_change_deconfliction
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_concurrent_change_deconfliction.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.concurrent_change_deconfliction import (
    ChangeSource,
    ConcurrentChangeDeconfliction,
)


class TestConcurrentChangeDeconflictionInstantiation:
    def test_default_construction(self):
        ccd = ConcurrentChangeDeconfliction()
        assert ccd.resource_versions == {}
        assert ccd.resolution_log == []
        assert ccd.conflict_grace_period == 5.0


class TestAttempt:
    def test_attempt_first_change_succeeds(self):
        ccd = ConcurrentChangeDeconfliction()
        assert ccd.attempt(ChangeSource.OWNER, "config.yaml", 0) is True
        assert ccd.resource_versions["config.yaml"] == 1

    def test_attempt_version_mismatch_fails(self):
        ccd = ConcurrentChangeDeconfliction()
        ccd.attempt(ChangeSource.OWNER, "config.yaml", 0)
        assert ccd.attempt(ChangeSource.FLE, "config.yaml", 0) is False

    def test_attempt_correct_version_succeeds(self):
        ccd = ConcurrentChangeDeconfliction()
        ccd.attempt(ChangeSource.OWNER, "config.yaml", 0)
        assert ccd.attempt(ChangeSource.FLE, "config.yaml", 1) is True

    def test_attempt_logs_accepted_and_rejected(self):
        ccd = ConcurrentChangeDeconfliction()
        ccd.attempt(ChangeSource.OWNER, "r1", 0)
        ccd.attempt(ChangeSource.FLE, "r1", 0)
        accepted = [a for a in ccd.resolution_log if a.accepted]
        rejected = [a for a in ccd.resolution_log if not a.accepted]
        assert len(accepted) == 1
        assert len(rejected) == 1


class TestRecentConflicts:
    def test_recent_conflicts_empty(self):
        ccd = ConcurrentChangeDeconfliction()
        assert ccd.recent_conflicts() == []

    def test_recent_conflicts_returns_rejected(self):
        ccd = ConcurrentChangeDeconfliction()
        ccd.attempt(ChangeSource.OWNER, "r1", 0)
        ccd.attempt(ChangeSource.FLE, "r1", 0)
        conflicts = ccd.recent_conflicts()
        assert len(conflicts) == 1


class TestBoundaries:
    def test_attempt_new_resource_from_zero(self):
        ccd = ConcurrentChangeDeconfliction()
        assert ccd.attempt(ChangeSource.EXTERNAL, "new_resource", 0) is True

    def test_attempt_wrong_initial_version(self):
        ccd = ConcurrentChangeDeconfliction()
        assert ccd.attempt(ChangeSource.OWNER, "r1", 5) is False
