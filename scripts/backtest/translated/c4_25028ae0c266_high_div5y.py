# [BLUEPRINT] MOD-BT-090 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_25028ae0c266_high_div5y
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas
# [CONSUMERS] C4 快筛批测（scripts/backtest/c4_batch_screen.py）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（分红按除息日入窗，行情/估值 ≤T-1）；成本=冻结土规
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-090 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 091: 高股息策略——五年累计股息率降序十强（原文: 2025年度精选策略/40 高股息策略）。

原文逻辑: 周频。全 A 剔科创北交；近 5 年分红总额/当前市值=五年股息率，降序取前 10 等权。
译文实现: 分红记录=c3_fundamental.dividend（dividend_before_tax/10=每股分红，ex_date 入窗），
  5 年累计每股分红/当前价=五年股息率；剔科创北交/ST。
因子拆解: 五年股息率——公开红利因子，不登记 factor_registry。
翻译差异声明:
  D1 股票池: 全 A（HFQ 表）剔 ST/科创北交
  D2 执行时点: 原文周一 9:30 → 每周首交易日 T 日收盘
  D3 股息率口径: 原文 bonus_amount_rmb 分红总额/市值 → 每股分红 5 年累计/价格（等价比率）
  D4 因子登记: 公开红利因子不登记
  D5 框架样板: finance.run_query 分批壳不翻译
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

from _c4_engine import emit, filter_st, load_px, load_st_flags, run_backtest, wide, _q

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-25028ae0c266"
WINDOW_KIND = "stock"
_TOP_N = 10


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=60))[:10]
    px = load_px(load_start, end, fields=("close",))
    closes = filter_st(wide(px).ffill(), load_st_flags(load_start, end))
    closes = closes.loc[:, ~closes.columns.str.startswith(("68", "8", "4"))]

    rows = _q("SELECT symbol, ex_date, dividend_before_tax FROM c3_fundamental.dividend "
              "WHERE ex_date IS NOT NULL AND dividend_before_tax IS NOT NULL")
    div = pd.DataFrame(rows, columns=["symbol", "ex_date", "per10"])
    div["ex_date"] = pd.to_datetime(div["ex_date"])
    div["per_share"] = div["per10"] / 10.0
    div5 = div.groupby(["symbol", pd.Grouper(key="ex_date", freq="5YS")])["per_share"].sum().reset_index()
    div_by_ex = div.set_index("ex_date")

    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    week_first = dates.to_series().groupby(dates.to_period("W")).min()
    weights = pd.DataFrame(0.0, index=dates, columns=closes.columns)
    for dt in week_first:
        row = closes.shift(1).reindex([dt]).iloc[0]
        t1 = pd.Timestamp(dt) - pd.Timedelta(days=1)
        t0 = t1 - pd.Timedelta(days=365 * 5)
        win = div_by_ex[(div_by_ex.index > t0) & (div_by_ex.index <= t1)]
        if win.empty:
            continue
        dr5 = win.groupby("symbol")["per_share"].sum() / row.dropna()
        dr5 = dr5.dropna()
        dr5 = dr5[dr5 > 0]
        if dr5.empty:
            continue
        picks = list(dr5.sort_values(ascending=False).index[:_TOP_N])
        weights.loc[dt, picks] = 1.0 / len(picks)
    return weights, closes


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 全A剔ST/科创北交", "D2 周首收盘", "D3 每股分红口径",
                                               "D4 公开因子不登记", "D5 壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
