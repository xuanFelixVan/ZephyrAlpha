# [A_test] module_id: MOD-SIG-094 | layer=test | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-094 | docs/03_modules/_domain_signal/wyckoff_accumulation_signal/blueprint.md
# [MODULE] tests.signal_ashare.test_wyckoff_accumulation_signal
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] permanent

"""Wyckoff 吸筹买点信号（MOD-SIG-094，B10-01362）施工验证测试。

覆盖：
- 买点：阶段评分上穿门槛+CVD 上行确认→发信号；未上穿/量差不配合→不发；
- 置信度=评分/100 有界；
- Granger 因果自检：领先关系显著检出、独立序列不显著、倒置（评分领先量差）
  → granger_passed=False 信号全阻断（防因果倒置）；样本不足→checked=False 不阻断；
- fail-closed：不等长/过短/NaN/评分越界/非法配置 → ValueError；
- 契约：frozen、to_dict JSON 可序列化。
全程内存合成数据，无 DB；wyckoff 评分/CVD 均鸭子类型注入（域方向纪律）。
"""

from __future__ import annotations

import dataclasses
import json

import numpy as np
import pandas as pd
import pytest

from zephyr.signal_ashare.wyckoff_accumulation_signal import (
    WyckoffAccumulationConfig,
    WyckoffAccumulationSignal,
)


def _engine(**kw) -> WyckoffAccumulationSignal:
    return WyckoffAccumulationSignal(WyckoffAccumulationConfig(**kw))


def _series(values: list[float]) -> pd.Series:
    return pd.Series(values, dtype=float)


class TestBuyPoint:
    def test_threshold_cross_with_cvd_rising_emits(self) -> None:
        score = _series([10, 20, 30, 45, 55, 65, 70, 75, 80, 85, 90, 92])
        cvd = _series([0, 1, 2, 3, 4, 6, 8, 10, 12, 14, 16, 18])
        r = _engine(granger_min_obs=60).generate(score, cvd)
        assert r.candidate_count == 1
        assert r.cvd_confirmed_count == 1
        assert len(r.signals) == 1
        sig = r.signals[0]
        assert sig.bar_index == 5  # 上穿 60 的第一根
        assert sig.wyckoff_score == pytest.approx(65.0)
        assert sig.cvd_slope > 0.0
        assert sig.confidence == pytest.approx(0.65)
        assert r.granger_checked is False  # 样本不足 → 不阻断（降级显式）

    def test_no_cross_no_signal(self) -> None:
        score = _series([10.0] * 12)
        cvd = _series(list(range(12)))
        r = _engine().generate(score, cvd)
        assert r.candidate_count == 0
        assert r.signals == ()

    def test_cross_without_cvd_confirmation_rejected(self) -> None:
        score = _series([10, 20, 30, 45, 55, 65, 70, 75, 80, 85, 90, 92])
        cvd = _series([20, 18, 16, 14, 12, 10, 8, 6, 4, 2, 0, -2])  # 量差持续走弱
        r = _engine().generate(score, cvd)
        assert r.candidate_count == 1
        assert r.cvd_confirmed_count == 0
        assert r.signals == ()

    def test_score_above_threshold_no_fresh_cross(self) -> None:
        # 一直在门槛上方（无上穿事件）→ 无新买点
        score = _series([70.0] * 12)
        cvd = _series(list(range(12)))
        r = _engine().generate(score, cvd)
        assert r.candidate_count == 0


