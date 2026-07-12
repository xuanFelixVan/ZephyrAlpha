# [A_test] module_id: SRC-TST-0940 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_checkpoint_manager
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.checkpoint_manager
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_checkpoint_manager.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.checkpoint_manager import CheckpointManager


class TestCheckpointManagerInstantiation:
    def test_default_construction(self):
        cm = CheckpointManager()
        assert cm.checkpoints == []


class TestSave:
    def test_save_returns_index(self):
        cm = CheckpointManager()
        idx = cm.save({"phase": "init"})
        assert idx == 0

    def test_save_multiple_returns_incrementing_index(self):
        cm = CheckpointManager()
        assert cm.save({"a": 1}) == 0
        assert cm.save({"b": 2}) == 1
        assert cm.save({"c": 3}) == 2

    def test_save_stores_copy(self):
        cm = CheckpointManager()
        state = {"key": "value"}
        cm.save(state)
        state["key"] = "modified"
        assert cm.checkpoints[0]["key"] == "value"


class TestBoundaries:
    def test_save_empty_dict(self):
        cm = CheckpointManager()
        idx = cm.save({})
        assert idx == 0
        assert cm.checkpoints[0] == {}

    def test_save_none_value_in_dict(self):
        cm = CheckpointManager()
        idx = cm.save({"key": None})
        assert idx == 0
        assert cm.checkpoints[0]["key"] is None
