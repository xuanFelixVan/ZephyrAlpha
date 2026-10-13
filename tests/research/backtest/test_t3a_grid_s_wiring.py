# [BLUEPRINT] MOD-BT-196 | docs/03_modules/_domain_backtest/blueprint.md（被测件挂靠）
# [MODULE] tests.research.backtest.test_t3a_grid_s_wiring
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.factory_grid_executor; scripts.backtest.translated._c4_engine; zephyr.strategy_factory.owner_regime_switcher.switcher; zephyr.position.core.defensive_asset_whitelist
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 全合成数据零 CH 依赖（gate_limits=False 绕封板闸真库查询）; S1-S5 每件有红组（缺件即 fail）与绿组; 缺省参数路径零漂移可断言; 千万格级名义面的展开测试一律经 `_narrow_compiler` 冻结窄批（维规格照抄真源册、非受测维冻结 baseline；谓词只读 ctx 故不改变激活判定），真源面另用 count_n_raw 零展开锚（维护七班 P1，接维护六班 §十.5 处方）
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


# ── T1 确定性分片（20261006 st-t3series：实测 9.96s/点 ⇒ T1 20.5h > 单job帽 12h）──


def test_shard_sample_partition_disjoint_union_deterministic():
    """红组：i::k 分片=互斥+并集=全集+同序确定性。"""
    sample = list(range(100))
    shards = [mod._shard_sample(sample, i, 3) for i in range(3)]
    union = sorted(x for s in shards for x in s)
    assert union == list(range(100))
    for a, b in ((0, 1), (0, 2), (1, 2)):
        assert not set(shards[a]) & set(shards[b]), f"分片 {a}/{b} 交集非空"
    assert shards[0] == list(range(0, 100, 3))
    assert mod._shard_sample(sample, 0, 3) == mod._shard_sample(sample, 0, 3)


def test_shard_sample_identity_when_unchunked_and_range_guard():
    """零漂移：num_shards 缺省=原样直返；越界 idx=ValueError 禁跑。"""
    sample = [7, 8, 9]
    assert mod._shard_sample(sample, None, None) is sample
    assert mod._shard_sample(sample, 0, None) is sample
    with pytest.raises(ValueError, match="shard_idx"):
        mod._shard_sample(sample, 2, 2)
    with pytest.raises(ValueError, match="shard_idx"):
        mod._shard_sample(sample, None, 2)


# ── M1 离场族 X 维引擎语义（20261006 st-t3series，T3b 前置；T3a 不接线=零漂移）──


def _flat_weights(idx: pd.DatetimeIndex, cols: list[str], w: float = 0.5) -> pd.DataFrame:
    return pd.DataFrame(w, index=idx, columns=cols)


def test_m1_off_mode_bit_identical():
    """off=恒等直返（未接线期零漂移锚）。"""
    closes = _synth_closes(n_days=30, n_sym=3, seed=41)
    w = _flat_weights(closes.index, list(closes.columns))
    out, mode = mod._apply_exit_overlay(w, closes, "off")
    assert mode == "off"
    assert out.equals(w)


def test_m1_tp20_target_take_profit():
    """红组（S1-03 止盈族）：涨幅触及入场价×1.20 当日收盘清仓，随后基础权重再入选=新段重入场。"""
    idx = pd.bdate_range("2023-01-02", periods=6)
    c = pd.DataFrame({"000001": [10.0, 10.0, 10.0, 12.5, 12.0, 12.0], "000002": [10.0] * 6}, index=idx)
    w = _flat_weights(idx, ["000001", "000002"])
    out, _ = mod._apply_exit_overlay(w, c, "tp20")
    # 000001: 入场价 10（day0）；day3 收盘 12.5≥12.0 触发→w=0；day4 基础权重仍在→按规则保留（overlay 只清触发日）
    assert out.loc[idx[3], "000001"] == 0.0
    assert out.loc[idx[0], "000001"] == 0.5
    assert (out["000002"] == 0.5).all()


def test_m1_trail20_trailing_stop():
    """红组（移动止盈）：持仓期运行峰值回落≥20% 当日收盘清仓；峰值按持仓段重置。"""
    idx = pd.bdate_range("2023-01-02", periods=5)
    c = pd.DataFrame({"000001": [10.0, 12.0, 12.5, 9.9, 9.9]}, index=idx)  # 峰 12.5；9.9<12.5×0.8=10.0
    w = _flat_weights(idx, ["000001"])
    out, _ = mod._apply_exit_overlay(w, c, "trail20")
    assert out.loc[idx[3], "000001"] == 0.0
    assert out.loc[idx[2], "000001"] == 0.5  # 峰值日不触发


