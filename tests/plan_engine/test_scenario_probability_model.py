# [A_test] module_id: MOD-PLAN-017 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PLAN-017 | 待统筹登记 | 45号 §4 W2 + 缺口总账 GAP-F-01
# [MODULE] tests.plan_engine.test_scenario_probability_model
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""ScenarioProbabilityModel (MOD-PLAN-017) 施工验证测试。

覆盖：
- base_rate_distribution 纯函数：足样本 Laplace 平滑经验频率/样本不足均匀兜底+
  degraded 低置信/越界情景与非法参数 fail-closed。
- map_state_distribution / state_conditional_distribution 纯函数：8 态→9 格
  条件质量映射（单态 100%/VIOLENT 均匀摊 9 格/字符串键/浮点尾差重归一）；
  态键越界/概率越界/行和偏离 fail-closed。
- density_grid_distribution 纯函数：分位数带→准蒙特卡洛 9 格折算（正带→上行格/
  负带→下行格/零带→洗盘格/大涨带→高开高走格）；确定性；非单调/非有限/点不足
  fail-closed。
- fuse_distributions 纯函数：权重和=1 fail-closed/缺层重归一+degraded 留痕/
  每格置信度（全一致=层自置信加权，分歧大→低置信）。
- ScenarioProbabilityModel 注入隔离组合：fake query_fn/fake providers 三层合成；
  PIT 窗口过滤；供给异常 fail-open 缺层降级；三层全缺 fail-closed；
  forecast_and_record tmp 库落库幂等 + 落库失败 fail-open -1。
全 tmp 库+fake 注入隔离，不触真 governance.db/不触真训练。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.plan_engine.premarket_constraint_loader import SCENARIO_LIST
from zephyr.plan_engine.scenario_probability_model import (
    LAYER_BASE_RATE,
    LAYER_DENSITY_HEAD,
    LAYER_STATE_CONDITIONAL,
    MODULE_LOG_NAME,
    PREDICTION_TYPE_SCENARIO_PROBABILITY,
    LayerDistribution,
    ScenarioProbabilityConfig,
    ScenarioProbabilityModel,
    base_rate_distribution,
    build_scenario_probability_forecast,
    density_grid_distribution,
    fuse_distributions,
    map_state_distribution,
    state_conditional_distribution,
)
from zephyr.reporting.prediction_log_writer import (
    ensure_prediction_log_table,
    query_predictions,
)
from zephyr.signal_ashare.next_day_8state_forecast import NextDayForecast, NextDayState

TRADE_DATE = "2026-08-21"
_WEIGHTS = {
    LAYER_BASE_RATE: 0.5,
    LAYER_STATE_CONDITIONAL: 0.3,
    LAYER_DENSITY_HEAD: 0.2,
}


def _sum1(probs: dict[str, float]) -> float:
    return sum(probs.values())


# ══════════════════════════════════════════════════════════════
# base_rate_distribution 纯函数
# ══════════════════════════════════════════════════════════════


