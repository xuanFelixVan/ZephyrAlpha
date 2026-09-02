# [BLUEPRINT] MOD-REGIME-012 | docs/03_modules/_domain_regime/market_forecast_fusion/blueprint.md | §test
# [MODULE] tests.regime.test_market_forecast_fusion
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.market_forecast_fusion
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_market_forecast_fusion.py
# [A_test] module_id: MOD-REGIME-012 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-REGIME-012 单元测试: C-014 大盘预测三层融合。

覆盖: 融合分布归一（Σ=1）与众数态/置信度口径、滚动准确率动态加权（命中抬权/
冷启动先验/权重下限）、外部信号畸形 Fail-Closed、settle 命中回写滚动窗口、
预测日志 payload 唯一键字段（module/prediction_type/trade_date）、log_sink 异常
不阻断如实记录。
"""

from __future__ import annotations

import pytest

from zephyr.regime.market_forecast_fusion import (
    INTERNAL_SOURCE_ID,
    ExternalForecast,
    FusionConfigError,
    InvalidExternalForecastError,
    MarketForecastFusion,
    RollingAccuracyTracker,
)
from zephyr.signal_ashare.next_day_8state_forecast import NextDayForecast, NextDayState

_STATES = [s.value for s in NextDayState]


def _uniform() -> dict[str, float]:
    return {s: 1.0 / len(_STATES) for s in _STATES}


def _peaked(state: str, peak: float = 0.55) -> dict[str, float]:
    rest = (1.0 - peak) / (len(_STATES) - 1)
    return {s: (peak if s == state else rest) for s in _STATES}


def _internal(top: str = "FLAT_UP", top_prob: float = 0.4) -> NextDayForecast:
    probs = _peaked(top, top_prob)
    return NextDayForecast(
        current_state=NextDayState(top),
        probabilities={NextDayState(k): v for k, v in probs.items()},
        top_state=NextDayState(top),
        top_probability=top_prob,
        confidence=0.6,
        n_transitions=100,
    )


class TestExternalForecastValidation:
    def test_valid(self):
        ef = ExternalForecast(source_id="anchor_a", probabilities=_uniform(), confidence=0.5)
        assert ef.source_id == "anchor_a"

    def test_probabilities_normalized_on_input(self):
        raw = {s: 2.0 for s in _STATES}
        ef = ExternalForecast(source_id="a", probabilities=raw, confidence=0.5)
        assert sum(ef.probabilities.values()) == pytest.approx(1.0)

    def test_missing_state_key_fail_closed(self):
        bad = _uniform()
        del bad[_STATES[0]]
        with pytest.raises(InvalidExternalForecastError):
            ExternalForecast(source_id="a", probabilities=bad, confidence=0.5)

    def test_unknown_state_key_fail_closed(self):
        bad = _uniform()
        bad["MYSTERY"] = 0.01
        with pytest.raises(InvalidExternalForecastError):
            ExternalForecast(source_id="a", probabilities=bad, confidence=0.5)

    def test_negative_probability_fail_closed(self):
        bad = _uniform()
        bad[_STATES[0]] = -0.1
        with pytest.raises(InvalidExternalForecastError):
            ExternalForecast(source_id="a", probabilities=bad, confidence=0.5)

    def test_zero_sum_fail_closed(self):
        with pytest.raises(InvalidExternalForecastError):
            ExternalForecast(source_id="a", probabilities={s: 0.0 for s in _STATES}, confidence=0.5)

    def test_confidence_out_of_range_fail_closed(self):
        with pytest.raises(InvalidExternalForecastError):
            ExternalForecast(source_id="a", probabilities=_uniform(), confidence=1.5)

    def test_empty_source_id_fail_closed(self):
        with pytest.raises(InvalidExternalForecastError):
            ExternalForecast(source_id="  ", probabilities=_uniform(), confidence=0.5)

    def test_internal_source_id_reserved(self):
        with pytest.raises(InvalidExternalForecastError):
            ExternalForecast(source_id=INTERNAL_SOURCE_ID, probabilities=_uniform(), confidence=0.5)


class TestRollingAccuracyTracker:
    def test_cold_start_prior(self):
        tracker = RollingAccuracyTracker()
        assert tracker.accuracy("unknown") == pytest.approx(1.0 / 8)

    def test_hits_raise_accuracy(self):
        tracker = RollingAccuracyTracker(prior_strength=16)
        for _ in range(16):
            tracker.record("a", "FLAT_UP", "FLAT_UP")
        assert tracker.accuracy("a") > 0.5

    def test_weight_floor(self):
        tracker = RollingAccuracyTracker(min_weight=0.05)
        for _ in range(40):
            tracker.record("a", "FLAT_UP", "VIOLENT")
        assert tracker.weight("a") == pytest.approx(0.05)

    def test_window_rolls(self):
        tracker = RollingAccuracyTracker(window=4, prior_strength=0.0)
        for _ in range(4):
            tracker.record("a", "X", "X")
        assert tracker.accuracy("a") == pytest.approx(1.0)
        for _ in range(4):
            tracker.record("a", "X", "Y")
        assert tracker.accuracy("a") == pytest.approx(0.0)

    def test_config_fail_closed(self):
        with pytest.raises(FusionConfigError):
            RollingAccuracyTracker(window=0)
        with pytest.raises(FusionConfigError):
            RollingAccuracyTracker(prior_strength=-1)
        with pytest.raises(FusionConfigError):
            RollingAccuracyTracker(min_weight=0.0)


class TestFuse:
    def test_fused_distribution_normalized(self):
        fusion = MarketForecastFusion()
        fused = fusion.fuse(_internal("FLAT_UP"), [ExternalForecast("a", _peaked("VIOLENT", 0.6), 0.7)])
        assert sum(fused.probabilities.values()) == pytest.approx(1.0)
        assert set(fused.probabilities) == set(_STATES)

    def test_internal_only_cold_start(self):
        fusion = MarketForecastFusion()
        fused = fusion.fuse(_internal("FLAT_UP", 0.4), [])
        assert fused.top_state == "FLAT_UP"
        assert fused.weights == {INTERNAL_SOURCE_ID: 1.0}
        # 唯一信号源一致度=1 → confidence = top_probability
        assert fused.confidence == pytest.approx(0.4)

    def test_strong_external_shifts_top(self):
        fusion = MarketForecastFusion()
        # 内部弱峰 FLAT_UP(0.30)，外部强峰 VIOLENT(0.80)；冷启动同权 → VIOLENT 胜出
        fused = fusion.fuse(
            _internal("FLAT_UP", 0.30),
            [ExternalForecast("a", _peaked("VIOLENT", 0.80), 0.9)],
        )
        assert fused.top_state == "VIOLENT"

    def test_weights_reflect_rolling_accuracy(self):
        fusion = MarketForecastFusion()
        # 源 a 连续命中抬权，源 b 连续失手降权
        for _ in range(24):
            fusion._tracker.record("a", "T", "T")
            fusion._tracker.record("b", "T", "F")
        fused = fusion.fuse(
            _internal("FLAT_UP"),
            [
                ExternalForecast("a", _peaked("VIOLENT", 0.6), 0.5),
                ExternalForecast("b", _peaked("GAP_UP_UP", 0.6), 0.5),
            ],
        )
        assert fused.weights["a"] > fused.weights[INTERNAL_SOURCE_ID] > fused.weights["b"]

    def test_confidence_scaled_by_agreement(self):
        fusion = MarketForecastFusion()
        fused = fusion.fuse(
            _internal("FLAT_UP", 0.5),
            [ExternalForecast("a", _peaked("VIOLENT", 0.9), 0.9)],
        )
        # 两源众数态不一致 → 一致度 < 1 → confidence < top_probability
        assert 0.0 < fused.confidence < fused.top_probability

    def test_confidence_bounds(self):
        fusion = MarketForecastFusion()
        fused = fusion.fuse(
            _internal("FLAT_UP"),
            [ExternalForecast("a", _uniform(), 0.0), ExternalForecast("b", _uniform(), 1.0)],
        )
        assert 0.0 <= fused.confidence <= 1.0
        assert 0.0 <= fused.top_probability <= 1.0


class TestSettle:
    def test_settle_records_all_sources(self):
        fusion = MarketForecastFusion()
        fusion.fuse(
            _internal("FLAT_UP"),
            [ExternalForecast("a", _peaked("VIOLENT", 0.9), 0.9)],
        )
        report = fusion.settle("FLAT_UP")
        assert report[INTERNAL_SOURCE_ID] is True  # 内部众数态 FLAT_UP 命中
        assert report["a"] is False  # 外部众数态 VIOLENT 失手
        assert fusion._tracker.accuracy(INTERNAL_SOURCE_ID) > 1.0 / 8

    def test_settle_without_fuse_fail_closed(self):
        fusion = MarketForecastFusion()
        with pytest.raises(FusionConfigError):
            fusion.settle("FLAT_UP")

    def test_settle_unknown_state_fail_closed(self):
        fusion = MarketForecastFusion()
        fusion.fuse(_internal("FLAT_UP"), [])
        with pytest.raises(FusionConfigError):
            fusion.settle("MYSTERY")


class TestLogPayload:
    def test_payload_unique_key_fields(self):
        fusion = MarketForecastFusion()
        fused = fusion.fuse(_internal("FLAT_UP"), [])
        payload = fusion.build_log_payload("2026-08-25", fused)
        assert payload["trade_date"] == "2026-08-25"
        assert payload["module"] == "market_forecast_fusion"
        assert payload["prediction_type"] == "next_day_8state_fusion"
        body = payload["payload"]
        assert body["top_state"] == "FLAT_UP"
        assert pytest.approx(sum(body["probabilities"].values())) == 1.0
        assert "weights" in body and "confidence" in body

    def test_log_sink_invoked_and_exception_not_blocking(self):
        calls: list[dict] = []

        def ok_sink(payload: dict) -> None:
            calls.append(payload)

        fusion = MarketForecastFusion(log_sink=ok_sink)
        fused = fusion.fuse(_internal("FLAT_UP"), [], trade_date="2026-08-25")
        assert len(calls) == 1
        assert fused.log_signaled is True

        def bad_sink(payload: dict) -> None:
            raise RuntimeError("db down")

        fusion2 = MarketForecastFusion(log_sink=bad_sink)
        fused2 = fusion2.fuse(_internal("FLAT_UP"), [], trade_date="2026-08-25")
        assert fused2.log_signaled is False  # 异常不阻断，如实记录
