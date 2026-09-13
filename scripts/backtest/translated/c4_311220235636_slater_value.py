# [BLUEPRINT] MOD-BT-103 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_311220235636_slater_value
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas; c3_fundamental.financial_indicator; c3_fundamental.balance_sheet; c3_fundamental.cashflow_statement
# [CONSUMERS] C4 快筛批测（scripts/backtest/c4_batch_screen.py）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（财报按 announce_date 公告日进信号）；成本=冻结土规；本文件同时导出
#   slater_screen 供 35（精选价值）与 55（价值改进）复用（同族原文）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-103 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 097: Slater 式价值精选（原文: 2020年度精选策略/07，md5=311220235636）。

原文逻辑（祖鲁/Slater 四条件，月频）: 全 A；①流通市值>截面均值 ②流动比率>截面均值
  ③近四季每季 ROE>当季截面均值 ④近五年 FCF（经营净额-投资净额）逐年>0；
  通过者按流通市值降序全选等权，日频调出。
译文实现: 流动比率=balance_sheet.total_current_assets/total_current_liabilities（announce_date PIT）；
  ROE=financial_indicator（季度，announce_date PIT）；FCF=cashflow_statement.ocf_net+icf_net 按年；
  市值=stock_indicator.circ_mv。第 5 条件（PE<均值）在原文被截断处之后未读到→省略（D3）。
因子拆解: Slater 价值筛选（市值+质量+现金流）——公开方法论，不登记 factor_registry。
翻译差异声明:
  D1 股票池: 全 A（HFQ 表）剔 ST；停牌不可剔（声明）
  D2 执行时点: T+1 收盘成交
  D3 第 5 条件（PE 截面比较）原文截断未读到→省略，登记 UNCERTAIN
  D4 因子登记: 公开价值方法论不登记
  D5 框架样板: 框架壳不翻译

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-14 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

from _c4_engine import emit, filter_st, load_px, load_st_flags, load_valuation, run_backtest, run_query, wide

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-311220235636"
WINDOW_KIND = "stock"


def _ann_pit_wide(rows: list[tuple], value_col: str) -> pd.DataFrame:
    """(symbol, announce_date, value) 长表 → 公告日宽表（同日多报取末条）。"""
    df = pd.DataFrame(rows, columns=["symbol", "announce_date", value_col])
    df["announce_date"] = pd.to_datetime(df["announce_date"])
    df = df.drop_duplicates(subset=["announce_date", "symbol"], keep="last")
    df = df.rename(columns={"announce_date": "trade_date"})
    return wide(df.rename(columns={value_col: "v"}), "v")


def slater_fundamentals(load_start: str, end: str):
    """三张财报的公告日 PIT 宽表字典（供 097/098/099 同族复用）。"""
    fund = run_query(
        f"SELECT symbol, announce_date, roe FROM c3_fundamental.financial_indicator "
        f"WHERE announce_date >= '{load_start}' AND announce_date <= '{end}' AND roe IS NOT NULL")
    roe = _ann_pit_wide(fund, "roe")
    bal = run_query(
        f"SELECT symbol, announce_date, total_current_assets, total_current_liabilities "
        f"FROM c3_fundamental.balance_sheet "
        f"WHERE announce_date >= '{load_start}' AND announce_date <= '{end}' "
        f"AND total_current_liabilities > 0")
    bal_df = pd.DataFrame(bal, columns=["symbol", "announce_date", "tca", "tcl"])
    bal_df["announce_date"] = pd.to_datetime(bal_df["announce_date"])
    bal_df["cr"] = bal_df["tca"] / bal_df["tcl"]
    cr = _ann_pit_wide(bal_df[["symbol", "announce_date", "cr"]].values.tolist(), "cr")
    cf = run_query(
        f"SELECT symbol, announce_date, ocf_net, icf_net FROM c3_fundamental.cashflow_statement "
        f"WHERE announce_date >= '{load_start}' AND announce_date <= '{end}' "
        f"AND ocf_net IS NOT NULL")
    cf_df = pd.DataFrame(cf, columns=["symbol", "announce_date", "ocf", "icf"])
    cf_df["announce_date"] = pd.to_datetime(cf_df["announce_date"])
    cf_df["fcf"] = cf_df["ocf"].fillna(0) + cf_df["icf"].fillna(0)
    fcf = _ann_pit_wide(cf_df[["symbol", "announce_date", "fcf"]].values.tolist(), "fcf")
    return roe, cr, fcf


def slater_screen(close: pd.DataFrame, start: str, end: str):
    """Slater 四条件面板（07/35/55 同族共用）：返回 (cand, mv, pe) 逐日面板。"""
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=400))[:10]
    val = load_valuation(load_start, end, fields=("pe", "circ_mv"))
    roe, cr, fcf = slater_fundamentals(load_start, end)
    dates = close.index[(close.index >= pd.Timestamp(start)) & (close.index <= pd.Timestamp(end))]
    roe_d = roe.reindex(index=dates, columns=close.columns).ffill()
    cr_d = cr.reindex(index=dates, columns=close.columns).ffill()
    fcf_d = fcf.reindex(index=dates, columns=close.columns).ffill()
    mv_d = val["circ_mv"].reindex(index=dates, columns=close.columns).ffill()
    pe_d = val["pe"].reindex(index=dates, columns=close.columns).ffill()
    rows = []
    for k in range(len(dates)):
        r4_ok = pd.Series(True, index=close.columns)
        for back in range(4):
            if k - back >= 0:
                col = roe_d.iloc[k - back]
                r4_ok &= col > col.mean()
        cond = (
            (mv_d.iloc[k] > mv_d.iloc[k].mean())
            & (cr_d.iloc[k] > cr_d.iloc[k].mean())
            & r4_ok
            & (fcf_d.iloc[max(0, k - 244): k + 1].min() > 0 if k >= 1 else False)
        )
        cond = cond.reindex(close.columns).fillna(False)
        cond &= pe_d.iloc[k].notna().reindex(close.columns).fillna(False)
        rows.append(cond)
    cand = pd.DataFrame(rows, index=dates, columns=close.columns)
    return cand, mv_d, pe_d


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    px = load_px(str(pd.Timestamp(start) - pd.Timedelta(days=400))[:10], end, fields=("close",))
    close = filter_st(wide(px, "close").ffill(), load_st_flags(str(pd.Timestamp(start) - pd.Timedelta(days=400))[:10], end))
    cand, mv_d, _pe = slater_screen(close, start, end)
    dates = close.index[(close.index >= pd.Timestamp(start)) & (close.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=close.columns)
    c_idx = cand.shift(1).reindex(dates).fillna(False)
    mv_prev = mv_d.shift(1).reindex(dates)
    for k, dt in enumerate(dates):
        cond = c_idx.iloc[k].values
        if not cond.any():
            continue
        caps = mv_prev.iloc[k][cond].fillna(0)
        caps = caps[caps > 0]
        if caps.empty:
            continue
        caps = caps.sort_values(ascending=False)
        weights.loc[dt, caps.index] = 1.0 / len(caps)
    return weights, close


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 全A剔ST", "D2 T+1收盘", "D3 PE条件截断省略",
                                               "D4 公开方法论不入库", "D5 壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