class TestBaseRateDistribution:
    def test_sufficient_samples_empirical(self) -> None:
        actuals = ["HIGH_OPEN_REAL_UP"] * 30 + ["FLAT_OPEN_WASH"] * 10
        layer = base_rate_distribution(actuals, min_base_samples=20, support_full=40, laplace_alpha=1.0)
        assert layer.name == LAYER_BASE_RATE
        assert layer.degraded is False
        assert layer.sample_size == 40
        assert layer.confidence == pytest.approx(1.0)
        # Laplace(α=1)：p(HIGH_OPEN_REAL_UP)=(30+1)/(40+9)=31/49
        assert layer.probabilities["HIGH_OPEN_REAL_UP"] == pytest.approx(31 / 49)
        assert layer.probabilities["FLAT_OPEN_WASH"] == pytest.approx(11 / 49)
        assert _sum1(layer.probabilities) == pytest.approx(1.0)

    def test_confidence_scales_with_samples(self) -> None:
        actuals = ["LOW_OPEN_WASH"] * 30
        layer = base_rate_distribution(actuals, min_base_samples=20, support_full=60, laplace_alpha=0.0)
        assert layer.confidence == pytest.approx(0.5)
        # α=0 无平滑：单格全质量
        assert layer.probabilities["LOW_OPEN_WASH"] == pytest.approx(1.0)

    def test_insufficient_samples_uniform_degraded(self) -> None:
        layer = base_rate_distribution(["HIGH_OPEN_WASH"] * 3, min_base_samples=20, support_full=60)
        assert layer.degraded is True
        assert layer.sample_size == 3
        assert layer.confidence == pytest.approx(3 / 60)
        assert all(p == pytest.approx(1 / 9) for p in layer.probabilities.values())
        assert layer.detail["reason"] == "insufficient_samples"

    def test_empty_uniform_degraded(self) -> None:
        layer = base_rate_distribution([], min_base_samples=20)
        assert layer.degraded is True
        assert _sum1(layer.probabilities) == pytest.approx(1.0)

    def test_invalid_scenario_fail_closed(self) -> None:
        with pytest.raises(ValueError):
            base_rate_distribution(["NOT_A_SCENARIO"] * 30, min_base_samples=20)

    def test_invalid_params_fail_closed(self) -> None:
        with pytest.raises(ValueError):
            base_rate_distribution([], min_base_samples=0)
        with pytest.raises(ValueError):
            base_rate_distribution([], min_base_samples=20, support_full=10)
        with pytest.raises(ValueError):
            base_rate_distribution([], laplace_alpha=-1.0)


# ══════════════════════════════════════════════════════════════
# map_state_distribution / state_conditional_distribution 纯函数
# ══════════════════════════════════════════════════════════════


class TestMapStateDistribution:
    def test_single_state_full_mass(self) -> None:
        grid = map_state_distribution({NextDayState.GAP_UP_UP: 1.0})
        assert grid["HIGH_OPEN_REAL_UP"] == pytest.approx(1.0)
        assert _sum1(grid) == pytest.approx(1.0)
        assert len(grid) == 9

    def test_violent_spreads_uniform(self) -> None:
        grid = map_state_distribution({NextDayState.VIOLENT: 1.0})
        assert all(p == pytest.approx(1 / 9) for p in grid.values())

    def test_flat_close_maps_to_flat_wash(self) -> None:
        grid = map_state_distribution({"FLAT_CLOSE": 1.0})  # 字符串键兼容
        assert grid["FLAT_OPEN_WASH"] == pytest.approx(1.0)

    def test_mixture_weighted(self) -> None:
        grid = map_state_distribution(
            {NextDayState.GAP_DOWN_DOWN: 0.5, NextDayState.FLAT_UP: 0.5}
        )
        assert grid["LOW_OPEN_REAL_DOWN"] == pytest.approx(0.5)
        assert grid["FLAT_OPEN_REAL_UP"] == pytest.approx(0.5)

    def test_fp_tail_tolerance_renormalized(self) -> None:
        grid = map_state_distribution({NextDayState.FLAT_UP: 0.1 + 0.1 + 0.1 + 0.7})  # 0.3 浮点尾差
        assert _sum1(grid) == pytest.approx(1.0)

    def test_invalid_fail_closed(self) -> None:
        with pytest.raises(ValueError):
            map_state_distribution({})  # 空映射
        with pytest.raises(ValueError):
            map_state_distribution({"BOGUS_STATE": 1.0})  # 态键越界
        with pytest.raises(ValueError):
            map_state_distribution({NextDayState.FLAT_UP: 1.2})  # 概率越界
        with pytest.raises(ValueError):
            map_state_distribution({NextDayState.FLAT_UP: 0.5})  # 行和偏离 >1e-4
        with pytest.raises(ValueError):
            map_state_distribution({123: 1.0})  # 键类型非法


