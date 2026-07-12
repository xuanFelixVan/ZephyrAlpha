# [A_test] module_id: SRC-TST-0608 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_context_truncation
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.context_truncation
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_context_truncation.py
# [TTL] task_bound

import pytest

from zephyr.feedback_loop.diagnosers.context_truncation import ContextTruncation


class TestContextTruncationInstantiation:
    def test_default_max_tokens(self):
        ct = ContextTruncation()
        assert ct.max_tokens == 8192

    def test_custom_max_tokens(self):
        ct = ContextTruncation(max_tokens=4096)
        assert ct.max_tokens == 4096


class TestContextTruncationCheck:
    def test_check_below_limit(self):
        ct = ContextTruncation(max_tokens=8192)
        assert ct.check(1000) is False

    def test_check_at_limit(self):
        ct = ContextTruncation(max_tokens=8192)
        assert ct.check(8192) is False

    def test_check_above_limit(self):
        ct = ContextTruncation(max_tokens=8192)
        assert ct.check(9000) is True

    def test_check_just_above_limit(self):
        ct = ContextTruncation(max_tokens=8192)
        assert ct.check(8193) is True

    def test_check_zero_tokens(self):
        ct = ContextTruncation(max_tokens=8192)
        assert ct.check(0) is False

    def test_check_small_max_tokens(self):
        ct = ContextTruncation(max_tokens=100)
        assert ct.check(50) is False
        assert ct.check(101) is True


class TestContextTruncationBoundary:
    def test_check_negative_tokens(self):
        ct = ContextTruncation(max_tokens=8192)
        assert ct.check(-1) is False

    def test_check_none_tokens_raises(self):
        ct = ContextTruncation(max_tokens=8192)
        with pytest.raises((TypeError, AttributeError)):
            ct.check(None)

    def test_zero_max_tokens(self):
        ct = ContextTruncation(max_tokens=0)
        assert ct.check(1) is True
        assert ct.check(0) is False

    def test_negative_max_tokens(self):
        ct = ContextTruncation(max_tokens=-100)
        assert ct.check(0) is True

    def test_large_token_count(self):
        ct = ContextTruncation(max_tokens=8192)
        assert ct.check(1_000_000) is True
