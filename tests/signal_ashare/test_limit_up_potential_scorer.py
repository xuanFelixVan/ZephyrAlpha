# [A_test] module_id: MOD-SIG-102 | layer=test | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-102 | docs/03_modules/_domain_signal/limit_up_potential_scorer/blueprint.md
# [MODULE] tests.signal_ashare.test_limit_up_potential_scorer
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] permanent

"""IC加权多因子涨停板潜力评分模型（MOD-SIG-102，B10-01380）施工验证测试。

覆盖：
- 七分封闭集：未知分名/重复分名/空标的/空分列表 → ValueError（fail-closed）；
- RankIC：完全单调正相关 → +1、完全单调负相关 → −1、零方差 → 0+notes 降级；
- IC 验证门：IC≤0.03 或 ICIR≤0.5 → 出局权重归 0；IC 加权 w_i=IC_i/ΣIC_j 归一；
- 全分出局 → 经验权重回退（fallback_used=True，sufficient=False）；
- 样本不足（<min_samples）→ 该分 checked 不足出局 + notes，不阻断其他分；
- 综合分=Σw_i×score_i×100；分档 A/B/C/D 边界；
- 契约：frozen、to_dict JSON 可序列化。
全程内存合成数据，无 DB。
"""

from __future__ import annotations

import dataclasses
import json
import math

import pytest

from zephyr.signal_ashare.limit_up_potential_scorer import (
    EMPIRICAL_WEIGHTS,
    LIMIT_UP_FACTOR_NAMES,
    FactorEvidence,
    LimitUpPotentialConfig,
    LimitUpPotentialScorer,
)


def _samples_monotone(n: int = 40, sign: float = 1.0) -> tuple[tuple[float, float], ...]:
    """完全单调样本（IC=±1）：分位与前瞻收益同向/反向。"""
    return tuple((float(i), sign * float(i)) for i in range(n))


def _samples_noisy(n: int = 40) -> tuple[tuple[float, float], ...]:
    """交替抖动样本（IC≈0）。"""
    return tuple((float(i), float((-1) ** i) * (i % 7)) for i in range(n))


def _factor(
    name: str = "ladder_height",
    score: float = 0.8,
    samples: tuple[tuple[float, float], ...] | None = None,
) -> FactorEvidence:
    return FactorEvidence(
        name=name,
        current_score=score,
        samples=samples if samples is not None else _samples_monotone(),
    )


def _scorer(**kwargs) -> LimitUpPotentialScorer:
    return LimitUpPotentialScorer(LimitUpPotentialConfig(**kwargs))


class TestConfigValidation:
    def test_ic_gate_negative(self):
        with pytest.raises(ValueError):
            LimitUpPotentialConfig(ic_gate=-0.01)

    def test_icir_gate_negative(self):
        with pytest.raises(ValueError):
            LimitUpPotentialConfig(icir_gate=-0.1)

    def test_min_samples_too_small(self):
        with pytest.raises(ValueError):
            LimitUpPotentialConfig(min_samples=5)

    def test_ic_chunks_too_small(self):
        with pytest.raises(ValueError):
            LimitUpPotentialConfig(ic_chunks=1)

    def test_grade_thresholds_not_monotonic(self):
        with pytest.raises(ValueError):
            LimitUpPotentialConfig(grade_a_threshold=50.0, grade_b_threshold=60.0)


class TestFactorEvidenceValidation:
    def test_unknown_factor_name(self):
        with pytest.raises(ValueError):
            _factor(name="mystery_factor")

    def test_score_above_one(self):
        with pytest.raises(ValueError):
            _factor(score=1.01)

    def test_score_below_zero(self):
        with pytest.raises(ValueError):
            _factor(score=-0.1)

    def test_closed_set_has_seven(self):
        assert len(LIMIT_UP_FACTOR_NAMES) == 7
        assert "ladder_height" in LIMIT_UP_FACTOR_NAMES
        assert "market_sentiment" in LIMIT_UP_FACTOR_NAMES


class TestEvaluateFailClosed:
    def test_empty_symbol(self):
        with pytest.raises(ValueError):
            _scorer().evaluate("", [_factor()])

    def test_empty_factors(self):
        with pytest.raises(ValueError):
            _scorer().evaluate("600000", [])

    def test_duplicate_factor_name(self):
        with pytest.raises(ValueError):
            _scorer().evaluate("600000", [_factor(), _factor()])

    def test_non_finite_sample(self):
        bad = ((1.0, 1.0), (2.0, math.inf)) + _samples_monotone(38)
        with pytest.raises(ValueError):
            _scorer().evaluate("600000", [_factor(samples=bad)])


