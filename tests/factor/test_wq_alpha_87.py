# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] tests.factor.test_wq_alpha_87
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.wq_alpha_87
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] production
# [INVARIANTS] 合成panel数据纯内存测试，不触网不触库; PIT前缀不变性锚定无未来函数
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=算子/公式实现/87注册集/PIT合规缺陷
# [TESTS] 本文件
# [TTL] permanent
"""WqAlpha87 单元测试（CAND-FAC-010 / B1-00847，92 87-Alpha，GATE-92-01）。

覆盖（min_build_spec）：
- ts 算子集（rank/delay/delta/correlation/covariance/decay_linear/ts_sum 等）正确性
- 87 个 Alpha 公式逐个实现（101 剔除 14 个 IndNeutralize/cap 依赖）
- PIT 合规：截断数据前缀不变性（无未来函数）
- 逐个 IC/IR 验证接入（ic_hook 委托，复用 ic_ir_calc 语义）
- 入因子注册（register_hook 委托）与 feature_store 形态（panel 输出）
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.wq_alpha_87 import (
    DEGRADED_FORMULAS,
    EXCLUDED_IDS,
    WQ_ALPHA_87_IDS,
    Alpha87Error,
    WqAlpha87,
    ops,
)

# 最长窗口组合 ~250（ts_sum(returns,250)/delay(close,100)+ts_mean(100)/correlation(230)+delay(5)），
# 取 280 个交易日保证 87 个公式最新截面均有值。
_DATES = pd.bdate_range("2025-06-01", periods=280)
# 30 标的截面：小截面 rank 离散值少，小窗 rolling corr 易零方差 NaN（非实现缺陷），
# 30 标的更贴近真实全市场截面形态。
_SYMBOLS = [f"{i:06d}.SZ" for i in range(30)]


def _panel(seed: int = 7) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    n, m = len(_DATES), len(_SYMBOLS)
    close = pd.DataFrame(
        10 + rng.normal(0, 0.4, (n, m)).cumsum(axis=0), index=_DATES, columns=_SYMBOLS
    ).clip(lower=1.0)
    open_ = close * (1 + rng.normal(0, 0.005, (n, m)))
    high = pd.DataFrame(np.maximum(open_.values, close.values), index=_DATES, columns=_SYMBOLS) * (
        1 + abs(rng.normal(0, 0.004, (n, m)))
    )
    low = pd.DataFrame(np.minimum(open_.values, close.values), index=_DATES, columns=_SYMBOLS) * (
        1 - abs(rng.normal(0, 0.004, (n, m)))
    )
    volume = pd.DataFrame(rng.integers(1_000_000, 9_000_000, (n, m)).astype(float), index=_DATES, columns=_SYMBOLS)
    amount = volume * close
    return {"open": open_, "high": high, "low": low, "close": close, "volume": volume, "amount": amount}


class TestOperatorSet:
    """ts 算子集正确性。"""

    def test_rank_is_cross_sectional_pct(self) -> None:
        df = pd.DataFrame({"a": [1.0, 5.0], "b": [2.0, 3.0], "c": [3.0, 1.0]})
        ranked = ops.rank(df)
        assert ranked.iloc[0].tolist() == [1 / 3, 2 / 3, 1.0]
        assert ranked.iloc[1].tolist() == [1.0, 2 / 3, 1 / 3]

    def test_delay_and_delta(self) -> None:
        df = pd.DataFrame({"a": [1.0, 2.0, 4.0, 8.0]})
        assert ops.delay(df, 2)["a"].iloc[3] == 2.0
        assert ops.delta(df, 1)["a"].iloc[3] == 4.0
        assert ops.delay(df, 1)["a"].iloc[0] != ops.delay(df, 1)["a"].iloc[0]  # NaN

    def test_ts_sum_min_max_stddev(self) -> None:
        df = pd.DataFrame({"a": [1.0, 2.0, 3.0, 4.0]})
        assert ops.ts_sum(df, 3)["a"].iloc[3] == 9.0
        assert ops.ts_min(df, 3)["a"].iloc[3] == 2.0
        assert ops.ts_max(df, 3)["a"].iloc[2] == 3.0
        assert ops.stddev(df, 2)["a"].iloc[3] == pytest.approx(0.7071068, rel=1e-5)

    def test_decay_linear_weights(self) -> None:
        df = pd.DataFrame({"a": [1.0, 2.0, 3.0]})
        # 权重 1,2,3 / 6：(1*1 + 2*2 + 3*3)/6 = 14/6
        assert ops.decay_linear(df, 3)["a"].iloc[2] == pytest.approx(14 / 6)

    def test_correlation_covariance(self) -> None:
        a = pd.DataFrame({"x": [1.0, 2.0, 3.0, 4.0]})
        b = pd.DataFrame({"x": [2.0, 4.0, 6.0, 8.0]})
        assert ops.correlation(a, b, 4)["x"].iloc[3] == pytest.approx(1.0)
        # pandas rolling.cov 默认 ddof=1：完全线性对的样本协方差 = 10/3
        assert ops.covariance(a, b, 4)["x"].iloc[3] == pytest.approx(10 / 3, rel=1e-6)

    def test_ts_rank_and_argmax(self) -> None:
        df = pd.DataFrame({"a": [3.0, 1.0, 2.0, 5.0]})
        # 窗口 3：iloc[3] 窗=[1,2,5]，最新值 5 的百分位=1.0
        assert ops.ts_rank(df, 3)["a"].iloc[3] == pytest.approx(1.0)
        assert ops.ts_argmax(df, 3)["a"].iloc[3] == pytest.approx(3.0)

    def test_signed_power_and_scale(self) -> None:
        df = pd.DataFrame({"a": [-2.0, 3.0]})
        assert ops.signed_power(df, 2.0)["a"].tolist() == [-4.0, 9.0]
        # scale 为截面归一（每行=一个截面）：单截面两标的 abs 和=1
        row = pd.DataFrame({"a": [-2.0], "b": [3.0]})
        scaled = ops.scale(row, 1.0)
        assert scaled.abs().sum(axis=1).iloc[0] == pytest.approx(1.0)
        assert scaled.iloc[0].tolist() == [-0.4, 0.6]


class TestAlpha87Registry:
    """87 公式注册集完整性。"""

    def test_87_ids_complete_and_excluded_14(self) -> None:
        assert len(WQ_ALPHA_87_IDS) == 87
        assert len(EXCLUDED_IDS) == 14
        assert set(WQ_ALPHA_87_IDS).isdisjoint(set(EXCLUDED_IDS))
        assert sorted(set(range(1, 102)) - set(WQ_ALPHA_87_IDS)) == sorted(EXCLUDED_IDS)

    def test_exclusion_reasons_documented(self) -> None:
        for excluded in (48, 56, 100):
            assert excluded in EXCLUDED_IDS

    def test_list_alphas_matches_ids(self) -> None:
        lib = WqAlpha87()
        assert lib.list_alphas() == WQ_ALPHA_87_IDS

    def test_all_87_computable_on_panel(self) -> None:
        lib = WqAlpha87()
        data = _panel()
        for alpha_id in WQ_ALPHA_87_IDS:
            out = lib.compute(alpha_id, data)
            assert out.shape == (len(_DATES), len(_SYMBOLS)), f"alpha#{alpha_id} 形状异常"
            assert out.iloc[-1].notna().any(), f"alpha#{alpha_id} 最新截面全 NaN"

    def test_unknown_alpha_raises(self) -> None:
        lib = WqAlpha87()
        with pytest.raises(Alpha87Error, match="101"):
            lib.compute(48, _panel())  # 排除集中的编号
        with pytest.raises(Alpha87Error):
            lib.compute(999, _panel())

    def test_degraded_formulas_flagged(self) -> None:
        lib = WqAlpha87()
        assert DEGRADED_FORMULAS  # IndNeutralize 降级集非空
        for alpha_id in DEGRADED_FORMULAS:
            assert alpha_id in WQ_ALPHA_87_IDS
            assert lib.is_degraded_formula(alpha_id) is True
        assert lib.is_degraded_formula(101) is False


class TestDerivedInputs:
    """派生输入仅依赖 OHLCV/成交额免费数据。"""

    def test_vwap_derived_from_amount_over_volume(self) -> None:
        lib = WqAlpha87()
        data = _panel()
        prepared = lib.prepare(data)
        expected = data["amount"] / data["volume"]
        pd.testing.assert_frame_equal(prepared["vwap"], expected)

    def test_returns_and_cap_derived(self) -> None:
        lib = WqAlpha87()
        prepared = lib.prepare(_panel())
        pd.testing.assert_frame_equal(prepared["returns"], prepared["close"].pct_change())
        pd.testing.assert_frame_equal(prepared["cap"], prepared["close"] * prepared["volume"])

    def test_explicit_vwap_not_overwritten(self) -> None:
        lib = WqAlpha87()
        data = _panel()
        data["vwap"] = data["close"] * 1.01
        prepared = lib.prepare(data)
        pd.testing.assert_frame_equal(prepared["vwap"], data["vwap"])

    def test_missing_required_field_raises(self) -> None:
        lib = WqAlpha87()
        with pytest.raises(Alpha87Error, match="close"):
            lib.prepare({"open": _panel()["open"]})


class TestPITCompliance:
    """PIT 合规：截断前缀不变性（无未来函数）。"""

    @pytest.mark.parametrize("alpha_id", [1, 5, 12, 24, 32, 54, 77, 101])
    def test_prefix_invariance(self, alpha_id: int) -> None:
        lib = WqAlpha87()
        data = _panel()
        full = lib.compute(alpha_id, data)
        n_cut = len(_DATES) - 10
        part = lib.compute(alpha_id, {k: v.iloc[:n_cut] for k, v in data.items()})
        # rolling 预热窗口外的共同区间必须逐值一致
        common = full.iloc[:n_cut].compare(part, result_names=("full", "part"))
        assert common.empty, f"alpha#{alpha_id} 截断前缀不一致（未来函数嫌疑）:\n{common.head()}"


class TestRegistrationAndIC:
    """入因子注册与逐个 IC/IR 验证接入。"""

    def test_register_all_delegates_87(self) -> None:
        lib = WqAlpha87()
        seen: list[tuple] = []
        count = lib.register_all(lambda factor_id, alpha_id: seen.append((factor_id, alpha_id)))
        assert count == 87
        assert seen[0] == ("wq_alpha_001", 1)
        assert seen[-1] == ("wq_alpha_101", 101)

    def test_validate_ic_delegates_with_factor_values(self) -> None:
        lib = WqAlpha87()
        captured: dict = {}

        def _ic_hook(factor_id: str, values: pd.DataFrame) -> dict:
            captured["factor_id"] = factor_id
            captured["shape"] = values.shape
            return {"ic_mean": 0.03, "ir": 0.5}

        result = lib.validate_ic(101, _panel(), _ic_hook)
        assert result == {"ic_mean": 0.03, "ir": 0.5}
        assert captured["factor_id"] == "wq_alpha_101"
        assert captured["shape"] == (len(_DATES), len(_SYMBOLS))

    def test_validate_ic_requires_hook(self) -> None:
        lib = WqAlpha87()
        with pytest.raises(Alpha87Error, match="ic_hook"):
            lib.validate_ic(101, _panel(), None)