def test_m1_atr3x_hard_stop():
    """红组（S1-02 止损族）：入场价−3×cATR14 硬带；深跌触发日收盘清仓。"""
    n = 30
    idx = pd.bdate_range("2023-01-02", periods=n)
    base = [10.0] * 20 + [10.0, 10.0] + [10.0] * 8
    vals = [10.0] * 25 + [4.0] * 5  # day25 深崩 60%（远超 3×cATR 带）
    c = pd.DataFrame({"000001": vals}, index=idx)
    w = _flat_weights(idx, ["000001"])
    out, _ = mod._apply_exit_overlay(w, c, "atr3x")
    assert out.loc[idx[25], "000001"] == 0.0
    assert (out.loc[idx[:25], "000001"] == 0.5).all()


def test_m1_unknown_mode_fail_closed():
    """未知 stop_mode=ValueError（fail-closed，禁静默当 off）。"""
    closes = _synth_closes(n_days=10, n_sym=2, seed=43)
    w = _flat_weights(closes.index, list(closes.columns))
    with pytest.raises(ValueError, match="stop_mode"):
        mod._apply_exit_overlay(w, closes, "magic_mode")


# ── M2 回撤熔断族 X 维引擎语义（X-R1-01/02，T3b 前置；T3a 不接线=零漂移）──


def test_m2_off_mode_bit_identical():
    """off=恒等直返。"""
    closes = _synth_closes(n_days=30, n_sym=3, seed=47)
    w = _flat_weights(closes.index, list(closes.columns))
    out, cap = mod._apply_dd_breaker_overlay(w, closes, "off")
    assert out.equals(w)
    assert cap is None


def test_m2_dd20_band_caps_and_peak_reference():
    """红组：组合回撤跌破带→同日帽乘性缩水（峰值=running max 非入场价）；KILL 带全关。"""
    idx = pd.bdate_range("2023-01-02", periods=5)
    # 组合 50/50 两票：+0% → +10% → −26%（dd≈−23.6% 落 DANGER/CRISIS 间）→ 0 → 0
    c = pd.DataFrame({"000001": [10.0, 10.0, 11.0, 8.0, 8.0], "000002": [10.0, 10.0, 11.0, 8.2, 8.2]}, index=idx)
    w = _flat_weights(idx, ["000001", "000002"])
    out, caps = mod._apply_dd_breaker_overlay(w, c, "dd20")
    r = c.pct_change().fillna(0.0)
    port = (w.shift(1).fillna(0.0) * r).sum(axis=1)
    nav = (1 + port).cumprod()
    dd = nav / nav.cummax() - 1
    import numpy as np

    expect = np.select([dd <= -0.20, dd <= -0.15, dd <= -0.10, dd <= -0.05], [0.0, 0.25, 0.50, 0.75], default=1.0)
    assert np.allclose(caps.to_numpy(), expect)
    assert np.allclose(out.to_numpy(), (w.mul(caps, axis=0)).to_numpy())
    assert caps.iloc[2] == 1.0 and caps.iloc[3] < 1.0  # 上涨日无帽、深跌日降帽


def test_m2_unknown_breaker_mode_fail_closed():
    """未知 breaker_mode=ValueError（fail-closed）。"""
    closes = _synth_closes(n_days=10, n_sym=2, seed=53)
    w = _flat_weights(closes.index, list(closes.columns))
    with pytest.raises(ValueError, match="breaker_mode"):
        mod._apply_dd_breaker_overlay(w, closes, "magic")


# ── M3 行业 Top-K 两层选股（L2 板块主干最简版，T3b 前置；T3a 不接线=零漂移）──


def test_m3_industry_topk_two_layer():
    """红组：行业动量 Top-K 外的个股清零；Top-K 行业内保留 combined 序；缺锚票淘汰。"""
    idx = pd.bdate_range("2023-01-02", periods=25)
    cols = ["111001", "111002", "222001", "222002", "333001"]
    rng = np.random.default_rng(61)
    base = pd.DataFrame(10.0 + np.cumsum(rng.normal(0, 0.05, (25, 5)), axis=0), index=idx, columns=cols)
    # 强推行业 11 上行、行业 22 下行（确定性动量差）
    base["111001"] = np.linspace(10, 14, 25)
    base["111002"] = np.linspace(10, 13.5, 25)
    base["222001"] = np.linspace(12, 9, 25)
    base["222002"] = np.linspace(12, 9.2, 25)
    imap = {"111001": "行业11", "111002": "行业11", "222001": "行业22", "222002": "行业22"}  # 333001 缺锚
    combined = pd.DataFrame(1.0, index=idx, columns=cols)
    out = mod._apply_industry_topk_overlay(combined, base, imap, top_k_industries=1, mom_window=20)
    late = out.iloc[-1]
    assert late["111001"] == 1.0 and late["111002"] == 1.0  # 动量冠军行业保留
    # 垫底行业/缺锚票=NaN 不进截面（与 S3 估值 NaN 档同约定，非 0 权）
    assert pd.isna(late["222001"]) and pd.isna(late["222002"])
    assert pd.isna(late["333001"])  # 缺行业锚=行业层淘汰（诚实，不静默保留）
    early = out.iloc[0]
    assert early.isna().all()  # 预热窗动量 NaN→无行业可排→全清（诚实缺供）


