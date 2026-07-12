# [A_test] module_id: SRC-TST-1482 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_rollback_integrity
# [INVARIANTS] verify returns True iff pre_state == post_rollback
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_rollback_integrity.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.verifiers.rollback_integrity import RollbackIntegrity


class TestRollbackIntegrityInstantiation:
    def test_default_construction(self):
        ri = RollbackIntegrity()
        assert ri is not None


class TestVerify:
    def test_matching_states(self):
        ri = RollbackIntegrity()
        state = {"cpu": 80.0, "mem": 60.0}
        assert ri.verify(state, state) is True

    def test_different_states(self):
        ri = RollbackIntegrity()
        pre = {"cpu": 80.0, "mem": 60.0}
        post = {"cpu": 90.0, "mem": 60.0}
        assert ri.verify(pre, post) is False

    def test_empty_dicts(self):
        ri = RollbackIntegrity()
        assert ri.verify({}, {}) is True

    def test_nested_dicts_match(self):
        ri = RollbackIntegrity()
        state = {"level1": {"level2": "value"}}
        assert ri.verify(state, state) is True

    def test_nested_dicts_differ(self):
        ri = RollbackIntegrity()
        pre = {"level1": {"level2": "value-a"}}
        post = {"level1": {"level2": "value-b"}}
        assert ri.verify(pre, post) is False

    def test_extra_key_in_post(self):
        ri = RollbackIntegrity()
        pre = {"a": 1}
        post = {"a": 1, "b": 2}
        assert ri.verify(pre, post) is False
