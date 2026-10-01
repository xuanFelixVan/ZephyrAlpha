# [BLUEPRINT] SH-SCRIPT-001 | docs/_working/decision_map_campaign_20260924/links/L05_t0/T0_MATERIAL_EXAM_CARD_draft.md §8 下游消费 + SKEL.md §5 D2/D3 块
# [MODULE] t0_state_match_matrix（T0 全量×状态匹配引擎：L05-C04 执行件）
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] t0_rule_engine 产物 manifest+pairs parquet（显式路径清单消费禁 glob）；.worktrees/st-t0-matrix-20260924/docs/_working/t0_matrix/six_phase_history_v1.csv（六段相位真源 B4，只读）；c1_market.industry_class（板块族 L1 静态快照，非 PIT 观察轴如实披露）；c1_market.stock_daily_basic（T-1 circ_mv 市值五分位）；src/zephyr/signal_ashare/strategy_signal/pattern_win_rate_provider._wilson_lower_bound（Wilson LB 复用禁重写）
# [CONSUMERS] links/L05_t0/t0_state_match_*.csv（P1 四元组矩阵，排序只认 Wilson LB，04 号文 §15）；L05 后续闭卷考卡（WFE 双轨预注册于 meta）
# [STARTUP] manual（python scripts/backtest/t0_state_match_matrix.py --manifest ... --tag v1）
# [MATURITY] draft
# [INVARIANTS] 四元组行规范=n/raw/Wilson LB/区间宽（禁改判据）；n<30 格=insufficient_no_merge 禁并格（V3 卡 §8.4 纪律）；报告披露各相位样本数（17 §三.5）；闭卷切点 2025-09-09 硬拦（对集越切点=SystemExit）；新闻十分位轴=v1 阻断（研究窗 per-symbol 新闻标注=0 行实测，evidence 入 meta，禁标题模糊匹配造料）；相位只认 B4 真源 routed 行，未路由日=unrouted 如实单列；ignition 极稀格如实 INSUFFICIENT；排序只认 Wilson LB 胜率仅观察列；产物=csv+yaml 禁 summary.json；查库只读
# [MODIFY-GUARD] 状态轴定义（相位真源/五分位口径/T-1 对齐）改动=口径变更须改卡重开；禁为格数好看并格放宽
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] manifest 缺失/对集文件缺失/零对=显式报错非静默空产物；越闭卷切点=SystemExit；产物写失败=非零退出码
# [TESTS] tests/backtest/test_t0_state_match_matrix.py（四元组数学 vs 手算/无并格/闭卷硬拦/相位 unrouted 落格/市值 T-1 对齐）
# [TTL] task_bound
"""t0_state_match_matrix.py — T0 全量×状态匹配引擎（L05-C04）。

判据口径（引用不重写）：
- 格子四元组（04 号文 §15 / 17 号文 §三.2）：n、raw 胜率（net_bp>0 占比，仅观察列）、
  Wilson 95% 置信下界、区间宽；**排序只认 Wilson LB**。
- 状态轴：六段相位（B4 真源 six_phase_history_v1.csv，routed 行法定，未路由日=unrouted）
  × 周期 {1,5,15,30,60}min × 板块族（SW L1 静态快照，非 PIT 观察轴如实披露）
  × 市值五分位（stock_daily_basic T-1 circ_mv 日截面分位，PIT 对齐）。
- 新闻活跃度十分位（17 §三.3）：**v1 阻断**——研究窗 2021-09-01→2025-09-09 内
  news_data 2,841,834 条中 related_symbols 非空=0 条（实测 2026-09-26），
  per-symbol 活跃度不可构造；发布时点审计（8.3/D3 ⑥ 在册项）未过前禁标题模糊匹配造料。
- 样本外判据（后续闭卷考卡适用，预注册引用）：WFE=OOS/IS≥50%（Pardo）+ Wilson LB 衰减
  ≤30% 双轨并行（17 §三.2，零改动）；本件只产出研究段（IS 侧）观察矩阵，闭卷段零触碰。

用法：
  python scripts/backtest/t0_state_match_matrix.py \
    --manifest data/backtest_artifacts/t0_rule_engine/t0_rule_manifest_<tag>.yaml \
    --out-dir docs/_working/decision_map_campaign_20260924/links/L05_t0 --tag v1
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "audit"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cost_trio_exam as ct  # 判据常量与土规真源（import 复用禁重写）

from zephyr.signal_ashare.strategy_signal.pattern_win_rate_provider import _wilson_lower_bound as wilson_lb

_REPO_ROOT = Path(__file__).resolve().parents[2]
SIX_PHASE_CSV = _REPO_ROOT / ".worktrees/st-t0-matrix-20260924/docs/_working/t0_matrix/six_phase_history_v1.csv"
CLOSED_BOOK_CUTOFF = "2025-09-09"
NEWS_AXIS_BLOCK = "blocked_no_pit_symbol_news"
PHASES_ORDER = ["ignition", "expansion", "euphoria", "distribution", "capitulation", "accumulation", "unrouted"]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_pairs_from_manifest(manifest_path: Path, rules: list[str], periods: list[int]) -> pd.DataFrame:
    """按 manifest 显式路径清单汇总对集（禁 glob；文件缺失=显式报错）。"""
    man = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    out_dir = manifest_path.parent
    frames = []
    for rule in rules:
        files = man.get("pairs_files", {}).get(rule)
        if not files:
            raise SystemExit(f"FAIL: manifest 无规则 {rule} 的对集清单（{manifest_path}）")
        for rel in files:
            p = out_dir / rel
            if not p.exists():
                raise SystemExit(f"FAIL: 对集文件缺失 {p}")
            import re

            m = re.search(r"_(\d+)min\.parquet$", rel)
            if not m:
                raise SystemExit(f"FAIL: 对集文件名无周期段 {rel}（期望 *_<rule>_<P>min.parquet）")
            period = int(m.group(1))
            if period not in periods:
                continue
            df = pd.read_parquet(p)
            df["rule"] = rule
            df["period"] = period
            frames.append(df)
    if not frames:
        raise SystemExit("FAIL: 对集为空——禁静默空产物")
    pairs = pd.concat(frames, ignore_index=True)
    pairs["trade_date"] = pairs["trade_date"].astype(str)
    if pairs["trade_date"].max() > CLOSED_BOOK_CUTOFF:
        raise SystemExit(
            f"FAIL: 对集含闭卷数据（max={pairs['trade_date'].max()} > {CLOSED_BOOK_CUTOFF}）——禁闭卷入研究"
        )
    return pairs


def load_phase_map(csv_path: Path, start: str) -> tuple[dict[str, str], dict]:
    """B4 六段真源 → 研究窗 trade_date→phase 映射（只认 routed 行；未路由=unrouted）。"""
    if not csv_path.exists():
        raise SystemExit(f"FAIL: 六段真源缺失 {csv_path}")
    ph = pd.read_csv(csv_path, dtype={"trade_date": str})
    ph = ph[(ph["trade_date"] >= start) & (ph["trade_date"] <= CLOSED_BOOK_CUTOFF)]
    routed = ph[(ph["routed"] == 1) & ph["six_phase"].notna() & (ph["six_phase"] != "")]
    phase_map = dict(zip(routed["trade_date"], routed["six_phase"].astype(str), strict=False))  # B905 落地整改
    meta = {
        "path": str(csv_path),
        "sha256": sha256_file(csv_path),
        "rows_in_window": int(len(ph)),
        "routed_days_in_window": int(len(routed)),
        "phase_day_counts": {k: int(v) for k, v in routed["six_phase"].value_counts().items()},
    }
    return phase_map, meta


# 表名真源=TableRegistry（#ARCH-CH-024 Phase 5 落地整改：禁硬编码 c1_market.* 字面量）
from zephyr.data.table_registry import get_registry

_TBL_INDUSTRY_CLASS = get_registry().table("market_industry_class")
_TBL_STOCK_DAILY_BASIC = get_registry().table("market_stock_daily_basic")

# NO-BARE-SQL 落地整改：函数内裸 SQL 提升为 _SQL_* 模块常量（原内联于 load_sector_family/load_mcap_quintile）
_SQL_SECTOR_FAMILY = f"""
SELECT symbol, argMax(industry_sw, updated_at) AS ind
FROM {_TBL_INDUSTRY_CLASS} FINAL
WHERE industry_level = 1 AND valid_to IS NULL AND industry_sw != 'nan'
GROUP BY symbol
"""

_SQL_MCAP_QUINTILE = f"""
SELECT symbol, trade_date, circ_mv
FROM {_TBL_STOCK_DAILY_BASIC} FINAL
WHERE trade_date >= toDate('{{start}}') AND trade_date <= toDate('{{cutoff}}')
  AND isNotNull(circ_mv)
