# [A_test] module_id: SRC-TST-1008 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_flag_lifecycle_manager
# [INVARIANTS] Retired flags must be marked RETIRED
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.flag_lifecycle_manager import FlagLifecycleManager


class TestFlagLifecycleManagerInstantiation:
    def test_default_empty_flags(self):
        flm = FlagLifecycleManager()
        assert flm.flags == {}

    def test_custom_flags(self):
        flm = FlagLifecycleManager(flags={"flag-1": "ACTIVE"})
        assert flm.flags["flag-1"] == "ACTIVE"


class TestRetire:
    def test_retire_marks_flag(self):
        flm = FlagLifecycleManager()
        flm.retire("flag-1")
        assert flm.flags["flag-1"] == "RETIRED"

    def test_retire_overwrites_active(self):
        flm = FlagLifecycleManager(flags={"flag-1": "ACTIVE"})
        flm.retire("flag-1")
        assert flm.flags["flag-1"] == "RETIRED"

    def test_retire_multiple_flags(self):
        flm = FlagLifecycleManager()
        flm.retire("flag-1")
        flm.retire("flag-2")
        assert len(flm.flags) == 2
        assert flm.flags["flag-1"] == "RETIRED"
        assert flm.flags["flag-2"] == "RETIRED"

    def test_retire_idempotent(self):
        flm = FlagLifecycleManager()
        flm.retire("flag-1")
        flm.retire("flag-1")
        assert flm.flags["flag-1"] == "RETIRED"