class TestStateConditionalDistribution:
    def test_next_day_forecast_passthrough(self) -> None:
        forecast = NextDayForecast(
            current_state=NextDayState.FLAT_UP,
            probabilities={s: 0.0 for s in NextDayState}
            | {NextDayState.FLAT_UP: 0.7, NextDayState.FLAT_DOWN: 0.3},
            top_state=NextDayState.FLAT_UP,
            top_probability=0.7,
            confidence=0.8,
            n_transitions=120,
        )
        layer = state_conditional_distribution(forecast)
        assert layer.name == LAYER_STATE_CONDITIONAL
        assert layer.confidence == pytest.approx(0.8)
        assert layer.sample_size == 120
        assert layer.probabilities["FLAT_OPEN_REAL_UP"] == pytest.approx(0.7)
        assert _sum1(layer.probabilities) == pytest.approx(1.0)

    def test_mapping_defaults(self) -> None:
        layer = state_conditional_distribution({NextDayState.GAP_UP_DOWN: 1.0})
        assert layer.confidence == pytest.approx(0.5)  # 中性先验
        assert layer.sample_size == 0
        assert layer.probabilities["HIGH_OPEN_FAKE_UP"] == pytest.approx(1.0)

    def test_invalid_type_fail_closed(self) -> None:
        with pytest.raises(ValueError):
            state_conditional_distribution(42)  # type: ignore[arg-type]
        with pytest.raises(ValueError):
            state_conditional_distribution({NextDayState.FLAT_UP: 1.0}, sample_size=-1)


# ══════════════════════════════════════════════════════════════
# density_grid_distribution 纯函数
# ══════════════════════════════════════════════════════════════


class TestDensityGridDistribution:
    def test_positive_band_up_cells(self) -> None:
        # 分位带全正（+1%~+3%）：gap_share=0.4 → g∈[0.4%,1.2%]<2% 平开；t∈[0.6%,1.8%]>0.3% 高走
        qs = {0.1: 0.01, 0.25: 0.015, 0.5: 0.02, 0.75: 0.025, 0.9: 0.03}
        layer = density_grid_distribution(qs, mc_samples=1000)
        assert layer.probabilities["FLAT_OPEN_REAL_UP"] == pytest.approx(1.0)
        assert _sum1(layer.probabilities) == pytest.approx(1.0)
        assert layer.sample_size == 1000
        assert layer.confidence == pytest.approx(0.5)

    def test_negative_band_down_cell(self) -> None:
        qs = {0.1: -0.03, 0.25: -0.02, 0.5: -0.015, 0.75: -0.012, 0.9: -0.01}
        layer = density_grid_distribution(qs, mc_samples=1000)
        assert layer.probabilities["FLAT_OPEN_REAL_DOWN"] == pytest.approx(1.0)

    def test_large_positive_high_open_real_up(self) -> None:
        # 大涨带（+6%~+9%，含尾部外推仍 ≥+5%）：g=r*0.4≥2% 高开；t=r*0.6>0.3% 高走
        qs = {0.1: 0.06, 0.25: 0.065, 0.5: 0.07, 0.75: 0.08, 0.9: 0.09}
        layer = density_grid_distribution(qs, mc_samples=1000)
        assert layer.probabilities["HIGH_OPEN_REAL_UP"] == pytest.approx(1.0)

    def test_zero_band_wash_cell(self) -> None:
        qs = {0.1: -0.001, 0.25: -0.0005, 0.5: 0.0, 0.75: 0.0005, 0.9: 0.001}
        layer = density_grid_distribution(qs, mc_samples=1000)
        assert layer.probabilities["FLAT_OPEN_WASH"] == pytest.approx(1.0)

    def test_deterministic(self) -> None:
        qs = {0.1: -0.02, 0.25: -0.005, 0.5: 0.01, 0.75: 0.02, 0.9: 0.035}
        a = density_grid_distribution(qs, mc_samples=500)
        b = density_grid_distribution(qs, mc_samples=500)
        assert a.probabilities == b.probabilities

    def test_mass_spread_across_cells(self) -> None:
        # 宽带跨零：质量应散布多格且行和=1
        qs = {0.1: -0.06, 0.25: -0.02, 0.5: 0.0, 0.75: 0.03, 0.9: 0.08}
        layer = density_grid_distribution(qs, mc_samples=2000)
        non_zero = sum(1 for p in layer.probabilities.values() if p > 0)
        assert non_zero >= 3
        assert _sum1(layer.probabilities) == pytest.approx(1.0)

    def test_invalid_fail_closed(self) -> None:
        with pytest.raises(ValueError):
            density_grid_distribution({0.5: 0.01})  # 点不足
        with pytest.raises(ValueError):
            density_grid_distribution({0.1: 0.02, 0.5: 0.01, 0.9: 0.03})  # 非单调
        with pytest.raises(ValueError):
            density_grid_distribution({0.1: 0.01, 0.9: float("nan")})  # 非有限
        with pytest.raises(ValueError):
            density_grid_distribution({0.0: 0.01, 0.9: 0.02})  # 键越界（0 不在 (0,1)）
        with pytest.raises(ValueError):
            density_grid_distribution({0.5: 0.01, 1.0: 0.02})  # 键越界（1 不在 (0,1)）
        with pytest.raises(ValueError):
            density_grid_distribution({0.1: 0.01, 0.9: 0.02}, mc_samples=0)
        with pytest.raises(ValueError):
            density_grid_distribution({0.1: 0.01, 0.9: 0.02}, gap_share=1.5)


