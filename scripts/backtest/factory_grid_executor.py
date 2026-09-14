# [BLUEPRINT] MOD-BT-196 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.factory_grid_executor
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.position.core.position_recipe_compiler; scripts.backtest.translated._c4_engine
# [CONSUMERS] data/strategy_intake/grid_<ts>/（出生证 manifest+阴性库）；factory_grid_ananova；E2 四车道（挂接预留）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] schema 一次定型（config/position_recipe_grid_schema.yaml 唯一真源，禁删维）；抽样完整性 100%（抽了必跑，禁截断）；每 recipe 带出生证+degraded 标记；阴性记录 MUST 带死亡层+死因否则校验拒绝；回测口径=冻结土规 T+1（引擎复用零重实现）；行业真源=sws2021_l1（schema industry_anchor）；降级取值必须标 degraded（结构知识阶段剔除，禁静默）
# [MODIFY-GUARD] tests/backtest/test_factory_grid_executor.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失/求值失败)；ValueError(schema/契约非法)
# [TESTS] tests/backtest/test_factory_grid_executor.py
# [A_module] module_id=MOD-BT-196 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""F-06 组合层穷尽网格——批次 A 普查执行器（MOD-BT-196）。

编译（MOD-POS-029 GridCompiler）→ signal 侧分层抽样 → recipe→weights 求值 →
冻结土规向量化回测（复用 _c4_engine，零重实现）→ 出生证 manifest + 阴性库。

v1 求值实现边界（诚实披露，立项稿 §十二 两批次的批次 A）:
  精确实现: B_top_n 全部 / D1_rebalance_freq 全部 / D2_rebalance_trigger 全部 /
            E_single_cap 全部 / G_universe 全部 / H_turnover_lambda 全部 /
            A1(raw/rank/zscore) / A2(equal/ic_mean/ic_ir/halflife20/halflife60) /
            C(equal_weight/inv_vol/signal_strength)
  降级实现(degraded=true, 结构知识阶段剔除): A1(industry_neutral/size_neutral/
            industsize_neutral→zscore; 行业数据健康观察项) /
            A2(orth_equal/lasso/pc1→equal) / C(mkt_cap/risk_parity/kelly_*
            →inv_vol) —— 格点照跑（抽样完整性 100%），结果标 non-informative。

用法:
  python scripts/backtest/factory_grid_executor.py --smoke                 # 烟测（管线联通，8 格点）
  python scripts/backtest/factory_grid_executor.py --n-samples 20000       # 批次 A 普查
产出: data/strategy_intake/grid_<run_ts>/manifest.csv + negatives.csv + summary.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "scripts" / "backtest" / "translated"))
sys.path.insert(0, str(_REPO / "scripts" / "backtest"))

SCHEMA_PATH = _REPO / "config" / "position_recipe_grid_schema.yaml"
INTAKE_DIR = _REPO / "data" / "strategy_intake"

# 死亡层枚举（立项稿 §十三: 阴性必须带死亡层+死因，否则不计）
DEATH_LAYERS = ("eval", "backtest", "gate")

DEFAULT_CONTEXT = {"strategy_pool": ["primary"], "phase": 1, "capital_ramp_enabled": False}
# NO-BARE-SQL + TABLE-NAME-REGISTRY 配方: SQL 常量化+表名走 TableRegistry 真源
from zephyr.data.table_registry import get_registry as _get_table_registry

# category_id=meta_stock_basic（business_data_categories.yaml 真源），TableRegistry 解析全限定表名
_SQL_ALL_A = (
    "SELECT DISTINCT symbol FROM " + _get_table_registry().table("meta_stock_basic") +
    " WHERE valid_to IS NULL AND board NOT LIKE '%ST%'"
)
# v1 因子集（F-02 接线后扩展；全部从 close 现算，零额外依赖）
V1_FACTORS = ("f_mom20", "f_lowvol20", "f_ma_gap")


@dataclass(frozen=True)
class NegativeRecord:
    """阴性配方记录——死亡层+死因缺失即校验拒绝（机械可校验）。"""

    recipe_id: str
    death_layer: str            # eval / backtest / gate
    death_reason: str           # 结构化原因码（禁空串）
    values: dict[str, str]
    degraded_dimensions: str    # 逗号分隔降级维（空=无）
    detail: str = ""

    def __post_init__(self) -> None:
        if self.death_layer not in DEATH_LAYERS:
            raise ValueError(f"死亡层非法: {self.death_layer}（合法 {DEATH_LAYERS}）")
        if not self.death_reason.strip():
            raise ValueError(f"阴性记录死因缺失: {self.recipe_id}")


