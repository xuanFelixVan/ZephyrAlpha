# [BLUEPRINT] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md §3.5/§3.6
# [TTL] permanent
"""SelectionResult.confidence 算法 + 事件过滤阈值单元测试——含边界/退化用例。"""

from __future__ import annotations

import pytest

from zephyr.signal_fundamental.selection_confidence import (
    EVENT_CONFIDENCE_FILTER_THRESHOLD,
    EVENT_TYPE_CONFIDENCE_THRESHOLDS,
    compute_daban_confidence,
    compute_event_confidence,
    compute_multifactor_confidence,
    event_passes_confidence_filter,
    validate_event_confidence_thresholds,
)


class TestThresholdConfig:
    def test_default_threshold_table_valid(self):
        assert validate_event_confidence_thresholds() == []
        assert EVENT_CONFIDENCE_FILTER_THRESHOLD == 0.7

    def test_invalid_values_detected(self):
        problems = validate_event_confidence_thresholds({"earnings": 0.0, "ma": 1.5, "": 0.5})
        assert any("越界" in p for p in problems)
        assert any("非法事件类型键" in p for p in problems)

    def test_empty_table_detected(self):
        assert validate_event_confidence_thresholds({}) == ["阈值表为空"]


class TestEventFilter:
    def test_threshold_boundary(self):
        assert event_passes_confidence_filter("earnings", 0.70) is True  # 边界含等号
        assert event_passes_confidence_filter("earnings", 0.69) is False

    def test_type_differentiation(self):
        # 并购阈值 0.75 > 政策 0.65
        assert event_passes_confidence_filter("ma", 0.70) is False
        assert event_passes_confidence_filter("policy", 0.70) is True

    def test_unknown_type_falls_back_default(self):
        assert event_passes_confidence_filter("unknown_type", 0.70) is True
        assert event_passes_confidence_filter("unknown_type", 0.60) is False


class TestEventConfidence:
    def test_mild_reaction_no_decay(self):
        assert compute_event_confidence(0.8, 0.03) == pytest.approx(0.8)  # 边界 3%
        assert compute_event_confidence(0.8, -0.02) == pytest.approx(0.8)

    def test_extreme_reaction_decay_to_tenth(self):
        assert compute_event_confidence(0.8, 0.031) == pytest.approx(0.08)
        assert compute_event_confidence(0.9, -0.05) == pytest.approx(0.09)

    def test_input_clipped(self):
        assert compute_event_confidence(1.5, 0.01) == pytest.approx(1.0)
        assert compute_event_confidence(-0.2, 0.01) == 0.0


class TestDabanConfidence:
    def test_product_of_phase_and_strength(self):
        assert compute_daban_confidence(0.8, 0.5) == pytest.approx(0.4)

    def test_default_strength_no_discount(self):
        assert compute_daban_confidence(0.75) == pytest.approx(0.75)

    def test_clipped(self):
        assert compute_daban_confidence(1.2, 1.0) == pytest.approx(1.0)
        assert compute_daban_confidence(-0.1) == 0.0


class TestMultifactorConfidence:
    def test_strong_consensus_high_confidence(self):
        # 均值 IC 0.05（满分线）+ 零离散 → 1.0
        c = compute_multifactor_confidence([0.05, 0.05, 0.05, 0.05])
        assert c == pytest.approx(1.0)

    def test_dispersion_discount(self):
        tight = compute_multifactor_confidence([0.05, 0.05, 0.05])
        loose = compute_multifactor_confidence([0.10, 0.05, 0.0])
        assert 0.0 < loose < tight

    def test_negative_mean_ic_zero(self):
        assert compute_multifactor_confidence([-0.02, -0.01, -0.03]) == 0.0

    def test_too_few_factors_zero(self):
        assert compute_multifactor_confidence([0.1, 0.1]) == 0.0
        assert compute_multifactor_confidence([]) == 0.0

    def test_output_bounded(self):
        c = compute_multifactor_confidence([0.5, -0.4, 0.3, 0.02, -0.1])
        assert 0.0 <= c <= 1.0
