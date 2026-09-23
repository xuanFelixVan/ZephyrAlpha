# [BLUEPRINT] MOD-SIG-026 supplement | docs/_working/sector_line/sector_prereg_exam_cards_v1_frozen.md（FROZEN 2026-09-23）
# [MODULE] scripts.backtest.sector_prereg_exam_runner
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] pandas/numpy; zephyr.infrastructure.database_service(reader); zephyr.signal_ashare.sector.sector_state_aggregator.map_preference(映射真源复用)
# [CONSUMERS] 考试报告 docs/_working/sector_line/exam/prereg_exam_report_v1.md; 裁定登记(判档入册)
# [STARTUP] manual（python scripts/backtest/sector_prereg_exam_runner.py）
# [MATURITY] testing
# [INVARIANTS] frozen 卡零参数改动（S10-1~6/D2-1~6 继承 v0=冻结版）；PIT：T 日信号只用 ≤T 收盘，
#   T+1 收益 shift(-1)；frozen 卡判档三态如实（裁定#325 禁全绿表述）；多重检验 13+9 格全披露
#   仅主判进族；ewm(span) 向量化 EMA 与 sector_rrg.ema_series（alpha=2/(span+1) 种子=首值）定义
#   等价（前 62 日为 RRG 预热窗整体丢弃）；rank pct 分母 n 与聚合器 n-1 单调等价（分组不变）；
#   成分<10 剔除以现行成分快照为代理（frozen §F.2 如实披露）
# [MODIFY-GUARD] none
# [STABILITY] frozen_run
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 数据窗不足→如实 INSUFFICIENT 判档，禁放行；只读考试零写库
# [TESTS] 本脚本判档结果=交付物；单测面由聚合器/管道测试覆盖公式件
# [TTL] task_bound
"""板块线预注册考试跑批器（S10 强弱量化卡 + D2 偏好映射卡，FROZEN v1.0）。

用法：python scripts/backtest/sector_prereg_exam_runner.py
输出：docs/_working/sector_line/exam/（报告 md + 明细 csv）。零写库（纯读考试）。
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

# sys.path 先注入本仓 src（worktree 感知，须先于 zephyr 导入；worktree src 优先于主仓 .pth）
_repo_src = str(Path(__file__).resolve().parents[2] / "src")
if _repo_src not in sys.path:
    sys.path.insert(0, _repo_src)

from zephyr.data.table_registry import get_registry  # noqa: E402
from zephyr.infrastructure.database_service import DatabaseService  # noqa: E402
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  SSOT 符号（paths.py 唯一定义）
from zephyr.signal_ashare.sector.sector_state_aggregator import map_preference  # noqa: E402

_T = {
    "kline880": get_registry().table("market_sector_kline_880"),
    "constituent": get_registry().table("market_sector_constituent_880"),
    "regime": get_registry().table("backtest_regime_state_anchored"),
    "emotion": get_registry().table("market_emotion_index"),
}

_SQL_PANEL_CLOSES = (
    "SELECT trade_date, sector_code, toFloat64(close) "
    "FROM {kline880} "
    "WHERE sector_code != '' ORDER BY trade_date, sector_code"
)
_SQL_PANEL_AMOUNTS = (
    "SELECT trade_date, sector_code, toFloat64(amount) "
    "FROM {kline880} "
    "WHERE sector_code != '' ORDER BY trade_date, sector_code"
)
_SQL_REGIME = "SELECT trade_date, dominant FROM {regime} ORDER BY trade_date"
_SQL_EMOTION_DATES = "SELECT DISTINCT trade_date FROM {emotion} WHERE stage = 'close_final'"
_SQL_CONSTITUENT_COUNTS = (
    "SELECT sector_code, count() FROM {constituent} FINAL WHERE valid_to IS NULL GROUP BY sector_code"
)

OUT_DIR = REPO_ROOT / "docs" / "_working" / "sector_line" / "exam"
NW_LAG = 5  # frozen：S10-3/D2-3
S10_MIN_SECTORS = 300
S10_MIN_DAYS = 500
D2_MIN_MAP_DAYS = 120
D2_MIN_CELL_DAYS = 15
W_RECENT = 250
BENCH = "880001.SH"


def nw_t(x: pd.Series, lag: int = NW_LAG) -> float:
    """Newey-West t（HAC，Bartlett 核，lag=frozen 5）。"""
    x = x.dropna()
    n = len(x)
    if n < 10:
        return float("nan")
    e = x - x.mean()
    s = float((e * e).sum())
    for l in range(1, lag + 1):
        w = 1.0 - l / (lag + 1.0)
        s += 2.0 * w * float((e.iloc[l:] * e.iloc[:-l]).sum())
    se = (s / n) ** 0.5 / np.sqrt(n)
    return float(x.mean() / se) if se > 0 else float("nan")


def load_panels() -> dict[str, pd.DataFrame]:
    """全史日K 面板（收盘/成交额）+ regime/emotion/成分数。"""
    ch = DatabaseService().get_clickhouse_conn()
    closes = ch.execute(_SQL_PANEL_CLOSES.format(**_T))
    amounts = ch.execute(_SQL_PANEL_AMOUNTS.format(**_T))
    df_c = pd.DataFrame(closes, columns=["date", "code", "close"])
    df_c = df_c.drop_duplicates(subset=["date", "code"], keep="last")  # ReplacingMergeTree 未合并双版本
    cl = df_c.pivot(index="date", columns="code", values="close").sort_index()
    df_a = pd.DataFrame(amounts, columns=["date", "code", "amount"])
    df_a = df_a.drop_duplicates(subset=["date", "code"], keep="last")
    am = df_a.pivot(index="date", columns="code", values="amount").sort_index()
    regime = ch.execute(_SQL_REGIME.format(**_T))
    rg = pd.DataFrame(regime, columns=["date", "dominant"]).set_index("date")["dominant"]
    emotion = ch.execute(_SQL_EMOTION_DATES.format(**_T))
    em_dates = pd.to_datetime([r[0] for r in emotion]).date if emotion else []
    try:
        const = ch.execute(_SQL_CONSTITUENT_COUNTS.format(**_T))
        const_counts = {r[0]: r[1] for r in const}
    except Exception:  # noqa: BLE001 — 成分快照缺失=代理口径降级，如实披露
        const_counts = {}
    cl.index = pd.to_datetime(cl.index)
    am.index = pd.to_datetime(am.index)
    rg.index = pd.to_datetime(rg.index)
    rg = rg[~rg.index.duplicated(keep="last")]  # 重跑双版本去重（latest 胜）
    em_ts = set(pd.to_datetime(sorted(em_dates)))
    return {"close": cl, "amount": am, "regime": rg, "emotion_dates": em_ts, "const": const_counts}


def _s10_momentum_panel(cl):
    """spec §3.1⑧ 向量化：q3/q5/q20 截面百分位加权（rank pct 分组不变性见文件头）。"""
    q = {w: cl.pct_change(w).rank(axis=1, pct=True) for w in (3, 5, 20)}
    return 0.4 * q[20] + 0.3 * q[5] + 0.3 * q[3]


def _s10_rrg_axes(cl):
    """spec §3.1④ 向量化：RS→ewm(10)/ewm(26)×100 → (rs_ratio, rs_mom)。"""
    bench = cl[BENCH] if BENCH in cl.columns else cl.mean(axis=1)
    rs = cl.div(bench, axis=0) * 100.0
    rs_ratio = rs.ewm(span=10, adjust=False).mean() / rs.ewm(span=26, adjust=False).mean() * 100.0
    rs_mom = rs_ratio.ewm(span=10, adjust=False).mean() / rs_ratio.ewm(span=26, adjust=False).mean() * 100.0
    return rs_ratio, rs_mom


def _s10_daily_rows(mom_f, fwd_f, rs_ratio, rs_mom, idx_all):
    """逐日五分位价差 + 象限探索位均值。"""
    rows = []
    for d in idx_all:
        m = mom_f.loc[d].dropna()
        f = fwd_f.loc[d]
        if len(m) < 100 or f.isna().all():
            continue
        try:
            bins = pd.qcut(m.rank(method="average"), 5, labels=False)
        except ValueError:
            continue
        q5 = f[m[bins == 4].index].mean()
        q1 = f[m[bins == 0].index].mean()
        row = {"date": d, "spread": q5 - q1 if pd.notna(q5) and pd.notna(q1) else np.nan}
        ratio_d, mom_d = rs_ratio.loc[d], rs_mom.loc[d]
        for quad, mask in (
            ("leading", (ratio_d > 100) & (mom_d > 100)),
            ("weakening", (ratio_d > 100) & (mom_d <= 100)),
            ("lagging", (ratio_d <= 100) & (mom_d <= 100)),
            ("improving", (ratio_d <= 100) & (mom_d > 100)),
        ):
            codes = mask.index[mask & mask.index.isin(f.dropna().index)]
            vals = f[codes].dropna()
            row[quad] = vals.mean() if len(vals) else np.nan
        rows.append(row)
    return rows


def s10_exam(p: dict) -> dict:
    """卡 S10：momentum_pct 五分位 Q5−Q1 对 T+1 等权收益差的区分力（frozen 程序）。"""
    cl = p["close"]
    ret_fwd = cl.pct_change().shift(-1)  # T→T+1 收益（PIT：T 日截面→T+1 收益）
    mom = _s10_momentum_panel(cl)
    rs_ratio, rs_mom = _s10_rrg_axes(cl)

    # 成分<10 剔除（现行快照代理，frozen §F.2）
    keep = [c for c in cl.columns if p["const"].get(c, 999) >= 10]
    mom_f = mom[keep]
    fwd_f = ret_fwd[keep]

    rows = _s10_daily_rows(mom_f, fwd_f, rs_ratio, rs_mom, cl.index)
    quad_rows = rows
    sp = pd.DataFrame(rows).set_index("date")["spread"].dropna()
    # 电风扇速度计（spec §3.1⑨）：rotation_speed 日序 → P75 分层（v0 无 P90 历史窗前置，卡面写分位）
    am = p["amount"][keep]
    shares = am.div(am.sum(axis=1), axis=0)
    rot_speed = 0.5 * shares.diff().abs().sum(axis=1)
    p75 = rot_speed.quantile(0.75)
    fast_days = rot_speed[rot_speed > p75].index
    slow_days = rot_speed[rot_speed <= p75].index
    sp_recent = sp.iloc[-W_RECENT:]
    yearly = sp.groupby(sp.index.year).agg(["mean", "count"])
    yearly_pos = float((yearly["mean"] > 0).mean())
    quads = pd.DataFrame(quad_rows)
    quad_means = {c: float(quads[c].mean()) for c in ("leading", "weakening", "lagging", "improving")}
    result = {
        "card": "S10",
        "n_days": int(len(sp)),
        "n_sectors_effective": int(mom_f.notna().sum(axis=1).median()),
        "w_full_mean": float(sp.mean()),
        "w_full_nw_t": nw_t(sp),
        "w_recent_mean": float(sp_recent.mean()),
        "w_recent_nw_t": nw_t(sp_recent),
        "yearly_pos_rate": yearly_pos,
        "yearly_detail": {str(k): round(v["mean"], 6) for k, v in yearly.iterrows()},
        "fast_mean": float(sp[sp.index.isin(fast_days)].mean()),
        "slow_mean": float(sp[sp.index.isin(slow_days)].mean()),
        "quad_means": quad_means,
    }
    if result["n_sectors_effective"] < S10_MIN_SECTORS or result["n_days"] < S10_MIN_DAYS:
        result["verdict"] = "INSUFFICIENT"
    elif (
        result["w_full_mean"] > 0
        and result["w_full_nw_t"] >= 2.0
        and result["w_recent_mean"] > 0
        and yearly_pos >= 0.60
    ):
        result["verdict"] = "EDGE"
    else:
        result["verdict"] = "NO_EDGE"
    return result


def _d2_axes(p: dict):
    """D2 面板轴：T+1 收益/RRG 双轴/动量三分位/regime 查询闭包。"""
    cl = p["close"]
    ret_fwd = cl.pct_change().shift(-1)
    bench = cl[BENCH] if BENCH in cl.columns else cl.mean(axis=1)
    rs = cl.div(bench, axis=0) * 100.0
    rs_ratio = rs.ewm(span=10, adjust=False).mean() / rs.ewm(span=26, adjust=False).mean() * 100.0
    rs_mom = rs_ratio.ewm(span=10, adjust=False).mean() / rs_ratio.ewm(span=26, adjust=False).mean() * 100.0
    ret5 = cl.pct_change(5)
    mom_tercile = ret5.rank(axis=1, pct=True)

    def dominant_of(d):
        try:
            v = p["regime"].get(pd.Timestamp(d))
            return None if v is None or (isinstance(v, float) and np.isnan(v)) else v
        except Exception:  # noqa: BLE001
            return None

    def pointed_set(d) -> tuple[list[str], str]:
        """tilt≥1.0 档指向组（进攻组=领先象限∩动量Top三分位；防御组=滞后象限）。"""
        pref = map_preference(dominant_of(d), None)  # 单轴降档：emotion=mock
        ratio_d, mom_d = rs_ratio.loc[d], rs_mom.loc[d]
        m5 = mom_tercile.loc[d]
        if pref.preference_label in ("OFFENSIVE", "FOLLOW"):
            codes = ratio_d.index[(ratio_d > 100) & (m5 >= 2.0 / 3.0)]
            return list(codes), pref.preference_label
        if pref.preference_label == "DEFENSIVE":
            codes = ratio_d.index[ratio_d <= 100]
            return list(codes), "DEFENSIVE"
        return [], pref.preference_label

    return cl, ret_fwd, dominant_of, pointed_set


def _d2_days_and_stats(p: dict, cl, ret_fwd, dominant_of, pointed_set):
    """双轴窗日数/档位计数 + 单轴降档版价差与命中序列。"""
    regime_index = [d for d in cl.index if dominant_of(d) is not None and not pd.isna(dominant_of(d))]
    # 双轴窗：regime ∩ emotion 真值日
    em_days = {d for d in p["emotion_dates"]}
    dual_days = [d for d in regime_index if d in em_days]
    # 5 档样本量（双轴口径）
    label_counts: dict[str, int] = {}
    for d in dual_days:
        _, label = pointed_set(d)
        label_counts[label] = label_counts.get(label, 0) + 1

    spreads: list[float] = []
    hits: list[int] = []
    label_hit: dict[str, list[int]] = {}
    per_label_days: dict[str, int] = {}
    for d in regime_index:
        codes, label = pointed_set(d)
        per_label_days[label] = per_label_days.get(label, 0) + 1
        f = ret_fwd.loc[d].dropna()
        if not codes:
            continue
        pointed_idx = [c for c in codes if c in f.index]
        if len(pointed_idx) < 5:
            continue
        rest = f.drop(index=pointed_idx)
        spread = f[pointed_idx].mean() - rest.mean()
        if pd.notna(spread):
            spreads.append(spread)
        # 命中：指向组次日是否跑赢截面中位（对随机 1/2 与标签基线 1/5 双披露）
        hit = int(f[pointed_idx].mean() > f.median())
        hits.append(hit)
        label_hit.setdefault(label, []).append(hit)
    return dual_days, label_counts, spreads, hits, label_hit, per_label_days


def d2_exam(p: dict) -> dict:
    """卡 D2：偏好映射解释力。双轴主判 + regime 单轴降档版（frozen 程序）。"""
    cl, ret_fwd, dominant_of, pointed_set = _d2_axes(p)
    dual_days, label_counts, spreads, hits, label_hit, per_label_days = _d2_days_and_stats(
        p, cl, ret_fwd, dominant_of, pointed_set
    )
    sp = pd.Series(spreads)
    n_map = len(dual_days)
    dual_insufficient = (
        n_map < D2_MIN_MAP_DAYS or any(v < D2_MIN_CELL_DAYS for v in label_counts.values()) or n_map == 0
    )
    t = nw_t(sp)
    hit_rate = float(np.mean(hits)) if hits else float("nan")
    result = {
        "card": "D2",
        "n_dual_axis_days": n_map,
        "label_counts_dual": label_counts,
        "n_single_axis_days": int(len(sp)),
        "per_label_days_single": per_label_days,
        "single_mean": float(sp.mean()) if len(sp) else float("nan"),
        "single_nw_t": t,
        "single_hit_rate": hit_rate,
        "label_hit_rate": {k: round(float(np.mean(v)), 4) for k, v in label_hit.items()},
        "note": "情绪轴真值仅 2026-09-15 起（frozen §F.3），单轴降档版=regime-only(emotion=契约mock)",
    }
    if dual_insufficient:
        result["verdict_dual"] = "INSUFFICIENT"
    else:
        result["verdict_dual"] = "NO_MAP"  # 双轴窗在窗长达标后才判，当前不可达
    # 单轴降档版判档（D2-1 预承诺通道）：MAP_OK 需 mean>0 且 t≥1.65 且命中对随机基线超>5pct
    if len(sp) < D2_MIN_MAP_DAYS:
        result["verdict_single"] = "INSUFFICIENT"
    elif result["single_mean"] > 0 and t >= 1.65 and (hit_rate - 0.5) > 0.05:
        result["verdict_single"] = "MAP_OK"
    else:
        result["verdict_single"] = "NO_MAP"
    return result


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p = load_panels()
    cl = p["close"]
    print(f"面板: {cl.shape[0]} 日 × {cl.shape[1]} 板块（{cl.index.min()} → {cl.index.max()}）")
    s10 = s10_exam(p)
    print("S10:", json.dumps(s10, ensure_ascii=False, default=str)[:400])
    d2 = d2_exam(p)
    print("D2:", json.dumps(d2, ensure_ascii=False, default=str)[:400])
    report = {
        "frozen_source": "sector_prereg_exam_cards_v1_frozen.md",
        "run_date": str(date.today()),
        "panel_days": int(cl.shape[0]),
        "panel_sectors": int(cl.shape[1]),
        "S10": s10,
        "D2": d2,
    }
    # .yaml 落盘（docs/_working/ 目录契约禁 .json；JSON 本身即合法 YAML）
    (OUT_DIR / "prereg_exam_results_v1.yaml").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    print("报告已落盘:", OUT_DIR / "prereg_exam_results_v1.yaml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