@dataclass
class GridEvalOutcome:
    """单 recipe 求值+回测结果（manifest 行）。"""

    recipe_id: str
    prefix_key: str
    values: dict[str, str]
    degraded_dimensions: tuple[str, ...]
    sharpe: float | None = None
    ann_return: float | None = None
    max_drawdown: float | None = None
    avg_turnover: float | None = None
    net_days: int = 0


def _load_engine():
    from _c4_engine import daily_net_returns, filter_st, load_px, load_st_flags, run_backtest, wide

    return load_px, wide, filter_st, load_st_flags, run_backtest, daily_net_returns


def _load_universe(universe: str) -> set[str]:
    """G_universe → {hs300, zz500, all_a_ex_st}（成分快照，index_constituent 真源）。"""
    from _c4_engine import load_index_constituents

    if universe == "hs300":
        return load_index_constituents("000300.SH")
    if universe == "zz500":
        return load_index_constituents("000905.SH")
    if universe == "all_a_ex_st":
        rows = _engine_query_all_a()
        return rows
    raise ValueError(f"G_universe 非法取值: {universe}")


def _engine_query_all_a() -> set[str]:
    from _c4_engine import run_query

    rows = run_query(_SQL_ALL_A)
    return {(r[0] or "")[:6] for r in rows if r[0]}