# ══════════════════════════════════════════════════════════════
# fuse_distributions 纯函数
# ══════════════════════════════════════════════════════════════


def _layer(name: str, probs: dict[str, float], conf: float = 1.0, degraded: bool = False) -> LayerDistribution:
    full = {s: 0.0 for s in SCENARIO_LIST} | probs
    return LayerDistribution(
        name=name,
        probabilities=full,
        confidence=conf,
        sample_size=10,
        degraded=degraded,
    )


class TestFuseDistributions:
    def test_three_layer_weighted_sum(self) -> None:
        base = _layer(LAYER_BASE_RATE, {s: 1 / 9 for s in SCENARIO_LIST})
        state = _layer(LAYER_STATE_CONDITIONAL, {"FLAT_OPEN_REAL_UP": 1.0})
        density = _layer(LAYER_DENSITY_HEAD, {"FLAT_OPEN_REAL_UP": 1.0})
        fused, cell_conf, meta = fuse_distributions([base, state, density], _WEIGHTS)
        # 0.5/9 + 0.3 + 0.2 = 0.5/9 + 0.5
        assert fused["FLAT_OPEN_REAL_UP"] == pytest.approx(0.5 / 9 + 0.5)
        assert fused["HIGH_OPEN_WASH"] == pytest.approx(0.5 / 9)
        assert _sum1(fused) == pytest.approx(1.0)
        assert meta["degraded_layers"] == []
        assert meta["weights_used"] == pytest.approx(_WEIGHTS)

    def test_missing_layer_renormalized(self) -> None:
        base = _layer(LAYER_BASE_RATE, {"HIGH_OPEN_REAL_UP": 1.0})
        state = _layer(LAYER_STATE_CONDITIONAL, {"FLAT_OPEN_REAL_UP": 1.0})
        fused, _, meta = fuse_distributions([base, state], _WEIGHTS)
        # 缺密度层：0.5/0.8=0.625、0.3/0.8=0.375
        assert meta["weights_used"][LAYER_BASE_RATE] == pytest.approx(0.625)
        assert meta["weights_used"][LAYER_STATE_CONDITIONAL] == pytest.approx(0.375)
        assert meta["degraded_layers"] == [LAYER_DENSITY_HEAD]
        assert fused["HIGH_OPEN_REAL_UP"] == pytest.approx(0.625)
        assert fused["FLAT_OPEN_REAL_UP"] == pytest.approx(0.375)

    def test_identical_layers_full_agreement(self) -> None:
        la = _layer(LAYER_BASE_RATE, {"LOW_OPEN_WASH": 1.0}, conf=0.9)
        lb = _layer(LAYER_STATE_CONDITIONAL, {"LOW_OPEN_WASH": 1.0}, conf=0.7)
        _, cell_conf, meta = fuse_distributions([la, lb], {LAYER_BASE_RATE: 0.6, LAYER_STATE_CONDITIONAL: 0.4})
        # 层间零分歧 → agreement=1 → 格置信=层自置信加权
        assert cell_conf["LOW_OPEN_WASH"] == pytest.approx(meta["overall_confidence"])
        assert meta["overall_confidence"] == pytest.approx(0.6 * 0.9 + 0.4 * 0.7)

    def test_disagreement_lowers_confidence(self) -> None:
        la = _layer(LAYER_BASE_RATE, {"HIGH_OPEN_REAL_UP": 1.0}, conf=1.0)
        lb = _layer(LAYER_STATE_CONDITIONAL, {"LOW_OPEN_REAL_DOWN": 1.0}, conf=1.0)
        _, cell_conf, _ = fuse_distributions([la, lb], {LAYER_BASE_RATE: 0.5, LAYER_STATE_CONDITIONAL: 0.5})
        # 两极分歧：σ²=0.25、p(1-p)=0.25 → agreement=0
        assert cell_conf["HIGH_OPEN_REAL_UP"] == pytest.approx(0.0)

    def test_invalid_fail_closed(self) -> None:
        base = _layer(LAYER_BASE_RATE, {s: 1 / 9 for s in SCENARIO_LIST})
        with pytest.raises(ValueError):
            fuse_distributions([], _WEIGHTS)  # 三层全缺
        with pytest.raises(ValueError):
            fuse_distributions([base], {LAYER_BASE_RATE: 0.5, LAYER_STATE_CONDITIONAL: 0.3})  # 权重和≠1
        with pytest.raises(ValueError):
            fuse_distributions([base], {LAYER_BASE_RATE: 0.5, "bogus_layer": 0.5})  # 未知层
        with pytest.raises(ValueError):
            fuse_distributions([base, base], {LAYER_BASE_RATE: 1.0})  # 同名重复
        with pytest.raises(ValueError):
            fuse_distributions(  # 在场层权重和=0
                [base],
                {LAYER_BASE_RATE: 0.0, LAYER_STATE_CONDITIONAL: 0.5, LAYER_DENSITY_HEAD: 0.5},
            )
        bad = _layer(LAYER_STATE_CONDITIONAL, {"HIGH_OPEN_REAL_UP": 0.5})  # 行和≠1
        with pytest.raises(ValueError):
            fuse_distributions([base, bad], {LAYER_BASE_RATE: 0.5, LAYER_STATE_CONDITIONAL: 0.5})


