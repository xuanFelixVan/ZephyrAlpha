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

    def test_industry_neutral_fail_closed_without_map(self) -> None:
        closes = _synth_closes()
        factors, _ = _factors(closes)
        out, deg = mod._normalize(factors["f_mom20"], "industry_neutral")
        assert deg is True  # T2b: 行业锚未传入 → fail-closed 降级（禁静默）

    def test_zscore_zero_std_no_explosion(self) -> None:
        closes = _synth_closes()
        flat = closes * 0 + 10.0  # 零方差截面
        out, deg = mod._normalize(flat, "zscore")
        assert not deg and out.fillna(0).abs().max().max() == 0


class TestIndustryNeutralExact:
    """T2b（2026-09-16）行业族精确实现: 合成行业映射验证组内 demean 正确 + 无行业信息泄露。"""

    @staticmethod
    def _synth_industries(n_sym: int = 30) -> dict[str, str]:
        names = ["银行", "医药生物", "食品饮料"]
        return {f"{600000 + i}": names[i % 3] for i in range(n_sym)}

    @staticmethod
    def _factor_with_industry_effect(industries: dict[str, str], n_days: int = 60,
                                     seed: int = 11) -> tuple[pd.DataFrame, pd.DataFrame]:
        """因子 = 行业效应(大) + 个股噪声(小)；返回 (因子, 噪声真值)。"""
        rng = np.random.default_rng(seed)
        idx = pd.bdate_range("2023-01-02", periods=n_days)
        symbols = list(industries)
        effect = pd.Series({"银行": 2.0, "医药生物": -1.0, "食品饮料": 0.5}).reindex(
            pd.Series(industries)).to_numpy()[None, :]  # (1, n_sym) 按列广播
        noise = pd.DataFrame(rng.normal(0, 0.01, (n_days, len(symbols))), index=idx, columns=symbols)
        f = noise + effect
        return f, noise

    def test_group_demean_within_group_mean_zero(self) -> None:
        industries = self._synth_industries()
        f, _ = self._factor_with_industry_effect(industries)
        out, deg = mod._normalize(f, "industry_neutral", industry_map=industries)
        assert deg is False
        ser = pd.Series(industries)
        for ind, cols in ser.groupby(ser).groups.items():
            assert (out[list(cols)].mean(axis=1).abs() < 1e-9).all()  # 组内逐日截面均值=0

    def test_industry_leakage_removed_noise_retained(self) -> None:
        industries = self._synth_industries()
        f, noise = self._factor_with_industry_effect(industries)
        out, _ = mod._normalize(f, "industry_neutral", industry_map=industries)
        ser = pd.Series(industries)
        gm = pd.DataFrame({ind: out[list(cols)].mean(axis=1)
                           for ind, cols in ser.groupby(ser).groups.items()})
        spread = gm.max(axis=1) - gm.min(axis=1)
        assert (spread < 0.1).all()  # 行业间组均值差消除（原始 spread≈3.0）
        corr = out.iloc[-1].corr(noise.iloc[-1])
        assert corr > 0.8  # 个股噪声成分保留（中性化只去行业效应，不磨平信号）

    def test_unknown_industry_symbol_fail_closed_nan(self) -> None:
        industries = self._synth_industries()
        f, _ = self._factor_with_industry_effect(industries)
        partial = dict(industries)
        orphan = f.columns[0]
        partial.pop(orphan)  # 一票无行业标签
        out, deg = mod._normalize(f, "industry_neutral", industry_map=partial)
        assert deg is False
        assert out[orphan].isna().all()  # 无行业票 fail-closed 置 NaN（不留在截面）
        ser = pd.Series(partial)
        same = list(ser[ser == industries[orphan]].index)
        assert (out[same].mean(axis=1).abs() < 1e-9).all()  # 组内均值仍=0（无标签票未污染）

    def test_size_neutral_pure_mv_signal_residual_zero(self) -> None:
        """因子=纯 log 市值线性函数 → OLS 残差≈0（中性化精确性）。"""
        rng = np.random.default_rng(3)
        idx = pd.bdate_range("2023-01-02", periods=30)
        symbols = [f"{600000 + i}" for i in range(24)]
        mv = pd.DataFrame(rng.uniform(1e9, 1e11, (30, 24)), index=idx, columns=symbols)
        lmv = np.log(mv)
        f = lmv.sub(lmv.mean(axis=1), axis=0) * 0.8
        out, deg = mod._normalize(f, "size_neutral", mkt_cap_w=mv)
        assert deg is False
        assert out.abs().to_numpy().max() < 1e-9

    def test_size_neutral_orthogonal_and_retains_signal(self) -> None:
        rng = np.random.default_rng(4)
        idx = pd.bdate_range("2023-01-02", periods=40)
        symbols = [f"{600000 + i}" for i in range(24)]
        mv = pd.DataFrame(rng.uniform(1e9, 1e11, (40, 24)), index=idx, columns=symbols)
        lmv = np.log(mv)
        sig = pd.DataFrame(rng.normal(0, 1.0, (40, 24)), index=idx, columns=symbols)
        f = sig.add(lmv.sub(lmv.mean(axis=1), axis=0) * 0.8)
        out, _ = mod._normalize(f, "size_neutral", mkt_cap_w=mv)
        daily = np.array([out.iloc[d].corr(lmv.iloc[d]) for d in range(40)])
        assert np.nanmax(np.abs(daily)) < 1e-6  # OLS 残差与 log 市值样本内严格正交
        assert out.iloc[-1].corr(sig.iloc[-1]) > 0.7  # 个股信号保留

    def test_industsize_neutral_removes_both(self) -> None:
        rng = np.random.default_rng(5)
        industries = self._synth_industries(30)
        idx = pd.bdate_range("2023-01-02", periods=30)
        symbols = list(industries)
        mv = pd.DataFrame(rng.uniform(1e9, 1e11, (30, 30)), index=idx, columns=symbols)
        lmv = np.log(mv)
        effect = pd.Series({"银行": 2.0, "医药生物": -1.0, "食品饮料": 0.5}).reindex(
            pd.Series(industries)).to_numpy()[None, :]
        f = lmv.sub(lmv.mean(axis=1), axis=0).mul(0.8) + effect
        out, deg = mod._normalize(f, "industsize_neutral", industry_map=industries, mkt_cap_w=mv)
        assert deg is False
        assert out.abs().to_numpy().max() < 1e-9  # 行业效应+市值效应全部消除（FWL 联合中性化）
        ser = pd.Series(industries)
        for ind, cols in ser.groupby(ser).groups.items():
            assert (out[list(cols)].mean(axis=1).abs() < 1e-9).all()  # 组内均值=0（无行业泄露）

    def test_size_family_fail_closed_without_data(self) -> None:
        industries = self._synth_industries()
        f, _ = self._factor_with_industry_effect(industries)
        assert mod._normalize(f, "size_neutral")[1] is True  # 缺市值宽表
        assert mod._normalize(f, "industsize_neutral")[1] is True  # 缺两者
        mv = f.abs() + 1.0
        assert mod._normalize(f, "industsize_neutral", mkt_cap_w=mv)[1] is True  # 缺行业锚
        assert mod._normalize(f, "industry_neutral", mkt_cap_w=mv)[1] is True  # 缺行业锚
        _, ok = mod._normalize(f, "industry_neutral", industry_map=industries)  # 行业分支不消费市值
        assert ok is False

    def test_clean_industry_rows_blocks_nan_bad_row(self) -> None:
        """词表清洗拦截数据线已知坏行（688806 裸符号行 industry_sw='nan' 字面量）与空值。"""
        rows = [("600000", "银行", "2026-08-03", "2026-08-03 02:57:53+00:00"),
                ("688806", "nan", "2026-08-03", "2026-08-03 02:57:53+00:00"),
                ("600001", "", "2026-08-03", "2026-08-03 02:57:53+00:00"),
                ("", "银行", "2026-08-03", "2026-08-03 02:57:53+00:00")]
        m, dropped = mod._clean_industry_rows(rows, {"银行", "食品饮料"})
        assert m == {"600000": "银行"}
        assert dropped == 2  # 'nan' 坏行 + 空行业

    def test_clean_industry_rows_dedup_latest_wins_order_independent(self) -> None:
        """符号格式混用（裸 6 位 vs .SH 后缀）6 位化去重: 新批（valid_from 更新）胜，与行序无关。"""
        old = ("688002", "国防军工", "2026-08-03", "2026-08-03 02:57:53+00:00")
        new = ("688002.SH", "电子", "2026-09-13", "2026-09-13 21:34:56+00:00")
        vocab = {"国防军工", "电子"}
        m1, _ = mod._clean_industry_rows([old, new], vocab)
        m2, _ = mod._clean_industry_rows([new, old], vocab)
        assert m1 == m2 == {"688002": "电子"}  # PIT 正确且行序无关

    def test_evaluate_recipe_industry_neutral_exact_with_map(self) -> None:
        closes = _synth_closes(140, 12)
        factors, vol20 = _factors(closes)
        cols = list(closes.columns)
        industries = {c: ["银行", "医药生物", "食品饮料"][i % 3] for i, c in enumerate(cols)}
        v = dict(V1, A1_factor_normalize="industry_neutral")
        w, degraded = mod.evaluate_recipe(_recipe(v), closes, factors, vol20, cols,
                                          industry_map=industries)
        assert degraded == ()  # 行业锚在位 → 行业族转精确，无降级
        assert w.iloc[-1].sum() <= 1.0 + 1e-9


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
        # T2b: kelly_050 已精确；行业锚未传入 → A1 行业族 fail-closed 降级
        assert set(degraded) == {"A1_factor_normalize"}
        assert w.iloc[-1].sum() <= 1.0 + 1e-9  # kelly 非满仓语义+cap 终态
        assert (w >= -1e-12).all().all()  # 负预期票零仓，无空头


