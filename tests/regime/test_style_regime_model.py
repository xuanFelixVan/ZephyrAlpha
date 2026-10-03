# [BLUEPRINT] MOD-REGIME-014 | docs/03_modules/_domain_regime/style_regime_model/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-REGIME-014 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.regime.test_style_regime_model
# [TESTS] src/zephyr/regime/style_regime_model.py
"""MOD-REGIME-014 单元测试：style_regime_model 市场风格体制识别模型。

蓝图验收（B10-01447/CAND-CYCLE-006，A1 模块32）：
大小盘/价值成长收益差风格序列构建 + HMM 风格态识别（注入 hmm_runner，
未装 hmmlearn 降级规则分档：差值正负+幅度阈值）+ 风格→策略参数映射表 +
风格切换确认（连续 N 期同向防抖）。hmm_runner 全注入内存替身，不触网。
"""

from __future__ import annotations

import pytest

pytest.importorskip(
    "zephyr.regime.style_regime_model",
    reason="style_regime_model not importable",
)

from zephyr.regime.style_regime_model import (  # noqa: E402
    SizeAxis,
    StyleParams,
    StyleReading,
    StyleRegimeError,
    StyleRegimeModel,
    StyleState,
    size_axis_of,
)

_PARAM_MAP = {
    StyleState.LARGE_VALUE: StyleParams(0.6, "大盘价值蓝筹", 10),
    StyleState.LARGE_GROWTH: StyleParams(0.7, "大盘成长赛道", 5),
    StyleState.SMALL_VALUE: StyleParams(0.4, "小盘价值挖掘", 10),
    StyleState.SMALL_GROWTH: StyleParams(0.5, "小盘成长弹性", 3),
}


def _model(**kwargs) -> StyleRegimeModel:
    kwargs.setdefault("param_map", _PARAM_MAP)
    return StyleRegimeModel(**kwargs)


# ──────────────────────────────────────────────────────────────────────────────
# 风格序列构建
# ──────────────────────────────────────────────────────────────────────────────


class TestBuildSpread:
    def test_spread_ok(self) -> None:
        spread = StyleRegimeModel.build_spread_series([0.03, 0.01], [0.01, 0.02])
        assert spread == pytest.approx((0.02, -0.01))

    def test_length_mismatch_raises(self) -> None:
        with pytest.raises(StyleRegimeError):
            StyleRegimeModel.build_spread_series([0.01, 0.02], [0.01])

    def test_empty_raises(self) -> None:
        with pytest.raises(StyleRegimeError):
            StyleRegimeModel.build_spread_series([], [])

    def test_non_finite_raises(self) -> None:
        with pytest.raises(StyleRegimeError):
            StyleRegimeModel.build_spread_series([0.01, float("nan")], [0.01, 0.02])
        with pytest.raises(StyleRegimeError):
            StyleRegimeModel.build_spread_series([0.01], [float("inf")])


# ──────────────────────────────────────────────────────────────────────────────
# 规则降级分档（差值正负 + 幅度阈值）
# ──────────────────────────────────────────────────────────────────────────────


class TestRuleFallback:
    def test_large_value(self) -> None:
        raw, used_hmm = _model().identify_raw([0.02], [0.01])
        assert raw == (StyleState.LARGE_VALUE,)
        assert used_hmm is False

    def test_large_growth(self) -> None:
        raw, _ = _model().identify_raw([0.02], [-0.01])
        assert raw == (StyleState.LARGE_GROWTH,)

    def test_small_growth(self) -> None:
        raw, _ = _model().identify_raw([-0.02], [-0.01])
        assert raw == (StyleState.SMALL_GROWTH,)

    def test_within_band_undetermined(self) -> None:
        raw, _ = _model().identify_raw([0.001], [0.02])  # 大小盘差落阈值带内
        assert raw == (None,)
        raw2, _ = _model().identify_raw([0.02], [-0.001])  # 价值成长差落带内
        assert raw2 == (None,)

    def test_invalid_spread_raises(self) -> None:
        with pytest.raises(StyleRegimeError):
            _model().identify_raw([], [])
        with pytest.raises(StyleRegimeError):
            _model().identify_raw([0.01, 0.02], [0.01])
        with pytest.raises(StyleRegimeError):
            _model().identify_raw([float("nan")], [0.01])


