# [A_test] module_id: MOD-GOV_fl_generator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_generator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.generator
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_generator.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.generator import generate


class TestGenerate:
    def test_generates_new_files(self, tmp_path):
        skeletons = {"subdir/test_file.py": 'print("hello")\n'}
        # 治本（2026-08-18 第八统筹）：原调用 generate(skeletons) 不传目标根，
        # 泄漏 src/zephyr/feedback_loop/subdir/test_file.py 进真源树（ORPHAN-MODULE 实证）。
        created, skipped, errors = generate(skeletons, target_root=str(tmp_path))
        assert isinstance(created, int)
        assert isinstance(skipped, int)
        assert isinstance(errors, int)
        assert (tmp_path / "subdir" / "test_file.py").exists()

    def test_empty_skeletons(self):
        created, skipped, errors = generate({})
        assert created == 0
        assert skipped == 0
        assert errors == 0

    def test_returns_tuple_of_three(self):
        result = generate({})
        assert len(result) == 3
        assert all(isinstance(v, int) for v in result)
