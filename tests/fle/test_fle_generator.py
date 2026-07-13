# [A_test] module_id: SRC-TST-1017 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_fle_generator
# [INVARIANTS] generate() returns (created, skipped, errors); atomic write via tmp+os.replace
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import os
from unittest.mock import patch

from zephyr.feedback_loop.generator import BASE, generate, main


class TestGeneratorInstantiation:
    def test_base_path_defined(self):
        assert BASE is not None
        assert isinstance(BASE, str)


class TestGenerate:
    def test_generate_with_empty_skeletons(self):
        created, skipped, errors = generate(skeletons={})
        assert created == 0
        assert skipped == 0
        assert errors == 0

    def test_generate_creates_new_file(self):
        skeletons = {"_test_gen_new_file.py": "# test content\n"}
        try:
            created, skipped, errors = generate(skeletons=skeletons)
            assert created == 1
            assert errors == 0
            target = os.path.normpath(os.path.join(BASE, "_test_gen_new_file.py"))
            assert os.path.exists(target)
        finally:
            target = os.path.normpath(os.path.join(BASE, "_test_gen_new_file.py"))
            if os.path.exists(target):
                os.remove(target)

    def test_generate_skips_existing_file(self):
        skeletons = {"_test_gen_skip_file.py": "# original\n"}
        target = os.path.normpath(os.path.join(BASE, "_test_gen_skip_file.py"))
        try:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                f.write("# original\n")
            created, skipped, errors = generate(skeletons=skeletons)
            assert skipped == 1
            assert created == 0
        finally:
            if os.path.exists(target):
                os.remove(target)

    def test_generate_returns_tuple_of_three(self):
        result = generate(skeletons={})
        assert isinstance(result, tuple)
        assert len(result) == 3


class TestGenerateBoundary:
    def test_generate_with_none_uses_default_skeletons(self):
        with patch("zephyr.feedback_loop.generator.SKELETONS", {}):
            created, skipped, errors = generate(skeletons=None)
            assert created == 0

    def test_generate_multiple_skeletons(self):
        skeletons = {
            "_test_gen_multi_a.py": "# a\n",
            "_test_gen_multi_b.py": "# b\n",
        }
        try:
            created, skipped, errors = generate(skeletons=skeletons)
            assert created == 2
        finally:
            for name in skeletons:
                target = os.path.normpath(os.path.join(BASE, name))
                if os.path.exists(target):
                    os.remove(target)


class TestMain:
    def test_main_runs_without_error(self):
        with patch("zephyr.feedback_loop.generator.generate", return_value=(0, 0, 0)):
            main()