# ══════════════════════════════════════════════════════════════
# build_scenario_probability_forecast 纯函数
# ══════════════════════════════════════════════════════════════


class TestBuildForecast:
    def test_top_and_low_confidence(self) -> None:
        base = _layer(LAYER_BASE_RATE, {s: 1 / 9 for s in SCENARIO_LIST}, conf=0.2, degraded=True)
        state = _layer(LAYER_STATE_CONDITIONAL, {"FLAT_OPEN_REAL_UP": 1.0}, conf=0.9)
        fc = build_scenario_probability_forecast(
            TRADE_DATE,
            [base, state],
            {LAYER_BASE_RATE: 0.5, LAYER_STATE_CONDITIONAL: 0.5},
        )
        assert fc.top_scenario == "FLAT_OPEN_REAL_UP"
        assert fc.low_confidence is True  # base degraded
        assert _sum1(fc.probabilities) == pytest.approx(1.0)
        assert json.dumps(fc.to_dict())  # JSON 可序列化

    def test_invalid_date_fail_closed(self) -> None:
        base = _layer(LAYER_BASE_RATE, {s: 1 / 9 for s in SCENARIO_LIST})
        with pytest.raises(ValueError):
            build_scenario_probability_forecast("2026-13-40", [base], {LAYER_BASE_RATE: 1.0})

    def test_config_weights_fail_closed(self) -> None:
        with pytest.raises(ValueError):
            ScenarioProbabilityConfig(weight_base=0.9, weight_state=0.3, weight_density=0.2)
        with pytest.raises(ValueError):
            ScenarioProbabilityConfig(base_support_full=5, min_base_samples=20)


# ══════════════════════════════════════════════════════════════
# ScenarioProbabilityModel 注入隔离组合
# ══════════════════════════════════════════════════════════════


def _fake_forecast() -> NextDayForecast:
    return NextDayForecast(
        current_state=NextDayState.FLAT_UP,
        probabilities={s: 0.0 for s in NextDayState} | {NextDayState.FLAT_UP: 1.0},
        top_state=NextDayState.FLAT_UP,
        top_probability=1.0,
        confidence=0.8,
        n_transitions=90,
    )


