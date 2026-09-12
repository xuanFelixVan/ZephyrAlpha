# [A_test] module_id: MOD-SIG-105 | layer=test | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-105 | docs/03_modules/_domain_signal/pattern_match_strategy_library/blueprint.md
# [MODULE] tests.signal_ashare.test_pattern_match_strategy_library
# [TTL] permanent
# [DEPENDENCIES] zephyr.signal_ashare.pattern_match_strategy_library

"""量化模式匹配与执行策略库（MOD-SIG-105，B10-01416）施工验证测试。

覆盖：模式封闭集注册、DTW 距离（同型零距/平移放大/带窗截断/非法输入）、
案例匹配排序与 top_k、双门控全组合（胜率/IC/案例数/缺IC fail-closed）、
异 pattern 案例剔除、frozen/JSON 契约。
全程内存合成数据，无 DB。
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from zephyr.signal_ashare.pattern_match_strategy_library import (
    BUY_PATTERNS,
    SELL_PATTERNS,
    PatternMatchConfig,
    PatternMatchStrategyLibrary,
    PatternSpec,
)


def _lib(cfg=None) -> PatternMatchStrategyLibrary:
    return PatternMatchStrategyLibrary(cfg or PatternMatchConfig())


class TestPatternRegistry:
    def test_buy_patterns_length(self):
        assert len(BUY_PATTERNS) == 4

    def test_sell_patterns_length(self):
        assert len(SELL_PATTERNS) == 3

    def test_list_patterns_all(self):
        lib = _lib()
        assert len(lib.list_patterns()) == 7

    def test_list_patterns_buy(self):
        lib = _lib()
        specs = lib.list_patterns("buy")
        assert len(specs) == 4
        assert all(s.side == "buy" for s in specs)

    def test_list_patterns_sell(self):
        lib = _lib()
        specs = lib.list_patterns("sell")
        assert len(specs) == 3
        assert all(s.side == "sell" for s in specs)

    def test_list_patterns_unknown_side(self):
        lib = _lib()
        assert lib.list_patterns("unknown") == ()


class TestDtwDistance:
    def test_identical_zero(self):
        lib = _lib()
        assert lib.dtw_distance([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]) == pytest.approx(0.0, abs=1e-9)

    def test_shifted_positive(self):
        lib = _lib()
        a = [1.0, 2.0, 3.0]
        b = [2.0, 3.0, 4.0]
        d = lib.dtw_distance(a, b)
        assert d > 0

    def test_scaled_positive(self):
        lib = _lib()
        a = [1.0, 2.0, 3.0]
        b = [2.0, 4.0, 6.0]
        d = lib.dtw_distance(a, b)
        assert d > 0

    def test_window_constraint_reduces(self):
        lib = _lib(PatternMatchConfig(dtw_window=0.25))
        a = [0.0] * 10 + [1.0] * 10
        b = [1.0] * 10 + [0.0] * 10
        d_narrow = lib.dtw_distance(a, b)
        lib2 = _lib(PatternMatchConfig(dtw_window=1.0))
        d_wide = lib2.dtw_distance(a, b)
        assert d_narrow >= d_wide

    def test_empty_sequence_raises(self):
        lib = _lib()
        with pytest.raises(ValueError):
            lib.dtw_distance([], [1.0])

    def test_non_finite_raises(self):
        lib = _lib()
        with pytest.raises(ValueError):
            lib.dtw_distance([1.0, float("inf")], [1.0, 2.0])


class TestMatchCases:
    def test_sorting_and_top_k(self):
        lib = _lib()
        query = [1.0, 2.0, 3.0]
        cases = [
            _Case("c1", [1.0, 2.0, 3.0]),
            _Case("c2", [10.0, 20.0, 30.0]),
            _Case("c3", [1.1, 2.1, 3.1]),
        ]
        matches = lib.match_cases(query, cases, top_k=2)
        assert len(matches) == 2
        assert matches[0].case_id == "c1"

    def test_mismatched_pattern_id_skipped(self):
        lib = _lib()
        cases = [_Case("c1", [1.0, 2.0], pattern_id="other")]
        matches = lib.match_cases([1.0, 2.0], cases, pattern_id="query_pat")
        assert len(matches) == 0


class TestGatePattern:
    def test_eligible(self):
        lib = _lib()
        cases = [
            _Case("c1", [1.0], pattern_id="counter_trend_dip", forward_return=0.02),
            _Case("c2", [2.0], pattern_id="counter_trend_dip", forward_return=0.03),
        ]
        r = lib.gate_pattern("counter_trend_dip", cases, ic_value=0.04)
        assert r.eligible is True

    def test_insufficient_cases(self):
        lib = _lib(PatternMatchConfig(min_cases=5))
        cases = [_Case("c1", [1.0], pattern_id="counter_trend_dip", forward_return=0.02)]
        r = lib.gate_pattern("counter_trend_dip", cases, ic_value=0.04)
        assert r.eligible is False
        assert "min_cases" in r.reason.lower()

    def test_low_win_rate(self):
        lib = _lib()
        cases = [
            _Case("c1", [1.0], pattern_id="counter_trend_dip", forward_return=-0.01),
            _Case("c2", [2.0], pattern_id="counter_trend_dip", forward_return=-0.02),
        ]
        r = lib.gate_pattern("counter_trend_dip", cases, ic_value=0.04)
        assert r.eligible is False
        assert "win_rate" in r.reason.lower()

    def test_low_ic(self):
        lib = _lib()
        cases = [
            _Case("c1", [1.0], pattern_id="counter_trend_dip", forward_return=0.02),
            _Case("c2", [2.0], pattern_id="counter_trend_dip", forward_return=0.03),
        ]
        r = lib.gate_pattern("counter_trend_dip", cases, ic_value=0.01)
        assert r.eligible is False
        assert "ic" in r.reason.lower()

    def test_missing_ic_fail_closed(self):
        lib = _lib()
        cases = [
            _Case("c1", [1.0], pattern_id="counter_trend_dip", forward_return=0.02),
            _Case("c2", [2.0], pattern_id="counter_trend_dip", forward_return=0.03),
        ]
        r = lib.gate_pattern("counter_trend_dip", cases, ic_value=None)
        assert r.eligible is False
        assert "ic_missing" in r.reason.lower()

    def test_unknown_pattern_raises(self):
        lib = _lib()
        with pytest.raises(ValueError):
            lib.gate_pattern("no_such_pattern", [])


class TestFrozenAndJson:
    def test_config_frozen(self):
        cfg = PatternMatchConfig()
        with pytest.raises(dataclasses.FrozenInstanceError):
            cfg.min_win_rate = 0.0

    def test_config_to_dict_roundtrip(self):
        cfg = PatternMatchConfig(min_cases=10)
        d = dataclasses.asdict(cfg)
        assert json.dumps(d)


# helpers
class _Case:
    def __init__(self, case_id: str, series, pattern_id=None, forward_return=None):
        self.case_id = case_id
        self.series = series
        self.pattern_id = pattern_id
        self.forward_return = forward_return
