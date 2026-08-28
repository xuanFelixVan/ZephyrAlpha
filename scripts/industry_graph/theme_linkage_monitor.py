# [MODULE] scripts.industry_graph.theme_linkage_monitor
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema; zephyr.data.ch_writer
# [CONSUMERS] 前端图谱页联动监控表; 主题联动告警
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只用 confidence>=0.85 互证映射; 行情取 kline_daily 最新交易日; 联动强度=近20日平均成对相关性
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无映射/无行情->退出码2
# [TTL] permanent
"""主题联动监控：0.85 互证映射子集 × 最新行情 → 产业链联动日报。

每条链输出：覆盖公司数、当日涨家占比、平均/中位涨跌幅、领涨股、
近 20 日平均成对相关性（联动强度）。按"当日强度"排序写 CSV，
前端图谱页读取展示；QMT 盘中接入后可切换为盘中实时版。

用法::

    python scripts/industry_graph/theme_linkage_monitor.py
"""

from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from zephyr.data import ch_writer
from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

OUT_CSV = os.path.join(
    os.path.dirname(__file__), "..", "..", ".runtime", "industry_graph", "theme_linkage_daily.csv"
)
_LOOKBACK_DAYS = 20
_MAX_SYMS_PER_CHAIN = 30


def ch_query_df(sql: str, columns: list[str]) -> pd.DataFrame:
    tsv = ch_writer.query(sql)
    if not tsv.strip():
        return pd.DataFrame(columns=columns)
    from io import StringIO

    return pd.read_csv(StringIO(tsv), sep="\t", header=None, names=columns)


def load_mappings() -> pd.DataFrame:
    conn = get_depgraph_pg_connection(read_only=True, autocommit=True)
    df = pd.read_sql(
        """
        SELECT c.name AS chain, nc.symbol
        FROM ig_node_company nc
        JOIN ig_node n ON n.node_id = nc.node_id
        JOIN ig_chain c ON c.chain_id = n.chain_id
        WHERE nc.confidence >= 0.85
        """,
        conn,
    )
    conn.close()
    return df.drop_duplicates()


def main() -> int:
    maps = load_mappings()
    if maps.empty:
        print("[ERROR] 无 0.85 互证映射")
        return 2
    chain_sizes = maps.groupby("chain").symbol.nunique()
    chains = chain_sizes[chain_sizes >= 3].index.tolist()
    maps = maps[maps.chain.isin(chains)]
    syms = sorted(maps.symbol.unique())
    print(f"[LINK] 链 {len(chains)} 条, 覆盖公司 {len(syms)} 家")

    latest = ch_query_df(
        "SELECT max(trade_date) FROM c1_market.kline_daily WHERE market_type='A_share'", ["d"]
    )["d"].iloc[0]
    print(f"[LINK] 最新交易日: {latest}")

    frames = []
    for i in range(0, len(syms), 500):
        batch = "','".join(syms[i : i + 500])
        df = ch_query_df(
            "SELECT symbol_canonical AS symbol, trade_date, "
            "close * if(adj_factor IS NULL, 1, adj_factor) AS adj_close, pct_change "
            "FROM c1_market.kline_daily "
            f"WHERE symbol_canonical IN ('{batch}') AND market_type='A_share' AND quality_flag=1 "
            f"AND trade_date BETWEEN addDays(toDate('{latest}'), -45) AND toDate('{latest}')",
            ["symbol", "trade_date", "adj_close", "pct_change"],
        )
        frames.append(df)
    px = pd.concat(frames, ignore_index=True)
    px = px.drop_duplicates(subset=["symbol", "trade_date"], keep="last")
    px["trade_date"] = pd.to_datetime(px["trade_date"])
    px["adj_close"] = px["adj_close"].astype(float)
    px["pct_change"] = px["pct_change"].astype(float)
    print(f"[LINK] 价格数据 {px.shape[0]} 行, 覆盖 {px.symbol.nunique()} 股, 日期 {px.trade_date.min().date()}~{px.trade_date.max().date()}")

    # 最新日可能处于入库中途（覆盖不足），取覆盖>=80%峰值的最近完整交易日
    coverage = px.groupby("trade_date").symbol.nunique()
    full_date = coverage[coverage >= 0.8 * coverage.max()].index.max()
    if full_date < px.trade_date.max():
        print(f"[LINK] 最新日 {px.trade_date.max().date()} 覆盖不足，回退完整交易日 {full_date.date()}")
    today = px[px.trade_date == full_date].set_index("symbol")["pct_change"]
    price = px.pivot_table(index="trade_date", columns="symbol", values="adj_close").tail(_LOOKBACK_DAYS + 1)
    rets = price.pct_change().dropna(how="all")

    rows = []
    for chain, grp in maps.groupby("chain"):
        s = [x for x in grp.symbol.unique() if x in rets.columns][: _MAX_SYMS_PER_CHAIN]
        if len(s) < 3:
            continue
        day = today.reindex(s).dropna()
        sub = rets[s].dropna(axis=1, how="any")
        if sub.shape[1] >= 3 and len(sub) >= 10:
            cm = sub.corr().to_numpy()
            iu = np.triu_indices(sub.shape[1], k=1)
            corr = float(np.nanmean(cm[iu]))
        else:
            corr = np.nan
        if day.empty:
            continue
        top_sym = day.idxmax()
        rows.append({
            "chain": chain,
            "n_companies": len(s),
            "up_ratio": float((day > 0).mean()),
            "mean_pct": float(day.mean()),
            "median_pct": float(day.median()),
            "top_symbol": top_sym,
            "top_pct": float(day.max()),
            "corr20": corr,
            "trade_date": str(full_date.date()),
        })
    out = pd.DataFrame(rows)
    if out.empty:
        print("[ERROR] 无有效链统计（映射与行情无交集）")
        return 2
    out = out.sort_values("mean_pct", ascending=False)
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    out.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    print(f"\n===== 联动 TOP10（{full_date.date()}）=====")
    for _, r in out.head(10).iterrows():
        print(f"  {r.chain}: 涨占比 {r.up_ratio:.0%} 均涨 {r.mean_pct:+.2f}% 联动 {r.corr20:.2f} 领涨 {r.top_symbol} {r.top_pct:+.2f}%")
    print(f"\n===== 联动 BOT5 =====")
    for _, r in out.tail(5).iterrows():
        print(f"  {r.chain}: 涨占比 {r.up_ratio:.0%} 均涨 {r.mean_pct:+.2f}% 联动 {r.corr20:.2f}")
    print(f"\n[LINK] 共 {len(out)} 条链, CSV 已存 {OUT_CSV}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
