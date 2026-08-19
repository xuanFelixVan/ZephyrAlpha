# [TTL] permanent
"""25号memo §3.7#1 SynthesisDegradationChain 测试。

覆盖：
- decide: 回归可行/条件数过高降IC加权/样本不足等权/信号衰竭等权/集中度过高等权/默认IC加权
- synthesize_with_degradation: 分派正确性 + 空输入退化
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

mod = pytest.importorskip("zephyr.factor.analysis.multifactor_degradation_chain")

DegradationChainParams = mod.DegradationChainParams
decide = mod.decide
synthesize_with_degradation = mod.synthesize_with_degradation


def _panel(n: int = 60, k: int = 3) -> dict[str, pd.Series]:
    rng = np.random.default_rng(7)
    idx = pd.RangeIndex(n)
    return {f"f{i}": pd.Series(rng.normal(size=n), index=idx) for i in range(k)}


def _ic_history(k: int = 3, n: int = 30, mean: float = 0.05) -> dict[str, list[float]]:
    return {f"f{i}": [mean] * n for i in range(k)}


class TestDecideRegression:
    def test_regression_feasible(self):
        panel = _panel(150, 3)
        fwd = pd.Series(np.random.default_rng(1).normal(size=150), index=pd.RangeIndex(150))
        d = decide(panel, _ic_history(), fwd)
        assert d.method == "regression"
        assert not d.degraded

    def test_high_condition_number_degrades_to_ic(self):
        # 构造完全共线面板（f2=2*f1, f3=3*f1）→ 条件数巨大
        base = pd.Series(np.arange(150.0), index=pd.RangeIndex(150))
        panel = {"f0": base, "f1": base * 2, "f2": base * 3}
        fwd = pd.Series(np.random.default_rng(2).normal(size=150), index=pd.RangeIndex(150))
        d = decide(panel, _ic_history(), fwd)
        assert d.method == "ic_weighted"
        assert d.degraded
        assert "共线性" in d.reason

    def test_insufficient_forward_returns_skips_regression(self):
        panel = _panel(60, 3)
        fwd = pd.Series(np.random.default_rng(3).normal(size=60), index=pd.RangeIndex(60))
        d = decide(panel, _ic_history(), fwd)
        assert d.method == "ic_weighted"  # 60<120 不判回归，走默认 IC 加权

    def test_no_forward_returns_never_regression(self):
        d = decide(_panel(), _ic_history(), None)
        assert d.method == "ic_weighted"


class TestDecideIcWeighted:
    def test_default_ic_weighted(self):
        d = decide(_panel(), _ic_history())
        assert d.method == "ic_weighted"
        assert not d.degraded
        # 等 |IC| → 权重均分
        assert all(abs(w - 1 / 3) < 1e-9 for w in d.ic_weights.values())

    def test_few_samples_equal_weight(self):
        d = decide(_panel(), _ic_history(n=19))
        assert d.method == "equal_weight"
        assert d.degraded

    def test_signal_exhaustion_equal_weight(self):
        d = decide(_panel(), _ic_history(mean=0.01))
        assert d.method == "equal_weight"
        assert "信号衰竭" in d.reason

    def test_concentration_equal_weight(self):
        # f0 权重 0.08/(0.08+0.01+0.01)=0.80 > 0.70 → 等权
        hist = {"f0": [0.08] * 30, "f1": [0.01] * 30, "f2": [0.01] * 30}
        d = decide(_panel(), hist)
        assert d.method == "equal_weight"
        assert "过度集中" in d.reason

    def test_empty_panel_equal_weight(self):
        d = decide({}, {})
        assert d.method == "equal_weight"
        assert d.degraded


class TestSynthesizeWithDegradation:
    def test_ic_weighted_dispatch(self):
        panel = _panel(10, 2)
        hist = {"f0": [0.06] * 30, "f1": [0.03] * 30}
        signal, d = synthesize_with_degradation(panel, hist)
        assert d.method == "ic_weighted"
        # 权重 2:1 归一化 → 2/3, 1/3
        expected = panel["f0"] * (2 / 3) + panel["f1"] * (1 / 3)
        pd.testing.assert_series_equal(signal, expected)

    def test_equal_weight_dispatch_on_exhaustion(self):
        panel = _panel(10, 2)
        hist = {"f0": [0.005] * 30, "f1": [0.005] * 30}
        signal, d = synthesize_with_degradation(panel, hist)
        assert d.method == "equal_weight"
        pd.testing.assert_series_equal(signal, (panel["f0"] + panel["f1"]) / 2)

    def test_regression_dispatch(self):
        n = 150
        panel = _panel(n, 2)
        fwd = panel["f0"] * 0.5 + panel["f1"] * 0.3
        signal, d = synthesize_with_degradation(panel, _ic_history(k=2), fwd)
        assert d.method == "regression"
        assert len(signal) == n

    def test_empty_input(self):
        signal, d = synthesize_with_degradation({})
        assert signal.empty
        assert d.method == "equal_weight"

    def test_custom_params(self):
        p = DegradationChainParams(ic_min_samples=5)
        d = decide(_panel(), _ic_history(n=6), params=p)
        assert d.method == "ic_weighted"
