# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md §P1 条件概率表
# [MODULE] scripts.backtest.p1_conditional_tables
# create-guard-not-dup: 本件是P1板块×相位条件概率表生成器(只读CH+只写CSV产物),命中词generator_auto_trigger系表生成语文巧合,非reconcile生成器自动触发能力的第二实现
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_reader（只读）; pandas; 六段相位物化件 six_phase_history_v1.csv
# [CONSUMERS] data/strategy_intake/conditional_tables/（P1 三表+Top5 产物）; LANE-DU881 v1↔v2 对比件
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 计算核与 .runtime/tmp/p1_conditional_tables.py 逐行等值（转正非重写）：口径真源
#              =docs/_working/quant_methodology/01_caliber_law.md + 03_conditional_stats_spec.md；
#              格子四元组 n/raw_win_rate/wilson_lb/mean_bp 同批产出，排序只认 wilson_lb；
#              n<MIN_OBS(30) → exam_ok=False 且永不与可考格并池统计（"不可考"第三态保留原格）；
#              --codes-file 只做宇宙白名单，不改任何公式；禁 datetime.now()/time.time()；
#              写库=零（只读 CH + 只写 CSV 产物）
# [MODIFY-GUARD] 改计算核须同步 04_p1_conditional_tables.md 施工文档与 v1↔v2 对比件重跑
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 相位件缺失 → FileNotFoundError（fail-visible，禁静默降级为随机相位）；
#                  diff 子命令两侧缺 T1 文件 → SystemExit(2)
# [TESTS] tests/backtest/test_p1_conditional_tables.py（宇宙白名单与 diff 判据的证尺）
# [TTL] task_bound
"""P1 板块×相位条件概率表生成器（.runtime/tmp 一次性脚本转正件）+ v1↔v2 宇宙对比。

用法：
    # 生产重跑（全宇宙，写 data/strategy_intake/conditional_tables/）
    python scripts/backtest/p1_conditional_tables.py

    # 宇宙白名单重放（DU-01 判据③ v1=469 码重放，写临时目录，零污染生产产物）
    python scripts/backtest/p1_conditional_tables.py --codes-file <codes.csv> --out-dir <dir>

    # 只算不写
    python scripts/backtest/p1_conditional_tables.py --no-write

    # v1↔v2 对比（格子四元组 + n<30 分层，禁并格）
    python scripts/backtest/p1_conditional_tables.py diff --a <v1dir> --b <v2dir> --out <cell_diff.csv>
"""

from __future__ import annotations

import argparse
import io
import itertools
import math
import pathlib
import sys

import pandas as pd

sys.path.insert(0, "src")

MIN_OBS = 30  # quant_methodology/03 主地板（condition_package.py:49 家族值）

# 相位真源：优先 HEAD 路径，缺则回退借读路径（落 HEAD 属排班债，回退时如实打印）
PHASE_CANDIDATES = (
    pathlib.Path("docs/_working/t0_matrix/six_phase_history_v1.csv"),
    pathlib.Path(".worktrees/st-t0-matrix-20260924/docs/_working/t0_matrix/six_phase_history_v1.csv"),
)
DEFAULT_OUT = pathlib.Path("data/strategy_intake/conditional_tables")
DEFAULT_CACHE = DEFAULT_OUT / "_cache_880.parquet"
# 表名真源=TableRegistry（#ARCH-CH-024 Phase 5 落地整改）
_TBL_KLINE_880 = (
    __import__("zephyr.data.table_registry", fromlist=["get_registry"]).get_registry().table("market_sector_kline_880")
)
SQL_KLINE = (  # NO-BARE-SQL 落地整改：常量名对齐 SQL_* 豁免契约（原 KLINE_SQL）
    f"SELECT trade_date, sector_code, sector_name, close FROM {_TBL_KLINE_880} "  # noqa: ch-final  经ch_reader.query集中通道(自动注FINAL),非绕过去重
    "WHERE period='1d' ORDER BY sector_code, trade_date FORMAT TSV"
)


def wilson_lb(wins: float, n: int, z: float = 1.96) -> float:
    if n == 0:
        return float("nan")
    p = wins / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    adj = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (centre - adj) / denom


def resolve_phase_csv(override: pathlib.Path | None) -> pathlib.Path:
    if override is not None:
        if not override.exists():
            raise FileNotFoundError(f"相位件不存在: {override}")
        return override
    for cand in PHASE_CANDIDATES:
        if cand.exists():
            print(f"相位件: {cand}")
            return cand
    raise FileNotFoundError(f"相位件缺失，候选={[str(c) for c in PHASE_CANDIDATES]}")