def test_m3_topk2_keeps_both_industries():
    """K=2 时两行业全保留（Top-K 边界语义）。"""
    idx = pd.bdate_range("2023-01-02", periods=25)
    cols = ["111001", "222001"]
    base = pd.DataFrame({"111001": np.linspace(10, 14, 25), "222001": np.linspace(12, 9, 25)}, index=idx)
    imap = {"111001": "I1", "222001": "I2"}
    combined = pd.DataFrame(1.0, index=idx, columns=cols)
    out = mod._apply_industry_topk_overlay(combined, base, imap, top_k_industries=2, mom_window=20)
    assert (out.iloc[-1] == 1.0).all()


# ── M4 K 维分批建仓路径（L4-01+P3+S2-05，T3b 前置；T3a 不接线=零漂移）──


def test_m4_lump_identity_and_linear_ramp():
    """红组：lump=恒等；linear_20d 段内第 n 日权重×n/N 线性爬坡（段重置）。"""
    idx = pd.bdate_range("2023-01-02", periods=6)
    c = pd.DataFrame(10.0, index=idx, columns=["000001"])
    w = _flat_weights(idx, ["000001"])
    out_lump, m = mod._apply_capital_ramp_overlay(w, c, "lump")
    assert m == "lump" and out_lump.equals(w)
    out, m = mod._apply_capital_ramp_overlay(w, c, "linear_20d")
    assert m == "linear_20d"
    # 段内第 1..6 日（cnt=1..6）→ 0.5×cnt/20
    expect = [0.5 * n / 20 for n in range(1, 7)]
    assert np.allclose(out["000001"].to_numpy(), expect)


def test_m4_pyramid_tranches():
    """红组：金字塔三档（入场 1/3、+3% 加至 2/3、+6% 加至 1.0）。"""
    idx = pd.bdate_range("2023-01-02", periods=4)
    c = pd.DataFrame({"000001": [10.0, 10.4, 10.7, 10.0]}, index=idx)  # day1 +4%、day2 +7%、day3 回落
    w = _flat_weights(idx, ["000001"])
    out, m = mod._apply_capital_ramp_overlay(w, c, "pyramid")
    assert m == "pyramid"
    vals = out["000001"].to_numpy()
    assert np.isclose(vals[0], 0.5 / 3)
    assert np.isclose(vals[1], 0.5 * 2 / 3)
    assert np.isclose(vals[2], 0.5)
    assert np.isclose(vals[3], 0.5)  # 已加仓档不因回落降档（路径依赖=金字塔语义）


def test_m4_unknown_ramp_mode_fail_closed():
    closes = _synth_closes(n_days=10, n_sym=2, seed=67)
    w = _flat_weights(closes.index, list(closes.columns))
    with pytest.raises(ValueError, match="ramp_mode"):
        mod._apply_capital_ramp_overlay(w, closes, "magic")


# ── M5 thesis 存活（P1-03，T3b 前置；T3a 不接线=零漂移）──


def test_m5_thesis_survival_rank_decay_exit():
    """红组：thesis 否决权语义——输入持仓段内秩下滑超阈值即持续否决，秩回升即放行（收盘判定）。"""
    idx = pd.bdate_range("2023-01-02", periods=5)
    cols = ["000001", "000002"]
    combined = pd.DataFrame(
        {"000001": [0.9, 0.2, 0.1, 0.95, 0.95], "000002": [0.5, 0.8, 0.9, 0.9, 0.9]}, index=idx
    )  # 000001 段内基准=day0 秩 1.0；day1/2 秩 0.5<0.7 否决；day3 秩回升 1.0 放行
    c = pd.DataFrame(10.0, index=idx, columns=cols)
    w = _flat_weights(idx, cols)
    out = mod._apply_thesis_survival_overlay(w, combined, c, thesis_decay=0.30)
    assert out.loc[idx[0], "000001"] == 0.5
    assert out.loc[idx[1], "000001"] == 0.0  # 秩下滑超阈值当日清仓
    assert out.loc[idx[2], "000001"] == 0.0  # 否决持续（秩未回升，段基准不重置）
    assert out.loc[idx[3], "000001"] == 0.5  # 秩回升放行
    assert (out["000002"] == 0.5).all()  # 秩上行持有


def test_m5_thesis_bad_decay_fail_closed():
    closes = _synth_closes(n_days=10, n_sym=2, seed=71)
    w = _flat_weights(closes.index, list(closes.columns))
    combined = pd.DataFrame(0.5, index=closes.index, columns=closes.columns)
    with pytest.raises(ValueError, match="thesis_decay"):
        mod._apply_thesis_survival_overlay(w, combined, closes, thesis_decay=1.5)


