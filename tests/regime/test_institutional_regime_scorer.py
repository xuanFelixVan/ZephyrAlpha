# [BLUEPRINT] MOD-REGIME-015 | docs/03_modules/_domain_regime/institutional_regime_scorer/blueprint.md | §test
# [MODULE] tests.regime.test_institutional_regime_scorer
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.institutional_regime_scorer
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_institutional_regime_scorer.py
# [A_test] module_id: MOD-REGIME-015 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-REGIME-015 单元测试: 三维机构级 regime 评分器。

覆盖: CAPE/IV/两融三维度正常态、缺失态、边界态；合成逻辑（加权/权重归一/降级）；
regime 态映射（泡沫/恐慌/中性/极端）；置信度计算。
"""

from __future__ import annotations

import pytest

pytest.importorskip(
    "zephyr.regime.institutional_regime_scorer",
    reason="institutional_regime_scorer not importable",
)

from zephyr.regime.institutional_regime_scorer import (  # noqa: E402
    InstitutionalRegimeConfigError,
    InstitutionalRegimeScore,
    InstitutionalRegimeScorer,
    RegimeDimensionScore,
    RegimeState,
)


# ──────────────────────────────────────────────────────────────────────────────
# 夹具（纯内存，不触网）
# ──────────────────────────────────────────────────────────────────────────────


def _scorer(**kwargs) -> InstitutionalRegimeScorer:
    return InstitutionalRegimeScorer(**kwargs)


def _full_inputs() -> dict:
    """三维度全量正常输入。"""
    return {
        "cape_percentile": 0.90,
        "cape_value": 35.0,
        "iv_synthetic_vix": 30.0,
        "iv_percentile_1y": 0.80,
        "margin_balance_ratio": 0.022,
        "margin_drop_from_peak": 0.10,
        "margin_buy_ratio": 0.08,
    }


# ──────────────────────────────────────────────────────────────────────────────
# 配置校验
# ──────────────────────────────────────────────────────────────────────────────


class TestConfigValidation:
    def test_default_weights(self):
        s = _scorer()
        assert s._w_cape == pytest.approx(0.35)
        assert s._w_iv == pytest.approx(0.35)
        assert s._w_margin == pytest.approx(0.30)

    def test_custom_weights(self):
        s = _scorer(weight_cape=0.5, weight_iv=0.3, weight_margin=0.2)
        assert s._w_cape == pytest.approx(0.5)
        assert s._w_iv == pytest.approx(0.3)
        assert s._w_margin == pytest.approx(0.2)

    def test_weight_auto_normalize(self):
        s = _scorer(weight_cape=2.0, weight_iv=1.0, weight_margin=1.0)
        assert s._w_cape == pytest.approx(0.5)
        assert s._w_iv == pytest.approx(0.25)
        assert s._w_margin == pytest.approx(0.25)

    def test_negative_weight_raises(self):
        with pytest.raises(InstitutionalRegimeConfigError):
            _scorer(weight_cape=-0.1)

    def test_weight_sum_zero_raises(self):
        with pytest.raises(InstitutionalRegimeConfigError):
            _scorer(weight_cape=0.0, weight_iv=0.0, weight_margin=0.0)


# ──────────────────────────────────────────────────────────────────────────────
# CAPE 维度
# ──────────────────────────────────────────────────────────────────────────────


class TestCapeDimension:
    def test_cape_extreme_high(self):
        s = _scorer()
        d = s._score_cape(0.96, 42.0)
        assert d.available is True
        assert d.score == 95.0
        assert d.detail["percentile"] == 0.96

    def test_cape_high(self):
        s = _scorer()
        d = s._score_cape(0.85, None)
        assert d.available is True
        assert d.score == 75.0

    def test_cape_neutral(self):
        s = _scorer()
        d = s._score_cape(0.60, None)
        assert d.available is True
        assert d.score == 50.0

    def test_cape_low(self):
        s = _scorer()
        d = s._score_cape(0.20, None)
        assert d.available is True
        assert d.score == 25.0

    def test_cape_deep_low(self):
        s = _scorer()
        d = s._score_cape(0.12, None)
        assert d.available is True
        assert d.score == 10.0

    def test_cape_extreme_low(self):
        s = _scorer()
        d = s._score_cape(0.05, None)
        assert d.available is True
        assert d.score == 5.0

    def test_cape_absolute_boost(self):
        s = _scorer()
        d = s._score_cape(0.60, 41.0)
        assert d.score == 90.0

    def test_cape_missing(self):
        s = _scorer()
        d = s._score_cape(None, None)
        assert d.available is False
        assert d.score == 0.0

    def test_cape_percentile_out_of_range(self):
        s = _scorer()
        d = s._score_cape(1.5, None)
        assert d.available is False


# ──────────────────────────────────────────────────────────────────────────────
# IV 维度
# ──────────────────────────────────────────────────────────────────────────────


class TestIvDimension:
    def test_iv_extreme_panic(self):
        s = _scorer()
        d = s._score_iv(42.0, None)
        assert d.available is True
        assert d.score == 95.0

    def test_iv_panic(self):
        s = _scorer()
        d = s._score_iv(36.0, None)
        assert d.available is True
        assert d.score == 80.0

    def test_iv_elevated(self):
        s = _scorer()
        d = s._score_iv(28.0, None)
        assert d.available is True
        assert d.score == 65.0

    def test_iv_normal(self):
        s = _scorer()
        d = s._score_iv(18.0, None)
        assert d.available is True
        assert d.score == 20.0

    def test_iv_percentile_extreme(self):
        s = _scorer()
        d = s._score_iv(None, 0.92)
        assert d.available is True
        assert d.score == 90.0

    def test_iv_percentile_high(self):
        s = _scorer()
        d = s._score_iv(None, 0.80)
        assert d.available is True
        assert d.score == 70.0

    def test_iv_both_inputs(self):
        s = _scorer()
        d = s._score_iv(36.0, 0.92)
        assert d.available is True
        assert d.score == pytest.approx((80.0 + 90.0) / 2)

    def test_iv_missing(self):
        s = _scorer()
        d = s._score_iv(None, None)
        assert d.available is False

    def test_iv_negative_vix(self):
        s = _scorer()
        d = s._score_iv(-5.0, None)
        assert d.available is False

    def test_iv_percentile_out_of_range(self):
        s = _scorer()
        d = s._score_iv(None, 1.2)
        assert d.available is False


# ──────────────────────────────────────────────────────────────────────────────
# 两融维度
# ──────────────────────────────────────────────────────────────────────────────


class TestMarginDimension:
    def test_margin_extreme_leverage(self):
        s = _scorer()
        d = s._score_margin(0.028, None, None)
        assert d.available is True
        assert d.score == 90.0

    def test_margin_high_leverage(self):
        s = _scorer()
        d = s._score_margin(0.022, None, None)
        assert d.available is True
        assert d.score == 70.0

    def test_margin_normal(self):
        s = _scorer()
        d = s._score_margin(0.012, None, None)
        assert d.available is True
        assert d.score == 30.0

    def test_margin_drop_extreme(self):
        s = _scorer()
        d = s._score_margin(None, 0.28, None)
        assert d.available is True
        assert d.score == 85.0

    def test_margin_drop_high(self):
        s = _scorer()
        d = s._score_margin(None, 0.18, None)
        assert d.available is True
        assert d.score == 65.0

    def test_margin_buy_cold(self):
        s = _scorer()
        d = s._score_margin(None, None, 0.06)
        assert d.available is True
        assert d.score == 65.0

    def test_margin_buy_extreme_cold(self):
        s = _scorer()
        d = s._score_margin(None, None, 0.04)
        assert d.available is True
        assert d.score == 85.0

    def test_margin_all_inputs(self):
        s = _scorer()
        d = s._score_margin(0.028, 0.28, 0.04)
        assert d.available is True
        # score 内部 round 到 2 位小数
        assert d.score == pytest.approx(round((90.0 + 85.0 + 85.0) / 3, 2))

    def test_margin_missing(self):
        s = _scorer()
        d = s._score_margin(None, None, None)
        assert d.available is False

    def test_margin_ratio_out_of_range(self):
        s = _scorer()
        d = s._score_margin(1.5, None, None)
        assert d.available is False

    def test_margin_drop_out_of_range(self):
        s = _scorer()
        d = s._score_margin(None, 1.5, None)
        assert d.available is False


# ──────────────────────────────────────────────────────────────────────────────
# 合成逻辑
# ──────────────────────────────────────────────────────────────────────────────


class TestComposite:
    def test_full_inputs(self):
        s = _scorer()
        result = s.score(**_full_inputs())
        assert isinstance(result, InstitutionalRegimeScore)
        assert 0.0 <= result.regime_score <= 100.0
        assert result.confidence > 0.0
        assert result.degraded is False
        assert result.degraded_dimensions == ()

    def test_all_missing(self):
        s = _scorer()
        result = s.score()
        assert result.regime_score == 50.0
        assert result.regime_state == RegimeState.NEUTRAL
        assert result.confidence == 0.0
        assert result.degraded is True
        assert set(result.degraded_dimensions) == {"cape", "iv", "margin"}

    def test_single_dimension_only(self):
        s = _scorer()
        result = s.score(cape_percentile=0.90)
        assert result.degraded is True
        assert "iv" in result.degraded_dimensions
        assert "margin" in result.degraded_dimensions
        # 单维有效时 composite = 该维 score
        assert result.regime_score == pytest.approx(75.0)

    def test_weight_normalization_on_missing(self):
        """缺失维度不减权重——剩余维度权重归一。"""
        s = _scorer(weight_cape=0.5, weight_iv=0.3, weight_margin=0.2)
        result = s.score(cape_percentile=0.96, iv_synthetic_vix=42.0)
        # 有效维度 = cape(95) + iv(95)，权重归一后各占 0.5
        assert result.regime_score == pytest.approx(95.0)

    def test_confidence_scales_with_dimensions(self):
        s = _scorer()
        r1 = s.score(cape_percentile=0.90)
        r2 = s.score(cape_percentile=0.90, iv_synthetic_vix=30.0)
        r3 = s.score(**_full_inputs())
        assert r1.confidence < r2.confidence < r3.confidence
        assert r3.confidence == pytest.approx(1.0)


# ──────────────────────────────────────────────────────────────────────────────
# Regime 态映射
# ──────────────────────────────────────────────────────────────────────────────


class TestRegimeStateMapping:
    def test_extreme_bubble(self):
        s = _scorer()
        result = s.score(
            cape_percentile=0.96,  # CAPE 极端高 → 95
            iv_synthetic_vix=18.0,  # IV 低 → 20
            margin_balance_ratio=0.028,  # 杠杆极端 → 90
        )
        assert result.regime_state == RegimeState.EXTREME_BUBBLE

    def test_bubble(self):
        s = _scorer()
        result = s.score(
            cape_percentile=0.85,  # CAPE 高 → 75
            iv_synthetic_vix=22.0,  # IV 正常 → 40
            margin_balance_ratio=0.022,  # 杠杆高 → 70
        )
        assert result.regime_state == RegimeState.BUBBLE

    def test_neutral(self):
        s = _scorer()
        result = s.score(
            cape_percentile=0.50,
            iv_synthetic_vix=20.0,
            margin_balance_ratio=0.015,
        )
        assert result.regime_state == RegimeState.NEUTRAL

    def test_panic(self):
        s = _scorer()
        result = s.score(
            cape_percentile=0.50,
            iv_synthetic_vix=42.0,  # IV 极端 → 95
            margin_balance_ratio=0.015,
        )
        assert result.regime_state == RegimeState.PANIC

    def test_extreme_panic(self):
        s = _scorer()
        result = s.score(
            cape_percentile=0.08,  # CAPE 大底 → 10
            iv_synthetic_vix=45.0,  # IV 极端 → 95
            margin_drop_from_peak=0.28,  # 去杠杆极端 → 85
        )
        assert result.regime_state == RegimeState.EXTREME_PANIC


# ──────────────────────────────────────────────────────────────────────────────
# 边界态
# ──────────────────────────────────────────────────────────────────────────────


class TestEdgeCases:
    def test_cape_boundary_95(self):
        s = _scorer()
        d = s._score_cape(0.95, None)
        assert d.score == 95.0

    def test_cape_boundary_80(self):
        s = _scorer()
        d = s._score_cape(0.80, None)
        assert d.score == 75.0

    def test_iv_boundary_35(self):
        s = _scorer()
        d = s._score_iv(35.0, None)
        assert d.score == 80.0

    def test_iv_boundary_40(self):
        s = _scorer()
        d = s._score_iv(40.0, None)
        assert d.score == 95.0

    def test_margin_boundary_25pct(self):
        s = _scorer()
        d = s._score_margin(None, 0.25, None)
        assert d.score == 85.0

    def test_margin_boundary_7pct(self):
        s = _scorer()
        d = s._score_margin(None, None, 0.07)
        assert d.score == 65.0

    def test_result_frozen(self):
        s = _scorer()
        result = s.score(**_full_inputs())
        with pytest.raises(AttributeError):
            result.regime_score = 99.0  # type: ignore[misc]

    def test_dimension_score_frozen(self):
        s = _scorer()
        d = s._score_cape(0.90, None)
        with pytest.raises(AttributeError):
            d.score = 99.0  # type: ignore[misc]
