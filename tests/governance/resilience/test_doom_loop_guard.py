# [A_test] module_id: SRC-TST-0762 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_doom_loop_guard
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
from zephyr.gov_code_quality.code_dedup.doom_loop_guard import (
    DoomLoopGuard,
)


class TestDoomLoopGuard:
    def test_instantiation_default(self):
        guard = DoomLoopGuard()
        assert guard is not None

    def test_instantiation_with_path(self, tmp_path):
        guard = DoomLoopGuard(freeze_path=str(tmp_path / "freeze.json"))
        assert guard is not None

    def test_escalate(self):
        guard = DoomLoopGuard()
        result = guard.escalate("group-001", current_level=0, reason="test")
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_is_frozen(self):
        guard = DoomLoopGuard()
        result = guard.is_frozen("group-001")
        assert isinstance(result, bool)

    def test_reset_group(self):
        guard = DoomLoopGuard()
        guard.escalate("group-001", current_level=0, reason="test")
        guard.reset_group("group-001")
        assert "group-001" not in guard._frozen

    def test_get_frozen_groups(self):
        guard = DoomLoopGuard()
        result = guard.get_frozen_groups()
        assert isinstance(result, list)

    def test_get_freeze_report(self):
        guard = DoomLoopGuard()
        result = guard.get_freeze_report()
        assert isinstance(result, dict)