# ── M6 相关性 cluster 上限（C2-03，T3b 前置；T3a 不接线=零漂移）──


def test_m6_cluster_cap_blocks_correlated_pair():
    """红组：高相关对=同簇，簇帽内按权重序保留、超额清零；独立票不受累。"""
    n = 90  # > corr_window=60 进簇帽块
    idx = pd.bdate_range("2023-01-02", periods=n)
    rng = np.random.default_rng(73)
    common = rng.normal(0, 0.01, n)
    c = pd.DataFrame(
        {
            "000001": 10 * np.exp(np.cumsum(common + rng.normal(0, 0.001, n))),  # 与 2 高相关
            "000002": 10 * np.exp(np.cumsum(common + rng.normal(0, 0.001, n))),
            "000003": 10 * np.exp(np.cumsum(rng.normal(0, 0.01, n))),  # 独立
        },
        index=idx,
    )
    w = pd.DataFrame(1.0 / 3.0, index=idx, columns=list(c.columns))
    out = mod._apply_cluster_cap_overlay(w, c, corr_window=60, corr_threshold=0.5, cap_per_cluster=1)
    late = out.iloc[-1]
    kept = [col for col in c.columns if late[col] > 0]
    assert "000003" in kept  # 独立票不受累
    assert len(kept) == 2  # 高相关对只保一只（并列按符号序=000001）
    assert kept[0] == "000001"


def test_m6_warmup_window_uncapped():
    """红组：预热窗（< corr_window）无相关面→不施加簇帽（诚实缺供，非全清）。"""
    idx = pd.bdate_range("2023-01-02", periods=30)
    c = _synth_closes(n_days=30, n_sym=3, seed=79)
    w = _flat_weights(idx, list(c.columns), w=1.0 / 3.0)
    out = mod._apply_cluster_cap_overlay(w, c, corr_window=60, corr_threshold=0.5, cap_per_cluster=1)
    assert out.equals(w)  # 30<60 无块→恒等


def test_m6_bad_params_fail_closed():
    c = _synth_closes(n_days=10, n_sym=2, seed=83)
    w = _flat_weights(c.index, list(c.columns))
    with pytest.raises(ValueError, match="corr_threshold"):
        mod._apply_cluster_cap_overlay(w, c, corr_threshold=1.5)
    with pytest.raises(ValueError, match="cap_per_cluster"):
        mod._apply_cluster_cap_overlay(w, c, cap_per_cluster=0)


# ── M7 参与率帽（L4-11，INV-UNIT-001 口径；T3b 前置；T3a 不接线=零漂移）──


def test_m7_participation_cap_clips_illiquid_only():
    """红组：低流动性票目标权重被削到 participation×ADV20 名义/capital；流动性票不动。"""
    idx = pd.bdate_range("2023-01-02", periods=25)
    c = pd.DataFrame({"000001": [10.0] * 25, "000002": [10.0] * 25}, index=idx)
    v = pd.DataFrame({"000001": [1e4] * 25, "000002": [1e9] * 25}, index=idx)  # A 流通额小 1e5 名义/日
    w = _flat_weights(idx, ["000001", "000002"], w=0.5)
    out = mod._apply_participation_cap_overlay(w, v, c, participation=0.05, capital=1e8)
    # A: ADV20 名义=1e4×10=1e5 → 帽=0.05×1e5/1e8=5e-5 → 0.5 被削
    assert np.isclose(out["000001"].iloc[-1], 0.05 * 1e5 / 1e8)
    assert np.isclose(out["000002"].iloc[-1], 0.5)  # B 名义 1e10 → 帽 5.0>0.5 不削
    assert out["000002"].equals(w["000002"])


def test_m7_bad_params_fail_closed():
    c = _synth_closes(n_days=10, n_sym=2, seed=89)
    v = pd.DataFrame(1e6, index=c.index, columns=c.columns)
    w = _flat_weights(c.index, list(c.columns))
    with pytest.raises(ValueError, match="participation"):
        mod._apply_participation_cap_overlay(w, v, c, participation=0.0)
    with pytest.raises(ValueError, match="capital"):
        mod._apply_participation_cap_overlay(w, v, c, participation=0.05, capital=-1)


# ── M8 双池 5 分制（L3-03，F 维 signal_additive 搭桥；T3b 前置；T3a 不接线=零漂移）──