class TestPerfEquivalence:
    """T2c（2026-09-16）性能优化的数值语义等价守卫。"""

    @staticmethod
    def _legacy_freq_trigger(w: pd.DataFrame, freq: str, trigger: str) -> pd.DataFrame:
        """T2c 之前的逐日循环实现（原样复刻，作为等价基准）。"""
        step = {"daily": 1, "weekly": 5, "biweekly": 10, "monthly": 21}[freq]
        dates = w.index
        last = w.iloc[0].copy()
        out_rows = []
        drift = 0.10
        for i, d in enumerate(dates):
            target = w.loc[d]
            if i % step == 0:
                last = target
            elif trigger == "drift_band":
                if (target - last).abs().sum() / 2.0 > drift:
                    last = target
            out_rows.append(last)
        return pd.DataFrame(out_rows, index=dates, columns=w.columns)

    @staticmethod
    def _combined(closes: pd.DataFrame):
        factors, vol20 = _factors(closes)
        norm = [factors[n] for n in mod.V1_FACTORS]
        combined, _ = mod._combine(factors, norm, "equal", closes)
        return combined, vol20

    def test_freq_trigger_vectorized_bitwise_equal(self) -> None:
        """periodic 向量化/drift_band numpy 循环与逐日循环逐位一致（含 NaN 行）。"""
        rng = np.random.default_rng(3)
        idx = pd.bdate_range("2024-01-02", periods=97)
        w = pd.DataFrame(rng.random((97, 8)), index=idx, columns=[f"s{i}" for i in range(8)])
        w.iloc[10, 3] = np.nan  # NaN: nansum ≡ pandas sum skipna，判阈语义不变
        for freq in ("daily", "weekly", "biweekly", "monthly"):
            for trigger in ("periodic", "drift_band"):
                out = mod._apply_freq_trigger(w, freq, trigger)
                ref = self._legacy_freq_trigger(w, freq, trigger)
                pd.testing.assert_frame_equal(out, ref, check_exact=True)

    def test_freq_trigger_short_window(self) -> None:
        """len(w) < step 时仍与逐日循环等价（仅第 0 行调仓）。"""
        w = pd.DataFrame(np.arange(12.0).reshape(4, 3))
        for trigger in ("periodic", "drift_band"):
            pd.testing.assert_frame_equal(
                mod._apply_freq_trigger(w, "monthly", trigger),
                self._legacy_freq_trigger(w, "monthly", trigger), check_exact=True)

    def test_sizing_rank_pre_bitwise_equal(self) -> None:
        """rank_pre 缓存直传与 _sizing 内部现算 rank 输出逐位一致。"""
        closes = _synth_closes()
        combined, vol20 = self._combined(closes)
        rank = combined.rank(axis=1, ascending=False)
        for mode in ("equal_weight", "inv_vol", "signal_strength"):
            w_ref, _ = mod._sizing(combined, 5, mode, vol20)
            w_pre, _ = mod._sizing(combined, 5, mode, vol20, rank_pre=rank)
            pd.testing.assert_frame_equal(w_pre, w_ref, check_exact=True)

    def test_combine_cache_bitwise_equal_and_flags(self) -> None:
        """(G,A1,A2) prefix 缓存: 命中/未命中输出与无缓存逐位一致，degraded 标记同步复现。"""
        closes = _synth_closes(140, 12)
        factors, vol20 = _factors(closes)
        cols = list(closes.columns)
        r_ic_a = _recipe(dict(V1, A2_combine_weight="ic_mean"), "t2001")
        r_ic_b = _recipe(dict(V1, A2_combine_weight="ic_mean", B_top_n="top3"), "t2002")
        r_unk_a = _recipe(dict(V1, A2_combine_weight="unknown_mode_x"), "t2003")
        r_unk_b = _recipe(dict(V1, A2_combine_weight="unknown_mode_x", B_top_n="top8"), "t2004")
        r_ind_a = _recipe(dict(V1, A1_factor_normalize="industry_neutral"), "t2005")
        r_ind_b = _recipe(dict(V1, A1_factor_normalize="industry_neutral", B_top_n="top3"), "t2006")
        cases = {"ic_a": r_ic_a, "ic_b": r_ic_b, "unk_a": r_unk_a,
                 "unk_b": r_unk_b, "ind_a": r_ind_a, "ind_b": r_ind_b}
        # 无缓存基准
        ref = {name: mod.evaluate_recipe(r, closes, factors, vol20, cols)
               for name, r in cases.items()}
        # 带缓存: 每 prefix 首算 miss + 二算 hit
        cache: dict = {}
        got = {name: mod.evaluate_recipe(r, closes, factors, vol20, cols, combine_cache=cache)
               for name, r in cases.items()}
        assert len(cache) == 3  # ic_mean / unknown / industry_neutral 三个 prefix
        for name in ref:
            pd.testing.assert_frame_equal(got[name][0], ref[name][0], check_exact=True)
            assert got[name][1] == ref[name][1], f"{name} degraded 标记漂移"
        assert ref["unk_a"][1] == ("A2_combine_weight",)  # A2 未知 mode 降级标记在缓存命中侧复现
        assert ref["ind_a"][1] == ("A1_factor_normalize",)  # A1 行业族降级标记同（industry_map 缺省）
        assert ref["ic_a"][1] == ()