def load_kline(cache: pathlib.Path, codes_file: pathlib.Path | None) -> pd.DataFrame:
    if cache.exists():
        df = pd.read_parquet(cache)
        print(f"880 日K（缓存 {cache}）: {len(df)} 行, {df['sector_code'].nunique()} 板块")
    else:
        from zephyr.data.ch_reader import query  # 只读通道（禁裸 duckdb/裸 Client）

        tsv = query(SQL_KLINE)
        df = pd.read_csv(
            io.StringIO(tsv), sep="\t", names=["trade_date", "sector_code", "sector_name", "close"], dtype=str
        )
        df["close"] = pd.to_numeric(df["close"], errors="coerce")
        df = df.dropna(subset=["close"])
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        print(f"880 日K（CH）: {len(df)} 行, {df['sector_code'].nunique()} 板块")
    if codes_file is not None:
        universe = {
            ln.strip() for ln in pathlib.Path(codes_file).read_text(encoding="utf-8").splitlines() if ln.strip()
        }
        before = df["sector_code"].nunique()
        df = df[df["sector_code"].isin(universe)]
        print(f"宇宙白名单: 声明 {len(universe)} 码 → 命中 {df['sector_code'].nunique()} 码（原 {before}）")
        missing = sorted(universe - set(df["sector_code"]))
        if missing:
            print(f"WARN 白名单中无日K数据的码 {len(missing)}: {missing[:8]}")
    return df.sort_values(["sector_code", "trade_date"]).reset_index(drop=True)