def compute_v1_factors(closes: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """v1 三因子（全从 close 现算）: 动量/低波/均线乖离。列=symbol, index=date。"""
    rets = closes.pct_change()
    ma20 = closes.rolling(20).mean()
    f_mom20 = closes.pct_change(20)
    f_lowvol20 = -rets.rolling(20).std()
    f_ma_gap = closes / ma20 - 1.0
    return {"f_mom20": f_mom20, "f_lowvol20": f_lowvol20, "f_ma_gap": f_ma_gap}


def _normalize(factor: pd.DataFrame, mode: str) -> tuple[pd.DataFrame, bool]:
    """A1 标准化。返回 (截面, degraded)。降级取值→zscore 并标记。"""
    if mode == "raw":
        return factor, False
    if mode == "rank":
        return factor.rank(axis=1, pct=True), False
    if mode == "zscore":
        mu = factor.mean(axis=1)
        sd = factor.std(axis=1)
        return factor.sub(mu, axis=0).div(sd.replace(0, np.nan), axis=0), False
    # industry_neutral / size_neutral / industsize_neutral: v1 降级（行业数据健康观察项+市值列未接）
    mu = factor.mean(axis=1)
    sd = factor.std(axis=1)
    return factor.sub(mu, axis=0).div(sd.replace(0, np.nan), axis=0), True


def _combine(factors: dict[str, pd.DataFrame], normalized: list[pd.DataFrame], mode: str,
             closes: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    """A2 合成。返回 (合成截面, degraded)。

    IC 类权重=60 日滚动 rank-IC（ic_mean 均值 / ic_ir 均值÷std / halflife 指数衰减均值），
    **shift(1) 前视防御：第 d 日合成只用截至 d-1 的 IC**（d 日因子预测 d→d+1 收益，
    权重若含 d 日 IC 即用了未来收益——bt-fin-correctness 前视铁律）。
    """
    names = list(factors.keys())
    dates = closes.index
    if mode == "equal":
        stack = pd.concat(normalized)
        return stack.groupby(level=0).mean(), False
    if mode in ("ic_mean", "ic_ir", "halflife20", "halflife60"):
        fwd = closes.pct_change().shift(-1)  # d→d+1 前向收益
        ic_by_name = []
        for nf in normalized:
            xr = nf.rank(axis=1)
            rr = fwd.rank(axis=1)
            m = xr.notna() & rr.notna()
            x = xr.where(m)
            y = rr.where(m)
            cov = (x.sub(x.mean(axis=1), axis=0) * y.sub(y.mean(axis=1), axis=0)).mean(axis=1)
            sd = (x.std(axis=1) * y.std(axis=1)).replace(0, np.nan)
            ic_by_name.append((cov / sd).fillna(0.0))
        ic_all = pd.concat(ic_by_name, axis=1, keys=names)  # index=date, columns=names
        if mode == "ic_mean":
            w = ic_all.rolling(60, min_periods=20).mean()
        elif mode == "ic_ir":
            w = ic_all.rolling(60, min_periods=20).mean() / (ic_all.rolling(60, min_periods=20).std() + 1e-12)
        else:
            span = 20 if mode == "halflife20" else 60
            w = ic_all.ewm(halflife=span, min_periods=10, adjust=False).mean()
        w = w.clip(lower=0.0).shift(1)  # ← 前视防御: d 日只用截至 d-1 的 IC
        w = w.div(w.sum(axis=1).replace(0, np.nan), axis=0)
        w = w.reindex(dates).fillna(1.0 / len(names))
        arr = np.zeros((len(dates), normalized[0].shape[1]))
        for j, nf in enumerate(normalized):
            arr += w[names[j]].to_numpy()[:, None] * nf.reindex(dates).fillna(0.0).to_numpy()
        combined = pd.DataFrame(arr, index=dates, columns=normalized[0].columns)
        return combined, False
    # orth_equal / lasso / pc1: v1 降级为等权（诚实标记，结构知识阶段剔除）
    stack = pd.concat(normalized)
    return stack.groupby(level=0).mean(), True


def _sizing(scores: pd.DataFrame, top_n: int, mode: str,
            vol20: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    """B 选股 + C 定尺寸。返回 (weights 截面, degraded)。"""
    rank = scores.rank(axis=1, ascending=False)
    mask = rank <= top_n
    base = mask.astype(float)
    base[base == 0] = np.nan
    if mode == "equal_weight":
        w = base
    elif mode == "inv_vol":
        iv = 1.0 / vol20.where(vol20 > 0)
        w = base * iv
    elif mode == "signal_strength":
        s = scores.where(mask)
        s = s - s.min(axis=1).min() + 1e-9
        w = base * s.abs()
    else:
        # mkt_cap / risk_parity / kelly_025 / kelly_050: v1 降级 inv_vol（诚实标记）
        iv = 1.0 / vol20.where(vol20 > 0)
        w = base * iv
        return _norm_rows(w, top_n), True
    return _norm_rows(w, top_n), False


def _norm_rows(w: pd.DataFrame, top_n: int) -> pd.DataFrame:
    row_sum = w.sum(axis=1).replace(0, np.nan)
    out = w.div(row_sum, axis=0).fillna(0.0)
    return out


def _apply_cap_and_lambda(w: pd.DataFrame, cap: str, lam: str) -> pd.DataFrame:
    """E 单票上限 + H 换手惩罚 λ（λ 收缩向旧权重）。"""
    cap_map = {"cap5": 0.05, "cap10": 0.10, "cap20": 0.20}
    lam_map = {"lambda_0": 0.0, "lambda_5bp": 0.0005, "lambda_15bp": 0.0015}
    c = cap_map[cap]
    # cap=硬约束终态 clip，不再 renorm（renorm 会重新突破上限）：
    # 持仓数不足（等权 1/n > cap）时允许低仓位——约束优先于满仓，超额留现金
    w = w.clip(upper=c)
    l = lam_map[lam] * 100.0  # λ 惩罚项放大为组合收缩系数（5bp/15bp→0.5/1.5 收缩比例）
    if l > 0:
        w = w.ewm(alpha=min(1.0, l), adjust=False).mean()
        rs = w.sum(axis=1).replace(0, np.nan)
        w = w.div(rs, axis=0).fillna(0.0)
    return w


def _apply_freq_trigger(w: pd.DataFrame, freq: str, trigger: str) -> pd.DataFrame:
    """D1 频率 + D2 触发: 非调仓日沿用旧权重；drift_band=偏离>10% 才重平衡。"""
    step = {"daily": 1, "weekly": 5, "biweekly": 10, "monthly": 21}[freq]
    dates = w.index
    keep = w.copy()
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
    out = pd.DataFrame(out_rows, index=dates, columns=w.columns)
    return out


def evaluate_recipe(recipe, closes: pd.DataFrame, factors: dict[str, pd.DataFrame],
                    vol20: pd.DataFrame, universe_cols: list[str]) -> tuple[pd.DataFrame, tuple[str, ...]]:
    """recipe → (weights 宽表, degraded 维元组)。求值失败抛 RuntimeError（fail-closed，调用方记阴性）。"""
    v = recipe.values
    degraded: list[str] = []
    cols = universe_cols
    cl = closes[cols]
    normalized: list[pd.DataFrame] = []
    names = list(factors.keys())
    for n in names:
        f = factors[n][cols]
        nf, deg = _normalize(f, v["A1_factor_normalize"])
        if deg:
            if "A1_factor_normalize" not in degraded:
                degraded.append("A1_factor_normalize")
        normalized.append(nf)
    combined, deg2 = _combine(factors, normalized, v["A2_combine_weight"], cl)
    if deg2:
        degraded.append("A2_combine_weight")
    top_n = int(v["B_top_n"].replace("top", ""))
    # E cap 约束的持仓数扩展（B×E 交互的实务语义）: 满仓+单票≤cap 要求
    # M=ceil(1/cap) 只——M>top_n 时有效持仓数扩展为 M（仍按分数序取）
    cap_val = {"cap5": 0.05, "cap10": 0.10, "cap20": 0.20}[v["E_single_cap"]]
    effective_n = max(top_n, -(-1 // cap_val) if (top_n * cap_val) < 1.0 else top_n)
    weights, deg3 = _sizing(combined, effective_n, v["C_sizing"], vol20[cols])
    if deg3:
        degraded.append("C_sizing")
    weights = _apply_freq_trigger(weights, v["D1_rebalance_freq"], v["D2_rebalance_trigger"])
    weights = _apply_cap_and_lambda(weights, v["E_single_cap"], v["H_turnover_lambda"])
    return weights, tuple(degraded)


def stratified_sample(expansion, n_samples: int, seed: int):
    """signal 侧（prefix_key）分层均匀抽样；n_samples>=N_raw 时全量直返。"""
    recipes = list(expansion.recipes)
    if n_samples >= len(recipes):
        return recipes
    rng = np.random.default_rng(seed)
    by_prefix: dict[str, list] = {}
    for r in recipes:
        by_prefix.setdefault(r.prefix_key, []).append(r)
    keys = sorted(by_prefix)
    picked: list = []
    if n_samples < len(keys):
        # 层数细于样本数: 随机抽层，每层 1 条（保证无重复且恰 n 条）
        layer_idx = rng.choice(len(keys), size=n_samples, replace=False)
        for i in layer_idx:
            pool = by_prefix[keys[i]]
            picked.append(pool[int(rng.integers(len(pool)))])
        return picked
    # 补齐余数（确定性: 全池洗牌后取前差值）
    if len(picked) < n_samples:
        chosen_ids = {r.recipe_id for r in picked}
        rest = [r for r in recipes if r.recipe_id not in chosen_ids]
        rest.sort(key=lambda r: r.recipe_id)
        rng.shuffle(rest)
        picked.extend(rest[: n_samples - len(picked)])
    return picked[:n_samples]


def run_batch(n_samples: int, seed: int, start: str, end: str, smoke: bool = False) -> dict:
    """批次 A 主入口。返回 summary dict；manifest/negatives 落 data/strategy_intake/grid_<ts>/。"""
    from zephyr.position.core.position_recipe_compiler import GridCompiler

    load_px, wide, filter_st, load_st_flags, run_backtest, daily_net_returns = _load_engine()
    compiler = GridCompiler.from_yaml(SCHEMA_PATH)
    expansion = compiler.compile(DEFAULT_CONTEXT)
    picked = stratified_sample(expansion, 8 if smoke else n_samples, seed)
    run_ts = time.strftime("%Y%m%d-%H%M%S")
    out_dir = INTAKE_DIR / f"grid_{run_ts}"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 数据一次拉取（窗口外多留 120 日算因子预热）
    import datetime as _dt

    warm_start = (pd.Timestamp(start) - pd.Timedelta(days=200)).date().isoformat()
    px = load_px(warm_start, end, fields=("close", "volume"))
    closes_all = wide(px, "close")
    closes = closes_all.loc[(closes_all.index >= pd.Timestamp(start)) & (closes_all.index <= pd.Timestamp(end))]
    flags = load_st_flags(start, end)
    closes_eval = filter_st(closes_all, flags).loc[closes.index]

    universe_cache: dict[str, set[str]] = {}
    factors_cache: dict[str, dict[str, pd.DataFrame]] = {}
    vol20 = closes_eval.pct_change().rolling(20).std()

    manifest_rows: list[GridEvalOutcome] = []
    negatives: list[NegativeRecord] = []
    eval_dead = bt_dead = 0
    for r in picked:
        g = r.values["G_universe"]
        if g not in universe_cache:
            try:
                universe_cache[g] = _load_universe(g)
            except Exception as exc:  # noqa: BLE001
                negatives.append(NegativeRecord(r.recipe_id, "eval", f"universe_load_fail:{type(exc).__name__}",
                                                r.values, "", str(exc)[:120]))
                eval_dead += 1
                continue
        cols = [c for c in universe_cache[g] if c in closes_eval.columns]
        if len(cols) < 30:
            negatives.append(NegativeRecord(r.recipe_id, "eval", "universe_too_small", r.values, "", f"cols={len(cols)}"))
            eval_dead += 1
            continue
        if g not in factors_cache:
            factors_cache[g] = compute_v1_factors(closes_eval[cols])
        try:
            weights, degraded = evaluate_recipe(r, closes_eval, factors_cache[g], vol20, cols)
        except Exception as exc:  # noqa: BLE001
            negatives.append(NegativeRecord(r.recipe_id, "eval", f"eval_fail:{type(exc).__name__}",
                                            r.values, "", str(exc)[:120]))
            eval_dead += 1
            continue
        try:
            stats = run_backtest(weights, closes_eval[cols])
            net = daily_net_returns(weights, closes_eval[cols])
            if len(net.dropna()) < 60 or float(net.std()) == 0:
                raise RuntimeError(f"insufficient_net:{len(net)}")
            sharpe = stats["sharpe"]
        except Exception as exc:  # noqa: BLE001
            negatives.append(NegativeRecord(r.recipe_id, "backtest", f"backtest_fail:{type(exc).__name__}",
                                            r.values, ",".join(degraded), str(exc)[:120]))
            bt_dead += 1
            continue
        manifest_rows.append(GridEvalOutcome(r.recipe_id, r.prefix_key, r.values, degraded,
                                         sharpe=sharpe, ann_return=stats["ann_return"],
                                         max_drawdown=stats["max_drawdown"],
                                         avg_turnover=stats["avg_turnover_1side"], net_days=len(net)))

    manifest = pd.DataFrame([asdict(o) | {"values_json": json.dumps(o.values, sort_keys=True)} for o in manifest_rows])
    manifest.drop(columns=["values"]).to_csv(out_dir / "manifest.csv", index=False)
    neg_df = pd.DataFrame([asdict(n) for n in negatives])
    neg_df.to_csv(out_dir / "negatives.csv", index=False)
    summary = {
        "run_ts": run_ts, "mode": "smoke" if smoke else "batch_a_census",
        "n_raw": expansion.n_raw, "n_sampled": len(picked),
        "evaluated": len(manifest_rows), "eval_dead": eval_dead, "backtest_dead": bt_dead,
        "degraded_recipes": int(manifest["degraded_dimensions"].apply(bool).sum()) if len(manifest) else 0,
        "window": [start, end], "seed": seed,
        "out_dir": str(out_dir),
        "n_eff_preregistered": None,  # 4.1: effective_rank（预注册记录见文档）
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(description="F-06 批次 A 普查执行器")
    ap.add_argument("--smoke", action="store_true", help="烟测：8 格点管线联通")
    ap.add_argument("--n-samples", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=20260915)
    ap.add_argument("--start", default="2020-01-01")
    ap.add_argument("--end", default="2023-12-31")
    args = ap.parse_args()
    s = run_batch(args.n_samples, args.seed, args.start, args.end, smoke=args.smoke)
    print(json.dumps(s, ensure_ascii=False, indent=2))
    return 0


# noqa: m11-perm-manual-legitimate  F-06 批处理跑批件: CLI 手动/计划任务触发与 c4_batch_screen 同类，
# 非常驻永久系统（无常驻状态/无自动循环），每次调用为一次有界批处理作业
if __name__ == "__main__":
    raise SystemExit(main())