ORDER BY symbol, trade_date
"""


def load_sector_family(conn) -> tuple[dict[str, str], str]:
    """SW L1 板块族静态映射（industry_class 最新未失效快照；非 PIT 观察轴，如实披露）。"""
    rows = conn.execute(_SQL_SECTOR_FAMILY)
    m = {str(s): str(i) for s, i in rows}
    return (
        m,
        f"{_TBL_INDUSTRY_CLASS} L1 latest valid_to-IS-NULL snapshot（静态非 PIT 观察轴，SKEL §4 C-F6 前视缺口如实登记）",
    )


def load_mcap_quintile(conn, start: str) -> pd.DataFrame:
    """市值五分位（T-1 circ_mv 日截面分位，1=最小市值组）：返回 (symbol, trade_date, mcap_q)。"""
    rows = conn.execute(_SQL_MCAP_QUINTILE.format(start=start, cutoff=CLOSED_BOOK_CUTOFF))
    dv = pd.DataFrame(rows, columns=["symbol", "trade_date", "circ_mv"])
    if dv.empty:
        raise SystemExit("FAIL: stock_daily_basic 研究窗零行——市值轴不可构建，禁造料")
    dv["trade_date"] = dv["trade_date"].astype(str)
    dv["prev_circ_mv"] = dv.groupby("symbol", sort=False)["circ_mv"].shift(1)  # T-1 对齐（PIT）
    dv = dv.dropna(subset=["prev_circ_mv"]).copy()
    dv["mcap_q"] = (dv.groupby("trade_date", sort=False)["prev_circ_mv"].rank(method="first", pct=True) * 5.0).apply(
        lambda x: f"q{min(int(np.ceil(x)), 5)}"
    )
    return dv[["symbol", "trade_date", "mcap_q"]]


def attach_axes(
    pairs: pd.DataFrame,
    phase_map: dict[str, str],
    sector_map: dict[str, str],
    mcap_q: pd.DataFrame,
) -> pd.DataFrame:
    df = pairs.copy()
    df["phase"] = df["trade_date"].map(phase_map).fillna("unrouted")
    df["sector_family"] = df["symbol"].astype(str).map(sector_map).fillna("unknown")
    df = df.merge(mcap_q, on=["symbol", "trade_date"], how="left")
    df["mcap_q"] = df["mcap_q"].fillna("missing")
    df["news_axis"] = NEWS_AXIS_BLOCK
    return df


def cell_stats(g: pd.DataFrame) -> dict:
    """格子四元组+观察列（四元组=n/raw/Wilson LB/区间宽；期望/前置命中为观察披露列）。"""
    n = int(len(g))
    wins = int((g["net_bp"] > 0).sum())
    raw = wins / n if n else 0.0
    lb = float(wilson_lb(raw, n)) if n else 0.0
    # Wilson 上界（与 _wilson_lower_bound 同 z=95% 口径的镜像公式，测试钉住对称性）
    z = 1.959963984540054
    denom = 1.0 + z * z / n
    centre = raw + z * z / (2.0 * n)
    margin = z * ((raw * (1.0 - raw) + z * z / (4.0 * n)) / n) ** 0.5
    ub = min(1.0, (centre + margin) / denom) if n else 0.0
    return {
        "n": n,
        "win_rate_raw": round(raw, 6),
        "wilson_lb": round(lb, 6),
        "wilson_ub": round(ub, 6),
        "interval_width": round(ub - lb, 6),
        "net_mean_bp": round(float(g["net_bp"].mean()), 4) if n else 0.0,
        "gross_mean_bp": round(float(g["gross_bp"].mean()), 4) if n else 0.0,
        "edge_ge_30bp_share": round(float((g["gross_bp"] >= ct.EDGE_PRECONDITION_BP).mean()), 6) if n else 0.0,
        "verdict": "ok" if n >= ct.PAIR_GATE else "insufficient_no_merge",
    }


def build_matrix(df: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    rows = []
    for k, g in df.groupby(keys, sort=True):
        if not isinstance(k, tuple):
            k = (k,)
        rows.append(
            dict(zip(keys, k, strict=False)),  # B905 落地整改
        )
        rows[-1].update(cell_stats(g))
    return pd.DataFrame(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description="T0 全量×状态匹配引擎（四元组矩阵，n<30 禁并格）")
    ap.add_argument("--manifest", required=True, help="t0_rule_engine 产物 manifest yaml（显式路径清单）")
    ap.add_argument("--rule", default="", help="逗号分隔，缺省=manifest 全部规则")
    ap.add_argument("--period", default="1,5,15,30,60")
    ap.add_argument("--six-phase-csv", default=str(SIX_PHASE_CSV))
    ap.add_argument("--start", default="2021-09-01")
    ap.add_argument("--out-dir", default="docs/_working/decision_map_campaign_20260924/links/L05_t0")
    ap.add_argument("--tag", default="v1")
    args = ap.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        raise SystemExit(f"FAIL: manifest 缺失 {manifest_path}")
    man = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    rules = [r.strip() for r in args.rule.split(",") if r.strip()] or list(man["rules"])
    periods = [int(p) for p in str(args.period).split(",")]

    pairs = load_pairs_from_manifest(manifest_path, rules, periods)
    phase_map, phase_meta = load_phase_map(Path(args.six_phase_csv), args.start)

    from zephyr.infrastructure.database_service import DatabaseService

    conn = DatabaseService().get_clickhouse_conn()
    sector_map, sector_source = load_sector_family(conn)
    mcap_q = load_mcap_quintile(conn, args.start)
    df = attach_axes(pairs, phase_map, sector_map, mcap_q)

    keys_full = ["rule", "period", "phase", "sector_family", "mcap_q", "news_axis"]
    keys_pp = ["rule", "period", "phase"]
    matrix = build_matrix(df, keys_full)
    phase_period = build_matrix(df, keys_pp)

    # 相位样本数披露（17 §三.5）：路由日数+逐周期对数
    cov_rows = []
    for ph_name, n_days in sorted(phase_meta["phase_day_counts"].items()):
        row = {"phase": ph_name, "routed_days": n_days}
        for period in periods:
            sub = df[(df["phase"] == ph_name) & (df["period"] == period)]
            row[f"n_pairs_{period}min"] = int(len(sub))
        unrouted_n = int((df["phase"] == "unrouted").sum()) if ph_name == PHASES_ORDER[-1] else None
        if unrouted_n is not None:
            row["note"] = "unrouted=非路由日单列披露，禁并入任何相位"
        cov_rows.append(row)
    unrouted_days = phase_meta["rows_in_window"] - phase_meta["routed_days_in_window"]
    unr_total = df["phase"] == "unrouted"
    cov_rows.append(
        {
            "phase": "unrouted",
            "routed_days": 0,
            "unrouted_days_in_window": unrouted_days,
            **{f"n_pairs_{p}min": int((unr_total & (df["period"] == p)).sum()) for p in periods},
            "note": "unrouted=非路由日单列披露，禁并入任何相位",
        }
    )
    coverage = pd.DataFrame(cov_rows)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    matrix_path = out_dir / f"t0_state_match_matrix_{args.tag}.csv"
    pp_path = out_dir / f"t0_state_match_phase_period_{args.tag}.csv"
    cov_path = out_dir / f"t0_state_match_phase_coverage_{args.tag}.csv"
    matrix.to_csv(matrix_path, index=False, encoding="utf-8-sig")
    phase_period.to_csv(pp_path, index=False, encoding="utf-8-sig")
    coverage.to_csv(cov_path, index=False, encoding="utf-8-sig")

    meta = {
        "tag": args.tag,
        "caliber": {
            "quadruple": "n / win_rate_raw(观察列) / wilson_lb(95%) / interval_width；排序只认 Wilson LB（04 号文 §15）",
            "win_definition": "net_bp > 0（net=gross−31.2bp，CST-T0-001 固定口径）",
            "cell_gate": f"n≥{ct.PAIR_GATE} 才 ok，n<{ct.PAIR_GATE}=insufficient_no_merge，禁并格（V3 卡 §8.4 纪律）",
            "phase_axis": "B4 六段真源 routed 行法定；unrouted 单列；ignition 等极稀格如实 INSUFFICIENT",
            "sector_axis": sector_source,
            "mcap_axis": "stock_daily_basic T-1 circ_mv 日截面五分位（q1=最小市值；PIT 对齐）",
            "news_axis": {
                "status": NEWS_AXIS_BLOCK,
                "evidence": "news_data 研究窗 2021-09-01→2025-09-09 共 2,841,834 条，related_symbols 非空=0 条（CH 实测 2026-09-26）；发布时点审计未过（8.3/D3 ⑥ 在册），禁标题模糊匹配造料",
            },
            "closed_book": f"对集 max(trade_date)={df['trade_date'].max()} ≤ 切点 {CLOSED_BOOK_CUTOFF}；闭卷考=WFE=OOS/IS≥50% + Wilson LB 衰减≤30% 双轨（17 §三.2 零改动引用，另卡执行）",
        },
        "inputs": {
            "manifest": {
                "path": str(manifest_path),
                "sha256": sha256_file(manifest_path),
                "rules": rules,
                "periods": periods,
            },
            "six_phase": phase_meta,
            "n_pairs_total": int(len(df)),
        },
        "outputs": {"matrix": str(matrix_path), "phase_period": str(pp_path), "coverage": str(cov_path)},
        "recompute": f"python scripts/backtest/t0_state_match_matrix.py --manifest {manifest_path} --out-dir {out_dir} --tag {args.tag}",
    }
    (out_dir / f"t0_state_match_meta_{args.tag}.yaml").write_text(
        yaml.safe_dump(meta, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    print(f"pairs={len(df)} cells={len(matrix)} phase_period_cells={len(phase_period)}")
    print(f"matrix -> {matrix_path}")
    print(yaml.safe_dump(phase_meta["phase_day_counts"], allow_unicode=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
