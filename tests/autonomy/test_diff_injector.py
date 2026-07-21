# [A_test] module_id: MOD-GOV_diff_injector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_diff_injector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_diff_injector.py -q
# [TTL] task_bound
from __future__ import annotations

from zephyr.autonomy_core.context.diff_injector import DiffInjector, DiffResult


class TestDiffResult:
    def test_instantiation_with_all_fields(self):
        dr = DiffResult(prefix_tokens=10, suffix_tokens=20, diff_tokens=10, compressed=False)
        assert dr.prefix_tokens == 10
        assert dr.suffix_tokens == 20
        assert dr.diff_tokens == 10
        assert dr.compressed is False

    def test_instantiation_with_compressed_true(self):
        dr = DiffResult(prefix_tokens=5, suffix_tokens=5, diff_tokens=0, compressed=True)
        assert dr.compressed is True

    def test_equality(self):
        a = DiffResult(prefix_tokens=1, suffix_tokens=2, diff_tokens=1, compressed=False)
        b = DiffResult(prefix_tokens=1, suffix_tokens=2, diff_tokens=1, compressed=False)
        assert a == b


class TestDiffInjector:
    def test_instantiation(self):
        injector = DiffInjector()
        assert injector is not None

    def test_inject_diff_returns_diff_result(self):
        injector = DiffInjector()
        result = injector.inject_diff("hello", "hello world")
        assert isinstance(result, DiffResult)

    def test_inject_diff_prefix_equals_prev_length(self):
        injector = DiffInjector()
        result = injector.inject_diff("abc", "abcdef")
        assert result.prefix_tokens == 3

    def test_inject_diff_suffix_equals_new_length(self):
        injector = DiffInjector()
        result = injector.inject_diff("abc", "abcdef")
        assert result.suffix_tokens == 6

    def test_inject_diff_tokens_is_difference(self):
        injector = DiffInjector()
        result = injector.inject_diff("abc", "abcdef")
        assert result.diff_tokens == 3

    def test_inject_diff_compressed_is_false(self):
        injector = DiffInjector()
        result = injector.inject_diff("x", "xy")
        assert result.compressed is False

    def test_inject_diff_empty_prev(self):
        injector = DiffInjector()
        result = injector.inject_diff("", "hello")
        assert result.prefix_tokens == 0
        assert result.suffix_tokens == 5
        assert result.diff_tokens == 5

    def test_inject_diff_empty_new(self):
        injector = DiffInjector()
        result = injector.inject_diff("hello", "")
        assert result.prefix_tokens == 5
        assert result.suffix_tokens == 0
        assert result.diff_tokens == -5

    def test_inject_diff_both_empty(self):
        injector = DiffInjector()
        result = injector.inject_diff("", "")
        assert result.prefix_tokens == 0
        assert result.suffix_tokens == 0
        assert result.diff_tokens == 0

    def test_inject_diff_equal_strings(self):
        injector = DiffInjector()
        result = injector.inject_diff("same", "same")
        assert result.prefix_tokens == 4
        assert result.suffix_tokens == 4
        assert result.diff_tokens == 0

    def test_inject_diff_shrinking_context(self):
        injector = DiffInjector()
        result = injector.inject_diff("longer context here", "short")
        assert result.diff_tokens < 0
        assert result.prefix_tokens == 19
        assert result.suffix_tokens == 5

    def test_inject_diff_unicode_content(self):
        injector = DiffInjector()
        result = injector.inject_diff("你好", "你好世界")
        assert result.prefix_tokens == 2
        assert result.suffix_tokens == 4
        assert result.diff_tokens == 2
