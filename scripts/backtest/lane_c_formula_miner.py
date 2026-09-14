# [BLUEPRINT] MOD-BT-155 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.lane_c_formula_miner
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; pandas; gplearn; zephyr.data.ch_config; zephyr.data.table_registry; scripts.backtest.compute_window_gate
# [CONSUMERS] 策略生产全景图 FAC-E1C 车道C-公式挖掘机（gplearn 轨 MVP）；FAC-E2 假说预审（下游）；
#   config/factor_mining_whitelist.yaml（算子约束真源）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 搜索空间受控（算子只从白名单 YAML 取，引擎缺算子=fail-closed）；
#   增量 IC fitness=候选因子对 REG-IND-001 基座残差的 rank IC（v1 混同池口径，CS-IC 是 v2）；
#   特征全用 ≤T 信息、y=前向 5 日收益（PIT）；随机种子固定可复算；出生证机器写入；
#   运动员不兼裁判——本车道输出的 ic 是描述性证据，判定权在 E2/E4；正式量产须白名单
#   status=active 且 E0 问闸放行（--smoke 工程烟测豁免只许小规模并在报告留痕）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(白名单/数据通道/算子集不可用); SystemExit(0)放行 SystemExit(3)闸拒
# [TESTS] tests/backtest/test_lane_c_formula_miner.py
# [A_module] module_id=MOD-BT-155 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  手动 CLI 挖掘器非常驻服务：由进货编排/夜批事件调用，无常驻循环
"""FAC-E1C 车道C-公式挖掘机 gplearn MVP（Owner 2026-09-14 四项裁定落地：双轨分期/
增量 IC 基座=REG-IND-001/种群 1000×50/白名单审定制）。

流程：E0 问闸（heavy 档）→ 白名单算子集（config/factor_mining_whitelist.yaml，fail-closed
交集）→ 面板数据（kline_daily_hfq 特征 ≤T + 前向 5 日收益 y + technical_indicator 日频
基座）→ gplearn 遗传规划（增量 IC fitness=对基座残差的 rank IC）→ 优等生公式带出生证
卸 data/strategy_intake/lane_c_candidates.csv → E2 预审消费。
AlphaGen 轨=立项另批（设计稿 docs/_working/2026-09-14-fac-e1c-formula-mining-design.md §二）。

用法:
  python scripts/backtest/lane_c_formula_miner.py mine --smoke --population 30 --generations 3 --universe-n 40
  python scripts/backtest/lane_c_formula_miner.py mine   # 正式档=白名单 1000x50（须审定+E0 放行）
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))  # scripts.* 命名空间导入（CLI 直跑场景）
_WHITELIST_YAML = _ROOT / "config" / "factor_mining_whitelist.yaml"
_INTAKE_CSV = _ROOT / "data" / "strategy_intake" / "lane_c_candidates.csv"

BIRTH_CHANNEL = "C"
BASELINE_TAG = "REG-IND-001"
FEATURES = ("ret_1d", "ret_5d", "ret_20d", "vol_20d", "turnover", "amt_z20", "close_ma20")
FWD_DAYS = 5
SMOKE_SCALE_NOTE = "工程烟测豁免（小规模、算力当量远低于正式档），闸拒时仅限本档使用"

SQL_UNIVERSE = (
    "SELECT symbol_canonical AS s, avg(amount) AS a FROM {kline} "
    "WHERE trade_date >= %(start)s GROUP BY 1 ORDER BY a DESC LIMIT %(n)s"
)
SQL_KLINE = (
    "SELECT trade_date, symbol_canonical AS s, close, turnover, amount FROM {kline} "
    "WHERE trade_date >= %(start)s AND symbol_canonical IN %(syms)s ORDER BY trade_date"
)
SQL_TI_DAILY = (
    "SELECT {cols} FROM {ti} WHERE period = 'daily' AND trade_date >= %(start)s "
    "AND symbol_canonical IN %(syms)s"
)
SQL_TI_COLS = (
    "SELECT name FROM system.columns WHERE database = 'c1_market' "
    "AND table = 'technical_indicator' AND default_kind != 'ALIAS'"
)
_TI_META = {"trade_date", "symbol_canonical", "period", "data_source", "ingest_ts",
            "exchange", "trade_time", "symbol", "updated_at"}


def _ti_columns(cli) -> list[str]:
    return [r[0] for r in cli.execute(SQL_TI_COLS)]


def load_whitelist(path: Path | None = None) -> dict:
    """白名单加载（唯一真源；缺失/解析失败 fail-closed）。"""
    import yaml

    p = path or _WHITELIST_YAML
    if not p.exists():
        raise RuntimeError(f"算子白名单不存在: {p}")
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(data.get("approved"), dict) or not data.get("constraints"):
        raise RuntimeError("白名单结构不合规（缺 approved/constraints）")
    return data


def build_function_set(whitelist: dict) -> list[str]:
    """白名单 approved → gplearn function_set（交集，双向 fail-closed）。"""
    from gplearn.functions import _function_map

    approved = [op for group in whitelist["approved"].values() for op in group]
    approved = [op["op"] if isinstance(op, dict) else op for op in approved]
    missing = [op for op in approved if op not in _function_map]
    if missing:
        raise RuntimeError(f"白名单算子引擎不支持（版本漂移）: {missing}")
    return sorted(approved)


def residualize(x: np.ndarray, baseline: np.ndarray) -> np.ndarray:
    """对基座矩阵+截距做最小二乘残差（增量信息的线性剥离，NaN 行一致剔除）。"""
    mask = np.isfinite(x)
    ok = mask & ~np.isnan(baseline).any(axis=1) if baseline.size else mask
    if ok.sum() < 10 or baseline.size == 0:
        return x.copy()
    design = np.column_stack([baseline[ok], np.ones(ok.sum())])
    coef, *_ = np.linalg.lstsq(design, x[ok], rcond=None)
    out = x.copy()
    out[ok] = x[ok] - design @ coef
    out[~ok] = np.nan
    return out


def rank_ic(a: np.ndarray, b: np.ndarray) -> float:
    """Spearman 秩相关（NaN 成对剔除；样本<10 记 0）。"""
    df = pd.DataFrame({"a": a, "b": b}).dropna()
    if len(df) < 10:
        return 0.0
    return float(df["a"].corr(df["b"], method="spearman"))


def make_incremental_ic_fitness(baseline: np.ndarray, fwd: np.ndarray):
    """gplearn 兼容 fitness（y, y_pred, w）：候选残差 vs 前向收益的 rank IC，越大越好。"""
    def _fitness(y, y_pred, _w):
        yp = np.asarray(y_pred, dtype=float)
        yp[~np.isfinite(yp)] = np.nan
        return rank_ic(residualize(yp, baseline), np.asarray(y, dtype=float))
    return _fitness


def build_hypothesis(expr: str, ic: float, n_samples: int) -> str:
    """确定性假说文本（公式+描述性证据；机制判断留给 E2，评分权留给 E4）。"""
    return (
        f"做多[公式因子]：{expr}——在 REG-IND-001 基座上增量 rank IC={ic:.4f}"
        f"（样本 {n_samples}，混同池口径 v1）。机制待审：该公式的每一项在行为/风险上"
        f"是什么意思？是否存在同义反复或换手陷阱？"
    )


def make_candidate_id(expr: str) -> str:
    return f"CAND-{hashlib.md5(f'E1C:{expr.strip()}'.encode('utf-8')).hexdigest()[:12]}"


def attach_birth_certificate(rows: list[dict], batch_id: str, cfg: dict) -> list[dict]:
    wl_sha = hashlib.md5(json.dumps(cfg["whitelist"], sort_keys=True, ensure_ascii=False,
                                    default=str).encode("utf-8")).hexdigest()[:12]
    out = []
    for r in rows:
        row = dict(r)
        row["birth_channel"] = BIRTH_CHANNEL
        row["birth_batch"] = batch_id
        row["birth_source"] = (f"gplearn pop={cfg['population_size']} gen={cfg['generations']} "
                               f"wl={wl_sha} baseline={BASELINE_TAG} seed={cfg['random_state']}")
        out.append(row)
    return out


def fetch_panel(universe_n: int, days: int) -> dict:
    """面板加载：universe=窗内成交额 top N；特征 ≤T；y=前向 5 日收益；基座=TI 日频。"""
    from zephyr.data.ch_writer import get_client_strict
    from zephyr.data.table_registry import get_registry

    cli = get_client_strict()
    start = (date.today() - timedelta(days=int(days * 1.7))).isoformat()
    syms = [r[0] for r in cli.execute(
        SQL_UNIVERSE.format(kline=get_registry().table("market_kline_daily_hfq")),
        {"start": start, "n": universe_n})]
    if len(syms) < 10:
        raise RuntimeError(f"universe 过小: {len(syms)}")
    k = pd.DataFrame(cli.execute(
        SQL_KLINE.format(kline=get_registry().table("market_kline_daily_hfq")),
        {"start": start, "syms": tuple(syms)}),
        columns=["date", "s", "close", "turnover", "amount"])
    for c in ("close", "turnover", "amount"):
        k[c] = pd.to_numeric(k[c], errors="coerce")  # CH Decimal → float
    k = k.sort_values(["s", "date"])
    g = k.groupby("s", group_keys=False)
    feats = pd.DataFrame({
        "ret_1d": g["close"].pct_change(),
        "ret_5d": g["close"].pct_change(5),
        "ret_20d": g["close"].pct_change(20),
        "vol_20d": g["close"].pct_change().rolling(20).std(),
        "turnover": np.log1p(k["turnover"].clip(lower=0)),
        "amt_z20": g["amount"].transform(lambda s: (s - s.rolling(20).mean()) / (s.rolling(20).std() + 1e-9)),
        "close_ma20": g["close"].transform(lambda s: s / (s.rolling(20).mean() + 1e-9) - 1),
    })
    feats["y_fwd5"] = g["close"].transform(lambda s: s.shift(-FWD_DAYS) / s - 1)
    feats["date"], feats["s"] = k["date"].values, k["s"].values
    feats = feats.dropna(subset=list(FEATURES) + ["y_fwd5"])

    ti_cols = _ti_columns(cli)
    ti = pd.DataFrame(cli.execute(
        SQL_TI_DAILY.format(ti=get_registry().table("market_technical_indicator"),
                            cols=", ".join(ti_cols)),
        {"start": start, "syms": tuple(syms)}), columns=ti_cols)
    ti = ti[ti["period"] == "daily"]
    base_cols = [c for c in ti.columns if c not in _TI_META]
    ti_num = ti[["trade_date", "symbol_canonical"] + base_cols].copy()
    ti_num = ti_num.rename(columns={"trade_date": "date", "symbol_canonical": "s"})
    for c in base_cols:
        ti_num[c] = pd.to_numeric(ti_num[c], errors="coerce")
    ti_num = ti_num.merge(feats[["date", "s"]], on=["date", "s"], how="inner")
    ti_num = ti_num.dropna(axis=1, thresh=int(len(ti_num) * 0.7))
    base_cols = [c for c in ti_num.columns if c not in ("date", "s")]
    ti_num = ti_num.sort_values(["s", "date"]).reset_index(drop=True)

    feats = feats.merge(ti_num[["date", "s"]].assign(_keep=True), on=["date", "s"], how="inner")
    X = feats[list(FEATURES)].to_numpy(dtype=float)
    y = feats["y_fwd5"].to_numpy(dtype=float)
    baseline = ti_num.loc[feats.index.values, base_cols].to_numpy(dtype=float)
    if len(X) < 500:
        raise RuntimeError(f"面板样本不足: {len(X)}")
    return {"X": X, "y": y, "baseline": baseline, "baseline_cols": base_cols,
            "n": len(X), "features": list(FEATURES), "universe": syms}


def render_expr(expr: str, features: list[str]) -> str:
    """gplearn 的 X0..Xn → 特征名（公式可读性；E2 预审要讲人话）。"""
    import re

    def _sub(m: re.Match) -> str:
        i = int(m.group(1))
        return features[i] if i < len(features) else m.group(0)
    return re.sub(r"X(\d+)", _sub, expr)


def run_mine(population_size: int, generations: int, universe_n: int, days: int,
             top_candidates: int, smoke: bool = False, dry_run: bool = False) -> dict:
    """主流程：问闸→白名单→面板→遗传挖掘→优等生卸货。"""
    from scripts.backtest.compute_window_gate import check_gate

    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    gate = check_gate("lane_c_gp_mine", "local_gpu", now)
    if not gate["allowed"] and not smoke:
        return {"gate": gate, "message": "E0 闸拒：重算力须收盘后/休市日（--smoke 仅限工程烟测档）"}

    whitelist = load_whitelist()
    status = whitelist.get("status")
    if status != "active" and not smoke:
        return {"gate": gate, "message": f"白名单 status={status}：正式量产须 Owner 审定后改 active"}
    func_set = build_function_set(whitelist)
    cons = whitelist["constraints"]

    panel = fetch_panel(universe_n, days)

    from gplearn.genetic import SymbolicTransformer

    # 搜索目标=gplearn 内置 spearman（Transformer 仅收内置 metric）；
    # 验收目标=自算增量 IC（对基座残差）——搜索与验收分离，终审判定权在 E2/E4。
    gp = SymbolicTransformer(
        function_set=func_set, metric="spearman",
        population_size=population_size, generations=generations,
        hall_of_fame=max(1, min(population_size, 50)),
        n_components=max(1, min(population_size, 10)),
        init_depth=tuple(cons["init_depth"]), parsimony_coefficient=cons["parsimony_coefficient"],
        random_state=cons["random_state"], n_jobs=cons["n_jobs"], verbose=0)
    gp.fit(panel["X"], panel["y"])

    fitness = make_incremental_ic_fitness(panel["baseline"], panel["y"])
    rows = []
    for prog in gp._programs[-1]:
        if prog is None or not np.isfinite(prog.fitness_):
            continue
        expr = render_expr(prog.__str__(), panel["features"])
        ic = fitness(panel["y"], prog.execute(panel["X"]), np.ones(panel["n"]))
        if ic <= 0:
            continue  # 验收目标=增量 IC>0 才入围
        rows.append({"formula": expr, "incr_ic": round(float(ic), 6),
                     "length": prog.length_,
                     "hypothesis_zh": build_hypothesis(expr, float(ic), panel["n"]),
                     "candidate_id": make_candidate_id(expr)})
    rows = sorted({r["candidate_id"]: r for r in rows}.values(),
                  key=lambda r: -r["incr_ic"])[:top_candidates]
    batch_id = now.strftime("E1C-%Y%m%d-%H%M%S")
    rows = attach_birth_certificate(rows, batch_id, {
        "whitelist": whitelist, "population_size": population_size,
        "generations": generations, "random_state": cons["random_state"]})

    record = {
        "batch": batch_id, "gate": gate, "smoke": smoke,
        "whitelist_status": status, "function_set": func_set,
        "panel": {"n": panel["n"], "universe_n": len(panel["universe"]),
                  "baseline_cols": len(panel["baseline_cols"])},
        "mined": len(rows),
        "items": [{k: r[k] for k in ("candidate_id", "incr_ic", "length", "formula")}
                  for r in rows],
    }
    if not dry_run and rows:
        cols = ["candidate_id", "formula", "incr_ic", "length", "hypothesis_zh",
                "birth_channel", "birth_batch", "birth_source"]
        header = not _INTAKE_CSV.exists()
        _INTAKE_CSV.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(rows)[cols].to_csv(_INTAKE_CSV, mode="a", header=header,
                                        index=False, encoding="utf-8-sig")
        record["written_to"] = str(_INTAKE_CSV.relative_to(_ROOT))
    return record


def main() -> int:
    ap = argparse.ArgumentParser(description="FAC-E1C 车道C-公式挖掘机（gplearn 轨，经 E0 问闸）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("mine", help="遗传挖掘一批公式因子")
    m.add_argument("--population", type=int, default=1000)
    m.add_argument("--generations", type=int, default=50)
    m.add_argument("--universe-n", type=int, default=100, help="成交额 top N 股")
    m.add_argument("--days", type=int, default=250, help="面板自然日窗")
    m.add_argument("--top", type=int, default=10, help="卸货优等生条数")
    m.add_argument("--smoke", action="store_true", help="工程烟测档（白名单未审定/闸拒时唯一豁免，小规模）")
    m.add_argument("--dry-run", action="store_true", help="只回看不写台账")
    args = ap.parse_args()
    try:
        record = run_mine(args.population, args.generations, args.universe_n,
                          args.days, args.top, args.smoke, args.dry_run)
    except RuntimeError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(record, ensure_ascii=False, indent=1, default=str))
    return 0 if record.get("gate", {}).get("allowed", True) else 3


if __name__ == "__main__":
    sys.exit(main())