def test_m8_dual_pool_quintile_scores():
    """红组：动量/低波双 5 分位 signal_additive 合流——联合最优=10、联合最差=2、预热窗 NaN。"""
    idx = pd.bdate_range("2023-01-02", periods=30)
    cols = ["000001", "000002", "000003", "000004", "000005", "000006"]
    a = [0.008, 0.006, 0.004, 0.002, 0.000, -0.002]  # 动量严格递减（数值预检实证）
    b = [0.0002, 0.005, 0.010, 0.015, 0.020, 0.030]  # 振荡幅严格递增
    tt = np.arange(30)
    sq = np.where(tt % 2 == 0, 1.0, -1.0)
    data = {c: 10 * np.exp(a[i] * tt + b[i] * np.cumsum(sq)) for i, c in enumerate(cols)}
    c = pd.DataFrame(data, index=idx)
    surf = mod.dual_pool_score_surface(c, pool_window=20)
    late = surf.iloc[-1]
    assert late["000002"] == 10.0  # 联合最优（次高动量+最低波）=5+5
    assert late["000006"] == 2.0  # 联合最差（垫底动量+最高波）=1+1（分面下界=2）
    assert ((late >= 2.0) & (late <= 10.0)).all()
    assert surf.iloc[20].notna().all()  # 预热窗后全定义
    assert surf.iloc[:20].isna().all().all()  # 预热窗=NaN（诚实缺供）


def test_m8_bad_params_fail_closed():
    c = _synth_closes(n_days=10, n_sym=2, seed=97)
    with pytest.raises(ValueError, match="pool_window"):
        mod.dual_pool_score_surface(c, pool_window=0)
    with pytest.raises(ValueError, match="n_quantile"):
        mod.dual_pool_score_surface(c, pool_window=5, n_quantile=1)


# ── mkt_cap_w 考窗基对齐（GPU 快路径资格恢复，Owner 令并行化前置；20261006）──


def test_mkt_cap_warm_basis_bit_identical_to_window_basis():
    """红组：mkt_cap 定尺寸在 warm 基市值表 vs 考窗基市值表下输出逐位恒等（对齐修复语义）。

    真跑实证：mkt_cap 全部 29/29 点 fastpath_ineligible（warm 基并集 230 行≠考窗 120 行
    被等形守卫挡回 CPU）。对齐后权重=考窗形（GPU 资格恢复），净值的逐位一致性由
    "并集多余行全 NaN→引擎丢弃"保证，本测试直接对拍两基输出。
    """
    rng = np.random.default_rng(107)
    idx = pd.bdate_range("2023-01-02", periods=120)
    cols = ["000001", "000002", "000003"]
    closes = pd.DataFrame(10 * np.exp(np.cumsum(rng.normal(0, 0.01, (120, 3)), axis=0)), index=idx, columns=cols)
    vol20 = closes.pct_change().rolling(20).std()
    warm_idx = pd.bdate_range("2022-08-01", periods=150)
    mv = pd.DataFrame(rng.uniform(5e9, 5e10, (150, 3)), index=warm_idx, columns=cols)
    w_warm, _ = mod._sizing(closes, 2, "mkt_cap", vol20, mkt_cap_w=mv)
    w_win, _ = mod._sizing(closes, 2, "mkt_cap", vol20, mkt_cap_w=mv.reindex(idx))
    # 逐位一致性=考窗切片对拍（warm 基的并集多余行全 NaN→引擎侧丢弃，此即等价机理）
    pd.testing.assert_frame_equal(w_warm.loc[idx], w_win)
    assert w_win.index.equals(closes.index) and w_win.columns.equals(closes.columns)


def test_sizing_full_column_inputs_fastpath_eligible():
    """红组（mkt_cap/kelly 列并集团案）：全列市值/rets60 面经调用点切列后权重=考窗宇宙形。

    真跑实锤：s4 分片 mkt_cap 173/173、kelly 330/330 全 CPU——根因=全 5055 列面 ×
    cols 秩面=列并集，等形守卫按列拒绝（行对齐修复不够，列才是主犯）。
    """
    rng = np.random.default_rng(109)
    idx = pd.bdate_range("2023-01-02", periods=120)
    all_cols = ["000001", "000002", "000003", "000004"]
    cols = all_cols[:3]  # 宇宙子集
    closes = pd.DataFrame(10 * np.exp(np.cumsum(rng.normal(0, 0.01, (120, 4)), axis=0)), index=idx, columns=all_cols)
    vol20_cols = closes[cols].pct_change().rolling(20).std()
    mkt_full = pd.DataFrame(1e9, index=idx, columns=all_cols)
    r60m_full = closes.pct_change().rolling(60).mean()
    r60v_full = closes.pct_change().rolling(60).var()
    combined = pd.DataFrame(rng.normal(0, 1, (120, 3)), index=idx, columns=cols)
    for mode, kw in (
        ("mkt_cap", {"mkt_cap_w": mkt_full}),
        ("kelly_025", {"rets60_mean": r60m_full, "rets60_var": r60v_full}),
    ):
        w, _ = mod._sizing(combined, 2, mode, vol20_cols, **kw)
        assert w.shape == (120, 3), f"{mode} 权重形 {w.shape}≠考窗宇宙形"
        assert w.index.equals(closes.index) and w.columns.equals(pd.Index(cols)), f"{mode} 等形破坏"