# ──────────────────────────────────────────────────────────────────────────────
# HMM 注入路径
# ──────────────────────────────────────────────────────────────────────────────


class TestHmmPath:
    def test_hmm_labels_used(self) -> None:
        runner = lambda size, value: ["large_value", "small_growth"]
        raw, used_hmm = _model(hmm_runner=runner).identify_raw([0.0, 0.0], [0.0, 0.0])
        assert raw == (StyleState.LARGE_VALUE, StyleState.SMALL_GROWTH)
        assert used_hmm is True

    def test_hmm_length_mismatch_raises(self) -> None:
        runner = lambda size, value: ["large_value"]
        with pytest.raises(StyleRegimeError):
            _model(hmm_runner=runner).identify_raw([0.0, 0.0], [0.0, 0.0])

    def test_hmm_bad_label_raises(self) -> None:
        runner = lambda size, value: ["mega_cap"]
        with pytest.raises(StyleRegimeError):
            _model(hmm_runner=runner).identify_raw([0.0], [0.0])


# ──────────────────────────────────────────────────────────────────────────────
# 切换确认（连续 N 期同向防抖）
# ──────────────────────────────────────────────────────────────────────────────


class TestConfirm:
    LV, SG = StyleState.LARGE_VALUE, StyleState.SMALL_GROWTH

    def test_switch_after_n_consecutive(self) -> None:
        m = _model(confirm_periods=3)
        out = m.confirm([self.LV, self.SG, self.SG, self.SG])
        assert out == (self.LV, self.LV, self.LV, self.SG)  # 第 3 连击才切换

    def test_intermittent_no_switch(self) -> None:
        m = _model(confirm_periods=3)
        out = m.confirm([self.LV, self.SG, self.LV, self.SG, self.SG])
        assert out == (self.LV,) * 5  # 候选连击被打断不切换

    def test_n1_immediate_switch(self) -> None:
        m = _model(confirm_periods=1)
        out = m.confirm([self.LV, self.SG])
        assert out == (self.LV, self.SG)

    def test_none_keeps_previous_and_breaks_streak(self) -> None:
        m = _model(confirm_periods=2)
        out = m.confirm([self.LV, None, self.SG, None, self.SG])
        assert out == (self.LV,) * 5  # 未决期保旧态但中断候选连击

    def test_leading_none_backfilled(self) -> None:
        m = _model(confirm_periods=2)
        out = m.confirm([None, None, self.SG, self.SG])
        assert out == (self.SG,) * 4  # 前导未决回填首个确认态

    def test_all_none_raises(self) -> None:
        with pytest.raises(StyleRegimeError):
            _model().confirm([None, None])
        with pytest.raises(StyleRegimeError):
            _model().confirm([])


# ──────────────────────────────────────────────────────────────────────────────
# 参数映射 + 一体识别
# ──────────────────────────────────────────────────────────────────────────────


class TestParamsAndAnalyze:
    def test_params_for_all_states(self) -> None:
        m = _model()
        for state in StyleState:
            assert m.params_for(state) is _PARAM_MAP[state]

    def test_missing_state_in_map_raises(self) -> None:
        bad = {k: v for k, v in _PARAM_MAP.items() if k is not StyleState.SMALL_GROWTH}
        with pytest.raises(StyleRegimeError):
            _model(param_map=bad)

    def test_bad_config_raises(self) -> None:
        with pytest.raises(StyleRegimeError):
            _model(magnitude_threshold=-0.1)
        with pytest.raises(StyleRegimeError):
            _model(confirm_periods=0)
        with pytest.raises(StyleRegimeError):
            StyleParams(1.5, "x", 5)
        with pytest.raises(StyleRegimeError):
            StyleParams(0.5, "", 5)
        with pytest.raises(StyleRegimeError):
            StyleParams(0.5, "x", 0)

    def test_analyze_rule_path(self) -> None:
        m = _model(confirm_periods=2)
        reading = m.analyze(
            large_returns=[0.03, 0.02, 0.02],
            small_returns=[0.01, 0.01, 0.01],
            value_returns=[0.02, 0.02, 0.02],
            growth_returns=[0.01, 0.01, 0.01],
        )
        assert isinstance(reading, StyleReading)
        assert reading.current is StyleState.LARGE_VALUE
        assert reading.used_hmm is False
        assert reading.params.focus == "大盘价值蓝筹"
        assert reading.confirmed_states == (StyleState.LARGE_VALUE,) * 3

    def test_analyze_hmm_path(self) -> None:
        runner = lambda size, value: ["small_growth"] * len(size)
        reading = _model(hmm_runner=runner).analyze([0.0], [0.0], [0.0], [0.0])
        assert reading.current is StyleState.SMALL_GROWTH
        assert reading.used_hmm is True
        assert reading.params.focus == "小盘成长弹性"

    def test_size_axis_mapping(self) -> None:
        assert size_axis_of(StyleState.LARGE_VALUE) is SizeAxis.LARGE
        assert size_axis_of(StyleState.LARGE_GROWTH) is SizeAxis.LARGE
        assert size_axis_of(StyleState.SMALL_VALUE) is SizeAxis.SMALL
        assert size_axis_of(StyleState.SMALL_GROWTH) is SizeAxis.SMALL
        with pytest.raises(StyleRegimeError):
            size_axis_of("large_value")

    def test_determinism(self) -> None:
        m = _model(confirm_periods=2)
        args = ([0.03, 0.01, -0.02], [0.01, 0.02, 0.01], [0.02, -0.01, -0.02], [0.01, 0.01, -0.01])
        r1 = m.analyze(*args)
        r2 = m.analyze(*args)
        assert r1 == r2


