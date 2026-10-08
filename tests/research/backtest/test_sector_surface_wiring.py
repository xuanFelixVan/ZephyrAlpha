# [BLUEPRINT] MOD-BT-238 | docs/03_modules/_domain_backtest/blueprint.md（被测件挂靠）
# [MODULE] tests.research.backtest.test_sector_surface_wiring
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.sector_surface; scripts.backtest.factory_grid_executor; zephyr.position.core.position_recipe_compiler
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 合成数据零真库依赖（禁 CH/禁写 data/）; 四路子分逐值对码规格卡 §2 计算式; 传导三档乘数封闭口径（≥9→1.15/≥6→1.05/<6→0.90）; X_sector=off 零漂移逐位相等; conduction 缺 sector_ctx fail-closed; phase=1 折叠相 N_raw 不变全 'off'（phase>=3 全展开 13M 点编译过重不入单测——折叠语义由编译器 active_if 既有单测族+phase1 断言承载）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assert
# [TESTS] self
# [TTL] permanent
"""test_sector_surface_wiring.py — W5 板块传导后处理+板块强度四路接线单测（合成数据）。"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_REPO = Path(__file__).resolve().parents[3]


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, _REPO / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


surf = _load("sector_surface", "scripts/backtest/sector_surface.py")
mod = _load("factory_grid_executor", "scripts/backtest/factory_grid_executor.py")

_INDUSTRIES = ("强势行业A", "弱势行业B")
_SYMS_A = ("600000", "600001", "600002")
_SYMS_B = ("600003", "600004", "600005")


def _synth_panel() -> surf.SectorPanel:
    """两行业×各 3 票×40 日合成面板：A 上行+封板+资金流入，B 反之（方向确定可断言）。"""
    idx = pd.bdate_range("2024-01-02", periods=40)
    cols = list(_SYMS_A + _SYMS_B)
    close = pd.DataFrame(10.0, index=idx, columns=cols)
    close[list(_SYMS_A)] = close[list(_SYMS_A)].add(np.linspace(0.0, 10.0, 40), axis=0)  # A 线性上行
    close[list(_SYMS_B)] = close[list(_SYMS_B)].sub(np.linspace(0.0, 3.0, 40), axis=0)  # B 阴跌
    amount = pd.DataFrame(1e8, index=idx, columns=cols)
    amount[list(_SYMS_A)] = 3e8  # A 成交占优
    sealed = pd.DataFrame(False, index=idx, columns=cols)
    sealed.iloc[-2:, list(range(3))] = True  # A 末两日全封（涨停比+梯队代理双触发）
    flow_idx = pd.DatetimeIndex([idx[-5], idx[-4], idx[-3], idx[-2], idx[-1]])
    flow = pd.DataFrame({"强势行业A": 100.0, "弱势行业B": -50.0}, index=flow_idx)
    big = pd.DataFrame({"强势行业A": 40.0, "弱势行业B": -20.0}, index=flow_idx)
    imap = {s: _INDUSTRIES[0] for s in _SYMS_A}
    imap.update({s: _INDUSTRIES[1] for s in _SYMS_B})
    ind_keys = [imap[c] for c in cols]
    return surf.SectorPanel(
        ind_close=close.T.groupby(ind_keys).mean().T.sort_index(),
        ind_amount=amount.T.groupby([imap[c] for c in cols]).sum().T.sort_index(),
        sealed_up=sealed,
        industry_map=imap,
        flow_3d=flow.rolling(3, min_periods=1).sum(),
        big_net=big,
        degraded_flags=(),
    )


class TestSectorStrengthFourWay:
    def test_four_way_extreme_spread(self) -> None:
        panel = _synth_panel()
        score, pool, degraded = surf.sector_strength(panel)
        last = score.iloc[-1]
        assert degraded == ()
        assert last["强势行业A"] == pytest.approx(100.0, abs=1e-9)  # 四路全满分
        # B 三路 rank-pct=50（双行业 rank 下限 1/n）+结构 0 → 0.25×150=37.5
        assert last["弱势行业B"] == pytest.approx(37.5, abs=1e-9)
        valid = score.dropna(how="all")
        assert valid.to_numpy().min() >= 0.0 and valid.to_numpy().max() <= 100.0
        assert score.iloc[:20].isna().all().all()  # 预热窗（mom20+diff5）=诚实缺供 NaN
        assert bool(pool.iloc[-1]["强势行业A"]) and not bool(pool.iloc[-1]["弱势行业B"])

    def test_pool_bottom_line_one(self) -> None:
        panel = _synth_panel()
        score, pool, _ = surf.sector_strength(panel)
        assert pool[score.notna().any(axis=1)].any(axis=1).all()  # 有分行保底 1（85 分位≤max 内蕴）

    def test_flow_absent_degrades_renormalized(self) -> None:
        p = _synth_panel()
        panel = surf.SectorPanel(
            ind_close=p.ind_close,
            ind_amount=p.ind_amount,
            sealed_up=p.sealed_up,
            industry_map=p.industry_map,
            flow_3d=None,
            big_net=None,
            degraded_flags=p.degraded_flags,
        )
        score, _, degraded = surf.sector_strength(panel)
        assert "flow_dim_absent_renormalized" in degraded
        last = score.iloc[-1]
        # 三路重归一：A=(100+100+100)/3=100，B=(0+50+50)/3=33.33——量纲仍 [0,100]
        assert last["强势行业A"] == pytest.approx(100.0, abs=1e-9)
        assert last["弱势行业B"] == pytest.approx(100.0 / 3.0, abs=1e-9)

    def test_market_adjustment_clamped(self) -> None:
        panel = _synth_panel()
        score, _, _ = surf.sector_strength(panel, market_adjustment=-200.0)
        assert score.iloc[-1]["强势行业A"] == pytest.approx(0.0, abs=1e-9)  # clamp 下界
        assert score.iloc[-1]["弱势行业B"] == pytest.approx(0.0, abs=1e-9)


class TestConductionMultiplier:
    def test_three_tier_frozen_table(self) -> None:
        df = pd.DataFrame([[9.5, 9.0, 8.9, 6.0, 5.9, 0.0]])
        out = surf.conduction_multiplier(df)
        assert out.iloc[0].tolist() == pytest.approx([1.15, 1.15, 1.05, 1.05, 0.90, 0.90])


class TestSectorOverlay:
    def _ctx(self, panel_score: dict[str, float]) -> dict:
        idx = pd.bdate_range("2024-01-02", periods=40)
        score = pd.DataFrame(panel_score, index=idx)
        pool = score.ge(score.quantile(0.85, axis=1), axis=0)
        amount = pd.DataFrame(3e8, index=idx, columns=list(_SYMS_A + _SYMS_B))
        return {"sector_score": score, "pool_mask": pool, "amount": amount}

    def _combined(self) -> pd.DataFrame:
        idx = pd.bdate_range("2024-02-01", periods=5)
        vals = [10.0, 9.0, 8.0, 7.0, 6.0, 5.0]
        return pd.DataFrame([vals] * 5, index=idx, columns=list(_SYMS_A + _SYMS_B))

    def test_strength_top15_masks_out_of_pool(self) -> None:
        combined = self._combined()
        out = mod._apply_sector_overlay(
            combined, self._ctx({"强势行业A": 95.0, "弱势行业B": 30.0}), _synth_panel().industry_map, "strength_top15"
        )
        assert out[list(_SYMS_A)].equals(combined[list(_SYMS_A)])  # 池内行业原样
        assert out[list(_SYMS_B)].isna().all().all()  # 池外行业整列 NaN（不进截面）

    def test_conduction_gate_and_multiplier(self) -> None:
        combined = self._combined()
        out = mod._apply_sector_overlay(
            combined, self._ctx({"强势行业A": 95.0, "弱势行业B": 30.0}), _synth_panel().industry_map, "conduction"
        )
        # A 行业 sec10=9.5>6 过板块关；个股强度 rank×10=[10,8.33,6.67,5,3.33,1.67]
        # → A 板块内前三票 stock10>5 过个股关，第 4 票=5 恰不>5 拦；乘数 ×1.15
        assert out.iloc[0]["600000"] == pytest.approx(11.5)
        assert out.iloc[0]["600001"] == pytest.approx(9.0 * 1.15)
        assert out.iloc[0]["600002"] == pytest.approx(8.0 * 1.15)
        assert np.isnan(out.iloc[0]["600005"])  # 弱板块弱票：gate 不过=不进打分池
        assert np.isnan(out.iloc[0]["600003"])  # 弱板块强票：板块关不过→打折也不放行（gate 先行）

    def test_conduction_amount_gate(self) -> None:
        combined = self._combined()
        ctx = self._ctx({"强势行业A": 95.0, "弱势行业B": 30.0})
        ctx["amount"] = ctx["amount"].copy()
        ctx["amount"]["600000"] = 1e8  # 日成交 1 亿 <2 亿门槛
        out = mod._apply_sector_overlay(combined, ctx, _synth_panel().industry_map, "conduction")
        assert np.isnan(out.iloc[0]["600000"])  # 流动性关不过
        assert out.iloc[0]["600001"] == pytest.approx(9.0 * 1.15)

    def test_unknown_mode_rejected(self) -> None:
        with pytest.raises(ValueError, match="X_sector"):
            mod._apply_sector_overlay(self._combined(), self._ctx({}), {}, "bogus")

    def test_no_industry_anchor_fail_closed(self) -> None:
        with pytest.raises(RuntimeError, match="行业锚"):
            mod._apply_sector_overlay(self._combined(), self._ctx({"A": 95.0}), {}, "strength_top15")


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


def _synth_closes(n_days: int = 120, n_sym: int = 12, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2023-01-02", periods=n_days)
    base = rng.uniform(5, 50, n_sym)
    drift = rng.normal(0.0004, 0.0002, n_sym)
    noise = rng.normal(0, 0.015, (n_days, n_sym))
    px = base * np.exp(np.cumsum(drift + noise, axis=0))
    return pd.DataFrame(px, index=idx, columns=[f"{300000 + i}"[:6] for i in range(n_sym)])


def _recipe(extra: dict | None = None, rid: str = "w5test0001"):
    from zephyr.position.core.position_recipe_compiler import PositionRecipe

    values = dict(V1)
    values.update(extra or {})
    return PositionRecipe(recipe_id=rid, values=values, folded_dimensions={}, prefix_key="")


class TestEvaluateRecipeWiring:
    def test_off_is_zero_drift(self) -> None:
        closes = _synth_closes()
        factors = mod.compute_v1_factors(closes)
        vol20 = closes.pct_change().rolling(20).std()
        cols = list(closes.columns)
        base, _ = mod.evaluate_recipe(_recipe(), closes, factors, vol20, cols)
        off, _ = mod.evaluate_recipe(_recipe({"X_sector": "off"}), closes, factors, vol20, cols)
        pd.testing.assert_frame_equal(base, off)  # 折叠相零漂移（逐位相等）

    def test_conduction_requires_ctx_fail_closed(self) -> None:
        closes = _synth_closes()
        factors = mod.compute_v1_factors(closes)
        vol20 = closes.pct_change().rolling(20).std()
        with pytest.raises(RuntimeError, match="sector_ctx"):
            mod.evaluate_recipe(
                _recipe({"X_sector": "conduction"}),
                closes,
                factors,
                vol20,
                list(closes.columns),
            )


class TestSchemaFold:
    def test_phase1_fold_unchanged_grid(self) -> None:
        from zephyr.position.core.position_recipe_compiler import GridCompiler

        compiler = GridCompiler.from_yaml(_REPO / "config" / "position_recipe_grid_schema.yaml")
        expansion = compiler.compile({"strategy_pool": ["primary"], "phase": 1, "capital_ramp_enabled": False})
        assert expansion.n_raw == 362880  # schema 头注名义 N（X_sector 折叠贡献=1）
        assert all(r.values["X_sector"] == "off" for r in expansion.recipes)

    def test_schema_declares_sector_dim(self) -> None:
        import yaml

        raw = yaml.safe_load((_REPO / "config" / "position_recipe_grid_schema.yaml").read_text("utf-8"))
        dim = next(d for d in raw["dimensions"] if d["id"] == "X_sector")
        assert dim["values"] == ["off", "strength_top15", "conduction"]
        assert dim["baseline"] == "off"
        assert dim["active_if"] == "phase >= 3"