def test_net_returns_parquet_columns_are_recipe_ids():
    """红组（读端实证缺陷）：net parquet 列名必须=recipe_id（values()-concat 丢键致列名
    退化 0..n=产物不自描述，判决读端配对全断）。修复=dict-concat 键即列名。"""
    idx = pd.bdate_range("2023-01-02", periods=10)
    archive = {
        "aaaa1111": pd.Series([0.01] * 10, index=idx),
        "bbbb2222": pd.Series([0.02] * 10, index=idx),
    }
    nr = pd.concat(archive, axis=1)
    assert list(nr.columns) == ["aaaa1111", "bbbb2222"]
    assert nr.shape == (10, 2)


# ── T3b X 维 schema（phase>=3 离场考；phase 1/2 折叠零漂移）──


def test_schema_x_dims_folded_below_phase3():
    """红组：X_stop/X_breaker 在 phase 1/2 必须折叠（存量考试零漂移），phase>=3 展开。"""
    import yaml

    schema = yaml.safe_load((_REPO / "config" / "position_recipe_grid_schema.yaml").read_text(encoding="utf-8"))
    xdims = {d["id"]: d for d in schema["dimensions"] if d["id"] in ("X_stop", "X_breaker")}
    assert set(xdims) == {"X_stop", "X_breaker"}
    assert xdims["X_stop"]["values"] == ["off", "atr3x", "trail20"]
    assert xdims["X_breaker"]["values"] == ["off", "dd20"]
    assert all(d["baseline"] == "off" for d in xdims.values())
    assert all(d["active_if"] == "phase >= 3" for d in xdims.values())


def _narrow_compiler(keep_dims: tuple[str, ...]):
    """冻结窄批尺（维护七班 P1＝接维护六班 §十.5 处方，两选一取"冻结窄批"＋"零展开 count_n_raw"合体）。

    病根实测：真源册 `config/position_recipe_grid_schema.yaml` 在 phase>=3 上下文下名义格点
    **13,063,680**（phase=2 面 725,760），`GridCompiler.compile()` 会逐格 `PositionRecipe`
    实体化（每格两次 `_canonical`→`json.dumps`＋两次 dict 拷贝），单格实测 14.3 µs ⇒
    整批 187 秒，直接超在册 pytest-timeout（120s，Windows thread 法杀不掉工作线程，
    实测表现为 Timeout 栈停在 `json/encoder.py:258 _iterencode`）。

    本尺做法＝**维规格逐条照抄真源册**（`active_if` / `depends_on` / `cost_tier` /
    `baseline` / 受测维的完整值集全部原样），只把**非受测维**的值集收到各自 baseline（＝1 值）。
    判别力不降的根据（在册实证，非假设）：谓词求值面 `_evaluate_active` 的命名空间＝
    `_SAFE_PREDICATE_BUILTINS + ctx`（只读 context 变量，不读其他维的取值），
    故冻结非受测维**不改变任何维的激活/折叠判定**；受测维值集原样⇒"取值集合恰等于在册集"
    这类断言仍是逐格实测，不是解析式改写。

    与真源面的数量关系由调用侧用 `count_n_raw`（O(维数) 零展开）另钉，两把尺并报。
    """
    import yaml

    from zephyr.position.core.position_recipe_compiler import GridCompiler

    data = yaml.safe_load((_REPO / "config" / "position_recipe_grid_schema.yaml").read_text(encoding="utf-8"))
    specs = []
    for s in data["dimensions"]:
        vals = list(s["values"]) if s["id"] in keep_dims else [s["baseline"]]
        specs.append({**s, "values": vals})
    return GridCompiler.from_dimensions(specs)


