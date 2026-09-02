# [BLUEPRINT] MOD-PA-015 | docs/03_modules/_domain_portfolio_alloc/regime_bma_weighting/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-PA-015 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.pf_alloc.test_regime_bma_weighting
# [TESTS] src/zephyr/pf_alloc/core/regime_bma_weighting.py
"""MOD-PA-015 单元测试：regime_bma_weighting 体制条件BMA信号权重。

蓝图验收（B11-02963/CAND-PFALLOC-010，A7）：
按体制分组滚动250日估计信号预测精度（命中率/IC）+ 后验归一Σ=1 +
权重变更审计回调 + 体制切换半衰期平滑。观测序列/审计/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.pf_alloc.core.regime_bma_weighting",
    reason="regime_bma_weighting not importable",
)

from zephyr.pf_alloc.core.regime_bma_weighting import (  # noqa: E402
    PrecisionMetric,
    RegimeBmaError,
    RegimeBmaWeighting,
    SignalOutcome,
    WeightAuditEvent,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)

_HIT = SignalOutcome(1.0, 1.0)
_MISS = SignalOutcome(1.0, -1.0)


def _engine(audits: list | None = None, **kwargs) -> RegimeBmaWeighting:
    kwargs.setdefault("clock", lambda: _T0)
    if audits is not None:
        kwargs["audit_sink"] = lambda e: audits.append(e)
    return RegimeBmaWeighting(**kwargs)


def _obs(a_series, b_series=("m", "m")) -> dict:
    conv = {"h": _HIT, "m": _MISS}
    return {
        "sig_a": [conv[x] for x in a_series],
        "sig_b": [conv[x] for x in b_series],
    }


# ──────────────────────────────────────────────────────────────────────────────
# 初始化与 Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestInitAndValidation:
    def test_default_ok(self) -> None:
        assert _engine() is not None

    def test_window_invalid_raises(self) -> None:
        with pytest.raises(RegimeBmaError):
            _engine(window=0)
        with pytest.raises(RegimeBmaError):
            _engine(window=2.5)

    def test_half_life_invalid_raises(self) -> None:
        with pytest.raises(RegimeBmaError):
            _engine(half_life=0)

    def test_min_samples_invalid_raises(self) -> None:
        with pytest.raises(RegimeBmaError):
            _engine(min_samples=0)

    def test_bad_metric_raises(self) -> None:
        with pytest.raises(RegimeBmaError):
            _engine(metric="sharpe")

    def test_empty_regime_raises(self) -> None:
        with pytest.raises(RegimeBmaError):
            _engine().update(regime="", observations=_obs("hh"))

    def test_empty_observations_raises(self) -> None:
        with pytest.raises(RegimeBmaError):
            _engine().update(regime="bull", observations={})

    def test_empty_signal_id_raises(self) -> None:
        with pytest.raises(RegimeBmaError):
            _engine().update(regime="bull", observations={"": [_HIT, _HIT]})

    def test_insufficient_samples_raises(self) -> None:
        with pytest.raises(RegimeBmaError):
            _engine(min_samples=3).update(regime="bull", observations=_obs("hh", "hh"))

    def test_non_finite_observation_raises(self) -> None:
        bad = SignalOutcome(float("inf"), 1.0)
        with pytest.raises(RegimeBmaError):
            _engine().update(regime="bull", observations={"sig_a": [bad, _HIT]})

    def test_non_outcome_raises(self) -> None:
        with pytest.raises(RegimeBmaError):
            _engine().update(regime="bull", observations={"sig_a": [(1.0, 1.0), (1.0, 1.0)]})

    def test_current_weights_before_update_raises(self) -> None:
        with pytest.raises(RegimeBmaError):
            _engine().current_weights()


# ──────────────────────────────────────────────────────────────────────────────
# 精度估计与后验归一
# ──────────────────────────────────────────────────────────────────────────────


class TestPosteriors:
    def test_hit_rate_extreme(self) -> None:
        w = _engine().update(regime="bull", observations=_obs("hhhh", "mmmm"))
        assert w == {"sig_a": 1.0, "sig_b": 0.0}

    def test_hit_rate_partial(self) -> None:
        w = _engine().update(regime="bull", observations=_obs("hhhm", "mmmh"))
        assert w == {"sig_a": 0.75, "sig_b": 0.25}

    def test_uniform_fallback_on_zero_evidence(self) -> None:
        w = _engine().update(
            regime="bull",
            observations={
                "s1": [_MISS, _MISS],
                "s2": [_MISS, _MISS],
                "s3": [_MISS, _MISS],
            },
        )
        assert w == pytest.approx({"s1": 1 / 3, "s2": 1 / 3, "s3": 1 / 3})
        assert sum(w.values()) == pytest.approx(1.0)

    def test_rolling_window_tail_only(self) -> None:
        # window=4：前2条miss出窗，尾4条全hit → 精度1.0
        e = _engine(window=4)
        w = e.update(regime="bull", observations=_obs("mmhhhh", "mmmmmm"))
        assert w == {"sig_a": 1.0, "sig_b": 0.0}

    def test_weights_sum_to_one(self) -> None:
        w = _engine().update(regime="bull", observations=_obs("hhhm", "hmmm"))
        assert sum(w.values()) == pytest.approx(1.0)

    def test_ic_perfect_positive(self) -> None:
        e = _engine(metric=PrecisionMetric.IC)
        w = e.update(
            regime="bull",
            observations={
                "sig_a": [SignalOutcome(1, 1), SignalOutcome(2, 2), SignalOutcome(3, 3)],
                "sig_b": [SignalOutcome(1, 3), SignalOutcome(2, 2), SignalOutcome(3, 1)],
            },
        )
        assert w == {"sig_a": 1.0, "sig_b": 0.0}  # 负IC截断0

    def test_ic_zero_variance_zero(self) -> None:
        e = _engine(metric=PrecisionMetric.IC)
        w = e.update(
            regime="bull",
            observations={
                "sig_a": [SignalOutcome(1, 1), SignalOutcome(1, 2)],
                "sig_b": [SignalOutcome(1, 1), SignalOutcome(1, 2)],
            },
        )
        assert w == {"sig_a": 0.5, "sig_b": 0.5}  # 双零方差→全零证据→均匀


# ──────────────────────────────────────────────────────────────────────────────
# 体制切换半衰期平滑
# ──────────────────────────────────────────────────────────────────────────────


class TestRegimeSwitchSmoothing:
    def _switched(self) -> RegimeBmaWeighting:
        e = _engine(half_life=1)
        e.update(regime="bull", observations=_obs("hhhh", "mmmm"))  # A=1,B=0
        return e

    def test_first_update_after_switch_half_blend(self) -> None:
        e = self._switched()
        w = e.update(regime="bear", observations=_obs("mmmm", "hhhh"))  # raw A=0,B=1
        assert w == {"sig_a": 0.5, "sig_b": 0.5}  # t=1, hl=1 → new_share=0.5

    def test_blend_converges(self) -> None:
        e = self._switched()
        e.update(regime="bear", observations=_obs("mmmm", "hhhh"))
        w2 = e.update(regime="bear", observations=_obs("mmmm", "hhhh"))
        assert w2 == {"sig_a": 0.25, "sig_b": 0.75}  # t=2 → new_share=0.75
        w3 = e.update(regime="bear", observations=_obs("mmmm", "hhhh"))
        assert w3 == {"sig_a": 0.125, "sig_b": 0.875}  # t=3 → new_share=0.875

    def test_same_regime_no_blend(self) -> None:
        e = _engine(half_life=1)
        e.update(regime="bull", observations=_obs("hhhh", "mmmm"))
        w = e.update(regime="bull", observations=_obs("hhhh", "mmmm"))
        assert w == {"sig_a": 1.0, "sig_b": 0.0}  # 未切换不混合

    def test_switch_back_uses_current_snapshot(self) -> None:
        e = self._switched()
        e.update(regime="bear", observations=_obs("mmmm", "hhhh"))  # 0.5/0.5
        w = e.update(regime="bull", observations=_obs("hhhh", "mmmm"))  # raw A=1,B=0
        assert w == {"sig_a": 0.75, "sig_b": 0.25}  # 自0.5/0.5向1/0混一半

    def test_current_regime_property(self) -> None:
        e = _engine()
        assert e.current_regime is None
        e.update(regime="bull", observations=_obs("hh", "mm"))
        assert e.current_regime == "bull"


# ──────────────────────────────────────────────────────────────────────────────
# 审计回调
# ──────────────────────────────────────────────────────────────────────────────


class TestAudit:
    def test_audit_event_fields(self) -> None:
        audits: list[WeightAuditEvent] = []
        e = _engine(audits, half_life=2)
        e.update(regime="bull", observations=_obs("hh", "mm"))
        assert len(audits) == 1
        ev = audits[0]
        assert ev.regime == "bull"
        assert ev.switched is False
        assert ev.updates_in_regime == 1
        assert ev.new_share == 1.0
        assert ev.raw_posteriors == {"sig_a": 1.0, "sig_b": 0.0}
        assert ev.effective_weights == ev.raw_posteriors
        assert ev.raised_at == _T0

    def test_audit_on_every_update_including_switch(self) -> None:
        audits: list[WeightAuditEvent] = []
        e = _engine(audits, half_life=1)
        e.update(regime="bull", observations=_obs("hhhh", "mmmm"))
        e.update(regime="bear", observations=_obs("mmmm", "hhhh"))
        assert len(audits) == 2
        assert audits[1].switched is True
        assert audits[1].new_share == 0.5

    def test_audit_sink_exception_not_blocking(self) -> None:
        def _boom(_event) -> None:
            raise RuntimeError("sink down")

        e = RegimeBmaWeighting(clock=lambda: _T0, audit_sink=_boom)
        w = e.update(regime="bull", observations=_obs("hh", "mm"))
        assert w == {"sig_a": 1.0, "sig_b": 0.0}  # 审计失败不阻断


# ──────────────────────────────────────────────────────────────────────────────
# 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_sequence_same_weights(self) -> None:
        def _run() -> dict:
            e = _engine(half_life=1)
            e.update(regime="bull", observations=_obs("hhhh", "mmmm"))
            return e.update(regime="bear", observations=_obs("mmmm", "hhhh"))

        assert _run() == _run()

    def test_weight_keys_sorted(self) -> None:
        w = _engine().update(
            regime="bull",
            observations={
                "z_sig": [_HIT, _HIT],
                "a_sig": [_MISS, _MISS],
            },
        )
        assert list(w) == ["a_sig", "z_sig"]
