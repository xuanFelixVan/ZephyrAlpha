# [A_test] module_id: SRC-TST-0964 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_flag_lifecycle_manager
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.flag_lifecycle_manager
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_flag_lifecycle_manager.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.flag_lifecycle_manager import FlagLifecycleManager


class TestFlagLifecycleManagerInstantiation:
    def test_default_construction(self):
        flm = FlagLifecycleManager()
        assert flm.flags == {}


class TestRetire:
    def test_retire_marks_flag(self):
        flm = FlagLifecycleManager()
        flm.retire("feature-x")
        assert flm.flags["feature-x"] == "RETIRED"

    def test_retire_overwrites_active(self):
        flm = FlagLifecycleManager(flags={"feature-y": "ACTIVE"})
        flm.retire("feature-y")
        assert flm.flags["feature-y"] == "RETIRED"

    def test_retire_multiple_flags(self):
        flm = FlagLifecycleManager()
        flm.retire("flag-a")
        flm.retire("flag-b")
        assert len(flm.flags) == 2
        assert all(v == "RETIRED" for v in flm.flags.values())


class TestBoundaries:
    def test_retire_empty_string_flag(self):
        flm = FlagLifecycleManager()
        flm.retire("")
        assert flm.flags[""] == "RETIRED"
