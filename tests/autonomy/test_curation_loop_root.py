# [A_test] module_id: MOD-GOV_curation_loop_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.curation_loop
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.autonomy_core.context.curation_loop import CurationLoop, CurationRecord
except Exception as exc:
    pytest.skip(f"无法导入 curation_loop: {exc}", allow_module_level=True)


class TestCurationLoop:
    def setup_method(self):
        self.loop = CurationLoop()

    def test_select_ke_first_turn_returns_all(self):
        result = self.loop.select_ke(["KE-001", "KE-002", "KE-003"], turn=1)
        assert result == ["KE-001", "KE-002", "KE-003"]

    def test_select_ke_deduplicates_across_turns(self):
        self.loop.select_ke(["KE-001", "KE-002", "KE-003"], turn=1)
        result = self.loop.select_ke(["KE-001", "KE-004"], turn=2)
        assert "KE-001" not in result
        assert "KE-004" in result

    def test_select_ke_empty_list(self):
        result = self.loop.select_ke([], turn=1)
        assert result == []

    def test_select_ke_all_already_seen(self):
        self.loop.select_ke(["KE-001", "KE-002"], turn=1)
        result = self.loop.select_ke(["KE-001", "KE-002"], turn=2)
        assert result == []

    def test_get_history_returns_records(self):
        self.loop.select_ke(["KE-001"], turn=1)
        self.loop.select_ke(["KE-002"], turn=2)
        history = self.loop.get_history()
        assert 1 in history
        assert 2 in history
        assert isinstance(history[1], CurationRecord)
        assert history[1].injected_ke_ids == ["KE-001"]
        assert history[2].injected_ke_ids == ["KE-002"]

    def test_reset_clears_history(self):
        self.loop.select_ke(["KE-001"], turn=1)
        self.loop.reset()
        history = self.loop.get_history()
        assert history == {}

    def test_select_ke_after_reset_injects_again(self):
        self.loop.select_ke(["KE-001"], turn=1)
        self.loop.reset()
        result = self.loop.select_ke(["KE-001"], turn=1)
        assert "KE-001" in result

    def test_select_ke_non_sequential_turns(self):
        self.loop.select_ke(["KE-001"], turn=1)
        result = self.loop.select_ke(["KE-001", "KE-002"], turn=5)
        assert "KE-001" not in result
        assert "KE-002" in result
