# [A_test] module_id: MOD-GOV_converters | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_converters.py — normalize_to_none 单测

Ruling:100PCT-AI-GOVERNANCE P1-1 (2026-07-19) 治本：
  验证 normalize_to_none 只转空字符串为 None，不误转其他 falsy 值。
"""

from __future__ import annotations

import pytest

from zephyr.shared.utils.converters import normalize_to_none


class TestNormalizeToNone:
    """normalize_to_none 行为验证。"""

    @pytest.mark.parametrize("value", ["", ""])
    def test_empty_string_becomes_none(self, value):
        """空字符串 → None（核心语义，对齐 PostgreSQL CHECK 约束）"""
        assert normalize_to_none(value) is None

    def test_none_stays_none(self):
        """None → None（原样）"""
        assert normalize_to_none(None) is None

    def test_non_empty_string_preserved(self):
        """非空字符串原样返回"""
        assert normalize_to_none("D_GOVERNANCE") == "D_GOVERNANCE"
        assert normalize_to_none("production") == "production"
        assert normalize_to_none(" ") == " "  # whitespace 不是空字符串

    def test_zero_preserved(self):
        """0 原样返回——与 `or None` 的关键区别（0 是合法值）"""
        assert normalize_to_none(0) == 0
        assert normalize_to_none(0) is not None

    def test_false_preserved(self):
        """False 原样返回——与 `or None` 的关键区别"""
        assert normalize_to_none(False) is False
        assert normalize_to_none(False) is not None

    def test_empty_list_preserved(self):
        """空列表原样返回——与 `or None` 的关键区别"""
        result = normalize_to_none([])
        assert result == []
        assert result is not None

    def test_empty_dict_preserved(self):
        """空字典原样返回"""
        result = normalize_to_none({})
        assert result == {}
        assert result is not None

    def test_integer_preserved(self):
        """整数原样返回"""
        assert normalize_to_none(42) == 42
        assert normalize_to_none(-1) == -1

    def test_float_preserved(self):
        """浮点数原样返回（包括 0.0）"""
        assert normalize_to_none(3.14) == 3.14
        assert normalize_to_none(0.0) == 0.0
        assert normalize_to_none(0.0) is not None

    def test_typical_usage_domain_id(self):
        """典型用法：weighted_domain_vote 返回值转换"""
        # 模拟 weighted_domain_vote 无域时返回 ""
        domain_id = normalize_to_none("")
        assert domain_id is None
        # 模拟有域时返回 "D_GOVERNANCE"
        domain_id = normalize_to_none("D_GOVERNANCE")
        assert domain_id == "D_GOVERNANCE"

    def test_or_none_vs_normalize_to_none_difference(self):
        """对比测试：`or None` 会误转 0，normalize_to_none 不会"""
        # `0 or None` → None（误转）
        assert (0 or None) is None
        # `normalize_to_none(0)` → 0（正确保留）
        assert normalize_to_none(0) == 0

    @pytest.mark.parametrize(
        "value,expected",
        [
            ("", None),
            (None, None),
            ("text", "text"),
            (0, 0),
            (False, False),
            ([], []),
        ],
    )
    def test_parametrized(self, value, expected):
        """参数化测试覆盖所有边界情况"""
        result = normalize_to_none(value)
        if expected is None:
            assert result is None
        elif expected == [] or expected == 0 or expected is False:
            # 这些值 == 比较为 True 但需要区分 None
            assert result == expected
            assert result is not None
        else:
            assert result == expected