def _fake_quantiles(trade_date: str) -> dict[float, float]:
    return {0.1: 0.01, 0.25: 0.015, 0.5: 0.02, 0.75: 0.025, 0.9: 0.03}


def _fake_query_fn(rows: list[dict]):
    def _query(**kwargs: object) -> list[dict]:
        assert kwargs["module"] == "plan_engine.scenario_planner"
        assert kwargs["prediction_type"] == "outcome"
        return list(rows)

    return _query


def _outcome_row(trade_date: str, actual: object) -> dict:
    return {"trade_date": trade_date, "payload_json": json.dumps({"actual_scenario": actual})}


class TestModelComposition:
    def test_three_layer_full_fusion(self) -> None:
        rows = [_outcome_row("2026-08-20", "FLAT_OPEN_REAL_UP") for _ in range(30)]
        model = ScenarioProbabilityModel(
            query_fn=_fake_query_fn(rows),
            state_forecast_provider=lambda td: _fake_forecast(),
            quantile_provider=_fake_quantiles,
        )
        fc = model.forecast(TRADE_DATE)
        assert fc.trade_date == TRADE_DATE
        assert fc.degraded_layers == ()
        assert fc.weights_used == pytest.approx(_WEIGHTS)
        assert fc.samples[LAYER_BASE_RATE] == 30
        assert fc.samples[LAYER_STATE_CONDITIONAL] == 90
        assert fc.samples[LAYER_DENSITY_HEAD] == 2000
        # 三层全指 FLAT_OPEN_REAL_UP（基础率 30/30 平滑后仍众数）
        assert fc.top_scenario == "FLAT_OPEN_REAL_UP"
        assert _sum1(fc.probabilities) == pytest.approx(1.0)
        json.dumps(fc.to_dict())

    def test_pit_window_excludes_future_and_same_day(self) -> None:
        rows = [
            _outcome_row(TRADE_DATE, "HIGH_OPEN_REAL_UP"),  # 当日（PIT 排除）
            _outcome_row("2026-08-20", "FLAT_OPEN_WASH"),  # 窗口内
        ]
        model = ScenarioProbabilityModel(
            query_fn=_fake_query_fn(rows),
            state_forecast_provider=lambda td: _fake_forecast(),
            quantile_provider=_fake_quantiles,
        )
        fc = model.forecast(TRADE_DATE)
        assert fc.samples[LAYER_BASE_RATE] == 1  # 仅窗口内历史行计入

    def test_base_query_failure_degrades(self) -> None:
        def _boom(**kwargs: object) -> list[dict]:
            raise RuntimeError("db down")

        model = ScenarioProbabilityModel(
            query_fn=_boom,
            state_forecast_provider=lambda td: _fake_forecast(),
            quantile_provider=_fake_quantiles,
        )
        fc = model.forecast(TRADE_DATE)
        assert LAYER_BASE_RATE in fc.degraded_layers
        assert LAYER_BASE_RATE not in fc.weights_used
        assert fc.weights_used[LAYER_STATE_CONDITIONAL] == pytest.approx(0.6)  # 0.3/0.5
        assert fc.weights_used[LAYER_DENSITY_HEAD] == pytest.approx(0.4)  # 0.2/0.5
        assert _sum1(fc.probabilities) == pytest.approx(1.0)

    def test_provider_failure_and_missing_degrade(self) -> None:
        rows = [_outcome_row("2026-08-20", "HIGH_OPEN_WASH") for _ in range(25)]
        model = ScenarioProbabilityModel(
            query_fn=_fake_query_fn(rows),
            state_forecast_provider=lambda td: (_ for _ in ()).throw(RuntimeError("markov down")),
            quantile_provider=None,  # 未注入=缺层
        )
        fc = model.forecast(TRADE_DATE)
        assert set(fc.degraded_layers) == {LAYER_STATE_CONDITIONAL, LAYER_DENSITY_HEAD}
        assert fc.weights_used == {LAYER_BASE_RATE: 1.0}
        assert fc.top_scenario == "HIGH_OPEN_WASH"

    def test_insufficient_base_uniform_low_confidence(self) -> None:
        model = ScenarioProbabilityModel(
            query_fn=_fake_query_fn([_outcome_row("2026-08-20", "HIGH_OPEN_WASH")]),
            state_forecast_provider=None,
            quantile_provider=None,
        )
        fc = model.forecast(TRADE_DATE)
        assert fc.low_confidence is True
        assert all(p == pytest.approx(1 / 9) for p in fc.probabilities.values())

    def test_invalid_outcome_rows_skipped(self) -> None:
        rows = [
            {"trade_date": "2026-08-20", "payload_json": "not-json"},  # 坏 JSON
            _outcome_row("2026-08-20", "BOGUS"),  # 情景越界
            {"trade_date": "2026-08-20", "payload_json": json.dumps({"other": 1})},  # 缺字段
        ]
        model = ScenarioProbabilityModel(
            query_fn=_fake_query_fn(rows),
            state_forecast_provider=lambda td: _fake_forecast(),
            quantile_provider=None,
        )
        fc = model.forecast(TRADE_DATE)
        assert fc.samples[LAYER_BASE_RATE] == 0  # 全 skipped，均匀兜底不炸

    def test_all_layers_missing_fail_closed(self) -> None:
        def _boom(**kwargs: object) -> list[dict]:
            raise RuntimeError("db down")

        model = ScenarioProbabilityModel(query_fn=_boom)
        with pytest.raises(ValueError):
            model.forecast(TRADE_DATE)

    def test_invalid_trade_date_fail_closed(self) -> None:
        model = ScenarioProbabilityModel(query_fn=_fake_query_fn([]))
        with pytest.raises(ValueError):
            model.forecast("not-a-date")