class TestGranger:
    def test_leading_relation_significant(self) -> None:
        rng = np.random.default_rng(11)
        n = 300
        x = rng.normal(0.0, 1.0, n)
        y = np.array([0.8 * x[t - 1] + 0.3 * rng.normal() if t >= 1 else 0.0 for t in range(n)])
        r = _engine().granger_causality(pd.Series(x), pd.Series(y))
        assert r.significant is True
        assert r.pvalue < 0.05
        assert r.f_stat > 0.0

    def test_independent_series_not_significant(self) -> None:
        rng = np.random.default_rng(23)
        x = pd.Series(rng.normal(0.0, 1.0, 300))
        y = pd.Series(rng.normal(0.0, 1.0, 300))
        r = _engine().granger_causality(x, y)
        assert r.significant is False
        assert r.pvalue > 0.05

    def test_cvd_leading_passes_and_signals_flow(self) -> None:
        # Δscore[t] ≈ 2.5×Δcvd[t-1] + 噪声 → 量差领先 → Granger 通过不阻断
        rng = np.random.default_rng(5)
        n = 150
        dcvd = rng.normal(0.0, 1.0, n)
        dcvd[-6:] = 2.0  # 尾段确定性拉升确保上穿
        cvd = np.cumsum(dcvd)
        score = np.zeros(n)
        score[0] = 55.0
        for t in range(1, n):
            score[t] = np.clip(score[t - 1] + 2.5 * dcvd[t - 1] + rng.normal(0.0, 0.5), 0.0, 100.0)
        score[-8:] = np.linspace(58.0, 75.0, 8)  # 确定性尾段：保证一次 60 上穿
        r = _engine().generate(pd.Series(score), pd.Series(cvd))
        assert r.granger_checked is True
        assert r.granger_passed is True
        assert r.blocked_by_granger == 0
        assert len(r.signals) >= 1

    def test_inverted_causality_blocks_all(self) -> None:
        # Δcvd[t] ≈ 3×Δscore[t-1] + 噪声 → 评分领先量差（因果倒置）→ 全阻断
        rng = np.random.default_rng(9)
        n = 150
        dscr = rng.normal(0.0, 0.8, n)
        score = np.clip(55.0 + np.cumsum(dscr), 0.0, 100.0)
        score[-8:] = np.linspace(score[-9], 70.0, 8)  # 确保上穿 60
        cvd = np.zeros(n)
        for t in range(1, n):
            prev = score[t - 1] - score[t - 2] if t >= 2 else 0.0
            cvd[t] = cvd[t - 1] + 3.0 * prev + rng.normal(0.0, 0.4)
        cvd[-8:] += np.linspace(0.0, 5.0, 8)  # 确保上穿点量差确认
        r = _engine().generate(pd.Series(score), pd.Series(cvd))
        assert r.granger_checked is True
        assert r.granger_passed is False
        assert r.signals == ()
        assert r.blocked_by_granger == r.cvd_confirmed_count >= 1


class TestFailClosed:
    def test_unequal_length(self) -> None:
        with pytest.raises(ValueError):
            _engine().generate(_series([1.0, 2.0]), _series([1.0]))

    def test_too_short(self) -> None:
        with pytest.raises(ValueError):
            _engine().generate(_series([1.0] * 3), _series([1.0] * 3))

    def test_nan_rejected(self) -> None:
        with pytest.raises(ValueError):
            _engine().generate(_series([10.0] * 11 + [float("nan")]), _series([1.0] * 12))

    def test_score_out_of_range_rejected(self) -> None:
        with pytest.raises(ValueError):
            _engine().generate(_series([10.0] * 11 + [120.0]), _series([1.0] * 12))

    def test_config_validation(self) -> None:
        with pytest.raises(ValueError):
            WyckoffAccumulationConfig(score_threshold=0.0)
        with pytest.raises(ValueError):
            WyckoffAccumulationConfig(score_threshold=100.1)
        with pytest.raises(ValueError):
            WyckoffAccumulationConfig(cvd_rise_window=0)
        with pytest.raises(ValueError):
            WyckoffAccumulationConfig(granger_pvalue=1.0)
        with pytest.raises(ValueError):
            WyckoffAccumulationConfig(granger_max_lag=0)


class TestContract:
    def test_result_frozen_and_json_serializable(self) -> None:
        score = _series([10, 20, 30, 45, 55, 65, 70, 75, 80, 85, 90, 92])
        cvd = _series([0, 1, 2, 3, 4, 6, 8, 10, 12, 14, 16, 18])
        r = _engine().generate(score, cvd)
        assert dataclasses.is_dataclass(r)
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.candidate_count = 0  # type: ignore[misc]
        json.dumps(r.to_dict())

    def test_granger_result_json_serializable(self) -> None:
        rng = np.random.default_rng(3)
        x = pd.Series(rng.normal(0.0, 1.0, 100))
        y = pd.Series(rng.normal(0.0, 1.0, 100))
        r = _engine().granger_causality(x, y)
        json.dumps(r.to_dict())
