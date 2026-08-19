# [A_test] module_id: MOD-GOV_test_correlation_sentiment_stratifier | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.factor.test_correlation_sentiment_stratifier
# [TESTS] src/zephyr/factor/analysis/correlation_sentiment_stratifier.py
# [TTL] task_bound
"""23 号 memo §3.1② 情绪周期分层标签器测试。

裁定真源：23_strategy_correlation_validation.md §3.1②④——
  BM-SEL-23-B 4+1 阶段打标签 + 置信度<60% 默认保守兜底 + 每阶段 ≥30 样本标注 +
  灰度软分配（30 号 §6.5）。
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.analysis.correlation_sentiment_stratifier import (
    CANONICAL_PHASES,
    build_phase_labels,
    labels_from_grayscale,
    phase_weight_frame,
    split_by_phase,
)


@dataclass(frozen=True)
class _FakeGrayscale:
    """duck-type 仿 MarketSentimentGrayscaleResult（属性访问）。"""

    phase_prob: dict[str, float]
    dominant_phase: str
    confidence: float


class TestBuildPhaseLabels:
    def test_high_confidence_passthrough(self):
        idx = pd.date_range("2026-01-01", periods=3)
        labels = pd.Series(["冰点", "主升", "退潮"], index=idx)
        res = build_phase_labels(labels, pd.Series([0.9, 0.8, 1.0], index=idx))
        assert list(res.labels) == ["冰点", "主升", "退潮"]
        assert res.fallback_count == 0
        assert not res.fallback_mask.any()

    def test_low_confidence_conservative_fallback(self):
        """confidence<0.60 → 默认保守（冰点）并留痕。"""
        idx = pd.date_range("2026-01-01", periods=2)
        labels = pd.Series(["疯狂", "主升"], index=idx)
        res = build_phase_labels(labels, pd.Series([0.4, 0.9], index=idx))
        assert res.labels.iloc[0] == "冰点"  # 疯狂→兜底冰点
        assert res.labels.iloc[1] == "主升"
        assert res.fallback_count == 1
        assert res.fallback_mask.iloc[0]

    def test_hard_labels_only_default_full_confidence(self):
        labels = pd.Series(["反核", "反核"])
        res = build_phase_labels(labels)
        assert list(res.labels) == ["反核", "反核"]

    def test_invalid_phase_rejected(self):
        with pytest.raises(ValueError):
            build_phase_labels(pd.Series(["震荡"]))
        with pytest.raises(ValueError):
            build_phase_labels(pd.Series(["主升"]), pd.Series([0.9, 0.8]))  # 长度不一致
        with pytest.raises(ValueError):
            build_phase_labels(pd.Series(dtype=str))  # 空


class TestLabelsFromGrayscale:
    def test_attr_and_mapping_access(self):
        days = pd.date_range("2026-01-01", periods=3).date
        gmap = {
            days[0]: _FakeGrayscale({"主升": 0.8, "疯狂": 0.2}, "主升", 0.8),
            days[1]: {"phase_prob": {"冰点": 0.5, "反核": 0.5}, "dominant_phase": "冰点", "confidence": 0.5},
            days[2]: _FakeGrayscale({"退潮": 0.95, "主升": 0.05}, "退潮", 0.95),
        }
        res = labels_from_grayscale(gmap)
        assert list(res.labels) == ["主升", "冰点", "退潮"]  # 中间日 0.5<0.6 → 兜底冰点（巧合同主导）
        assert res.fallback_count == 1

    def test_empty_rejected(self):
        with pytest.raises(ValueError):
            labels_from_grayscale({})


class TestSplitByPhase:
    def test_split_counts_and_sufficiency(self):
        n = 100
        idx = pd.date_range("2026-01-01", periods=n)
        panel = pd.DataFrame({"a": np.random.default_rng(1).normal(0, 0.01, n)}, index=idx)
        labels = pd.Series(["主升"] * 80 + ["冰点"] * 20, index=idx)
        slices = split_by_phase(panel, labels, min_samples=30)
        assert slices["主升"].n_obs == 80 and slices["主升"].sufficient
        assert slices["冰点"].n_obs == 20 and not slices["冰点"].sufficient  # 样本不足标注
        assert slices["疯狂"].n_obs == 0 and not slices["疯狂"].sufficient  # 缺阶段也在册
        assert set(slices) == set(CANONICAL_PHASES)

    def test_index_misalignment_uses_intersection(self):
        idx = pd.date_range("2026-01-01", periods=5)
        panel = pd.DataFrame({"a": range(5)}, index=idx)
        labels = pd.Series(["主升"] * 3, index=idx[:3])
        slices = split_by_phase(panel, labels, min_samples=1)
        assert slices["主升"].n_obs == 3

    def test_invalid_inputs_rejected(self):
        with pytest.raises(ValueError):
            split_by_phase(pd.DataFrame(), pd.Series(["主升"]))
        with pytest.raises(ValueError):
            split_by_phase(pd.DataFrame({"a": [0.1]}), pd.Series(["主升"]), min_samples=0)


class TestPhaseWeightFrame:
    def test_weights_sum_to_one(self):
        days = pd.date_range("2026-01-01", periods=2).date
        gmap = {
            days[0]: _FakeGrayscale({"主升": 0.6, "疯狂": 0.3, "退潮": 0.1}, "主升", 0.6),
            days[1]: _FakeGrayscale({"主升": 0.4, "疯狂": 0.35}, "主升", 0.4),
        }
        frame = phase_weight_frame(gmap)
        assert list(frame.columns) == list(CANONICAL_PHASES)
        assert frame.sum(axis=1).to_numpy() == pytest.approx([1.0, 1.0])
        # 高置信日按 P 比例；低置信日全押保守阶段
        assert frame.loc[days[0], "主升"] == pytest.approx(0.6)
        assert frame.loc[days[1], "冰点"] == pytest.approx(1.0)

    def test_zero_prob_degenerates_to_fallback(self):
        days = pd.date_range("2026-01-01", periods=1).date
        gmap = {days[0]: _FakeGrayscale({p: 0.0 for p in CANONICAL_PHASES}, "主升", 0.9)}
        frame = phase_weight_frame(gmap)
        assert frame.loc[days[0], "冰点"] == pytest.approx(1.0)
