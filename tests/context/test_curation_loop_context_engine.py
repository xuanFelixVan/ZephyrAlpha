# [A_test] module_id: MOD-GOV_curation_loop_context_engine | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-466 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.context_engine.test_curation_loop
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Tests for curation_loop.py (TASK-014 beta b)."""

from zephyr.autonomy_core.context.curation_loop import CurationLoop


class TestCurationLoop:
    def test_first_turn_all_ke(self):
        loop = CurationLoop()
        result = loop.select_ke(["KE-001", "KE-002"], turn=1)
        assert result == ["KE-001", "KE-002"]

    def test_second_turn_dedup(self):
        loop = CurationLoop()
        loop.select_ke(["KE-001", "KE-002"], turn=1)
        result = loop.select_ke(["KE-001", "KE-003"], turn=2)
        assert "KE-001" not in result
        assert "KE-003" in result

    def test_history(self):
        loop = CurationLoop()
        loop.select_ke(["KE-001"], turn=1)
        loop.select_ke(["KE-002"], turn=2)
        h = loop.get_history()
        assert len(h) == 2

    def test_reset(self):
        loop = CurationLoop()
        loop.select_ke(["KE-001"], turn=1)
        loop.reset()
        result = loop.select_ke(["KE-001"], turn=1)
        assert "KE-001" in result

    def test_multiple_turns(self):
        loop = CurationLoop()
        t1 = loop.select_ke(["KE-001"], turn=1)
        t2 = loop.select_ke(["KE-001", "KE-002"], turn=2)
        t3 = loop.select_ke(["KE-001", "KE-002", "KE-003"], turn=3)
        assert t1 == ["KE-001"]
        assert t2 == ["KE-002"]
        assert t3 == ["KE-003"]