# ══════════════════════════════════════════════════════════════
# 落库（tmp 库隔离，append-only 公共 API）
# ══════════════════════════════════════════════════════════════


class TestForecastAndRecord:
    @pytest.fixture
    def tmp_db(self, tmp_path: Path) -> Path:
        db = tmp_path / "governance.db"
        ensure_prediction_log_table(db)
        return db

    def _model(self, db: Path) -> ScenarioProbabilityModel:
        rows = [_outcome_row("2026-08-20", "FLAT_OPEN_REAL_UP") for _ in range(30)]
        return ScenarioProbabilityModel(
            query_fn=_fake_query_fn(rows),
            state_forecast_provider=lambda td: _fake_forecast(),
            quantile_provider=_fake_quantiles,
            db_path=db,
        )

    def test_record_roundtrip(self, tmp_db: Path) -> None:
        model = self._model(tmp_db)
        fc, row_id = model.forecast_and_record(TRADE_DATE, asof_ts="2026-08-21T09:00:00+08:00")
        assert row_id > 0
        rows = query_predictions(
            trade_date=TRADE_DATE,
            module=MODULE_LOG_NAME,
            prediction_type=PREDICTION_TYPE_SCENARIO_PROBABILITY,
            db_path=tmp_db,
        )
        assert len(rows) == 1
        payload = json.loads(rows[0]["payload_json"])
        assert payload["top_scenario"] == fc.top_scenario
        assert _sum1(payload["probabilities"]) == pytest.approx(1.0)
        assert set(payload["probabilities"]) == set(SCENARIO_LIST)
        assert payload["weights_used"] == pytest.approx(_WEIGHTS)

    def test_record_idempotent_keeps_first(self, tmp_db: Path) -> None:
        model = self._model(tmp_db)
        _, first = model.forecast_and_record(TRADE_DATE)
        _, second = model.forecast_and_record(TRADE_DATE)
        assert first == second > 0
        rows = query_predictions(
            trade_date=TRADE_DATE,
            module=MODULE_LOG_NAME,
            prediction_type=PREDICTION_TYPE_SCENARIO_PROBABILITY,
            db_path=tmp_db,
        )
        assert len(rows) == 1

    def test_record_failure_fail_open(self, tmp_path: Path) -> None:
        bad_dir = tmp_path / "not_a_db"
        bad_dir.mkdir()  # 目录路径当库路径 → sqlite 连接失败
        model = self._model(bad_dir)
        fc, row_id = model.forecast_and_record(TRADE_DATE)
        assert row_id == -1
        assert fc.top_scenario == "FLAT_OPEN_REAL_UP"  # 预测主流程不阻塞