def test_grid_expansion_x_dims_phase_gating():
    """绿组：phase=1/2 编译 X 维折叠（N_raw 不变+values 携 baseline 'off' 字符串）；
    phase=3 展开（N_raw ×6，X 双腿字符串在册）。

    展开面走 `_narrow_compiler`（冻结窄批，见其 docstring 的实测病根）；真源册面用
    `count_n_raw` 零展开锚住"phase 闸确实放大格点面"，两把尺同钉防窄批与真源脱钩。
    """
    from zephyr.position.core.position_recipe_compiler import GridCompiler

    real = GridCompiler.from_yaml(_REPO / "config" / "position_recipe_grid_schema.yaml")
    compiler = _narrow_compiler(("X_stop", "X_breaker", "J_regime_switch"))
    base_ctx = {"strategy_pool": ["primary"], "phase": 2, "capital_ramp_enabled": False}
    e2 = compiler.compile(base_ctx)
    assert "X_stop" in e2.folded_dimensions and "X_breaker" in e2.folded_dimensions
    assert all(r.values["X_stop"] == "off" and r.values["X_breaker"] == "off" for r in e2.recipes)
    e3 = compiler.compile({**base_ctx, "phase": 3})
    assert "X_stop" in e3.active_dimensions and "X_breaker" in e3.active_dimensions
    js = {r.values["X_stop"] for r in e3.recipes}
    bs = {r.values["X_breaker"] for r in e3.recipes}
    assert js == {"off", "atr3x", "trail20"} and bs == {"off", "dd20"}
    assert e3.n_raw == e2.n_raw * 6
    # J 在 phase 3 保持展开（T3b 继承 T3a 空间）
    assert {r.values["J_regime_switch"] for r in e3.recipes} == {"on", "off"}
    # 真源册锚（零展开）：phase 闸在真源面上确实放大格点面。注意**不能钉 ×6**——
    # 实测真源 phase2→3 比值＝18（除 X_stop×X_breaker=6 外还有 X_sector 同闸 active_if
    # "phase >= 3"），×6 只属窄批面（非受测维已冻结）。
    n2 = real.count_n_raw(base_ctx)
    n3 = real.count_n_raw({**base_ctx, "phase": 3})
    assert n3 > n2, f"真源册 phase 闸未放大格点面: {n2} -> {n3}"
    assert n3 > e3.n_raw, "窄批面应显著小于真源面（否则本尺没在冻结非受测维）"


# ── T3b X 族接线（20261007 袋B：evaluate_recipe 序钉 J帽→stop→breaker；折叠 'off'=零漂移）──


def test_evaluate_recipe_x_off_identity_folded():
    """零漂移锚：X_stop/X_breaker='off'（折叠相 baseline）→ 与无 X 键 recipe 逐位一致。"""
    closes = _synth_closes(n_days=80, n_sym=4, seed=113)
    factors = mod.compute_v1_factors(closes)
    vol20 = closes.pct_change().rolling(20).std()
    cols = list(closes.columns)
    r_no_x = _recipe(dict(V1))
    w_no, _ = mod.evaluate_recipe(r_no_x, closes, factors, vol20, cols)
    r_off = _recipe({**V1, "X_stop": "off", "X_breaker": "off"})
    w_off, _ = mod.evaluate_recipe(r_off, closes, factors, vol20, cols)
    assert w_off.equals(w_no)


def test_evaluate_recipe_x_stop_trail20_wired_end_to_end():
    """绿组：X_stop=trail20 经 evaluate_recipe 全链生效——深跌票权重被离场清零。"""
    idx = pd.bdate_range("2023-01-02", periods=80)
    cols = ["000001", "000002", "000003", "000004"]
    rng = np.random.default_rng(127)
    up = 10 * np.exp(np.cumsum(rng.normal(0.002, 0.01, (80, 1)), axis=0))
    crash = np.concatenate(
        [
            10 * np.exp(np.cumsum(rng.normal(0.002, 0.01, (30, 1)), axis=0)),
            10 * np.exp(np.cumsum(rng.normal(-0.05, 0.005, (50, 1)), axis=0)),
        ]
    )
    closes = pd.DataFrame(np.hstack([up, crash, up * 0.9, crash * 1.05]), index=idx, columns=cols)
    factors = mod.compute_v1_factors(closes)
    vol20 = closes.pct_change().rolling(20).std()
    r_base = _recipe({**V1, "B_top_n": "top2", "X_stop": "trail20"})
    w_stop, _ = mod.evaluate_recipe(r_base, closes, factors, vol20, cols)
    r_base0 = _recipe({**V1, "B_top_n": "top2"})
    w_base, _ = mod.evaluate_recipe(r_base0, closes, factors, vol20, cols)
    diff_days = (w_stop.sum(axis=1) - w_base.sum(axis=1)).abs()
    assert (diff_days > 1e-12).any(), "trail20 全程无清仓=接线未生效"
    assert (w_stop.sum(axis=1) <= w_base.sum(axis=1) + 1e-12).all(), "离场只减不增"