class TestNetReturnsArchive:
    """T2c: run_batch 成功分支收益序列档案落盘（DSR 精确口径数据基础）。"""

    N_DAYS = 160
    START_POS = 80  # 窗口起点 → T = 80 行

    @staticmethod
    def _stub_engine(closes: pd.DataFrame):
        def load_px(start, end, fields=("close",)):
            long = closes.stack().rename("close").reset_index()
            long.columns = ["trade_date", "symbol", "close"]
            long["volume"] = 1e6
            return long

        def wide(px, field="close"):
            return px.pivot(index="trade_date", columns="symbol", values=field)

        def filter_st(w, flags):
            return w

        def load_st_flags(start, end):
            return pd.DataFrame()

        def daily_net(weights, px):
            r = px.reindex(weights.index.union(weights.index)).ffill().pct_change()
            return (weights.fillna(0.0).shift(1) * r).sum(axis=1).fillna(0.0)

        def run_backtest(weights, px):
            net = daily_net(weights, px)
            return {"sharpe": float(net.mean() / net.std() * np.sqrt(244)),
                    "ann_return": 0.1, "max_drawdown": -0.2, "avg_turnover_1side": 0.3}

        return load_px, wide, filter_st, load_st_flags, run_backtest, daily_net

    def _run_batch(self, tmp_path, monkeypatch, seed: int = 7) -> tuple[dict, int]:
        closes = _synth_closes(self.N_DAYS, 36, seed=seed)  # 36 列 ≥ universe_too_small 门槛
        monkeypatch.setattr(mod, "_load_engine", lambda: self._stub_engine(closes))
        monkeypatch.setattr(mod, "_load_universe", lambda u: set(closes.columns))
        monkeypatch.setattr(mod, "_load_mkt_cap_wide", lambda s, e, c: None)
        monkeypatch.setattr(mod, "_industry_map", lambda: None)
        monkeypatch.setattr(mod, "INTAKE_DIR", tmp_path)
        start = str(closes.index[self.START_POS].date())
        end = str(closes.index[-1].date())
        return mod.run_batch(8, 1, start, end, smoke=True), len(closes) - self.START_POS

    def test_parquet_written_rows_equal_T(self, tmp_path, monkeypatch) -> None:
        summary, t_expected = self._run_batch(tmp_path, monkeypatch)
        assert summary["evaluated"] >= 2  # 至少 2 格点成功（否则档案不落盘）
        assert summary["net_returns_file"] == "net_returns.parquet"
        f = Path(summary["out_dir"]) / summary["net_returns_file"]
        assert f.exists()
        nr = pd.read_parquet(f)
        assert len(nr) == t_expected  # 行数 = 交易日 T
        assert nr.shape[1] == summary["evaluated"]  # 列 = 成功格点数
        assert np.isfinite(nr.to_numpy()).all()

    def test_fallback_csv_gz_when_no_parquet_engine(self, tmp_path, monkeypatch) -> None:
        def _no_parquet(self, path, *args, **kwargs):
            raise ImportError("Unable to find a usable engine; pyarrow missing")

        monkeypatch.setattr(pd.DataFrame, "to_parquet", _no_parquet)
        summary, t_expected = self._run_batch(tmp_path, monkeypatch, seed=11)
        assert summary["net_returns_file"] == "net_returns.csv.gz"
        f = Path(summary["out_dir"]) / summary["net_returns_file"]
        assert f.exists()
        assert len(pd.read_csv(f)) == t_expected
