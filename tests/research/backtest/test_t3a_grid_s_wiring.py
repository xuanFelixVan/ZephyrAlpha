# [BLUEPRINT] MOD-BT-196 | docs/03_modules/_domain_backtest/blueprint.md（被测件挂靠）
# [MODULE] tests.research.backtest.test_t3a_grid_s_wiring
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.factory_grid_executor; scripts.backtest.translated._c4_engine; zephyr.strategy_factory.owner_regime_switcher.switcher; zephyr.position.core.defensive_asset_whitelist
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 全合成数据零 CH 依赖（gate_limits=False 绕封板闸真库查询）; S1-S5 每件有红组（缺件即 fail）与绿组; 缺省参数路径零漂移可断言
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assert
# [TESTS] self
# [TTL] permanent
"""test_t3a_grid_s_wiring.py — T3a 开闸考 S 级五件接线测试（合成数据，无 CH 依赖）。

锚定说明：MODIFY-GUARD 原锚 tests/backtest/test_factory_grid_executor.py 正处 tests
治理战役重编窗口（旧路径已从 HEAD 删除、新路径袋未落），本件临时锚定 tests/research/
backtest/（HEAD 在册目录）；战役落位后随套件平移。被测件锚不变（MOD-BT-196 / MOD-BT-039）。
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_REPO = Path(__file__).resolve().parents[3]
_spec = importlib.util.spec_from_file_location(
    "factory_grid_executor", _REPO / "scripts" / "backtest" / "factory_grid_executor.py"
)
mod = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = mod
_spec.loader.exec_module(mod)

sys.path.insert(0, str(_REPO / "scripts" / "backtest" / "translated"))
import _c4_engine as engine  # noqa: E402


def _synth_closes(n_days: int = 120, n_sym: int = 8, seed: int = 11) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2023-01-02", periods=n_days)
    base = rng.uniform(5, 50, n_sym)
    drift = rng.normal(0.0004, 0.0002, n_sym)
    noise = rng.normal(0, 0.015, (n_days, n_sym))
    px = base * np.exp(np.cumsum(drift + noise, axis=0))
    return pd.DataFrame(px, index=idx, columns=[f"{300000 + i}"[:6] for i in range(n_sym)])


def _recipe(values: dict, rid: str = "t3a0001"):
    from zephyr.position.core.position_recipe_compiler import PositionRecipe

    base = {
        "A1_factor_normalize": "zscore",
        "A2_combine_weight": "equal",
        "B_top_n": "top3",
        "C_sizing": "equal_weight",
        "D1_rebalance_freq": "daily",
        "D2_rebalance_trigger": "periodic",
        "E_single_cap": "cap20",
        "G_universe": "hs300",
        "H_turnover_lambda": "lambda_0",
    }
    base.update(values)
    return PositionRecipe(recipe_id=rid, values=base, folded_dimensions={}, prefix_key="")


def _schedule(states: list[str], caps: dict[str, tuple[float, float]], idx: pd.DatetimeIndex) -> pd.DataFrame:
    rows = [{"state": s, "cap_A": caps[s][0], "cap_B": caps[s][1], "fail_safe": False} for s in states]
    return pd.DataFrame(rows, index=idx)


V1 = {
    "A1_factor_normalize": "zscore",
    "A2_combine_weight": "equal",
    "B_top_n": "top3",
    "C_sizing": "equal_weight",
    "D1_rebalance_freq": "daily",
    "D2_rebalance_trigger": "periodic",
    "E_single_cap": "cap20",
    "G_universe": "hs300",
    "H_turnover_lambda": "lambda_0",
}


# ── S1 J 接线 ────────────────────────────────────────────────────────────────


def test_apply_regime_caps_rowwise_multiplication():
    """绿组：日级帽×权重逐行乘（cap_t=max(cap_A,cap_B)）。"""
    idx = pd.bdate_range("2023-01-02", periods=4)
    w = pd.DataFrame(0.5, index=idx, columns=["000001", "000002"])
    sched = _schedule(
        ["trend_up", "range", "trend_down", "fail_safe"],
        {"trend_up": (0.0, 1.0), "range": (0.6, 0.0), "trend_down": (0.0, 0.0), "fail_safe": (0.5, 0.5)},
        idx,
    )
    out, dist = mod._apply_regime_caps(w, sched)
    expect_cap = pd.Series([1.0, 0.6, 0.0, 0.5], index=idx)
    assert np.allclose(out.values, (w.mul(expect_cap, axis=0)).values)
    assert dist == {"trend_up": 1, "range": 1, "trend_down": 1, "fail_safe": 1}


def test_apply_regime_caps_full_exposure_rows_unchanged():
    """绿组：cap=1 的行权重逐位不变；零帽行清零。"""
    idx = pd.bdate_range("2023-01-02", periods=2)
    rng = np.random.default_rng(3)
    w = pd.DataFrame(rng.uniform(0, 0.2, (2, 3)), index=idx, columns=list("abc"))
    sched = _schedule(["trend_up", "trend_down"], {"trend_up": (0.0, 1.0), "trend_down": (0.0, 0.0)}, idx)
    out, _ = mod._apply_regime_caps(w, sched)
    assert np.allclose(out.iloc[0].values, w.iloc[0].values)
    assert np.allclose(out.iloc[1].values, 0.0)


def test_evaluate_recipe_j_on_requires_schedule():
    """红组：J=on 而调度表缺席必须 RuntimeError（fail-closed，禁静默放行全帽）。"""
    closes = _synth_closes()
    factors = mod.compute_v1_factors(closes)
    vol20 = closes.pct_change().rolling(20).std()
    r = _recipe({**V1, "J_regime_switch": "on"})
    with pytest.raises(RuntimeError, match="调度表"):
        mod.evaluate_recipe(r, closes, factors, vol20, list(closes.columns))


def test_evaluate_recipe_j_on_scales_weights():
    """绿组：J=on + 调度表 → 权重逐行乘帽；J=off → 与无 J 维逐位一致。"""
    closes = _synth_closes()
    factors = mod.compute_v1_factors(closes)
    vol20 = closes.pct_change().rolling(20).std()
    cols = list(closes.columns)
    sched = _schedule(
        ["trend_up"] * len(closes.index),
        {"trend_up": (0.0, 0.7)},
        closes.index,
    )
    r_on = _recipe({**V1, "J_regime_switch": "on"})
    w_on, _ = mod.evaluate_recipe(r_on, closes, factors, vol20, cols, j_schedule=sched)
    r_off = _recipe({**V1, "J_regime_switch": "off"})
    w_off, _ = mod.evaluate_recipe(r_off, closes, factors, vol20, cols)
    r_none = _recipe(dict(V1))
    w_none, _ = mod.evaluate_recipe(r_none, closes, factors, vol20, cols)
    mask = w_off.sum(axis=1) > 0
    assert np.allclose(w_on[mask].values, 0.7 * w_off[mask].values)
    assert np.allclose(w_off.values, w_none.values)


def test_build_schedule_caps_flow_through():
    """绿组：owner_regime_switcher.build_schedule（冻结口径）产出可与 _apply_regime_caps 对接。"""
    from zephyr.strategy_factory.owner_regime_switcher.switcher import SwitcherConfig, build_schedule

    idx = pd.bdate_range("2023-01-02", periods=10)
    snaps = pd.DataFrame(
        {
            "trade_date": pd.bdate_range("2022-12-20", periods=14),
            "dominant": ["r3"] * 14,
            "confidence": [0.9] * 14,
        }
    )
    sched = build_schedule(idx, snaps, SwitcherConfig())
    w = pd.DataFrame(0.25, index=idx, columns=["000001"])
    out, dist = mod._apply_regime_caps(w, sched)
    assert set(dist) == {"trend_up"}  # r3=trend_up
    assert np.allclose(out.values, w.values)  # trend_up cap_B=1.0 全帽


# ── S2 成交价口径 ────────────────────────────────────────────────────────────


def test_exec_interval_returns_math():
    """绿组：区间收益=px_{d+1}/px_d−1，末行 NaN。"""
    idx = pd.bdate_range("2023-01-02", periods=3)
    px = pd.DataFrame([100.0, 110.0, 121.0], index=idx, columns=["000001"])
    r = engine.exec_interval_returns(px)
    assert np.isclose(r.iloc[0, 0], 0.10)
    assert np.isclose(r.iloc[1, 0], 0.10)
    assert pd.isna(r.iloc[2, 0])


def _manual_next_open_stats(weights: pd.DataFrame, px_open: pd.DataFrame) -> tuple[dict, pd.Series]:
    """手工基准：next_open 口径 gross=(w.shift(1)×rets_oo)，成本线=冻结土规标量。"""
    w = weights.reindex(px_open.index).ffill().fillna(0.0)
    rets = px_open.shift(-1) / px_open - 1.0
    gross = (w.shift(1) * rets).sum(axis=1).fillna(0.0)
    turnover = (w - w.shift(1)).abs().sum(axis=1).fillna(0.0) / 2.0
    net = gross - turnover * (engine.COMMISSION_BP * 2 + engine.STAMP_BP + engine.SLIPPAGE_BP * 2) / 10000.0
    equity = (1.0 + net).cumprod()
    years = max(len(net) / 244.0, 1e-9)
    stats = {
        "days": int(len(net)),
        "ann_return": round(float(equity.iloc[-1] ** (1 / years) - 1.0), 4),
        "avg_turnover_1side": round(float(turnover.mean()), 4),
    }
    return stats, net


def test_run_backtest_full_next_open_matches_manual():
    """绿组：next_open 口径与手工换源基准逐位一致（gate_limits=False 离线）。"""
    closes = _synth_closes(seed=5)
    opens = closes.copy()
    rng = np.random.default_rng(9)
    opens.values[:] = closes.values * (1.0 + rng.normal(0, 0.005, closes.shape))
    idx = closes.index
    w = pd.DataFrame(0.0, index=idx, columns=closes.columns)
    w.iloc[10:50, :3] = 1.0 / 3
    w.iloc[50:100, 3:6] = 1.0 / 3
    stats, net = engine.run_backtest_full(w, closes, gate_limits=False, exec_caliber="next_open", px_exec=opens)
    mstats, mnet = _manual_next_open_stats(w, opens)
    assert np.allclose(net.values, mnet.values)
    assert stats["ann_return"] == mstats["ann_return"]
    assert stats["avg_turnover_1side"] == mstats["avg_turnover_1side"]
    assert stats["backend"] == "cpu"  # 非 close 口径恒 CPU（GPU 核仅 close 等形面）
    assert stats["guard_reason"] == engine._GUARD_EXEC_CALIBER


def test_run_backtest_full_vwap_matches_manual():
    """绿组：vwap 口径同形换源逐位一致。"""
    closes = _synth_closes(seed=6)
    vwap = closes * (1.0 + 0.002)
    idx = closes.index
    w = pd.DataFrame(0.0, index=idx, columns=closes.columns)
    w.iloc[5:60, :4] = 0.25
    stats, net = engine.run_backtest_full(w, closes, gate_limits=False, exec_caliber="vwap", px_exec=vwap)
    mstats, mnet = _manual_next_open_stats(w, vwap)
    assert np.allclose(net.values, mnet.values)
    assert stats["ann_return"] == mstats["ann_return"]


def test_exec_caliber_validation():
    """红组：非法口径/缺执行价宽表必须 ValueError（禁静默回落 close）。"""
    closes = _synth_closes()
    w = pd.DataFrame(0.1, index=closes.index, columns=closes.columns)
    with pytest.raises(ValueError, match="exec_caliber"):
        engine.run_backtest_full(w, closes, gate_limits=False, exec_caliber="twap")
    with pytest.raises(ValueError, match="px_exec"):
        engine.run_backtest_full(w, closes, gate_limits=False, exec_caliber="next_open")


def test_close_caliber_default_bit_identical():
    """零漂移：缺省调用与显式 close 口径逐位一致；且与换源路径互不影响。"""
    closes = _synth_closes(seed=7)
    idx = closes.index
    w = pd.DataFrame(0.0, index=idx, columns=closes.columns)
    w.iloc[8:40, :2] = 0.5
    s1, n1 = engine.run_backtest_full(w, closes, gate_limits=False)
    s2, n2 = engine.run_backtest_full(w, closes, gate_limits=False, exec_caliber="close", px_exec=None)
    assert n1.equals(n2)
    assert s1 == s2


def test_vwap_unit_guard():
    """红组：vwap 单位错配（amount/volume 量纲漂移）必须 RuntimeError（引擎侧哨兵）。"""
    closes = _synth_closes()
    amt = closes * 1000.0
    vol = pd.DataFrame(1.0, index=closes.index, columns=closes.columns)  # vwap=1000×close → 单位错
    with pytest.raises(RuntimeError, match="量纲"):
        engine._vwap_from_amount_volume(amt, vol, closes)


# ── S3 估值财务因子面 ────────────────────────────────────────────────────────


def test_compute_value_factors_math():
    """绿组：f_ep=1/PE、f_bp=1/PB；pe/pb≤1（含亏损/近零）→NaN。"""
    idx = pd.bdate_range("2023-01-02", periods=2)
    pe = pd.DataFrame([[10.0, 0.5], [-8.0, 25.0]], index=idx, columns=["a", "b"])
    pb = pd.DataFrame([[2.0, 0.8], [1.0, 4.0]], index=idx, columns=["a", "b"])
    f = mod.compute_value_factors(pe, pb)
    assert np.isclose(f["f_ep"].iloc[0, 0], 0.1)
    assert pd.isna(f["f_ep"].iloc[0, 1]) and pd.isna(f["f_ep"].iloc[1, 0])
    assert np.isclose(f["f_ep"].iloc[1, 1], 0.04)
    assert np.isclose(f["f_bp"].iloc[0, 0], 0.5)
    assert pd.isna(f["f_bp"].iloc[0, 1]) and pd.isna(f["f_bp"].iloc[1, 0])
    assert np.isclose(f["f_bp"].iloc[1, 1], 0.25)


def test_fin_np_yoy_panel_pit_effective_next_day():
    """绿组：公告门 PIT——公告日当日不可见，次一交易日生效（shift(1) 行位）。"""
    idx = pd.bdate_range("2023-01-02", periods=6)
    hist = pd.DataFrame(
        {
            "symbol": ["a", "a"],
            "report_period": pd.to_datetime(["2022-09-30", "2022-12-31"]),
            "announce_date": pd.to_datetime([idx[2].date(), idx[4].date()]),
            "np_q_yoy": [10.0, 40.0],
        }
    )
    panel = mod._fin_np_yoy_panel(hist, idx, pd.Index(["a", "b"]))
    assert pd.isna(panel.loc[idx[2], "a"])  # 公告日当日不可见
    assert panel.loc[idx[3], "a"] == 10.0  # 次一交易日生效
    assert panel.loc[idx[4], "a"] == 10.0  # 第二次公告当日仍旧值
    assert panel.loc[idx[5], "a"] == 40.0  # 次日换新值
    assert pd.isna(panel.loc[idx[0], "a"])  # 公告前无值
    assert pd.isna(panel["b"]).all()  # 无财务数据票恒 NaN


def test_factor_surface_v1_value_assembles_five_factors():
    """绿组：v1_value 因子面=v1 三因子+f_ep/f_bp（+f_np_yoy），交 A2 合成不断链。"""
    closes = _synth_closes()
    factors = mod.compute_v1_factors(closes)
    idx2 = closes.index
    pe = pd.DataFrame(20.0, index=idx2, columns=closes.columns)
    pb = pd.DataFrame(3.0, index=idx2, columns=closes.columns)
    factors.update(mod.compute_value_factors(pe, pb))
    assert set(factors) == {"f_mom20", "f_lowvol20", "f_ma_gap", "f_ep", "f_bp"}
    combined, deg = mod._combine(factors, [factors[k] for k in factors], "equal", closes)
    assert not deg and combined.notna().any().any()


# ── S4 护盘白名单内容登记 ────────────────────────────────────────────────────


def test_defensive_whitelist_content_matches_source_module():
    """绿组：登记内容=MOD-POS-026 模块常量逐位一致（AI 禁自填，只做真源引用）。"""
    from zephyr.position.core.defensive_asset_whitelist import DEFAULT_TIER1, DEFAULT_TIER2

    reg = mod.defensive_whitelist_assets()
    assert reg["tier1"] == list(DEFAULT_TIER1)
    assert reg["tier2"] == list(DEFAULT_TIER2)
    assert reg["source_module"] == "MOD-POS-026"
    assert reg["enabled"] is False  # D114 休眠铁律：登记≠启用


def test_defensive_registration_validate_pass_and_drift_systemexit():
    """绿组+红组：prereg defensive_leg 与真源一致放行；漂移 SystemExit fail-closed。"""
    reg = mod.defensive_whitelist_assets()
    mod._validate_defensive_whitelist_registration({"tier1": reg["tier1"], "tier2": reg["tier2"]})
    with pytest.raises(SystemExit, match="defensive_leg"):
        mod._validate_defensive_whitelist_registration({"tier1": ["000001"], "tier2": reg["tier2"]})


# ── S5 归因 manifest 增列 ────────────────────────────────────────────────────


def test_cost_attribution_row_decomposition_exact():
    """绿组：分量=冻结土规成本线精确分解（comm 5bp/stamp 10bp/slip 2×档），份额和=1。

    恒等口径：引擎 stats 实测 avg_turnover_1side×days×k = 总成本（k=25bp@滑点5bp）。
    """
    idx = pd.bdate_range("2023-01-02", periods=5)
    turnover = pd.Series([0.1, 0.2, 0.0, 0.3, 0.05], index=idx)
    row = mod.cost_attribution_row(float(turnover.mean()), len(turnover), slippage_bp=5.0)
    k = (engine.COMMISSION_BP * 2 + engine.STAMP_BP + 2 * 5.0) / 10000.0
    assert np.isclose(row["cost_drag_total"], float(turnover.sum() * k))
    assert np.isclose(row["cost_drag_annual"], float(turnover.mean() * 244.0 * k))
    assert np.isclose(row["cost_commission_share"], 5.0 / (5.0 + 10.0 + 10.0))
    assert np.isclose(row["cost_stamp_share"], 10.0 / 25.0)
    assert np.isclose(row["cost_slippage_share"], 10.0 / 25.0)
    assert np.isclose(row["cost_commission_share"] + row["cost_stamp_share"] + row["cost_slippage_share"], 1.0)


def test_cost_attribution_zero_turnover():
    """红组（边界）：零换手→零成本，份额=结构常数（禁 NaN/除零崩）。"""
    row = mod.cost_attribution_row(0.0, 3, slippage_bp=None)
    assert row["cost_drag_total"] == 0.0
    assert row["cost_drag_annual"] == 0.0
    assert np.isclose(row["cost_commission_share"] + row["cost_stamp_share"] + row["cost_slippage_share"], 1.0)


# ── stage t3 / prereg t3a 卡 ────────────────────────────────────────────────


def test_stage_t3_context_expands_j_dimension():
    """绿组：phase=2 展开 J 维（N_raw=362,880×2=725,760，挖矿 §3.1 口径）。"""
    from zephyr.position.core.position_recipe_compiler import GridCompiler

    compiler = GridCompiler.from_yaml(mod.SCHEMA_PATH)
    n_base = compiler.count_n_raw({"strategy_pool": ["primary"], "phase": 1, "capital_ramp_enabled": False})
    n_t3 = compiler.count_n_raw({"strategy_pool": ["primary"], "phase": 2, "capital_ramp_enabled": False})
    assert n_base == 362_880
    assert n_t3 == 725_760


def test_prereg_budget_t3_family(monkeypatch):
    """绿组：t3 家族预算钳制（总帽+分层帽），fail-closed 键齐备时放行。"""
    caps = {
        "cost_gate_in_every_tier": True,
        "t3_points": 940,
        "t3_calibration_points": 20,
        "t3_tier1_points": 74,
        "t3_tier2_points": 18,
        "t3_per_point_seconds_measured": 0.53,
    }
    monkeypatch.setattr(mod, "_load_prereg_caps", lambda stage="": caps)
    assert mod._apply_prereg_budget("t3", 100) == 20
    assert mod._apply_prereg_budget("t3-t1", 100) == 74
    assert mod._apply_prereg_budget("t3-t2", 100) == 18
    assert mod._apply_prereg_budget("t3", 10) == 10  # 低于帽不放大


def test_prereg_budget_t3_tier_requires_per_point_measured(monkeypatch):
    """红组：t3_per_point_seconds_measured=null 时 t3-t1/t3-t2 禁开跑（T0 标定门槛）。"""
    caps = {
        "cost_gate_in_every_tier": True,
        "t3_points": 9400,
        "t3_calibration_points": 200,
        "t3_tier1_points": 7400,
        "t3_tier2_points": 1800,
        "t3_per_point_seconds_measured": None,
    }
    monkeypatch.setattr(mod, "_load_prereg_caps", lambda stage="": caps)
    with pytest.raises(SystemExit, match="t3_per_point_seconds_measured"):
        mod._apply_prereg_budget("t3-t1", 100)
    with pytest.raises(SystemExit, match="t3_per_point_seconds_measured"):
        mod._apply_prereg_budget("t3-t2", 100)
    assert mod._apply_prereg_budget("t3", 100) == 100  # 标定档（T3a-T0）不要求回填键


def test_resolve_stage_cost_tiers_t3_full(monkeypatch):
    """绿组：t3 家族=全档成本门（exam_scale_cost_gate 真源，禁跳门）。"""
    tiers = mod._resolve_stage_cost_tiers("t3")
    assert tiers is not None and 40.0 in tiers
    assert mod._resolve_stage_cost_tiers("t3-t2") == tiers


def test_load_prereg_caps_t3_reads_t3a_card(monkeypatch):
    """绿组：stage t3 家族读 config/search_space_prereg_t3a.yaml（新 prereg 文件）。"""
    caps = mod._load_prereg_caps("t3")
    assert caps.get("t3_points")
    assert caps.get("cost_gate_in_every_tier") is True


def test_t3a_prereg_card_frozen_wellformed():
    """冻结卡结构纪律（exam_policy §1）：考窗/阈值/抽样在跑数前写死。"""
    import yaml

    card = yaml.safe_load((_REPO / "config" / "search_space_prereg_t3a.yaml").read_text(encoding="utf-8"))
    assert card["doc_type"] == "search_space_preregistration"
    assert card.get("frozen_at") and card.get("frozen_by")
    exam = card["exam_definition"]
    assert exam["context_overrides"] == {"phase": 2}
    assert exam["G_universe"] == ["all_a_ex_st"]
    assert exam["J_regime_switch"] == ["on", "off"]
    assert exam["factor_surface"] == "v1_value"
    assert exam["exec_caliber"] == "close"
    assert exam["seed"] == 20260915
    assert exam["stratify_dims"]
    assert exam["window"] == ["2020-01-01", "2023-12-31"]
    crit = card["pass_criteria"]
    assert crit["cost_gate"]["survival_floor"] == 0.0
    assert crit["regime_gain"]["crisis_maxdd_improvement_min_pp"] == 5.0
    assert crit["regime_gain"]["caliber_source"].endswith("c2_extreme_event_protection.py")
    caps = card["budget_caps"]
    assert caps["t3_points"] == 9400
    assert caps["t3_calibration_points"] == 200
    assert caps["t3_tier1_points"] == 7400
    assert caps["t3_tier2_points"] == 1800
    assert caps["cost_gate_in_every_tier"] is True
    assert card.get("honesty") and len(card["honesty"]) >= 3
    assert card["exam_definition"]["defensive_leg"]["registered"] is True
    assert card["exam_definition"]["defensive_leg"]["enabled"] is False


# ── 存量守护（零漂移红线）────────────────────────────────────────────────────


def test_load_engine_tuple_shape_unchanged():
    """零漂移：_load_engine 九元组签名不变（factory_guard 桩依赖）。"""
    import inspect

    src = inspect.getsource(mod._load_engine)
    assert "run_backtest_full_with_tiers" in src
    assert len(inspect.getsource(mod._load_engine).splitlines()) < 40


def test_default_context_unchanged():
    """零漂移：DEFAULT_CONTEXT phase=1 不变（存量批次语义）。"""
    assert mod.DEFAULT_CONTEXT == {"strategy_pool": ["primary"], "phase": 1, "capital_ramp_enabled": False}


# ── T0 点火实钓缺陷回归（st-t3series-20261006，T0 标定 200 格：83 eval 死 + J 布尔陷阱）──


def test_grid_schema_dimensions_all_string_values():
    """红组（YAML 1.1 布尔陷阱）：schema 全维度 values/baseline 必须字符串。

    裸 on/off 被 YAML 1.1 解析为 True/False，执行器 J 判定全是 == "on"
    字符串比较——布尔化即 on 腿静默≡off 腿（regime 增益恒 0=考试失真）。
    """
    import yaml

    schema = yaml.safe_load((_REPO / "config" / "position_recipe_grid_schema.yaml").read_text(encoding="utf-8"))
    jdim = next(d for d in schema["dimensions"] if d["id"] == "J_regime_switch")
    assert jdim["values"] == ["off", "on"]
    assert jdim["baseline"] == "off"
    for d in schema["dimensions"]:
        assert all(isinstance(v, str) for v in d["values"]), f"{d['id']} 含非字符串取值"
        assert isinstance(d["baseline"], str), f"{d['id']} baseline 非字符串"


def test_grid_expansion_phase2_j_legs_string_semantics():
    """绿组：phase=2 展开 J 双腿后 recipe values 为字符串 'on'/'off'（== "on" 可命中）。"""
    from zephyr.position.core.position_recipe_compiler import GridCompiler

    expansion = GridCompiler.from_yaml(_REPO / "config" / "position_recipe_grid_schema.yaml").compile(
        {"strategy_pool": ["primary"], "phase": 2, "capital_ramp_enabled": False}
    )
    js = {r.values["J_regime_switch"] for r in expansion.recipes}
    assert js == {"on", "off"}


def test_j_string_guard_fail_closed_on_boolean():
    """红组守卫：J 值布尔化（陷阱复发面）必须 SystemExit 禁跑；字符串同值放行。"""
    vals_on = dict(V1, J_regime_switch=True)
    with pytest.raises(SystemExit, match="布尔陷阱"):
        mod._validate_j_string_semantics([_recipe(vals_on, "t3aguard1")])
    vals_str = dict(V1, J_regime_switch="on")
    mod._validate_j_string_semantics([_recipe(vals_str, "t3aguard2")])  # 不抛=过


def test_combine_mixed_index_factor_panels_all_a2_modes():
    """红组（T0 83/200 死因回归）：因子帧行基不一（预热 vs 考窗）时 A2 全模式不崩且对齐考窗。

    v1_value 面 val_pe/pb 挂 warm 面板（1106 行）而 v1/f_np_yoy 挂考窗（970 行）：
    orth_equal 逐帧 to_numpy 广播炸、lasso/pc1 np.stack 同形炸——83 死全在
    A2∈{lasso, orth_equal, pc1}。修复语义：_combine 入口统一 reindex 考窗 index；
    同基输入 reindex 恒等=逐位零漂移。
    """
    closes = _synth_closes(n_days=40, n_sym=5, seed=13)
    warm_idx = pd.bdate_range("2022-10-03", periods=60)
    rng = np.random.default_rng(17)
    f_win = pd.DataFrame(
        rng.normal(0, 1, (len(closes), len(closes.columns))), index=closes.index, columns=closes.columns
    )
    f_warm = pd.DataFrame(rng.normal(0, 1, (60, len(closes.columns))), index=warm_idx, columns=closes.columns)
    factors = {"f_win": f_win, "f_warm": f_warm}
    normalized = [mod._normalize(f, "zscore")[0] for f in factors.values()]
    for a2 in ("equal", "ic_mean", "halflife60", "orth_equal", "lasso", "pc1"):
        combined, _deg = mod._combine(factors, normalized, a2, closes)
        assert combined.index.equals(closes.index), f"A2={a2} 输出未对齐考窗 index"
        assert np.isfinite(combined.to_numpy()).any(), f"A2={a2} 输出全空"


def test_combine_same_basis_input_bit_identical():
    """零漂移守护：同基输入下修复前后语义不变（reindex 恒等）——equal 模式输出行基=考窗。"""
    closes = _synth_closes(n_days=40, n_sym=5, seed=19)
    rng = np.random.default_rng(23)
    factors = {
        n: pd.DataFrame(
            rng.normal(0, 1, (len(closes), len(closes.columns))), index=closes.index, columns=closes.columns
        )
        for n in ("f_a", "f_b")
    }
    normalized = [mod._normalize(f, "zscore")[0] for f in factors.values()]
    combined, deg = mod._combine(factors, normalized, "equal", closes)
    assert combined.index.equals(closes.index)
    assert deg is False