# ──────────────────────────────────────────────────────────────────────────────
# 宏观敏感度投影（L08-WO-2：MacroRegimeSensor→caution_factor/tier 附注位）
# ──────────────────────────────────────────────────────────────────────────────


class TestMacroProjection:
    @pytest.fixture(autouse=True)
    def _hermetic_macro(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """全文件气密：缺省 live 读数桩化（不触真传感器/CH），既有用例零感知。"""
        monkeypatch.setattr(
            "zephyr.regime.style_regime_model._default_macro_reading",
            lambda: {"caution_factor": 0.85, "tier": "cautious", "weather_score": 32.0},
        )

    _ARGS = ([0.03, 0.02], [0.01, 0.01], [0.02, 0.02], [0.01, 0.01])

    def test_a_sensor_ok_macro_attached(self) -> None:
        """a 传感器正常（注入桩）→ 合成包含宏观项（caution_factor/tier 附注）。"""
        reading = _model(macro_reading_provider=lambda: {"caution_factor": 1.1, "tier": "cautious"}).analyze(
            *self._ARGS
        )
        assert reading.macro_caution_factor == pytest.approx(1.1)
        assert reading.macro_tier == "cautious"
        # 注入优先于缺省桩：缺省桩 0.85 未被采用
        assert reading.macro_caution_factor != pytest.approx(0.85)

    def test_a2_default_provider_used_when_not_injected(self) -> None:
        """未注入 → 走缺省读数（本文件已桩化=live 惰性位被调用的证据）。"""
        reading = _model().analyze(*self._ARGS)
        assert reading.macro_caution_factor == pytest.approx(0.85)
        assert reading.macro_tier == "cautious"

    def test_b_sensor_exception_degrades(self) -> None:
        """b 传感器异常 → 降级置 None，风格合成照常产出（不阻断）。"""

        def _boom() -> dict[str, object]:
            raise RuntimeError("sensor down")

        reading = _model(macro_reading_provider=_boom).analyze(*self._ARGS)
        assert reading.macro_caution_factor is None
        assert reading.macro_tier is None
        assert reading.current is StyleState.LARGE_VALUE  # 主合成不受影响

    def test_b2_bad_reading_degrades(self) -> None:
        """读数非法（非 Mapping/NaN caution）→ 同降级置 None。"""
        r1 = _model(macro_reading_provider=lambda: "not-a-mapping").analyze(*self._ARGS)  # type: ignore[arg-type,return-value]
        assert r1.macro_caution_factor is None and r1.macro_tier is None
        r2 = _model(macro_reading_provider=lambda: {"caution_factor": float("nan"), "tier": "no_data"}).analyze(
            *self._ARGS
        )
        assert r2.macro_caution_factor is None
        assert r2.macro_tier == "no_data"  # tier 合法字符串照附注，caution 非有限→None

    def test_no_macro_fields_default_none(self) -> None:
        """直接构造 StyleReading（旧调用方）→ 宏观字段默认 None（向后兼容）。"""
        from dataclasses import fields

        assert {f.name for f in fields(StyleReading)} >= {"macro_caution_factor", "macro_tier"}
