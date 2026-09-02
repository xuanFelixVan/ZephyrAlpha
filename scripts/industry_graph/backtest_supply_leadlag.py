# [MODULE] scripts.industry_graph.backtest_supply_leadlag
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema; zephyr.data.ch_writer; zephyr.simulation.look_ahead_bias_detector
# [CONSUMERS] 因子框架(候选注册); 前端供应链 ego 网络
# [STARTUP] manual
# [MATURITY] research
# [INVARIANTS] 披露滞后: 年报边 year=Y 仅自 Y+1-05-01 起可用(防前视); 复权价 close*adj_factor; 月度调仓; 结果可复现(无随机)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 行情覆盖不足->退出码2; 自检不通过->打印告警仍输出结果但标记
# [TTL] permanent
"""供应链 lead-lag 传导因子验证回测（Cohen-Frazzini 客户动量，A股适配）。

假设：客户（下游）股价信息领先传导到供应商（上游）——客户过去 20 日收益
对供应商下月收益有正向预测力。

设计：
  边样本    ig_company_edge 对手方为上市公司的全部三源边（483 权重边优先）
  披露滞后  边 year=Y → 交易可用窗口 [Y+1-05-01, Y+2-04-30]（年报 4 月底前披露）
  信号      供应商 f 在调仓日 d：其全部活跃客户的过去 20 交易日收益加权均值
            （483 边按销售额占比加权，其余等权）
  组合      每月首个交易日调仓，信号分五档，做多 Q5 做空 Q1（等权，不计成本）
  指标      Spearman IC / ICIR、多空价差序列、分年表现
  自检      LookAheadBiasDetector.scan 扫描信号面板（项目回测前置强制项）

用法::

    python scripts/industry_graph/backtest_supply_leadlag.py [--freq monthly|weekly]
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from zephyr.data import ch_writer
from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
from zephyr.simulation.look_ahead_bias_detector import LookAheadBiasDetector

LOOKBACK_SESSIONS = 20
REBAL_START = date(2013, 5, 1)
REBAL_END = date(2025, 11, 1)
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", ".runtime", "industry_graph")


def load_edges() -> pd.DataFrame:
    conn = get_depgraph_pg_connection(read_only=True, autocommit=True)
    df = pd.read_sql(
        """
        SELECT from_symbol, to_symbol, year,
               max(CASE WHEN source='483_top5_customer' THEN weight END) AS sales_pct,
               count(DISTINCT source) AS n_sources
        FROM ig_company_edge
        WHERE to_symbol <> ''
        GROUP BY 1,2,3
        """,
        conn,
    )
    conn.close()
    return df


def ch_query_df(sql: str, columns: list[str]) -> pd.DataFrame:
    """ch_writer.query 返回无表头 TSV，列名由调用方提供。"""
    tsv = ch_writer.query(sql)
    if not tsv.strip():
        return pd.DataFrame(columns=columns)
    from io import StringIO

    return pd.read_csv(StringIO(tsv), sep="\t", header=None, names=columns)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--freq", choices=["monthly", "weekly"], default="monthly")
    args = ap.parse_args()
    lookback = LOOKBACK_SESSIONS if args.freq == "monthly" else 5
    os.makedirs(OUT_DIR, exist_ok=True)

    # ---- 1. 交易日历与调仓日 ----
    cal = ch_query_df(
        "SELECT DISTINCT trade_date FROM c1_market.kline_daily "
        "WHERE market_type='A_share' AND trade_date BETWEEN '2012-01-01' AND '2026-08-01' ORDER BY trade_date",
        ["trade_date"],
    )
    if cal.empty:
        print("[ERROR] 交易日历为空")
        return 2
    cal["trade_date"] = pd.to_datetime(cal["trade_date"]).dt.date
    sessions = sorted(cal["trade_date"].tolist())
    sidx = {d: i for i, d in enumerate(sessions)}
    if args.freq == "monthly":
        month_first: dict[date, date] = {}
        for d in sessions:  # 升序遍历，setdefault 保留每月首个交易日
            month_first.setdefault(date(d.year, d.month, 1), d)
        rebal = [d for _, d in sorted(month_first.items()) if REBAL_START <= d <= REBAL_END]
    else:
        week_first: dict[tuple[int, int], date] = {}
        for d in sessions:  # 保留每周首个交易日
            iso = d.isocalendar()
            week_first.setdefault((iso[0], iso[1]), d)
        rebal = [d for _, d in sorted(week_first.items()) if REBAL_START <= d <= REBAL_END]
    print(f"[BT] 调仓日 {len(rebal)} 个 ({rebal[0]} ~ {rebal[-1]}), freq={args.freq}, lookback={lookback}")

    # ---- 2. 边与信号所需价格点 ----
    edges = load_edges()
    print(f"[BT] 边 {len(edges)} 条, 涉及供应商 {edges.from_symbol.nunique()} / 客户 {edges.to_symbol.nunique()}")
    syms = sorted(set(edges.from_symbol) | set(edges.to_symbol))

    need_dates = set()
    for d in rebal:
        i = sidx[d]
        need_dates.add(d)
        if i >= lookback:
            need_dates.add(sessions[i - lookback])  # 回看点
        if i + 1 < len(sessions):
            nxt = [rd for rd in rebal if rd > d]
            if nxt:
                need_dates.add(nxt[0])  # 次期调仓日（前向收益终点）
    date_list = "','".join(str(d) for d in sorted(need_dates))

    # 分批拉价（符号多，按 500 个一批）
    frames = []
    for i in range(0, len(syms), 500):
        batch = "','".join(syms[i : i + 500])
        df = ch_query_df(
            "SELECT symbol_canonical AS symbol, trade_date, close * if(adj_factor IS NULL, 1, adj_factor) AS adj_close "
            "FROM c1_market.kline_daily "
            f"WHERE symbol_canonical IN ('{batch}') AND trade_date IN ('{date_list}') "
            "AND market_type='A_share' AND quality_flag=1",
            ["symbol", "trade_date", "adj_close"],
        )
        frames.append(df)
    px = pd.concat(frames, ignore_index=True)
    if px.empty:
        print("[ERROR] 价格数据为空")
        return 2
    px["trade_date"] = pd.to_datetime(px["trade_date"]).dt.date
    px["adj_close"] = px["adj_close"].astype(float)
    price = px.pivot_table(index="trade_date", columns="symbol", values="adj_close")
    print(f"[BT] 价格面板 {price.shape[0]} 日 × {price.shape[1]} 股")

    # ---- 3. 信号与前向收益 ----
    adj = price
    trail = adj / adj.shift(lookback) - 1.0  # 过去 N 期收益
    records = []
    for d in rebal:
        i = sidx[d]
        nxt = [rd for rd in rebal if rd > d]
        if not nxt or i < lookback:
            continue
        f_d = nxt[0]
        if d not in adj.index or f_d not in adj.index:
            continue
        fwd = adj.loc[f_d] / adj.loc[d] - 1.0  # 次月收益
        t20 = trail.loc[d]
        # 活跃边：year+1-05-01 <= d <= year+2-04-30
        act = edges[
            (edges.year.map(lambda y: date(y + 1, 5, 1)) <= d) & (edges.year.map(lambda y: date(y + 2, 4, 30)) >= d)
        ]
        for f, grp in act.groupby("from_symbol"):
            cust = grp.to_symbol.tolist()
            w = grp.sales_pct.fillna(1.0).clip(lower=0).tolist()
            r = t20.reindex(cust)
            mask = r.notna()
            if not mask.any() or pd.isna(fwd.get(f)):
                continue
            wv = np.array(w)[mask.to_numpy()]
            sig = float(np.average(r[mask], weights=wv)) if wv.sum() > 0 else float(r[mask].mean())
            records.append(
                {"date": d, "symbol": f, "signal": sig, "fwd_ret": float(fwd[f]), "n_customers": int(mask.sum())}
            )

    panel = pd.DataFrame(records)
    if panel.empty:
        print("[ERROR] 信号面板为空（边窗口与价格覆盖不匹配）")
        return 2
    print(f"[BT] 信号面板 {len(panel)} 条 ({panel.date.min()} ~ {panel.date.max()})")

    # ---- 4. 前视偏差自检（项目强制项）----
    scan_df = panel.rename(columns={"signal": "trail20_customer"}).copy()
    scan_df["ts"] = pd.to_datetime(scan_df["date"])
    scan_df = scan_df.sort_values("ts").reset_index(drop=True)
    detector = LookAheadBiasDetector()
    scan_res = detector.scan(
        scan_df,
        feature_columns=["trail20_customer", "n_customers"],
        label_column="fwd_ret",
        timestamp_column="ts",
    )
    print(f"[BT] 前视自检: is_clean={scan_res.is_clean} issues={scan_res.total_issues}")
    for f_ in scan_res.issues[:5]:
        print("   ", repr(f_), getattr(f_, "__dict__", ""))

    # ---- 5. IC 与分档组合 ----
    ic_by_date = panel.groupby("date").apply(
        lambda g: g.signal.corr(g.fwd_ret, method="spearman") if len(g) >= 10 else np.nan
    )
    periods_per_year = 12 if args.freq == "monthly" else 52
    ic_mean, ic_std = ic_by_date.mean(), ic_by_date.std()
    icir = ic_mean / ic_std * np.sqrt(periods_per_year) if ic_std and not np.isnan(ic_std) else np.nan

    def quintile_spread(g: pd.DataFrame) -> float:
        if len(g) < 25:
            return np.nan
        q = pd.qcut(g.signal, 5, labels=False, duplicates="drop")
        top, bot = g.fwd_ret[q == q.max()], g.fwd_ret[q == q.min()]
        if len(top) == 0 or len(bot) == 0:
            return np.nan
        return top.mean() - bot.mean()

    spread = panel.groupby("date").apply(quintile_spread).dropna()
    ann_spread = (1 + spread).prod() ** (periods_per_year / max(len(spread), 1)) - 1 if len(spread) else np.nan
    hit = (spread > 0).mean()

    print("\n===== 回测结果 =====")
    print(f"IC 均值={ic_mean:.4f}  ICIR(年化)={icir:.2f}  IC>0 占比={(ic_by_date > 0).mean():.1%}")
    print(f"多空期均价差={spread.mean():.2%}  年化={ann_spread:.2%}  期胜率={hit:.1%}  ({len(spread)} 期)")
    yearly = spread.groupby(spread.index.map(lambda d: d.year)).agg(["mean", "count"])
    print("\n分年（期均多空价差）:")
    for y, row in yearly.iterrows():
        print(f"  {y}: {row['mean']:+.2%} ({int(row['count'])} 期)")

    panel.to_csv(os.path.join(OUT_DIR, f"leadlag_signal_panel_{args.freq}.csv"), index=False)
    spread.to_csv(os.path.join(OUT_DIR, f"leadlag_spread_series_{args.freq}.csv"))
    print(f"\n[BT] 面板与价差序列已存 {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