class TestRankIC:
    def test_monotone_positive_ic_near_one(self):
        report = _scorer().evaluate("600000", [_factor()])
        ev = report.evaluations[0]
        assert ev.ic == pytest.approx(1.0, abs=1e-9)
        assert ev.effective is True

    def test_monotone_negative_ic_near_minus_one(self):
        report = _scorer().evaluate("600000", [_factor(samples=_samples_monotone(sign=-1.0))])
        ev = report.evaluations[0]
        assert ev.ic == pytest.approx(-1.0, abs=1e-9)
        assert ev.effective is False
        # 单分全出局 → 经验权重回退（归一后=1.0），显式降级不静默
        assert report.fallback_used is True
        assert report.sufficient is False
        assert ev.weight == pytest.approx(1.0)

    def test_noisy_ic_below_gate(self):
        report = _scorer().evaluate("600000", [_factor(samples=_samples_noisy())])
        ev = report.evaluations[0]
        assert abs(ev.ic) <= 0.03
        assert ev.effective is False
        assert report.fallback_used is True
        assert ev.weight == pytest.approx(1.0)


class TestWeighting:
    def test_weights_proportional_to_ic(self):
        strong = _factor(name="ladder_height", samples=_samples_monotone())
        weak = _factor(name="seal_strength", samples=_samples_noisy())
        report = _scorer().evaluate("600000", [strong, weak])
        w = {e.name: e.weight for e in report.evaluations}
        assert w["ladder_height"] == pytest.approx(1.0)
        assert w["seal_strength"] == pytest.approx(0.0)
        assert report.fallback_used is False
        assert report.sufficient is True

    def test_weights_sum_to_one_over_effective(self):
        f1 = _factor(name="ladder_height", samples=_samples_monotone())
        f2 = _factor(name="seal_strength", samples=_samples_monotone())
        f3 = _factor(name="sector_momentum", samples=_samples_monotone())
        report = _scorer().evaluate("600000", [f1, f2, f3])
        total = sum(e.weight for e in report.evaluations)
        assert total == pytest.approx(1.0)

    def test_fallback_when_all_ineffective(self):
        weak1 = _factor(name="ladder_height", samples=_samples_noisy())
        weak2 = _factor(name="market_sentiment", samples=_samples_noisy())
        report = _scorer().evaluate("600000", [weak1, weak2])
        assert report.fallback_used is True
        assert report.sufficient is False
        expected = EMPIRICAL_WEIGHTS["ladder_height"] + EMPIRICAL_WEIGHTS["market_sentiment"]
        w = {e.name: e.weight for e in report.evaluations}
        assert w["ladder_height"] == pytest.approx(EMPIRICAL_WEIGHTS["ladder_height"] / expected)

    def test_insufficient_samples_excluded(self):
        few = tuple((float(i), float(i)) for i in range(10))
        report = _scorer(min_samples=30).evaluate("600000", [_factor(samples=few), _factor(name="seal_strength")])
        ev = {e.name: e for e in report.evaluations}
        assert ev["ladder_height"].effective is False
        assert any("样本不足" in n for n in ev["ladder_height"].notes)
        assert ev["seal_strength"].effective is True


class TestCompositeAndGrade:
    def test_all_perfect_scores_composite_100_grade_a(self):
        factors = [_factor(name=n, score=1.0) for n in ("ladder_height", "seal_strength", "sector_momentum")]
        report = _scorer().evaluate("600000", factors)
        assert report.composite_score == pytest.approx(100.0)
        assert report.grade == "A"

    def test_all_zero_scores_composite_0_grade_d(self):
        factors = [_factor(name=n, score=0.0) for n in ("ladder_height", "seal_strength")]
        report = _scorer().evaluate("600000", factors)
        assert report.composite_score == pytest.approx(0.0)
        assert report.grade == "D"

    def test_grade_boundaries(self):
        report = _scorer().evaluate("600000", [_factor(score=0.7)])
        assert report.composite_score == pytest.approx(70.0)
        assert report.grade == "A"
        report_b = _scorer().evaluate("600000", [_factor(score=0.5)])
        assert report_b.grade == "B"
        report_c = _scorer().evaluate("600000", [_factor(score=0.3)])
        assert report_c.grade == "C"


class TestContract:
    def test_frozen_and_json_serializable(self):
        report = _scorer().evaluate("600000", [_factor()])
        assert dataclasses.is_dataclass(report)
        with pytest.raises(dataclasses.FrozenInstanceError):
            report.grade = "X"  # type: ignore[misc]
        json.dumps(report.to_dict(), ensure_ascii=False)