def test_evaluate_recipe_x_breaker_dd20_wired_end_to_end():
    """绿组：X_breaker=dd20 经 evaluate_recipe 全链生效——组合深撤带触发帽缩水。"""
    idx = pd.bdate_range("2023-01-02", periods=80)
    cols = ["000001", "000002", "000003", "000004"]
    rng = np.random.default_rng(131)
    rise = 10 * np.exp(np.cumsum(rng.normal(0.004, 0.008, (40, 4)), axis=0))
    crash = rise[-1:, :] * np.exp(np.cumsum(rng.normal(-0.03, 0.004, (40, 4)), axis=0))
    closes = pd.DataFrame(np.vstack([rise, crash]), index=idx, columns=cols)
    factors = mod.compute_v1_factors(closes)
    vol20 = closes.pct_change().rolling(20).std()
    w_brk, _ = mod.evaluate_recipe(_recipe({**V1, "X_breaker": "dd20"}), closes, factors, vol20, cols)
    w_base, _ = mod.evaluate_recipe(_recipe(dict(V1)), closes, factors, vol20, cols)
    tail = slice(idx[45], idx[-1])
    assert (w_brk.loc[tail].to_numpy() <= w_base.loc[tail].to_numpy() + 1e-12).all(), "帽后权重须≤基准"
    assert (w_brk.loc[tail].to_numpy() < w_base.loc[tail].to_numpy() - 1e-12).any(), "深撤带内应有帽缩水"


def test_evaluate_recipe_x_order_pin_stop_then_breaker():
    """序钉：J帽→stop→breaker 组合输出=手工两级 compose（breaker 消费 post-stop 权重）。"""
    idx = pd.bdate_range("2023-01-02", periods=80)
    cols = ["000001", "000002", "000003", "000004"]
    rng = np.random.default_rng(137)
    up = 10 * np.exp(np.cumsum(rng.normal(0.002, 0.01, (80, 1)), axis=0))
    crash = np.concatenate(
        [
            10 * np.exp(np.cumsum(rng.normal(0.002, 0.01, (30, 1)), axis=0)),
            10 * np.exp(np.cumsum(rng.normal(-0.05, 0.005, (50, 1)), axis=0)),
        ]
    )
    closes = pd.DataFrame(np.hstack([up, crash, up * 0.9, crash * 1.05]), index=idx, columns=cols)
    factors = mod.compute_v1_factors(closes)
    vol20 = closes.pct_change().rolling(20).std()
    r_both = _recipe({**V1, "B_top_n": "top2", "X_stop": "trail20", "X_breaker": "dd20"})
    w_both, _ = mod.evaluate_recipe(r_both, closes, factors, vol20, cols)
    # 手工 compose：先 stop 后 breaker（同输入面，breaker 消费 post-stop 权重与组合权益）
    w_stop_only, _ = mod.evaluate_recipe(
        _recipe({**V1, "B_top_n": "top2", "X_stop": "trail20"}), closes, factors, vol20, cols
    )
    w_manual, _ = mod._apply_dd_breaker_overlay(w_stop_only, closes, "dd20")
    assert np.allclose(w_both.values, w_manual.values), "序钉破坏：组合输出≠stop→breaker 两级 compose"


# ── T3b stage 族（20261007 袋C：冻卡消费 fail-closed 机械）──


def test_t3b_card_frozen_and_budget_clamps():
    """红组：t3b 冻结卡在场且 frozen；预算钳制沿 t3b_* 键；实测秒/格在场解锁 t1/t2。"""
    card = mod._load_t3b_exam_card()
    assert card["exam_definition"]["context_overrides"]["phase"] == 3
    assert card["exam_definition"]["X_stop"] == ["off", "atr3x", "trail20"]
    assert card["budget_caps"]["t3b_tier1_points"] == 7400
    assert card["budget_caps"]["t3b_per_point_seconds_measured"] == 5.08
    assert mod._apply_prereg_budget("t3b-t1", 20000) == 7400
    assert mod._apply_prereg_budget("t3b", 20000) == 200
    caps = mod._load_prereg_caps("t3b-t1")
    assert caps.get("t3b_per_point_seconds_measured")


def test_t3b_context_injection_phase3_activates_x():
    """绿组：t3b 卡 context（phase=3）编译展开 X 双维——注入面与考卷面闭环。

    展开面走 `_narrow_compiler`（该卡上下文在真源册下名义 13,063,680 格＝实测超闸）；
    真源册面用 `count_n_raw` 零展开锚住"卡上下文确实触发展相"，两把尺同钉。
    """
    from zephyr.position.core.position_recipe_compiler import GridCompiler

    card = mod._load_t3b_exam_card()
    ctx = card["exam_definition"]["context_overrides"]
    expansion = _narrow_compiler(("X_stop", "X_breaker")).compile(ctx)
    assert {r.values["X_stop"] for r in expansion.recipes} == {"off", "atr3x", "trail20"}
    assert {r.values["X_breaker"] for r in expansion.recipes} == {"off", "dd20"}
    real = GridCompiler.from_yaml(_REPO / "config" / "position_recipe_grid_schema.yaml")
    n_real = real.count_n_raw(ctx)
    assert n_real > expansion.n_raw, f"卡上下文在真源册上应是展开相（名义 {n_real} 格 > 窄批 {expansion.n_raw} 格）"
    assert n_real > real.count_n_raw({**ctx, "phase": 2}), "卡上下文与 phase=2 相比未放大格点面"
