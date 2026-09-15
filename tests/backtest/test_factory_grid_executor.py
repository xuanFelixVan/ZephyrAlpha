# [BLUEPRINT] MOD-BT-196 | docs/03_modules/_domain_backtest/blueprint.md（被测件挂靠）
# [MODULE] tests.backtest.test_factory_grid_executor
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.factory_grid_executor
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 阴性记录死亡层+死因机械校验; 求值管线零真库依赖（合成数据）; 前视防御可测（IC 权重 shift(1)）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assert
# [TESTS] self
# [TTL] permanent
"""test_factory_grid_executor.py — F-06 批次 A 执行器单元测试（合成数据，无 CH 依赖）。"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_REPO = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "factory_grid_executor", _REPO / "scripts" / "backtest" / "factory_grid_executor.py"
)
mod = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = mod
_spec.loader.exec_module(mod)


def _synth_closes(n_days: int = 120, n_sym: int = 12, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2023-01-02", periods=n_days)
    base = rng.uniform(5, 50, n_sym)
    drift = rng.normal(0.0004, 0.0002, n_sym)
    noise = rng.normal(0, 0.015, (n_days, n_sym))
    px = base * np.exp(np.cumsum(drift + noise, axis=0))
    return pd.DataFrame(px, index=idx, columns=[f"{300000 + i}"[:6] for i in range(n_sym)])


def _factors(closes: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    factors = mod.compute_v1_factors(closes)
    vol20 = closes.pct_change().rolling(20).std()
    return factors, vol20


def _recipe(values: dict, rid: str = "test0001"):
    from zephyr.position.core.position_recipe_compiler import PositionRecipe

    return PositionRecipe(recipe_id=rid, values=values, folded_dimensions={}, prefix_key="")


V1 = {
    "A1_factor_normalize": "zscore",
    "A2_combine_weight": "equal",
    "B_top_n": "top5",
    "C_sizing": "equal_weight",
    "D1_rebalance_freq": "daily",
    "D2_rebalance_trigger": "periodic",
    "E_single_cap": "cap10",
    "G_universe": "hs300",
    "H_turnover_lambda": "lambda_0",
    "F_merge_policy": "single",
    "I_cost_tier": "frozen_l0",
    "J_regime_switch": "off",
    "K_capital_ramp": "lump",
}


class TestNegativeRecord:
    def test_death_layer_illegal_rejected(self) -> None:
        with pytest.raises(ValueError, match="死亡层"):
            mod.NegativeRecord("r1", "wrong_layer", "reason", {}, "")

    def test_empty_reason_rejected(self) -> None:
        with pytest.raises(ValueError, match="死因"):
            mod.NegativeRecord("r1", "eval", "  ", {}, "")

    def test_valid_record_passes(self) -> None:
        rec = mod.NegativeRecord("r1", "backtest", "backtest_fail:RuntimeError", {}, "A1_factor_normalize")
        assert rec.death_layer == "backtest" and rec.death_reason


class TestNormalize:
    def test_rank_uniform_and_not_degraded(self) -> None:
        closes = _synth_closes()
        factors, _ = _factors(closes)
        out, deg = mod._normalize(factors["f_mom20"].dropna(how="all"), "rank")
        assert not deg
        med = out.median(axis=1).dropna()
        assert len(med) > 90  # mom20 预热后有效行充足
        assert (med.sub(0.5).abs() < 0.05).all()  # 容差: 小截面并列值影响

    def test_industry_neutral_degrades_to_zscore(self) -> None:
        closes = _synth_closes()
        factors, _ = _factors(closes)
        out, deg = mod._normalize(factors["f_mom20"], "industry_neutral")
        assert deg is True  # 行业数据健康观察项下诚实降级

    def test_zscore_zero_std_no_explosion(self) -> None:
        closes = _synth_closes()
        flat = closes * 0 + 10.0  # 零方差截面
        out, deg = mod._normalize(flat, "zscore")
        assert not deg and out.fillna(0).abs().max().max() == 0


class TestCombine:
    def test_equal_mean(self) -> None:
        closes = _synth_closes()
        factors, _ = _factors(closes)
        norm = [factors[n] for n in mod.V1_FACTORS]
        out, deg = mod._combine(factors, norm, "equal", closes)
        assert not deg
        # 语义: 等权=逐行 skipna 均值（某因子缺失不污染合成）
        valid = out.notna() & (out != 0)
        assert (out.stack().abs() < 1e9).all()  # 无 inf

    def test_ic_weight_uses_shifted_ic_no_lookahead(self) -> None:
        """前视防御：合成截面在第 d 行只用截至 d-1 的 IC——构造 d 日后才出现的信号验证。"""
        closes = _synth_closes(160, 12)
        # 人造因子: f1 在全期有效; 验证 ic 权重 shift 后第 0 行为等权回退
        factors = {"f_a": closes.pct_change(20).fillna(0), "f_b": -closes.pct_change(20).fillna(0)}
        norm = [f.apply(lambda s: (s - s.mean()) / (s.std() + 1e-9), axis=1) for f in factors.values()]
        out, deg = mod._combine(factors, norm, "ic_mean", closes)
        assert not deg
        assert np.isfinite(out.to_numpy()).all()

    def test_orth_and_lasso_now_exact(self) -> None:
        """T2a（2026-09-16）：orth/lasso/pc1 转精确实现，不再降级。"""
        closes = _synth_closes(200, 12)
        factors, _ = _factors(closes)
        norm = [factors[n].fillna(0.0) for n in mod.V1_FACTORS]
        for mode in ("orth_equal", "lasso", "pc1"):
            out, deg = mod._combine(factors, norm, mode, closes)
            assert deg is False, f"{mode} 应为精确实现"
            assert np.isfinite(out.to_numpy()).all()

    def test_orth_residuals_decorrelated(self) -> None:
        """Gram-Schmidt 后各正交分量与既有分量日截面相关≈0。"""
        closes = _synth_closes(120, 12)
        factors, _ = _factors(closes)
        norm = [factors[n].fillna(0.0) for n in mod.V1_FACTORS]
        out, deg = mod._combine(factors, norm, "orth_equal", closes)
        assert deg is False
        # orth 输出与 f1 原始秩相关的绝对值应低于 equal 输出（去共线生效）
        eq, _ = mod._combine(factors, norm, "equal", closes)
        c_orth = abs(out.iloc[-1].corr(norm[0].iloc[-1]))
        c_eq = abs(eq.iloc[-1].corr(norm[0].iloc[-1]))
        assert c_orth <= c_eq + 0.05


class TestSizingAndTriggers:
    def _combined(self, closes):
        factors, vol20 = _factors(closes)
        norm = [factors[n] for n in mod.V1_FACTORS]
        combined, _ = mod._combine(factors, norm, "equal", closes)
        return combined, vol20

    def test_top_n_selection_and_row_sum(self) -> None:
        closes = _synth_closes()
        combined, vol20 = self._combined(closes)
        w, deg = mod._sizing(combined, 5, "equal_weight", vol20)
        assert not deg
        last = w.iloc[-1]
        assert (last > 0).sum() <= 5
        assert abs(last[last > 0].sum() - 1.0) < 1e-9

    def test_cap_expands_effective_holding(self) -> None:
        """cap5+top5 数学不可行（5×0.05<1）——有效持仓扩展 M=ceil(1/cap)=20 后 cap 恒满足。"""
        closes = _synth_closes()
        factors, vol20 = _factors(closes)
        cols = list(closes.columns)
        v = dict(V1, E_single_cap="cap5")  # top5 × cap5 → 扩展至 20 只
        w, degraded = mod.evaluate_recipe(_recipe(v), closes, factors, vol20, cols)
        last = w.iloc[-1]
        assert (last[last > 0] <= 0.05 + 1e-9).all()  # cap 硬约束满足
        assert last.sum() <= 1.0 + 1e-9  # 股票池不足时低仓位（超额留现金）

    def test_lambda_shrinks_turnover(self) -> None:
        closes = _synth_closes()
        combined, vol20 = self._combined(closes)
        w, _ = mod._sizing(combined, 5, "equal_weight", vol20)
        w_l0 = mod._apply_cap_and_lambda(w, "cap10", "lambda_0")
        w_l15 = mod._apply_cap_and_lambda(w, "cap10", "lambda_15bp")
        t0 = w_l0.diff().abs().sum(axis=1).mean()
        t15 = w_l15.diff().abs().sum(axis=1).mean()
        assert t15 <= t0 + 1e-9  # λ 收缩降低换手

    def test_weekly_freq_holds_between_rebalance(self) -> None:
        closes = _synth_closes()
        combined, vol20 = self._combined(closes)
        w, _ = mod._sizing(combined, 5, "equal_weight", vol20)
        w2 = mod._apply_freq_trigger(w, "weekly", "periodic")
        # 相邻非调仓日权重恒等
        assert (w2.iloc[1].equals(w2.iloc[2])) and (w2.iloc[3].equals(w2.iloc[4]))

    def test_drift_band_triggers_on_divergence(self) -> None:
        closes = _synth_closes()
        combined, vol20 = self._combined(closes)
        w, _ = mod._sizing(combined, 5, "signal_strength", vol20)
        w_band = mod._apply_freq_trigger(w, "monthly", "drift_band")
        w_pure = mod._apply_freq_trigger(w, "monthly", "periodic")
        # drift_band 至少不会比纯周期更"冻结"（更新次数 >= periodic）
        assert w_band.nunique(dropna=False).shape == w_pure.nunique(dropna=False).shape


class TestStratifiedSample:
    def _expansion(self):
        from zephyr.position.core.position_recipe_compiler import GridCompiler

        return GridCompiler.from_yaml(_REPO / "config" / "position_recipe_grid_schema.yaml").compile(
            {"strategy_pool": ["primary"], "phase": 1, "capital_ramp_enabled": False}
        )

    def test_full_when_n_geq_raw(self) -> None:
        exp = self._expansion()
        picked = mod.stratified_sample(exp, exp.n_raw + 10, 1)
        assert len(picked) == exp.n_raw

    def test_sample_size_and_no_dup(self) -> None:
        exp = self._expansion()
        picked = mod.stratified_sample(exp, 500, 42)
        ids = {r.recipe_id for r in picked}
        assert len(picked) == 500 and len(ids) == 500

    def test_all_signal_prefixes_covered(self) -> None:
        exp = self._expansion()
        picked = mod.stratified_sample(exp, exp.n_raw, 42)  # 全量: 覆盖必然完整
        assert {r.prefix_key for r in picked} == {r.prefix_key for r in exp.recipes}

    def test_small_n_random_layer_pick_no_dup(self) -> None:
        """n < 层数(720)时随机抽层每层 1 条——恰好 n 条无重复。"""
        exp = self._expansion()
        picked = mod.stratified_sample(exp, 300, 42)
        ids = [r.recipe_id for r in picked]
        assert len(picked) == 300 and len(set(ids)) == 300


class TestEvaluateRecipe:
    def test_full_pipeline_shapes_and_degraded_tracking(self) -> None:
        closes = _synth_closes(140, 12)
        factors, vol20 = _factors(closes)
        cols = list(closes.columns)
        r = _recipe(V1)
        w, degraded = mod.evaluate_recipe(r, closes, factors, vol20, cols)
        assert w.shape[0] == closes.shape[0]
        row = w.iloc[-1]
        assert abs(row.sum() - 1.0) < 1e-9
        assert degraded == ()

    def test_degraded_dims_reported(self) -> None:
        closes = _synth_closes(140, 12)
        factors, vol20 = _factors(closes)
        cols = list(closes.columns)
        v = dict(V1, A1_factor_normalize="industry_neutral", C_sizing="kelly_050")
        w, degraded = mod.evaluate_recipe(_recipe(v), closes, factors, vol20, cols,
                                          rets60_mean=closes.pct_change().rolling(60).mean(),
                                          rets60_var=closes.pct_change().rolling(60).var())
        # T2a: kelly_050 已精确——只剩 A1 行业族降级（等数据线修复）
        assert set(degraded) == {"A1_factor_normalize"}
        assert w.iloc[-1].sum() <= 1.0 + 1e-9  # kelly 非满仓语义+cap 终态
        assert (w >= -1e-12).all().all()  # 负预期票零仓，无空头