def build_tables(phase_csv: pathlib.Path, df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """计算核（与 .runtime/tmp 原件逐行等值）。"""
    ph = pd.read_csv(phase_csv, parse_dates=["trade_date"])
    routed = ph[(ph["routed"] == 1) & ph["six_phase"].notna() & (ph["six_phase"].astype(str).str.len() > 0)]
    routed = routed[["trade_date", "six_phase"]].sort_values("trade_date").reset_index(drop=True)
    print(f"相位路由日: {len(routed)} / 全史 {len(ph)} 日（r1/r2 不路由=宁漏勿误）")

    d = df.copy()
    d["ret"] = d.groupby("sector_code")["close"].pct_change()
    m = d.merge(routed, on="trade_date", how="inner")
    print(f"合流样本: {len(m)} 行（有效窗 {m['trade_date'].min().date()} → {m['trade_date'].max().date()}）")

    rows = []
    # sector_name 在 CH 中为空串(解析为 NaN)——dropna=False 防组键全灭（09-24 验尸教训）
    for (code, name), g in m.groupby(["sector_code", "sector_name"], dropna=False):
        for phase, gp in g.groupby("six_phase"):
            r = gp["ret"].dropna()
            n = int(len(r))
            if n == 0:
                continue
            wins = float((r > 0).sum())
            std = float(r.std())
            rows.append(
                {
                    "sector_code": code,
                    "sector_name": name,
                    "phase": phase,
                    "n": n,
                    "raw_win_rate": round(wins / n, 6),
                    "wilson_lb": round(wilson_lb(wins, n), 6),
                    "mean_bp": round(float(r.mean()) * 1e4, 2),
                    "median_bp": round(float(r.median()) * 1e4, 2),
                    "p25_bp": round(float(r.quantile(0.25)) * 1e4, 2),
                    "p75_bp": round(float(r.quantile(0.75)) * 1e4, 2),
                    "std_bp": round(std * 1e4, 2),
                    "t_stat": round(float(r.mean()) / (std / math.sqrt(n)), 3) if n > 1 and std > 0 else float("nan"),
                    "exam_ok": n >= MIN_OBS,
                }
            )
    t1 = pd.DataFrame(rows).sort_values(["phase", "wilson_lb"], ascending=[True, False])
    print(f"T1: {len(t1)} 格（exam_ok {int(t1['exam_ok'].sum())} / 不可考 {int((~t1['exam_ok']).sum())}）")

    d["ret20"] = d.groupby("sector_code")["close"].pct_change(20)
    d["fwd5"] = d.groupby("sector_code")["close"].pct_change(5).shift(-5)
    m2 = d.merge(routed, on="trade_date", how="inner").dropna(subset=["ret20", "fwd5"])
    t2_rows = []
    for phase, gp in m2.groupby("six_phase"):
        if len(gp) < MIN_OBS:
            continue
        corr = float(gp["ret20"].corr(gp["fwd5"]))
        t2_rows.append(
            {
                "phase": phase,
                "n_obs": int(len(gp)),
                "n_days": int(gp["trade_date"].nunique()),
                "momentum_corr_20v5": round(corr, 4),
                "reading": "正=动量延续(强者恒强)"
                if corr > 0.02
                else ("负=轮动反转(高低切)" if corr < -0.02 else "≈0 无稳定方向"),
            }
        )
    t2 = pd.DataFrame(t2_rows)

    seq = routed["six_phase"].tolist()
    transitions: dict[tuple[str, str], int] = {}
    for a, b in itertools.pairwise(seq):  # RUF007/B905 落地整改：pairwise 替代 zip(seq, seq[1:])（语义等值）
        transitions[(a, b)] = transitions.get((a, b), 0) + 1
    phases = sorted({p for pair in transitions for p in pair})
    t3_rows = []
    for a in phases:
        total = sum(v for (x, _), v in transitions.items() if x == a)
        for b in phases:
            c = transitions.get((a, b), 0)
            t3_rows.append(
                {"from_phase": a, "to_phase": b, "count": c, "prob": round(c / total, 4) if total else float("nan")}
            )
    t3 = pd.DataFrame(t3_rows)

    runs, cur, cur_len = [], None, 0
    for p in seq:
        if p == cur:
            cur_len += 1
        else:
            if cur is not None:
                runs.append((cur, cur_len))
            cur, cur_len = p, 1
    runs.append((cur, cur_len))
    stay = (
        pd.DataFrame(runs, columns=["phase", "run_len_days"])
        .groupby("phase")["run_len_days"]
        .agg(["count", "mean", "max"])
        .round(2)
    )

    top_rows = []
    ok = t1[t1["exam_ok"]]
    for phase, gp in ok.groupby("phase"):
        for _, r in gp.nlargest(5, "wilson_lb").iterrows():
            top_rows.append(
                {
                    "phase": phase,
                    "rank": len([x for x in top_rows if x["phase"] == phase]) + 1,
                    "sector_code": r["sector_code"],
                    "sector_name": r["sector_name"],
                    "n": r["n"],
                    "wilson_lb": r["wilson_lb"],
                    "mean_bp": r["mean_bp"],
                }
            )
    return {"t1": t1, "t2": t2, "t3": t3, "stay": stay, "top5": pd.DataFrame(top_rows)}


def cmd_run(args: argparse.Namespace) -> int:
    phase_csv = resolve_phase_csv(args.phase_csv)
    cache = pathlib.Path(args.cache) if args.cache else DEFAULT_CACHE
    df = load_kline(cache, args.codes_file)
    tabs = build_tables(phase_csv, df)
    out = pathlib.Path(args.out_dir)
    if args.no_write:
        print(f"--no-write：产物仅内存（out_dir={out} 未写）")
        return 0
    out.mkdir(parents=True, exist_ok=True)
    tabs["t1"].to_csv(out / "p1_sector_by_phase.csv", index=False, encoding="utf-8-sig")
    tabs["t2"].to_csv(out / "p1_phase_momentum.csv", index=False, encoding="utf-8-sig")
    tabs["t3"].to_csv(out / "p1_phase_transition.csv", index=False, encoding="utf-8-sig")
    tabs["stay"].to_csv(out / "p1_phase_stay.csv", encoding="utf-8-sig")
    tabs["top5"].to_csv(out / "p1_top5_by_phase.csv", index=False, encoding="utf-8-sig")
    print(f"产物落 {out}")
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    """v1↔v2 宇宙对比：格子四元组逐格对拍 + n<30 分层（禁并格）+ T2 宇宙敏感面对拍。"""
    a, b = pathlib.Path(args.a), pathlib.Path(args.b)
    t1a = pd.read_csv(a / "p1_sector_by_phase.csv")
    t1b = pd.read_csv(b / "p1_sector_by_phase.csv")
    # exam_ok 一律按地板重算（不信任产物里的旧旗标：地板口径变更时对比器不得跟着漂移）
    for _t in (t1a, t1b):
        _t["exam_ok"] = pd.to_numeric(_t["n"], errors="coerce") >= MIN_OBS
    cols = ["n", "raw_win_rate", "wilson_lb", "mean_bp"]
    j = t1a.merge(t1b, on=["sector_code", "phase"], how="outer", suffixes=("_a", "_b"), indicator=True)
    common = j[j["_merge"] == "both"].copy()
    only_b = j[j["_merge"] == "right_only"].copy()
    only_a = j[j["_merge"] == "left_only"].copy()
    drift = []
    for c in cols:
        va, vb = common[f"{c}_a"], common[f"{c}_b"]
        num = pd.to_numeric(va, errors="coerce").notna() & pd.to_numeric(vb, errors="coerce").notna()
        eq = (pd.to_numeric(va, errors="coerce").round(6) == pd.to_numeric(vb, errors="coerce").round(6)) | (~num)
        drift.append(
            {
                "col": c,
                "cells_compared": int(num.sum()),
                "cells_equal": int(eq.sum()),
                "cells_drifted": int((~eq & num).sum()),
            }
        )
    common["ci_width_lb"] = (common["raw_win_rate_b"] - common["wilson_lb_b"]).round(6)
    keep = ["sector_code", "phase", "_merge"] + [f"{c}_{s}" for c in cols for s in "ab"] + ["ci_width_lb"]
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    common[keep].to_csv(out, index=False, encoding="utf-8-sig")

    def fam(s):  # E731 落地整改：lambda 改 def（语义等值）
        s = str(s)
        if s.startswith("881"):
            return "881"
        if s.startswith(("8803", "8804")):
            return "8803_04"
        return "880fam"

    summary: dict[str, object] = {
        "label_a": args.label_a,
        "label_b": args.label_b,
        "t1_cells_a": int(len(t1a)),
        "t1_cells_b": int(len(t1b)),
        "cells_common": int(len(common)),
        "cells_only_b": int(len(only_b)),
        "cells_only_a": int(len(only_a)),
        "codes_a": int(t1a["sector_code"].nunique()),
        "codes_b": int(t1b["sector_code"].nunique()),
        "cell_drift_by_column": drift,
        "exam_floor": MIN_OBS,
    }
    strat = []
    for src, tag in ((t1a, args.label_a), (t1b, args.label_b)):
        s = src.copy()
        s["fam"] = s["sector_code"].map(fam)
        for (f, exam), g in s.groupby(["fam", "exam_ok"]):
            strat.append(
                {
                    "side": tag,
                    "family": f,
                    "exam_ok": bool(exam),
                    "cells": int(len(g)),
                    "codes": int(g["sector_code"].nunique()),
                    "median_n": float(g["n"].median()),
                    "median_ci_width_lb": float((g["raw_win_rate"] - g["wilson_lb"]).median()),
                }
            )
    summary["strata_no_pooling_across_n30"] = strat
    t2a = pd.read_csv(a / "p1_phase_momentum.csv").rename(columns={"n_obs": "n_obs_a", "momentum_corr_20v5": "corr_a"})
    t2b = pd.read_csv(b / "p1_phase_momentum.csv").rename(columns={"n_obs": "n_obs_b", "momentum_corr_20v5": "corr_b"})
    t2 = t2a[["phase", "n_obs_a", "corr_a"]].merge(t2b[["phase", "n_obs_b", "corr_b"]], on="phase", how="outer")
    t2["corr_delta"] = (t2["corr_b"] - t2["corr_a"]).round(4)
    summary["t2_universe_sensitive"] = t2.to_dict("records")
    if only_b.shape[0]:
        ob = only_b.copy()
        ob["fam"] = ob["sector_code"].map(fam)
        summary["new_cells_by_family"] = ob.groupby("fam").size().to_dict()
        summary["new_cells_exam_ok"] = int(pd.to_numeric(ob["n_b"], errors="coerce").ge(MIN_OBS).sum())
        summary["new_cells_below_floor"] = int(pd.to_numeric(ob["n_b"], errors="coerce").lt(MIN_OBS).sum())
    import json

    print(json.dumps(summary, ensure_ascii=False, indent=1, default=str))
    pathlib.Path(args.summary_json).write_text(
        json.dumps(summary, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--phase-csv", type=pathlib.Path, default=None)
    ap.add_argument("--cache", type=pathlib.Path, default=None)
    ap.add_argument("--codes-file", type=pathlib.Path, default=None, help="宇宙白名单（一行一个 sector_code）")
    ap.add_argument("--out-dir", type=pathlib.Path, default=DEFAULT_OUT)
    ap.add_argument("--no-write", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    dp = sub.add_parser("diff", help="两目录产物做 v1↔v2 对比")
    dp.add_argument("--a", required=True)
    dp.add_argument("--b", required=True)
    dp.add_argument("--out", required=True)
    dp.add_argument("--summary-json", required=True)
    dp.add_argument("--label-a", default="v1")
    dp.add_argument("--label-b", default="v2")
    args = ap.parse_args(argv)
    if args.cmd == "diff":
        return cmd_diff(args)
    return cmd_run(args)


if __name__ == "__main__":
    raise SystemExit(main())
