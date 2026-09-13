# [BLUEPRINT] MOD-BT-155 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_4879b2c6f2bb_div_value
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas
# [CONSUMERS] C4 快筛批测（scripts/backtest/c4_batch_screen.py）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（信号/估值/财务快照均用 ≤T-1；财务按 announce_date 公告门）；成本=冻结土规
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-155 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 086: 高股息低市盈高增长月频十强（原文: 2024年度精选策略1/19 高股息低市盈率高增长的价投策略）。

原文逻辑: 月频首个交易日调仓：全 A 剔科创北交/ST/上市<300 天/停牌/涨停；
  股息率∈(0,10%) 排序 + PE∈(0,25) + 扣非ROE>3% + 营收同比>5% + 净利同比>11%
  + PE/净利增速∈(0.08,1.9)（PEG 带）；等权 10 只，调出即清。
译文实现: 股息率=dv_ttm；扣非ROE=np_excl_cum/equity_incl_minority（DS-230 最新公告期，
  announce_date<=T-1 公告门）；增速=rev_q_yoy/np_q_yoy。全 A 剔 ST/次新。
因子拆解: 股息率/PE/扣非ROE/增速——公开估值成长因子组，不登记 factor_registry。
翻译差异声明:
  D1 股票池: 全 A（HFQ 表）剔 ST/科创北交/次新（250 交易日近似 300 天）
  D2 执行时点: 原文 9:30 → T 日收盘
  D3 停牌/涨停不可剔（HFQ 无该列，声明）；扣非ROE 用最新公告期累计口径近似
  D4 因子登记: 公开因子组不登记
  D5 框架样板: 涨停开板监控（14:00 盘中）不翻译（日频口径）

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-14 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd

from _c4_engine import emit, fin_snapshot, filter_st, load_px, load_st_flags, load_valuation, run_backtest, wide

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-4879b2c6f2bb"
WINDOW_KIND = "stock"
_TOP_N = 10
_MIN_LIST_DAYS = 250


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=420))[:10]
    px = load_px(load_start, end, fields=("close",))
    close = filter_st(wide(px).ffill(), load_st_flags(load_start, end))
    close = close.loc[:, ~close.columns.str.startswith(("68", "8", "4"))]
    val = load_valuation(load_start, end, fields=("pe", "dividend_yield"))
    pe = val["pe"].reindex(close.index).reindex(columns=close.columns)
    dv = val["dividend_yield"].reindex(close.index).reindex(columns=close.columns)

    dates = close.index[(close.index >= pd.Timestamp(start)) & (close.index <= pd.Timestamp(end))]
    month_first = dates.to_series().groupby(dates.to_period("M")).min()
    weights = pd.DataFrame(0.0, index=dates, columns=close.columns)
    for dt in month_first:
        # 财务快照：公告门 <=T-1
        fin = fin_snapshot(str((pd.Timestamp(dt) - pd.Timedelta(days=1)).date()),
                           metrics=("np_excl_cum", "equity_incl_minority", "rev_q_yoy", "np_q_yoy"))
        if fin.empty:
            continue
        roe = (fin["np_excl_cum"] / fin["equity_incl_minority"].replace(0.0, np.nan)) * 100.0
        fdf = pd.DataFrame({"roe": roe, "rev_yoy": fin["rev_q_yoy"] * 100.0,
                            "np_yoy": fin["np_q_yoy"] * 100.0})
        prow = pe.shift(1).reindex([dt]).iloc[0]
        drow = dv.shift(1).reindex([dt]).iloc[0]
        cand = []
        for sym in close.columns:
            if sym not in fdf.index:
                continue
            p, dvv = prow.get(sym), drow.get(sym)
            f = fdf.loc[sym]
            if pd.isna(p) or pd.isna(dvv) or pd.isna(f["roe"]):
                continue
            if not (0 < p <= 25 and 0 < dvv <= 10 and f["roe"] > 3
                    and f["rev_yoy"] > 5 and f["np_yoy"] > 11 and 0.08 < p / f["np_yoy"] < 1.9):
                continue
            cand.append((sym, dvv))
        if not cand:
            continue
        picks = [s for s, _ in sorted(cand, key=lambda x: -x[1])][:_TOP_N]
        weights.loc[dt, picks] = 1.0 / len(picks)
    return weights, close


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 全A剔ST/科创北交/次新", "D2 T日收盘", "D3 停牌涨停不可剔/ROE口径近似",
                                               "D4 公开因子不登记", "D5 盘中监控不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
