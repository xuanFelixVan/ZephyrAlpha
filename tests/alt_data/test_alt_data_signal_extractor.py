# [BLUEPRINT] MOD-ALT-013 | docs/03_modules/_domain_alt_data/alt_data_signal_extractor/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-ALT-013 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.alt_data.test_alt_data_signal_extractor
# [TESTS] src/zephyr/alt_data/alt_data_signal_extractor.py
"""MOD-ALT-013 单元测试：alt_data_signal_extractor 另类数据信号提取网关。

蓝图验收（B5-07085/CAND-TESTA-023，B5 D-ALT-DATA-05）：
特征注册表 + IC 测试（注入计算器，∈[-1,1] 闭合校验）+ 衰减分析 +
正交化（注入回归器取残差，未注入 Fail-Closed）+ CTR-002 兼容输出
（注入校验器，拒绝即 Fail-Closed）。ic/回归/校验/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.alt_data.alt_data_signal_extractor",
    reason="alt_data_signal_extractor not importable",
)

from zephyr.alt_data.alt_data_signal_extractor import (  # noqa: E402
    AltDataSignalExtractor,
    AltSignalExtractorError,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)


def _ic_ok(fv, fr) -> float:
    return 0.08  # 内存替身：固定合法 IC


def _regressor_demean(target, proxies):
    mean = sum(target) / len(target)
    return [v - mean for v in target]  # 内存替身：去均值残差


def _validator_ok(signal) -> bool:
    return True


def _extractor(
    *,
    ic_calculator=_ic_ok,
    regressor=None,
    validator=None,
    ic_threshold: float = 0.03,
) -> AltDataSignalExtractor:
    return AltDataSignalExtractor(
        ic_calculator=ic_calculator,
        ic_threshold=ic_threshold,
        regressor=regressor,
        validator=validator,
        clock=lambda: _T0,
    )


def _registered(ext: AltDataSignalExtractor, fid: str = "social_heat") -> str:
    ext.register_feature(fid, description="社媒热度", half_life_days=10.0)
    return fid


# ──────────────────────────────────────────────────────────────────────────────
# 构造期 Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestConfig:
    def test_missing_ic_calculator_raises(self) -> None:
        with pytest.raises(AltSignalExtractorError):
            AltDataSignalExtractor(ic_calculator=None, clock=lambda: _T0)

    def test_ic_threshold_out_of_range_raises(self) -> None:
        with pytest.raises(AltSignalExtractorError):
            _extractor(ic_threshold=1.5)


# ──────────────────────────────────────────────────────────────────────────────
# 特征注册表
# ──────────────────────────────────────────────────────────────────────────────


class TestFeatureRegistry:
    def test_register_ok(self) -> None:
        ext = _extractor()
        feat = ext.register_feature("f1", description="d", half_life_days=5.0)
        assert feat.feature_id == "f1"
        assert feat.half_life_days == 5.0

    def test_register_blank_id_raises(self) -> None:
        ext = _extractor()
        with pytest.raises(AltSignalExtractorError):
            ext.register_feature(" ", half_life_days=5.0)

    def test_register_duplicate_raises(self) -> None:
        ext = _extractor()
        _registered(ext)
        with pytest.raises(AltSignalExtractorError):
            ext.register_feature("social_heat", half_life_days=3.0)

    def test_register_nonpositive_half_life_raises(self) -> None:
        ext = _extractor()
        with pytest.raises(AltSignalExtractorError):
            ext.register_feature("f1", half_life_days=0.0)

    def test_features_sorted(self) -> None:
        ext = _extractor()
        ext.register_feature("b_feat", half_life_days=1.0)
        ext.register_feature("a_feat", half_life_days=1.0)
        assert [f.feature_id for f in ext.features()] == ["a_feat", "b_feat"]


# ──────────────────────────────────────────────────────────────────────────────
# IC 测试
# ──────────────────────────────────────────────────────────────────────────────


class TestIc:
    def test_ic_pass(self) -> None:
        ext = _extractor()
        fid = _registered(ext)
        result = ext.test_ic(fid, [1.0, 2.0, 3.0], [0.01, 0.02, 0.03])
        assert result.ic == pytest.approx(0.08)
        assert result.passed is True
        assert result.sample_size == 3

    def test_ic_below_threshold_fails(self) -> None:
        ext = _extractor(ic_calculator=lambda fv, fr: 0.01, ic_threshold=0.03)
        fid = _registered(ext)
        assert ext.test_ic(fid, [1.0, 2.0], [0.1, 0.2]).passed is False

    def test_ic_unknown_feature_raises(self) -> None:
        ext = _extractor()
        with pytest.raises(AltSignalExtractorError):
            ext.test_ic("ghost", [1.0, 2.0], [0.1, 0.2])

    def test_ic_length_mismatch_raises(self) -> None:
        ext = _extractor()
        fid = _registered(ext)
        with pytest.raises(AltSignalExtractorError):
            ext.test_ic(fid, [1.0, 2.0], [0.1])

    def test_ic_insufficient_samples_raises(self) -> None:
        ext = _extractor()
        fid = _registered(ext)
        with pytest.raises(AltSignalExtractorError):
            ext.test_ic(fid, [1.0], [0.1])

    def test_ic_out_of_range_calculator_violation_raises(self) -> None:
        ext = _extractor(ic_calculator=lambda fv, fr: 1.5)
        fid = _registered(ext)
        with pytest.raises(AltSignalExtractorError):
            ext.test_ic(fid, [1.0, 2.0], [0.1, 0.2])

    def test_ic_calculator_exception_raises(self) -> None:
        def boom(fv, fr):
            raise RuntimeError("calc down")

        ext = _extractor(ic_calculator=boom)
        fid = _registered(ext)
        with pytest.raises(AltSignalExtractorError):
            ext.test_ic(fid, [1.0, 2.0], [0.1, 0.2])

    def test_ic_negative_abs_passes(self) -> None:
        ext = _extractor(ic_calculator=lambda fv, fr: -0.5)
        fid = _registered(ext)
        assert ext.test_ic(fid, [1.0, 2.0], [0.1, 0.2]).passed is True


# ──────────────────────────────────────────────────────────────────────────────
# 衰减分析
# ──────────────────────────────────────────────────────────────────────────────


class TestDecay:
    def test_decay_weight_half_life(self) -> None:
        ext = _extractor()
        fid = _registered(ext)
        assert ext.decay_weight(fid, 0.0) == 1.0
        assert ext.decay_weight(fid, 10.0) == pytest.approx(0.5)
        assert ext.decay_weight(fid, 20.0) == pytest.approx(0.25)

    def test_decay_negative_age_raises(self) -> None:
        ext = _extractor()
        fid = _registered(ext)
        with pytest.raises(AltSignalExtractorError):
            ext.decay_weight(fid, -1.0)

    def test_analyze_decay_batch(self) -> None:
        ext = _extractor()
        fid = _registered(ext)
        weights = ext.analyze_decay(fid, [0.0, 10.0, 30.0])
        assert weights[0] == 1.0
        assert weights[1] == pytest.approx(0.5)
        assert weights[2] == pytest.approx(0.125)


# ──────────────────────────────────────────────────────────────────────────────
# 正交化
# ──────────────────────────────────────────────────────────────────────────────


class TestOrthogonalize:
    def test_orthogonalize_ok(self) -> None:
        ext = _extractor(regressor=_regressor_demean)
        fid = _registered(ext)
        residuals = ext.orthogonalize(
            fid, [1.0, 2.0, 3.0], {"industry": [0.0, 1.0, 0.0], "mktcap": [10.0, 20.0, 30.0]}
        )
        assert residuals == pytest.approx((-1.0, 0.0, 1.0))

    def test_regressor_not_injected_fail_closed(self) -> None:
        ext = _extractor()
        fid = _registered(ext)
        with pytest.raises(AltSignalExtractorError):
            ext.orthogonalize(fid, [1.0, 2.0], {"industry": [0.0, 1.0]})

    def test_empty_proxies_raises(self) -> None:
        ext = _extractor(regressor=_regressor_demean)
        fid = _registered(ext)
        with pytest.raises(AltSignalExtractorError):
            ext.orthogonalize(fid, [1.0, 2.0], {})

    def test_proxy_length_mismatch_raises(self) -> None:
        ext = _extractor(regressor=_regressor_demean)
        fid = _registered(ext)
        with pytest.raises(AltSignalExtractorError):
            ext.orthogonalize(fid, [1.0, 2.0], {"industry": [0.0]})

    def test_residual_length_violation_raises(self) -> None:
        ext = _extractor(regressor=lambda t, p: [0.0])
        fid = _registered(ext)
        with pytest.raises(AltSignalExtractorError):
            ext.orthogonalize(fid, [1.0, 2.0], {"industry": [0.0, 1.0]})


# ──────────────────────────────────────────────────────────────────────────────
# CTR-002 统一出口
# ──────────────────────────────────────────────────────────────────────────────


class TestEmitSignal:
    def test_emit_ok(self) -> None:
        seen: list = []
        ext = _extractor(validator=lambda s: seen.append(s) or True)
        fid = _registered(ext)
        signal = ext.emit_signal(fid, {"000002": 0.5, "000001": 0.9}, as_of=_T0, ic=0.08)
        assert signal["contract"] == "CTR-002"
        assert signal["factor_id"] == fid
        assert list(signal["values"]) == ["000001", "000002"]  # 确定性排序
        assert signal["advisory"] is True
        assert seen == [signal]  # 经注入校验器

    def test_emit_validator_not_injected_fail_closed(self) -> None:
        ext = _extractor()
        fid = _registered(ext)
        with pytest.raises(AltSignalExtractorError):
            ext.emit_signal(fid, {"000001": 0.9}, as_of=_T0)

    def test_emit_validator_rejected_fail_closed(self) -> None:
        ext = _extractor(validator=lambda s: False)
        fid = _registered(ext)
        with pytest.raises(AltSignalExtractorError):
            ext.emit_signal(fid, {"000001": 0.9}, as_of=_T0)

    def test_emit_empty_values_raises(self) -> None:
        ext = _extractor(validator=_validator_ok)
        fid = _registered(ext)
        with pytest.raises(AltSignalExtractorError):
            ext.emit_signal(fid, {}, as_of=_T0)

    def test_emit_future_as_of_raises(self) -> None:
        ext = _extractor(validator=_validator_ok)
        fid = _registered(ext)
        future = _T0 + datetime.timedelta(days=1)
        with pytest.raises(AltSignalExtractorError):
            ext.emit_signal(fid, {"000001": 0.9}, as_of=future)

    def test_emit_ic_out_of_range_raises(self) -> None:
        ext = _extractor(validator=_validator_ok)
        fid = _registered(ext)
        with pytest.raises(AltSignalExtractorError):
            ext.emit_signal(fid, {"000001": 0.9}, as_of=_T0, ic=2.0)

    def test_determinism_same_input_same_output(self) -> None:
        def run() -> dict:
            ext = _extractor(validator=_validator_ok)
            fid = _registered(ext)
            return ext.emit_signal(fid, {"b": 1.0, "a": 2.0}, as_of=_T0, ic=-0.1)

        assert run() == run()
