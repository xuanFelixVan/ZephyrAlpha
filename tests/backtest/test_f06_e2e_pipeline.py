# [BLUEPRINT] MOD-BT-196 | docs/03_modules/_domain_backtest/blueprint.md（端到端链路挂靠）
# [MODULE] tests.backtest.test_f06_e2e_pipeline
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.factory_grid_executor; scripts.backtest.factory_grid_anova; zephyr.position.core.position_recipe_compiler; zephyr.backtest.core.n_trial_ledger
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 端到端链路（schema→编译→子空间→求值→N_eff→ANOVA→报告渲染）零真库依赖全绿；链路任一环断即红
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assert
# [TESTS] self
# [TTL] permanent
"""test_f06_e2e_pipeline.py — F-06 端到端链路测试（合成数据，无 CH 依赖）。

链路: schema 真源 → GridCompiler 编译（活性谓词折叠）→ 子空间枚举过滤 →
recipe 求值（T2a 精确实现）→ N_eff 估计 → ANOVA 结构知识 → 报告渲染。
与生产批次的差异仅在数据源（合成 closes vs CH 行情）与回测执行（真库）——
执行/回测段的真数据验证由批次 A/B 产物 + test_factory_grid_executor 覆盖。
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_REPO = Path(__file__).resolve().parents[2]


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, _REPO / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


ex = _load("fge_e2e", "scripts/backtest/factory_grid_executor.py")
an = _load("fga_e2e", "scripts/backtest/factory_grid_anova.py")


def _synth(n_days=160, n_sym=12, seed=17):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2024-01-02", periods=n_days)
    px = pd.DataFrame(
        10 * np.exp(np.cumsum(rng.normal(0.0005, 0.012, (n_days, n_sym)), axis=0)),
        index=idx,
        columns=[f"{300000 + i}"[:6] for i in range(n_sym)],
    )
    return px


def test_e2e_schema_to_report(tmp_path) -> None:
    """端到端：真 schema 编译→子空间过滤→求值→N_eff→ANOVA→MD 报告，全链零断。"""
    from zephyr.position.core.position_recipe_compiler import GridCompiler

    # ① schema 真源编译（真 YAML）
    compiler = GridCompiler.from_yaml(_REPO / "config" / "position_recipe_grid_schema.yaml")
    expansion = compiler.compile({"strategy_pool": ["primary"], "phase": 1, "capital_ramp_enabled": False})
    assert expansion.n_raw == 362880

    # ② 子空间枚举过滤（批次 B 语义）
    subspace = {
        "D1_rebalance_freq": ["weekly"],
        "E_single_cap": ["cap10"],
        "D2_rebalance_trigger": ["periodic"],
        "G_universe": ["hs300"],
        "B_top_n": ["top30"],
        "C_sizing": ["mkt_cap", "equal_weight", "inv_vol", "risk_parity", "kelly_025", "kelly_050", "signal_strength"],
        "H_turnover_lambda": ["lambda_15bp"],
    }
    recipes = [r for r in expansion.recipes
               if all(r.values.get(k) in vs for k, vs in subspace.items())]
    assert len(recipes) == 336  # 6(A1)×2(A2)×7(C)×2(H)×2(B 子集) 子空间全枚举
    # ③ 求值（T2a 精确实现含 mkt_cap 数据面）
    closes = _synth()
    factors = ex.compute_v1_factors(closes)
    vol20 = closes.pct_change().rolling(20).std()
    rets = closes.pct_change()
    r60m, r60v = rets.rolling(60).mean(), rets.rolling(60).var()
    mkt = pd.DataFrame(1e8, index=closes.index, columns=closes.columns)  # 均值市值
    manifest = []
    for r in recipes:
        w, deg = ex.evaluate_recipe(r, closes, factors, vol20, list(closes.columns),
                                    mkt_cap_w=mkt[closes.columns], rets60_mean=r60m, rets60_var=r60v)
        ret = (w.shift(1) * closes[closes.columns].pct_change()).sum(axis=1).fillna(0.0)
        manifest.append({"recipe_id": r.recipe_id, "sharpe": float(ret.mean() / (ret.std() + 1e-12) * np.sqrt(244)),
                         "degraded_dimensions": str(degraded := deg),
                         "values_json": json.dumps(r.values, sort_keys=True)})
    md = pd.DataFrame(manifest)
    assert len(md) == 336 and md["sharpe"].abs().max() < 100

    # ④ N_eff（对齐容忍长度不齐）
    nets = {r["recipe_id"]: [0.001, -0.001, 0.002] * (30 + i % 3) for i, r in md.iterrows()}
    n_eff, meta = ex.__dict__ and __import__("zephyr.backtest.core.n_trial_ledger", fromlist=["compute_effective_rank"]).compute_effective_rank(nets)
    assert 1 <= n_eff <= len(nets)

    # ⑤ ANOVA → ⑥ 报告渲染
    tmp = tmp_path / "e2e_manifest.csv"
    md.to_csv(tmp, index=False)
    report = an.run_anova(tmp)
    assert set(report) >= {"importance", "significant_interactions", "prunable_dims"}
    rendered = an.render_report_md(report)
    assert "维度重要性表" in rendered and "可砍维度" in rendered
